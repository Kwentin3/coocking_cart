# MVP roles and access v0.1

- Статус: минимальный контракт ролей Demo MVP
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Документ фиксирует минимальную систему ролей для Demo MVP.

В MVP достаточно двух ролей:

- `user`;
- `admin`.

Цель - дать будущей реализации простую границу доступа без проектирования production IAM, RBAC или ABAC.

## Почему только две роли

Demo MVP проверяет продуктовую ценность чатового ассистента, file-driven context и structured output. Сложная матрица ролей сейчас создаст лишнюю архитектуру и замедлит прототип.

Роли `technologist`, `manager`, `owner`, `operator` и другие можно рассматривать позже как future track.

## Роль user

`user` - обычный пользователь демо.

Может:

- работать с чатом;
- создавать и вести demo session;
- отправлять сообщения ассистенту;
- получать проект ТК/ТТК;
- видеть `user_answer`;
- видеть warnings;
- видеть data statuses;
- видеть document draft;
- видеть structured JSON в пределах своей сессии.

Не должен:

- редактировать markdown context layers;
- менять context manifest;
- просматривать чужие demo sessions;
- видеть технические diagnostics вне своей сессии;
- управлять bootstrap/admin settings.

## Роль admin

`admin` - пользователь для управления демонстрационным окружением и диагностики.

Может:

- управлять demo-настройками;
- просматривать context layers;
- использовать Context Inspector / debug view;
- просматривать сессии для отладки demo;
- видеть context trace и технические diagnostics в рамках MVP;
- проверять, какие layers попали в context window;
- в будущем управлять prompt/context assets.

Не должен:

- обходить ограничения Demo MVP;
- превращать debug trace в production audit;
- хранить секреты в репозитории;
- использовать Context Inspector как замену production observability.

## Таблица возможностей

| Возможность | user | admin |
| --- | --- | --- |
| Вести чат | Да | Да |
| Создавать demo session | Да | Да |
| Видеть свой `user_answer` | Да | Да |
| Видеть warnings/data statuses | Да | Да |
| Видеть document draft | Да | Да |
| Видеть structured JSON своей сессии | Да | Да |
| Открывать Context Inspector | Нет | Да |
| Смотреть context layers | Нет | Да |
| Смотреть context trace | Нет | Да |
| Смотреть чужие demo sessions для отладки | Нет | Да |
| Управлять demo-настройками | Нет | Да |
| Редактировать prompt/context assets | Нет | Future |

## Связь с Context Inspector

Context Inspector является admin/debug-инструментом MVP.

В первом прототипе пользователь `user` может видеть только результат своей сессии: user-facing ответ, warnings, statuses, draft и structured JSON. Техническая цепочка сборки context window должна быть доступна роли `admin`.

## Связь с bootstrap admin

Первый `admin` создается через bootstrap data contract и environment contract.

Реализация не должна содержать захардкоженный admin email, пароль или hash. Эти значения приходят из безопасного runtime environment или отдельного bootstrap процесса.

## Что не входит в MVP

- Production IAM.
- Сложная RBAC/ABAC-модель.
- Организации и команды.
- Роли `technologist`, `manager`, `owner`.
- Fine-grained permissions.
- SSO/OAuth enterprise flow.
- Admin audit trail production-уровня.

## Future roles

После MVP можно рассмотреть:

- технолог;
- владелец заведения;
- управляющий;
- оператор демо;
- аудитор;
- интеграционный администратор.

Эти роли не входят в Demo MVP.

## Ограничения безопасности

- Секреты не хранятся в репозитории.
- Bootstrap credentials не хардкодятся.
- Admin diagnostics не должны показывать API keys или secrets.
- Context Inspector не должен раскрывать секреты из environment.
- Любая production IAM-модель проектируется отдельно.
