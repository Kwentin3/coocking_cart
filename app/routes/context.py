from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

from ..storage import User


@dataclass(frozen=True)
class RouteContext:
    """Small route boundary over BaseHTTPRequestHandler-owned edge helpers."""

    handler: Any
    path: str

    @property
    def state(self) -> Any:
        return self.handler.state

    def json(
        self,
        payload: dict[str, Any],
        status: HTTPStatus = HTTPStatus.OK,
        headers: list[tuple[str, str]] | None = None,
        body: bool = True,
    ) -> None:
        self.handler._json(payload, status, headers=headers, body=body)

    def read_json(self) -> dict[str, Any]:
        return self.handler._read_json()

    def discard_request_body(self) -> None:
        self.handler._discard_request_body()

    def read_audio_upload(self) -> dict[str, Any]:
        return self.handler._read_audio_upload()

    def current_user(self) -> User | None:
        return self.handler._current_user()

    def current_token(self) -> str | None:
        return self.handler._current_token()

    def require_user(self) -> User | None:
        return self.handler._require_user()

    def require_admin(self) -> User | None:
        return self.handler._require_admin()

    def issue_session(self, user: User) -> None:
        self.handler._issue_session(user)

    def clear_cookie_header(self) -> tuple[str, str]:
        return self.handler._clear_cookie_header()

    def user_payload(self, user: User | None) -> dict[str, Any] | None:
        return self.handler._user_payload(user)

    def session_id_from_path(self, suffix: str = "") -> int | None:
        return self.handler._session_id_from_path(self.path, suffix=suffix)

    def admin_user_id_from_path(self) -> int | None:
        return self.handler._admin_user_id_from_path(self.path)

    def voice_input_config(self) -> dict[str, Any]:
        return self.handler._voice_input_config()

    def prepare_live_voice_token_response(
        self,
        user: User,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], HTTPStatus]:
        return self.handler._prepare_live_voice_token_response(user, payload)
