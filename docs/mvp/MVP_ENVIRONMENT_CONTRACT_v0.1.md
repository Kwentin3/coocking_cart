# MVP environment contract v0.1

- Статус: минимальный контракт переменного окружения Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Environment contract фиксирует, какие runtime-настройки будущая реализация должна получать из окружения или безопасного config layer.

Принцип: никакие секреты, API keys, passwords, provider settings, bootstrap credentials и deployment details не хардкодятся в коде и не хранятся в репозитории.

Этот документ не создает `.env`, не содержит реальные значения и не является production secrets management design.

## Общие правила

- В документации используются только placeholder-значения.
- Реальные secrets передаются отдельно безопасным способом.
- `.env` с реальными значениями не коммитится.
- `.env.example` в будущем может содержать только placeholders.
- Код доменной логики не должен напрямую зависеть от конкретных значений environment.

## Минимальные группы переменных

### App/runtime

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `APP_ENV` | Да | `<APP_ENV>` | Режим приложения: demo/local/stage. |
| `APP_NAME` | Да | `<APP_NAME>` | Человекочитаемое имя приложения. |
| `APP_BASE_URL` | Optional | `<APP_BASE_URL>` | Базовый URL будущего приложения, если нужен runtime. |

### Auth/bootstrap

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `BOOTSTRAP_ADMIN_EMAIL` | Да | `<BOOTSTRAP_ADMIN_EMAIL>` | Идентификатор первого admin. |
| `BOOTSTRAP_ADMIN_PASSWORD` | Optional | `<BOOTSTRAP_ADMIN_PASSWORD>` | Bootstrap password, если используется plain bootstrap flow. |
| `BOOTSTRAP_ADMIN_PASSWORD_HASH` | Optional | `<BOOTSTRAP_ADMIN_PASSWORD_HASH>` | Bootstrap password hash, если plain password не используется. |
| `AUTH_SESSION_SECRET` | Да | `<AUTH_SESSION_SECRET>` | Секрет подписи/шифрования сессии. |

Правило: использовать либо `BOOTSTRAP_ADMIN_PASSWORD`, либо `BOOTSTRAP_ADMIN_PASSWORD_HASH`, но не хранить реальные значения в репозитории.

### Database

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `SQLITE_DB_PATH` | Да | `<SQLITE_DB_PATH>` | Путь к SQLite-файлу Demo MVP. |
| `DATABASE_URL` | Optional/future | `<DATABASE_URL>` | Future-compatible database URL, если SQLite path будет заменен. |

Для Demo MVP достаточно SQLite. Production database design остается future track.

### LLM provider

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `LLM_PROVIDER` | Да | `<LLM_PROVIDER>` | Имя выбранного LLM provider. |
| `LLM_MODEL` | Да | `<LLM_MODEL>` | Имя модели. |
| `LLM_API_KEY` | Да | `<LLM_API_KEY>` | API key provider. |
| `LLM_BASE_URL` | Optional | `<LLM_BASE_URL>` | Base URL для совместимых API, если нужен. |
| `LLM_TIMEOUT_SECONDS` | Optional | `<LLM_TIMEOUT_SECONDS>` | Timeout вызова LLM. |

Provider factory и capability matrix не входят в MVP.

### Context files

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `CONTEXT_MANIFEST_PATH` | Да | `<CONTEXT_MANIFEST_PATH>` | Путь к `context_manifest.yml`. |
| `CONTEXT_LAYERS_DIR` | Да | `<CONTEXT_LAYERS_DIR>` | Путь к директории markdown context layers. |

Эти пути не должны быть глубоко захардкожены в доменной логике.

### Debug/demo

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `DEMO_MODE` | Да | `<DEMO_MODE>` | Явный режим Demo MVP. |
| `ENABLE_CONTEXT_INSPECTOR` | Optional | `<ENABLE_CONTEXT_INSPECTOR>` | Включение Context Inspector/debug view. |
| `ENABLE_LLM_TRACE` | Optional | `<ENABLE_LLM_TRACE>` | Включение минимального context trace. |

### Deployment placeholders

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `PUBLIC_DOMAIN` | Optional/future | `<PUBLIC_DOMAIN>` | Будущий публичный домен. |
| `DEPLOY_HOST` | Optional/future | `<DEPLOY_HOST>` | Будущий host для деплоя. |
| `DEPLOY_USER` | Optional/future | `<DEPLOY_USER>` | Будущий deploy user. |
| `TRAEFIK_NETWORK_NAME` | Optional/future | `<TRAEFIK_NETWORK_NAME>` | Будущее имя Traefik/Docker network, если применимо. |

Эти значения не заполняются до отдельного инфраструктурного задания.

## Что нельзя хранить в репозитории

- Реальные `.env` файлы.
- API keys.
- Session secrets.
- Passwords.
- Password hashes реального окружения.
- SSH private keys.
- Server IP.
- Public domain.
- Deploy user.
- Internal network names реального сервера.

## Связанные документы

- [Bootstrap data contract](MVP_BOOTSTRAP_DATA_CONTRACT_v0.1.md)
- [Roles and access](MVP_ROLES_AND_ACCESS_v0.1.md)
- [LLM provider adapter note](MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md)
- [Ops environment notes](../ops/ENVIRONMENT_PREPARATION_NOTES_v0.1.md)
