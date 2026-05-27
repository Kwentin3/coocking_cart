from __future__ import annotations

import argparse
import json
import mimetypes
import secrets
import threading
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .config import REPO_ROOT, AppConfig, load_config
from .live_voice_proxy import (
    connect_gemini_live_websocket,
    is_websocket_upgrade,
    relay_websocket,
    websocket_accept_value,
)
from .runtime import DemoRuntime
from .security import session_token, sign_cookie, unsign_cookie
from .storage import Storage, User


COOKIE_NAME = "cc_session"
STATIC_DIR = REPO_ROOT / "app" / "static"
INDEX_PATH = REPO_ROOT / "app" / "templates" / "index.html"


def build_session_cookie_header(name: str, value: str, *, max_age: int, secure: bool) -> str:
    header = f"{name}={value}; HttpOnly; SameSite=Lax; Path=/; Max-Age={max_age}"
    if secure:
        header += "; Secure"
    return header


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
        self.live_voice_sessions: dict[str, dict[str, Any]] = {}
        self.live_voice_sessions_lock = threading.Lock()


class DemoMvpHandler(BaseHTTPRequestHandler):
    state: AppState
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/live-voice/ws/"):
            self._handle_live_voice_websocket(parsed.path)
            return
        if parsed.path == "/":
            self._send_file(INDEX_PATH, "text/html; charset=utf-8")
            return
        if parsed.path.startswith("/static/"):
            self._serve_static(parsed.path)
            return
        if parsed.path == "/api/config":
            self._json({"ok": True, "config_errors": self.state.config.public_errors(), "voice_input": self._voice_input_config()})
            return
        if parsed.path == "/api/me":
            user = self._current_user()
            self._json({
                "ok": True,
                "user": self._user_payload(user),
                "config_errors": self.state.config.public_errors(),
                "voice_input": self._voice_input_config(),
            })
            return
        if parsed.path == "/api/admin/users":
            admin = self._require_admin()
            if not admin:
                return
            self._json({"ok": True, "users": self.state.storage.list_users(current_user_id=admin.id)})
            return
        if parsed.path == "/api/admin/dashboard":
            admin = self._require_admin()
            if not admin:
                return
            self._json({"ok": True, "dashboard": self.state.storage.admin_dashboard()})
            return
        if parsed.path == "/api/admin/context":
            admin = self._require_admin()
            if not admin:
                return
            self._json(self.state.runtime.admin_context_payload(admin))
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
            self._json({"ok": True, "config_errors": self.state.config.public_errors(), "voice_input": self._voice_input_config()}, body=False)
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
            self._discard_request_body()
            token = self._current_token()
            if token:
                self.state.storage.delete_auth_session(token)
            self._json({"ok": True}, headers=[self._clear_cookie_header()])
            return
        if parsed.path == "/api/transcribe":
            user = self._require_user()
            if not user:
                return
            audio = self._read_audio_upload()
            if not audio["ok"]:
                self._json({"ok": False, "error": audio["error"]}, audio["status"])
                return
            payload = self.state.runtime.transcribe_audio(
                user,
                audio["audio_bytes"],
                audio["mime_type"],
                audio["duration_ms"],
            )
            status = HTTPStatus(payload.pop("status", 200))
            self._json(payload, status)
            return
        if parsed.path == "/api/live-voice/token":
            self._discard_request_body()
            user = self._require_user()
            if not user:
                return
            payload = self.state.runtime.create_live_voice_token(user)
            status = HTTPStatus(payload.pop("status", 200))
            if status == HTTPStatus.OK and payload.get("ok"):
                payload, status = self._prepare_live_voice_token_response(user, payload)
            self._json(payload, status)
            return
        if parsed.path == "/api/admin/users":
            admin = self._require_admin()
            if not admin:
                return
            body = self._read_json()
            try:
                user = self.state.storage.create_user(
                    email=str(body.get("email", "")),
                    password=str(body.get("password", "")),
                    role=str(body.get("role", "user")),
                )
            except ValueError as exc:
                self._json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            user["is_current"] = user["id"] == admin.id
            self._json({"ok": True, "user": user}, HTTPStatus.CREATED)
            return
        if parsed.path == "/api/sessions":
            user = self._require_user()
            if not user:
                return
            body = self._read_json()
            session_id = self.state.storage.create_chat_session(user.id, str(body.get("title") or "Новая сессия"))
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

    def do_PATCH(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/admin/users/"):
            admin = self._require_admin()
            if not admin:
                return
            user_id = self._admin_user_id_from_path(parsed.path)
            if user_id is None:
                return
            body = self._read_json()
            try:
                user = self.state.storage.update_user(
                    user_id,
                    email=str(body["email"]) if "email" in body else None,
                    role=str(body["role"]) if "role" in body else None,
                    password=str(body["password"]) if "password" in body else None,
                    current_admin_id=admin.id,
                )
            except ValueError as exc:
                self._json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._json({"ok": True, "user": user})
            return
        if parsed.path.startswith("/api/sessions/"):
            user = self._require_user()
            if not user:
                return
            session_id = self._session_id_from_path(parsed.path)
            if session_id is None:
                return
            body = self._read_json()
            try:
                session = self.state.storage.update_chat_session(session_id, user, str(body.get("title", "")))
            except PermissionError as exc:
                self._json({"ok": False, "error": str(exc)}, HTTPStatus.FORBIDDEN)
                return
            except ValueError as exc:
                self._json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._json({"ok": True, "session": session})
            return
        self._json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/admin/users/"):
            admin = self._require_admin()
            if not admin:
                return
            user_id = self._admin_user_id_from_path(parsed.path)
            if user_id is None:
                return
            try:
                self.state.storage.delete_user(user_id, current_admin_id=admin.id)
            except ValueError as exc:
                self._json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._json({"ok": True})
            return
        if parsed.path.startswith("/api/sessions/"):
            user = self._require_user()
            if not user:
                return
            session_id = self._session_id_from_path(parsed.path)
            if session_id is None:
                return
            try:
                self.state.storage.delete_chat_session(session_id, user)
            except PermissionError as exc:
                self._json({"ok": False, "error": str(exc)}, HTTPStatus.FORBIDDEN)
                return
            except ValueError as exc:
                self._json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._json({"ok": True})
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

    def _discard_request_body(self) -> None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length > 0:
            self.rfile.read(length)

    def _read_audio_upload(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return {"ok": False, "error": "Аудио пустое.", "status": HTTPStatus.BAD_REQUEST}
        if length > self.state.config.stt_max_audio_bytes:
            return {"ok": False, "error": "Аудиофайл слишком большой.", "status": HTTPStatus.REQUEST_ENTITY_TOO_LARGE}
        try:
            duration_ms = int(self.headers.get("X-Audio-Duration-Ms") or 0)
        except ValueError:
            duration_ms = 0
        if duration_ms <= 0:
            return {"ok": False, "error": "Длительность аудио не указана.", "status": HTTPStatus.BAD_REQUEST}
        if duration_ms > self.state.config.stt_max_audio_seconds * 1000:
            return {"ok": False, "error": "Запись слишком длинная.", "status": HTTPStatus.REQUEST_ENTITY_TOO_LARGE}
        mime_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if not mime_type:
            return {"ok": False, "error": "Тип аудио не указан.", "status": HTTPStatus.UNSUPPORTED_MEDIA_TYPE}
        return {
            "ok": True,
            "audio_bytes": self.rfile.read(length),
            "mime_type": mime_type,
            "duration_ms": duration_ms,
        }

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

    def _prepare_live_voice_token_response(
        self,
        user: User,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], HTTPStatus]:
        transport = self.state.config.live_voice_transport
        if transport == "direct_client":
            payload["transport"] = "direct_client"
            return payload, HTTPStatus.OK
        if transport != "server_proxy":
            return {
                "ok": False,
                "error": "LIVE_VOICE_TRANSPORT должен быть direct_client или server_proxy.",
            }, HTTPStatus.SERVICE_UNAVAILABLE
        upstream_url = str(payload.get("websocket_url") or "")
        if not upstream_url:
            return {
                "ok": False,
                "error": "Не удалось подготовить серверный Live Voice transport.",
            }, HTTPStatus.BAD_GATEWAY

        self._purge_expired_live_voice_sessions()
        session_id = secrets.token_urlsafe(24)
        expires_at = time.time() + max(30, self.state.config.live_voice_new_session_seconds)
        with self.state.live_voice_sessions_lock:
            self.state.live_voice_sessions[session_id] = {
                "user_id": user.id,
                "websocket_url": upstream_url,
                "expires_at": expires_at,
            }

        payload.pop("token", None)
        payload["transport"] = "server_proxy"
        payload["websocket_url"] = self._live_voice_proxy_url(session_id)
        return payload, HTTPStatus.OK

    def _handle_live_voice_websocket(self, path: str) -> None:
        if self.state.config.live_voice_transport != "server_proxy":
            self._json({"ok": False, "error": "Live Voice server proxy выключен."}, HTTPStatus.NOT_FOUND)
            return
        user = self._require_user()
        if not user:
            return
        if not is_websocket_upgrade(self.headers):
            self._json({"ok": False, "error": "Ожидался WebSocket Upgrade."}, HTTPStatus.BAD_REQUEST)
            return
        session_id = path.removeprefix("/api/live-voice/ws/").strip("/")
        session = self._take_live_voice_session(session_id, user)
        if session is None:
            return
        try:
            upstream = connect_gemini_live_websocket(str(session["websocket_url"]), self.state.config)
        except Exception as exc:
            payload: dict[str, Any] = {
                "ok": False,
                "error": "Не удалось открыть серверный Live Voice transport.",
            }
            if user.role == "admin":
                payload["admin_hint"] = f"{type(exc).__name__}: {exc}"
            self._json(payload, HTTPStatus.BAD_GATEWAY)
            return

        self._accept_websocket()
        relay_websocket(
            browser_reader=self.rfile,
            browser_writer=self.wfile,
            browser_socket=self.connection,
            upstream=upstream,
        )

    def _take_live_voice_session(self, session_id: str, user: User) -> dict[str, Any] | None:
        self._purge_expired_live_voice_sessions()
        with self.state.live_voice_sessions_lock:
            session = self.state.live_voice_sessions.pop(session_id, None)
        if not session:
            self._json({"ok": False, "error": "Live Voice session не найдена или истекла."}, HTTPStatus.NOT_FOUND)
            return None
        if int(session.get("user_id", 0)) != user.id:
            self._json({"ok": False, "error": "Нет доступа к Live Voice session."}, HTTPStatus.FORBIDDEN)
            return None
        if float(session.get("expires_at", 0)) < time.time():
            self._json({"ok": False, "error": "Live Voice session истекла."}, HTTPStatus.GONE)
            return None
        return session

    def _purge_expired_live_voice_sessions(self) -> None:
        now = time.time()
        with self.state.live_voice_sessions_lock:
            expired = [
                session_id
                for session_id, session in self.state.live_voice_sessions.items()
                if float(session.get("expires_at", 0)) < now
            ]
            for session_id in expired:
                self.state.live_voice_sessions.pop(session_id, None)

    def _accept_websocket(self) -> None:
        key = str(self.headers.get("Sec-WebSocket-Key", "")).strip()
        self.send_response(HTTPStatus.SWITCHING_PROTOCOLS)
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", websocket_accept_value(key))
        self.end_headers()
        self.close_connection = True

    def _live_voice_proxy_url(self, session_id: str) -> str:
        forwarded_proto = str(self.headers.get("X-Forwarded-Proto", "")).split(",", 1)[0].strip().lower()
        forwarded_host = str(self.headers.get("X-Forwarded-Host", "")).split(",", 1)[0].strip()
        app_base = urlparse(self.state.config.app_base_url)
        if forwarded_proto:
            scheme = "wss" if forwarded_proto == "https" else "ws"
        elif app_base.scheme == "https":
            scheme = "wss"
        else:
            scheme = "ws"
        host = forwarded_host or self.headers.get("Host") or app_base.netloc
        return f"{scheme}://{host}/api/live-voice/ws/{session_id}"

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

    def _require_admin(self) -> User | None:
        user = self._require_user()
        if not user:
            return None
        # Sticky MVP boundary: admin user CRUD is demo tooling, not client-declared RBAC.
        if user.role != "admin":
            self._json({"ok": False, "error": "Требуются права admin."}, HTTPStatus.FORBIDDEN)
            return None
        return user

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

    def _admin_user_id_from_path(self, path: str) -> int | None:
        value = path.removeprefix("/api/admin/users/").strip("/")
        try:
            return int(value)
        except ValueError:
            self._json({"ok": False, "error": "Некорректный user id."}, HTTPStatus.BAD_REQUEST)
            return None

    def _cookie_header(self, value: str) -> tuple[str, str]:
        return (
            "Set-Cookie",
            build_session_cookie_header(COOKIE_NAME, value, max_age=604800, secure=self._use_secure_session_cookie()),
        )

    def _clear_cookie_header(self) -> tuple[str, str]:
        return (
            "Set-Cookie",
            build_session_cookie_header(COOKIE_NAME, "", max_age=0, secure=self._use_secure_session_cookie()),
        )

    def _use_secure_session_cookie(self) -> bool:
        mode = self.state.config.session_cookie_secure
        if mode == "true":
            return True
        if mode == "false":
            return False
        forwarded_proto = str(self.headers.get("X-Forwarded-Proto", "")).split(",", 1)[0].strip().lower()
        if forwarded_proto:
            return forwarded_proto == "https"
        host = str(self.headers.get("Host", "")).split(":", 1)[0].strip().lower()
        app_base = urlparse(self.state.config.app_base_url)
        return app_base.scheme == "https" and host not in {"127.0.0.1", "::1", "localhost"}

    def _voice_input_config(self) -> dict[str, Any]:
        return {
            "enabled": self.state.config.stt_enabled,
            "streaming_enabled": self.state.config.live_voice_ready,
            "streaming_model": self.state.config.live_voice_model if self.state.config.live_voice_ready else "",
            "streaming_sample_rate": self.state.config.live_voice_input_sample_rate,
            "streaming_transport": self.state.config.live_voice_transport,
            "batch_enabled": self.state.config.stt_enabled,
            "max_audio_seconds": self.state.config.stt_max_audio_seconds,
            "countdown_seconds": self.state.config.stt_countdown_seconds,
            "max_audio_bytes": self.state.config.stt_max_audio_bytes,
        }


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
