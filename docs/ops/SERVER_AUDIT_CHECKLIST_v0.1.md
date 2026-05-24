# Server audit checklist v0.1

- Статус: checklist read-only аудита перед деплоем
- Дата: 2026-05-24

## Назначение

Перед любым деплоем агент должен понять текущее состояние сервера. Первый проход должен быть read-only.

Нельзя менять конфигурацию, останавливать контейнеры, удалять volumes или менять Traefik без отдельного задания и подтверждения.

## Known target context

- Target domain: `coocking-cart.speechbattle.com`.
- Target server: `91.132.48.224`.
- SSH user: `root`.
- SSH access: key-based.
- Docker already present.
- Traefik already present.
- Existing containers already running.

Для этого сервера любые изменения Traefik, Docker networks, containers, firewall, DNS или TLS допускаются только отдельным заданием после review.

## Что выяснить у владельца проекта

- Кто владелец сервера.
- Подтвердить public domain `coocking-cart.speechbattle.com`.
- Подтвердить SSH access для `root@91.132.48.224`.
- Где можно размещать приложение.
- Какие сервисы нельзя трогать.
- Какой Traefik entrypoint/certresolver использовать.
- Можно ли использовать Docker network `edge`.
- Какие ограничения по портам и TLS.

## Read-only проверки на сервере

Первый технический аудит должен проверить:

- текущего пользователя;
- hostname и базовую ОС;
- доступность Docker, если он должен использоваться;
- список уже работающих контейнеров;
- существующие Docker networks;
- существующие volumes;
- занятые порты;
- наличие и состояние reverse proxy;
- наличие и состояние Traefik, если он есть;
- существующие deploy paths;
- права на предполагаемую директорию деплоя;
- где безопасно хранить logs/backups.
- что Traefik containers подключены к ожидаемой network.
- что выбранный app deploy path не конфликтует с существующими проектами.

## Что нельзя делать на первом проходе

- Останавливать контейнеры.
- Перезапускать Traefik.
- Удалять networks или volumes.
- Менять firewall.
- Выпускать TLS certificates.
- Создавать production config.
- Записывать secrets в репозиторий.
- Использовать `docker compose down` или аналогичные разрушительные команды.
- Читать или копировать secret files без отдельного разрешения.
- Коммитить результаты, содержащие secrets.

## Результат аудита

После read-only аудита нужно подготовить отдельный отчет:

- что уже работает;
- какие порты заняты;
- есть ли Traefik;
- какие networks/containers/volumes существуют;
- где можно безопасно разместить Demo MVP;
- какие данные все еще неизвестны;
- какие действия требуют подтверждения владельца.

## Связанные документы

- [Deployment context template](DEPLOYMENT_CONTEXT_TEMPLATE_v0.1.md)
- [Environment preparation notes](ENVIRONMENT_PREPARATION_NOTES_v0.1.md)
- [MVP environment contract](../mvp/MVP_ENVIRONMENT_CONTRACT_v0.1.md)
