from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class VisualAssetContract:
    asset_kind: str
    background_mode: str
    transparent_background: bool
    layer_role: str
    z_slot: str
    overlap_policy: str
    safe_area: str
    crop_policy: str
    shadow_policy: str
    aspect_ratio: str
    output_format: str
    constraints: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PromptTemplate:
    id: str
    version: str
    display_name: str
    purpose: str
    target_section: str
    target_asset_kind: str
    recommended_provider: str
    visual_contract: VisualAssetContract
    required_user_approval: bool
    template: str
    negative_prompt: str = ""
    contains_people: bool = False

    def to_dict(self, *, include_template: bool = True) -> dict[str, Any]:
        payload = asdict(self)
        payload["visual_contract"] = self.visual_contract.to_dict()
        if not include_template:
            payload.pop("template", None)
        return payload


@dataclass(frozen=True)
class ProviderGenerationRequest:
    prompt: str
    aspect_ratio: str
    output_format: str
    request_metadata: dict[str, Any]


@dataclass(frozen=True)
class ProviderImage:
    data: bytes
    mime_type: str
    provider_index: int = 0


@dataclass(frozen=True)
class ProviderGenerationResponse:
    provider: str
    model: str
    images: tuple[ProviderImage, ...]
    provider_request_id: str = ""
    metadata: dict[str, Any] | None = None
