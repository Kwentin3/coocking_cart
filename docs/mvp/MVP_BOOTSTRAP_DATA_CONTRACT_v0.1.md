# MVP bootstrap data contract v0.1

- Статус: контракт стартовых данных Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Bootstrap data - минимальные данные, которые нужны приложению при первом запуске Demo MVP.

Цель - не хардкодить admin, роли, provider/model, context paths и demo settings в коде.

Документ не описывает SQL-миграции и не является production identity/storage design.

## Что создается при первом запуске

Минимально:

- роли `user` и `admin`;
- bootstrap admin;
- demo settings;
- ссылка на initial context manifest;
- LLM provider/model defaults;
- debug/context inspector settings.

## Bootstrap admin

Bootstrap admin нужен, чтобы открыть demo-настройки и Context Inspector без ручного изменения кода.

Данные должны приходить из environment/bootstrap contract:

- `BOOTSTRAP_ADMIN_EMAIL`;
- `BOOTSTRAP_ADMIN_PASSWORD` или `BOOTSTRAP_ADMIN_PASSWORD_HASH`;
- `AUTH_SESSION_SECRET`.

В репозитории нельзя хранить реальные email, passwords, hashes или secrets.

## Initial roles

При первом запуске должны существовать только:

- `user`;
- `admin`.

Другие роли не создаются в MVP.

## Demo user

Demo user опционален.

Если он нужен для показа, его параметры должны быть placeholders и приходить из безопасного bootstrap-процесса или создаваться вручную через admin-действие после запуска.

Не хардкодить demo user credentials.

## Initial context manifest

Приложение должно знать путь к initial context manifest:

- `CONTEXT_MANIFEST_PATH`;
- `CONTEXT_LAYERS_DIR`.

Эти значения приходят из env или config, а не из глубоко захардкоженной доменной логики.

## Demo settings

Минимальные demo settings:

- `DEMO_MODE`;
- `ENABLE_CONTEXT_INSPECTOR`;
- `ENABLE_LLM_TRACE`;
- `APP_BASE_URL`, если runtime должен знать публичный URL;
- `PUBLIC_DOMAIN`, если runtime или deployment layer использует домен;
- max dialogue messages for context, если будет нужно как future setting;
- выбранный default scenario, если будет нужно как future setting.

## LLM provider defaults

Минимально:

- `LLM_PROVIDER`;
- `LLM_MODEL`;
- `LLM_BASE_URL`, если нужен совместимый API endpoint;
- `LLM_TIMEOUT_SECONDS`.

`LLM_API_KEY` должен приходить только из environment/secrets management и не попадать в репозиторий.

## Deployment context defaults

Для текущего target deployment известны не-secret значения:

- domain: `coocking-cart.speechbattle.com`;
- server: `91.132.48.224`;
- SSH user: `root`;
- reverse proxy: existing Traefik;
- container runtime: Docker.

Эти данные помогают будущему deployment handoff, но не создают приложение, `.env`, compose или Traefik config.

## Что должно приходить из env

- Bootstrap admin identity.
- Bootstrap credential или password hash.
- Session secret.
- SQLite/database path.
- LLM provider/model/API key.
- Context manifest path.
- Context layers dir.
- Debug flags.
- App base URL/domain, если требуется runtime.
- Deployment host/user/network placeholders, если требуется deployment layer.

## Что не должно быть захардкожено

- Admin email.
- Admin password или hash.
- API keys.
- Session secrets.
- Provider model.
- Context file paths в доменной логике.
- Secrets, passwords, API keys и SSH keys.
- Deployment network/entrypoint/certresolver values до review.

## Что нельзя коммитить

- `.env` с реальными значениями.
- API keys.
- Passwords.
- Password hashes, если они относятся к реальному окружению.
- SSH keys.
- API tokens.
- Реальные `.env` значения.
- Private deployment credentials.
- Internal secrets реального сервера.

Публичный domain, server IP и SSH user можно хранить только как явно переданный deployment context в `docs/ops/`; они не являются bootstrap secrets.

## Связанные документы

- [Roles and access](MVP_ROLES_AND_ACCESS_v0.1.md)
- [Environment contract](MVP_ENVIRONMENT_CONTRACT_v0.1.md)
- [Implementation handoff](MVP_IMPLEMENTATION_HANDOFF_v0.1.md)
- [Ops README](../ops/README.md)
