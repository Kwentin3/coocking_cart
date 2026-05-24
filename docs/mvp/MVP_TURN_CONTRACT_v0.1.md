# MVP turn contract v0.1

- Статус: контракт одного такта Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Такт - один полный цикл взаимодействия пользователя, runtime и LLM.

Такт нужен как явная граница: вход пользователя, сборка context window, вызов LLM, structured output, сохранение результата и переход к следующему сообщению.

Этот контракт не является production state machine.

## Вход такта

Минимальный вход:

- `session_id`;
- новое сообщение пользователя;
- текущий `context_manifest.yml`;
- доступные markdown context layers;
- короткая история user/assistant из SQLite;
- последний сохраненный turn result, если он нужен для debug view.

## Сборка context window

Runtime должен собрать context window в воспроизводимом порядке:

1. Прочитать `context_manifest.yml`.
2. Загрузить markdown layers в указанном порядке.
3. Добавить короткую историю user/assistant сообщений из SQLite.
4. Добавить последнее сообщение пользователя.
5. Добавить инструкцию вернуть полный structured output.
6. Сформировать assembled context window.

Context window должен быть воспроизводимым артефактом: можно понять, какие слои, какая история и какая инструкция ушли в LLM.

## Вызов LLM

Runtime передает assembled context window в LLM через provider adapter boundary.

Для MVP может быть один provider. Важно, чтобы доменная логика не зависела напрямую от конкретного SDK или API провайдера.

## Structured output

LLM должна вернуть structured output по MVP-контракту:

- `user_answer`;
- `workflow_status`;
- `known_facts`;
- `open_questions`;
- `warnings`;
- `data_statuses`;
- `document_draft`;
- `structured_json`;
- `next_step`.

`user_answer` показывается пользователю. Остальные поля сохраняются как служебный результат такта и могут показываться в debug view.

## Сохранение результата

После ответа runtime должен сохранить:

- user message;
- assistant `user_answer`;
- structured output как turn result;
- warnings/statuses;
- document draft, если он сформирован;
- trace metadata, если включен debug/trace режим.

## Переход к следующему такту

Следующий такт начинается с нового сообщения пользователя.

LLM не хранит память между тактами. Runtime снова приносит context window: markdown pack, историю, последнее сообщение и structured output instruction.

## Что такт не делает в MVP

- Не исполняет production state machine.
- Не выполняет approval workflow.
- Не запускает integration adapters.
- Не выполняет production validation layer.
- Не формирует production audit/event log.
- Не создает новые context layers.
- Не меняет `context_manifest.yml` автоматически.

## Связанные документы

- [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md)
- [Structured output contract](MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md)
- [SQLite dialogue storage](MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md)
- [LLM provider adapter note](MVP_LLM_PROVIDER_ADAPTER_NOTE_v0.1.md)
