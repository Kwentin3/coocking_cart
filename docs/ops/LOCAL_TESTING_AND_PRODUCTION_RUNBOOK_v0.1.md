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

Если изменение затрагивает Python MVP runtime imports, env или packaging, дополнительно выполнить artifact simulation по тем же путям, которые копирует root `Dockerfile`:

- `app/`;
- `docs/mvp/context/`;
- `README.md`.

Проверка должна импортировать приложение из временного artifact path, а не из IDE/workspace visibility.

Если изменение затрагивает Landing Showcase runtime/build, дополнительно проверить:

- `frontend/Dockerfile`;
- `frontend/package.json` / `frontend/package-lock.json`;
- `NEXT_PUBLIC_MVP_ENTRY_URL=/mvp`;
- `npm run validate`, `npm run lint`, `npm run build` inside `frontend/`.

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
- MVP container: `coocking-cart-app`.
- landing container: `coocking-cart-landing` when same-domain landing/MVP topology is deployed.

Live Voice transport:

- browser JavaScript must not receive SOCKS5 credentials and cannot force `fetch`/`WebSocket` through an application-level SOCKS5 proxy;
- if Gemini Live direct WSS is rejected by location, set `LIVE_VOICE_TRANSPORT=server_proxy` in `/opt/coocking-cart/runtime/.env`;
- set `LIVE_VOICE_RESPONSE_MODALITY=AUDIO`; the browser still uses only Live input transcription for textarea dictation;
- set real `LIVE_VOICE_SOCKS5_HOST`, `LIVE_VOICE_SOCKS5_PORT`, `LIVE_VOICE_SOCKS5_USERNAME`, `LIVE_VOICE_SOCKS5_PASSWORD` only in the server runtime env, never in Git or docs;
- in `server_proxy` mode `/api/live-voice/token` returns backend WSS `/api/live-voice/ws/<session>` to the browser; the backend connects to Gemini Live WSS through SOCKS5.
- GUI contract: batch fallback shows record/stop controls; Live streaming shows an animated mic. Do not expose `server_proxy` or SOCKS5 labels in user-facing GUI copy.
- Transcription policy is shared by batch and Live: configure `VOICE_TRANSCRIPTION_LANGUAGE`, `VOICE_TRANSCRIPTION_SCRIPT`, `VOICE_TRANSCRIPTION_LATIN_ALLOWLIST`, `VOICE_TRANSCRIPTION_DOMAIN_TERMS`, `VOICE_TRANSCRIPTION_EXTRA_INSTRUCTION`, or full `VOICE_TRANSCRIPTION_PROMPT_OVERRIDE` in runtime env. For Gemini Live this is a prompt-level preference, not hard API `languageCode`.

Same-domain landing/MVP target:

- Root `/` belongs to the public landing showcase.
- Demo MVP can be mounted under `/mvp` by setting `APP_BASE_PATH=/mvp`.
- Edge routing for the MVP should use `PathPrefix(/mvp)` without stripping the prefix, because the app now handles the prefix itself.
- `docker-compose.demo.yml` owns only coocking-cart labels/services: landing catch-all router on `/`, MVP router on `PathPrefix(/mvp)`.
- Landing deploy env should point the icon-only MVP entry to `NEXT_PUBLIC_MVP_ENTRY_URL=/mvp`.
- In prefixed mode the browser-facing MVP endpoints are `/mvp/api/...`, while internal route contracts remain `/api/...` after handler prefix normalization.
- MVP session cookies are scoped to `Path=/mvp` in prefixed mode.
- Prefixed login/logout responses also clear the legacy root `cc_session` cookie with `Path=/; Max-Age=0`.

Перед серверным deploy:

1. Убедиться, что изменения закоммичены и отправлены в Git.
2. Убедиться, что локальный worktree чистый: `git status --short --branch`.
3. Собрать release-артефакт из коммита, а не из незакоммиченных файлов: `git archive --format=tar -o <tmp>/coocking-cart-<sha>.tar HEAD`.
4. Загрузить архив на сервер в `/tmp/coocking-cart-<sha>.tar`.
5. На сервере распаковать архив в `/opt/coocking-cart/releases/<sha>`.
6. Не читать и не печатать реальные secrets из runtime `.env`.
7. Внутри release выполнить `docker compose -f docker-compose.demo.yml config --quiet`.
8. Для same-domain topology выполнить rebuild/restart только сервисов `landing` и `app`. Из-за фиксированных `container_name` допустимо удалять только контейнеры `coocking-cart-landing` и `coocking-cart-app`, не трогая чужие контейнеры, сети и volumes.
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
docker exec coocking-cart-landing node -e "console.log(process.version)"
readlink -f /opt/coocking-cart/current
docker logs --tail 40 coocking-cart-app
docker logs --tail 40 coocking-cart-landing
```

Снаружи:

Legacy root-mode MVP deployment:

- `HEAD https://coocking-cart.speechbattle.com/` returns `200`.
- `GET https://coocking-cart.speechbattle.com/api/config` returns `ok=true`.
- `POST /api/demo-login` followed by `GET /api/sessions` on the same cookie jar returns `ok=true`.

Same-domain landing plus prefixed MVP deployment:

- `HEAD https://coocking-cart.speechbattle.com/` returns the landing showcase.
- `HEAD https://coocking-cart.speechbattle.com/mvp` returns the Demo MVP shell.
- `GET https://coocking-cart.speechbattle.com/mvp/api/config` returns `ok=true`.
- `POST /mvp/api/demo-login` followed by `GET /mvp/api/sessions` on the same cookie jar returns `ok=true`.
- Login/logout responses include `Path=/mvp` and root-cookie cleanup with `Path=/; Max-Age=0`.
- `GET https://coocking-cart.speechbattle.com/api/config` should not be served by the MVP app in prefixed mode.

## Stop rules

- Не считать локальный Docker build обязательным, если локальный Docker/Linux отсутствует или сломан.
- Не подменять server parity локальной IDE visibility.
- Не коммитить `.env`, API keys, SSH keys, tokens.
- Не трогать чужие контейнеры, сети и Traefik config вне `coocking-cart`.
- Не использовать strip-prefix middleware для `/mvp`, пока MVP сам обрабатывает `APP_BASE_PATH=/mvp`.
- Не деплоить незакоммиченный рабочий каталог.
- Не планировать `git pull` на сервере, пока `git` там явно не установлен и не зафиксирован в runbook.

## Где зафиксировано для будущих тестов

Та же архитектурная заметка продублирована sticky-комментарием в `tests/test_mvp_core.py`, чтобы она попадала в контекст при изменении тестов.
