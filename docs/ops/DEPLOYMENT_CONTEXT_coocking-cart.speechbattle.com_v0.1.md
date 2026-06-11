# Deployment context: coocking-cart.speechbattle.com v0.1

- Статус документа: актуальный deployment context Demo MVP
- Дата: 2026-05-24
- Deployment status: deployed Demo MVP
- Audit status: completed, read-only on 2026-05-24
- Runtime status update: active production path verified on 2026-05-27

## Назначение

Документ фиксирует актуальный deployment context Demo MVP AI-ассистента технологических карт.

Этот документ не заменяет runbook деплоя. Текущий app-only deploy flow описан в `LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md`.

## Known deployment target

| Field | Value |
| --- | --- |
| Public domain | `coocking-cart.speechbattle.com` |
| Server IP | `91.132.48.224` |
| SSH user | `root` |
| SSH access | key-based, passwordless |
| Container runtime | Docker already present |
| Reverse proxy | Existing Traefik |
| Deploy path | `/opt/coocking-cart` |
| Runtime env | `/opt/coocking-cart/runtime/.env` |
| Data path | `/opt/coocking-cart/data` |
| Release root | `/opt/coocking-cart/releases/<commit>` |
| Current release symlink | `/opt/coocking-cart/current` |
| App container | `coocking-cart-app` |
| Docker network | `edge` |
| Traefik certresolver | `le` |
| Server git | not installed; deploy uses release archives |

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

- Demo MVP application: deployed.
- DNS/domain: known target domain.
- Server access: key-based SSH context is known.
- Docker: known to be present.
- Traefik: known to be present.
- Existing containers: confirmed by read-only audit; do not touch containers outside `coocking-cart`.
- Deployment path: `/opt/coocking-cart`.
- Runtime env path: `/opt/coocking-cart/runtime/.env`.
- SQLite/data path: `/opt/coocking-cart/data`.
- Current verified release at last update: `/opt/coocking-cart/releases/5b15136`.
- Current symlink: `/opt/coocking-cart/current`.
- App container: `coocking-cart-app`.
- Traefik network: `edge`.
- TLS/certresolver policy: Traefik `websecure` + certresolver `le`.
- Server-side `git`: unavailable; deploy must use a local `git archive` release artifact.

## Read-only audit summary

Read-only audit confirmed:

- SSH access works as `root`.
- Hostname: `r1121293`.
- OS/kernel: Debian-based Linux, kernel `5.10.0-32-amd64`.
- Docker is installed.
- Docker Compose is installed.
- Existing Traefik containers are running.
- Public Traefik container exposes ports `80` and `443`.
- Shared Docker network `edge` exists.
- Existing project paths under `/opt` include `platform`, `seminar`, `doctorbridge` and `switerkoff`.
- Traefik files are located under `/opt/platform/traefik`.

No server files were changed. Secret files were not read.

## Remaining TODO

- Add a first-class deploy script for the release-artifact flow.
- Add rollback command/runbook for `/opt/coocking-cart/current`.
- Add backup/restore procedure for `/opt/coocking-cart/data/demo.sqlite`.
- Decide logs retention policy.
- Later replace root SSH with a dedicated deploy user.

## Allowed next action

For current Demo MVP iteration, allowed app-only action is release-artifact deploy of committed code under `/opt/coocking-cart/releases/<commit>`, followed by rebuild/restart of only `coocking-cart-app`. Do not change Traefik, Docker networks, unrelated containers, volumes, DNS, firewall or runtime secrets.

See:

- [Server audit checklist](SERVER_AUDIT_CHECKLIST_v0.1.md)
- [Deployment preparation handoff](DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md)
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md)
