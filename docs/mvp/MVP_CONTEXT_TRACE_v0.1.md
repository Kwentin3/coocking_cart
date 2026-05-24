# MVP context trace v0.1

- Статус: концепт минимальной трассировки такта Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Context trace - минимальная запись о том, как был собран и выполнен один такт.

Trace нужен для отладки Demo MVP: понять, какие layers использовались, какая история попала в context window, какой provider/model вызван и какой structured output получен.

Это не production audit/event log.

## Зачем нужен trace

- Диагностировать неожиданные ответы LLM.
- Проверять, что runtime использовал правильный manifest.
- Проверять порядок context layers.
- Связать structured output с конкретным assembled context window.
- Показать данные в Context Inspector.
- Подготовить почву для будущей observability.

## Минимальные поля trace

Для MVP можно фиксировать:

- `session_id`;
- `turn_id`;
- timestamp;
- context manifest version;
- список context layers;
- order и source file каждого layer;
- количество сообщений истории;
- id или preview последнего user message;
- LLM provider;
- LLM model;
- structured output;
- warnings;
- data statuses;
- document draft, если был сформирован;
- structured JSON, если был сформирован.

## Связь с Context Inspector

Context Inspector может читать trace текущего или последнего такта и показывать:

- какие layers были подключены;
- какая история была добавлена;
- какой provider/model использован;
- какой structured output получен;
- какие warnings/statuses появились.

В MVP можно хранить trace как часть turn result или рядом с ним.

## Отличие от production audit/event log

MVP trace:

- нужен для debug/demo;
- может быть минимальным;
- не обязан быть неизменяемым;
- не обязан покрывать compliance;
- не является юридическим доказательством;
- не заменяет production observability.

Production audit/event log позже должен отдельно решать неизменяемость, версии, actor identity, права, retention, поиск и расследование инцидентов.

## Что не делать в MVP

- Не строить полноценную audit/event subsystem.
- Не проектировать сложные таблицы trace.
- Не хранить secrets или raw API credentials.
- Не делать trace источником правды для юридического утверждения документа.
- Не добавлять сложный event sourcing.
- Не блокировать демо из-за отсутствия production-grade observability.

## Связанные документы

- [Context Inspector](MVP_CONTEXT_INSPECTOR_v0.1.md)
- [Turn contract](MVP_TURN_CONTRACT_v0.1.md)
- [Context window contract](MVP_CONTEXT_WINDOW_CONTRACT_v0.1.md)
- [SQLite dialogue storage](MVP_SQLITE_DIALOGUE_STORAGE_v0.1.md)
