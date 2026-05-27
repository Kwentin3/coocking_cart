from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import AppConfig, is_blank_or_placeholder


FACTORY_REQUIRED = "LIVE_VOICE_PROVIDER_CALLS_MUST_USE_make_live_voice_adapter"
FORBIDDEN = "DO_NOT_CALL_GEMINI_LIVE_TOKEN_ENDPOINT_FROM_ROUTES_OR_UI"

# Sticky integration boundary: routes/runtime request Live API tokens only
# through make_live_voice_adapter. The browser never receives the Gemini API key;
# in direct_client mode it receives an ephemeral token, and in server_proxy mode
# it receives only our backend WebSocket URL.

LIVE_VOICE_TRANSCRIPTION_INSTRUCTION = """\
Транскрибируй русскую речь пользователя для черновика сообщения в чат.
Не отвечай на содержание, не суммаризируй и не отправляй сообщение.
Сохраняй числа, граммы, килограммы, проценты, температуры, время и единицы измерения максимально точно.
Термины предметной области: ТК, ТТК, брутто, нетто, выход, БЖУ, ХАССП, СанПиН, iiko, r_keeper, StoreHouse, 1С.
Если фрагмент неразборчив, пометь его как [неразборчиво].
"""


@dataclass(frozen=True)
class LiveVoiceTokenResult:
    ok: bool
    provider: str
    model: str
    timestamp: str
    token: str = ""
    websocket_url: str = ""
    setup: dict[str, Any] | None = None
    expires_at: str = ""
    new_session_expires_at: str = ""
    error: str | None = None
    admin_hint: str | None = None
    metadata: dict[str, Any] | None = None


class LiveVoiceAdapter:
    def create_token(self) -> LiveVoiceTokenResult:
        raise NotImplementedError


class GeminiLiveVoiceAdapter(LiveVoiceAdapter):
    def __init__(self, config: AppConfig):
        self.config = config

    def create_token(self) -> LiveVoiceTokenResult:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if self.config.live_voice_provider != "gemini":
            return self._config_error(
                "Live Voice provider не поддерживается.",
                "LIVE_VOICE_PROVIDER must be gemini.",
                timestamp,
            )
        if is_blank_or_placeholder(self.config.live_voice_model):
            return self._config_error(
                "Live Voice model не настроена.",
                "LIVE_VOICE_MODEL is missing, blank, or placeholder.",
                timestamp,
            )
        if is_blank_or_placeholder(self.config.live_voice_api_key):
            return self._config_error(
                "Live Voice API key не настроен.",
                "LIVE_VOICE_API_KEY is missing, blank, or placeholder.",
                timestamp,
            )

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=max(60, self.config.live_voice_token_ttl_seconds))
        new_session_expires_at = now + timedelta(seconds=max(30, self.config.live_voice_new_session_seconds))
        setup = live_voice_setup(self.config)
        payload = {
            "uses": 1,
            "expireTime": _format_google_timestamp(expires_at),
            "newSessionExpireTime": _format_google_timestamp(new_session_expires_at),
            "bidiGenerateContentSetup": setup,
        }
        endpoint = f"{_rest_base_url(self.config)}/v1alpha/auth_tokens"
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.config.live_voice_api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.live_voice_timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw_error = exc.read().decode("utf-8", errors="replace")
            return LiveVoiceTokenResult(
                ok=False,
                provider="gemini",
                model=self.config.live_voice_model,
                timestamp=timestamp,
                error="Не удалось подготовить потоковый голосовой ввод.",
                admin_hint=f"Gemini Live token HTTP {exc.code}: {raw_error[:500]}",
                metadata={"status": exc.code},
            )
        except Exception as exc:
            return LiveVoiceTokenResult(
                ok=False,
                provider="gemini",
                model=self.config.live_voice_model,
                timestamp=timestamp,
                error="Не удалось подготовить потоковый голосовой ввод.",
                admin_hint=f"{type(exc).__name__}: {exc}",
                metadata={},
            )

        token = str(body.get("name") or "")
        if not token:
            return LiveVoiceTokenResult(
                ok=False,
                provider="gemini",
                model=self.config.live_voice_model,
                timestamp=timestamp,
                error="Не удалось получить временный токен Live API.",
                admin_hint="Gemini Live token response did not include name.",
                metadata={"response_keys": sorted(body.keys())},
            )

        return LiveVoiceTokenResult(
            ok=True,
            provider="gemini",
            model=self.config.live_voice_model,
            timestamp=timestamp,
            token=token,
            websocket_url=_websocket_url(self.config, token),
            setup=setup,
            expires_at=_format_google_timestamp(expires_at),
            new_session_expires_at=_format_google_timestamp(new_session_expires_at),
            metadata={"token_response_keys": sorted(body.keys())},
        )

    def _config_error(self, public_error: str, admin_hint: str, timestamp: str) -> LiveVoiceTokenResult:
        return LiveVoiceTokenResult(
            ok=False,
            provider=self.config.live_voice_provider,
            model=self.config.live_voice_model,
            timestamp=timestamp,
            error=public_error,
            admin_hint=admin_hint,
            metadata={},
        )


def make_live_voice_adapter(config: AppConfig) -> LiveVoiceAdapter:
    return GeminiLiveVoiceAdapter(config)


def live_voice_setup(config: AppConfig) -> dict[str, Any]:
    return {
        "model": _model_resource(config.live_voice_model),
        "generationConfig": {
            "responseModalities": [config.live_voice_response_modality or "TEXT"],
            "temperature": 0,
        },
        "systemInstruction": {
            "parts": [
                {
                    "text": LIVE_VOICE_TRANSCRIPTION_INSTRUCTION.strip(),
                }
            ]
        },
        "inputAudioTranscription": {},
        "realtimeInputConfig": {
            "automaticActivityDetection": {
                "disabled": False,
            },
            "turnCoverage": "TURN_INCLUDES_ONLY_ACTIVITY",
        },
    }


def _model_resource(model: str) -> str:
    clean = model.strip()
    if clean.startswith("models/"):
        return clean
    return f"models/{clean}"


def _rest_base_url(config: AppConfig) -> str:
    return (config.live_voice_base_url or "https://generativelanguage.googleapis.com").rstrip("/")


def _websocket_url(config: AppConfig, token: str) -> str:
    base = _rest_base_url(config)
    if base.startswith("https://"):
        base = "wss://" + base.removeprefix("https://")
    elif base.startswith("http://"):
        base = "ws://" + base.removeprefix("http://")
    encoded_token = urllib.parse.quote(token, safe="")
    return (
        f"{base}/ws/google.ai.generativelanguage.v1alpha."
        f"GenerativeService.BidiGenerateContentConstrained?access_token={encoded_token}"
    )


def _format_google_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
