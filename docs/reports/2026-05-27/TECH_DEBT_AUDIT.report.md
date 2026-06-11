# Technical Debt Audit: Demo MVP

- Date: 2026-05-27
- Last updated: 2026-05-27 after backend route split and release-artifact deploy
- Branch: implementation/demo-mvp
- Scope: repository code, docs, tests, deployment/runtime shape, current production health smoke
- Out of scope: reading secrets, deep penetration testing, full product/domain validation, load testing

## Executive Summary

The project is healthy for a Demo MVP: it has a small dependency surface, clear provider adapters for LLM/STT/Live Voice, centralized env config, documented runtime constraints, and tests covering the main contracts. The most important technical debt is not that the code is simple. The debt is that several MVP shortcuts now sit on active change paths: chat UI, voice streaming, auth/session handling, request limits, and storage evolution.

No finding requires a full rewrite. The right strategy is small hardening/refactoring slices around the current boundaries.

## Current Ownership Map

| Domain | Current owner | Boundary today | Main debt signal |
| --- | --- | --- | --- |
| HTTP/API/session/websocket edge | `app/main.py`, `app/http/cookies.py`, `app/routes/*` | `DemoMvpHandler` entrypoint + `RouteContext` domain routes | JSON routes are split by domain; JSON/audio parsing, auth helpers, static files and Live Voice WS relay still live on the edge handler. |
| Runtime orchestration | `app/runtime.py` | `DemoRuntime` | Good boundary; still synchronous and turn-level only. |
| LLM/STT/Live provider calls | `app/llm.py`, `app/stt.py`, `app/live_voice.py`, `app/live_voice_proxy.py` | adapters/factory functions | Good adapter direction; Live proxy needs operational observability. |
| Persistence | `app/storage.py` | `Storage` facade over SQLite | Migration/version baseline and indexes exist; repository/domain split is still future work. |
| Browser UI | `app/static/app.js`, `app/static/styles.css`, `app/templates/index.html` | one global state object and direct DOM rendering | Largest active-change surface; chat, admin, voice, markdown and layout are coupled. |
| Context assets | `docs/mvp/context/*`, `app/context_loader.py` | manifest + markdown layers | Good explicit context boundary; parser and file-path guard are MVP-only. |
| Tests | `tests/test_mvp_core.py` | unittest contract tests | Good breadth for backend contracts; UI is mostly static-text assertions. |
| Ops/runtime | `Dockerfile`, `docker-compose.demo.yml`, `docs/ops/*` | local Windows workspace + server-side Docker/Traefik release artifacts | Runtime split is documented; server has no `git`, so deploy uses `git archive` release artifacts. Rollback/backup automation remains future work. |

## What Is Not Debt Right Now

- Keeping the backend on stdlib `http.server` is acceptable for Demo MVP while traffic is low and routes are few.
- Keeping SQLite is acceptable for Demo MVP; it is explicitly documented as non-production storage.
- Keeping Context Inspector/admin CRUD as demo tooling is acceptable; do not turn it into production IAM yet.
- Not having local Docker is already documented in `docs/ops/LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md`; server-side Docker/Linux parity or artifact simulation is the correct gate.
- Not introducing a frontend framework yet is reasonable. The next step should be modularizing the current static JS, not a full SPA rewrite.

## Debt Register

### TD-01: Request size and cost-control limits are incomplete

- Severity: P1
- Evidence:
  - `app/main.py:346` reads JSON body by `Content-Length` with no max body limit.
  - `app/main.py:231` accepts chat message from JSON and only checks non-empty at `app/main.py:232-235`.
  - `app/runtime.py:26-60` assembles context and sends the full last user message into LLM context.
  - `app/main.py:365-390` has explicit audio upload limits, so the missing JSON/message limits are an inconsistent boundary.
- Risk: a large chat/admin JSON request can allocate memory and/or create expensive LLM calls. This is the highest practical hardening item because it protects cost and availability.
- Recommended slice:
  1. Add `MAX_JSON_BODY_BYTES` and a safe `_read_json` result that can return 413/400.
  2. Add env-configurable `CHAT_MESSAGE_MAX_CHARS` with conservative default.
  3. Enforce limits before `DemoRuntime.process_user_message`.
  4. Add tests for oversized JSON, malformed JSON and oversized chat message.
