# MVP context window contract v0.1

- Статус: контракт контекстного окна Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Документ фиксирует, из чего состоит контекстное окно каждого обращения к LLM в Demo MVP.

Главный принцип: LLM не имеет собственной памяти. Runtime каждый такт приносит ей рабочее контекстное окно, достаточное для ответа в текущем диалоге.

Контекстное окно должно быть воспроизводимым assembled artifact, а не непрозрачной строкой prompt. После такта должно быть возможно понять, из каких слоев, истории и инструкций оно было собрано.

## Состав контекстного окна

Каждый такт должен включать:

1. Роль ассистента.
2. Правила продукта.
3. Workflow / дорожную карту диалога.
4. Сжатый доменный контекст.
5. Структуру ТК/ТТК.
6. Статусы данных.
7. Ограничения Demo MVP.
8. Короткую цепочку текущего диалога user/assistant.
9. Последнее сообщение пользователя.
10. Task instruction: что сделать в текущем такте.

Structured output schema передается Gemini adapter отдельно через provider generation config. Контекстное окно не должно полагаться на prompt-only форматирование для управления формой ответа.

## Reproducible assembled artifact

Для debug и будущей observability runtime должен уметь показать:

- версию `context_manifest.yml`;
- список подключенных layers;
- порядок layers;
- source file каждого layer;
- краткое назначение layer;
- текст каждого layer;
- сколько сообщений истории добавлено;
- какие user/assistant сообщения добавлены;
- последнее сообщение пользователя;
- task instruction;
- structured output schema/config, переданную provider adapter;
- итоговый assembled context window или его preview.

В MVP это debug-возможность, а не production audit/event log.

## Статическая часть

Статическая часть контекстного окна управляется markdown-файлами в `docs/mvp/context/`.

Эти файлы описывают:

- роль ассистента;
- правила продукта;
- workflow;
- сжатый нормативный контекст;
- структуру документа;
- статусы данных;
- правила ответа;
- ограничения демо.

Статические слои не должны быть захардкожены в коде.

Контракт отдельного markdown layer описан в [MVP_PROMPT_LAYER_CONTRACT_v0.1.md](MVP_PROMPT_LAYER_CONTRACT_v0.1.md).

## Динамическая часть

Динамическая часть - это короткая история user/assistant сообщений и служебный результат прошлых тактов.

История диалога:

- хранится в SQLite;
- не хранится в markdown-файлах;
- добавляется runtime отдельно после markdown context pack;
- на первых демо-сценариях может отправляться в LLM целиком, если диалог короткий.

Диалоговая цепочка является центральной динамической частью контекста, но не единственной частью контекстного окна.

## Последнее сообщение пользователя

Последнее сообщение пользователя должно явно добавляться в конец текущего рабочего окна после истории диалога.

Если оно уже есть в истории, runtime должен избегать смыслового дублирования. Важен принцип: LLM должна видеть актуальный пользовательский запрос как текущий фокус.

## Structured output schema

Каждый такт должен использовать structured output по MVP-контракту.

Structured output - это полный ответ LLM для runtime. Он включает пользовательский `user_answer` и служебные поля. Structured JSON - только один из блоков structured output; он появляется, когда сформирован проект ТК/ТТК.

Для Gemini MVP форма ответа задается через provider-level structured output mechanism: JSON MIME type и JSON Schema/response schema в generation config. Prompt/context объясняет задачу и доменные правила, но не управляет форматом ответа в одиночку.

Минимально ожидаются:

- `user_answer`;
- `workflow_status`;
- `known_facts`;
- `open_questions`;
- `warnings`;
- `data_statuses`;
- `document_draft`;
- `structured_json`;
- `next_step`.

Полный смысл полей описан в [MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md](MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md).

Если проект карты еще не сформирован, `document_draft` и `structured_json` должны быть пустыми или `null`. Runtime не должен трактовать `structured_json` как формат iiko, r_keeper, 1С, StoreHouse или production-интеграционную схему.

## Не-goals

- Не проектировать production memory.
- Не проектировать semantic context layer.
- Не проектировать state machine.
- Не хранить prompt layers в коде.
- Не хранить историю диалога в markdown.
- Не отправлять полный PRD и полный research в каждый запрос без сжатых слоев.
- Не считать MVP debug trace полноценным production audit log.
