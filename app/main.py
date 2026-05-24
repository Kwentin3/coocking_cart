from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .config import REPO_ROOT, AppConfig, load_config
from .runtime import DemoRuntime
from .security import session_token, sign_cookie, unsign_cookie
from .storage import Storage, User


COOKIE_NAME = "cc_session"
STATIC_DIR = REPO_ROOT / "app" / "static"
INDEX_PATH = REPO_ROOT / "app" / "templates" / "index.html"


class AppState:
    def __init__(self, config: AppConfig):
        self.config = config
        self.storage = Storage(config.sqlite_db_path)
        if config.bootstrap_ready:
            self.storage.bootstrap_admin(
                config.bootstrap_admin_email,
                password=config.bootstrap_admin_password,
                password_hash_value=config.bootstrap_admin_password_hash,
            )
        if config.demo_mode:
            self.storage.ensure_demo_user()
        self.runtime = DemoRuntime(config, self.storage)


class DemoMvpHandler(BaseHTTPRequestHandler):
    state: AppState

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(INDEX_PATH, "text/html; charset=utf-8")
            return
        if parsed.path.startswith("/static/"):
            self._serve_static(parsed.path)
            return
        if parsed.path == "/api/config":
            self._json({"ok": True, "config_errors": self.state.config.public_errors()})
            return
        if parsed.path == "/api/me":
            user = self._current_user()
            self._json({"ok": True, "user": self._user_payload(user), "config_errors": self.state.config.public_errors()})
            return
        if parsed.path == "/api/sessions":
            user = self._require_user()
            if not user:
                return
            self._json({"ok": True, "sessions": self.state.storage.list_chat_sessions(user)})
            return
        if parsed.path.startswith("/api/sessions/") and parsed.path.endswith("/inspector"):
            user = self._require_user()
            if not user:
                return
            session_id = self._session_id_from_path(parsed.path, suffix="/inspector")
            if session_id is None:
                return
            self._json(self.state.runtime.context_inspector_payload(session_id, user))
            return
        if parsed.path.startswith("/api/sessions/"):
            user = self._require_user()
            if not user:
                return
            session_id = self._session_id_from_path(parsed.path)
            if session_id is None:
                return
            if not self.state.storage.can_access_session(session_id, user):
                self._json({"ok": False, "error": "Нет доступа к сессии."}, HTTPStatus.FORBIDDEN)
                return
            payload = self.state.storage.session_payload(session_id, user)
            if user.role != "admin" and payload.get("latest_turn"):
                payload["latest_turn"] = {
                    key: value
                    for key, value in payload["latest_turn"].items()
                    if key != "trace"
                }
            self._json({"ok": True, **payload})
            return
        self._json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(INDEX_PATH, "text/html; charset=utf-8", body=False)
            return
        if parsed.path.startswith("/static/"):
            self._serve_static(parsed.path, body=False)
            return
        if parsed.path == "/api/config":
            self._json({"ok": True, "config_errors": self.state.config.public_errors()}, body=False)
            return
        self._json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND, body=False)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/login":
            body = self._read_json()
            user = self.state.storage.authenticate(str(body.get("email", "")), str(body.get("password", "")))
            if not user:
                self._json({"ok": False, "error": "Неверный email или пароль."}, HTTPStatus.UNAUTHORIZED)
                return
            self._issue_session(user)
            return
        if parsed.path == "/api/demo-login":
            if not self.state.config.demo_mode:
                self._json({"ok": False, "error": "Demo mode выключен."}, HTTPStatus.FORBIDDEN)
                return
            user = self.state.storage.ensure_demo_user()
            self._issue_session(user)
            return
        if parsed.path == "/api/logout":
            token = self._current_token()
            if token:
                self.state.storage.delete_auth_session(token)
            self._json({"ok": True}, headers=[self._clear_cookie_header()])
            return
        if parsed.path == "/api/sessions":
            user = self._require_user()
            if not user:
                return
            body = self._read_json()
            title = str(body.get("title") or "Новая сессия").strip()[:120] or "Новая сессия"
            session_id = self.state.storage.create_chat_session(user.id, title)
            self._json({"ok": True, "session_id": session_id})
            return
        if parsed.path.startswith("/api/sessions/") and parsed.path.endswith("/messages"):
            user = self._require_user()
            if not user:
                return
            session_id = self._session_id_from_path(parsed.path, suffix="/messages")
            if session_id is None:
                return
            body = self._read_json()
            message = str(body.get("message") or "").strip()
            if not message:
                self._json({"ok": False, "error": "Сообщение пустое."}, HTTPStatus.BAD_REQUEST)
                return
            self._json(self.state.runtime.process_user_message(session_id, user, message))
            return
        self._json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)

    def _serve_static(self, path: str, *, body: bool = True) -> None:
        parts = [part for part in path.removeprefix("/static/").split("/") if part]
        file_path = (STATIC_DIR / Path(*parts)).resolve()
        if STATIC_DIR.resolve() not in file_path.parents and file_path != STATIC_DIR.resolve():
            self._json({"ok": False, "error": "Invalid static path."}, HTTPStatus.BAD_REQUEST)
            return
        if not file_path.exists() or not file_path.is_file():
            self._json({"ok": False, "error": "Static file not found."}, HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "text/javascript"}:
            content_type += "; charset=utf-8"
        self._send_file(file_path, content_type, body=body)

    def _send_file(self, path: Path, content_type: str, *, body: bool = True) -> None:
        try:
            data = path.read_bytes()
        except OSError:
            self._json({"ok": False, "error": "File not found."}, HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if body:
            self.wfile.write(data)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _json(
        self,
        payload: dict[str, Any],
        status: HTTPStatus = HTTPStatus.OK,
        headers: list[tuple[str, str]] | None = None,
        body: bool = True,
    ) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        for key, value in headers or []:
            self.send_header(key, value)
        self.end_headers()
        if body:
            self.wfile.write(data)

    def _current_token(self) -> str | None:
        if not self.state.config.auth_ready:
            return None
        raw_cookie = self.headers.get("Cookie", "")
        cookie = SimpleCookie(raw_cookie)
        morsel = cookie.get(COOKIE_NAME)
        if not morsel:
            return None
        return unsign_cookie(morsel.value, self.state.config.auth_session_secret)

    def _current_user(self) -> User | None:
        token = self._current_token()
        if not token:
            return None
        return self.state.storage.user_for_token(token)

    def _require_user(self) -> User | None:
        user = self._current_user()
        if user:
            return user
        self._json({"ok": False, "error": "Требуется вход."}, HTTPStatus.UNAUTHORIZED)
        return None

    def _issue_session(self, user: User) -> None:
        if not self.state.config.auth_ready:
            self._json({"ok": False, "error": "Авторизация не настроена."}, HTTPStatus.SERVICE_UNAVAILABLE)
            return
        token = session_token()
        self.state.storage.create_auth_session(token, user.id)
        signed = sign_cookie(token, self.state.config.auth_session_secret).value
        self._json({"ok": True, "user": self._user_payload(user)}, headers=[self._cookie_header(signed)])

    @staticmethod
    def _user_payload(user: User | None) -> dict[str, Any] | None:
        if not user:
            return None
        return {"id": user.id, "email": user.email, "role": user.role, "is_admin": user.role == "admin"}

    def _session_id_from_path(self, path: str, suffix: str = "") -> int | None:
        value = path.removeprefix("/api/sessions/")
        if suffix:
            value = value.removesuffix(suffix)
        value = value.strip("/")
        try:
            return int(value)
        except ValueError:
            self._json({"ok": False, "error": "Некорректный session id."}, HTTPStatus.BAD_REQUEST)
            return None

    @staticmethod
    def _cookie_header(value: str) -> tuple[str, str]:
        return (
            "Set-Cookie",
            f"{COOKIE_NAME}={value}; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800",
        )

    @staticmethod
    def _clear_cookie_header() -> tuple[str, str]:
        return ("Set-Cookie", f"{COOKIE_NAME}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")


def run(host: str, port: int) -> None:
    config = load_config()
    state = AppState(config)
    DemoMvpHandler.state = state
    server = ThreadingHTTPServer((host, port), DemoMvpHandler)
    print(f"Demo MVP server: http://{host}:{port}")
    print(f"SQLite: {config.sqlite_db_path}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Demo MVP server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    run(args.host, args.port)


if __name__ == "__main__":
    main()