- Acceptance checks:
  - Oversized JSON returns 413 and does not call runtime.
  - Oversized chat message returns 413/400 and does not create a message row.
  - Existing normal chat flow stays unchanged.

### TD-02: Session cookie policy was MVP-level, now HTTPS-hardened

- Severity: resolved for Demo MVP
- Evidence:
  - `app/http/cookies.py` owns `build_session_cookie_header` and `should_use_secure_session_cookie`.
  - `SESSION_COOKIE_SECURE=auto|true|false` is handled in `app/config.py`.
  - `docker-compose.demo.yml:11-13` and production route use HTTPS domain `coocking-cart.speechbattle.com`.
- Risk: current Demo MVP risk is addressed; future work is production IAM/session lifecycle, not the `Secure` flag.
- Implemented slice:
  1. Added `SESSION_COOKIE_SECURE` config defaulting to `auto`.
  2. Included `Secure` for HTTPS/proxy requests and preserved local HTTP usability.
  3. Added cookie tests and production smoke that confirmed `Secure` and `HttpOnly`.
- Acceptance checks:
  - Production config emits `Set-Cookie` with `Secure`.
  - Local `http://127.0.0.1` remains usable when explicitly disabled.

### TD-03: `app/main.py` still owns edge, but JSON route orchestration is split

- Severity: P2 remaining edge cleanup
- Evidence:
  - JSON route behavior moved to `app/routes/config_routes.py`, `auth_routes.py`, `chat_routes.py`, `admin_routes.py`, and `voice_routes.py`.
  - `app/routes/contracts.py` records method/path/domain/guard mapping.
  - `DemoMvpHandler` still owns static files, body parsing, auth helpers, explicit dispatch and socket-bound Live Voice relay.
- Risk: remaining risk is mostly edge consistency: JSON/body limits, helper extraction and eventual route table/router drift.
- Remaining slice:
  1. Keep `http.server`; do not migrate framework yet.
  2. Extract JSON/audio body parsing and response helpers into `app/http/request_response.py`.
  3. Keep socket-bound Live Voice relay on the handler unless a real WebSocket server layer is introduced.
  4. Preserve response shapes and route URLs.
- Acceptance checks:
  - Existing 34 tests remain green.
  - Anti-drift route contracts remain authoritative for protected routes.

### TD-04: Frontend is now the largest active-change monolith

- Severity: P2
- Evidence:
  - `app/static/app.js` is the largest tracked code file at ~1744 PowerShell-counted lines.
  - One global `state` owns user/session/admin/artifact/voice state at `app/static/app.js:1-50`.
  - Chat rendering/Markdown lives around `app/static/app.js:459-563`.
  - Voice batch + live streaming lives around `app/static/app.js:1105-1475`.
  - Admin/inspector rendering uses large `innerHTML` blocks around `app/static/app.js:884-1030` and `app/static/app.js:1728-1746`.
  - `app/static/styles.css` is ~1178 lines and owns layout, chat, admin, voice and markdown styling.
- Risk: UI work is increasingly likely to regress unrelated states. The recent chat/typing/Markdown changes were correctly narrow, but the file shape is becoming friction.
- Recommended slice:
  1. Split by behavior, still as static browser scripts loaded in order: `state.js`, `api.js`, `chat.js`, `voice.js`, `admin.js`, `artifacts.js`, `ui.js`.
  2. Keep one global namespace, e.g. `window.CookingCart`, to avoid build tooling.
  3. Move scoped CSS sections into comments or separate files only if static loading remains simple.
  4. Add a browser smoke test later; do not introduce bundler before real need.
- Acceptance checks:
  - Chat send optimistic flow, assistant Markdown, batch voice fallback and Live voice UI contracts are still covered.
  - No behavior change in `/static/app.js` public runtime state unless explicitly migrated.

### TD-05: UI tests are contract-heavy but not behavior-complete

- Severity: P2
- Evidence:
  - UI tests in `tests/test_mvp_core.py:565-614` assert strings and CSS selectors in static assets.
  - There is no real browser test for optimistic chat rendering, Markdown DOM output, disabled send state, or voice mode transitions.
- Risk: static assertions catch anti-drift but can miss broken DOM behavior. The Markdown change is a good example: a parser behavior detail around images required an extra smoke check.
- Recommended slice:
  1. Keep static anti-drift tests; they are useful.
  2. Add one Playwright or browser-level smoke suite that starts the app with fake runtime/provider behavior.
  3. Cover: login/demo login, send message optimistic bubble, typing dots, assistant Markdown rendering, user plain text, voice batch/live visual mode.
