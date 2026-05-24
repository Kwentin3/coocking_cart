from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass


PASSWORD_HASH_PREFIX = "pbkdf2_sha256"


def hash_password(password: str, *, iterations: int = 210_000, salt: str | None = None) -> str:
    salt_value = salt or secrets.token_urlsafe(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_value.encode("utf-8"), iterations)
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"{PASSWORD_HASH_PREFIX}${iterations}${salt_value}${encoded}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        prefix, iterations_raw, salt, expected = stored_hash.split("$", 3)
        if prefix != PASSWORD_HASH_PREFIX:
            return False
        calculated = hash_password(password, iterations=int(iterations_raw), salt=salt).split("$", 3)[3]
        return hmac.compare_digest(calculated, expected)
    except Exception:
        return False


def session_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SignedCookie:
    value: str


def sign_cookie(token: str, secret: str) -> SignedCookie:
    signature = hmac.new(secret.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
    return SignedCookie(f"{token}.{signature}")


def unsign_cookie(cookie_value: str, secret: str) -> str | None:
    if "." not in cookie_value:
        return None
    token, signature = cookie_value.rsplit(".", 1)
    expected = hmac.new(secret.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
    if hmac.compare_digest(signature, expected):
        return token
    return None


def constant_time_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).decode("ascii").rstrip("=")
