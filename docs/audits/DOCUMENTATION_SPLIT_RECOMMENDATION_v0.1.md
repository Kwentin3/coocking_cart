# Documentation split recommendation v0.1

- Дата: 2026-05-24
- Статус: рекомендация по структуре документации
- Связанный аудит: `docs/audits/DOCUMENTATION_POOL_AUDIT_v0.1.md`

## 1. Как держать два направления в одном репозитории

Репозиторий должен сохранить один общий продуктовый baseline и два отдельных инженерно-документационных контура.

### Common product docs

Общие документы описывают продукт, предметную область, пользовательский workflow, research, glossary и решения. Они не должны зависеть от выбранной реализации.

Common docs могут использоваться и Demo MVP, и future production architecture.

### Demo MVP docs

Demo MVP docs описывают быстрый прототип для демонстрации идеи потенциальному заказчику. Их задача - зафиксировать осознанные компромиссы:

- file-driven context;
- markdown context layers;
- короткая история диалога user/assistant в SQLite;
- простая сборка prompt context из markdown pack и последних сообщений;
- structured output без production-сложности;
- явные demo limitations.

MVP-документы не должны проектировать state machine, полноценный semantic context engine, интеграционные адаптеры или production storage.

### Production architecture docs

Production docs описывают future track. Они нужны, чтобы не потерять правильную архитектурную линию, но не должны блокировать быстрый demo MVP.

Production-контур должен покрывать managed state, state machine, semantic context layer, contract-first context, calculation engine, validation layer, audit/event log, versioning, approval workflow и integrations.

## 2. Рекомендуемая целевая структура

Текущие пути PRD и workflow лучше не переносить без отдельного решения. Консервативнее оставить существующие common-документы на месте и добавить недостающие контуры.

```text
docs/
  README.md

  prd/
    PRD_AI_TECH_CARDS_MVP_v0.1.md
    PRD_AI_TECH_CARDS_MVP_v0.2.md

  product/
    PRODUCT_WORKFLOW_v0.1.md
    PRODUCT_WORKFLOW_v0.2.md
    PRODUCT_VISION_v0.1.md

  research/
    RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_v0.1.md
    RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_ADDENDUM_v0.2.md
    RESEARCH_REFERENCE_DATA_AND_EXPORTS_v0.1.md

  decisions/
    DECISION_LOG.md

  glossary/
    GLOSSARY.md

  mvp/
    README.md
    MVP_SCOPE_v0.1.md
    MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md
    MVP_FILE_DRIVEN_CONTEXT_ARCHITECTURE_v0.1.md
    MVP_MARKDOWN_CONTEXT_LAYERS_v0.1.md
    MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md
    MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md
    MVP_DEMO_LIMITATIONS_v0.1.md

  mvp/context/
    00_AGENT_ROLE.md
    01_PRODUCT_RULES.md
    02_WORKFLOW.md
    03_NORMATIVE_BASE_SHORT.md
    04_TECH_CARD_STRUCTURE.md
    05_DATA_STATUSES.md
    06_OUTPUT_RULES.md
    07_DEMO_LIMITATIONS.md
    context_manifest.yml

  production/
    README.md
    PRODUCTION_ARCHITECTURE_OVERVIEW_v0.1.md
    MANAGED_STATE_LAYER_v0.1.md
    STATE_MACHINE_v0.1.md
    SEMANTIC_CONTEXT_LAYER_v0.1.md
    CONTEXT_ASSEMBLY_ENGINE_v0.1.md
    CALCULATION_ENGINE_v0.1.md
    VALIDATION_LAYER_v0.1.md
    AUDIT_AND_EVENT_LOG_v0.1.md
    DOCUMENT_VERSIONING_v0.1.md
    APPROVAL_WORKFLOW_v0.1.md
    INTEGRATION_ADAPTERS_v0.1.md

  audits/
    DOCUMENTATION_POOL_AUDIT_v0.1.md
    DOCUMENTATION_SPLIT_RECOMMENDATION_v0.1.md

  templates/
    PRD_TEMPLATE.md
    DECISION_RECORD_TEMPLATE.md
    ARCHITECTURE_NOTE_TEMPLATE.md

  archive/
    .gitkeep
```

Примечания:

