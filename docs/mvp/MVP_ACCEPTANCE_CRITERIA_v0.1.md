# MVP acceptance criteria v0.1

- Статус: критерии готовности документации и будущего Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Документ определяет, когда MVP-документация достаточна для старта реализации и когда будущий прототип можно считать демонстрационно готовым.

Эти критерии не являются production acceptance criteria. Они описывают только Demo MVP.

## Критерии документационной готовности

Документация достаточна для старта реализации, если есть:

- PRD v0.2;
- workflow v0.2;
- MVP scope;
- context window contract;
- file-driven context architecture;
- markdown context layers и manifest;
- prompt layer contract;
- turn contract;
- context inspector concept;
- context trace concept;
- LLM provider adapter note;
- roles/access contract;
- environment contract;
- bootstrap data contract;
- ops placeholder docs;
- structured output contract;
- SQLite dialogue storage concept;
- demo limitations;
- implementation handoff;
- demo scenarios;
- acceptance criteria.

Также должно быть явно зафиксировано:

- Demo MVP не production-ready система;
- production architecture остается future track;
- structured output и structured JSON разведены терминологически;
- `docs/out/` не является частью проектной документации.

## Критерии будущей реализации

Будущий прототип можно считать демонстрационно готовым, если:

- приложение загружает markdown context layers через `context_manifest.yml`;
- код не содержит захардкоженных доменных prompt rules;
- история user/assistant хранится в SQLite;
- каждый такт собирает context window;
- LLM возвращает structured output;
- frontend показывает `user_answer`;
- frontend или debug view показывает warnings, data statuses, document draft и structured JSON;
- можно увидеть список использованных context layers;
- можно увидеть structured output;
- можно увидеть debug-представление собранного context window или его основных частей;
- LLM provider вызов изолирован минимальным adapter boundary;
- есть роли `user` и `admin`;
- bootstrap admin можно создать без ручного вмешательства в код;
- LLM provider/model/API key не хардкодятся;
- context manifest path не хардкодится глубоко в доменной логике;
- secrets не попадают в репозиторий;
- работает сценарий "курица по-вьетнамски";
- работает сценарий "яичница/омлет";
- результат явно помечен как проект, требующий проверки;
- structured JSON не выдается за формат iiko, r_keeper, StoreHouse или 1С;
- LLM не создает и не подключает новые context layers автоматически.
- trace/debug output не выдается за production audit/event log.

## Минимальная демонстрационная проверка

Перед показом потенциальному заказчику нужно пройти:

1. Новый чат по сценарию "курица по-вьетнамски".
2. Новый чат по сценарию "яичница" или "омлет".
3. Проверку, что в обоих сценариях виден `user_answer`.
4. Проверку, что служебные поля structured output доступны в UI или debug view.
5. Проверку, что документ не представлен как юридически утвержденный.

## Что не является блокером для Demo MVP

- Нет production state machine.
- Нет semantic context engine.
- Нет production calculation engine.
- Нет интеграционных адаптеров.
- Нет сложных ролей и approval workflow.
- Нет production audit/event log.
- Нет production document versioning.

Эти темы остаются future track и не должны задерживать демонстрационную готовность.

## Условия остановки перед реализацией

Реализацию можно начинать после согласования:

- состава MVP-пакета;
- двух demo scenarios;
- минимального structured output contract;
- prompt layer contract;
- turn contract;
- правила, что markdown context layers являются источником статического контекста;
- правила, что SQLite хранит динамическую историю и результаты тактов;
- правила, что provider integration изолируется через adapter boundary;
- roles/access contract;
- environment contract;
- bootstrap data contract;
- ops placeholder docs.
