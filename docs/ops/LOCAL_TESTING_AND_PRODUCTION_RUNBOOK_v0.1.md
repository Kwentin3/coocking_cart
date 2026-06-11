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
- на сервере сейчас нет `git`; production deploy выполняется через release-артефакт из уже закоммиченного локального дерева.

Из этого следует: локальный `docker build` или Linux-container parity нельзя считать обязательным локальным gate. Если Docker на локальной машине не запускается, это не блокер само по себе. Блокером является отсутствие серверной проверки или явной artifact simulation.

## Как тестировать локально

Локальные обязательные проверки:

```powershell
python -m unittest discover -s tests
python -m compileall app tests scripts
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
- release root: `/opt/coocking-cart/releases/<commit>`;
- current symlink: `/opt/coocking-cart/current`;
- container: `coocking-cart-app`.

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
2. Убедиться, что локальный worktree чистый: `git status --short --branch`.
3. Собрать release-артефакт из коммита, а не из незакоммиченных файлов: `git archive --format=tar -o <tmp>/coocking-cart-<sha>.tar HEAD`.
4. Загрузить архив на сервер в `/tmp/coocking-cart-<sha>.tar`.
5. На сервере распаковать архив в `/opt/coocking-cart/releases/<sha>`.
6. Не читать и не печатать реальные secrets из runtime `.env`.
7. Внутри release выполнить `docker compose -f docker-compose.demo.yml config --quiet`.
8. Выполнить rebuild/restart только сервиса `app`. Из-за фиксированного `container_name` допустимо удалять только контейнер `coocking-cart-app`, не трогая чужие контейнеры, сети и volumes.
9. После успешного старта переключить `/opt/coocking-cart/current` на новый release.
10. Проверить HTTP/HTTPS endpoint, импорт модулей внутри контейнера и последние logs.

Минимальный production smoke после deploy:

```powershell
python -m unittest discover -s tests
python -m compileall app tests scripts
node --check app/static/app.js
git diff --check
```

На сервере:

```bash
docker exec coocking-cart-app python -c 'import app.main, app.routes.contracts, app.http.cookies; print(len(app.routes.contracts.ROUTE_DOMAIN_CONTRACTS))'
readlink -f /opt/coocking-cart/current
docker logs --tail 40 coocking-cart-app
```

Снаружи:

- `HEAD https://coocking-cart.speechbattle.com/` returns `200`.
- `GET https://coocking-cart.speechbattle.com/api/config` returns `ok=true`.
- `POST /api/demo-login` followed by `GET /api/sessions` on the same cookie jar returns `ok=true`.

## Stop rules

- Не считать локальный Docker build обязательным, если локальный Docker/Linux отсутствует или сломан.
- Не подменять server parity локальной IDE visibility.
- Не коммитить `.env`, API keys, SSH keys, tokens.
- Не трогать чужие контейнеры, сети и Traefik config вне `coocking-cart`.
- Не деплоить незакоммиченный рабочий каталог.
- Не планировать `git pull` на сервере, пока `git` там явно не установлен и не зафиксирован в runbook.

## Где зафиксировано для будущих тестов

Та же архитектурная заметка продублирована sticky-комментарием в `tests/test_mvp_core.py`, чтобы она попадала в контекст при изменении тестов.
