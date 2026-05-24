# Environment preparation notes v0.1

- Статус: заметки по подготовке окружения Demo MVP
- Дата: 2026-05-24

## Назначение

Документ фиксирует, как относиться к environment settings до реального инфраструктурного задания.

Реальная настройка будет отдельной задачей после передачи IP/domain/SSH/Traefik context владельцем проекта.

## Где хранить `.env`

Реальный `.env` должен храниться вне git.

Будущее место хранения зависит от выбранного способа деплоя и будет определено после server audit.

В документах можно использовать только placeholders.

## `.env.example`

`.env.example` можно создать позже, когда начнется реализация приложения.

Он должен содержать только:

- имена переменных;
- placeholder-значения;
- комментарии;
- отсутствие реальных secrets.

В рамках текущего прохода `.env.example` не создается.

## Минимальные группы переменных

См. [MVP environment contract](../mvp/MVP_ENVIRONMENT_CONTRACT_v0.1.md):

- app/runtime;
- auth/bootstrap;
- database;
- LLM provider;
- context files;
- debug/demo;
- deployment placeholders.

## Что нельзя коммитить

- Реальный `.env`.
- API keys.
- Passwords.
- Session secrets.
- SSH private keys.
- Реальный server IP.
- Реальный public domain.
- Реальный deploy user.
- Реальные Docker network names, если они раскрывают инфраструктуру.

## Перед реальной настройкой нужно получить

- public domain;
- hosting/server address;
- SSH user;
- SSH auth method;
- deploy path policy;
- Traefik/reverse proxy context;
- existing containers list или разрешение на read-only аудит;
- ports/TLS policy;
- способ передачи secrets.

## Что делает агент после получения данных

Только после отдельного задания агент может:

- выполнить read-only server audit;
- заполнить deployment context;
- предложить безопасный deployment plan;
- подготовить `.env.example` с placeholders;
- подготовить инструкции по реальному `.env` без коммита secrets.

## Что не делать сейчас

- Не создавать `.env`.
- Не создавать real deployment config.
- Не придумывать IP/domain/SSH user.
- Не проектировать Docker/Traefik setup.
- Не добавлять CI/CD.
