# MVP frontend visual contract v0.1

- Статус: visual/UI contract для будущей реализации Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Документ фиксирует, как должен выглядеть и вести себя frontend Demo MVP, чтобы реализация не превратилась в случайный чат без понятного результата.

Цель интерфейса:

- показать продуктовую ценность за один короткий демо-сценарий;
- дать пользователю чат и рабочие блоки результата одновременно;
- явно показать, что ТК/ТТК является проектом, требующим проверки;
- визуально отделить warnings, data statuses, document draft и structured JSON от основного ответа ассистента;
- дать роли `admin` доступ к Context Inspector/debug-view без раскрытия secrets обычному `user`.

Это не дизайн-макет, не Figma specification и не выбор UI framework.

## Основные экраны

Demo MVP должен иметь минимум:

- login screen;
- main chat screen;
- document/result panel;
- structured JSON panel;
- Context Inspector/debug view для `admin`;
- empty/loading/error states.

## Desktop layout

Для MVP предпочтителен простой three-zone layout:

- top/header: название продукта, текущая роль, кнопка новой сессии, admin/debug toggle для `admin`;
- center: чат с историей user/assistant и input;
- right panel: текущий result/document area с warnings, data statuses и tabs/sections для document draft и structured JSON.

Left sidebar со списком demo sessions допускается, но не обязателен. Если реализация ограничивает scope, достаточно:

- top navigation;
- center chat;
- right result panel.

Причина: основной демо-сценарий должен быстро показывать диалог и результат, а не управление большим списком документов.

## Composition layer

Композиционный слой является частью visual contract. Он фиксирует не стиль, а распределение внимания, ширину чтения и владение контентом между зонами интерфейса.

### Базовая композиция

На desktop интерфейс состоит из трех функциональных зон:

- sessions rail: узкая вторичная зона для выбора demo sessions;
- chat stage: центральная рабочая зона диалога;
- artifact panel: правая зона для document draft, warnings, statuses, JSON, trace и admin tools.

Chat stage может занимать свободное пространство, но сам читаемый чат внутри него не должен растягиваться на всю ширину экрана. На широком desktop лишняя ширина остается воздухом вокруг chat column или отдается artifact/debug панелям.

### Readability rules

Чат должен быть колоночным.

Правила:

- chat column имеет ограниченную максимальную ширину;
- assistant message не должен превращаться в длинную строку на весь экран;
- user message обычно короче assistant message и может быть визуально уже;
- длинные документы, structured JSON, trace и admin tables не рендерятся как chat bubble;
- line-height должен поддерживать чтение длинных уточняющих ответов;
- длинные слова, JSON fragments и технические идентификаторы не должны ломать ширину layout.

Ориентиры для реализации:

- chat column: примерно `640-760px`;
- assistant message: примерно `64-72ch`;
- user message: примерно `48-60ch`;
- result/artifact panel: отдельная колонка или mobile sheet/tab, а не часть chat bubble.

### Content ownership

Chat отвечает за диалог:

- `user_answer`;
- уточняющие вопросы;
- краткое резюме текущего состояния;
- следующий conversational step.

Artifact panel отвечает за артефакты:

- `document_draft`;
- warnings;
- data statuses;
- structured JSON;
- Context Inspector;
- admin user management.

Если structured output содержит большой draft, JSON или trace, чат показывает только user-facing ответ. Большой блок показывается в artifact panel.

### Priority rules

- Основной пользовательский фокус: chat column.
- Вторичный пользовательский фокус: current document/result panel.
- Admin/debug panels не должны вытеснять чат как главный рабочий поток.
- Sessions rail не должен доминировать над экраном.
- На mobile главный поток один: сначала чат, затем result/status/JSON/admin panels через вкладки или stacked sections.

## Mobile layout

На mobile интерфейс должен быть single-flow:

- чат является главным экраном;
- result/document/statuses/JSON открываются через tabs, accordion или bottom sheet;
- Context Inspector для `admin` открывается отдельным экраном или bottom sheet;
- JSON отображается в scrollable/preformatted block и не ломает ширину экрана;
- основные кнопки доступны большим пальцем;
- длинные блоки сворачиваются;
- critical warnings остаются видимыми текстом, а не только иконкой.

## Chat components

Основной чат содержит:

- user message bubble;
- assistant message bubble;
- typing/loading state;
- input field;
- send button;
- new session button;
- quick demo scenario buttons:
  - "Курица по-вьетнамски";
  - "Яичница/омлет";
- optional action button "Сформировать карту", только если контекст уже близок к формированию документа;
- explicit disabled/loading state для всех async actions.

Чат показывает `user_answer`. Остальные поля structured output отображаются в отдельных блоках результата или debug/admin area.

## Chat/session management

Demo sessions являются рабочими чатами MVP. Интерфейс должен поддерживать минимальный CRUD с icon-first controls:

- create: иконка `+` / new session button;
- read/open: выбор session в sessions rail;
- update/rename: иконка edit рядом с session title;
- delete: destructive icon рядом с session title с явным подтверждением.

Правила:

- `user` управляет только своими demo sessions;
- `admin` может управлять видимыми demo sessions для отладки demo;
- действия rename/delete не должны быть спрятаны в длинных текстовых легендах;
- каждая icon action имеет `title` и `aria-label`;
- destructive delete не является primary action и требует подтверждения;
- после create/rename/delete пользователь получает toast или иной terminal feedback;
- удаление session в MVP удаляет связанные messages и turn results через SQLite cascade и не является production retention policy.

## Result/document panel

Result panel должен показывать рабочие блоки результата:

