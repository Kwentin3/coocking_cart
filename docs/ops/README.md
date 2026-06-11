# Ops documentation

- Статус: актуальный ops-контур Demo MVP
- Дата: 2026-05-24
- Последнее обновление: 2026-05-27

## Назначение

`docs/ops/` содержит deployment context, runbook, шаблоны и checklist для текущего Demo MVP deployment.

Часть non-secret deployment context уже передана владельцем проекта:

- domain `coocking-cart.speechbattle.com`;
- server `91.132.48.224`;
- SSH user `root`;
- key-based SSH access;
- existing Docker and Traefik.

Подтвержденный текущий runtime/deploy контур:

- app deploy path `/opt/coocking-cart`;
- runtime env `/opt/coocking-cart/runtime/.env`;
- SQLite/data path `/opt/coocking-cart/data`;
- releases `/opt/coocking-cart/releases/<commit>`;
- current symlink `/opt/coocking-cart/current`;
- app container `coocking-cart-app`;
- Traefik network `edge`;
- Traefik certresolver `le`;
- server-side `git` is not installed, so deploy uses release archives from committed local Git state.

## Важные правила

- `docs/out/` не является источником ops-документации.
- Секреты не хранятся в репозитории.
- IP, domains, SSH users, paths и network names не придумываются: фиксируются только явно переданные или подтвержденные аудитом значения.
- Для app-only deploy можно пересобирать/перезапускать только `coocking-cart-app`.
- Нельзя останавливать существующие контейнеры вне `coocking-cart`.
- Нельзя выполнять server-side `git pull`, пока наличие `git` и такой flow не зафиксированы в runbook.

## Документы

- [Deployment context template](DEPLOYMENT_CONTEXT_TEMPLATE_v0.1.md) - какие данные нужно будет собрать перед деплоем.
- [Deployment context: coocking-cart.speechbattle.com](DEPLOYMENT_CONTEXT_coocking-cart.speechbattle.com_v0.1.md) - известный target context для Demo MVP.
- [Deployment preparation handoff](DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md) - исторический handoff; текущий deploy flow см. в runbook.
- [Server audit checklist](SERVER_AUDIT_CHECKLIST_v0.1.md) - что проверить на сервере до любых изменений.
- [Server audit report: 91.132.48.224](SERVER_AUDIT_REPORT_91.132.48.224_v0.1.md) - результат read-only аудита.
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md) - как относиться к `.env`, placeholders и секретам.
- [Local testing and production runtime runbook](LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md) - фиксирует локальные Windows/PowerShell проверки, отсутствие локального Docker/Linux и server-side release-artifact deploy.

## Не-goals

- Не хранить secrets.
- Не менять Traefik/DNS/firewall в рамках app-only deploy.
- Не объявлять текущий root SSH deploy production-hardening решением.
