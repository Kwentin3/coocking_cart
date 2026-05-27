# MVP environment contract v0.1

- Статус: минимальный контракт переменного окружения Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Environment contract фиксирует, какие runtime-настройки будущая реализация должна получать из окружения или безопасного config layer.

Принцип: никакие секреты, API keys, passwords, provider settings, bootstrap credentials и deployment details не хардкодятся в коде и не хранятся в репозитории.

Этот документ не является реальным `.env`, не содержит секреты и не является production secrets management design.

В корне репозитория есть безопасный шаблон [`.env.example`](../../.env.example). Его можно коммитить только потому, что он содержит non-secret deployment values и placeholders для секретов. Реальные значения должны жить в локальном `.env`, runtime environment или другом безопасном secrets/config layer вне Git.

Известный deployment context можно фиксировать в документации, если он не содержит секретов. Для текущего Demo MVP известны:

- `APP_BASE_URL=https://coocking-cart.speechbattle.com`;
- `PUBLIC_DOMAIN=coocking-cart.speechbattle.com`;
- `DEPLOY_HOST=91.132.48.224`;
- `DEPLOY_USER=root`.

Эти значения не заменяют реальные secrets и не являются готовым `.env`.

В `.env.example` эти non-secret значения уже могут быть заполнены:

- `APP_BASE_URL=https://coocking-cart.speechbattle.com`;
- `PUBLIC_DOMAIN=coocking-cart.speechbattle.com`;
- `DEPLOY_HOST=91.132.48.224`;
- `DEPLOY_USER=root`;
- `LLM_PROVIDER=gemini`.

Секреты и credentials остаются placeholders:

- `LLM_API_KEY=<GEMINI_API_KEY>`;
- `AUTH_SESSION_SECRET=<AUTH_SESSION_SECRET>`;
- `BOOTSTRAP_ADMIN_EMAIL=<BOOTSTRAP_ADMIN_EMAIL>`;
- `BOOTSTRAP_ADMIN_PASSWORD=<BOOTSTRAP_ADMIN_PASSWORD>`;
- `BOOTSTRAP_ADMIN_PASSWORD_HASH=`.

## Общие правила

- В документации используются только placeholder-значения для секретов.
- Реальные secrets передаются отдельно безопасным способом.
- `.env` с реальными значениями не коммитится.
- `.env.example` является безопасным шаблоном: non-secret deployment values могут быть заполнены, secrets всегда остаются placeholders.
- Код доменной логики не должен напрямую зависеть от конкретных значений environment.

## Placeholder validation

Любое значение вида `<...>` в `.env.example` является placeholder и должно считаться `not configured`.

Это относится, в том числе, к:

- `<GEMINI_API_KEY>`;
- `<GEMINI_FLASH_MODEL_ID>` или любой будущий placeholder вида `<...>`;
- `<BOOTSTRAP_ADMIN_EMAIL>`;
- `<BOOTSTRAP_ADMIN_PASSWORD>`;
- `<AUTH_SESSION_SECRET>`;
- `<TRAEFIK_NETWORK_NAME>`;
- `<TRAEFIK_ENTRYPOINT>`;
- `<TRAEFIK_CERTRESOLVER>`;
- любым будущим placeholder-значениям.

Правило: реализация не должна принимать placeholder как реальное значение. Если обязательная переменная пустая или содержит `<...>`, приложение должно показать user-safe ошибку конфигурации и admin/debug hint. Обычный пользователь не должен видеть stack trace, secrets или raw provider error.

Для optional/future переменных placeholder означает, что соответствующая функция не настроена и не должна использоваться без отдельной конфигурации.

## Минимальные группы переменных

### App/runtime

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `APP_ENV` | Да | `<APP_ENV>` | Режим приложения: demo/local/stage. |
| `APP_NAME` | Да | `<APP_NAME>` | Человекочитаемое имя приложения. |
| `APP_BASE_URL` | Optional | `<APP_BASE_URL>` | Базовый URL будущего приложения, если нужен runtime. |

### Auth/bootstrap

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `BOOTSTRAP_ADMIN_EMAIL` | Да | `<BOOTSTRAP_ADMIN_EMAIL>` | Идентификатор первого admin. |
| `BOOTSTRAP_ADMIN_PASSWORD` | Optional | `<BOOTSTRAP_ADMIN_PASSWORD>` | Bootstrap password, если используется plain bootstrap flow. |
| `BOOTSTRAP_ADMIN_PASSWORD_HASH` | Optional | `<BOOTSTRAP_ADMIN_PASSWORD_HASH>` | Bootstrap password hash, если plain password не используется. |
| `AUTH_SESSION_SECRET` | Да | `<AUTH_SESSION_SECRET>` | Секрет подписи/шифрования сессии. |

