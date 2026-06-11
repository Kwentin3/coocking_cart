# Deployment preparation handoff v0.1

- Статус: исторический handoff; актуальный app deploy flow см. в runbook
- Дата: 2026-05-24
- Target domain: `coocking-cart.speechbattle.com`
- Target server: `91.132.48.224`
- Status update: historical handoff; current app deploy flow is release-artifact based, see `LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md`

## Current status update 2026-05-27

This document was originally written before the first deploy. Current confirmed state:

- Demo MVP is deployed at `https://coocking-cart.speechbattle.com/`.
- App path is `/opt/coocking-cart`.
- Runtime env is `/opt/coocking-cart/runtime/.env`.
- Data path is `/opt/coocking-cart/data`.
- Releases live under `/opt/coocking-cart/releases/<commit>`.
- Current app symlink is `/opt/coocking-cart/current`.
- App container is `coocking-cart-app`.
- Docker network is `edge`; Traefik certresolver is `le`.
- Server-side `git` is not installed; do not use this handoff as a `git pull` deploy guide.
- Current deploy procedure is documented in `LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md`.

## Назначение

Документ сохраняет исторический контекст подготовки первого деплоя Demo MVP и текущие запреты для app-only deploy.

Это не deployment runbook и не production config. Актуальная процедура деплоя живет в `LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md`.

## Что уже известно

- Public domain: `coocking-cart.speechbattle.com`.
- Server IP: `91.132.48.224`.
- SSH user: `root`.
- SSH access: key-based, passwordless.
- Docker установлен.
- Docker Compose установлен.
- Traefik уже работает.
- На сервере уже есть работающие контейнеры.
- Public Traefik container: `platform-edge-traefik`.
- Docker network `edge` существует.
- Traefik-related path: `/opt/platform/traefik`.

## SSH access and hardening note

`root@91.132.48.224` принят как текущий demo deployment context, потому что этот доступ был передан владельцем проекта для read-only audit, первого деплоя и текущих app-only release обновлений.

Правила:

- private SSH key не хранится в Git;
- SSH password, tokens и key material не документируются в репозитории;
- любые изменения SSH-доступа не входят в Demo MVP implementation task;
- для production hardening желательно перейти на dedicated deploy user с минимальными правами.

Dedicated deploy user, sudo policy и SSH hardening остаются future ops hardening и не блокируют Demo MVP.

## Что нужно проверить перед деплоем

- Где безопасно разместить приложение.
- Можно ли использовать Docker network `edge` для routing через Traefik.
- Нужно ли создавать отдельную internal network для приложения.
- Какие Traefik entrypoints используются для public routing.
- Какой Traefik certresolver используется для TLS.
- Какой labels convention принят на сервере.
- Где должен храниться real `.env`.
- Где хранить SQLite/demo data.
- Где хранить logs.
- Нужны ли backups для SQLite/demo sessions.
- Какие существующие сервисы нельзя трогать.

## Что нельзя делать без отдельного подтверждения

- Деплоить приложение.
- Создавать или запускать Docker Compose config.
- Менять Traefik config.
- Менять Docker networks.
- Останавливать или перезапускать containers.
- Удалять containers, images, volumes или networks.
- Выпускать TLS certificates.
- Менять firewall.
- Менять DNS.
- Коммитить `.env`, secrets, tokens, API keys или SSH keys.

## Минимальная текущая стратегия app-only деплоя

1. Выполнить или переиспользовать read-only server audit.
2. Убедиться, что изменения закоммичены и отправлены в GitHub.
3. Собрать локальный `git archive` из коммита.
4. Загрузить архив на сервер в `/tmp`.
5. Распаковать release в `/opt/coocking-cart/releases/<commit>`.
6. Проверить `docker compose -f docker-compose.demo.yml config --quiet` внутри release.
7. Пересобрать/перезапустить только `coocking-cart-app`.
8. Переключить `/opt/coocking-cart/current` на новый release после успешного старта.
9. Проверить домен, `/api/config`, demo login + `/api/sessions`, контейнерный импорт и logs.
10. Не читать и не печатать `/opt/coocking-cart/runtime/.env`.

## Open questions

- Нужна ли отдельная app internal network позднее, если появятся новые backend services?
- Кто долгосрочный владелец `.env` и секретов?
- Какая политика logs retention?
- Нужны ли backups для SQLite/demo data?
- Какой rollback strategy достаточен для Demo MVP?

## Связанные документы

- [Deployment context](DEPLOYMENT_CONTEXT_coocking-cart.speechbattle.com_v0.1.md)
- [Server audit report](SERVER_AUDIT_REPORT_91.132.48.224_v0.1.md)
- [Server audit checklist](SERVER_AUDIT_CHECKLIST_v0.1.md)
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md)
- [MVP environment contract](../mvp/MVP_ENVIRONMENT_CONTRACT_v0.1.md)