- document title;
- document type: ТК или ТТК;
- status badge: "Проект, требует проверки";
- recipe/ingredients block;
- technology block;
- serving/storage block;
- warnings block;
- data statuses block;
- structured JSON block;
- copy document button;
- copy JSON button;
- new document/session button.

Warnings и data statuses не должны сливаться с основным текстом assistant message. Они должны быть отдельными визуальными блоками или вкладками.

## Icon-first/contextual UI

MVP UI должен предпочитать icon-first/contextual подход вместо длинных постоянных легенд.

Правила:

- не перегружать интерфейс длинными объясняющими текстами;
- рядом с важным блоком показывать компактную иконку;
- по нажатию на иконку открывать contextual popover/sheet/modal;
- contextual window должно быть коротким, актуальным и связанным с конкретным блоком;
- иконки должны иметь accessibility label/title;
- interactive icon должен иметь видимый focus state;
- critical warnings нельзя прятать только за иконку: для критичного риска нужна явная текстовая подпись.

Примеры:

| UI context | Icon meaning | Contextual content |
| --- | --- | --- |
| ТК/ТТК | info | Короткое объяснение разницы ТК и ТТК. |
| Срок хранения | warning | Почему срок требует проверки предприятием. |
| БЖУ | database/reference | Источник или статус данных. |
| Structured JSON | code/json | Открыть машинно-читаемый блок. |
| Context Inspector | trace/debug | Открыть debug-view для `admin`. |

На desktop contextual content может открываться как popover, side panel или modal. На mobile предпочтителен bottom sheet.

## Context Inspector UI

Context Inspector является admin/debug UI.

Визуально он может быть:

- правой debug-панелью;
- отдельной вкладкой;
- отдельным debug screen.

Минимально Context Inspector показывает:

- context manifest path/version;
- context layers;
- dialogue history;
- last user message;
- assembled context preview;
- structured output preview;
- warnings/statuses/document draft/structured JSON.

Каждый markdown layer отображается строкой:

- order;
- name;
- source file;
- short description;
- status;
- expand/collapse control.

По клику слой раскрывает текст layer. Полный assembled context можно показывать как preview, если он слишком длинный.

## Roles in UI

### user

`user` видит:

- чат;
- свои demo sessions;
- `user_answer`;
- warnings;
- data statuses;
- document draft;
- structured JSON своей сессии;
- copy document / copy JSON actions.

`user` не видит:

- prompt/context layers;
- context trace;
- чужие sessions;
- provider diagnostics;
- technical stack traces;
- secrets/API keys.

### admin

`admin` видит:

- все user-facing блоки;
- Context Inspector;
- context trace;
- markdown layers;
- sessions для отладки demo;
- панель управления пользователями Demo MVP;
- technical diagnostics, если они безопасны для показа.

`admin` не должен видеть:

- API keys;
- session secrets;
- bootstrap credentials;
- SSH keys;
- raw `.env` values.

### Admin user management panel

Панель пользователей доступна только роли `admin`.

Минимально показывает:

- список пользователей;
- email;
- роль `user`/`admin`;
- признак текущего admin;
- статус наличия пароля без показа hash;
- действия создать, сохранить, удалить.

Панель не является production admin console и не должна вводить роли, permissions, организации или SSO.

## Theme policy

Для MVP используется одна базовая светлая тема.

Требования:

- обычный текст, warnings, statuses, draft/project badge и admin/debug elements должны различаться визуально;
- warning color не должен использоваться для обычных декоративных элементов;
- status badges должны быть читаемыми;
- focus states должны быть видимыми;
- theme customizer не входит в MVP;
- dark theme остается optional/future.

## Language policy

Для MVP основной язык user-facing UI - русский.

Правила:

- основные кнопки, подписи, предупреждения и пустые состояния на русском;
- technical field names structured output могут оставаться на английском в admin/debug view;
- JSON keys остаются такими, как определены в structured output contract;
- мультиязычность и отдельный английский интерфейс остаются future track.

## UI states

Интерфейс должен явно показывать:

- не авторизован;
- пустая сессия;
- ассистент думает;
- LLM timeout/error;
- structured output parse error;
- context manifest missing;
- markdown layer missing;
- SQLite unavailable;
- API key missing;
- unauthorized access to admin/debug;
- insufficient data to generate card.

Обычный `user` не должен видеть stack traces. `admin` может видеть безопасное debug-summary без secrets.

Подробный states/errors contract вынесен в [MVP frontend states and errors](MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md).

## Copy/export actions

В MVP входят:

- copy document draft;
- copy structured JSON;
- new session.

Optional/future:

- download `.json`.

Out of scope:

- PDF export;
- Word export;
- Excel export;
- direct iiko/r_keeper/1С/StoreHouse import.

## UI-domain boundary

Frontend должен:

- отображать данные structured output;
- показывать states и feedback;
- отправлять user intent: send message, new session, copy, open inspector.

Frontend не должен:

- принимать доменные решения о ТК/ТТК;
- рассчитывать рецептуру как источник истины;
- собирать context window;
- вызывать LLM напрямую в обход runtime/provider adapter;
- хранить prompt/context rules в UI code.

## Связанные документы

- [MVP frontend states and errors](MVP_FRONTEND_STATES_AND_ERRORS_v0.1.md)
- [MVP structured output contract](MVP_STRUCTURED_OUTPUT_CONTRACT_v0.1.md)
- [MVP Context Inspector](MVP_CONTEXT_INSPECTOR_v0.1.md)
- [MVP roles and access](MVP_ROLES_AND_ACCESS_v0.1.md)
- [MVP admin user CRUD blueprint](MVP_ADMIN_USER_CRUD_BLUEPRINT_v0.1.md)
- [MVP implementation handoff](MVP_IMPLEMENTATION_HANDOFF_v0.1.md)
