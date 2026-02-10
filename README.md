# Data Assistant TG Bot

Pet-проект Telegram-бота, который отвечает на аналитические вопросы на русском языке по данным видео-метрик.

Пайплайн ответа:

1. Пользователь пишет вопрос в Telegram.
2. LLM (AliceAI) превращает вопрос в один безопасный SQL `SELECT`.
3. SQL выполняется в PostgreSQL.
4. Бот отправляет пользователю числовой результат.

---

## Что внутри и зачем

Проект демонстрирует практичный подход к связке **Telegram + LLM + SQL** для BI-подобных вопросов:

- строгий prompt под доменную схему;
- валидация SQL и ограничение на read-only запросы;
- проверка формата результата (ровно 1 строка, 1 колонка, число);
- наблюдаемость через логи (вход, SQL, время SQL, исходящий ответ, ответ);
- конфигурируемые таймауты LLM и БД;
- миграции Alembic;
- unit/integration тесты.

---

## Технологии

- **Python 3.12**
- **aiogram** — Telegram Bot API
- **YandexGPT API** — генерация SQL
- **PostgreSQL 16**
- **SQLAlchemy (async)** + **psycopg**
- **Alembic** — миграции
- **Pydantic Settings** — env-конфиг
- **pytest / pytest-asyncio** — тестирование
- **ruff, mypy, pre-commit** — линтеры

---

## Архитектура

```text
Telegram user
   │
   ▼
aiogram router (app/bot/router.py)
   │  input_text log
   │  telegram_response log
   ▼
YandexGPT client (app/llm/client.py)
   │  timeout (LLM_TIMEOUT_SECONDS)
   ▼
SQL validator + executor (app/db/executor.py)
   │  generated_sql log
   │  sql_execution_time_ms log
   ▼
PostgreSQL (videos, video_snapshots)
```

Ключевая бизнес-логика:

- Prompt ограничивает LLM только на `SELECT` и результат типа "одно число".
- Исполнитель SQL дополнительно страхует: запрещает DDL/DML/utility и `;`.
- Пользователь получает единый текст ошибки: **«не смог обработать запрос»**.

---

## Структура проекта

```text
app/
  bot/          # Telegram handler
  llm/          # LLM-клиент и prompt
  db/           # SQLAlchemy модели, сессии, executor
  core/         # settings, logging
alembic/        # миграции
scripts/        # утилиты (загрузка данных)
tests/          # unit/integration тесты
```

---

## Переменные окружения

Создайте `.env` в корне проекта:

```env
TG_BOT_TOKEN=123456:ABCDEF
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/video
YANDEX_API_KEY=your_api_key
YANDEX_FOLDER_ID=your_folder_id

# необязательно
LEVEL_LOGGING=INFO
LLM_TIMEOUT_SECONDS=30
DB_TIMEOUT_SECONDS=15
```

### Пояснения

- `TG_BOT_TOKEN` — токен Telegram-бота от BotFather.
- `DATABASE_URL` — строка подключения SQLAlchemy async.
- `YANDEX_API_KEY`, `YANDEX_FOLDER_ID` — доступ к YandexGPT.
- `LLM_TIMEOUT_SECONDS` — общий timeout запроса в LLM.
- `DB_TIMEOUT_SECONDS` — `statement_timeout` для PostgreSQL.

---

## Быстрый старт

### 1) Клонирование и виртуальное окружение

```bash
git clone <your-repo-url>
cd data_assistant_tg_bot
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 2) Установка зависимостей

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3) Поднять PostgreSQL в Docker

```bash
docker compose up -d db
```

### 4) Применить миграции

```bash
alembic upgrade head
```

### 5) (Опционально) загрузить тестовые данные

```bash
python -m scripts.load_data
```


### 6) Запуск бота

```bash
python -m app.main
```

---

## Команды для разработки

### Линтеры и типизация

```bash
make lint
```

Команда включает:

- `ruff check`
- `ruff format --check`
- `mypy`

### Тесты

Только unit:

```bash
make test
```

Только integration:

```bash
make test-integration
```

Полный pytest напрямую:

```bash
pytest -q
```

---

## Наблюдаемость и эксплуатация

Проект логирует важные этапы:

- `input_text=...` — что пришло от пользователя;
- `generated_sql=...` — SQL, который сгенерировала LLM;
- `sql_execution_time_ms=...` — время SQL;
- `telegram_response=...` — что бот отправил пользователю;
- `failed_to_process_request` — exception с traceback.

Единая ошибка для пользователя: `не смог обработать запрос`.

---

## Безопасность текущей версии

Сделано:

- Только `SELECT` по контракту prompt.
- Запрещены `;` и опасные токены (`insert`, `update`, `drop`, ...).
- Запрос должен вернуть строго одно числовое значение.
- Таймауты на LLM и БД.

---

## Пример пользовательских запросов

- «Сколько всего видео?»
- «Сколько видео у креатора 123 вышло с 2025-01-01 по 2025-01-31?»
- «На сколько просмотров в сумме выросли все видео 2025-02-01?»

---

## Ограничения

- Поддерживается сценарий «вопрос → одно число».
- Бот рассчитан на доменную схему `videos`/`video_snapshots`.
- Качество ответа зависит от формулировки вопроса и prompt.