- `docs/prd/` остается отдельным common-контуром, потому что так уже устроен репозиторий.
- `docs/product/PRODUCT_VISION_v0.1.md` сейчас отсутствует, но его стоит добавить как короткий common-документ.
- `docs/mvp/context/` содержит управляемые markdown layers для runtime context pack. Это документационно-управляемые prompt assets, а не код приложения.
- `context_manifest.yml` нужен только как предложенный manifest контекста. Создавать его стоит вместе с MVP context documents, не в рамках аудита.
- `docs/production/` создается после утверждения MVP-пакета или параллельно только на уровне overview, без deep design.

## 3. Правила связности между контурами

- Common docs могут ссылаться на Demo MVP и Production, но не должны зависеть от их деталей.
- Demo MVP может ссылаться на Common docs как источник продукта, workflow и domain rules.
- Demo MVP не должен ссылаться на production state machine как обязательное runtime-требование.
- Production может ссылаться на Common docs и на MVP docs как на historical/demo baseline, но должна явно помечать отличия production-подхода.
- Markdown context layers должны быть производными от PRD, workflow, research и glossary, но не заменять их.
- Dynamic dialogue history не должна храниться в markdown context layers.

## 4. Какие документы создать следующими первыми

### Приоритет 1

1. `docs/mvp/MVP_SCOPE_v0.1.md`
2. `docs/mvp/MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md`
3. `docs/mvp/MVP_FILE_DRIVEN_CONTEXT_ARCHITECTURE_v0.1.md`
4. `docs/mvp/MVP_MARKDOWN_CONTEXT_LAYERS_v0.1.md`
5. `docs/mvp/MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md`

Цель приоритета 1 - дать минимальную документационную основу для будущей реализации демо-прототипа без production-архитектуры.

### Приоритет 2

1. `docs/mvp/MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md`
2. `docs/mvp/MVP_DEMO_LIMITATIONS_v0.1.md`
3. `docs/production/PRODUCTION_ARCHITECTURE_OVERVIEW_v0.1.md`

Цель приоритета 2 - закрыть runtime-компромисс по истории диалога, явно ограничить демо и сохранить production-направление на уровне overview.

### Приоритет 3

1. `docs/production/MANAGED_STATE_LAYER_v0.1.md`
2. `docs/production/STATE_MACHINE_v0.1.md`
3. `docs/production/SEMANTIC_CONTEXT_LAYER_v0.1.md`
4. `docs/production/CONTEXT_ASSEMBLY_ENGINE_v0.1.md`
5. `docs/production/CALCULATION_ENGINE_v0.1.md`
6. `docs/production/VALIDATION_LAYER_v0.1.md`
7. `docs/production/AUDIT_AND_EVENT_LOG_v0.1.md`
8. `docs/production/DOCUMENT_VERSIONING_v0.1.md`
9. `docs/production/APPROVAL_WORKFLOW_v0.1.md`
10. `docs/production/INTEGRATION_ADAPTERS_v0.1.md`

Цель приоритета 3 - проектировать будущую систему после того, как Demo MVP подтвердит ценность или появятся четкие production-требования.

## 5. Что пока не делать

- Не проектировать production state machine в деталях.
- Не делать полноценный semantic context engine.
- Не делать авторасширение markdown-слоев через LLM.
- Не делать интеграции с iiko, r_keeper, StoreHouse или 1С.
- Не проектировать расчетный движок глубоко.
- Не писать миграции и детальную схему БД.
- Не создавать backend, frontend или инфраструктуру.
- Не добавлять зависимости.
- Не писать код до утверждения MVP-документов.

## 6. Следующий шаг после аудита

1. Согласовать предложенную структуру `docs/`.
2. Создать минимальный пакет Demo MVP docs из приоритета 1.
3. После согласования MVP-документов дать отдельное задание на реализацию прототипа.
4. Production architecture держать как future track и начинать с `PRODUCTION_ARCHITECTURE_OVERVIEW_v0.1.md`, когда появится отдельный запрос.

## 7. Вопросы владельцу продукта

1. Считать ли `PRD_AI_TECH_CARDS_MVP_v0.2.md` окончательным common baseline для демо-пакета или перед MVP-документами нужен короткий `PRODUCT_VISION_v0.1.md`?
2. Какой уровень детализации нужен в первом structured output: только блоки ответа и статусы данных или уже минимальная JSON-схема?
3. Демо должно показывать один сценарий "курица по-вьетнамски" или несколько типов блюд?
4. Нужно ли в первом demo MVP сохранять версии сформированных документов или достаточно истории диалога и последнего structured output?
5. Когда обновлять `docs/README.md`: сразу после утверждения структуры или после создания первых MVP-документов?
