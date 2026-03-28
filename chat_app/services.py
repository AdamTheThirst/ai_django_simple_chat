from __future__ import annotations

from typing import List, Dict

from django.conf import settings
from openai import APIStatusError
from openai import OpenAI

from .models import Message


def get_recent_dialog_context(limit_pairs: int = 20) -> List[Dict[str, str]]:
    """Возвращает последние N пар (user+ai) = до 2N сообщений."""
    limit_messages = limit_pairs * 2
    queryset = Message.objects.order_by('-created_at', '-id')[:limit_messages]
    messages = list(reversed(list(queryset)))

    role_map = {
        Message.ROLE_USER: 'user',
        Message.ROLE_AI: 'assistant',
    }

    return [
        {
            'role': role_map[m.role],
            'content': m.content,
        }
        for m in messages
    ]


def get_ai_response(user_text: str) -> str:
    if not settings.AI_BASE_URL:
        raise ValueError('AI_BASE_URL не задан в .env')

    if not settings.AI_API_KEY:
        raise ValueError('AI_API_KEY не задан в .env')

    base_url = settings.AI_BASE_URL.strip().rstrip('/')

    messages = [
        {'role': 'system', 'content': settings.AI_MASTER_PROMPT},
        *get_recent_dialog_context(limit_pairs=20),
        {'role': 'user', 'content': user_text},
    ]

    def request_with_base_url(current_base_url: str):
        client = OpenAI(
            base_url=current_base_url,
            api_key=settings.AI_API_KEY,
        )
        return client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            max_tokens=400,
            temperature=0.7,
            top_p=0.8,
        )

    try:
        chat_response = request_with_base_url(base_url)
    except APIStatusError as exc:
        # Частая проблема для vLLM/OpenAI-compatible прокси:
        # URL указан без /v1, из-за этого сервер отвечает 405.
        if exc.status_code == 405 and not base_url.endswith('/v1'):
            fallback_url = f'{base_url}/v1'
            chat_response = request_with_base_url(fallback_url)
        else:
            raise

    return chat_response.choices[0].message.content or 'Пустой ответ от AI.'
