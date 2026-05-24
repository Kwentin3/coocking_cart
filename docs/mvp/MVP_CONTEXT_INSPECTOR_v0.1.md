# MVP context inspector v0.1

- Статус: концепт GUI/debug-инструмента Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Context Inspector - debug/demo view для просмотра цепочки сборки context window.

Он нужен, чтобы понимать, почему ассистент ответил именно так: какие markdown layers попали в запрос, какая история диалога была добавлена, какое последнее сообщение пользователя использовалось и какой structured output вернула LLM.

Это не production observability и не forensic audit system. В MVP это легкий инструмент прозрачности и диагностики.

## Кто использует

- Разработчик MVP.
- Демо-оператор.
- Владелец продукта при разборе поведения ассистента.
- Будущий администратор или технолог как возможное направление развития.

## Что показывает

Context Inspector должен показывать:

- context manifest version;
- список context layers;
- order каждого layer;
- source file каждого layer;
- краткое назначение layer;
- раскрытие текста layer по клику или в preview;
- историю user/assistant, добавленную в context;
- последнее сообщение пользователя;
- assembled context window или сокращенный preview;
- structured output LLM;
- warnings, data statuses, document draft и structured JSON.

## Концептуальные секции

### Context manifest

Показывает:

- путь к `context_manifest.yml`;
- версию manifest;
- порядок сборки;
- список активных layers.

### Context layers

Показывает таблицу:

- order;
- layer name;
- role;
- source file;
- source document;
- status;
- short description.

### Layer text preview

Позволяет раскрыть текст выбранного markdown layer.

Цель - быстро увидеть, какие правила реально попали в LLM context.

### Dialogue history

Показывает сообщения user/assistant, которые runtime добавил в текущий context window.

Для MVP достаточно короткой истории.

### Last user message

Показывает последнее сообщение пользователя как текущий фокус такта.

### Assembled context preview

Показывает итоговый assembled context window или его основные части.

Если полный текст слишком длинный, MVP может показывать preview и метаданные: layer count, history message count, approximate length.

### Structured output preview

Показывает structured output, возвращенный LLM:

- `user_answer`;
- `workflow_status`;
- `known_facts`;
- `open_questions`;
- `warnings`;
- `data_statuses`;
- `document_draft`;
- `structured_json`;
- `next_step`.

### Warnings/statuses/document draft

Отдельно выделяет:

- предупреждения;
- статусы данных;
- проект документа;
- structured JSON.

## Что не входит в MVP

- Production observability platform.
- Полноценный audit/event log.
- Ролевая модель доступа к inspector.
- Поиск по всем историческим сессиям.
- Сравнение prompt versions.
- Автоматическое исправление layers.
- Автоматическое создание новых context layers.

## Как может вырасти позже

В production track Context Inspector может стать частью observability/forensic-friendly архитектуры:

- просмотр версий prompt layers;
- сравнение context window между тактами;
- trace по session/turn;
- audit/event log;
- мониторинг provider/model;
- диагностика drift в structured output;
- объяснение статусов данных и источников.

Но это future direction. Для Demo MVP достаточно легкого debug-view.
