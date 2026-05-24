from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from .security import hash_password, token_hash, verify_password


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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
            conn.executescript(
                """
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
                    user_message_id INTEGER,
                    assistant_message_id INTEGER,
                    structured_output TEXT NOT NULL,
                    trace TEXT NOT NULL,
                    document_draft TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.executemany("INSERT OR IGNORE INTO roles(name) VALUES (?)", [("user",), ("admin",)])

    def bootstrap_admin(self, email: str, password: str = "", password_hash_value: str = "") -> User | None:
        if not email or (not password and not password_hash_value):
            return None
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
        with self.connect() as conn:
            row = conn.execute("SELECT id, email, role, password_hash FROM users WHERE email = ?", (email,)).fetchone()
            if not row or not row["password_hash"]:
                return None
            if not verify_password(password, row["password_hash"]):
                return None
            return User(id=row["id"], email=row["email"], role=row["role"])

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

    def can_access_session(self, session_id: int, user: User) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT owner_user_id FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return False
            return user.role == "admin" or row["owner_user_id"] == user.id

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

    def session_payload(self, session_id: int, user: User) -> dict[str, Any]:
        with self.connect() as conn:
            session = conn.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
        return {
            "session": dict(session) if session else None,
            "messages": self.list_messages(session_id),
            "latest_turn": self.latest_turn_result(session_id),
            "is_admin": user.role == "admin",
        }
