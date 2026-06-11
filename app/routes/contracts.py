from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteContract:
    method: str
    path: str
    domain: str
    guard: str
    handler: str


# These are internal route paths after DemoMvpHandler strips APP_BASE_PATH.
# Public deployments may expose them under a prefix such as /mvp/api/...
ROUTE_DOMAIN_CONTRACTS: tuple[RouteContract, ...] = (
    RouteContract("GET", "/api/config", "config", "public", "config_routes.get_config"),
    RouteContract("HEAD", "/api/config", "config", "public", "config_routes.get_config"),
    RouteContract("GET", "/api/me", "auth", "public", "config_routes.get_me"),
    RouteContract("POST", "/api/login", "auth", "public", "auth_routes.post_login"),
    RouteContract("POST", "/api/demo-login", "auth", "public", "auth_routes.post_demo_login"),
    RouteContract("POST", "/api/logout", "auth", "public", "auth_routes.post_logout"),
    RouteContract("GET", "/api/admin/users", "admin", "admin", "admin_routes.get_users"),
    RouteContract("POST", "/api/admin/users", "admin", "admin", "admin_routes.post_user"),
    RouteContract("PATCH", "/api/admin/users/{user_id}", "admin", "admin", "admin_routes.patch_user"),
    RouteContract("DELETE", "/api/admin/users/{user_id}", "admin", "admin", "admin_routes.delete_user"),
    RouteContract("GET", "/api/admin/dashboard", "admin", "admin", "admin_routes.get_dashboard"),
    RouteContract("GET", "/api/admin/context", "admin", "admin", "admin_routes.get_context"),
    RouteContract("GET", "/api/sessions", "chat", "user", "chat_routes.list_sessions"),
    RouteContract("POST", "/api/sessions", "chat", "user", "chat_routes.create_session"),
    RouteContract("GET", "/api/sessions/{session_id}", "chat", "user", "chat_routes.get_session"),
    RouteContract("PATCH", "/api/sessions/{session_id}", "chat", "user", "chat_routes.patch_session"),
    RouteContract("DELETE", "/api/sessions/{session_id}", "chat", "user", "chat_routes.delete_session"),
    RouteContract("POST", "/api/sessions/{session_id}/messages", "chat", "user", "chat_routes.post_message"),
    RouteContract("GET", "/api/sessions/{session_id}/inspector", "context", "user", "chat_routes.get_inspector"),
    RouteContract("POST", "/api/transcribe", "voice", "user", "voice_routes.post_transcribe"),
    RouteContract("POST", "/api/live-voice/token", "voice", "user", "voice_routes.post_live_voice_token"),
    RouteContract("GET", "/api/live-voice/ws/{session_id}", "voice", "user", "DemoMvpHandler._handle_live_voice_websocket"),
)
