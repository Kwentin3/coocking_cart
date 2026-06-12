from __future__ import annotations

import base64
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from app.asset_generation.contracts import ProviderGenerationRequest, ProviderGenerationResponse, ProviderImage
from app.asset_generation.providers import (
    FACTORY_REQUIRED,
    GeminiImageProvider,
    MockImageProvider,
    OpenAIImageProvider,
    make_image_generation_provider,
)
from app.asset_generation.service import AssetGenerationService, make_asset_generation_service
from app.asset_generation.storage import LocalAssetStore
from app.config import AppConfig, REPO_ROOT


def make_test_config(tmp: Path) -> AppConfig:
    return AppConfig(
        app_env="test",
        app_name="coocking-cart",
        app_base_url="http://127.0.0.1:8000",
        app_base_path="",
        public_domain="",
        demo_mode=True,
        sqlite_db_path=tmp / "demo.sqlite",
        context_manifest_path=REPO_ROOT / "docs" / "mvp" / "context" / "context_manifest.yml",
        context_layers_dir=REPO_ROOT / "docs" / "mvp" / "context",
        llm_provider="gemini",
        llm_model="gemini-3.1-pro-preview",
        llm_api_key="",
        llm_base_url="",
        llm_timeout_seconds=5,
        stt_enabled=True,
        stt_provider="gemini",
        stt_model="gemini-3.1-pro-preview",
        stt_api_key="",
        stt_base_url="",
        stt_timeout_seconds=5,
        stt_max_audio_seconds=180,
        stt_countdown_seconds=15,
        stt_max_audio_bytes=12_000_000,
        live_voice_enabled=True,
        live_voice_provider="gemini",
        live_voice_model="gemini-3.1-flash-live-preview",
        live_voice_api_key="",
        live_voice_base_url="",
        live_voice_timeout_seconds=5,
        live_voice_token_ttl_seconds=1800,
        live_voice_new_session_seconds=60,
        live_voice_input_sample_rate=16000,
        live_voice_response_modality="AUDIO",
        live_voice_transport="direct_client",
        live_voice_socks5_host="",
        live_voice_socks5_port=1080,
        live_voice_socks5_username="",
        live_voice_socks5_password="",
        voice_transcription_language="russian",
        voice_transcription_script="cyrillic",
        voice_transcription_latin_allowlist="iiko, r_keeper, StoreHouse, HACCP",
        voice_transcription_domain_terms="TK, TTK",
        voice_transcription_unclear_marker="[unclear]",
        voice_transcription_extra_instruction="",
        voice_transcription_prompt_override="",
        enable_context_inspector=True,
        enable_llm_trace=True,
        bootstrap_admin_email="admin@example.test",
        bootstrap_admin_password="password",
        bootstrap_admin_password_hash="",
        auth_session_secret="test-session-secret",
        session_cookie_secure="auto",
        deploy_host="",
        deploy_user="",
        traefik_network_name="",
        traefik_entrypoint="",
        traefik_certresolver="",
        asset_generation_enabled=False,
        asset_provider="mock",
        asset_model="",
        asset_gemini_api_key="",
        asset_openai_api_key="",
        asset_openai_base_url="https://api.openai.com",
        asset_base_url="",
        asset_timeout_seconds=5,
        asset_storage_root=tmp / "generated-assets",
        asset_max_candidates_per_run=2,
    )


