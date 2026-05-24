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
- context assembly engine;
- calculation engine;
- validation layer;
- audit/event log;
- document versioning;
- approval workflow;
- integration adapters.

В этом проходе production state machine, semantic context engine, расчетный движок, валидация, аудит, версионирование и интеграции не проектируются в деталях.
