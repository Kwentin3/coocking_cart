# MVP implementation roadmap v0.1

- Статус: execution roadmap для будущей реализации Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## 1. Назначение roadmap

Этот документ задает порядок реализации Demo MVP AI-ассистента технологических карт.

Это не product roadmap на месяцы и не production architecture blueprint. Это execution roadmap для агента-реализатора: что делать сначала, когда фаза считается готовой, что нельзя делать преждевременно и где сверяться с документацией.

Roadmap не заменяет PRD, implementation handoff, frontend visual contract или acceptance criteria. Он связывает их в последовательность реализации и удерживает scope от расползания.

## 2. Общий принцип

Реализация идет по фазам:

1. Documentation intake.
2. Project skeleton.
3. Context pack loader.
4. SQLite dialogue storage.
5. LLM provider adapter.
6. Structured output loop.
7. Chat UI and frontend visual contract.
8. Context Inspector / admin debug.
9. Demo scenarios.
10. Deployment preparation.

Главный порядок:

- сначала контекстный контур;
- потом хранение диалога;
- потом LLM adapter;
- потом structured output loop;
- потом frontend;
- потом Context Inspector;
- потом demo scenarios;
- потом только deployment preparation.

Нельзя переходить к следующей фазе, пока acceptance/gate текущей фазы не выполнены. Если gate не проходит, нужно остановиться, исправить фазу или зафиксировать вопрос владельцу проекта.

## 3. Phase 0. Documentation intake

### Цель

Агент-реализатор должен прочитать ключевые документы и подтвердить понимание Demo MVP scope.

### Что сделать

- Прочитать ключевые документы:
  - [PRD MVP v0.2](../prd/PRD_AI_TECH_CARDS_MVP_v0.2.md);
  - [Product workflow v0.2](../product/PRODUCT_WORKFLOW_v0.2.md);
  - [MVP scope](MVP_SCOPE_v0.1.md);
  - [Implementation handoff](MVP_IMPLEMENTATION_HANDOFF_v0.1.md);
  - [Acceptance criteria](MVP_ACCEPTANCE_CRITERIA_v0.1.md);
  - [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md);
  - [File-driven context architecture](MVP_FILE_DRIVEN_CONTEXT_ARCHITECTURE_v0.1.md);
  - [Prompt layer contract](MVP_PROMPT_LAYER_CONTRACT_v0.1.md);
  - [Turn contract](MVP_TURN_CONTRACT_v0.1.md);
  - [Structured output contract](MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md);
  - [Frontend visual contract](MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md);
  - [Frontend states and errors](MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md);
  - [Deployment preparation handoff](../ops/DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md).
- Кратко перечислить, какие документы использованы.
- Подтвердить, что реализуется Demo MVP, а не production system.
- Подтвердить, что production state machine, semantic context engine, integrations, PDF/Word export, full RBAC и production audit не входят в текущую реализацию.

### Acceptance / gate

- Агент перечислил прочитанные документы.
- Агент сформулировал, что реализует Demo MVP, а не production system.
- Агент зафиксировал, что prompt/context layers не хардкодятся в коде.
- Агент понял, что frontend visual contract обязателен.
- Агент понял, что deployment не выполняется без отдельного task.

### Нельзя

- Писать код до завершения intake.
- Выбирать стек без фиксации решения.
- Начинать с UI без context loader.
- Начинать с deployment.

## 4. Phase 1. Project skeleton

### Цель

Создать минимальный каркас приложения.

### Что сделать

- Предложить минимальный стек реализации, если стек еще не задан.
- Зафиксировать короткий stack decision note в отчете или отдельном документе, если нужно.
- Создать структуру проекта.
- Предусмотреть место для frontend, backend/runtime, context loader, SQLite, LLM adapter.
- Подготовить local run skeleton.

### Acceptance / gate

- Приложение запускается локально.
- Есть базовая структура проекта.
- Нет доменных prompt rules в коде.
- Есть понятное место для чтения `context_manifest.yml`.
- Есть базовый способ конфигурации через env/placeholders.
- Нет production-усложнений.

### Нельзя

- Хардкодить Gemini, model id или API key.
- Хардкодить prompt/context rules.
- Создавать production Docker/Traefik config.
- Начинать полноценную RBAC/IAM.
- Делать deployment.

## 5. Phase 2. Context pack loader

### Цель

Научить runtime читать markdown context layers через manifest.

### Что сделать

- Прочитать `docs/mvp/context/context_manifest.yml`.
- Загрузить layers в указанном порядке.
- Собрать static context pack.
- Обработать ошибки missing manifest / missing layer.
- Обеспечить возможность показать список подключенных layers.

### Acceptance / gate

- Runtime читает manifest.
- Порядок layers соблюдается.
- Отсутствующий layer дает понятную ошибку.
- Список layers доступен для debug/Context Inspector.
- Domain prompts не захардкожены в коде.