class AssetGenerationContractsTest(unittest.TestCase):
    def test_context_exposes_visual_contract_for_agent_and_future_cms(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            service = make_asset_generation_service(make_test_config(Path(raw_tmp)))
            context = service.generation_context("food.cutout.square")

        contract = context["visualContract"]
        self.assertEqual(context["provider"]["recommendedProvider"], "openai")
        self.assertEqual(contract["asset_kind"], "cutout")
        self.assertEqual(contract["background_mode"], "transparent")
        self.assertTrue(contract["transparent_background"])
        self.assertEqual(contract["aspect_ratio"], "1:1")
        self.assertIn("transparent background with real alpha", contract["constraints"])
        self.assertTrue(context["publicationBoundary"]["candidateGenerationDoesNotPublish"])
        self.assertFalse(context["publicationBoundary"]["registryMutationAllowed"])

    def test_final_cta_brand_band_contract_is_embedded_backdrop(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            service = make_asset_generation_service(make_test_config(Path(raw_tmp)))
            context = service.generation_context("finalCta.backdrop.brandBand")

        contract = context["visualContract"]
        self.assertEqual(context["provider"]["recommendedProvider"], "openai")
        self.assertEqual(contract["asset_kind"], "backdrop")
        self.assertEqual(contract["background_mode"], "embedded")
        self.assertFalse(contract["transparent_background"])
        self.assertEqual(contract["layer_role"], "finalCtaBrandBand")
        self.assertEqual(contract["safe_area"], "preserveTextAndCta")
        self.assertIn("no baked text", contract["constraints"])

    def test_audience_card_media_contract_is_embedded_content_image(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            service = make_asset_generation_service(make_test_config(Path(raw_tmp)))
            context = service.generation_context("audience.card.media")

        contract = context["visualContract"]
        self.assertEqual(context["provider"]["recommendedProvider"], "openai")
        self.assertEqual(contract["asset_kind"], "contentImage")
        self.assertEqual(contract["background_mode"], "embedded")
        self.assertFalse(contract["transparent_background"])
        self.assertEqual(contract["layer_role"], "audienceCardMedia")
        self.assertEqual(contract["safe_area"], "preserveCardContent")
        self.assertEqual(contract["aspect_ratio"], "16:9")
        self.assertIn("no baked text", contract["constraints"])
        self.assertTrue(context["template"]["contains_people"])

    def test_mock_generation_persists_candidate_metadata_and_original_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            config = make_test_config(Path(raw_tmp))
            service = make_asset_generation_service(config)

            candidates = service.generate_candidates(
                "food.cutout.square",
                "plate of borscht",
                count=1,
                target_asset_key="hero.dishCutout",
                requested_by="test",
            )
            candidate = candidates[0]
            inspected = service.inspect_candidate(candidate["id"])

            self.assertEqual(inspected["status"], "pending_review")
            self.assertEqual(inspected["provider"], "mock")
            self.assertEqual(inspected["targetAssetKey"], "hero.dishCutout")
            self.assertEqual(inspected["assetKind"], "cutout")
            self.assertTrue(inspected["transparentBackground"])
            self.assertEqual(len(inspected["checksum"]), 64)
            self.assertTrue(Path(inspected["originalPath"]).exists())
            self.assertTrue(Path(inspected["metadataPath"]).exists())

    def test_approve_copies_candidate_to_approved_storage_without_publishing_registry(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            config = make_test_config(Path(raw_tmp))
            service = make_asset_generation_service(config)
            candidate = service.generate_candidates("food.cutout.square", "plate of borscht")[0]

            approved = service.approve_candidate(candidate["id"], "hero.dishCutout", approved_by="test")
            inspected = service.inspect_candidate(candidate["id"])

            self.assertEqual(approved["status"], "approved")
            self.assertEqual(inspected["approvalStatus"], "approved")
            self.assertEqual(approved["targetAssetKey"], "hero.dishCutout")
            self.assertTrue(Path(approved["approvedOriginalPath"]).exists())
            self.assertNotIn("asset.registry.ts", approved["approvedOriginalPath"])

    def test_transparent_contract_blocks_jpeg_approval(self) -> None:
        class JpegProvider:
            provider_key = "fake-jpeg"

            def generate(self, request: ProviderGenerationRequest) -> ProviderGenerationResponse:
                return ProviderGenerationResponse(
                    provider=self.provider_key,
                    model="fake-jpeg-model",
                    images=(ProviderImage(data=b"fake-jpeg-bytes", mime_type="image/jpeg"),),
                )

        with tempfile.TemporaryDirectory() as raw_tmp:
            config = make_test_config(Path(raw_tmp))
            service = AssetGenerationService(
                config=config,
                provider=JpegProvider(),  # type: ignore[arg-type]
                store=LocalAssetStore(config.asset_storage_root),
            )

            candidate = service.generate_candidates("food.cutout.square", "plate of borscht")[0]

            self.assertFalse(candidate["contractValidation"]["ok"])
            self.assertIn(
                "transparent_background_required_but_jpeg_has_no_alpha",
                candidate["contractValidation"]["violations"],
            )
            with self.assertRaisesRegex(ValueError, "visual asset contract"):
                service.approve_candidate(candidate["id"], "hero.dishCutout")

    def test_real_provider_is_factory_routed_and_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            mock_config = make_test_config(Path(raw_tmp))
            self.assertIsInstance(make_image_generation_provider(mock_config), MockImageProvider)
            self.assertIn("make_image_generation_provider", FACTORY_REQUIRED)

            gemini_config = replace(
                mock_config,
                asset_provider="gemini",
                asset_model="gemini-3.1-flash-image",
                asset_gemini_api_key="test-key",
                asset_generation_enabled=False,
            )
            self.assertIsInstance(make_image_generation_provider(gemini_config), GeminiImageProvider)
            service = make_asset_generation_service(gemini_config)
            with self.assertRaisesRegex(RuntimeError, "disabled"):
                service.generate_candidates("food.cutout.square", "plate of borscht")

    def test_openai_provider_uses_transparent_png_contract(self) -> None:
        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps(
                    {
                        "data": [
                            {
                                "b64_json": base64.b64encode(b"png-with-alpha").decode("ascii"),
                            }
                        ],
                        "usage": {"total_tokens": 1},
                    }
                ).encode("utf-8")

        captured: dict[str, object] = {}

        def fake_urlopen(request: object, timeout: int = 0) -> FakeResponse:
            captured["timeout"] = timeout
            captured["headers"] = dict(getattr(request, "headers"))
            captured["payload"] = json.loads(getattr(request, "data").decode("utf-8"))
            return FakeResponse()

        with tempfile.TemporaryDirectory() as raw_tmp:
            config = replace(
                make_test_config(Path(raw_tmp)),
                asset_provider="openai",
                asset_model="gpt-image-1.5",
                asset_openai_api_key="test-openai-key",
                asset_generation_enabled=True,
            )
            self.assertIsInstance(make_image_generation_provider(config), OpenAIImageProvider)
            service = make_asset_generation_service(config)

            with patch("app.asset_generation.providers.urllib.request.urlopen", fake_urlopen):
                candidate = service.generate_candidates("food.cutout.square", "plate of borscht")[0]

        payload = captured["payload"]
        self.assertEqual(payload["model"], "gpt-image-1.5")
        self.assertEqual(payload["background"], "transparent")
        self.assertEqual(payload["output_format"], "png")
        self.assertEqual(payload["size"], "1024x1024")
        self.assertEqual(candidate["provider"], "openai")
        self.assertEqual(candidate["mimeType"], "image/png")
        self.assertTrue(candidate["contractValidation"]["ok"])


if __name__ == "__main__":
    unittest.main()
