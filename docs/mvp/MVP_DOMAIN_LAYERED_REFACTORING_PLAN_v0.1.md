# MVP domain-layered refactoring plan v0.1

- Status: active implementation plan; backend route split slice completed
- Date: 2026-05-27
- Scope: Demo MVP codebase after Live Voice, Markdown chat rendering and SQLite hardening

## Goal

Разнести текущие монолитные поверхности по доменам и слоям так, чтобы контракты были явными, а новые фичи не требовали менять `app/main.py`, `app/storage.py` и `app/static/app.js` одновременно.

Не цель: переписать проект на новый framework, заменить SQLite или построить production IAM. Рефакторинг должен идти малыми проверяемыми срезами с сохранением текущих route URL, JSON response shapes и UI-поведения.

## Implementation Status

2026-05-27 backend slice completed:

- `app/main.py` remains the stdlib `ThreadingHTTPServer` entrypoint and owns static files, raw request/response IO helpers, session helpers and the socket-bound Live Voice WebSocket relay.
- Cookie contract moved to `app/http/cookies.py`: `COOKIE_NAME`, `build_session_cookie_header`, and `should_use_secure_session_cookie`.
- JSON route orchestration moved by domain to `app/routes/config_routes.py`, `auth_routes.py`, `chat_routes.py`, `admin_routes.py`, and `voice_routes.py`.
- Route modules receive only `RouteContext`; this keeps direct `BaseHTTPRequestHandler` usage out of domain route functions.
- `app/routes/contracts.py` records the explicit method/path/domain/guard map. Test `test_route_domain_contracts_keep_protected_routes_explicit` is the anti-drift check for protected routes.
- `POST /api/demo-login` now drains its optional JSON body before responding, so HTTP/1.1 keep-alive clients do not leak `{}` into the next request line.
- API URLs, JSON keys and UI behavior were intentionally preserved. Frontend `app/static/app.js` is still a later slice.

## Target Layers

| Layer | Owns | Must not own |
| --- | --- | --- |
| `edge/http` | HTTP parsing, cookies, response helpers, path matching, WebSocket upgrade shell | domain rules, SQL, provider payloads |
| `api routes` | route-level orchestration, auth/admin guards, DTO mapping | provider calls directly, raw SQL |
| `application/runtime` | turn orchestration, context assembly, provider adapter calls, user-safe errors | HTTP status/cookies, DOM/UI state |
| `domain contracts` | typed DTO/read-model shapes for sessions, messages, turn result, voice token, config | transport-specific details |
| `persistence` | SQLite repositories, migrations, read models | HTTP request/session identity, provider logic |
| `integrations` | Gemini LLM/STT/Live Voice adapters, SOCKS5/WebSocket transport | UI copy, storage decisions |
| `frontend UI modules` | browser state, rendering, events, voice client, markdown rendering | API internals, SOCKS5/provider secrets |

## Domain Map

| Domain | Backend modules after refactor | Frontend modules after refactor | Contract boundary |
| --- | --- | --- | --- |
| Auth/session | `app/http/cookies.py`, `app/routes/auth_routes.py`, `app/storage/users.py` | `static/js/auth.js`, `static/js/system_menu.js` | `CurrentUserDTO`, `LoginResponse`, cookie policy |
| Chat/session | `app/routes/chat_routes.py`, `app/runtime.py`, `app/storage/chat.py` | `static/js/chat.js`, `static/js/sessions.js` | `ChatSessionDTO`, `MessageDTO`, `SendMessageResponse` |
| Structured result/artifact | `app/storage/turns.py`, `app/structured_output.py` | `static/js/artifacts.js` | `StructuredOutput`, `TurnResultDTO` |
| Admin/demo ops | `app/routes/admin_routes.py`, `app/storage/admin.py` | `static/js/admin.js` | `AdminUserDTO`, `DashboardDTO`, read-only context payload |
| Context pack | `app/context_loader.py`, future `app/context_contracts.py` | `static/js/inspector.js` | `ContextPackDTO`, manifest/layer metadata |
| Voice/STT | `app/routes/voice_routes.py`, `app/stt.py`, `app/live_voice.py`, `app/live_voice_proxy.py` | `static/js/voice.js` | `VoiceInputConfig`, `TranscriptionResponse`, `LiveVoiceSessionDTO` |
| Config/health | `app/config.py`, `app/routes/config_routes.py` | `static/js/config.js` | public config only, no secrets |

