# Deployment preparation handoff v0.1

- Статус: handoff для будущего deployment task
- Дата: 2026-05-24
- Target domain: `coocking-cart.speechbattle.com`
- Target server: `91.132.48.224`

## Назначение

Документ объясняет, с чего начинать будущий деплой Demo MVP и какие действия запрещены до отдельного подтверждения.

Это не deployment runbook и не production config. Приложение сейчас не деплоится.

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

`root@91.132.48.224` принят как текущий demo deployment context, потому что этот доступ был передан владельцем проекта для read-only audit и будущей подготовки деплоя.

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

## Минимальная будущая стратегия деплоя

1. Выполнить или переиспользовать read-only server audit.
2. Согласовать app deploy path.
3. Согласовать Docker network strategy.
4. Подготовить `.env.example` только с placeholders.
5. Передать real `.env` вне Git.
6. Подготовить compose/config в отдельной ветке и task.
7. Подключить Traefik labels после review existing Traefik conventions.
8. Сделать dry-run/review без остановки существующих сервисов.
9. Выполнить deploy отдельным подтвержденным заданием.
10. Проверить домен, health endpoint, logs и rollback path.

## Open questions

- Какой final app deploy path использовать?
- Можно ли подключать Demo MVP к network `edge` напрямую?
- Нужна ли отдельная app internal network?
- Какой Traefik certresolver использовать?
- Какие entrypoints использовать: `web`, `websecure` или другие?
- Где должен жить real `.env`?
- Кто владелец `.env` и секретов?
- Какая политика logs retention?
- Нужны ли backups для SQLite/demo data?
- Какой rollback strategy достаточен для Demo MVP?

## Связанные документы

- [Deployment context](DEPLOYMENT_CONTEXT_coocking-cart.speechbattle.com_v0.1.md)
- [Server audit report](SERVER_AUDIT_REPORT_91.132.48.224_v0.1.md)
- [Server audit checklist](SERVER_AUDIT_CHECKLIST_v0.1.md)
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md)
- [MVP environment contract](../mvp/MVP_ENVIRONMENT_CONTRACT_v0.1.md)
