# MVP frontend states and errors v0.1

- Статус: UI states/errors contract для будущей реализации Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Документ фиксирует обязательные состояния frontend Demo MVP.

Пользователь не должен гадать, что происходит. Каждое действие должно иметь видимое подтверждение, loading state и терминальный результат: success или error.

## Общий принцип

UI показывает:

- что происходит сейчас;
- что пользователь может сделать дальше;
- какие данные требуют проверки;
- что является проектом, а не утвержденным документом.

Обычный `user` не видит stack traces, secrets, raw provider diagnostics и технические детали context assembly. `admin` может видеть безопасный debug-summary в Context Inspector.

## State matrix

| State | Что видит user | Что видит admin/debug | UI action |
| --- | --- | --- | --- |
| Not authenticated | Login screen и просьбу войти. | То же, без diagnostics. | Login action. |
| Empty session | Пустой чат, quick demo buttons, короткий next step. | Дополнительно session id, если создан. | Start scenario или send message. |
| Assistant thinking | Typing/loading indicator, disabled send button. | Turn pending, provider/model placeholder, trace pending. | Wait/cancel optional future. |
| LLM timeout/error | Короткое сообщение: ассистент временно недоступен. | Provider error summary without secrets. | Retry / send again. |
| Structured output parse error | Сообщение, что ответ не удалось разобрать; предложение повторить. | Raw-safe parse summary, field missing info. | Retry / inspect. |
| Context manifest missing | User: сервис временно не готов. | Manifest path and missing file summary. | Admin fixes config, user retries later. |
| Markdown layer missing | User: сервис временно не готов. | Missing layer name/source file. | Admin fixes context pack. |
| SQLite unavailable | User: история временно недоступна. | Storage error summary without stack trace by default. | Retry / restart future task. |
| API key missing | User: ассистент не настроен. | Missing env variable name only, no values. | Admin config task. |
| Unauthorized admin/debug access | User: нет доступа к debug view. | Access denied event summary. | Return to chat. |
| Insufficient data to generate card | User sees clear open questions. | Known facts/open questions in structured output. | Answer questions. |
| Copy success | Short confirmation. | Same. | Continue. |
| Copy failure | Copy failed message and manual selection hint. | Browser/runtime reason if safe. | Retry/manual copy. |

## Loading states

Loading must be explicit for:

- initial app load;
- login;
- sending message;
- assistant response pending;
- loading session history;
- loading result/document draft;
- opening Context Inspector;
- copying document/JSON if async.

Buttons in loading state must be disabled or marked busy to prevent duplicate turns.

## Error states

Error states must:

- use clear Russian user-facing text;
- avoid stack traces for `user`;
- show safe technical summary for `admin`;
- provide a next action where possible;
- avoid exposing secrets, API keys, raw `.env`, SSH data or provider credentials.

## Empty states

Empty states must include a next step:

- login screen: ask user to sign in;
- empty chat: show quick demo scenario buttons;
- empty result panel: explain that document appears after recipe/technology confirmation;
- empty JSON panel: explain that structured JSON appears after document draft generation;
- empty Context Inspector: explain that trace appears after at least one turn.

## Success states

Success states must be visible for:

- message sent;
- assistant response received;
- document draft generated;
- structured JSON available;
- copy document success;
- copy JSON success;
- new session created.

## Disabled states

Disabled states are required when:

- input is empty;
- message is being sent;
- assistant response is pending;
- required data is insufficient for "Сформировать карту";
- user is not allowed to open admin/debug UI;
- structured JSON is not available yet.

Disabled controls must have accessible label/title or contextual explanation where helpful.

## Focus and keyboard

Interactive elements must be operable without a mouse:

- input focus visible;
- send button focus visible;
- icon buttons focus visible;
- popover/sheet close action reachable from keyboard;
- tabs/accordion/context inspector sections reachable by keyboard;
- escape/back behavior for modal/sheet where applicable.

## UI-domain boundary

UI state management can decide what to show, expand, collapse or disable.

UI must not:

- decide document type;
- validate recipe legally;
- calculate domain facts as source of truth;
- assemble LLM context;
- call LLM provider directly;
- hide critical warnings because they are inconvenient visually.

## Related documents

- [MVP frontend visual contract](MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md)
- [MVP roles and access](MVP_ROLES_AND_ACCESS_v0.1.md)
- [MVP Context Inspector](MVP_CONTEXT_INSPECTOR_v0.1.md)
- [MVP structured output contract](MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md)
