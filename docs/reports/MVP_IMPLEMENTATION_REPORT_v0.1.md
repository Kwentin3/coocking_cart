# MVP implementation report v0.1

- Статус: локальная Demo MVP реализация
- Дата: 2026-05-24
- Ветка: `implementation/demo-mvp`

## Кратко

Реализован минимальный веб-прототип Demo MVP без npm/pip runtime dependencies:

- авторизация через bootstrap admin и demo user;
- роли `user` и `admin`;
- чатовые сессии;
- загрузка markdown context layers через `context_manifest.yml`;
- SQLite-хранение сессий, сообщений, turn result и document draft;
- Gemini provider adapter через REST boundary;
- schema-first Structured Output через Gemini generation config;
- frontend с чатом, result panel, warnings/statuses, structured JSON и admin Context Inspector;
- smoke-тесты для context loader, placeholder validation, безопасной LLM-ошибки и Gemini structured output payload.

## Прочитанная база

Реализация велась от финальной документационной базы:

- `docs/prd/PRD_AI_TECH_CARDS_MVP_v0.2.md`
- `docs/product/PRODUCT_WORKFLOW_v0.2.md`
- `docs/mvp/MVP_IMPLEMENTATION_ROADMAP_v0.1.md`
- `docs/mvp/MVP_IMPLEMENTATION_HANDOFF_v0.1.md`
- `docs/mvp/MVP_ACCEPTANCE_CRITERIA_v0.1.md`
- `docs/mvp/MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md`
- `docs/mvp/MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md`
- `docs/mvp/MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md`
- `docs/mvp/MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md`
- `docs/mvp/MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md`
- `docs/ops/DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md`
- `.env.example`

## Stack decision

Выбран стек:

- Python 3.11 standard library;
- `http.server` для локального web/API runtime;
- `sqlite3` для MVP-хранилища;
- vanilla HTML/CSS/JavaScript;
- Gemini REST API через `urllib.request`;
- без runtime-зависимостей npm/pip.

Решение зафиксировано в `docs/mvp/MVP_STACK_DECISION_v0.1.md`.

## Structured Output correction

По официальной спецификации Gemini Structured Outputs форма ответа задается не prompt-инструкцией, а generation config с JSON MIME type и JSON Schema/response schema:

- источник: https://ai.google.dev/gemini-api/docs/structured-output
- в коде Gemini adapter отправляет `generationConfig.responseFormat.text.mimeType = "application/json"`;
- schema передается как `generationConfig.responseFormat.text.schema`;
- prompt/context window больше не содержит инструкции форматирования JSON;
- runtime все равно валидирует и нормализует ответ, потому что schema не подтверждает юридическую или технологическую корректность значений.

## Реализовано по фазам

Phase 0/0.1:

- подтверждена финальная documentation base;
- внесена корректировка по Gemini Structured Output;
- secrets не добавлены.

Phase 1:

- создан каркас `app/`;
- добавлен root `README.md` с локальным запуском;
- обновлен `.gitignore`;
- добавлен stack decision.

Phase 2:

- реализовано чтение env и `.env`;
- добавлена placeholder validation;
- bootstrap admin создается из env;
- demo user создается в `DEMO_MODE`.

Phase 3:

- реализован `ContextLoader`;
- manifest и markdown layers читаются из `docs/mvp/context/`;
- список layers доступен для inspector.

Phase 4:

- реализовано SQLite-хранилище сессий, сообщений и turn result;
- runtime SQLite files остаются ignored.

Phase 5:

- реализован Gemini adapter boundary;
- provider/model/API key читаются из env;
- provider errors нормализуются.

Phase 6:

- реализован turn loop: user message -> context assembly -> LLM adapter -> structured output parse -> save result -> UI.

Phase 7/8:

- реализован responsive frontend;
- user видит чат, warnings/statuses, document draft, structured JSON;
- admin видит Context Inspector, context layers, trace и structured output.

Phase 9/10:

- выполнены smoke checks без реального LLM call;
- deployment не выполнялся.

## Локальный запуск

1. Создать локальный `.env` вне Git на базе `.env.example`.
2. Заполнить:
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

Если LLM env не настроен, приложение показывает безопасную ошибку вместо stack trace.

## Проверки

Выполнено:

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Результат:

- `unittest`: 4 tests, OK;
- `compileall`: OK.

Локальный HTTP smoke:

- `/api/me` и `/api/config` отвечают;
- demo user login работает;
- при placeholder `LLM_API_KEY` turn возвращает безопасный `llm_error`;
- admin login работает;
- Context Inspector доступен admin и показывает 8 context layers;
- user trace не получает.

## Demo scenarios

Полный Gemini-backed прогон сценариев зависит от реальных env:

- `LLM_API_KEY`;
- актуальный `LLM_MODEL`.

Без реального ключа проверен безопасный fallback:

- "Хочу технологическую карту яичницы" сохраняется как user message;
- assistant возвращает user-safe LLM configuration error;
- trace скрыт от `user` и доступен `admin`.

## Ограничения

- Не реализованы production state machine, semantic context engine, calculation engine, integrations и production audit log.
- Нет PDF/Word/Excel export.
- Нет Docker/Traefik production config.
- Нет real deployment.
- Structured JSON не является форматом iiko/r_keeper/1С/StoreHouse.
- MVP UI простой и рассчитан на демонстрацию, не на production admin panel.

## Follow-up

- Перед реальным demo заполнить `.env` вне Git.
- Проверить актуальный Gemini model id по официальной документации Google AI.
- Прогнать два сценария с реальным Gemini:
  - "Курица по-вьетнамски";
  - "Яичница/омлет".
- После локальной приемки подготовить отдельный deployment task.
