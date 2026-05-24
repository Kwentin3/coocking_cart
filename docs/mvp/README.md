# Demo MVP documentation pack

- Статус: минимальный пакет документации Demo MVP
- Дата: 2026-05-24
- Источники: PRD v0.2, product workflow v0.2, research, glossary, decision log, documentation audit

## Что такое Demo MVP

Demo MVP - демонстрационный прототип AI-ассистента технологических карт общепита. Его задача - быстро показать потенциальному заказчику продуктовую ценность: пользователь описывает блюдо в чате, ассистент уточняет детали, помогает согласовать рецепт, формирует проект ТК/ТТК, показывает предупреждения, статусы данных и structured JSON для будущих интеграций.

Demo MVP не является production-ready системой. Он не утверждает документы юридически, не подтверждает лабораторные данные, не заменяет технолога и не реализует полноценную production-архитектуру.

Для реализации использовать финальную документационную ветку `docs/mvp-final-docs-before-implementation` или cleanup-ветку после merge. Не стартовать реализацию с default branch, если он не содержит финальную MVP-документацию.

Терминология MVP:

- structured output - полный ответ LLM для runtime: `user_answer` и служебные поля;
- user-facing answer / `user_answer` - текст, который видит пользователь в чате;
- document draft / `document_draft` - проект ТК/ТТК, если пользователь запросил карту и данных достаточно;
- structured JSON / `structured_json` - один из блоков structured output, нейтральное машинно-читаемое представление проекта документа для будущих интеграций.

Structured JSON не является форматом iiko, r_keeper, 1С, StoreHouse, production-интеграционной схемой или юридически утвержденным документом.

## Чем Demo MVP отличается от production architecture

В Demo MVP принимается простой file-driven context approach:

- статические части контекстного окна хранятся в markdown-файлах;
- runtime собирает context pack из markdown-слоев;
- короткая история user/assistant сообщений хранится отдельно в SQLite;
- на первых демо-сценариях короткая история диалога может отправляться в LLM целиком;
- structured output используется, но остается минимальным.

Production architecture остается future track. Managed state, state machine, semantic context layer, audit/event log, полноценный calculation engine, validation layer, versioning и integrations не входят в этот пакет.

## Документы MVP-пакета

- [MVP scope](MVP_SCOPE_v0.1.md) - цель, сценарии, включения, исключения и сознательные ограничения Demo MVP.
- [Implementation handoff](MVP_IMPLEMENTATION_HANDOFF_v0.1.md) - порядок чтения и инварианты для будущей реализации прототипа.
- [Implementation roadmap](MVP_IMPLEMENTATION_ROADMAP_v0.1.md) - основной документ порядка реализации по фазам, gates и stop rules.
- [Demo scenarios](MVP_DEMO_SCENARIOS_v0.1.md) - первые сценарии проверки: "курица по-вьетнамски" и "яичница/омлет".
- [Acceptance criteria](MVP_ACCEPTANCE_CRITERIA_v0.1.md) - критерии готовности документации и будущего демо-прототипа.
- [Frontend visual contract](MVP_FRONTEND_VISUAL_CONTRACT_v0.1.md) - desktop/mobile layout, result panel, Context Inspector UI, icon-first подход, language/theme policy.
- [Frontend states and errors](MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md) - обязательные loading/error/empty/success states и user/admin visibility.
- [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md) - из чего состоит контекстное окно каждого такта.
- [Prompt layer contract](MVP_PROMPT_LAYER_CONTRACT_v0.1.md) - контракт отдельного markdown prompt/context layer.
- [Turn contract](MVP_TURN_CONTRACT_v0.1.md) - контракт одного такта взаимодействия.
- [File-driven context architecture](MVP_FILE_DRIVEN_CONTEXT_ARCHITECTURE_v0.1.md) - как runtime собирает контекст без хардкода prompt/domain rules в коде.
- [Context Inspector](MVP_CONTEXT_INSPECTOR_v0.1.md) - концепт debug-view для просмотра сборки context window.
- [Context trace](MVP_CONTEXT_TRACE_v0.1.md) - минимальная трассировка такта для debug/demo.
- [LLM provider adapter note](MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md) - граница интеграции с LLM provider.
- [Roles and access](MVP_ROLES_AND_ACCESS_v0.1.md) - минимальные роли `user` и `admin`.
- [Environment contract](MVP_ENVIRONMENT_CONTRACT_v0.1.md) - env-переменные и placeholders для будущей реализации.
- [Safe env example](../../.env.example) - безопасный root-шаблон `.env.example`; реальные `.env` не коммитятся.
- [Bootstrap data contract](MVP_BOOTSTRAP_DATA_CONTRACT_v0.1.md) - стартовые данные первого запуска без реальных секретов.
- [Markdown context layers](MVP_MARKDOWN_CONTEXT_LAYERS_v0.1.md) - назначение каждого markdown-слоя.
- [Structured output contract](MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md) - минимальный контракт ответа LLM для MVP.
- [SQLite dialogue storage](MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md) - зачем MVP хранит динамическую историю диалога в SQLite.
- [Demo limitations](MVP_DEMO_LIMITATIONS_v0.1.md) - ограничения демо-прототипа.

## Markdown context layers

Рабочие слои для LLM находятся в [context/](context/):

- `00_AGENT_ROLE.md`
- `01_PRODUCT_RULES.md`
- `02_WORKFLOW.md`
- `03_NORMATIVE_BASE_SHORT.md`
- `04_TECH_CARD_STRUCTURE.md`
- `05_DATA_STATUSES.md`
- `06_OUTPUT_RULES.md`
- `07_DEMO_LIMITATIONS.md`
- `context_manifest.yml`

Эти файлы не заменяют PRD, research или workflow. Они являются сжатыми runtime-слоями, производными от common product baseline.

## Динамическая история диалога

Markdown context layers содержат только статический контекст. Динамическая история user/assistant сообщений и служебный structured result хранятся отдельно в SQLite.

LLM не имеет собственной памяти. На каждом такте runtime должен заново собрать рабочее контекстное окно: markdown context pack, короткую историю диалога, последнее сообщение пользователя и инструкцию вернуть полный structured output.

## Вне текущего прохода

В этом проходе не создаются приложение, backend, frontend, зависимости, инфраструктура, миграции или CI. Документы фиксируют будущую реализационную рамку, но не являются кодом.

Для будущей реализации основным документом порядка работ является [MVP implementation roadmap](MVP_IMPLEMENTATION_ROADMAP_v0.1.md). Он не заменяет contracts, но задает фазовый порядок, gate-критерии и stop rules.
