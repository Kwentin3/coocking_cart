# MVP implementation report v0.1

- Статус: Demo MVP реализован, задеплоен и проверен
- Дата: 2026-05-24
- Ветка: `implementation/demo-mvp`

## Кратко

Реализован минимальный веб-прототип Demo MVP без npm/pip runtime dependencies:

- авторизация через bootstrap admin и demo user;
- роли `user` и `admin`;
- admin-only CRUD пользователей для демо-операций;
- чатовые сессии;
- загрузка markdown context layers через `docs/mvp/context/context_manifest.yml`;
- SQLite-хранение сессий, сообщений, turn result и document draft;
- Gemini provider adapter через REST boundary;
- schema-first Structured Output через Gemini generation config;
- frontend с чатом, result panel, warnings/statuses, structured JSON, admin Context Inspector и user management panel;
- тесты для context loader, placeholder validation, bootstrap, LLM error path, Gemini payload, inspector access и admin user CRUD;
- Dockerfile и compose-шаблон для будущего деплоя за существующим Traefik.

MVP не является production-ready системой. Любая ТК/ТТК в интерфейсе помечается как проект, требующий проверки ответственным лицом предприятия.

## Прочитанная база

Реализация велась от финальной документационной базы:

- `docs/prd/PRD_AI_TECH_CARDS_MVP_v0.2.md`
- `docs/product/PRODUCT_WORKFLOW_v0.2.md`
- `docs/mvp/MVP_IMPLEMENTATION_ROADMAP_v0.1.md`
- `docs/mvp/MVP_IMPLEMENTATION_HANDOFF_v0.1.md`
- `docs/mvp/MVP_ACCEPTANCE_CRITERIA_v0.1.md`
- `docs/mvp/MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md`
- `docs/mvp/MVP_FILE_DRIVEN_CONTEXT_ARCHITECTURE_v0.1.md`
- `docs/mvp/MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md`
- `docs/mvp/MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md`
- `docs/mvp/MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md`
- `docs/mvp/MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md`
- `docs/mvp/MVP_CONTEXT_INSPECTOR_v0.1.md`
- `docs/mvp/MVP_DEMO_SCENARIOS_v0.1.md`
- `docs/ops/DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md`
- `docs/ops/SERVER_AUDIT_REPORT_91.132.48.224_v0.1.md`
- `.env.example`

Default branch на GitHub остается устаревшим: `docs/prd-refine-v0.2`. Реализация находится в `implementation/demo-mvp`.

## Stack decision

Выбран минимальный стек:

- Python 3.11 standard library;
- `http.server` для web/API runtime;
- `sqlite3` для MVP-хранилища;
- vanilla HTML/CSS/JavaScript;
- Gemini REST API через `urllib.request`;
- без runtime-зависимостей npm/pip.

Решение зафиксировано в `docs/mvp/MVP_STACK_DECISION_v0.1.md`.

## Structured Output correction

По официальной спецификации Gemini Structured Outputs форма ответа задается provider-level config, а не просьбой "верни JSON без Markdown" внутри prompt.

В реализации:

- prompt/context window описывает задачу, доменные правила, workflow, историю и последнее сообщение пользователя;
- Gemini adapter передает `generationConfig.responseMimeType = "application/json"`;
- JSON Schema передается как `generationConfig.responseJsonSchema`;
- runtime парсит, нормализует и сохраняет structured output;
- если `document_draft` есть, но `structured_json` пустой, runtime формирует минимальное нейтральное `structured_json` из draft;
- `structured_json` явно не является форматом iiko/r_keeper/1C/StoreHouse или production-интеграционной схемой.

Проверенные источники:

- https://ai.google.dev/gemini-api/docs/structured-output
- https://ai.google.dev/gemini-api/docs/models

## Реализовано по фазам

Phase 0/0.1:

- подтверждена финальная documentation base;
- проверено, что реализация идет от `implementation/demo-mvp`;
- внесена корректировка по Gemini Structured Output;
- secrets не добавлены.

Phase 1:

- создан каркас `app/`;
- добавлен root `README.md` с локальным запуском;
- добавлен stack decision;
- добавлены Dockerfile, `.dockerignore` и `docker-compose.demo.yml` для будущего деплоя.

Phase 2:

- реализовано чтение env и `.env`;
- OS environment перекрывает `.env`;
- добавлена placeholder validation для значений вида `<...>`;
- bootstrap admin создается из env;
- demo user создается при `DEMO_MODE=true`;
- `.env` и SQLite runtime files не отслеживаются Git.

Phase 3:

- реализован `ContextLoader`;
- manifest и markdown layers читаются из `docs/mvp/context/`;
- порядок layers соблюдается;
- список layers доступен для Context Inspector.

Phase 4:

- реализовано SQLite-хранилище сессий, сообщений и turn result;
- сохраняется last document draft;
- trace metadata сохраняется для admin/debug;
- SQLite не используется как production storage.

Phase 5:

