# Documentation pool audit v0.1

- Дата: 2026-05-24
- Статус: аудит текущего документационного пула
- Ветка: `docs/documentation-pool-audit`
- Область: разделение документации на общий продуктовый контур, Demo MVP и future production architecture

## 1. Краткое резюме

Текущая документация уже хорошо покрывает product discovery: есть актуальный PRD v0.2, первая версия PRD v0.1, workflow v0.1/v0.2, research по нормативной базе, addendum к research, research по справочным данным и будущим экспортам, glossary, decision log и шаблоны.

Код приложения, backend, frontend, инфраструктура и зависимости в репозитории отсутствуют. Это соответствует текущему статусу проекта: сначала документация и согласование продукта, затем реализация.

Главный разрыв сейчас не в качестве продуктовых документов, а в отсутствии явного разделения на два документационных контура:

- Demo MVP - быстрый демонстрационный прототип с file-driven context, markdown context layers, SQLite для истории диалога и простым structured output.
- Production architecture - будущий контур с managed state, state machine, semantic context layer, расчетным движком, валидатором, audit/event log, версионированием и интеграциями.

Если это не развести явно, следующие задачи могут начать смешивать быстрый демо-путь с полноценной production-архитектурой.

## 2. Найденная структура

```text
README.md
docs/
  README.md
  archive/
    .gitkeep
  decisions/
    DECISION_LOG.md
  glossary/
    GLOSSARY.md
  prd/
    PRD_AI_TECH_CARDS_MVP_v0.1.md
    PRD_AI_TECH_CARDS_MVP_v0.2.md
  product/
    PRODUCT_WORKFLOW_v0.1.md
    PRODUCT_WORKFLOW_v0.2.md
  research/
    RESEARCH_REFERENCE_DATA_AND_EXPORTS_v0.1.md
    RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_v0.1.md
    RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_ADDENDUM_v0.2.md
  templates/
    DECISION_RECORD_TEMPLATE.md
    PRD_TEMPLATE.md
```

Инвентаризация по типам:

- PRD: `PRD_AI_TECH_CARDS_MVP_v0.1.md`, `PRD_AI_TECH_CARDS_MVP_v0.2.md`.
- Workflow: `PRODUCT_WORKFLOW_v0.1.md`, `PRODUCT_WORKFLOW_v0.2.md`.
- Research: нормативная база v0.1, addendum v0.2, справочные данные и экспорты v0.1.
- Decision log: `docs/decisions/DECISION_LOG.md`.
- Glossary: `docs/glossary/GLOSSARY.md`.
- Templates: PRD template и decision record template.
- Docs navigation: `docs/README.md`.
- Dedicated Demo MVP docs: отсутствуют.
- Dedicated production architecture docs: отсутствуют.
- Context markdown layers: отсутствуют.

## 3. Классификация документов

| Файл | Назначение | Текущая категория | Действие | Комментарий |
| --- | --- | --- | --- | --- |
| `README.md` | Корневая справка о статусе проекта | Common | Оставить как есть | Четко фиксирует, что код приложения пока не реализуется. |
| `docs/README.md` | Навигация по документации | Common | Обновить позже | Сейчас полезен, но после согласования структуры должен получить ссылки на `mvp/`, `production/` и `audits/`. |
| `docs/prd/PRD_AI_TECH_CARDS_MVP_v0.2.md` | Актуальный продуктовый PRD | Common | Оставить как основной PRD | Документ продуктовый, не инженерный. Подходит и для Demo MVP, и как baseline для future production. |
| `docs/prd/PRD_AI_TECH_CARDS_MVP_v0.1.md` | Первый черновик PRD | Common / history | Оставить как историческую версию | Не использовать как активную спецификацию, но сохранять для трассировки эволюции продукта. |
| `docs/product/PRODUCT_WORKFLOW_v0.2.md` | Актуальный пользовательский workflow | Common | Оставить как общий workflow | Хорошо отделяет кулинарную гипотезу от проекта документа. Может стать источником для MVP context layer `02_WORKFLOW.md`. |
| `docs/product/PRODUCT_WORKFLOW_v0.1.md` | Первый workflow | Common / history | Оставить как историческую версию | Полезен как ранний baseline, но v0.2 должен считаться актуальным. |
| `docs/research/RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_v0.1.md` | Нормативная база и продуктовые следствия | Common | Оставить как research | Подходит для обоих контуров. Для MVP нужен короткий извлеченный слой, а не весь research в prompt context. |
| `docs/research/RESEARCH_TECH_CARDS_RU_NORMATIVE_BASE_ADDENDUM_v0.2.md` | Уточнение актуальности нормативного контекста | Common | Оставить как research | Перед production-проектированием потребуется повторная проверка актуальности нормативных ссылок. |
| `docs/research/RESEARCH_REFERENCE_DATA_AND_EXPORTS_v0.1.md` | Справочные данные, БЖУ, JSON, будущие интеграции | Common / ambiguous | Требует разведения позже | Полезен для MVP JSON, но также содержит production-темы: версии справочников, интеграции, учетные системы. |
| `docs/decisions/DECISION_LOG.md` | Журнал продуктовых решений | Common | Обновить | Нужно зафиксировать разведение Demo MVP и production architecture. |
| `docs/glossary/GLOSSARY.md` | Термины предметной области | Common | Оставить как есть, расширить позже | Сейчас покрывает продуктовые термины. Для production позже нужны managed state, state machine, semantic context, context contract. |
| `docs/templates/PRD_TEMPLATE.md` | Шаблон PRD | Common / template | Оставить как есть | Полезен для будущих продуктовых документов. |
| `docs/templates/DECISION_RECORD_TEMPLATE.md` | Шаблон decision record | Common / template | Оставить как есть | Можно использовать для будущих ADR/architecture decisions. |
| `docs/archive/.gitkeep` | Пустой placeholder архива | Common / repo hygiene | Оставить как есть | Архив пока не используется. |

