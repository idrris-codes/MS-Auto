# Masir Service Telegram Bot

Готовый Telegram-бот для Masir Service: выбор языка, проверка подписки на канал, заявки на ремонт/запчасти, пункт выдачи, уведомление админу и статистика.

## Файлы

- `main.py` — основной код бота
- `requirements.txt` — зависимости
- `Procfile` — запуск на Railway как worker
- `.env.example` — пример переменных окружения
- `.gitignore` — файлы, которые не нужно заливать в GitHub

## Railway Variables

Добавьте в Railway → Variables:

```env
BOT_TOKEN=новый_токен_бота
ADMIN_ID=7826275748
CHANNEL_USERNAME=@masirservice
STATS_USERS=7826275748
DATA_FILE=bot_data.json
```

Важно: токен из старого кода был открыт в файле. Его нужно заменить через BotFather, потому что старый токен уже нельзя считать безопасным.

## Запуск через GitHub + Railway

1. Создайте новый GitHub repository.
2. Загрузите туда файлы проекта.
3. В Railway создайте New Project → Deploy from GitHub repo.
4. Добавьте переменные окружения из блока выше.
5. Railway должен запустить команду из `Procfile`: `worker: python main.py`.
6. Проверьте Logs. Если всё правильно, появится polling без ошибок.

## Важно про хранение заявок

Сейчас заявки хранятся в `bot_data.json`. Для маленького проекта этого достаточно. Для серьёзного запуска лучше позже подключить PostgreSQL, потому что Railway может потерять локальный файл при redeploy.