- реализован Gemini adapter boundary;
- `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY` читаются из env/config;
- пустой `LLM_BASE_URL` использует default Gemini endpoint `https://generativelanguage.googleapis.com`;
- provider/model сохраняются в trace;
- ошибки provider нормализуются.

Phase 6:

- реализован turn loop: user message -> context assembly -> LLM adapter -> structured output parse -> save result -> UI;
- parse/provider errors не показывают обычному user stack trace;
- user не получает trace.

Phase 7/8:

- реализован responsive frontend;
- user видит чат, warnings/statuses, document draft и structured JSON своей сессии;
- admin видит Context Inspector, context layers, trace и structured output;
- user не видит Context Inspector;
- UI использует русский user-facing текст и light theme.

Phase 9/10:

- выполнены реальные Gemini-backed локальные сценарии;
- выполнены unit/smoke проверки;
- выполнена security/config sanity проверка.

Phase 11:

- deployment artifacts подготовлены;
- server read-only audit выполнен;
- deployment выполнен контролируемо без изменения существующих сервисов.

## Реальный Gemini-backed прогон

Реальный runtime env был доступен локально. Секреты не печатались и не коммитились.

Проверено:

- `LLM_PROVIDER=gemini`;
- `LLM_MODEL` берется из env;
- использованный non-secret model id: `gemini-3.1-pro-preview`;
- выбранная модель найдена через Gemini models API;
- `.env.example` оставлен с безопасным примером `LLM_MODEL=gemini-flash-latest`;
- `LLM_API_KEY` берется только из real env/.env вне Git.

Smoke turn:

- запрос: "Хочу технологическую карту яичницы.";
- provider error: нет;
- parse error: нет;
- `user_answer`: сохранен и отображается;
- `workflow_status`: сохранен;
- warnings/data statuses: сохранены;
- structured output: сохранен в SQLite;
- admin inspector: доступен;
- user trace: скрыт.

## Demo scenarios

### Курица по-вьетнамски

Локально пройден Gemini-backed сценарий:

- первый turn не формирует карту преждевременно;
- ассистент уточняет формат/доставку/порцию/ингредиенты;
- сценарий ведет к проекту ТТК;
- warnings по потерям, хранению, температурным режимам присутствуют;
- после подтверждения появляется `document_draft`;
- `structured_json` появляется вместе с проектом;
- `structured_json.integration_status = not_an_accounting_system_import_format`;
- документ помечен как проект, требующий проверки.

### Яичница/омлет

Локально пройден Gemini-backed сценарий:

- ассистент не усложняет простой сценарий чрезмерно;
- возможен проект ТК;
- warnings/statuses присутствуют;
- `document_draft` появляется после минимального подтверждения;
- `structured_json` доступен;
- документ не выдается за юридически утвержденный.

## Frontend acceptance

Проверено локально:

- login screen работает;
- demo user login работает;
- admin login работает;
- chat screen отображает user/assistant сообщения;
- result panel не смешивает основной ответ, warnings, statuses, draft и JSON;
- copy document / copy JSON имеют feedback;
- session list использует semantic buttons;
- toast имеет `role="status"` и `aria-live="polite"`;
- focus-visible состояния добавлены для keyboard navigation;
- JSON/pre blocks не ломают mobile width;
- Context Inspector доступен только admin;
- trace не содержит API key, auth secret, bootstrap password/hash или raw `.env`.

Browser smoke:

- desktop screenshot smoke: pass;
- mobile screenshot smoke: pass;
- Playwright test runner в проект не добавлялся, чтобы не вводить npm dependency.

## Security/config sanity

Проверено:

- `.env` не tracked;
- `data/` и SQLite runtime files не tracked;
- `docs/out/` не tracked;
- `.gitignore` защищает `.env`, `.env.*`, `*.sqlite`, `*.sqlite3`, `data/*.sqlite`, `data/*.sqlite3`;
- `.env.example` содержит только non-secret values и placeholders/empty secret fields;
- реальные Gemini API key, session secret, bootstrap credentials и SSH key не коммитились;
- Git grep по private key / API key / session secret patterns не выявил секретов в tracked files.

## Тесты

Выполнено в PowerShell:

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Результат:

- `unittest`: 10 tests, OK;
- `compileall`: OK.

Тестовое покрытие включает:

- config placeholder validation;
- context loader;
- missing LLM key safe error;
- Gemini payload shape with `responseMimeType` and `responseJsonSchema`;
- non-admin inspector denial;
- admin inspector payload;
- bootstrap admin creation/authentication;
- admin user CRUD create/update/delete;
- current/last admin guard;
- derived neutral `structured_json` when draft exists.

## Admin user CRUD update

Добавлен минимальный admin-only CRUD пользователей:

- blueprint: `docs/mvp/MVP_ADMIN_USER_CRUD_BLUEPRINT_v0.1.md`;
- API: `GET/POST /api/admin/users`, `PATCH/DELETE /api/admin/users/{id}`;
- storage contract: public user DTO без `password_hash`;
- UI: вкладка "Пользователи" доступна только `admin`;
- guard: текущий admin не может удалить или понизить сам себя;
- guard: последний admin не может быть удален или понижен;
- deletion behavior: hard delete в MVP каскадно удаляет demo auth/chat sessions через SQLite FK.

Локальный HTTP smoke:

- admin login: OK;
- list/create/update/delete user: OK;
- non-admin access to `/api/admin/users`: 403 OK;
- secrets/password hashes в ответах не возвращались.

## Deployment preparation

Read-only server audit подтвердил:

- domain: `coocking-cart.speechbattle.com`;
- server: `91.132.48.224`;
- SSH context: `root@91.132.48.224`;
- container runtime: Docker;
- reverse proxy: existing Traefik;
- Traefik container: `platform-edge-traefik`;
- Docker network: `edge`;
- entrypoints: `web`, `websecure`;
- certresolver: `le`;
- существующие контейнеры менять/останавливать нельзя.

Подготовлены:

- `Dockerfile`;
- `.dockerignore`;
- `docker-compose.demo.yml`.

Compose использует:

- container: `coocking-cart-app`;
- external network: `edge`;
- app port inside container: `8000`;
- env file outside Git: `/opt/coocking-cart/runtime/.env`;
- SQLite volume path: `/opt/coocking-cart/data:/app/data`;
- Traefik host rule: `coocking-cart.speechbattle.com`;
- TLS certresolver: `le`.

## Deployment result

Deployment выполнен 2026-05-24 на:

- URL: `https://coocking-cart.speechbattle.com/`;
- server: `91.132.48.224`;
- deployed code commit: `347e5d9`;
- container: `coocking-cart-app`;
- Docker network: `edge`;
- reverse proxy: existing Traefik;
- runtime env file: `/opt/coocking-cart/runtime/.env` outside Git;
- SQLite data path: `/opt/coocking-cart/data`.

Что было изменено на сервере:

- создан release under `/opt/coocking-cart/releases/347e5d9`;
- обновлен symlink `/opt/coocking-cart/current`;
- скопирован runtime `.env` в `/opt/coocking-cart/runtime/.env` без вывода содержимого;
- создан/обновлен только контейнер `coocking-cart-app`;
- существующие Traefik и другие контейнеры не останавливались и не пересоздавались.

Проверки после деплоя:

- `docker ps`: `coocking-cart-app` is up on network `edge`;
- `HEAD https://coocking-cart.speechbattle.com/`: HTTP 200;
- `GET https://coocking-cart.speechbattle.com/api/config`: `config_errors: []`;
- demo user login: OK;
- remote Gemini-backed chicken scenario: final turn has `document_draft=true`, `structured_json=true`;
- remote Gemini-backed egg scenario: final turn has `document_draft=true`, `structured_json=true`;
- user session payload does not expose trace;
- admin login: OK;
- admin Context Inspector: OK, 8 layers, trace present;
- admin trace did not expose API key/session secret/bootstrap credentials;
- remote admin user CRUD smoke: list/create/update/delete OK;
- remote non-admin access to `/api/admin/users`: 403 OK;
- remote user CRUD responses did not expose password hashes or secrets.

Remote egg scenario required a third confirmation turn before draft generation. This is acceptable for MVP dialogue behavior and was not fixed through hardcoded scenario logic.

## Локальный запуск

1. Создать локальный `.env` вне Git на базе `.env.example`.
2. Заполнить runtime secrets:
   - `AUTH_SESSION_SECRET`;
   - `BOOTSTRAP_ADMIN_EMAIL`;
   - `BOOTSTRAP_ADMIN_PASSWORD` или `BOOTSTRAP_ADMIN_PASSWORD_HASH`;
   - `LLM_PROVIDER=gemini`;
   - актуальный `LLM_MODEL`;
   - `LLM_API_KEY`.
3. Запустить:

```powershell
python -m app.main --host 127.0.0.1 --port 8000
```

Открыть: `http://127.0.0.1:8000`

Если LLM env не настроен, приложение показывает безопасную конфигурационную ошибку вместо stack trace.

## Ограничения

- Нет production state machine.
- Нет semantic context engine.
- Нет calculation engine.
- Нет validation layer уровня production.
- Нет integrations с iiko/r_keeper/1C/StoreHouse.
- Нет PDF/Word/Excel export.
- Нет production IAM/RBAC; admin user CRUD является demo operations.
- Нет production audit/event log.
- Structured JSON не является готовым импортом в учетную систему.
- MVP UI рассчитан на демонстрацию, не на production admin panel.

## Follow-up

- Провести демонстрацию владельцу продукта на `https://coocking-cart.speechbattle.com/`.
- После демо собрать feedback по качеству уточняющих вопросов, draft-структуре и UI.
- Отдельно решить, нужно ли усиливать расчеты, валидацию и production state.
- Для production hardening позже перейти с root SSH на dedicated deploy user и формализовать backup/log policy.
