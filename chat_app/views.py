import json

from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .models import Message
from .services import get_ai_response


@require_GET
def chat_page(request: HttpRequest):
    messages = Message.objects.all().order_by('created_at', 'id')
    return render(request, 'chat_app/chat.html', {'messages': messages})


@require_POST
def chat_api(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest('Некорректный JSON')

    user_text = (payload.get('message') or '').strip()
    if not user_text:
        return JsonResponse({'error': 'Пустое сообщение'}, status=400)

    user_message = Message.objects.create(role=Message.ROLE_USER, content=user_text)

    try:
        ai_text = get_ai_response(user_text)
    except Exception as exc:
        ai_text = f'Ошибка при обращении к AI: {exc}'

    ai_message = Message.objects.create(role=Message.ROLE_AI, content=ai_text)

    return JsonResponse(
        {
            'user': {
                'id': user_message.id,
                'role': user_message.role,
                'content': user_message.content,
                'created_at': user_message.created_at.isoformat(),
            },
            'ai': {
                'id': ai_message.id,
                'role': ai_message.role,
                'content': ai_message.content,
                'created_at': ai_message.created_at.isoformat(),
            },
        }
    )
