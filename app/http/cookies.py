from __future__ import annotations

from urllib.parse import urlparse

from ..config import AppConfig


COOKIE_NAME = "cc_session"
LOCAL_COOKIE_HOSTS = {"127.0.0.1", "::1", "localhost"}


def build_session_cookie_header(name: str, value: str, *, max_age: int, secure: bool) -> str:
    header = f"{name}={value}; HttpOnly; SameSite=Lax; Path=/; Max-Age={max_age}"
    if secure:
        header += "; Secure"
    return header


def should_use_secure_session_cookie(config: AppConfig, *, forwarded_proto: str, host_header: str) -> bool:
    mode = config.session_cookie_secure
    if mode == "true":
        return True
    if mode == "false":
        return False
    proto = str(forwarded_proto or "").split(",", 1)[0].strip().lower()
    if proto:
        return proto == "https"
    host = _host_without_port(host_header)
    app_base = urlparse(config.app_base_url)
    return app_base.scheme == "https" and host not in LOCAL_COOKIE_HOSTS


def _host_without_port(host_header: str) -> str:
    raw_host = str(host_header or "").split(",", 1)[0].strip().lower()
    if raw_host.startswith("["):
        end = raw_host.find("]")
        if end >= 0:
            return raw_host[1:end]
        return raw_host.strip("[]")
    return raw_host.split(":", 1)[0]
