from __future__ import annotations

from typing import Any

from .context import RouteContext


def public_config_payload(ctx: RouteContext) -> dict[str, Any]:
    return {
        "ok": True,
        "config_errors": ctx.state.config.public_errors(),
        "voice_input": ctx.voice_input_config(),
    }


def get_config(ctx: RouteContext, *, body: bool = True) -> None:
    ctx.json(public_config_payload(ctx), body=body)


def get_me(ctx: RouteContext) -> None:
    user = ctx.current_user()
    ctx.json(
        {
            "ok": True,
            "user": ctx.user_payload(user),
            "config_errors": ctx.state.config.public_errors(),
            "voice_input": ctx.voice_input_config(),
        }
    )
