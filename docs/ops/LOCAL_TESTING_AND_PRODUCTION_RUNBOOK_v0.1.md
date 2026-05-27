# Local testing and production runtime runbook v0.1

- Статус: обязательная ops-заметка для тестов и деплоя
- Дата: 2026-05-27
- Контур: Demo MVP

## Ключевой архитектурный факт

Локальное рабочее пространство разработчика не является production-like средой:

- локально нет рабочего Docker runtime;
- локально нет Linux runtime;
- локальные проверки выполняются в Windows/PowerShell;
- production runtime живет на хостинговом сервере `91.132.48.224`;
- Docker, Linux, Traefik и production-like network доступны только на сервере.

Из этого следует: локальный `docker build` или Linux-container parity нельзя считать обязательным локальным gate. Если Docker на локальной машине не запускается, это не блокер само по себе. Блокером является отсутствие серверной проверки или явной artifact simulation.

## Как тестировать локально

Локальные обязательные проверки:

```powershell
python -m unittest discover -s tests
python -m compileall app tests
node --check app/static/app.js
git diff --check
```

Если изменение затрагивает runtime imports, env или packaging, дополнительно выполнить artifact simulation по тем же путям, которые копирует `Dockerfile`:

- `app/`;
- `docs/mvp/context/`;
- `README.md`.

Проверка должна импортировать приложение из временного artifact path, а не из IDE/workspace visibility.

## Как проверять production/runtime parity

Production parity проверяется на сервере или через artifact simulation.

Серверный контекст:

- SSH: `root@91.132.48.224`;
- deploy path: `/opt/coocking-cart`;
- runtime env: `/opt/coocking-cart/runtime/.env`;
- app data: `/opt/coocking-cart/data`;
- public domain: `coocking-cart.speechbattle.com`;
- Docker network: `edge`;
- Traefik certresolver: `le`.

Live Voice transport:

- browser JavaScript must not receive SOCKS5 credentials and cannot force `fetch`/`WebSocket` through an application-level SOCKS5 proxy;
- if Gemini Live direct WSS is rejected by location, set `LIVE_VOICE_TRANSPORT=server_proxy` in `/opt/coocking-cart/runtime/.env`;
- set `LIVE_VOICE_RESPONSE_MODALITY=AUDIO`; the browser still uses only Live input transcription for textarea dictation;
- set real `LIVE_VOICE_SOCKS5_HOST`, `LIVE_VOICE_SOCKS5_PORT`, `LIVE_VOICE_SOCKS5_USERNAME`, `LIVE_VOICE_SOCKS5_PASSWORD` only in the server runtime env, never in Git or docs;
- in `server_proxy` mode `/api/live-voice/token` returns backend WSS `/api/live-voice/ws/<session>` to the browser; the backend connects to Gemini Live WSS through SOCKS5.
- GUI contract: batch fallback shows record/stop controls; Live streaming shows an animated mic. Do not expose `server_proxy` or SOCKS5 labels in user-facing GUI copy.
- Transcription policy is shared by batch and Live: configure `VOICE_TRANSCRIPTION_LANGUAGE`, `VOICE_TRANSCRIPTION_SCRIPT`, `VOICE_TRANSCRIPTION_LATIN_ALLOWLIST`, `VOICE_TRANSCRIPTION_DOMAIN_TERMS`, `VOICE_TRANSCRIPTION_EXTRA_INSTRUCTION`, or full `VOICE_TRANSCRIPTION_PROMPT_OVERRIDE` in runtime env. For Gemini Live this is a prompt-level preference, not hard API `languageCode`.

Перед серверным deploy:

1. Убедиться, что изменения закоммичены и отправлены в Git.
2. На сервере обновить `/opt/coocking-cart` из Git.
3. Не читать и не печатать реальные secrets из runtime `.env`.
4. Проверить `docker compose config` без вывода секретов.
5. Выполнить rebuild/restart только сервиса `app`.
6. Проверить HTTP/HTTPS endpoint и последние logs.

## Stop rules

- Не считать локальный Docker build обязательным, если локальный Docker/Linux отсутствует или сломан.
- Не подменять server parity локальной IDE visibility.
- Не коммитить `.env`, API keys, SSH keys, tokens.
- Не трогать чужие контейнеры, сети и Traefik config вне `coocking-cart`.
- Не деплоить незакоммиченный рабочий каталог.

## Где зафиксировано для будущих тестов

Та же архитектурная заметка продублирована sticky-комментарием в `tests/test_mvp_core.py`, чтобы она попадала в контекст при изменении тестов.
