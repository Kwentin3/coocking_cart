# MVP Gemini Live streaming voice research v0.1

- Статус: research note для следующей итерации голосового ввода
- Дата: 2026-05-27
- Контур: Demo MVP
- Связанный текущий контракт: [MVP voice input transcription blueprint](MVP_VOICE_INPUT_TRANSCRIPTION_BLUEPRINT_v0.1.md)

## Задача

Текущая схема голосового ввода выглядит так:

1. Браузер записывает аудио целиком.
2. Браузер отправляет готовый файл на сервер.
3. Сервер отправляет аудио в Gemini через обычный request/response вызов.
4. Пользователь ждёт полный результат транскрипции.

Это даёт заметный лаг: обработка начинается только после остановки записи и загрузки всего аудио. Для более естественного UX нужно проверить потоковую схему, где аудио уходит чанками, а промежуточные события возвращаются во время записи.

## Ключевой вывод

Для потокового голосового сценария в Gemini нужен не обычный `generateContent` с аудиофайлом, а `Gemini Live API`.

Официальная документация Google разделяет эти режимы:

- `generateContent` умеет понимать аудио, но не является real-time STT API.
- Для real-time voice/video взаимодействий Google указывает `Live API`.
- Для dedicated real-time speech-to-text Google отдельно указывает Google Cloud Speech-to-Text.

Практический вывод: Gemini Live API подходит для прототипа low-latency voice interaction, но если продуктовая цель останется строго "диктовка в textarea без голосового диалога", нужно отдельно проверить, достаточно ли нам `inputAudioTranscription` в Live API. Это не то же самое, что специализированный STT-сервис.

## Документальный домен