Правило: использовать либо `BOOTSTRAP_ADMIN_PASSWORD`, либо `BOOTSTRAP_ADMIN_PASSWORD_HASH`, но не хранить реальные значения в репозитории.

### Database

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `SQLITE_DB_PATH` | Да | `<SQLITE_DB_PATH>` | Путь к SQLite-файлу Demo MVP. |
| `DATABASE_URL` | Optional/future | `<DATABASE_URL>` | Future-compatible database URL, если SQLite path будет заменен. |

Для Demo MVP достаточно SQLite. Production database design остается future track.

### LLM provider

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `LLM_PROVIDER` | Да | `gemini` или `<LLM_PROVIDER>` | Имя выбранного LLM provider. Для MVP ожидается `gemini`. |
| `LLM_MODEL` | Да | `gemini-flash-latest` или `<GEMINI_FLASH_MODEL_ID>` | Имя модели. Exact id задается через env и должен быть проверен по актуальной документации Google AI перед первым LLM call. |
| `LLM_API_KEY` | Да | `<GEMINI_API_KEY>` | API key provider. |
| `LLM_BASE_URL` | Optional | `<LLM_BASE_URL>` | Base URL для совместимых API, если нужен. |
| `LLM_TIMEOUT_SECONDS` | Optional | `<LLM_TIMEOUT_SECONDS>` | Timeout вызова LLM. |

Gemini является target provider family для Demo MVP, но доменная логика не должна хардкодить Gemini SDK, endpoint или model id. Вызов LLM должен идти через provider adapter boundary. Provider factory и capability matrix не входят в MVP.

Для первой реализации ожидается `LLM_PROVIDER=gemini`. `LLM_MODEL` берется только из env/config: если там placeholder вида `<...>`, значение считается not configured; если там конкретный non-secret model id из `.env.example`, агент реализации все равно должен проверить его актуальность по официальной документации Google AI перед первым LLM call. `LLM_API_KEY` не коммитится и передается только через реальный runtime env или secrets layer.

### STT provider

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `STT_ENABLED` | Optional | `<STT_ENABLED>` | Включает голосовой ввод через `/api/transcribe`. |
| `STT_PROVIDER` | Optional | `gemini` или `<STT_PROVIDER>` | STT provider. Для Demo MVP ожидается `gemini`. |
| `STT_MODEL` | Optional | `<GEMINI_FLASH_MODEL_ID>` | Модель для транскрибации; если пусто, используется `LLM_MODEL`. |
| `STT_API_KEY` | Optional | `<GEMINI_API_KEY>` | API key для STT; если пусто, используется `LLM_API_KEY` / `GEMINI_API_KEY`. |
| `STT_BASE_URL` | Optional | `<STT_BASE_URL>` | Base URL для совместимого Gemini API, если нужен. |
| `STT_TIMEOUT_SECONDS` | Optional | `<STT_TIMEOUT_SECONDS>` | Timeout вызова STT provider. |
| `STT_MAX_AUDIO_SECONDS` | Optional | `<STT_MAX_AUDIO_SECONDS>` | Максимальная длительность записи. Для текущего UX: 180 секунд. |
| `STT_COUNTDOWN_SECONDS` | Optional | `<STT_COUNTDOWN_SECONDS>` | За сколько секунд до автостопа показывать countdown. Для текущего UX: 15 секунд. |
| `STT_MAX_AUDIO_BYTES` | Optional | `<STT_MAX_AUDIO_BYTES>` | Максимальный размер raw audio upload. |

STT является отдельной provider capability. UI и route не должны вызывать Gemini напрямую: транскрибация идет через adapter/factory boundary. Аудио не хранится после обработки.

