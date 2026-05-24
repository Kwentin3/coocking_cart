# MVP implementation handoff v0.1

- Статус: handoff для будущей реализации Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## 1. Цель реализации

Создать демонстрационный прототип AI-ассистента технологических карт общепита.

Прототип должен показать, что пользователь может через короткий чат перейти от идеи блюда к проекту ТК/ТТК, предупреждениям, статусам данных и structured JSON для будущих интеграций.

Это не production-ready система и не юридическое утверждение технологической карты.

## 2. Читать в первую очередь

Перед реализацией читать документы в таком порядке:

1. [PRD MVP v0.2](../prd/PRD_AI_TECH_CARDS_MVP_v0.2.md)
2. [Product workflow v0.2](../product/PRODUCT_WORKFLOW_v0.2.md)
3. [Demo MVP README](README.md)
4. [MVP scope](MVP_SCOPE_v0.1.md)
5. [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md)
6. [File-driven context architecture](MVP_FILE_DRIVEN_CONTEXT_ARCHITECTURE_v0.1.md)
7. [Structured output contract](MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md)
8. [Prompt layer contract](MVP_PROMPT_LAYER_CONTRACT_v0.1.md)
9. [Turn contract](MVP_TURN_CONTRACT_v0.1.md)
10. [Context manifest](context/context_manifest.yml)

Дополнительно полезно прочитать:

- [Markdown context layers](MVP_MARKDOWN_CONTEXT_LAYERS_v0.1.md)
- [SQLite dialogue storage](MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md)
- [Demo limitations](MVP_DEMO_LIMITATIONS_v0.1.md)
- [Context Inspector](MVP_CONTEXT_INSPECTOR_v0.1.md)
- [Context trace](MVP_CONTEXT_TRACE_v0.1.md)
- [LLM provider adapter note](MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md)
- [Roles and access](MVP_ROLES_AND_ACCESS_v0.1.md)
- [Environment contract](MVP_ENVIRONMENT_CONTRACT_v0.1.md)
- [Bootstrap data contract](MVP_BOOTSTRAP_DATA_CONTRACT_v0.1.md)
- [Ops README](../ops/README.md)
- [Deployment context template](../ops/DEPLOYMENT_CONTEXT_TEMPLATE_v0.1.md)
- [Demo scenarios](MVP_DEMO_SCENARIOS_v0.1.md)
- [Acceptance criteria](MVP_ACCEPTANCE_CRITERIA_v0.1.md)

## 3. Что реализовать в MVP

На уровне задачи, без выбора стека:

- простой чат;
- загрузку markdown context layers через `context_manifest.yml`;
- хранение истории диалога в SQLite;
- сборку context window на каждый такт;
- вызов LLM через минимальный provider adapter boundary;
- обработку structured output;
- отображение `user_answer`;
- отображение warnings, data statuses, document draft и structured JSON;
- debug-view или Context Inspector для основных частей context window;
- минимальный context trace такта;
- роли `user` и `admin`;
- bootstrap admin через environment/bootstrap contract;
- два демо-сценария: "курица по-вьетнамски" и "яичница/омлет".

## 4. Что не реализовывать

- Production state machine.
- Semantic context engine.
- Production calculation engine.
- Интеграции с iiko, r_keeper, StoreHouse или 1С.
- Сложные роли и права.
- Approval workflow.
- Авторасширение context layers через LLM.
- Хардкод доменных prompts в коде.
- Production audit/event log.
- Production document versioning.
- Миграции и сложный storage design сверх простого SQLite для демо.
- Provider factory и capability matrix.
- Production observability вместо MVP debug/trace.
- Сложную RBAC/ABAC или production IAM.
- Реальные deployment config, Docker/Traefik/TLS настройки.

## 5. Инварианты реализации

- В коде не должно быть доменных prompts, нормативных правил или скрытой предметной семантики.
- Markdown context layers являются источником статического контекста.
- `context_manifest.yml` задает порядок сборки markdown layers.
- SQLite хранит только динамическую историю диалога и результаты тактов.
- История диалога не хранится в markdown-файлах.
- LLM не имеет собственной памяти.
- Каждый такт получает заново собранное context window.
- Context window должен быть воспроизводимым assembled artifact.
- Реализация должна уметь показать, какие markdown layers были использованы в такте.
- Provider integration должна быть изолирована хотя бы минимальным adapter boundary.
- Trace/debug output не должен подменять production audit/event log.
- Structured output является полным ответом LLM для runtime.
- `user_answer` является пользовательской частью structured output.
- `structured_json` является только одним блоком structured output и не является форматом учетной системы.
- Итоговый документ всегда является проектом, требующим проверки ответственным лицом предприятия.
- Роли MVP: только `user` и `admin`.
- Bootstrap admin создается через env/bootstrap contract.
- Secrets не хардкодятся.
- LLM provider/model/API key приходят через environment.
- Context paths приходят через env или config boundary.
- Deployment details не должны быть выдуманы агентом.

## 6. Минимальный порядок реализации

1. Поднять пустой чатовый сценарий.
2. Научить runtime читать `context_manifest.yml`.
3. Научить runtime загружать markdown layers в указанном порядке.
4. Прочитать environment settings без хардкода secrets.
5. Создать bootstrap admin и роли `user`/`admin` через bootstrap contract.
6. Добавить SQLite-хранение session/message/turn result на концептуально минимальном уровне.
7. Собрать context window: markdown pack, короткая история, последнее сообщение пользователя, инструкция structured output.
8. Сохранить или подготовить минимальный context trace.
9. Вызвать LLM через provider adapter boundary и получить structured output.
10. Показать `user_answer`.
11. Показать служебные блоки для демо: warnings, data statuses, document draft, structured JSON.
12. Показать debug-view основных частей context window.
13. Прогнать два demo scenarios.

## 7. Критерий остановки

Реализация MVP считается достаточной для демонстрации, когда оба demo scenarios проходят end-to-end, а результат явно показывает проектный статус документа, предупреждения, статусы данных и structured JSON.

Если возникает соблазн добавить state machine, semantic context engine, интеграционный адаптер или расчетный движок, это отдельная future-track задача, а не часть этого MVP handoff.