### Нельзя

- Делать semantic context engine.
- Позволять LLM создавать новые layers.
- Хранить dialogue history в markdown.
- Загружать полный PRD/research в каждый запрос вместо сжатых context layers.

## 6. Phase 3. SQLite dialogue storage

### Цель

Сохранить динамическую историю диалога и результаты тактов.

### Что сделать

- Создать минимальное хранение session/chat.
- Сохранить user/assistant messages.
- Сохранить structured output / turn result.
- Сохранить last document draft, если есть.
- Обеспечить загрузку короткой истории для следующего такта.

### Acceptance / gate

- Новая session создается.
- Сообщения сохраняются и достаются в правильном порядке.
- Structured output последнего такта сохраняется.
- История диалога не хранится в markdown.
- SQLite не превращается в production storage design.

### Нельзя

- Строить production audit/event log.
- Делать сложную схему версионирования документов.
- Делать approval workflow.
- Хранить secrets/API keys в SQLite.

## 7. Phase 4. LLM provider adapter

### Цель

Подключить LLM через минимальный provider adapter boundary.

### Что сделать

- Использовать env:
  - `LLM_PROVIDER`;
  - `LLM_MODEL`;
  - `LLM_API_KEY`;
  - optional `LLM_BASE_URL`;
  - optional `LLM_TIMEOUT_SECONDS`.
- Учитывать target provider family для MVP: Gemini.
- Брать точный model id из env, не хардкодить его.
- Adapter получает assembled context window и возвращает normalized structured output или normalized error.
- Provider/model сохраняются в trace.

### Acceptance / gate

- Вызов LLM идет через adapter.
- Доменная логика не зависит напрямую от Gemini SDK/API.
- Provider/model/API key берутся из env.
- Ошибка provider отображается user-safe и admin-debug отдельно.
- Provider factory не реализуется.

### Нельзя

- Строить multi-provider factory.
- Делать capability matrix.
- Хардкодить model id.
- Вызывать LLM напрямую из frontend.
- Пропускать provider adapter ради скорости.

## 8. Phase 5. Structured output loop

### Цель

Получить рабочий цикл: user message -> context window -> LLM -> structured output -> `user_answer` + служебные поля.

### Что сделать

- Собрать context window из markdown pack, history, last user message и structured output instruction.
- Отправить context window в LLM через provider adapter.
- Распарсить structured output.
- Показать `user_answer`.
- Сохранить warnings, data_statuses, document_draft, structured_json.
- Обработать parse error.

### Acceptance / gate

- `user_answer` отображается в чате.
- `workflow_status` сохраняется.
- `known_facts`, `open_questions`, `warnings`, `data_statuses` доступны.
- `document_draft` появляется только когда уместно.
- `structured_json` не выдается за формат учетной системы.
- Parse errors обрабатываются безопасно.

### Нельзя

- Выдавать неподтвержденные данные как финальные.
- Показывать document draft как утвержденный документ.
- Смешивать `user_answer` и debug/internal fields в один текст.
- Терять warnings/statuses при сохранении turn result.

## 9. Phase 6. Chat UI + frontend visual contract

### Цель

Сделать демонстрационно пригодный UI.

### Что сделать

- Login screen.
- Main chat screen.
- Desktop layout.
- Mobile layout.
- Result/document panel.
- Warnings block.
- Data statuses block.
- Structured JSON panel.
- Copy document / copy JSON.
- Loading states.
- Error states.
- Russian user-facing UI.
- Light theme default.
- Icon-first contextual hints.

### Acceptance / gate

- Desktop layout usable.
- Mobile layout usable.
- User/assistant messages читаемы.
- Loading state есть.
- Errors user-safe.
- Warnings/statuses визуально отделены от основного ответа.
- Document draft помечен как проект.
- JSON можно открыть и скопировать.
- Critical warnings не спрятаны только за иконками.
- Пользовательский UI на русском.

### Нельзя

- Делать complex design system.
- Делать theme customizer.
- Делать multilingual UI.
- Делать PDF/Word/Excel export.
- Делать production admin panel.
- Переносить domain logic в UI components.

## 10. Phase 7. Context Inspector / admin debug

### Цель

Дать admin/debug-инструмент для просмотра сборки context window.

### Что сделать

- Открыть Context Inspector только для `admin`.
- Показать context manifest.
- Показать список layers.
- Показать текст layer по раскрытию.
- Показать dialogue history.
- Показать last user message.
- Показать assembled context preview или основные части.
- Показать structured output.
- Показать warnings/statuses/document_draft/structured_json.

### Acceptance / gate