### Voice transcription policy

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `VOICE_TRANSCRIPTION_LANGUAGE` | Optional | `русский` | Предпочтительный язык транскрипта для batch STT и Live input transcription. |
| `VOICE_TRANSCRIPTION_SCRIPT` | Optional | `кириллица` | Предпочтительный алфавит/скрипт. Для Gemini Live это prompt-level preference, не API `languageCode`. |
| `VOICE_TRANSCRIPTION_LATIN_ALLOWLIST` | Optional | `iiko, r_keeper, StoreHouse, HACCP` | Термины, которые разрешено оставлять латиницей. |
| `VOICE_TRANSCRIPTION_DOMAIN_TERMS` | Optional | `ТК, ТТК, ...` | Предметные термины, которые prompt просит сохранять точно. |
| `VOICE_TRANSCRIPTION_UNCLEAR_MARKER` | Optional | `[неразборчиво]` | Маркер для неразборчивых фрагментов. |
| `VOICE_TRANSCRIPTION_EXTRA_INSTRUCTION` | Optional | empty | Дополнительное правило транскрипции без замены всего prompt. |
| `VOICE_TRANSCRIPTION_PROMPT_OVERRIDE` | Optional | empty | Полная замена prompt для обоих STT transport paths. Использовать осторожно: override должен сохранять запрет на автоответ и автоотправку. |

Эта policy применяется к обоим STT transport paths: batch `/api/transcribe` и Live `/api/live-voice/token`. Для Gemini Live `inputAudioTranscription` не имеет собственного поля `languageCode`; язык и script задаются через `systemInstruction`.

### Live Voice provider

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `LIVE_VOICE_ENABLED` | Optional | `true` или `<LIVE_VOICE_ENABLED>` | Включает потоковый голосовой ввод через `/api/live-voice/token` и Gemini Live API. |
| `LIVE_VOICE_PROVIDER` | Optional | `gemini` или `<LIVE_VOICE_PROVIDER>` | Provider потокового голоса. Для Demo MVP ожидается `gemini`. |
| `LIVE_VOICE_MODEL` | Optional | `gemini-3.1-flash-live-preview` | Live API модель. Model id хранится только в env/config. |
| `LIVE_VOICE_API_KEY` | Optional | `<GEMINI_API_KEY>` | API key для выдачи ephemeral token; если пусто, используется `STT_API_KEY` / `LLM_API_KEY` / `GEMINI_API_KEY`. |
| `LIVE_VOICE_BASE_URL` | Optional | `<LIVE_VOICE_BASE_URL>` | Base URL Gemini API; по умолчанию `https://generativelanguage.googleapis.com`. |
| `LIVE_VOICE_TIMEOUT_SECONDS` | Optional | `<LIVE_VOICE_TIMEOUT_SECONDS>` | Timeout backend-вызова создания ephemeral token. |
| `LIVE_VOICE_TOKEN_TTL_SECONDS` | Optional | `<LIVE_VOICE_TOKEN_TTL_SECONDS>` | Срок действия ephemeral token для сообщений в Live session. |
| `LIVE_VOICE_NEW_SESSION_SECONDS` | Optional | `<LIVE_VOICE_NEW_SESSION_SECONDS>` | Окно, в течение которого по token можно открыть новую Live session. |
| `LIVE_VOICE_INPUT_SAMPLE_RATE` | Optional | `16000` | Sample rate PCM16 mono, который браузер стримит в Live API. |
| `LIVE_VOICE_RESPONSE_MODALITY` | Optional | `AUDIO` | Response modality Live session. Gemini Live стабильно подтверждает setup с `AUDIO`; UI для диктовки использует `serverContent.inputTranscription` и игнорирует audio output. |
| `LIVE_VOICE_TRANSPORT` | Optional | `direct_client` или `server_proxy` | Transport mode. `direct_client` выдаёт браузеру Gemini ephemeral token и прямой WSS URL; `server_proxy` выдаёт браузеру только backend WSS URL. |
| `LIVE_VOICE_SOCKS5_HOST` | Optional/secret-adjacent | `<SOCKS5_HOST_OR_IP>` | SOCKS5 host/IP для server-side Live Voice transport. Поддерживаются aliases `LIVE_VOICE_SOCKS5_IP` и `LIVE_VOICE_SOCKS5_SERVER`. |
| `LIVE_VOICE_SOCKS5_PORT` | Optional | `1080` | SOCKS5 port. |
| `LIVE_VOICE_SOCKS5_USERNAME` | Optional/secret | `<SOCKS5_USERNAME>` | SOCKS5 username. Не передаётся в frontend и не коммитится. |
| `LIVE_VOICE_SOCKS5_PASSWORD` | Optional/secret | `<SOCKS5_PASSWORD>` | SOCKS5 password. Не передаётся в frontend и не коммитится. |

Live Voice является отдельной provider capability от batch-STT. Route `/api/live-voice/token` всегда проходит через `LiveVoiceAdapter`/`make_live_voice_adapter`. В `direct_client` режиме браузер получает short-lived ephemeral token и подключается к Gemini Live API напрямую по WSS. В `server_proxy` режиме браузер получает только backend WebSocket URL `/api/live-voice/ws/<session>`, а backend открывает Gemini Live WSS, при наличии `LIVE_VOICE_SOCKS5_HOST`, через SOCKS5. API key, Gemini token в proxy mode и SOCKS5 credentials не передаются в frontend. Для production/demo с SOCKS5 ожидается `LIVE_VOICE_TRANSPORT=server_proxy`.

