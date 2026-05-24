from __future__ import annotations

import json
import tempfile
import unittest
import urllib.request
from pathlib import Path
from typing import Any

from app.config import AppConfig, REPO_ROOT, is_blank_or_placeholder
from app.context_loader import ContextLoader
from app.llm import GeminiAdapter
from app.runtime import DemoRuntime
from app.storage import Storage
from app.structured_output import STRUCTURED_OUTPUT_SCHEMA


def test_config(db_path: Path, *, api_key: str = "") -> AppConfig:
    return AppConfig(
        app_env="test",
        app_name="coocking-cart",
        app_base_url="http://127.0.0.1:8000",
        public_domain="",
        demo_mode=True,
        sqlite_db_path=db_path,
        context_manifest_path=REPO_ROOT / "docs" / "mvp" / "context" / "context_manifest.yml",
        context_layers_dir=REPO_ROOT / "docs" / "mvp" / "context",
        llm_provider="gemini",
        llm_model="gemini-3.1-pro-preview",
        llm_api_key=api_key,
        llm_base_url="",
        llm_timeout_seconds=5,
        enable_context_inspector=True,
        enable_llm_trace=True,
        bootstrap_admin_email="admin@example.test",
        bootstrap_admin_password="password",
        bootstrap_admin_password_hash="",
        auth_session_secret="test-session-secret",
        deploy_host="",
        deploy_user="",
        traefik_network_name="",
        traefik_entrypoint="",
        traefik_certresolver="",
    )


class CoreContractsTest(unittest.TestCase):
    def test_placeholder_validation(self) -> None:
        self.assertTrue(is_blank_or_placeholder(""))
        self.assertTrue(is_blank_or_placeholder("<GEMINI_API_KEY>"))
        self.assertFalse(is_blank_or_placeholder("real-looking-value"))

    def test_context_loader_reads_manifest_order(self) -> None:
        loader = ContextLoader(
            REPO_ROOT / "docs" / "mvp" / "context" / "context_manifest.yml",
            REPO_ROOT / "docs" / "mvp" / "context",
        )
        pack = loader.load()
        self.assertEqual([layer.order for layer in pack.layers], list(range(8)))
        self.assertEqual(pack.layers[0].file, "00_AGENT_ROLE.md")
        self.assertIn("Context layer 0", pack.static_text())

    def test_runtime_missing_llm_key_returns_safe_structured_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            user = storage.ensure_demo_user()
            session_id = storage.create_chat_session(user.id, "smoke")
            result = DemoRuntime(config, storage).process_user_message(session_id, user, "Хочу карту яичницы")
            self.assertTrue(result["ok"])
            self.assertEqual(result["structured_output"]["workflow_status"], "llm_error")
            self.assertIn("user_answer", result["structured_output"])
            self.assertIsNone(result["trace"])

    def test_gemini_adapter_sends_response_schema_in_generation_config(self) -> None:
        captured: dict[str, Any] = {}

        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: Any) -> None:
                return None

            def read(self) -> bytes:
                body = {"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}
                return json.dumps(body).encode("utf-8")

        original_urlopen = urllib.request.urlopen

        def fake_urlopen(request: urllib.request.Request, timeout: int = 0) -> FakeResponse:
            captured["payload"] = json.loads(request.data.decode("utf-8"))  # type: ignore[union-attr]
            captured["timeout"] = timeout
            return FakeResponse()

        try:
            urllib.request.urlopen = fake_urlopen  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp:
                config = test_config(Path(tmp) / "demo.sqlite", api_key="fake-key")
                GeminiAdapter(config).call("assembled context", STRUCTURED_OUTPUT_SCHEMA)
        finally:
            urllib.request.urlopen = original_urlopen  # type: ignore[assignment]

        response_format = captured["payload"]["generationConfig"]["responseFormat"]["text"]
        self.assertEqual(response_format["mimeType"], "application/json")
        self.assertEqual(response_format["schema"]["type"], "object")
        self.assertIn("user_answer", response_format["schema"]["properties"])


if __name__ == "__main__":
    unittest.main()
