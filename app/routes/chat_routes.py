from __future__ import annotations

from http import HTTPStatus

from .context import RouteContext


def list_sessions(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    ctx.json({"ok": True, "sessions": ctx.state.storage.list_chat_sessions(user)})


def get_inspector(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    session_id = ctx.session_id_from_path(suffix="/inspector")
    if session_id is None:
        return
    ctx.json(ctx.state.runtime.context_inspector_payload(session_id, user))


def get_session(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    session_id = ctx.session_id_from_path()
    if session_id is None:
        return
    if not ctx.state.storage.can_access_session(session_id, user):
        ctx.json({"ok": False, "error": "Нет доступа к сессии."}, HTTPStatus.FORBIDDEN)
        return
    payload = ctx.state.storage.session_payload(session_id, user)
    if user.role != "admin" and payload.get("latest_turn"):
        payload["latest_turn"] = {
            key: value
            for key, value in payload["latest_turn"].items()
            if key != "trace"
        }
    ctx.json({"ok": True, **payload})


def create_session(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    body = ctx.read_json()
    session_id = ctx.state.storage.create_chat_session(user.id, str(body.get("title") or "Новая сессия"))
    ctx.json({"ok": True, "session_id": session_id})


def post_message(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    session_id = ctx.session_id_from_path(suffix="/messages")
    if session_id is None:
        return
    body = ctx.read_json()
    message = str(body.get("message") or "").strip()
    if not message:
        ctx.json({"ok": False, "error": "Сообщение пустое."}, HTTPStatus.BAD_REQUEST)
        return
    ctx.json(ctx.state.runtime.process_user_message(session_id, user, message))


def patch_session(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    session_id = ctx.session_id_from_path()
    if session_id is None:
        return
    body = ctx.read_json()
    try:
        session = ctx.state.storage.update_chat_session(session_id, user, str(body.get("title", "")))
    except PermissionError as exc:
        ctx.json({"ok": False, "error": str(exc)}, HTTPStatus.FORBIDDEN)
        return
    except ValueError as exc:
        ctx.json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    ctx.json({"ok": True, "session": session})


def delete_session(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    session_id = ctx.session_id_from_path()
    if session_id is None:
        return
    try:
        ctx.state.storage.delete_chat_session(session_id, user)
    except PermissionError as exc:
        ctx.json({"ok": False, "error": str(exc)}, HTTPStatus.FORBIDDEN)
        return
    except ValueError as exc:
        ctx.json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    ctx.json({"ok": True})