### Context files

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `CONTEXT_MANIFEST_PATH` | Да | `<CONTEXT_MANIFEST_PATH>` | Путь к `context_manifest.yml`. |
| `CONTEXT_LAYERS_DIR` | Да | `<CONTEXT_LAYERS_DIR>` | Путь к директории markdown context layers. |

Эти пути не должны быть глубоко захардкожены в доменной логике.

### Debug/demo

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `DEMO_MODE` | Да | `<DEMO_MODE>` | Явный режим Demo MVP. |
| `ENABLE_CONTEXT_INSPECTOR` | Optional | `<ENABLE_CONTEXT_INSPECTOR>` | Включение Context Inspector/debug view. |
| `ENABLE_LLM_TRACE` | Optional | `<ENABLE_LLM_TRACE>` | Включение минимального context trace. |

### Deployment placeholders

| Variable | Required | Placeholder | Назначение |
| --- | --- | --- | --- |
| `PUBLIC_DOMAIN` | Optional/future | `<PUBLIC_DOMAIN>` | Будущий публичный домен. |
| `DEPLOY_HOST` | Optional/future | `<DEPLOY_HOST>` | Будущий host для деплоя. |
| `DEPLOY_USER` | Optional/future | `<DEPLOY_USER>` | Будущий deploy user. |
| `TRAEFIK_NETWORK_NAME` | Optional/future | `<TRAEFIK_NETWORK_NAME>` | Будущее имя Traefik/Docker network, если применимо. |
| `TRAEFIK_ENTRYPOINT` | Optional/future | `<TRAEFIK_ENTRYPOINT>` | Имя Traefik entrypoint, если deployment будет подключаться через labels. |
| `TRAEFIK_CERTRESOLVER` | Optional/future | `<TRAEFIK_CERTRESOLVER>` | Имя Traefik certresolver, если TLS управляется Traefik. |

Для текущего deployment target известны `PUBLIC_DOMAIN`, `DEPLOY_HOST` и `DEPLOY_USER`. Read-only audit подтвердил Docker network `edge`, но final `TRAEFIK_NETWORK_NAME`, `TRAEFIK_ENTRYPOINT` и `TRAEFIK_CERTRESOLVER` должны быть подтверждены отдельным deployment task до создания compose/labels.

## Что нельзя хранить в репозитории

- Реальные `.env` файлы.
- API keys.
- Session secrets.
- Passwords.
- Password hashes реального окружения.
- SSH private keys.
- Private deployment credentials.
- Real `.env` values.
- Traefik/acme secrets.
- Internal secrets или tokens реального сервера.

Публичный deployment context, например domain, server IP и SSH user, может быть задокументирован в `docs/ops/`, если владелец проекта явно передал эти значения для будущего деплоя.

## Связь с `.env.example`

Root [`.env.example`](../../.env.example) является рабочим шаблоном для будущей реализации и deployment handoff.

Правила:

- `.env.example` можно копировать в локальный `.env`, но сам `.env` не коммитится.
- `APP_BASE_URL`, `PUBLIC_DOMAIN`, `DEPLOY_HOST`, `DEPLOY_USER` и `LLM_PROVIDER=gemini` могут быть заполнены как non-secret values.
- `LLM_MODEL` должен быть проверен по актуальной документации Google AI; placeholder вида `<...>` не может использоваться как реальная модель.
- `LLM_API_KEY`, `AUTH_SESSION_SECRET`, bootstrap admin password и password hash не коммитятся.
- Значения `<...>` должны валидироваться как `not configured`.
- Если runtime использует другой config layer вместо `.env`, он должен сохранять те же границы: non-secret config отдельно, secrets вне Git.

## Связанные документы

- [Bootstrap data contract](MVP_BOOTSTRAP_DATA_CONTRACT_v0.1.md)
- [Roles and access](MVP_ROLES_AND_ACCESS_v0.1.md)
- [LLM provider adapter note](MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md)
- [Voice input transcription blueprint](MVP_VOICE_INPUT_TRANSCRIPTION_BLUEPRINT_v0.1.md)
- [Ops environment notes](../ops/ENVIRONMENT_PREPARATION_NOTES_v0.1.md)
- [Safe env example](../../.env.example)
