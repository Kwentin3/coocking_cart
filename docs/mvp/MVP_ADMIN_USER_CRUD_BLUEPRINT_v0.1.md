# MVP admin user CRUD blueprint v0.1

- Статус: implementation blueprint
- Дата: 2026-05-24
- Контур: Demo MVP

## Назначение

Документ фиксирует минимальный CRUD пользователей для роли `admin` в Demo MVP.

Цель фичи - дать администратору демо возможность заводить и сопровождать пользователей без ручного вмешательства в SQLite или bootstrap env.

Это не production IAM/RBAC. В MVP остаются только роли:

- `user`;
- `admin`.

## Граница фичи

Входит:

- просмотр списка пользователей;
- создание пользователя с email, паролем и ролью `user` или `admin`;
- изменение email, роли и пароля;
- удаление пользователя;
- защита от удаления текущего admin;
- защита от удаления или понижения последнего admin;
- скрытие password hashes и любых secrets из API/UI;
- отображение user management panel только роли `admin`.

Не входит:

- организации, команды, tenant model;
- fine-grained permissions;
- сложная RBAC/ABAC;
- SSO/OAuth;
- production audit trail;
- восстановление пароля по email;
- управление secrets или runtime `.env`;
- просмотр API keys, session secrets, bootstrap password/hash.

## Домены и границы

| Зона | Ответственность | Контракт |
| --- | --- | --- |
| `storage` | CRUD users, password hash, last-admin guard | Python methods returning public user DTO |
| HTTP API | Admin-only routes, validation, user-safe errors | JSON over `/api/admin/users` |
| Frontend | Admin panel for user CRUD | Russian UI, no secrets, accessible feedback |
| Auth/session | Current signed cookie user | Admin identity comes only from server session |
| Docs/report | Blueprint and delivery notes | No `docs/out`, no secrets |

Клиент не передает роль текущего пользователя как authority. API определяет admin-доступ только по текущей server-side session.

## API contract

### `GET /api/admin/users`

Только `admin`.

Response:

```json
{
  "ok": true,
  "users": [
    {
      "id": 1,
      "email": "admin@example.test",
      "role": "admin",
      "created_at": "2026-05-24T00:00:00+00:00",
      "has_password": true,
      "is_current": true
    }
  ]
}
```

### `POST /api/admin/users`

Только `admin`.

Request:

```json
{
  "email": "new-user@example.test",
  "password": "temporary-password",
  "role": "user"
}
```

Rules:

- `email` обязателен, нормализуется в lower-case;
- `password` обязателен при создании;
- `role` может быть только `user` или `admin`;
- duplicate email возвращает user-safe ошибку;
- response не возвращает password hash.

### `PATCH /api/admin/users/{id}`

Только `admin`.

Request:

```json
{
  "email": "changed@example.test",
  "role": "admin",
  "password": "new-password-or-empty"
}
```

Rules:

- пустой `password` означает "не менять пароль";
- нельзя понизить последнего admin;
- нельзя понизить собственную текущую admin-сессию;
- response не возвращает password hash.

### `DELETE /api/admin/users/{id}`

Только `admin`.

Rules:

- нельзя удалить текущего admin;
- нельзя удалить последнего admin;
- удаление пользователя в MVP удаляет связанные auth sessions и demo chat sessions через SQLite foreign keys;
- это допустимо для demo storage, но не является production retention policy.

## UI contract

Admin получает отдельную вкладку или панель "Пользователи" в рабочем интерфейсе.

Panel показывает:

- форму создания пользователя;
- список пользователей;
- email;
- роль;
- статус наличия пароля;
- признак текущего admin;
- действия сохранить / удалить.

`user` не видит вкладку пользователей и не может вызвать API.

UI не показывает:

- password hashes;
- raw session tokens;
- API keys;
- auth session secret;
- bootstrap password/hash;
- raw `.env`.

## Sticky implementation comments

В коде допустимы короткие sticky comments только в местах, где будущий агент может ошибочно расширить MVP до production IAM:

- рядом с guard последнего admin;
- рядом с каскадным удалением demo sessions;
- рядом с admin-only API boundary.

Комментарии должны объяснять ограничение, а не пересказывать очевидный код.

## Acceptance checks

- admin может создать `user`;
- admin может создать другого `admin`;
- admin может изменить email/role/password пользователя;
- admin может удалить обычного пользователя;
- user не может открыть `/api/admin/users`;
- API не возвращает password hash;
- текущий admin не может удалить себя;
- последний admin не может быть удален или понижен;
- `.env`, secrets и SQLite runtime files не попадают в Git;
- UI показывает CRUD только admin;
- тесты проходят локально.

## Open questions

- Нужна ли позже soft-delete модель вместо hard delete?
- Нужен ли отдельный audit trail для admin CRUD в production?
- Нужно ли позже разделить demo operator и system admin?

Ответы на эти вопросы не блокируют Demo MVP и относятся к future track.
