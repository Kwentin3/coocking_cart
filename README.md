# coocking_cart

Проект находится на стадии Demo MVP implementation.

Основная навигация по проектной документации находится в [docs/README.md](docs/README.md).

## Локальный запуск

1. Скопируйте `.env.example` в локальный `.env`.
2. Заполните runtime secrets вне Git: `AUTH_SESSION_SECRET`, bootstrap admin credentials и `LLM_API_KEY`.

For local HTTP, keep `SESSION_COOKIE_SECURE=auto` and open the app through `127.0.0.1`/`localhost`, or set `APP_BASE_URL=http://127.0.0.1:8000`.
3. Запустите приложение:

```powershell
python -m app.main --host 127.0.0.1 --port 8000
```

Откройте: http://127.0.0.1:8000

Если `LLM_API_KEY` или обязательные env-переменные не настроены, приложение покажет безопасную конфигурационную ошибку.

## Проверки

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```
