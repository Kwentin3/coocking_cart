from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _is_placeholder(value: str | None) -> bool:
    if value is None:
        return False
    stripped = value.strip()
    return stripped.startswith("<") and stripped.endswith(">")


def _is_blank_or_placeholder(value: str | None) -> bool:
    return value is None or value.strip() == "" or _is_placeholder(value)


def _bool_value(value: str | None, default: bool = False) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_value(value: str | None, default: int) -> int:
    try:
        return int(value or default)
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    app_env: str
    app_name: str
    app_base_url: str
    public_domain: str
    demo_mode: bool
    sqlite_db_path: Path
    context_manifest_path: Path
    context_layers_dir: Path
    llm_provider: str
    llm_model: str
    llm_api_key: str
    llm_base_url: str
    llm_timeout_seconds: int
    stt_enabled: bool
    stt_provider: str
    stt_model: str
    stt_api_key: str
    stt_base_url: str
    stt_timeout_seconds: int
    stt_max_audio_seconds: int
    stt_countdown_seconds: int
    stt_max_audio_bytes: int
    enable_context_inspector: bool
    enable_llm_trace: bool
    bootstrap_admin_email: str
    bootstrap_admin_password: str
    bootstrap_admin_password_hash: str
    auth_session_secret: str
    deploy_host: str
    deploy_user: str
    traefik_network_name: str
    traefik_entrypoint: str
    traefik_certresolver: str

    @property
    def llm_ready(self) -> bool:
        return (
            self.llm_provider == "gemini"
            and not _is_blank_or_placeholder(self.llm_model)
            and not _is_blank_or_placeholder(self.llm_api_key)
        )

    @property
    def stt_ready(self) -> bool:
        return (
            self.stt_enabled
            and self.stt_provider == "gemini"
            and not _is_blank_or_placeholder(self.stt_model)
            and not _is_blank_or_placeholder(self.stt_api_key)
        )

    @property
    def auth_ready(self) -> bool:
        return not _is_blank_or_placeholder(self.auth_session_secret)

    @property
    def bootstrap_ready(self) -> bool:
        has_password = not _is_blank_or_placeholder(self.bootstrap_admin_password)
        has_hash = not _is_blank_or_placeholder(self.bootstrap_admin_password_hash)
        return (
            not _is_blank_or_placeholder(self.bootstrap_admin_email)
            and self.auth_ready
            and (has_password ^ has_hash)
        )

    def public_errors(self) -> list[str]:
        errors: list[str] = []
        if not self.auth_ready:
            errors.append("Не настроен секрет пользовательских сессий.")
        if not self.bootstrap_ready:
            errors.append("Bootstrap admin не готов: проверьте env-настройки.")
        if self.llm_provider != "gemini":
            errors.append("Для Demo MVP ожидается LLM_PROVIDER=gemini.")
        if _is_blank_or_placeholder(self.llm_model):
            errors.append("Не настроена модель LLM.")
        if _is_blank_or_placeholder(self.llm_api_key):
            errors.append("Не настроен API key LLM.")
        if self.stt_enabled:
            if self.stt_provider != "gemini":
                errors.append("Для голосового ввода ожидается STT_PROVIDER=gemini.")
            if _is_blank_or_placeholder(self.stt_model):
                errors.append("Не настроена модель STT.")
            if _is_blank_or_placeholder(self.stt_api_key):
                errors.append("Не настроен API key STT.")
        return errors

    def admin_diagnostics(self) -> list[str]:
        diagnostics: list[str] = []
        if _is_blank_or_placeholder(self.auth_session_secret):
            diagnostics.append("AUTH_SESSION_SECRET is missing, blank, or placeholder.")
        if _is_blank_or_placeholder(self.bootstrap_admin_email):
            diagnostics.append("BOOTSTRAP_ADMIN_EMAIL is missing, blank, or placeholder.")
        if (
            not _is_blank_or_placeholder(self.bootstrap_admin_password)
            and not _is_blank_or_placeholder(self.bootstrap_admin_password_hash)
        ):
            diagnostics.append("Both BOOTSTRAP_ADMIN_PASSWORD and BOOTSTRAP_ADMIN_PASSWORD_HASH are configured.")
        if _is_blank_or_placeholder(self.bootstrap_admin_password) and _is_blank_or_placeholder(
            self.bootstrap_admin_password_hash
        ):
            diagnostics.append("Bootstrap password/password hash is missing, blank, or placeholder.")
        if _is_blank_or_placeholder(self.llm_model):
            diagnostics.append("LLM_MODEL is missing, blank, or placeholder.")
        if _is_blank_or_placeholder(self.llm_api_key):
            diagnostics.append("LLM_API_KEY is missing, blank, or placeholder.")
        if self.stt_enabled and self.stt_provider != "gemini":
            diagnostics.append("STT_PROVIDER must be gemini for Demo MVP.")
        if self.stt_enabled and _is_blank_or_placeholder(self.stt_model):
            diagnostics.append("STT_MODEL is missing, blank, or placeholder.")
        if self.stt_enabled and _is_blank_or_placeholder(self.stt_api_key):
            diagnostics.append("STT_API_KEY is missing, blank, or placeholder.")
        return diagnostics


