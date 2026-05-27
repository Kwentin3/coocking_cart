from __future__ import annotations

from http import HTTPStatus

from .context import RouteContext


def post_transcribe(ctx: RouteContext) -> None:
    user = ctx.require_user()
    if not user:
        return
    audio = ctx.read_audio_upload()
    if not audio["ok"]:
        ctx.json({"ok": False, "error": audio["error"]}, audio["status"])
        return
    payload = ctx.state.runtime.transcribe_audio(
        user,
        audio["audio_bytes"],
        audio["mime_type"],
        audio["duration_ms"],
    )
    status = HTTPStatus(payload.pop("status", 200))
    ctx.json(payload, status)


def post_live_voice_token(ctx: RouteContext) -> None:
    ctx.discard_request_body()
    user = ctx.require_user()
    if not user:
        return
    payload = ctx.state.runtime.create_live_voice_token(user)
    status = HTTPStatus(payload.pop("status", 200))
    if status == HTTPStatus.OK and payload.get("ok"):
        payload, status = ctx.prepare_live_voice_token_response(user, payload)
    ctx.json(payload, status)