| Источник | Что фиксирует | Влияние на реализацию |
| --- | --- | --- |
| [Audio understanding](https://ai.google.dev/gemini-api/docs/audio) | Обычный Gemini audio input работает как анализ аудио в запросе; для real-time voice/video нужно смотреть Live API. | Текущий `/api/transcribe` остаётся batch-STT. Streaming нельзя строить поверх текущей схемы "готовый файл -> generateContent". |
| [Live API overview](https://ai.google.dev/gemini-api/docs/live-api) | Live API даёт low-latency real-time voice/vision через stateful WebSocket. Поддерживает server-to-server и client-to-server подходы. | Новый контур должен быть WebSocket/session-based, а не HTTP POST. |
| [Live API using GenAI SDK](https://ai.google.dev/gemini-api/docs/live-api/get-started-sdk) | SDK даёт `live.connect`, `send_realtime_input`, приём audio chunks и transcriptions. | Серверный Python backend может держать Gemini Live session через SDK, если выберем proxy-подход. |
| [Live API using raw WebSockets](https://ai.google.dev/gemini-api/docs/live-api/get-started-websocket) | Raw WSS endpoint, первый `setup`, затем `realtimeInput` с base64 PCM audio, приём `serverContent`. | Браузер может подключаться напрямую к Gemini Live, но только при безопасной авторизации. |
| [Live API WebSockets reference](https://ai.google.dev/api/live) | Контракты `BidiGenerateContentSetup`, `BidiGenerateContentRealtimeInput`, `BidiGenerateContentServerMessage`, `inputAudioTranscription`, `outputAudioTranscription`. | Нужен отдельный contract layer для live-событий; обычный `SttAdapter.transcribe(bytes)` не подходит. |
| [Live API capabilities](https://ai.google.dev/gemini-api/docs/live-api/capabilities) | Audio format, VAD, barge-in, transcriptions, session limitations, model capabilities. | Браузер должен слать raw PCM 16-bit, желательно 16 kHz mono; UI должен учитывать VAD/turn events. |
| [Ephemeral tokens](https://ai.google.dev/gemini-api/docs/live-api/ephemeral-tokens) | Для client-to-server подключения из браузера рекомендуется short-lived token, выдаваемый backend. | API key нельзя класть в frontend. Нужен backend endpoint для выдачи ephemeral token. |
| [Session management](https://ai.google.dev/gemini-api/docs/live-api/session-management) | Audio-only sessions limited, WebSocket connection может завершаться, есть session resumption/compression. | Даже для MVP нужен lifecycle: reconnect, close, timeout, graceful stop. |
| [Gemini 3.1 Flash Live Preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview) | Актуальная Live-модель для low-latency audio-to-audio; model id `gemini-3.1-flash-live-preview`. | Model id хранить в env/config. Не хардкодить в доменной логике. |
| [Gemini Live examples](https://github.com/google-gemini/gemini-live-api-examples) | Официальные примеры: Python SDK, raw WebSocket + ephemeral tokens, CLI audio streaming. | Использовать как практическую базу для spike, особенно browser + token example. |

Проверено по официальной документации Google AI на 2026-05-27.

## Технические факты из документации

- Протокол Live API: stateful WebSocket (`WSS`).
- Input audio: raw 16-bit PCM, little-endian; нативно 16 kHz, MIME вида `audio/pcm;rate=16000`.
- Output audio: raw 16-bit PCM, little-endian, 24 kHz.
- Клиентские сообщения: ровно один top-level тип за сообщение: `setup`, `clientContent`, `realtimeInput` или `toolResponse`.
- Первый message после открытия сокета: `BidiGenerateContentSetup`.
- Для real-time audio используется `realtimeInput.audio`.
- Для транскрипции голоса в Live setup есть `inputAudioTranscription`.
- Транскрипции приходят независимо от остальных server messages; порядок событий не гарантирован.
- При автоматическом VAD, если микрофон остановлен/пауза больше секунды, нужно отправлять `audioStreamEnd`.
- Если automatic VAD выключен, клиент сам отправляет `activityStart` и `activityEnd`.
- Для прямого подключения браузера нужен ephemeral token; обычный API key в браузер не кладём.
- Live API сейчас в preview, значит модельные id и ограничения надо проверять перед реализацией и деплоем.

## Две возможные архитектуры

### Вариант A: server-to-server streaming proxy

Поток:

```text
Browser mic -> our WebSocket endpoint -> backend Gemini Live session -> backend -> Browser UI
```

Плюсы:

- API key остаётся только на сервере.
- Проще контролировать auth, лимиты, аудит, provider errors.
- Легче встроить в текущие backend runtime boundaries.
- Можно централизованно нормализовать live-события.
- Можно применить server-side SOCKS5 transport для Gemini Live WSS, если прямое подключение из текущей локации не принимается provider.

Минусы:

- Остаётся лишний сетевой hop.
- Сервер держит долгие WebSocket-сессии и аудио-трафик.
- Нужно писать proxy backpressure, reconnect, cancellation.

Подходит, если важнее контроль backend и минимальный security risk.

### Вариант B: browser-to-Gemini direct через ephemeral token

Поток:

```text
Browser -> our /api/gemini-live-token -> Browser WSS -> Gemini Live API
Browser -> our app API only for final transcript/message persistence
```

Плюсы:

- Минимальная задержка: аудио не проксируется через наш backend.
- Backend не держит live audio stream.
- Это подход, который Google прямо рекомендует для лучшей latency при client-to-server streaming.

Минусы:

- Нужен token provisioning endpoint.
- Часть realtime-событий обходит backend, значит отдельно решаем audit/debug.
- Frontend становится владельцем live-session lifecycle.
- Нужно аккуратно ограничивать token: `uses`, TTL, model/config constraints.
- Браузерный JavaScript не может назначить SOCKS5 proxy для `WebSocket`/`fetch` и не должен получать SOCKS5 credentials. Если нужен SOCKS5, direct browser-to-Gemini режим заменяется backend WebSocket proxy.

Подходит для UX-focused spike и демо, если нас устраивает, что backend видит только итоговый transcript или отдельные клиентские telemetry events.

## Консервативная рекомендация для spike

Начать с варианта B как изолированного spike рядом с текущим `/api/transcribe`, без удаления batch-STT. Если provider rejects по локации клиента или сервера, переключить `LIVE_VOICE_TRANSPORT=server_proxy` и держать SOCKS5 только в backend env.

Причина: текущая боль именно latency и user-friendliness. Прямой browser-to-Gemini поток через ephemeral token максимально проверяет, снимает ли Live API эту боль. Если spike покажет проблемы с качеством транскрипта, lifecycle или compliance, можно перейти к варианту A или выделить dedicated STT provider.

Не менять текущий chat flow на первом шаге:

- микрофон по-прежнему заполняет editable `messageInput`;
- transcript не auto-send;
- существующий `/api/sessions/{id}/messages` остаётся точкой отправки пользовательского текста;
- Live API на первом этапе используется только как streaming voice capture/transcription layer.

## Предлагаемые границы кода

| Область | Ответственность |
| --- | --- |
| Browser audio capture | `getUserMedia`, Web Audio / AudioWorklet, ресемплинг в PCM16 16 kHz mono, чанки, stop/cancel. |
| Live session client | Открытие WSS/SDK session, отправка `setup`, `realtimeInput.audio`, `audioStreamEnd`, обработка `serverContent`. |
| Token provisioning API | Auth текущего пользователя, создание short-lived ephemeral token, model/config constraints, user-safe errors. |
| UI state | `idle`, `connecting`, `recording`, `streaming`, `receiving_transcript`, `stopping`, `error`, `unsupported`. |
| Transcript buffer | Сбор incremental `inputTranscription.text`, дедупликация/склейка, финальная вставка в textarea. |
| Provider config | `LIVE_VOICE_ENABLED`, `LIVE_VOICE_MODEL`, token TTL, max session seconds, VAD mode, chunk size. |
| Observability | Latency markers: mic start, WSS open, first audio sent, first transcript received, stop, final transcript inserted. |

## Минимальные контракты spike

### Token endpoint

```http
POST /api/live-voice/token
```

Response:

```json
{
  "ok": true,
  "token": "<ephemeral-token>",
  "model": "gemini-3.1-flash-live-preview",
  "expires_at": "2026-05-27T12:34:56Z"
}
```

Ошибки должны быть user-safe, без provider raw error и без секретов.

### Live setup

Raw WebSocket shape:

```json
{
  "setup": {
    "model": "models/gemini-3.1-flash-live-preview",
    "generationConfig": {
      "responseModalities": ["AUDIO"]
    },
    "inputAudioTranscription": {},
    "realtimeInputConfig": {
      "automaticActivityDetection": {
        "disabled": false
      }
    },
    "systemInstruction": {
      "parts": [
        {
          "text": "Transcribe Russian food-service recipe and tech-card dictation accurately. Do not auto-submit anything."
        }
      ]
    }
  }
}
```

Важно: точный shape может отличаться между SDK и raw WSS casing. Перед реализацией сверить с выбранным SDK/raw endpoint.

### Audio chunk

```json
{
  "realtimeInput": {
    "audio": {
      "data": "<base64-pcm16-chunk>",
      "mimeType": "audio/pcm;rate=16000"
    }
  }
}
```

### Stop with automatic VAD

```json
{
  "realtimeInput": {
    "audioStreamEnd": true
  }
}
```

### Incoming transcript event

```json
{
  "serverContent": {
    "inputTranscription": {
      "text": "текст пользователя"
    }
  }
}
```

Клиент не должен полагаться на строгий порядок `inputTranscription`, `modelTurn`, `turnComplete`.

## UX contract для streaming voice input

- Первый клик по микрофону открывает live session и начинает стриминг.
- Пользователь видит, что соединение открывается, а потом запись активна.
- Частичный transcript можно показывать как черновик, но не отправлять.
- Stop завершает аудио-поток и вставляет финальный transcript в textarea.
- Cancel закрывает live session и отбрасывает transcript buffer.
- Если соединение оборвалось, UI показывает короткую ошибку и сохраняет уже полученный черновик отдельно от отправленного сообщения.
- Send обычного chat message остаётся заблокированным во время активной записи, если это уже текущий UX-инвариант.

## Риски и проверки

- **Live API не dedicated STT.** Нужно проверить, насколько `inputAudioTranscription` подходит для диктовки без полноценного voice chat.
- **Preview API.** Model id и ограничения могут меняться; хранить model id в env и проверять перед релизом.
- **Structured output не поддерживается у Live model.** Live layer не должен пытаться заменить основной chat LLM turn.
- **Audio conversion in browser.** Нужен стабильный PCM16 16 kHz mono pipeline; `MediaRecorder` blobs недостаточны для raw Live input без преобразования.
- **Ordering.** Transcription events приходят независимо; нужен устойчивый transcript buffer.
- **Token leakage.** Ephemeral token всё равно извлекаем из frontend; ограничивать TTL, uses и config.
- **Session lifecycle.** Учесть connection close около 10 минут и audio-only session limit около 15 минут, даже если MVP ограничит запись 180 секундами.
- **Cost/traffic.** Streaming audio увеличивает количество событий и держит соединение открытым.

## Минимальный план верификации

1. Поднять отдельный frontend-only proof с ephemeral token endpoint.
2. Проверить Chrome desktop: start -> first partial transcript latency -> stop -> textarea insert.
3. Проверить русский диктант с числами, граммами, процентами, температурами, `брутто/нетто`, `ТК/ТТК`.
4. Проверить cancel без сохранения transcript.
5. Проверить потерю WSS соединения и user-safe recovery.
6. Сравнить latency против текущего `/api/transcribe`: время до первого видимого текста и время до финального текста.
7. Если `inputAudioTranscription` нестабилен для dictation-only UX, зафиксировать fallback: server-to-server streaming или dedicated Google Cloud Speech-to-Text.

## Реализованный MVP-slice

- Backend endpoint: `POST /api/live-voice/token`.
- Provider boundary: `app/live_voice.py`, `LiveVoiceAdapter`, `GeminiLiveVoiceAdapter`, `make_live_voice_adapter`.
- Runtime routing: `DemoRuntime.create_live_voice_token`.
- Direct frontend path: browser получает ephemeral token, открывает WSS напрямую в Gemini Live API, отправляет `setup`, затем `realtimeInput.audio` чанками PCM16.
- Server proxy path: browser получает backend WSS URL `/api/live-voice/ws/<session>`, отправляет тот же `setup`/`realtimeInput.audio`, а backend relays WebSocket frames в Gemini Live. SOCKS5 применяется только на backend стороне при наличии `LIVE_VOICE_SOCKS5_HOST`.
- Fallback: если streaming недоступен, UI использует текущий batch-STT `/api/transcribe`.
- Chat invariant: transcript вставляется в editable textarea и не отправляется автоматически.

## Deferred work

- Voice chat с аудио-ответом ассистента.
- Tool calls из Live API.
- Расширенный audit/backpressure для server-side proxy.
- Session resumption для долгих разговоров.
- WebRTC/LiveKit/Pipecat интеграции.
- Persistent transcript audit trail.