- Acceptance checks:
  - Browser test asserts DOM terminal state, not screenshots only.
  - Test can be skipped or run only where browser tooling exists; local Windows/no-Docker constraint remains respected.

### TD-06: SQLite schema baseline is hardened; repository split remains

- Severity: resolved baseline; P2 remaining repository split
- Evidence:
- Evidence:
  - `schema_migrations` and idempotent startup migration exist in `app/storage.py`.
  - Product read indexes and `turn_results` foreign keys to `messages` are in place.
  - Production DB was backed up before migration and verified with `foreign_key_check=0`.
- Risk: schema-version debt is addressed for Demo MVP. Remaining debt is that `Storage` still mixes users, auth sessions, chat sessions, messages, turn results and admin metrics.
- Remaining slice:
  1. Keep one SQLite transaction owner.
  2. Split repositories by domain behind the existing `Storage` facade.
  3. Avoid moving away from SQLite until production storage requirements exist.
- Acceptance checks:
  - Existing DB opens and migrates idempotently.
  - Fresh DB and old DB both pass storage tests.

### TD-07: Live Voice server proxy has limited operational observability

- Severity: P2
- Evidence:
  - `app/live_voice_proxy.py:188-241` relays WebSocket frames with two daemon threads.
  - Exceptions in relay directions are swallowed at `app/live_voice_proxy.py:210-211` and `app/live_voice_proxy.py:228-229`.
  - Browser-side backpressure drops chunks silently when `websocket.bufferedAmount > 1_000_000` at `app/static/app.js:1430-1433`.
  - Production/server_proxy relies on SOCKS5 for provider reachability, documented in `docs/ops/LOCAL_TESTING_AND_PRODUCTION_RUNBOOK_v0.1.md:54-60`.
- Risk: when streaming degrades, we can see “does not work” without enough evidence: provider close code, proxy close reason, dropped chunk count, session duration, setup timing.
- Recommended slice:
  1. Add structured non-secret logs for Live Voice session id prefix, setup success/failure, close opcode, exception type and duration.
  2. Count dropped browser chunks and expose user/admin-safe error if backpressure persists.
  3. Add tests around close frames/error propagation where practical.
- Acceptance checks:
  - Logs never include Gemini token, SOCKS5 credentials or raw audio.
  - Admin hint explains upstream/proxy failure class without exposing secrets.

### TD-08: Context manifest parser is intentionally minimal but has no path guard

- Severity: P2
- Evidence:
  - `app/context_loader.py:67-99` is a custom simple manifest parser, not a full YAML parser.
  - `app/context_loader.py:116-118` joins `layers_dir / file_name` and checks existence, but does not enforce that the resolved path stays inside `layers_dir`.
- Risk: today manifest files are Git-controlled, so this is not user-exploitable in normal MVP flow. It becomes risky if admin GUI ever edits context layers or if deployment pulls unreviewed manifest changes.
- Recommended slice:
  1. Resolve `layer_path` and assert it is relative to resolved `layers_dir`.
  2. Add manifest validation for required fields and duplicate order values.
  3. Keep custom parser unless manifest complexity grows; adding PyYAML solely for this is not needed yet.
- Acceptance checks:
  - `../outside.md` in manifest fails with `ContextLoadError`.
  - Current manifest still loads in documented order.

### TD-09: Provider adapters are isolated but still one-provider concrete classes

- Severity: P3
- Evidence:
  - `DemoRuntime` constructs `GeminiAdapter(config)` directly at `app/runtime.py:18-21`, while STT and Live Voice already use factories.
  - `app/llm.py:25-98` is named `GeminiAdapter` and has no `make_llm_adapter` equivalent.
- Risk: low right now because Gemini is the accepted MVP provider. This becomes active only when a second LLM provider or test double is needed.
- Recommended slice:
  1. Add `LlmAdapter` protocol/base and `make_llm_adapter(config)` to mirror STT/Live Voice.
  2. Keep only Gemini implementation.
  3. Update runtime to use the factory.
- Acceptance checks:
  - No route or UI imports `GeminiAdapter` directly.
  - Existing structured output tests still assert Gemini payload shape at adapter boundary.

### TD-10: Deployment hardening is documented but not implemented

