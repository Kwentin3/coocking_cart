from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import secrets
from typing import Any

from app.config import AppConfig

from .contracts import ProviderGenerationRequest, VisualAssetContract
from .prompt_templates import get_prompt_template, list_prompt_templates
from .providers import ImageGenerationProvider, make_image_generation_provider
from .storage import LocalAssetStore


class AssetGenerationService:
    def __init__(self, config: AppConfig, provider: ImageGenerationProvider, store: LocalAssetStore):
        self.config = config
        self.provider = provider
        self.store = store

    def list_templates(self) -> list[dict[str, Any]]:
        return [template.to_dict(include_template=False) for template in list_prompt_templates()]

    def generation_context(self, template_id: str) -> dict[str, Any]:
        template = get_prompt_template(template_id)
        return {
            "template": template.to_dict(),
            "visualContract": template.visual_contract.to_dict(),
            "provider": {
                "configuredProvider": self.config.asset_provider,
                "recommendedProvider": template.recommended_provider,
                "realGenerationEnabled": self.config.asset_generation_enabled,
                "storageRoot": str(self.config.asset_storage_root),
            },
            "publicationBoundary": {
                "candidateGenerationDoesNotPublish": True,
                "registryMutationAllowed": False,
                "futureCmsEntryPoint": "call AssetGenerationService, not provider adapters directly",
            },
        }

    def draft_prompt(self, template_id: str, subject: str, *, target_asset_key: str = "") -> dict[str, Any]:
        template = get_prompt_template(template_id)
        prompt = template.template.format(subject=subject.strip())
        return {
            "templateId": template.id,
            "templateVersion": template.version,
            "subject": subject,
            "targetAssetKey": target_asset_key,
            "prompt": prompt,
            "negativePrompt": template.negative_prompt,
            "promptHash": sha256(prompt.encode("utf-8")).hexdigest(),
            "visualContract": template.visual_contract.to_dict(),
        }

    def generate_candidates(
        self,
        template_id: str,
        subject: str,
        *,
        count: int = 1,
        target_asset_key: str = "",
        requested_by: str = "cli",
    ) -> list[dict[str, Any]]:
        if count < 1:
            raise ValueError("count must be at least 1.")
        if count > self.config.asset_max_candidates_per_run:
            raise ValueError(f"count exceeds ASSET_MAX_CANDIDATES_PER_RUN={self.config.asset_max_candidates_per_run}.")
        if self.config.asset_provider != "mock" and not self.config.asset_generation_enabled:
            raise RuntimeError("Real asset generation is disabled. Set ASSET_GENERATION_ENABLED=true to call providers.")

        draft = self.draft_prompt(template_id, subject, target_asset_key=target_asset_key)
        template = get_prompt_template(template_id)
        stored: list[dict[str, Any]] = []
        for _ in range(count):
            response = self.provider.generate(
                ProviderGenerationRequest(
                    prompt=draft["prompt"],
                    aspect_ratio=template.visual_contract.aspect_ratio,
                    output_format=template.visual_contract.output_format,
                    request_metadata={
                        "template_id": template.id,
                        "template_version": template.version,
                        "target_asset_key": target_asset_key,
                        "transparent_background": template.visual_contract.transparent_background,
                        "asset_kind": template.visual_contract.asset_kind,
                    },
                )
            )
            for image in response.images:
                candidate_id = _candidate_id()
                generated_at = _utc_now()
                contract_validation = _validate_image_contract(template.visual_contract, image.mime_type)
                candidate = {
                    "id": candidate_id,
                    "status": "pending_review",
                    "approvalStatus": "pending_review",
                    "contractValidation": contract_validation,
                    "provider": response.provider,
                    "model": response.model,
                    "providerRequestId": response.provider_request_id,
                    "assetKind": template.visual_contract.asset_kind,
                    "backgroundMode": template.visual_contract.background_mode,
                    "transparentBackground": template.visual_contract.transparent_background,
                    "layerRole": template.visual_contract.layer_role,
                    "zSlot": template.visual_contract.z_slot,
                    "overlapPolicy": template.visual_contract.overlap_policy,
                    "safeArea": template.visual_contract.safe_area,
                    "cropPolicy": template.visual_contract.crop_policy,
                    "shadowPolicy": template.visual_contract.shadow_policy,
                    "aspectRatio": template.visual_contract.aspect_ratio,
                    "outputFormat": template.visual_contract.output_format,
                    "subject": subject,
                    "targetAssetKey": target_asset_key,
                    "prompt": draft["prompt"],
                    "negativePrompt": template.negative_prompt,
                    "promptHash": draft["promptHash"],
                    "promptTemplateKey": template.id,
                    "promptTemplateVersion": template.version,
                    "generatedAt": generated_at,
                    "generatedBy": requested_by,
                    "rightsStatus": "unchecked",
                    "commercialUseChecked": False,
                    "provenance": {
                        "source": "generated",
                        "promptStored": True,
                        "sourcePromptHash": draft["promptHash"],
                        "synthIdWatermarkExpected": response.provider == "gemini",
                        "containsPeople": template.visual_contract.layer_role == "heroHumanCutout",
                        "containsRecognizablePerson": False,
                        "containsBrandElements": False,
                        "containsThirdPartyLogo": False,
                        "containsKnownCharacter": False,
                        "commercialUseChecked": False,
                    },
                    "providerMetadata": response.metadata or {},
                }
                stored.append(self.store.save_candidate(candidate, image))
                if len(stored) >= count:
                    return stored
        return stored

    def list_candidates(self) -> list[dict[str, Any]]:
        return self.store.list_candidates()

    def inspect_candidate(self, candidate_id: str) -> dict[str, Any]:
        return self.store.inspect_candidate(candidate_id)

    def approve_candidate(self, candidate_id: str, asset_key: str, *, approved_by: str = "cli") -> dict[str, Any]:
        return self.store.approve_candidate(candidate_id, asset_key, approved_by=approved_by, approved_at=_utc_now())


def make_asset_generation_service(config: AppConfig) -> AssetGenerationService:
    return AssetGenerationService(
        config=config,
        provider=make_image_generation_provider(config),
        store=LocalAssetStore(config.asset_storage_root),
    )


def _candidate_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"cand_{stamp}_{secrets.token_hex(4)}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validate_image_contract(contract: VisualAssetContract, mime_type: str) -> dict[str, Any]:
    violations: list[str] = []
    normalized_mime = (mime_type or "").lower()
    if contract.transparent_background and normalized_mime in {"image/jpeg", "image/jpg"}:
        violations.append("transparent_background_required_but_jpeg_has_no_alpha")
    if contract.transparent_background and normalized_mime not in {"image/png", "image/webp"}:
        violations.append("transparent_background_requires_png_or_webp_candidate")
    return {
        "ok": not violations,
        "violations": violations,
    }