- `user` не видит Context Inspector.
- `admin` видит Context Inspector.
- Layers раскрываются.
- Structured output виден.
- Secrets/API keys не показываются.
- Inspector не выдается за production observability.

### Нельзя

- Показывать secrets.
- Делать full observability platform.
- Делать поиск по всем историческим сессиям.
- Делать prompt version comparison.
- Давать `user` доступ к prompt/context layers.

## 11. Phase 8. Demo scenarios

### Цель

Проверить end-to-end два сценария.

### Сценарии

1. "Курица по-вьетнамски".
2. "Яичница" или "омлет".

### Acceptance / gate

- Оба сценария проходят от первого сообщения до результата.
- Ассистент не формирует карту без уточнений.
- Для адаптированного блюда предлагает ТТК.
- Для простого стандартного блюда не усложняет сценарий и может предложить ТК.
- Warnings/statuses видны.
- Document draft виден.
- `structured_json` доступен.
- Документ помечен как проект.
- JSON не выдается за готовый импорт.
- Copy actions работают.

### Нельзя

- Подгонять сценарии хардкодом в коде.
- Делать ответ только под один заранее известный текст.
- Скрывать ошибки сценария.
- Убирать warnings/statuses ради красивого демо.

## 12. Phase 9. Deployment preparation

### Цель

Подготовить прототип к будущему деплою, но не деплоить без отдельного задания.

### Что сделать

- Убедиться, что secrets не в Git.
- Подготовить `.env.example` только с placeholders, если выбран этот подход.
- Проверить, что app может работать за reverse proxy.
- Проверить, что deployment context не захардкожен в доменной логике.
- Свериться с ops/deployment docs.

### Acceptance / gate

- Нет реальных secrets в Git.
- Нет реального `.env` с ключами.
- Приложение готово к будущему контейнерному деплою на уровне конфигурационной дисциплины.
- Traefik/Docker на сервере не менялись.
- Deployment task остается отдельным.

### Нельзя

- Деплоить.
- Менять Traefik.
- Менять Docker networks.
- Выпускать TLS.
- Останавливать containers.
- Менять firewall/DNS.
- Коммитить `.env`, API keys, tokens, passwords или SSH keys.

## 13. Global stop rules

Остановиться и запросить решение владельца проекта, если:

- нужен выбор стека, который сильно влияет на архитектуру;
- нужно менять сервер;
- нужно коммитить secrets;
- нужно добавлять production state machine;
- нужно делать semantic context engine;
- нужно делать integration с iiko, r_keeper, StoreHouse или 1С;
- нужно добавлять сложную role/permission model;
- нужно делать export PDF/Word/Excel;
- нужно менять prompt/context layers runtime-автоматикой;
- нужно делать provider factory/model fallback system;
- текущая фаза не проходит acceptance criteria;
- roadmap конфликтует с более детальным contract doc.

Если roadmap конфликтует с более детальным contract doc, агент должен остановиться и зафиксировать вопрос. Нельзя молча выбирать вариант.

## 14. Scope guard / что не делать в Demo MVP

В Demo MVP не делать:

- production state machine;
- semantic context engine;
- iiko/r_keeper/StoreHouse/1С integrations;
- PDF/Word/Excel export;
- full RBAC/IAM;
- payment/subscriptions;
- advanced admin panel;
- production audit log;
- model fallback system;
- prompt auto-generation;
- context layers auto-generation by LLM;
- complex design system;
- theme customizer;
- multilingual UI;
- production deployment without separate task.

## 15. Consistency check

Roadmap согласован с текущими документами:

- implementation handoff уже задает общий набор задач и инвариантов;
- acceptance criteria уже фиксируют документационную и будущую демонстрационную готовность;
- frontend visual contract требует desktop/mobile UI, icon-first hints, Russian UI и light theme;
- LLM provider adapter note фиксирует Gemini family через env и adapter boundary;
- ops/deployment docs запрещают deployment и server changes без отдельного task.

Открытый вопрос перед Phase 1: конкретный стек реализации не зафиксирован владельцем проекта. Агент реализации должен предложить минимальный стек и зафиксировать stack decision before coding.

## 16. Связанные документы

- [Implementation handoff](MVP_IMPLEMENTATION_HANDOFF_v0.1.md)
- [Acceptance criteria](MVP_ACCEPTANCE_CRITERIA_v0.1.md)
- [Demo scenarios](MVP_DEMO_SCENARIOS_v0.1.md)
- [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md)
- [File-driven context architecture](MVP_FILE_DRIVEN_CONTEXT_ARCHITECTURE_v0.1.md)
- [SQLite dialogue storage](MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md)
- [LLM provider adapter note](MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md)
- [Frontend visual contract](MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md)
- [Frontend states and errors](MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md)
- [Deployment preparation handoff](../ops/DEPLOYMENT_PREPARATION_HANDOFF_v0.1.md)
