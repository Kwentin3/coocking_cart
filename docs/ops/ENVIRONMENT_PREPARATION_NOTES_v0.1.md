# Environment preparation notes v0.1

- Статус: заметки по подготовке окружения Demo MVP
- Дата: 2026-05-24

## Назначение

Документ фиксирует, как относиться к environment settings до реального инфраструктурного задания.

Реальная настройка будет отдельной задачей. Domain, server IP и SSH user уже переданы как deployment context, но secrets, Traefik settings и final deploy strategy еще не утверждены.

## Где хранить `.env`

Реальный `.env` должен храниться вне git.

Будущее место хранения зависит от выбранного способа деплоя и будет определено после server audit.

В документах можно использовать только placeholders.

## `.env.example`

Root [`.env.example`](../../.env.example) является безопасным шаблоном для разработчика, агента реализации и будущего deployment handoff.

Он содержит:

- имена переменных;
- placeholder-значения;
- известные non-secret deployment values для `coocking-cart.speechbattle.com`;
- отсутствие реальных secrets.

Для сервера `coocking-cart.speechbattle.com` будущий real `.env` должен быть создан вручную или безопасным способом вне Git и размещен в согласованном deploy path после отдельного deployment task.

В Git допустимо документировать:

- public domain;
- server IP;
- SSH user;
- expected `LLM_PROVIDER=gemini`;
- placeholders для Traefik settings.

В Git нельзя документировать:

- Gemini API key;
- real admin password или password hash;
- `AUTH_SESSION_SECRET`;
- private SSH key;
- реальные tokens или provider secrets.

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
- Private deployment credentials.
- Internal secrets.
- Traefik/acme secrets.
- Реальные Docker network names, если они раскрывают приватную инфраструктуру и не были явно зафиксированы как deployment context.

## Перед реальной настройкой нужно получить

- confirmation for public domain `coocking-cart.speechbattle.com`;
- confirmation for server `91.132.48.224`;
- confirmation for SSH user `root` and key-based access;
- deploy path policy;
- Traefik entrypoint/certresolver policy;
- confirmation that Docker network `edge` can be used or an alternative network plan;
- ports/TLS policy;
- способ передачи secrets;
- актуальный Gemini model id для `LLM_MODEL`;
- Gemini API key, переданный вне Git.

## Что делает агент после получения данных

Только после отдельного задания агент может:

- выполнить read-only server audit;
- заполнить deployment context;
- предложить безопасный deployment plan;
- создать или обновить `.env.example` с placeholders;
- подготовить инструкции по реальному `.env` без коммита secrets;
- разместить real `.env` только в согласованном deploy path и только после подтвержденного deployment task.

## Что не делать сейчас

- Не создавать `.env`.
- Не создавать real deployment config.
- Не придумывать IP/domain/SSH user.
- Не проектировать Docker/Traefik setup.
- Не добавлять CI/CD.
