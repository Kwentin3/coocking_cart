from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from typing import Any

from app.config import AppConfig, is_blank_or_placeholder

from .contracts import ProviderGenerationRequest, ProviderGenerationResponse, ProviderImage


FACTORY_REQUIRED = "ASSET_IMAGE_PROVIDER_CALLS_MUST_USE_make_image_generation_provider"


class ImageGenerationProvider:
    provider_key = "base"

    def generate(self, request: ProviderGenerationRequest) -> ProviderGenerationResponse:
        raise NotImplementedError


class ImageProviderError(RuntimeError):
    pass


class MockImageProvider(ImageGenerationProvider):
    provider_key = "mock"

    def generate(self, request: ProviderGenerationRequest) -> ProviderGenerationResponse:
        return ProviderGenerationResponse(
            provider=self.provider_key,
            model="mock-transparent-png",
            images=(ProviderImage(data=_TRANSPARENT_PNG_BYTES, mime_type="image/png"),),
            metadata={"mock": True, "request_metadata": request.request_metadata},
        )


class GeminiImageProvider(ImageGenerationProvider):
    provider_key = "gemini"

    def __init__(self, config: AppConfig):
        self.config = config

    def generate(self, request: ProviderGenerationRequest) -> ProviderGenerationResponse:
        if is_blank_or_placeholder(self.config.asset_model):
            raise ImageProviderError("ASSET_MODEL is missing, blank, or placeholder.")
        if is_blank_or_placeholder(self.config.asset_gemini_api_key):
            raise ImageProviderError("ASSET_GEMINI_API_KEY/GEMINI_API_KEY is missing, blank, or placeholder.")

        base_url = (self.config.asset_base_url or "https://generativelanguage.googleapis.com").rstrip("/")
        endpoint = f"{base_url}/v1/models/{self.config.asset_model}:generateContent"
        # Gemini image REST currently accepts the minimal generateContent shape
        # reliably. Aspect ratio stays in the governed prompt contract; do not
        # bypass the service/prompt boundary with provider-specific defaults.
        payload = {
            "contents": [{"parts": [{"text": request.prompt}]}],
        }
        http_request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.config.asset_gemini_api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=self.config.asset_timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw_error = exc.read().decode("utf-8", errors="replace")
            raise ImageProviderError(f"Gemini image generation HTTP {exc.code}: {raw_error[:500]}") from exc
        except Exception as exc:
            raise ImageProviderError(f"{type(exc).__name__}: {exc}") from exc

        images = _extract_inline_images(body)
        if not images:
            raise ImageProviderError("Gemini image generation response did not include inline image data.")

        return ProviderGenerationResponse(
            provider=self.provider_key,
            model=self.config.asset_model,
            images=tuple(images),
            metadata={
                "finish": _finish_reasons(body),
                "usage_metadata": body.get("usageMetadata") or body.get("usage_metadata") or {},
                "request_metadata": request.request_metadata,
            },
        )


class OpenAIImageProvider(ImageGenerationProvider):
    provider_key = "openai"

    def __init__(self, config: AppConfig):
        self.config = config

    def generate(self, request: ProviderGenerationRequest) -> ProviderGenerationResponse:
        if is_blank_or_placeholder(self.config.asset_model):
            raise ImageProviderError("ASSET_MODEL is missing, blank, or placeholder.")
        if is_blank_or_placeholder(self.config.asset_openai_api_key):
            raise ImageProviderError("ASSET_OPENAI_API_KEY/OPENAI_API_KEY is missing, blank, or placeholder.")

        output_format = _openai_output_format(request)
        payload = {
            "model": self.config.asset_model,
            "prompt": request.prompt,
            "n": 1,
            "size": _openai_size(request.aspect_ratio),
            "background": _openai_background(request),
            "output_format": output_format,
        }
        endpoint = f"{self.config.asset_openai_base_url.rstrip('/')}/v1/images/generations"
        http_request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.asset_openai_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=self.config.asset_timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw_error = exc.read().decode("utf-8", errors="replace")
            raise ImageProviderError(f"OpenAI image generation HTTP {exc.code}: {raw_error[:500]}") from exc
        except Exception as exc:
            raise ImageProviderError(f"{type(exc).__name__}: {exc}") from exc

        images = _extract_openai_images(body, output_format=output_format)
        if not images:
            raise ImageProviderError("OpenAI image generation response did not include image data.")

        return ProviderGenerationResponse(
            provider=self.provider_key,
            model=self.config.asset_model,
            images=tuple(images),
            metadata={
                "usage_metadata": body.get("usage") or {},
                "request_metadata": request.request_metadata,
                "openai_background": payload["background"],
                "openai_output_format": output_format,
                "openai_size": payload["size"],
            },
        )


def make_image_generation_provider(config: AppConfig) -> ImageGenerationProvider:
    provider = (config.asset_provider or "mock").strip().lower()
    if provider == "mock":
        return MockImageProvider()
    if provider == "gemini":
        return GeminiImageProvider(config)
    if provider == "openai":
        return OpenAIImageProvider(config)
    raise ValueError("ASSET_PROVIDER must be mock, gemini, or openai.")


def _extract_inline_images(body: dict[str, Any]) -> list[ProviderImage]:
    images: list[ProviderImage] = []
    for candidate in body.get("candidates") or []:
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            if part.get("thought"):
                continue
            inline = part.get("inlineData") or part.get("inline_data") or {}
            encoded = inline.get("data")
            if not encoded:
                continue
            mime_type = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            images.append(
                ProviderImage(
                    data=base64.b64decode(encoded),
                    mime_type=str(mime_type),
                    provider_index=len(images),
                )
            )
    return images


def _finish_reasons(body: dict[str, Any]) -> list[str]:
    return [str(candidate.get("finishReason") or candidate.get("finish_reason") or "") for candidate in body.get("candidates") or []]


def _openai_background(request: ProviderGenerationRequest) -> str:
    return "transparent" if request.request_metadata.get("transparent_background") else "auto"


def _openai_output_format(request: ProviderGenerationRequest) -> str:
    output_format = (request.output_format or "png").strip().lower()
    if _openai_background(request) == "transparent" and output_format not in {"png", "webp"}:
        return "png"
    if output_format in {"png", "webp", "jpeg"}:
        return output_format
    return "png"


def _openai_size(aspect_ratio: str) -> str:
    ratio = (aspect_ratio or "1:1").replace(" ", "")
    if ratio in {"1:1", "1/1"}:
        return "1024x1024"
    if ratio in {"3:4", "3/4", "9:16", "9/16"}:
        return "1024x1536"
    if ratio in {"4:3", "4/3", "16:9", "16/9"}:
        return "1536x1024"
    return "1024x1024"


def _extract_openai_images(body: dict[str, Any], *, output_format: str) -> list[ProviderImage]:
    mime_type = {"png": "image/png", "webp": "image/webp", "jpeg": "image/jpeg"}.get(output_format, "image/png")
    images: list[ProviderImage] = []
    for item in body.get("data") or []:
        encoded = item.get("b64_json")
        if encoded:
            images.append(
                ProviderImage(
                    data=base64.b64decode(encoded),
                    mime_type=mime_type,
                    provider_index=len(images),
                )
            )
            continue
        url = item.get("url")
        if url:
            images.append(
                ProviderImage(
                    data=_download_image_url(str(url)),
                    mime_type=str(item.get("mime_type") or mime_type),
                    provider_index=len(images),
                )
            )
    return images


def _download_image_url(url: str) -> bytes:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


_TRANSPARENT_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lzQn7wAAAABJRU5ErkJggg=="
)
