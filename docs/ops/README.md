# Ops documentation placeholders

- Статус: placeholder-пакет для будущей инфраструктурной документации
- Дата: 2026-05-24

## Назначение

`docs/ops/` содержит deployment context, шаблоны и checklist для будущего инфраструктурного задания.

Часть non-secret deployment context уже передана владельцем проекта:

- domain `coocking-cart.speechbattle.com`;
- server `91.132.48.224`;
- SSH user `root`;
- key-based SSH access;
- existing Docker and Traefik.

Оставшиеся инфраструктурные данные должны уточняться отдельным заданием:

- existing containers;
- Traefik entrypoint/certresolver;
- safe deployment path;
- deployment constraints.

## Важные правила

- `docs/out/` не является источником ops-документации.
- Секреты не хранятся в репозитории.
- IP, domains, SSH users, paths и network names не придумываются: фиксируются только явно переданные или подтвержденные аудитом значения.
- Первое инфраструктурное действие должно быть read-only аудитом существующего сервера.
- Нельзя останавливать существующие контейнеры без отдельного подтверждения.

## Документы

- [Deployment context template](DEPLOYMENT_CONTEXT_TEMPLATE_v0.1.md) - какие данные нужно будет собрать перед деплоем.
- [Deployment context: coocking-cart.speechbattle.com](DEPLOYMENT_CONTEXT_coocking-cart.speechbattle.com_v0.1.md) - известный target context для Demo MVP.
- [Deployment preparation handoff](DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md) - что делать перед будущим deployment task.
- [Server audit checklist](SERVER_AUDIT_CHECKLIST_v0.1.md) - что проверить на сервере до любых изменений.
- [Server audit report: 91.132.48.224](SERVER_AUDIT_REPORT_91.132.48.224_v0.1.md) - результат read-only аудита.
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md) - как относиться к `.env`, placeholders и секретам.
- [Local testing and production runtime runbook](LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md) - фиксирует, что локально нет Docker/Linux, а production Docker/Linux живет на хостинговом сервере.

## Не-goals

- Не создавать production Docker/TLS/Traefik config.
- Не описывать реальные серверные данные.
- Не заменять будущий deployment runbook.
- Не хранить secrets.
