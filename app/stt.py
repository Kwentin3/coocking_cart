from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .config import AppConfig, is_blank_or_placeholder
from .transcription_policy import build_batch_transcription_prompt


SUPPORTED_STT_MIME_TYPES = {
    "audio/wav",
    "audio/mp4",
    "audio/mp3",
    "audio/mpeg",
    "audio/aiff",
    "audio/aac",
    "audio/ogg",
    "audio/flac",
}


@dataclass(frozen=True)
class SttResult:
    ok: bool
    text: str
    provider: str
    model: str
    timestamp: str
    error: str | None = None
    admin_hint: str | None = None
    metadata: dict[str, Any] | None = None


class SttAdapter:
    def transcribe(self, audio_bytes: bytes, mime_type: str, duration_ms: int | None = None) -> SttResult:
        raise NotImplementedError


class GeminiSttAdapter(SttAdapter):
    def __init__(self, config: AppConfig):
        self.config = config

    def transcribe(self, audio_bytes: bytes, mime_type: str, duration_ms: int | None = None) -> SttResult:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        normalized_mime = normalize_mime_type(mime_type)
        if self.config.stt_provider != "gemini":
            return self._config_error("STT provider не поддерживается.", "STT_PROVIDER must be gemini.", timestamp)
        if is_blank_or_placeholder(self.config.stt_model):
            return self._config_error("STT model не настроена.", "STT_MODEL is missing, blank, or placeholder.", timestamp)
        if is_blank_or_placeholder(self.config.stt_api_key):
            return self._config_error("STT API key не настроен.", "STT_API_KEY is missing, blank, or placeholder.", timestamp)
        if normalized_mime not in SUPPORTED_STT_MIME_TYPES:
            return self._config_error(
                "Формат аудио не поддерживается.",
                f"Unsupported STT MIME type: {normalized_mime}",
                timestamp,
            )

        base_url = (self.config.stt_base_url or "https://generativelanguage.googleapis.com").rstrip("/")
        endpoint = f"{base_url}/v1beta/models/{self.config.stt_model}:generateContent"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": build_batch_transcription_prompt(self.config)},
                        {
                            "inlineData": {
                                "mimeType": normalized_mime,
                                "data": base64.b64encode(audio_bytes).decode("ascii"),
                            }
                        },
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0,
            },
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.config.stt_api_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.stt_timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw_error = exc.read().decode("utf-8", errors="replace")
            return SttResult(
                ok=False,
                text="",
                provider="gemini",
                model=self.config.stt_model,
                timestamp=timestamp,
                error="Не удалось распознать аудио.",
                admin_hint=f"Gemini STT HTTP {exc.code}: {raw_error[:500]}",
                metadata={"status": exc.code, "duration_ms": duration_ms},
            )
        except Exception as exc:
            return SttResult(
                ok=False,
                text="",
                provider="gemini",
                model=self.config.stt_model,
                timestamp=timestamp,
                error="Не удалось распознать аудио.",
                admin_hint=f"{type(exc).__name__}: {exc}",
                metadata={"duration_ms": duration_ms},
            )

        text = extract_text(body)
        if not text.strip():
            return SttResult(
                ok=False,
                text="",
                provider="gemini",
                model=self.config.stt_model,
                timestamp=timestamp,
                error="Не удалось распознать речь в аудио.",
                admin_hint="Gemini STT returned an empty text response.",
                metadata={"duration_ms": duration_ms, "finish": finish_reason(body)},
            )
        return SttResult(
            ok=True,
            text=text.strip(),
            provider="gemini",
            model=self.config.stt_model,
            timestamp=timestamp,
            metadata={
                "duration_ms": duration_ms,
                "finish": finish_reason(body),
                "usage_metadata": body.get("usageMetadata") or {},
            },
        )

    def _config_error(self, public_error: str, admin_hint: str, timestamp: str) -> SttResult:
        return SttResult(
            ok=False,
            text="",
            provider=self.config.stt_provider,
            model=self.config.stt_model,
            timestamp=timestamp,
            error=public_error,
            admin_hint=admin_hint,
            metadata={},
        )


def make_stt_adapter(config: AppConfig) -> SttAdapter:
    return GeminiSttAdapter(config)


def normalize_mime_type(value: str) -> str:
    mime_type = (value or "").split(";", 1)[0].strip().lower()
    if mime_type in {"audio/m4a", "audio/x-m4a"}:
        return "audio/mp4"
    return mime_type


def extract_text(body: dict[str, Any]) -> str:
    candidates = body.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    return "\n".join(texts).strip()


def finish_reason(body: dict[str, Any]) -> str:
    candidates = body.get("candidates") or []
    if not candidates:
        return ""
    return str(candidates[0].get("finishReason", ""))