## 4. Что уже хорошо

- PRD v0.2 уже понятен для продуктового обсуждения с владельцем кафе, технологом, поваром, инвестором или партнером.
- PRD v0.2 не пытается описывать внутреннюю инженерную архитектуру, что сохраняет его читаемость для нетехнической аудитории.
- Workflow v0.2 хорошо разводит кулинарную гипотезу, подтверждение пользователем и проект документа.
- В workflow уже явно обозначены статусы данных и граница ответственности предприятия.
- Decision log уже фиксирует ключевые продуктовые решения и последствия.
- Research по нормативной базе дает полезные ограничения для MVP: проект документа, предупреждения, неподтвержденные поля, человеческое утверждение.
- Research по справочным данным правильно выносит прямые интеграции за пределы MVP.
- Glossary уже закрывает базовые термины предметной области.
- Репозиторий пока не содержит приложения и зависимостей, поэтому документационный split можно сделать без миграций и технического долга.

## 5. Что требует разведения

- Demo MVP и future production architecture нельзя смешивать в одном архитектурном документе. У них разные цели, риски и уровень строгости.
- File-driven context для Demo MVP нужно описать отдельно от production semantic context layer.
- Markdown context layers для MVP должны быть управляемым набором файлов, а не случайными фрагментами из PRD.
- SQLite dialogue storage для MVP нужно описать как простой runtime-компромисс, без детального проектирования production storage.
- Structured output для MVP должен быть простым контрактом ответа, а не полноценной доменной схемой production-уровня.
- Research по `canonical JSON` и будущим интеграциям нужно позднее разделить на MVP structured output и production integration adapters.
- Production managed state, state machine, audit/event log и versioning должны остаться future track до отдельного architecture pass.
- `docs/README.md` сейчас не отражает будущие контуры `mvp/` и `production/`, но обновлять навигацию лучше после утверждения структуры.

## 6. Риски

- Если не развести документы, агент может начать строить production-архитектуру вместо быстрого демонстрационного MVP.
- Если все описывать только как MVP, потеряется стратегическое направление production-системы.
- Если захардкодить prompts, правила продукта и доменную семантику в коде, дальнейший рефакторинг контекста будет болезненным.
- Если не зафиксировать ограничения MVP, демо могут принять за production-ready продукт.
- Если отправлять в контекст полный PRD и полный research без сжатых слоев, окно контекста быстро станет шумным и дорогим.
- Если structured output сразу сделать слишком сложным, MVP начнет обслуживать схему вместо демонстрации ценности.
- Если dynamic dialogue history хранить в markdown, появится смешение runtime state и документации.
- Если production topics не вынести в отдельный контур, future state machine и semantic context layer начнут конфликтовать с простым file-driven MVP.

## 7. Рекомендации

1. Сохранять существующие product discovery документы без переименований на этом этапе.
2. Считать `docs/prd/PRD_AI_TECH_CARDS_MVP_v0.2.md` и `docs/product/PRODUCT_WORKFLOW_v0.2.md` актуальным common baseline.
3. Добавить отдельный контур `docs/mvp/` для демонстрационного прототипа.
4. Добавить отдельный контур `docs/mvp/context/` для markdown context layers.
5. Добавить отдельный контур `docs/production/` для будущей production-архитектуры.
6. Описывать Demo MVP как осознанный компромисс: markdown context pack плюс короткая история user/assistant сообщений из SQLite.
7. Описывать structured output в MVP минимально: рабочий контракт ответа, warnings, data statuses и machine-readable draft, без production-схемы.
8. Зафиксировать в decision log, что state machine, semantic context layer, полноценный расчетный движок, validation layer, audit/event log и integrations остаются future track.
9. После согласования структуры создать минимальный пакет MVP-документов, и только после этого выдавать отдельное задание на реализацию прототипа.
