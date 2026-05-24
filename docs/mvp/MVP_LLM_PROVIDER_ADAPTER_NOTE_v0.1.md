# MVP LLM provider adapter note v0.1

- Статус: заметка по LLM provider boundary
- Дата: 2026-05-24
- Контур: Demo MVP с future production direction

## Назначение

Demo MVP должен выбрать LLM provider для первой реализации, но не должен размазывать зависимость от конкретного провайдера по всей кодовой базе.

Даже если в MVP используется один provider, вызов LLM должен проходить через минимальный provider adapter boundary.

## Почему нужен adapter boundary

- Доменная логика не должна зависеть от конкретного SDK или API shape.
- Provider можно заменить без переписывания prompt/context assembly.
- Проще логировать provider/model в context trace.
- Проще тестировать runtime-cycle.
- Проще позже добавить capability matrix или provider factory.

## Минимальный контракт adapter для MVP

Adapter получает:

- assembled context window;
- structured output schema / response schema;
- provider/model config;
- request metadata, если нужно для trace.

Adapter возвращает:

- structured output;
- provider name;
- model name;
- timestamp или metadata ответа;
- ошибку в нормализованном виде, если вызов не удался.

## Что остается вне adapter

Adapter не должен:

- собирать markdown context layers;
- читать `context_manifest.yml`;
- решать workflow;
- изменять domain rules;
- создавать context layers;
- хранить историю диалога;
- выполнять validation layer;
- делать integration mapping.

Эти обязанности остаются у runtime orchestration, documentation assets или future production components.

## MVP approach

Для MVP достаточно:

- одного provider;
- одного простого adapter boundary;
- явного места, где вызывается LLM;
- сохранения provider/model в trace;
- отсутствия прямых provider-зависимостей в доменной логике.

Не нужно строить сложную multi-provider архитектуру до появления реальной необходимости.

## Target provider defaults

Для первой реализации Demo MVP целевое provider family: Gemini.

Ожидаемый env value:

- `LLM_PROVIDER=gemini`;
- `LLM_MODEL` задается через env/config. В текущем `.env.example` может быть указан non-secret default model id, но он должен быть проверен по официальной документации Google AI перед первым LLM call.

Likely model family: Gemini Flash. Точное model id должно быть задано через `LLM_MODEL` и подтверждено на момент реализации. Его нельзя хардкодить в доменной логике, prompt/context assembly или UI.

Пример "Gemini Flash 3.1 Preview" можно рассматривать только как ориентир семейства модели, если такое имя актуально и доступно на момент реализации. Документация MVP не фиксирует его как окончательное.

Root [`.env.example`](../../.env.example) фиксирует безопасный шаблон:

- `LLM_PROVIDER=gemini`;
- `LLM_MODEL=<GEMINI_FLASH_MODEL_ID>` или проверенный concrete model id из env;
- `LLM_API_KEY=<GEMINI_API_KEY>`.

Агент реализации должен проверить актуальный Gemini model id в официальной документации Google AI/Gemini перед запуском. Точное имя модели нельзя переносить в код как константу: adapter должен брать provider, model и API key из env/config.

`LLM_MODEL=<GEMINI_FLASH_MODEL_ID>` и `LLM_API_KEY=<GEMINI_API_KEY>` являются placeholders. Adapter не должен принимать placeholder model id или placeholder API key как валидные values. Concrete `LLM_MODEL` из env не является secret, но не должен быть зашит в код.

Если `LLM_MODEL` или `LLM_API_KEY` не заданы или оставлены placeholders, приложение должно вернуть user-safe ошибку и admin/debug hint. Обычный пользователь не должен видеть stack trace, raw provider error или секретные детали окружения.

## Gemini structured output mode

Для Gemini MVP adapter должен использовать structured output API, а не полагаться на prompt-only форматирование.

Официальная спецификация: https://ai.google.dev/gemini-api/docs/structured-output

Практическое правило:

- prompt/context window описывает задачу, правила продукта, workflow, историю и последнее сообщение пользователя;
- adapter передает schema в generation config (`responseMimeType: "application/json"` + `responseJsonSchema` по актуальной Gemini API);
- adapter парсит structured response;
- runtime дополнительно валидирует бизнес-смысл полей и статусы данных.

Если модель возвращает schema-compliant, но семантически слабый результат, это обрабатывается как runtime/domain validation issue, а не как повод переносить JSON-formatting rules обратно в prompt.

Adapter boundary остается обязательным даже при одном provider:

- runtime передает adapter assembled context window и config;
- adapter вызывает provider;
- adapter возвращает normalized structured output или normalized error;
- provider/model пишутся в context trace.

## Future production direction

Позже можно рассмотреть:

- provider factory;
- capability matrix;
- разные модели для разных задач;
- fallback provider;
- cost/latency tracking;
- structured output compatibility checks;
- policy по хранению provider metadata;
- observability по provider/model.

Это future track и не является блокером Demo MVP.

## Связанные документы

- [Turn contract](MVP_TURN_CONTRACT_v0.1.md)
- [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md)
- [Context trace](MVP_CONTEXT_TRACE_v0.1.md)
- [Implementation handoff](MVP_IMPLEMENTATION_HANDOFF_v0.1.md)
