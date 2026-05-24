from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .config import AppConfig, is_blank_or_placeholder


@dataclass(frozen=True)
class LlmResult:
    ok: bool
    text: str
    provider: str
    model: str
    timestamp: str
    error: str | None = None
    admin_hint: str | None = None
    metadata: dict[str, Any] | None = None


class GeminiAdapter:
    def __init__(self, config: AppConfig):
        self.config = config

    def call(
        self,
        assembled_context: str,
        response_schema: dict[str, Any],
        request_metadata: dict[str, Any] | None = None,
    ) -> LlmResult:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if self.config.llm_provider != "gemini":
            return self._config_error("LLM provider не поддерживается.", "LLM_PROVIDER must be gemini.", timestamp)
        if is_blank_or_placeholder(self.config.llm_model):
            return self._config_error("LLM model не настроена.", "LLM_MODEL is missing, blank, or placeholder.", timestamp)
        if is_blank_or_placeholder(self.config.llm_api_key):
            return self._config_error("LLM API key не настроен.", "LLM_API_KEY is missing, blank, or placeholder.", timestamp)

        base_url = (self.config.llm_base_url or "https://generativelanguage.googleapis.com").rstrip("/")
        endpoint = f"{base_url}/v1beta/models/{self.config.llm_model}:generateContent"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": assembled_context}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": response_schema,
            },
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.config.llm_api_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.llm_timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw_error = exc.read().decode("utf-8", errors="replace")
            return LlmResult(
                ok=False,
                text="",
                provider="gemini",
                model=self.config.llm_model,
                timestamp=timestamp,
                error="Ошибка вызова LLM provider.",
                admin_hint=f"Gemini HTTP {exc.code}: {raw_error[:500]}",
                metadata={"status": exc.code, "request_metadata": request_metadata or {}},
            )
        except Exception as exc:
            return LlmResult(
                ok=False,
                text="",
                provider="gemini",
                model=self.config.llm_model,
                timestamp=timestamp,
                error="Ошибка вызова LLM provider.",
                admin_hint=f"{type(exc).__name__}: {exc}",
                metadata={"request_metadata": request_metadata or {}},
            )

        text = self._extract_text(body)
        return LlmResult(
            ok=True,
            text=text,
            provider="gemini",
            model=self.config.llm_model,
            timestamp=timestamp,
            metadata={
                "request_metadata": request_metadata or {},
                "finish": self._finish_reason(body),
                "usage_metadata": body.get("usageMetadata") or {},
            },
        )

    def _config_error(self, public_error: str, admin_hint: str, timestamp: str) -> LlmResult:
        return LlmResult(
            ok=False,
            text="",
            provider=self.config.llm_provider,
            model=self.config.llm_model,
            timestamp=timestamp,
            error=public_error,
            admin_hint=admin_hint,
            metadata={},
        )

    @staticmethod
    def _extract_text(body: dict[str, Any]) -> str:
        candidates = body.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
        return "\n".join(texts).strip()

    @staticmethod
    def _finish_reason(body: dict[str, Any]) -> str:
        candidates = body.get("candidates") or []
        if not candidates:
            return ""
        return str(candidates[0].get("finishReason", ""))