- Severity: P3 for Demo MVP, P1 before production use
- Evidence:
  - Current compose runs behind Traefik and uses `/opt/coocking-cart/runtime/.env` outside Git in `docker-compose.demo.yml:8-18`.
  - Server smoke shows `coocking-cart-app Up` with restart policy `unless-stopped`.
  - Server-side `git` is not installed, so current deploy uses local `git archive` release artifacts under `/opt/coocking-cart/releases/<commit>`.
  - Existing docs call out future deploy-user/backup/log policy in `docs/reports/MVP_IMPLEMENTATION_REPORT_v0.1.md` and ops runbooks.
- Risk: root SSH deployment, no formal backup/restore procedure for SQLite, and no release rollback command as a first-class script are acceptable for demo iteration but not for production claims.
- Recommended slice:
  1. Add backup/restore runbook for `/opt/coocking-cart/data/demo.sqlite`.
  2. Add a non-interactive deploy script that records release sha and rollback target.
  3. Later move from root SSH to dedicated deploy user.
- Acceptance checks:
  - Dry-run deploy lists target release, current symlink and compose project before changing anything.
  - Rollback can restore previous release without reading secrets.

### TD-11: Vendored browser dependency has no local metadata beyond license

- Severity: P3
- Evidence:
  - `app/static/vendor/markdown-it.min.js` and `app/static/vendor/markdown-it.LICENSE.txt` are present.
  - Template loads it directly at `app/templates/index.html:112`.
- Risk: low. The benefit is good closed-world runtime. The missing piece is upgrade traceability: version/source/integrity are not captured in a small manifest.
- Recommended slice:
  1. Add `app/static/vendor/README.md` with package name, version, source command and update steps.
  2. Optionally add SHA256 of vendored file.
- Acceptance checks:
  - Future audits can identify exact vendor origin without npm registry access.


## Follow-up Disposition 2026-05-27

Accepted/deferred by owner:

- TD-01 JSON/body/message size limits: accepted debt, postponed. It should be implemented later in the HTTP edge layer.
- TD-07 Live Voice forensic logging/observability: accepted debt, postponed.

Implemented in follow-up slice:

- TD-02 Session cookie hardening: `SESSION_COOKIE_SECURE=auto|true|false`; `auto` sets `Secure` for HTTPS/proxy requests and preserves local HTTP usability.
- TD-06 SQLite product-preparation baseline: `schema_migrations`, idempotent startup migrations, product read indexes and `turn_results` foreign keys to `messages`.

Planning artifact added:

- `docs/mvp/MVP_DOMAIN_LAYERED_REFACTORING_PLAN_v0.1.md` defines the domain/layer refactoring sequence for `app/main.py`, `app/storage.py` and `app/static/app.js`.
## Recommended Implementation Order

1. TD-01: request/body/message limits in the HTTP edge layer.
2. TD-07: Live Voice observability. Needed because streaming is now an active feature and location/SOCKS5 failures are realistic.
3. TD-04 + TD-05: frontend modularization plus one browser-level smoke. Do this before adding more chat/voice UI features.
4. TD-03 remaining edge cleanup: request/response helpers and optional route table, after request limits.
5. TD-06 remaining storage repository split behind the `Storage` facade before adding exports/admin analytics.
6. TD-08 + TD-11: context/vendor guardrails. Low risk, cheap cleanup.
7. TD-09 + TD-10: provider factory parity and deploy hardening. Do when those tracks become active.

## Validation Baseline Used For This Audit

Local PowerShell checks run during audit:

```powershell
python -m unittest discover -s tests
node --check app/static/app.js
python -m compileall app tests scripts
git diff --check
```

Production smoke used during audit, without reading secrets:

- `https://coocking-cart.speechbattle.com/api/config` returned 200 and included `voice_input`.
- `https://coocking-cart.speechbattle.com/static/vendor/markdown-it.min.js` returned 200.
- Server container `coocking-cart-app` was running with restart policy `unless-stopped`.

## Non-Goals For The Next Refactor

- Do not rewrite to FastAPI/React just to reduce file size.
- Do not replace SQLite until production storage requirements are explicit.
- Do not introduce local Docker as a required gate; local workspace constraints are documented.
- Do not build production IAM/RBAC inside demo admin CRUD.
- Do not make browser code aware of SOCKS5 or Gemini provider credentials.
