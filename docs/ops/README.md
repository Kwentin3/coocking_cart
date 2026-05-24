# Ops documentation placeholders

- Статус: placeholder-пакет для будущей инфраструктурной документации
- Дата: 2026-05-24

## Назначение

`docs/ops/` содержит шаблоны и checklist для будущего инфраструктурного задания.

Реальные серверные данные будут добавлены позже отдельным заданием после передачи владельцем проекта:

- public domain;
- hosting/server address;
- SSH context;
- Traefik context;
- existing containers;
- deployment constraints.

## Важные правила

- `docs/out/` не является источником ops-документации.
- Секреты не хранятся в репозитории.
- Реальные IP, domains, SSH users, paths и network names не придумываются.
- Первое инфраструктурное действие должно быть read-only аудитом существующего сервера.
- Нельзя останавливать существующие контейнеры без отдельного подтверждения.

## Документы

- [Deployment context template](DEPLOYMENT_CONTEXT_TEMPLATE_v0.1.md) - какие данные нужно будет собрать перед деплоем.
- [Server audit checklist](SERVER_AUDIT_CHECKLIST_v0.1.md) - что проверить на сервере до любых изменений.
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md) - как относиться к `.env`, placeholders и секретам.

## Не-goals

- Не создавать production Docker/TLS/Traefik config.
- Не описывать реальные серверные данные.
- Не заменять будущий deployment runbook.
- Не хранить secrets.
