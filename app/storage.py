from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from .security import hash_password, token_hash, verify_password


VALID_ROLES = {"user", "admin"}
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def validate_email(email: str) -> str:
    normalized = normalize_email(email)
    if not normalized or "@" not in normalized or any(char.isspace() for char in normalized) or len(normalized) > 254:
        raise ValueError("Некорректный email.")
    return normalized


def validate_role(role: str) -> str:
    value = str(role or "").strip().lower()
    if value not in VALID_ROLES:
        raise ValueError("Роль должна быть user или admin.")
    return value


def normalize_session_title(title: str) -> str:
    return str(title or "Новая сессия").strip()[:120] or "Новая сессия"


def estimate_tokens(value: Any) -> int:
    text = value if isinstance(value, str) else json.dumps(value or "", ensure_ascii=False)
    return max(0, (len(text) + 3) // 4)


@dataclass(frozen=True)
class User:
    id: int
    email: str
    role: str


class Storage:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self.connect() as conn:
            self._ensure_base_schema(conn)
            self._apply_schema_migrations(conn)
            self._ensure_product_indexes(conn)
            conn.executemany("INSERT OR IGNORE INTO roles(name) VALUES (?)", [("user",), ("admin",)])

    def _ensure_base_schema(self, conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS roles (
                name TEXT PRIMARY KEY
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                role TEXT NOT NULL REFERENCES roles(name),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS auth_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS turn_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                user_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
                assistant_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
                structured_output TEXT NOT NULL,
                trace TEXT NOT NULL,
                document_draft TEXT,
                created_at TEXT NOT NULL
            );
            """
        )

    def _apply_schema_migrations(self, conn: sqlite3.Connection) -> None:
        current = self._schema_version(conn)
        if current < 1:
            if not self._turn_results_has_message_foreign_keys(conn):
                self._rebuild_turn_results_with_message_foreign_keys(conn)
            self._record_schema_migration(conn, 1, "turn_results_message_fks_and_product_indexes")
        if self._schema_version(conn) > SCHEMA_VERSION:
            raise RuntimeError("SQLite schema version is newer than this application.")

    @staticmethod
    def _schema_version(conn: sqlite3.Connection) -> int:
        row = conn.execute("SELECT MAX(version) AS version FROM schema_migrations").fetchone()
        return int(row["version"] or 0)

    @staticmethod
    def _record_schema_migration(conn: sqlite3.Connection, version: int, name: str) -> None:
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, name, applied_at) VALUES (?, ?, ?)",
            (version, name, utc_now()),
        )

    @staticmethod
    def _turn_results_has_message_foreign_keys(conn: sqlite3.Connection) -> bool:
        rows = conn.execute("PRAGMA foreign_key_list(turn_results)").fetchall()
        message_columns = {
            row["from"]
            for row in rows
            if row["table"] == "messages" and row["from"] in {"user_message_id", "assistant_message_id"}
        }
        return message_columns == {"user_message_id", "assistant_message_id"}

    @staticmethod
    def _rebuild_turn_results_with_message_foreign_keys(conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            DROP TABLE IF EXISTS turn_results_v1;

            CREATE TABLE turn_results_v1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                user_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
                assistant_message_id INTEGER REFERENCES messages(id) ON DELETE SET NULL,
                structured_output TEXT NOT NULL,
                trace TEXT NOT NULL,
                document_draft TEXT,
                created_at TEXT NOT NULL
            );

            INSERT INTO turn_results_v1(
                id, session_id, user_message_id, assistant_message_id, structured_output, trace, document_draft, created_at
            )
            SELECT
                tr.id,
                tr.session_id,
                CASE
                    WHEN tr.user_message_id IS NOT NULL
                    AND EXISTS (SELECT 1 FROM messages m WHERE m.id = tr.user_message_id)
                    THEN tr.user_message_id
                    ELSE NULL
                END,
                CASE
                    WHEN tr.assistant_message_id IS NOT NULL
                    AND EXISTS (SELECT 1 FROM messages m WHERE m.id = tr.assistant_message_id)
                    THEN tr.assistant_message_id
                    ELSE NULL
                END,
                tr.structured_output,
                tr.trace,
                tr.document_draft,
                tr.created_at
            FROM turn_results tr
            WHERE EXISTS (SELECT 1 FROM chat_sessions cs WHERE cs.id = tr.session_id);

            DROP TABLE turn_results;
            ALTER TABLE turn_results_v1 RENAME TO turn_results;
            """
        )

    @staticmethod
    def _ensure_product_indexes(conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at ON auth_sessions(expires_at);
            CREATE INDEX IF NOT EXISTS idx_chat_sessions_owner_updated ON chat_sessions(owner_user_id, updated_at DESC, id DESC);
            CREATE INDEX IF NOT EXISTS idx_messages_session_id_id ON messages(session_id, id);
            CREATE INDEX IF NOT EXISTS idx_turn_results_session_id_id ON turn_results(session_id, id);
            CREATE INDEX IF NOT EXISTS idx_turn_results_created_at ON turn_results(created_at);
            """
        )

    def bootstrap_admin(self, email: str, password: str = "", password_hash_value: str = "") -> User | None:
        if not email or (not password and not password_hash_value):
            return None
        email = normalize_email(email)
        stored_hash = password_hash_value or hash_password(password)
        now = utc_now()
        with self.connect() as conn:
            existing = conn.execute("SELECT id, email, role FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                conn.execute(
                    "UPDATE users SET password_hash = ?, role = 'admin' WHERE id = ?",
                    (stored_hash, existing["id"]),
                )
                return User(id=existing["id"], email=existing["email"], role="admin")
            cur = conn.execute(
                "INSERT INTO users(email, password_hash, role, created_at) VALUES (?, ?, 'admin', ?)",
                (email, stored_hash, now),
            )
            return User(id=cur.lastrowid, email=email, role="admin")

    def ensure_demo_user(self) -> User:
        email = "demo-user@local"
        now = utc_now()
        with self.connect() as conn:
            existing = conn.execute("SELECT id, email, role FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                return User(id=existing["id"], email=existing["email"], role=existing["role"])
            cur = conn.execute(
                "INSERT INTO users(email, password_hash, role, created_at) VALUES (?, NULL, 'user', ?)",
                (email, now),
            )
            return User(id=cur.lastrowid, email=email, role="user")

    def authenticate(self, email: str, password: str) -> User | None:
        email = normalize_email(email)
        with self.connect() as conn:
            row = conn.execute("SELECT id, email, role, password_hash FROM users WHERE email = ?", (email,)).fetchone()
            if not row or not row["password_hash"]:
                return None
            if not verify_password(password, row["password_hash"]):
                return None
            return User(id=row["id"], email=row["email"], role=row["role"])

    def list_users(self, current_user_id: int | None = None) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, email, role, password_hash, created_at
                FROM users
                ORDER BY id ASC
                """
            ).fetchall()
        return [self._public_user(row, current_user_id=current_user_id) for row in rows]

    def create_user(self, email: str, password: str, role: str = "user") -> dict[str, Any]:
        email = validate_email(email)
        role = validate_role(role)
        if not str(password or "").strip():
            raise ValueError("Пароль обязателен при создании пользователя.")
        now = utc_now()
        with self.connect() as conn:
            try:
                cur = conn.execute(
                    "INSERT INTO users(email, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                    (email, hash_password(password), role, now),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("Пользователь с таким email уже существует.") from exc
            row = conn.execute(
                "SELECT id, email, role, password_hash, created_at FROM users WHERE id = ?",
                (cur.lastrowid,),
            ).fetchone()
        return self._public_user(row)

    def update_user(
        self,
        user_id: int,
        *,
        email: str | None = None,
        role: str | None = None,
        password: str | None = None,
        current_admin_id: int | None = None,
    ) -> dict[str, Any]:
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT id, email, role, password_hash, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if not existing:
                raise ValueError("Пользователь не найден.")

            fields: list[str] = []
            values: list[Any] = []

            if email is not None:
                fields.append("email = ?")
                values.append(validate_email(email))

            if role is not None:
                next_role = validate_role(role)
                if existing["role"] == "admin" and next_role != "admin":
                    self._ensure_admin_can_be_removed(conn, user_id, current_admin_id)
                fields.append("role = ?")
                values.append(next_role)

            if password is not None and str(password).strip():
                fields.append("password_hash = ?")
                values.append(hash_password(password))

            if fields:
                values.append(user_id)
                try:
                    conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", tuple(values))
                except sqlite3.IntegrityError as exc:
                    raise ValueError("Пользователь с таким email уже существует.") from exc

            row = conn.execute(
                "SELECT id, email, role, password_hash, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return self._public_user(row, current_user_id=current_admin_id)

    def delete_user(self, user_id: int, *, current_admin_id: int | None = None) -> None:
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT id, email, role, password_hash, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if not existing:
                raise ValueError("Пользователь не найден.")
            if existing["role"] == "admin":
                self._ensure_admin_can_be_removed(conn, user_id, current_admin_id)
            # Sticky MVP guard: hard delete cascades demo auth/chat sessions; production retention is future track.
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    def _ensure_admin_can_be_removed(
        self,
        conn: sqlite3.Connection,
        user_id: int,
        current_admin_id: int | None,
    ) -> None:
        # Sticky MVP guard: keep at least one active admin and prevent deleting the current admin session owner.
        if current_admin_id == user_id:
            raise ValueError("Нельзя удалить или понизить текущего admin.")
        row = conn.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'admin'").fetchone()
        if int(row["count"]) <= 1:
            raise ValueError("Нельзя удалить или понизить последнего admin.")

    @staticmethod
    def _public_user(row: sqlite3.Row, current_user_id: int | None = None) -> dict[str, Any]:
        return {
            "id": row["id"],
            "email": row["email"],
            "role": row["role"],
            "created_at": row["created_at"],
            "has_password": bool(row["password_hash"]),
            "is_current": current_user_id == row["id"],
        }

    def create_auth_session(self, token: str, user_id: int, days: int = 7) -> None:
        expires = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(timespec="seconds")
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO auth_sessions(token_hash, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (token_hash(token), user_id, expires, utc_now()),
            )

    def user_for_token(self, token: str) -> User | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT users.id, users.email, users.role, auth_sessions.expires_at
                FROM auth_sessions
                JOIN users ON users.id = auth_sessions.user_id
                WHERE auth_sessions.token_hash = ?
                """,
                (token_hash(token),),
            ).fetchone()
            if not row:
                return None
            if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
                return None
            return User(id=row["id"], email=row["email"], role=row["role"])

    def delete_auth_session(self, token: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_hash(token),))

    def create_chat_session(self, owner_user_id: int, title: str = "Новая сессия") -> int:
        now = utc_now()
        title = normalize_session_title(title)
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO chat_sessions(title, owner_user_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (title, owner_user_id, now, now),
            )
            return int(cur.lastrowid)

    def list_chat_sessions(self, user: User) -> list[dict[str, Any]]:
        with self.connect() as conn:
            if user.role == "admin":
                rows = conn.execute(
                    """
                    SELECT chat_sessions.*, users.email AS owner_email
                    FROM chat_sessions
                    JOIN users ON users.id = chat_sessions.owner_user_id
                    ORDER BY updated_at DESC
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT chat_sessions.*, users.email AS owner_email
                    FROM chat_sessions
                    JOIN users ON users.id = chat_sessions.owner_user_id
                    WHERE owner_user_id = ?
                    ORDER BY updated_at DESC
                    """,
                    (user.id,),
                ).fetchall()
            return [dict(row) for row in rows]

    def admin_dashboard(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        periods = [
            ("day", "Сегодня", datetime(now.year, now.month, now.day, tzinfo=timezone.utc)),
            ("week", "7 дней", now - timedelta(days=7)),
            ("month", "30 дней", now - timedelta(days=30)),
            ("year", "365 дней", now - timedelta(days=365)),
            ("all_time", "Все время", None),
        ]
        with self.connect() as conn:
            period_metrics = [self._period_metrics(conn, key, label, cutoff) for key, label, cutoff in periods]
            latest = conn.execute(
                """
                SELECT
                    chat_sessions.id,
                    chat_sessions.title,
                    chat_sessions.owner_user_id,
                    users.email AS owner_email,
                    chat_sessions.created_at,
                    chat_sessions.updated_at,
                    COUNT(DISTINCT messages.id) AS message_count,
                    COUNT(DISTINCT turn_results.id) AS turn_count,
                    MAX(messages.created_at) AS last_message_at
                FROM chat_sessions
                JOIN users ON users.id = chat_sessions.owner_user_id
                LEFT JOIN messages ON messages.session_id = chat_sessions.id
                LEFT JOIN turn_results ON turn_results.session_id = chat_sessions.id
                GROUP BY chat_sessions.id
                ORDER BY COALESCE(MAX(messages.created_at), chat_sessions.updated_at) DESC
                LIMIT 20
                """
            ).fetchall()
            latest_activity = [self._admin_activity_row(conn, row) for row in latest]
            totals = {
                "users": self._count(conn, "users"),
                "sessions": self._count(conn, "chat_sessions"),
                "messages": self._count(conn, "messages"),
                "turns": self._count(conn, "turn_results"),
            }
        return {
            "periods": period_metrics,
            "totals": totals,
            "latest_activity": latest_activity,
            "token_policy": "provider_usage_when_available_otherwise_estimated_not_billing_usage",
        }

    def can_access_session(self, session_id: int, user: User) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT owner_user_id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return False
            return user.role == "admin" or row["owner_user_id"] == user.id

    def update_chat_session(self, session_id: int, user: User, title: str) -> dict[str, Any]:
        title = normalize_session_title(title)
        with self.connect() as conn:
            row = conn.execute("SELECT owner_user_id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                raise ValueError("Сессия не найдена.")
            if user.role != "admin" and row["owner_user_id"] != user.id:
                raise PermissionError("Нет доступа к сессии.")
            conn.execute(
                "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title, utc_now(), session_id),
            )
            session = conn.execute(
                """
                SELECT chat_sessions.*, users.email AS owner_email
                FROM chat_sessions
                JOIN users ON users.id = chat_sessions.owner_user_id
                WHERE chat_sessions.id = ?
                """,
                (session_id,),
            ).fetchone()
        return dict(session)

    def delete_chat_session(self, session_id: int, user: User) -> None:
        with self.connect() as conn:
            row = conn.execute("SELECT owner_user_id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                raise ValueError("Сессия не найдена.")
            if user.role != "admin" and row["owner_user_id"] != user.id:
                raise PermissionError("Нет доступа к сессии.")
            # Sticky MVP guard: deleting a demo chat cascades messages and turn results, not production retention.
            conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))

    def add_message(self, session_id: int, role: str, content: str) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO messages(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, utc_now()),
            )
            conn.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (utc_now(), session_id))
            return int(cur.lastrowid)

    def list_messages(self, session_id: int, limit: int | None = None) -> list[dict[str, Any]]:
        query = "SELECT id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY id ASC"
        params: tuple[Any, ...] = (session_id,)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        messages = [dict(row) for row in rows]
        if limit is not None and len(messages) > limit:
            return messages[-limit:]
        return messages

    def save_turn_result(
        self,
        session_id: int,
        user_message_id: int,
        assistant_message_id: int,
        structured_output: dict[str, Any],
        trace: dict[str, Any],
    ) -> int:
        document_draft = structured_output.get("document_draft")
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO turn_results(
                    session_id, user_message_id, assistant_message_id, structured_output, trace, document_draft, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_message_id,
                    assistant_message_id,
                    json.dumps(structured_output, ensure_ascii=False),
                    json.dumps(trace, ensure_ascii=False),
                    json.dumps(document_draft, ensure_ascii=False) if document_draft else None,
                    utc_now(),
                ),
            )
            return int(cur.lastrowid)

    def latest_turn_result(self, session_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM turn_results WHERE session_id = ? ORDER BY id DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "structured_output": json.loads(row["structured_output"]),
            "trace": json.loads(row["trace"]),
            "document_draft": json.loads(row["document_draft"]) if row["document_draft"] else None,
            "created_at": row["created_at"],
        }

    def latest_turn_result_any(self) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    turn_results.*,
                    chat_sessions.title AS session_title,
                    users.email AS owner_email
                FROM turn_results
                JOIN chat_sessions ON chat_sessions.id = turn_results.session_id
                JOIN users ON users.id = chat_sessions.owner_user_id
                ORDER BY turn_results.id DESC
                LIMIT 1
                """
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "session_title": row["session_title"],
            "owner_email": row["owner_email"],
            "structured_output": json.loads(row["structured_output"]),
            "trace": json.loads(row["trace"]),
            "document_draft": json.loads(row["document_draft"]) if row["document_draft"] else None,
            "created_at": row["created_at"],
        }

    def session_payload(self, session_id: int, user: User) -> dict[str, Any]:
        with self.connect() as conn:
            session = conn.execute(
                """
                SELECT chat_sessions.*, users.email AS owner_email
                FROM chat_sessions
                JOIN users ON users.id = chat_sessions.owner_user_id
                WHERE chat_sessions.id = ?
                """,
                (session_id,),
            ).fetchone()
        return {
            "session": dict(session) if session else None,
            "messages": self.list_messages(session_id),
            "latest_turn": self.latest_turn_result(session_id),
            "is_admin": user.role == "admin",
        }

    @staticmethod
    def _count(conn: sqlite3.Connection, table: str) -> int:
        row = conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])

    def _period_metrics(
        self,
        conn: sqlite3.Connection,
        key: str,
        label: str,
        cutoff: datetime | None,
    ) -> dict[str, Any]:
        if cutoff is None:
            params: tuple[Any, ...] = ()
            session_where = ""
            message_where = ""
            turn_where = ""
            active_where = ""
        else:
            cutoff_value = cutoff.isoformat(timespec="seconds")
            params = (cutoff_value,)
            session_where = "WHERE created_at >= ?"
            message_where = "WHERE created_at >= ?"
            turn_where = "WHERE created_at >= ?"
            active_where = "WHERE updated_at >= ?"

        sessions = conn.execute(f"SELECT COUNT(*) AS count FROM chat_sessions {session_where}", params).fetchone()
        messages = conn.execute(f"SELECT COUNT(*) AS count FROM messages {message_where}", params).fetchone()
        turns = conn.execute(f"SELECT COUNT(*) AS count FROM turn_results {turn_where}", params).fetchone()
        active_users = conn.execute(
            f"SELECT COUNT(DISTINCT owner_user_id) AS count FROM chat_sessions {active_where}",
            params,
        ).fetchone()
        drafts = conn.execute(
            f"SELECT COUNT(*) AS count FROM turn_results {turn_where} {'AND' if turn_where else 'WHERE'} document_draft IS NOT NULL",
            params,
        ).fetchone()
        return {
            "key": key,
            "label": label,
            "sessions": int(sessions["count"]),
            "messages": int(messages["count"]),
            "turns": int(turns["count"]),
            "active_users": int(active_users["count"]),
            "document_drafts": int(drafts["count"]),
            "estimated_tokens": self._estimated_tokens_for_period(conn, cutoff),
        }

    def _estimated_tokens_for_period(self, conn: sqlite3.Connection, cutoff: datetime | None) -> int:
        if cutoff is None:
            message_rows = conn.execute("SELECT content FROM messages").fetchall()
            turn_rows = conn.execute("SELECT structured_output, trace FROM turn_results").fetchall()
        else:
            cutoff_value = cutoff.isoformat(timespec="seconds")
            message_rows = conn.execute("SELECT content FROM messages WHERE created_at >= ?", (cutoff_value,)).fetchall()
            turn_rows = conn.execute(
                "SELECT structured_output, trace FROM turn_results WHERE created_at >= ?",
                (cutoff_value,),
            ).fetchall()
        total = sum(estimate_tokens(row["content"]) for row in message_rows)
        for row in turn_rows:
            total += estimate_tokens(row["structured_output"])
            trace = json.loads(row["trace"])
            total += self._provider_token_count(trace) or estimate_tokens(trace.get("assembled_context_preview", ""))
        return total

    def _admin_activity_row(self, conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
        latest_turn = conn.execute(
            "SELECT structured_output, trace, created_at FROM turn_results WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (row["id"],),
        ).fetchone()
        latest_status = ""
        latest_turn_at = ""
        estimated_tokens = 0
        if latest_turn:
            structured = json.loads(latest_turn["structured_output"])
            trace = json.loads(latest_turn["trace"])
            latest_status = str(structured.get("workflow_status") or "")
            latest_turn_at = latest_turn["created_at"]
            estimated_tokens += estimate_tokens(latest_turn["structured_output"])
            estimated_tokens += self._provider_token_count(trace) or estimate_tokens(trace.get("assembled_context_preview", ""))
        messages = conn.execute("SELECT content FROM messages WHERE session_id = ?", (row["id"],)).fetchall()
        estimated_tokens += sum(estimate_tokens(message["content"]) for message in messages)
        return {
            "id": row["id"],
            "title": row["title"],
            "owner_user_id": row["owner_user_id"],
            "owner_email": row["owner_email"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_message_at": row["last_message_at"],
            "latest_turn_at": latest_turn_at,
            "message_count": int(row["message_count"]),
            "turn_count": int(row["turn_count"]),
            "workflow_status": latest_status,
            "estimated_tokens": estimated_tokens,
        }

    @staticmethod
    def _provider_token_count(trace: dict[str, Any]) -> int:
        usage = ((trace.get("llm_metadata") or {}).get("usage_metadata") or {})
        for key in ("totalTokenCount", "total_token_count"):
            value = usage.get(key)
            if isinstance(value, int):
                return value
        return 0
