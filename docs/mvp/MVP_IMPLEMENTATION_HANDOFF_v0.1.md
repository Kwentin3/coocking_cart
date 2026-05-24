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
8. [Context manifest](context/context_manifest.yml)

Дополнительно полезно прочитать:

- [Markdown context layers](MVP_MARKDOWN_CONTEXT_LAYERS_v0.1.md)
- [SQLite dialogue storage](MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md)
- [Demo limitations](MVP_DEMO_LIMITATIONS_v0.1.md)
- [Demo scenarios](MVP_DEMO_SCENARIOS_v0.1.md)
- [Acceptance criteria](MVP_ACCEPTANCE_CRITERIA_v0.1.md)

## 3. Что реализовать в MVP

На уровне задачи, без выбора стека:

- простой чат;
- загрузку markdown context layers через `context_manifest.yml`;
- хранение истории диалога в SQLite;
- сборку context window на каждый такт;
- вызов LLM;
- обработку structured output;
- отображение `user_answer`;
- отображение warnings, data statuses, document draft и structured JSON;
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

## 5. Инварианты реализации

- В коде не должно быть доменных prompts, нормативных правил или скрытой предметной семантики.
- Markdown context layers являются источником статического контекста.
- `context_manifest.yml` задает порядок сборки markdown layers.
- SQLite хранит только динамическую историю диалога и результаты тактов.
- История диалога не хранится в markdown-файлах.
- LLM не имеет собственной памяти.
- Каждый такт получает заново собранное context window.
- Structured output является полным ответом LLM для runtime.
- `user_answer` является пользовательской частью structured output.
- `structured_json` является только одним блоком structured output и не является форматом учетной системы.
- Итоговый документ всегда является проектом, требующим проверки ответственным лицом предприятия.

## 6. Минимальный порядок реализации

1. Поднять пустой чатовый сценарий.
2. Научить runtime читать `context_manifest.yml`.
3. Научить runtime загружать markdown layers в указанном порядке.
4. Добавить SQLite-хранение session/message/turn result на концептуально минимальном уровне.
5. Собрать context window: markdown pack, короткая история, последнее сообщение пользователя, инструкция structured output.
6. Вызвать LLM и получить structured output.
7. Показать `user_answer`.
8. Показать служебные блоки для демо: warnings, data statuses, document draft, structured JSON.
9. Прогнать два demo scenarios.

## 7. Критерий остановки

Реализация MVP считается достаточной для демонстрации, когда оба demo scenarios проходят end-to-end, а результат явно показывает проектный статус документа, предупреждения, статусы данных и structured JSON.

Если возникает соблазн добавить state machine, semantic context engine, интеграционный адаптер или расчетный движок, это отдельная future-track задача, а не часть этого MVP handoff.
