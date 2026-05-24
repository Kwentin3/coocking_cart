# MVP stack decision v0.1

- Статус: stack decision для реализации Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP implementation

## Решение

Для Demo MVP выбран минимальный стек:

- Python 3.11 standard library;
- встроенный HTTP server на `http.server`;
- SQLite через `sqlite3`;
- vanilla HTML/CSS/JavaScript;
- Gemini REST API через `urllib.request`;
- без npm/pip runtime dependencies.

## Почему подходит для Demo MVP

- Markdown context layers читаются напрямую из файлов.
- SQLite доступен из стандартной библиотеки.
- Env/config можно валидировать в одном entrypoint без дополнительных пакетов.
- Gemini вызывается через явный provider adapter boundary.
- Structured output для Gemini задается schema-first через generation config (`responseMimeType` + `responseJsonSchema`), а не prompt-only форматированием.
- Frontend остается простым: чат, result panel, Context Inspector и states без тяжелого UI-framework.
- Локальный запуск прост: `python -m app.main`.
- Будущая контейнеризация возможна, но не требуется для локального MVP.

## Границы

Этот стек выбран для демонстрационного прототипа, а не как production architecture.

В scope не входят:

- production ASGI/WSGI server;
- сложный frontend framework;
- ORM;
- production IAM/RBAC;
- background jobs;
- provider factory;
- Docker/Traefik config;
- CI/CD.

Если после демо потребуется production hardening, стек можно пересмотреть отдельно.
