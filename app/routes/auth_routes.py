from __future__ import annotations

from http import HTTPStatus

from .context import RouteContext


def post_login(ctx: RouteContext) -> None:
    body = ctx.read_json()
    user = ctx.state.storage.authenticate(str(body.get("email", "")), str(body.get("password", "")))
    if not user:
        ctx.json({"ok": False, "error": "Неверный email или пароль."}, HTTPStatus.UNAUTHORIZED)
        return
    ctx.issue_session(user)


def post_demo_login(ctx: RouteContext) -> None:
    ctx.discard_request_body()
    if not ctx.state.config.demo_mode:
        ctx.json({"ok": False, "error": "Demo mode выключен."}, HTTPStatus.FORBIDDEN)
        return
    user = ctx.state.storage.ensure_demo_user()
    ctx.issue_session(user)


def post_logout(ctx: RouteContext) -> None:
    ctx.discard_request_body()
    token = ctx.current_token()
    if token:
        ctx.state.storage.delete_auth_session(token)
    ctx.json({"ok": True}, headers=[ctx.clear_cookie_header()])
