# Simple Django AI Chat

Простой чат на Django с сохранением всех реплик в SQLite и интеграцией с OpenAI-compatible API (например vLLM).

## Что сделано (тезисно)

- Реализован чат без регистрации: открыл страницу и можно сразу писать.
- Реализован API endpoint `POST /api/chat/` для отправки сообщений без перезагрузки страницы (fetch + минимальный JS).
- Реализовано хранение истории в SQLite в таблице `Message` (`id`, `created_at`, `role`, `content`).
- Реализована интеграция с AI через `openai` клиент и параметры из `.env`.
- Добавлен мастер-промпт по умолчанию:
  - `Ты - умный помощник, который всё знает и умеет отвечать на вопросы. Стиль ответа дружественный, простой, но не панибратский`.
- Добавлена память контекста: последние 20 пар сообщений (до 40 сообщений).
- Добавлен интерфейс на Bootstrap с базовым визуальным стилем в духе Material Design.
- Вёрстка mobile-first.
- Добавлен отдельный подробный гайд по подключению Django к AI: `AI_DJANGO_SETUP.md`.

## Структура проекта

- `chat_project/` — настройки Django и маршруты.
- `chat_app/` — логика чата (модель, views, сервис вызова AI, шаблон и статика).
- `db.sqlite3` — SQLite база (появится после миграций).

## Подробная инструкция по запуску

### 1. Подготовка окружения

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

- `AI_BASE_URL` — endpoint вашего AI сервера (OpenAI-compatible)
- `AI_API_KEY` — ключ
- при необходимости `AI_MODEL`

### 3. Применение миграций

```bash
python manage.py migrate
```

### 4. Запуск сервера

```bash
python manage.py runserver
```

Откройте в браузере: `http://127.0.0.1:8000/`

### 5. Проверка

- Отправьте сообщение в чат.
- Должен появиться ответ AI без перезагрузки страницы.
- Проверьте сохранение истории в SQLite:

```bash
python manage.py shell -c "from chat_app.models import Message; print(Message.objects.count())"
```

## API формат

### `POST /api/chat/`

Request:

```json
{
  "message": "Привет!"
}
```

Response:

```json
{
  "user": {
    "id": 1,
    "role": "user",
    "content": "Привет!",
    "created_at": "..."
  },
  "ai": {
    "id": 2,
    "role": "ai",
    "content": "Привет! Чем могу помочь?",
    "created_at": "..."
  }
}
```

## Примечания

- В режиме ошибки подключения к модели чат всё равно сохранит реплики в БД.
- Если видите `405 Method Not Allowed`, проверьте `AI_BASE_URL`: обычно нужен путь с `/v1`.
  В коде есть авто-fallback (повтор запроса на `${AI_BASE_URL}/v1`), но лучше сразу указать корректный URL.
- Для production обязательно:
  - выставить `DJANGO_DEBUG=False`
  - задать безопасный `DJANGO_SECRET_KEY`
  - настроить `DJANGO_ALLOWED_HOSTS`.