## Slice 1: Contract Definitions Before Extraction

Problem: if files are split before response contracts are named, drift can hide inside the refactor.

Work:

1. Create `app/contracts.py` or small domain contract files with typed dict/dataclass helpers for public DTOs.
2. Keep JSON keys identical to current API.
3. Add tests that validate representative response shapes for `/api/me`, `/api/config`, session list, send message, live voice token and admin dashboard.

Acceptance:

- No route URL changes.
- No UI changes.
- Existing tests pass plus response-shape tests.

## Slice 2: HTTP Edge Helpers

Problem: `DemoMvpHandler` owns parsing, cookies, JSON response, auth and route behavior.

Work:

1. Extract cookie header building and request HTTPS detection to `app/http/cookies.py`.
2. Extract JSON/audio body parsing and response helpers to `app/http/request_response.py`.
3. Keep `DemoMvpHandler` as the server entrypoint.
4. Keep terminal response behavior explicit: every route returns after sending response.

Acceptance:

- Secure cookie tests remain green.
- Oversized JSON/message limits can be added later in this layer without touching runtime.

## Slice 3: Route Modules By Domain

Problem: manual `if parsed.path` chains mix unrelated route ownership.

Work:

1. Introduce a tiny route table that maps `(method, path pattern)` to route handlers.
2. Move auth/session/admin/voice route functions into `app/routes/*_routes.py`.
3. Route handlers receive an explicit request context: config, storage, runtime, current user helpers, parsed body.
4. Preserve all current JSON shapes.

Acceptance:

- Anti-drift test lists protected routes and required guard: user/admin/public.
- Handler still runs on stdlib `ThreadingHTTPServer`.

## Slice 4: Persistence Repositories

Problem: `Storage` mixes users, auth sessions, chat sessions, messages, turn results, admin metrics and migrations.

Work:

1. Keep one SQLite connection/transaction owner.
2. Split repository classes by domain, created from a provided connection/transaction context.
3. Keep `Storage` as facade initially, so runtime/routes do not change all at once.
4. Move migrations into `app/storage_migrations.py` or `app/storage/migrations.py` only after facade tests are stable.

Acceptance:

- No direct SQL leaks into route/runtime modules.
- Existing storage methods remain as compatibility facade until callers are migrated.
- Schema migration tests cover fresh and legacy DB.

## Slice 5: Frontend Static Modules Without Build Step

Problem: `app/static/app.js` owns chat, admin, voice, artifacts, markdown and global event wiring.

Work:

1. Keep static files and no bundler.
2. Add `window.CookingCart = {}` namespace.
3. Split in script-load order:
   - `static/js/state.js`
   - `static/js/api.js`
   - `static/js/render_helpers.js`
   - `static/js/chat.js`
   - `static/js/voice.js`
   - `static/js/sessions.js`
   - `static/js/artifacts.js`
   - `static/js/admin.js`
   - `static/js/bootstrap.js`
4. Move CSS by sections only if it does not create asset churn; otherwise add section anchors first.

Acceptance:

- Current DOM ids/classes stay stable.
- Markdown renders only assistant output.
- User messages remain plain text.
- Batch/Live voice visual contracts stay unchanged.
- Browser smoke test covers one chat send and one Markdown response.

## Slice 6: Provider Factory Parity

Problem: STT and Live Voice use factories, LLM currently constructs `GeminiAdapter` directly.

Work:

1. Add `LlmAdapter` boundary and `make_llm_adapter(config)`.
2. Runtime depends on the factory, not concrete Gemini class.
3. Keep only Gemini implementation until a real second provider exists.

Acceptance:

- No route/UI imports provider concrete classes.
- Gemini structured output payload tests remain at adapter boundary.

## Deferred Work

- JSON/body/message size limits: accepted debt, to be fixed in HTTP edge layer.
- Live Voice forensic logging: accepted debt, to be fixed after route/transport boundaries are cleaner.
- Production IAM/RBAC, tenant model, RLS and audit/event log: future production track.
- Framework migration: not justified until stdlib edge layer blocks real requirements.

## Validation Plan

Each slice must run:

```powershell
python -m unittest discover -s tests
python -m compileall app tests scripts
node --check app/static/app.js
```

If a slice changes packaging/imports/static assets, also run artifact simulation or server-side build according to `docs/ops/LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md`.
