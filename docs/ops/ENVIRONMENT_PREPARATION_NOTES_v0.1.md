# Environment preparation notes v0.1

- Статус: заметки по подготовке окружения Demo MVP
- Дата: 2026-05-24
- Последнее обновление: 2026-05-27

## Назначение

Документ фиксирует, как относиться к environment settings в текущем Demo MVP deployment.

Domain, server IP, SSH user, deploy path, runtime env path, data path, Traefik network and certresolver уже подтверждены. Secrets по-прежнему не документируются и не коммитятся.

## Где хранить `.env`

Реальный `.env` должен храниться вне git.

Текущее серверное место хранения: `/opt/coocking-cart/runtime/.env`.

В документах можно использовать только placeholders.

## `.env.example`

Root [`.env.example`](../../.env.example) является безопасным шаблоном для разработчика, агента реализации и deployment handoff.

Он содержит:

- имена переменных;
- placeholder-значения;
- известные non-secret deployment values для `coocking-cart.speechbattle.com`;
- отсутствие реальных secrets.

Для сервера `coocking-cart.speechbattle.com` real `.env` живет вне Git в `/opt/coocking-cart/runtime/.env`.

В Git допустимо документировать:

- public domain;
- server IP;
- SSH user;
- expected `LLM_PROVIDER=gemini`;
- подтвержденные non-secret Traefik settings: network `edge`, certresolver `le`.

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

## Подтвержденный runtime/deploy context

- public domain `coocking-cart.speechbattle.com`;
- server `91.132.48.224`;
- SSH user `root` and key-based access;
- deploy path `/opt/coocking-cart`;
- runtime env path `/opt/coocking-cart/runtime/.env`;
- data path `/opt/coocking-cart/data`;
- Docker network `edge`;
- Traefik certresolver `le`;
- app container `coocking-cart-app`.

## Перед изменением secrets нужно получить

- способ передачи secrets;
- актуальный Gemini model id для `LLM_MODEL`;
- Gemini API key, переданный вне Git.

## Что делает агент после получения данных

Только после отдельного задания агент может:

- создать или обновить `.env.example` с placeholders;
- подготовить инструкции по реальному `.env` без коммита secrets;
- изменить real `.env` только в `/opt/coocking-cart/runtime/.env` и только без вывода secrets в лог.

## Что не делать сейчас

- Не читать и не печатать real `.env`.
- Не придумывать IP/domain/SSH user/path/network/certresolver.
- Не менять Docker/Traefik setup в app-only задачах.
- Не добавлять CI/CD.
