from __future__ import annotations

from http import HTTPStatus

from .context import RouteContext


def get_users(ctx: RouteContext) -> None:
    admin = ctx.require_admin()
    if not admin:
        return
    ctx.json({"ok": True, "users": ctx.state.storage.list_users(current_user_id=admin.id)})


def get_dashboard(ctx: RouteContext) -> None:
    admin = ctx.require_admin()
    if not admin:
        return
    ctx.json({"ok": True, "dashboard": ctx.state.storage.admin_dashboard()})


def get_context(ctx: RouteContext) -> None:
    admin = ctx.require_admin()
    if not admin:
        return
    ctx.json(ctx.state.runtime.admin_context_payload(admin))


def post_user(ctx: RouteContext) -> None:
    admin = ctx.require_admin()
    if not admin:
        return
    body = ctx.read_json()
    try:
        user = ctx.state.storage.create_user(
            email=str(body.get("email", "")),
            password=str(body.get("password", "")),
            role=str(body.get("role", "user")),
        )
    except ValueError as exc:
        ctx.json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    user["is_current"] = user["id"] == admin.id
    ctx.json({"ok": True, "user": user}, HTTPStatus.CREATED)


def patch_user(ctx: RouteContext) -> None:
    admin = ctx.require_admin()
    if not admin:
        return
    user_id = ctx.admin_user_id_from_path()
    if user_id is None:
        return
    body = ctx.read_json()
    try:
        user = ctx.state.storage.update_user(
            user_id,
            email=str(body["email"]) if "email" in body else None,
            role=str(body["role"]) if "role" in body else None,
            password=str(body["password"]) if "password" in body else None,
            current_admin_id=admin.id,
        )
    except ValueError as exc:
        ctx.json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    ctx.json({"ok": True, "user": user})


def delete_user(ctx: RouteContext) -> None:
    admin = ctx.require_admin()
    if not admin:
        return
    user_id = ctx.admin_user_id_from_path()
    if user_id is None:
        return
    try:
        ctx.state.storage.delete_user(user_id, current_admin_id=admin.id)
    except ValueError as exc:
        ctx.json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return
    ctx.json({"ok": True})
