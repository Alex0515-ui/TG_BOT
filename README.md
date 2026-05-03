🤖 TG_BOT — Telegram-бот для изучения английского с AI
Telegram-бот на Python, созданный как личный инструмент для изучения английского языка, с поддержкой AI-диалога, системы уровней и режимов обучения. Работает через webhook и развёртывается с помощью Docker Compose.

📋 Содержание
Описание
Технологии
Структура проекта
Быстрый старт
Настройка webhook (ngrok)
Команды управления
Заполнение базы данных
Тестирование
Переменные окружения

Описание
Этот проект был разработан как решение личной проблемы: большинство сервисов для изучения английского языка либо платные, либо не подходят под реальные задачи разработчика.

Поэтому бот был создан для:

практики английского через диалог
изучения слов через контекст
понимания технической документации

👉 Основная идея: учить английский через реальное использование и взаимодействие с AI

Основные возможности:
AI-диалог — общение через LLM (Groq API)

Словарь слов — база данных слов, автоматически заполняемая через Gemini API (seed_words.py)

Практика перевода — пользователь переводит предложения, AI проверяет и анализирует ответ

Система уровней — 6 уровней сложности (от базового до продвинутого)

Режимы обучения:

general — общий английский (повседневная речь)
tech — технический английский (для чтения документации и разработки)

Webhook Telegram — обработка обновлений через HTTP (без polling)

REST API (web-сервис) — управление логикой и данными

PostgreSQL — хранение слов, прогресса и состояний

Redis — хранение временных данных и сессий

Celery — фоновые задачи (например, генерация слов)

Тесты — покрытие через pytest

Технологии
Технология	Назначение
Python	Основной язык
Webhook (Telegram Bot API)	Получение обновлений
SQLAlchemy / Alembic	ORM и миграции
PostgreSQL	Основная база данных
Redis	Временные данные
Celery	Фоновые задачи
Groq API	AI-диалог и проверка
Gemini API	Генерация слов
Docker & Docker Compose	Контейнеризация
pytest	Тестирование

Структура проекта
TG_BOT/
└── bot/
├── docker-compose.yml      # Сервисы (db, redis, web, worker)
├── Dockerfile              # Образ приложения
├── tasks.py                # Celery задачи
├── telegram.py             # Webhook обработка Telegram
├── main.py                 # Точка входа
├── seed_words.py           # Генерация слов через Gemini
├── alembic/                # Миграции
├── app/
│   ├── handlers/           # Обработчики сообщений
│   ├── AI/                 # Работа с Groq/Gemini
│   ├── db/                 # Конфигурация БД
│   ├── entities/           # ORM модели
│   └── services/           # Бизнес-логика
└── tests/                  # Тесты

Быстрый старт
Требования

Docker и Docker Compose

Telegram Bot Token

API-ключи:

Groq (диалог)
Gemini (генерация слов)

1. Клонировать репозиторий
   git clone https://github.com/Alex0515-ui/TG_BOT.git
   cd TG_BOT

2. Настроить переменные окружения
   cd bot
   cp .env.example .env

3. Запуск
   docker-compose up --build

---

🌐 Настройка webhook (ngrok)

Поскольку Telegram требует публичный HTTPS URL для webhook, при локальной разработке используется ngrok.

Требования
ngrok (https://ngrok.com/download)
Аккаунт ngrok и authtoken

1. Установить ngrok
   Скачайте и распакуйте ngrok

2. Получить authtoken
   https://dashboard.ngrok.com/signup
   https://dashboard.ngrok.com/get-started/your-authtoken

3. Добавить токен
   ngrok config add-authtoken YOUR_TOKEN_HERE

4. Запустить ngrok
   ngrok http 8000

Вы получите URL вида:
https://xxxx.ngrok-free.app

5. Указать webhook
   Добавьте в .env:
   WEBHOOK_URL=https://xxxx.ngrok-free.app/webhook

Перезапустите проект:
docker-compose down
docker-compose up

Важно
URL меняется при каждом запуске
нужно обновлять WEBHOOK_URL
используется только для разработки

Ошибка
ERR_NGROK_4018 — не добавлен authtoken

Решение:
ngrok config add-authtoken YOUR_TOKEN_HERE

---

Команды управления
Команда	Описание
docker-compose up --build	Запуск
docker-compose up -d	Фоновый запуск
docker-compose down	Остановка
docker-compose logs -f	Логи
docker-compose ps	Статус

Заполнение базы данных
docker-compose exec web python seed_words.py
Использует Gemini API для генерации слов.

Тестирование
python -m pytest

В Docker:
docker-compose exec web python -m pytest

Переменные окружения
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
DATABASE_URL=...

REDIS_HOST=redis
REDIS_PORT=6379

BOT_TOKEN=...

GROQ_API_KEY=...
GEMINI_API_KEY=...
WEBHOOK_URL=...

📌 Итог
Проект демонстрирует:

backend-разработку с несколькими сервисами
работу с webhook вместо polling
интеграцию с несколькими AI API
использование очередей задач (Celery)
работу с Redis и PostgreSQL
контейнеризацию (Docker)
тестирование

👉 Основной фокус: автоматизация изучения английского с использованием AI и backend-инженерии

Лицензия
MIT License