def load_config() -> AppConfig:
    env_file_values = _read_env_file(REPO_ROOT / ".env")
    merged = dict(env_file_values)
    for key, value in os.environ.items():
        if value != "":
            merged[key] = value

    def get(key: str, default: str = "") -> str:
        return merged.get(key, default)

    def repo_path(value: str, default: str) -> Path:
        raw = value or default
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path

    llm_api_key = get("LLM_API_KEY") or get("GEMINI_API_KEY")
    stt_api_key = get("STT_API_KEY") or llm_api_key
    stt_model = get("STT_MODEL") or get("LLM_MODEL", "")

    return AppConfig(
        app_env=get("APP_ENV", "demo"),
        app_name=get("APP_NAME", "coocking-cart"),
        app_base_url=get("APP_BASE_URL", "http://127.0.0.1:8000"),
        public_domain=get("PUBLIC_DOMAIN", ""),
        demo_mode=_bool_value(get("DEMO_MODE"), True),
        sqlite_db_path=repo_path(get("SQLITE_DB_PATH"), "./data/demo.sqlite"),
        context_manifest_path=repo_path(get("CONTEXT_MANIFEST_PATH"), "./docs/mvp/context/context_manifest.yml"),
        context_layers_dir=repo_path(get("CONTEXT_LAYERS_DIR"), "./docs/mvp/context"),
        llm_provider=get("LLM_PROVIDER", "gemini").strip().lower(),
        llm_model=get("LLM_MODEL", ""),
        llm_api_key=llm_api_key,
        llm_base_url=get("LLM_BASE_URL", ""),
        llm_timeout_seconds=_int_value(get("LLM_TIMEOUT_SECONDS"), 60),
        stt_enabled=_bool_value(get("STT_ENABLED"), True),
        stt_provider=(get("STT_PROVIDER") or get("LLM_PROVIDER", "gemini")).strip().lower(),
        stt_model=stt_model,
        stt_api_key=stt_api_key,
        stt_base_url=get("STT_BASE_URL") or get("LLM_BASE_URL", ""),
        stt_timeout_seconds=_int_value(get("STT_TIMEOUT_SECONDS"), 90),
        stt_max_audio_seconds=_int_value(get("STT_MAX_AUDIO_SECONDS"), 180),
        stt_countdown_seconds=_int_value(get("STT_COUNTDOWN_SECONDS"), 15),
        stt_max_audio_bytes=_int_value(get("STT_MAX_AUDIO_BYTES"), 12_000_000),
        enable_context_inspector=_bool_value(get("ENABLE_CONTEXT_INSPECTOR"), True),
        enable_llm_trace=_bool_value(get("ENABLE_LLM_TRACE"), True),
        bootstrap_admin_email=get("BOOTSTRAP_ADMIN_EMAIL", ""),
        bootstrap_admin_password=get("BOOTSTRAP_ADMIN_PASSWORD", ""),
        bootstrap_admin_password_hash=get("BOOTSTRAP_ADMIN_PASSWORD_HASH", ""),
        auth_session_secret=get("AUTH_SESSION_SECRET", ""),
        deploy_host=get("DEPLOY_HOST", ""),
        deploy_user=get("DEPLOY_USER", ""),
        traefik_network_name=get("TRAEFIK_NETWORK_NAME", ""),
        traefik_entrypoint=get("TRAEFIK_ENTRYPOINT", ""),
        traefik_certresolver=get("TRAEFIK_CERTRESOLVER", ""),
    )


def is_blank_or_placeholder(value: str | None) -> bool:
    return _is_blank_or_placeholder(value)
