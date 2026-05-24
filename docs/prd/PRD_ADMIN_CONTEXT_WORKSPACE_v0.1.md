# PRD: Admin context workspace v0.1

- Дата: 2026-05-24
- Статус: feature PRD для Demo MVP
- Контур: Demo MVP

## Назначение

Admin context workspace нужен, чтобы администратор демо видел состояние системы без входа в пользовательский чатовый поток.

Для `admin` основной сценарий отличается от сценария `user`: админу важнее наблюдать активность, проверять чаты, смотреть prompt/context layers и диагностировать context window. Поэтому admin UI должен быть отдельным служебным рабочим местом, а не тем же чатом с дополнительными вкладками.

## Проблема

Текущий admin `Trace` показывает полезные данные, но он слишком технический и привязан к пользовательскому экрану чата.

Проблемы:

- admin вынужден находиться в интерфейсе пользователя;
- список prompt layers не воспринимается как отдельный рабочий экран;
- assembled context preview спрятан внутри trace;
- нет сводки по последней активности пользователей;
- нет видимой динамики чатов, сообщений, turn results и token estimate;
- нет удобного read-only просмотра чатов как операционного инструмента.

## Цель MVP-среза

Сделать удобный read-only admin workspace:

- левую служебную навигацию для admin screens;
- экран дашборда чатов и активности;
- read-only просмотр выбранного чата;
- экран просмотра prompt/context pack;
- просмотр assembled context preview последнего такта;
- сохранение текущего user UI без изменений.

## Роли

### user

`user` продолжает видеть обычный чат, свои сессии, проект документа, warnings, statuses и structured JSON.

User UI в рамках этой фичи не меняется.

### admin

`admin` видит служебное рабочее место:

- `Дашборд` - активность, агрегаты, последние чаты;
- `Промты` - prompt/context layers, manifest, context window preview;
- `Пользователи` - текущий MVP CRUD пользователей.

Admin не видит secrets, API keys, auth session secret, bootstrap credentials, raw `.env` или SSH key material.

## Экран "Дашборд"

Дашборд должен показывать:

- количество пользователей;
- количество чатов;
- количество сообщений;
- количество turn results;
- количество document drafts;
- примерную оценку tokens;
- динамику за день, неделю, месяц, год и все время;
- последние активные чаты;
- владельца чата;
- последний workflow status;
- read-only preview выбранного чата.

Token count в Demo MVP является estimate, если provider usage metadata недоступна. Estimate нельзя выдавать за billing-grade usage.

## Экран "Промты"

Экран prompt/context просмотра должен показывать:

- context manifest path/version/purpose;
- список markdown layers;
- order, file, role, source, status, description;
- текст каждого layer по раскрытию;
- static context pack preview;
- structured output schema/config как отдельный блок;
- latest assembled context preview, если был хотя бы один turn;
- latest structured output и trace metadata без secrets;
- copy actions для layer text, static context и assembled context preview.

Фича является read-only. Редактирование prompt layers через GUI не входит в этот MVP-срез.

## UX-принципы

- Admin workspace использует левую служебную навигацию.
- User chat UI не меняется.
- Длинные тексты prompt/context показываются в scrollable blocks.
- Иконки используются для быстрых действий, но навигация может иметь icon + label.
- Любое действие copy/view дает terminal feedback.
- Empty/loading/error states должны быть явными.

## Non-goals

- Prompt CRUD.
- Runtime-редактирование markdown layers на сервере.
- Автоматическое исправление prompt layers через LLM.
- Production observability.
- Billing-grade token accounting.
- Production analytics.
- Production IAM/RBAC.
- Экспорт отчетов.

## Acceptance

- `admin` видит служебную левую навигацию вместо пользовательского списка сессий.
- `admin` видит dashboard с агрегатами активности.
- `admin` видит последние чаты и может открыть read-only preview.
- `admin` видит prompt/context layers и manifest.
- `admin` видит latest assembled context preview, если есть turn.
- `admin` может копировать layer/static/assembled context blocks.
- `user` UI не изменен.
- Secrets не отображаются.
