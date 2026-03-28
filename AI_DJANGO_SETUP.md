# Подключение Django к AI (vLLM/OpenAI-compatible API)

Ниже — подробный гайд, как подключён AI в проекте.

## 1) Где хранится конфигурация

Все чувствительные данные и параметры подключения хранятся в `.env`:

- `AI_BASE_URL` — URL точки входа OpenAI-compatible сервера (например vLLM), обычно с `/v1`
- `AI_API_KEY` — API ключ
- `AI_MODEL` — имя модели (например `Qwen/Qwen3-32B`)
- `AI_MASTER_PROMPT` — мастер-промпт (system message)

Пример есть в `.env.example`.

## 2) Как Django читает `.env`

В `chat_project/settings.py` вызывается:

```python
from dotenv import load_dotenv
load_dotenv()
```

После этого переменные читаются через `os.getenv(...)` и сохраняются в настройках:

- `AI_BASE_URL`
- `AI_API_KEY`
- `AI_MODEL`
- `AI_MASTER_PROMPT`

## 3) Логика запроса к AI

В `chat_app/services.py`:

1. Создаётся клиент:

```python
client = OpenAI(
    base_url=settings.AI_BASE_URL,
    api_key=settings.AI_API_KEY,
)
```

2. Формируется `messages`:

- `system` с мастер-промптом
- последние сообщения контекста (до 20 пар = до 40 сообщений)
- текущее сообщение пользователя

3. Вызывается Chat Completions:

```python
client.chat.completions.create(
    model=settings.AI_MODEL,
    messages=messages,
    max_tokens=400,
    temperature=0.7,
    top_p=0.8,
)
```

4. Возвращается `chat_response.choices[0].message.content`.

## 4) Как работает контекст 20 пар

Функция `get_recent_dialog_context(limit_pairs=20)`:

- берёт из SQLite последние `limit_pairs * 2` сообщений,
- разворачивает в хронологический порядок,
- маппит роли:
  - `user` → `user`
  - `ai` → `assistant`

Таким образом модель получает историю в правильном формате API.

## 5) Где вызывается AI в HTTP-потоке

В `chat_app/views.py` endpoint `POST /api/chat/`:

1. Считывает JSON с текстом пользователя.
2. Сохраняет сообщение пользователя в БД.
3. Вызывает `get_ai_response(user_text)`.
4. Сохраняет ответ AI в БД.
5. Возвращает JSON для фронтенда.

## 6) Обработка ошибок

- Если `AI_BASE_URL`/`AI_API_KEY` не заданы, выбрасывается ошибка с понятным текстом.
- Если вызов модели падает (сеть/401/500), пользователю возвращается текст ошибки в сообщении AI.

## 7) Быстрая проверка подключения

1. Заполните `.env` по образцу `.env.example`.
2. Запустите сервер Django.
3. Отправьте сообщение в чате.
4. Если конфигурация верная, увидите ответ модели.
5. Если нет — увидите диагностический текст ошибки.
