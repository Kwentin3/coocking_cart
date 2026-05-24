# Deployment context template v0.1

- Статус: шаблон будущих инфраструктурных данных
- Дата: 2026-05-24

## Назначение

Этот документ должен быть заполнен позже, когда владелец проекта передаст реальные инфраструктурные данные.

Сейчас все значения являются placeholders. Не заменять их выдуманными значениями.

## Project

| Field | Placeholder | Notes |
| --- | --- | --- |
| Project name | `<PROJECT_NAME>` | Название приложения/сервиса. |
| Deployment purpose | `<DEPLOYMENT_PURPOSE>` | Demo/stage/production-like demo. |
| Responsible owner | `<OWNER_CONTACT_PLACEHOLDER>` | Контакт владельца без реальных данных в этом шаблоне. |

## Network and access

| Field | Placeholder | Notes |
| --- | --- | --- |
| Public domain | `<PUBLIC_DOMAIN>` | Заполнить только после передачи владельцем. |
| Hosting IP | `<HOSTING_IP>` | Не придумывать. |
| Internal server address | `<INTERNAL_SERVER_ADDRESS>` | Если применимо. |
| SSH user | `<SSH_USER>` | Не придумывать. |
| Auth method | `<AUTH_METHOD>` | Ожидаемо: key-based. |

## Deployment layout

| Field | Placeholder | Notes |
| --- | --- | --- |
| App deploy path | `<APP_DEPLOY_PATH>` | Согласовать после аудита сервера. |
| Environment file location | `<ENV_FILE_LOCATION>` | Не хранить секреты в git. |
| Logs location | `<LOGS_LOCATION>` | Уточнить после выбора runtime. |
| Backups location | `<BACKUPS_LOCATION>` | Future/optional. |

## Reverse proxy and routing

| Field | Placeholder | Notes |
| --- | --- | --- |
| Existing reverse proxy | `<REVERSE_PROXY>` | Например Traefik, если подтвердится аудитом. |
| Traefik status | `<TRAEFIK_STATUS>` | Unknown до аудита. |
| TLS policy | `<TLS_POLICY>` | Unknown до аудита. |
| Ports policy | `<PORTS_POLICY>` | Какие порты можно использовать. |

## Docker/server state

| Field | Placeholder | Notes |
| --- | --- | --- |
| Docker networks | `<DOCKER_NETWORKS>` | Заполняется после read-only аудита. |
| Existing containers | `<EXISTING_CONTAINERS>` | Заполняется после read-only аудита. |
| Volumes | `<VOLUMES>` | Заполняется после read-only аудита. |
| Do-not-touch services | `<DO_NOT_TOUCH_SERVICES>` | Критично перед деплоем. |

## Unknowns / TODO

- `<TODO_CONFIRM_DOMAIN>`
- `<TODO_CONFIRM_SSH_ACCESS>`
- `<TODO_AUDIT_EXISTING_CONTAINERS>`
- `<TODO_CONFIRM_TRAEFIK>`
- `<TODO_CONFIRM_DEPLOY_PATH>`
- `<TODO_CONFIRM_ENV_STRATEGY>`
