# Production architecture future track

- Статус: placeholder будущей production-архитектуры
- Дата: 2026-05-24

Production architecture остается future track и не блокирует Demo MVP.

Сейчас репозиторий фиксирует быстрый демонстрационный подход в `docs/mvp/`: file-driven context, markdown context layers, SQLite для короткой истории диалога и минимальный structured output.

Будущий production-контур позже должен покрыть:

- managed state;
- state machine;
- semantic context layer;
- contract-first context;
- prompt layer registry;
- context assembly engine;
- provider adapters/factory;
- provider capability matrix;
- context inspector / observability;
- context trace / audit log;
- calculation engine;
- validation layer;
- audit/event log;
- document versioning;
- approval workflow;
- integration adapters.

В этом проходе production state machine, semantic context engine, расчетный движок, валидация, аудит, версионирование и интеграции не проектируются в деталях.

## Возможные future documents

Когда появится отдельная production-задача, можно создать:

- `PRODUCTION_CONTEXT_ASSEMBLY_ENGINE_v0.1.md`;
- `PRODUCTION_PROMPT_LAYER_REGISTRY_v0.1.md`;
- `PRODUCTION_PROVIDER_ADAPTERS_AND_FACTORY_v0.1.md`;
- `PRODUCTION_CONTEXT_OBSERVABILITY_v0.1.md`;
- `PRODUCTION_CONTEXT_TRACE_AND_AUDIT_LOG_v0.1.md`;
- `PRODUCTION_MANAGED_STATE_LAYER_v0.1.md`;
- `PRODUCTION_STATE_MACHINE_v0.1.md`;
- `PRODUCTION_CALCULATION_ENGINE_v0.1.md`;
- `PRODUCTION_VALIDATION_LAYER_v0.1.md`;
- `PRODUCTION_APPROVAL_WORKFLOW_v0.1.md`;
- `PRODUCTION_INTEGRATION_ADAPTERS_v0.1.md`.

Не нужно создавать эти документы до отдельного production architecture pass.
