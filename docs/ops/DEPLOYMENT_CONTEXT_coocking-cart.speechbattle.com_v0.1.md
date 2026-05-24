# Deployment context: coocking-cart.speechbattle.com v0.1

- Статус документа: deployment context для будущего Demo MVP
- Дата: 2026-05-24
- Deployment status: not deployed yet
- Audit status: pending

## Назначение

Документ фиксирует известный deployment context для будущего деплоя Demo MVP AI-ассистента технологических карт.

Этот документ не является runbook деплоя и не разрешает менять сервер. Перед любыми изменениями нужен read-only server audit и отдельное deployment task.

## Known deployment target

| Field | Value |
| --- | --- |
| Public domain | `coocking-cart.speechbattle.com` |
| Server IP | `91.132.48.224` |
| SSH user | `root` |
| SSH access | key-based, passwordless |
| Container runtime | Docker already present |
| Reverse proxy | Existing Traefik |

## Known warning

На сервере уже есть работающие Docker containers и Traefik. Их нельзя останавливать, перезапускать, удалять или менять без отдельного review и подтвержденного deployment task.

Первый инфраструктурный проход должен быть только read-only.

## Secrets policy

- Секреты не хранятся в репозитории.
- Приватные SSH keys не хранятся в репозитории.
- LLM API keys не хранятся в репозитории.
- Реальные `.env` файлы с секретами не коммитятся.
- Пароли, tokens и private credentials не добавляются в documentation.

## Current status

- Demo MVP application: not deployed yet.
- DNS/domain: known target domain.
- Server access: key-based SSH context is known.
- Docker: known to be present.
- Traefik: known to be present.
- Existing containers: present, exact list must be confirmed by read-only audit.
- Deployment path: unknown.
- Traefik network: unknown.
- TLS/certresolver policy: unknown.

## Unknowns / TODO

- Confirm safe app deploy path.
- Confirm Docker network for the app.
- Confirm existing Traefik network name.
- Confirm current TLS policy.
- Confirm Traefik certresolver name.
- Confirm Traefik email/resolver configuration without exposing secrets.
- Confirm whether there is a shared external Docker network.
- Decide where `.env` will live on the server.
- Decide logs policy.
- Decide backup policy for SQLite/demo data.
- Identify containers and services that must not be touched.

## Allowed next action

Only read-only server audit is allowed at this stage.

See:

- [Server audit checklist](SERVER_AUDIT_CHECKLIST_v0.1.md)
- [Deployment preparation handoff](DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md)
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md)
