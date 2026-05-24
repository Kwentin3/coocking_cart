# MVP admin context workspace blueprint v0.1

- Статус: implementation blueprint
- Дата: 2026-05-24
- Контур: Demo MVP

## Current problem and risk

Admin diagnostics уже существуют как `Trace`, но экран привязан к пользовательской композиции чата и недостаточно удобен для операционного просмотра.

Риск прямого prompt CRUD уже признан: GUI-редактирование markdown layers на сервере может создать drift между Git, docs и runtime. Поэтому первый срез остается read-only.

## Domain and ownership map

| Domain | Ownership |
| --- | --- |
| Chat runtime | создает sessions, messages, turn results и trace |
| SQLite storage | хранит demo users, sessions, messages, turn results |
| Context loader | читает `context_manifest.yml` и markdown layers |
| Admin workspace UI | показывает dashboard, prompt/context viewer и users panel |
| User chat UI | остается текущим user-facing чатом |

## Boundary contracts

### Admin dashboard API

Read-only endpoint:

```text
GET /api/admin/dashboard
```

Возвращает:

- period metrics: day/week/month/year/all_time;
- total users/sessions/messages/turns/drafts;
- estimated tokens;
- latest active chats;
- selected chat preview через существующий session read endpoint.

### Admin context API

Read-only endpoint:

```text
GET /api/admin/context
```

Возвращает:

- manifest metadata;
- layers metadata and text;
- static context preview;
- structured output schema;
- latest turn trace, если есть;
- latest assembled context preview, если есть;
- health summary.

### Access

Оба endpoint доступны только `admin`. `user` получает `403`.

## Proposed implementation slices

1. Docs:
   - feature PRD;
   - blueprint;
   - visual contract update;
   - decision log update.

2. Storage/read models:
   - `admin_dashboard()` with period aggregates;
   - latest activity list;
   - token estimate as MVP-only approximation.

3. Runtime context payload:
   - `admin_context_payload()`;
   - manifest/layers/static context/schema/latest turn.

4. HTTP API:
   - `GET /api/admin/dashboard`;
   - `GET /api/admin/context`.

5. Admin UI:
   - admin service nav in the left rail;
   - dashboard screen;
   - read-only chat preview;
   - prompt/context viewer screen;
   - keep users screen in admin workspace.

6. Tests:
   - dashboard read model;
   - admin context payload;
   - user access remains denied for admin context data.

## UI states

- loading dashboard;
- empty dashboard;
- dashboard API error;
- loading prompt/context viewer;
- missing context manifest/layer error;
- no latest turn yet;
- copy success/failure;
- unauthorized admin screen access.

## Non-goals

- Prompt CRUD.
- Editing context files from GUI.
- Production analytics.
- Provider billing reconciliation.
- Production audit/event log.
- Changing user chat UI.

## Validation plan

- Unit tests for dashboard aggregates and context payload.
- `python -m unittest discover -s tests`.
- `python -m compileall app tests`.
- `node --check app/static/app.js`.
- Local HTTP smoke for admin dashboard/context endpoints.
- Manual UI smoke for admin screens.
