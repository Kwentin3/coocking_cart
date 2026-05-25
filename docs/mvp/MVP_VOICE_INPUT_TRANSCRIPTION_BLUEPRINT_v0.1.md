# MVP voice input transcription blueprint v0.1

- Статус: implementation blueprint для малой фичи
- Дата: 2026-05-25
- Контур: Demo MVP

## Goal

Добавить голосовой ввод как транскрибацию аудио в редактируемый текст chat input.

Голос не создает отдельный сценарий общения. После транскрибации пользователь видит текст, может исправить числа, ингредиенты, брутто/нетто, температуры и только потом отправляет обычное сообщение в существующий chat flow.

## Non-goals

- Нет voice chat.
- Нет голосовых ответов ассистента.
- Нет auto-send после распознавания.
- Нет realtime/streaming STT.
- Нет хранения аудио после обработки.
- Нет новых prompt/context layers для STT.
- Нет отдельной истории voice events в SQLite.

## Domain and ownership

| Area | Owner | Responsibility |
| --- | --- | --- |
| Browser UI | `app/static/app.js`, `app/templates/index.html`, `app/static/styles.css` | Запись, таймер, countdown, cancel, отправка audio bytes, вставка transcript в textarea. |
| HTTP boundary | `app/main.py` | Auth, size/duration validation, raw audio body, response status. |
| Runtime orchestration | `app/runtime.py` | User-safe STT response, adapter call, normalized errors. |
| Provider boundary | `app/stt.py` | `SttAdapter`, Gemini STT adapter, factory, provider payload. |
| Config | `app/config.py`, `.env.example` | STT provider/model/key/limits without secrets in Git. |
| Existing chat flow | current `/api/sessions/{id}/messages` | Unchanged. Transcript becomes normal user-edited text. |

## UX contract

- Voice button is on/off, not hold-to-talk.
- First click starts recording.
- Second click stops recording and sends audio to transcription.
- Cancel stops recording and discards audio without provider call.
- Max recording length: 180 seconds.
- Last 15 seconds show explicit auto-stop countdown.
- During recording/transcription, normal send is disabled.
- On success, transcript is inserted into `messageInput`, not sent.
- If `messageInput` already contains text, transcript is appended on a new line.
- User can edit transcript before sending.

Visible states:

- `idle`: mic button enabled.
- `recording`: stop button, cancel button, elapsed timer.
- `countdown`: recording state plus "auto-stop in N sec".
- `transcribing`: controls disabled, visible progress text.
- `success`: transcript inserted, status says it can be edited.
- `error`: visible short error and retry path.
- `unsupported`: mic button disabled if browser audio capture is unavailable.

## API contract

### `POST /api/transcribe`

Auth: logged-in user.

Request:

- `Content-Type: audio/wav`
- `Content-Type: audio/mp4` for `.m4a` test uploads
- `X-Audio-Duration-Ms: <integer>`
- raw audio bytes in request body

Limits:

- duration must be `1..180000` ms;
- body must be non-empty;
- body must not exceed configured `STT_MAX_AUDIO_BYTES`;
- accepted MIME type for browser path: `audio/wav`;
- accepted MIME type for direct `.m4a` tests: `audio/mp4` (`audio/m4a` and `audio/x-m4a` normalize to `audio/mp4`).

Response success:

```json
{
  "ok": true,
  "text": "распознанный текст",
  "provider": "gemini",
  "model": "gemini-flash-latest"
}
```

Response failure:

```json
{
  "ok": false,
  "error": "Не удалось распознать аудио."
}
```

No raw provider errors, API keys or secrets are returned to user.

## STT adapter contract

```python
class SttAdapter:
    def transcribe(self, audio_bytes: bytes, mime_type: str, duration_ms: int | None = None) -> SttResult:
        ...
```

Factory:

```python
def make_stt_adapter(config: AppConfig) -> SttAdapter:
    ...
```

For Demo MVP only `gemini` is implemented. Factory is still useful because STT is a separate provider capability from chat LLM.

## Gemini STT approach

Use Gemini `generateContent` with inline audio data and a strict transcription prompt.

Reasoning from official Gemini docs:

- Gemini supports audio input for transcription through `generateContent`.
- Inline audio is acceptable for requests up to 20 MB total.
- Files API is recommended when total request size exceeds 20 MB.
- Real-time transcription is not needed for this feature.
- The browser recording path sends `audio/wav`; `.m4a` test files are sent as `audio/mp4`.

Reference:

- https://ai.google.dev/gemini-api/docs/audio
- https://ai.google.dev/gemini-api/docs/files

Browser records WAV PCM 16 kHz mono to avoid relying on browser `audio/webm` compatibility with Gemini.

## Transcription prompt

```text
Транскрибируй русскую речь в текст.
Не отвечай на содержание, не суммаризируй и не исправляй смысл.
Сохраняй числа, граммы, килограммы, проценты, температуры, время и единицы измерения максимально точно.
Термины предметной области: ТК, ТТК, брутто, нетто, выход, БЖУ, ХАССП, СанПиН, iiko, r_keeper, StoreHouse, 1С.
Если фрагмент неразборчив, пометь его как [неразборчиво].
Верни только текст транскрипта.
```

## Environment contract

| Variable | Default | Purpose |
| --- | --- | --- |
| `STT_ENABLED` | `true` | Enables `/api/transcribe`. |
| `STT_PROVIDER` | `gemini` | STT provider. |
| `STT_MODEL` | fallback to `LLM_MODEL` | Gemini model for transcription. |
| `STT_API_KEY` | fallback to `LLM_API_KEY` / `GEMINI_API_KEY` | Provider key, never committed. |
| `STT_BASE_URL` | fallback to `LLM_BASE_URL` | Optional compatible base URL. |
| `STT_TIMEOUT_SECONDS` | `90` | Provider timeout. |
| `STT_MAX_AUDIO_SECONDS` | `180` | Recording duration limit. |
| `STT_COUNTDOWN_SECONDS` | `15` | UI countdown window. |
| `STT_MAX_AUDIO_BYTES` | `12000000` | Server body limit. |

## Implementation slices

1. Add blueprint/docs/env contract.
2. Add config fields and `.env.example`.
3. Add `app/stt.py` adapter factory and Gemini inline audio request.
4. Add `DemoRuntime.transcribe_audio`.
5. Add `POST /api/transcribe` route.
6. Add browser WAV recorder and UI states.
7. Add tests for config, adapter payload and runtime validation.
8. Verify local tests, build artifact and server deployment.

## Acceptance checks

- User can click voice button, record, stop and receive transcript in textarea.
- User can cancel recording without provider call.
- Recording auto-stops at 180 seconds.
- Countdown is visible during the last 15 seconds.
- Transcript is never auto-sent.
- Send button is disabled while recording/transcribing.
- Backend rejects unauthenticated, empty, oversized, too-long or unsupported audio.
- Gemini call goes through STT adapter, not directly from UI or route.
- Audio bytes are not persisted.

## Deferred work

- Streaming transcription.
- Speaker diarization.
- Audio upload via Gemini Files API for large files.
- Dedicated Google Cloud Speech-to-Text provider.
- Persistent transcript audit trail.
