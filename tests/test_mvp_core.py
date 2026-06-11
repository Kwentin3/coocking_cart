from __future__ import annotations

import io
import json
import socket
import sqlite3
import tempfile
import threading
import unittest
import urllib.request
from dataclasses import replace
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

# Sticky test environment note: this local workspace is Windows-only and must not
# be treated as Docker/Linux parity. Production Docker/Linux runs on the hosting
# server; local tests verify code contracts, while runtime parity is checked by
# a server-side build/artifact or an explicit artifact simulation. The current
# server deploy path is release-artifact based because git is not installed on
# the host; do not assume a server-side git pull.
# Sticky Live Voice transport note: browser JS cannot receive SOCKS5 secrets or
# force WebSocket/fetch through app-level SOCKS5. SOCKS5 is a backend-only
# server_proxy concern, and direct_client remains the no-proxy browser path.
from app.config import AppConfig, REPO_ROOT, is_blank_or_placeholder
from app.context_loader import ContextLoader
from app.live_voice import (
    FORBIDDEN,
    FACTORY_REQUIRED,
    GeminiLiveVoiceAdapter,
    live_voice_setup,
    make_live_voice_adapter,
)
from app.live_voice_proxy import (
    build_websocket_frame,
    connect_gemini_live_websocket,
    read_websocket_frame,
    websocket_accept_value,
)
from app.llm import GeminiAdapter
from app.main import COOKIE_NAME, DemoMvpHandler, build_session_cookie_header
from app.routes.contracts import ROUTE_DOMAIN_CONTRACTS
from app.runtime import DemoRuntime
from app.security import session_token, sign_cookie
from app.storage import Storage
from app.stt import GeminiSttAdapter, SUPPORTED_STT_MIME_TYPES, normalize_mime_type
from app.transcription_policy import build_batch_transcription_prompt, build_live_voice_transcription_instruction
from app.structured_output import STRUCTURED_OUTPUT_SCHEMA, normalize_structured_output


def make_test_config(db_path: Path, *, api_key: str = "") -> AppConfig:
    return AppConfig(
        app_env="test",
        app_name="coocking-cart",
        app_base_url="http://127.0.0.1:8000",
        app_base_path="",
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
        stt_enabled=True,
        stt_provider="gemini",
        stt_model="gemini-3.1-pro-preview",
        stt_api_key=api_key,
        stt_base_url="",
        stt_timeout_seconds=5,
        stt_max_audio_seconds=180,
        stt_countdown_seconds=15,
        stt_max_audio_bytes=12_000_000,
        live_voice_enabled=True,
        live_voice_provider="gemini",
        live_voice_model="gemini-3.1-flash-live-preview",
        live_voice_api_key=api_key,
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
        voice_transcription_language="русский",
        voice_transcription_script="кириллица",
        voice_transcription_latin_allowlist="iiko, r_keeper, StoreHouse, HACCP",
        voice_transcription_domain_terms="ТК, ТТК, брутто, нетто, выход, БЖУ, ХАССП, СанПиН, 1С",
        voice_transcription_unclear_marker="[неразборчиво]",
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
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            user = storage.ensure_demo_user()
            session_id = storage.create_chat_session(user.id, "smoke")
            result = DemoRuntime(config, storage).process_user_message(session_id, user, "Хочу карту яичницы")
            self.assertTrue(result["ok"])
            self.assertEqual(result["structured_output"]["workflow_status"], "llm_error")
            self.assertIn("user_answer", result["structured_output"])
            self.assertIsNone(result["trace"])

    def test_admin_can_read_inspector_and_user_cannot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            admin = storage.bootstrap_admin(config.bootstrap_admin_email, config.bootstrap_admin_password)
            user = storage.ensure_demo_user()
            session_id = storage.create_chat_session(user.id, "inspector smoke")
            runtime = DemoRuntime(config, storage)
            runtime.process_user_message(session_id, user, "Хочу технологическую карту яичницы")

            assert admin is not None
            admin_payload = runtime.context_inspector_payload(session_id, admin)
            user_payload = runtime.context_inspector_payload(session_id, user)

            self.assertTrue(admin_payload["ok"])
            self.assertEqual(len(admin_payload["layers"]), 8)
            self.assertFalse(user_payload["ok"])

    def test_admin_context_workspace_payload_is_read_only_and_admin_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            admin = storage.bootstrap_admin(config.bootstrap_admin_email, config.bootstrap_admin_password)
            user = storage.ensure_demo_user()
            session_id = storage.create_chat_session(user.id, "context workspace")
            runtime = DemoRuntime(config, storage)
            runtime.process_user_message(session_id, user, "Хочу технологическую карту омлета")

            assert admin is not None
            admin_payload = runtime.admin_context_payload(admin)
            user_payload = runtime.admin_context_payload(user)

            self.assertTrue(admin_payload["ok"])
            self.assertEqual(admin_payload["manifest"]["layer_count"], 8)
            self.assertEqual(len(admin_payload["layers"]), 8)
            self.assertIn("static_context_preview", admin_payload)
            self.assertIn("structured_output_schema", admin_payload)
            self.assertIn("latest_turn", admin_payload)
            self.assertGreater(admin_payload["static_context_estimated_tokens"], 0)
            self.assertFalse(user_payload["ok"])

    def test_admin_dashboard_aggregates_chat_activity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            user = storage.ensure_demo_user()
            session_id = storage.create_chat_session(user.id, "dashboard smoke")
            user_message_id = storage.add_message(session_id, "user", "Хочу карту яичницы")
            assistant_message_id = storage.add_message(session_id, "assistant", "Уточню выход порции.")
            storage.save_turn_result(
                session_id,
                user_message_id,
                assistant_message_id,
                {
                    "user_answer": "Уточню выход порции.",
                    "workflow_status": "clarification",
                    "known_facts": [],
                    "open_questions": [],
                    "warnings": [],
                    "data_statuses": [],
                    "document_draft": None,
                    "structured_json": None,
                    "next_step": "Уточнить порцию.",
                },
                {
                    "assembled_context_preview": "context preview",
                    "llm_metadata": {"usage_metadata": {"totalTokenCount": 123}},
                },
            )

            dashboard = storage.admin_dashboard()
            day = next(item for item in dashboard["periods"] if item["key"] == "day")
            self.assertEqual(day["sessions"], 1)
            self.assertEqual(day["messages"], 2)
            self.assertEqual(day["turns"], 1)
            self.assertGreaterEqual(day["estimated_tokens"], 123)
            self.assertEqual(dashboard["latest_activity"][0]["id"], session_id)
            self.assertEqual(dashboard["latest_activity"][0]["workflow_status"], "clarification")

    def test_bootstrap_admin_is_created_from_env_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            admin = storage.bootstrap_admin(config.bootstrap_admin_email, config.bootstrap_admin_password)
            self.assertIsNotNone(admin)
            self.assertEqual(admin.role, "admin")
            authenticated = storage.authenticate(config.bootstrap_admin_email, config.bootstrap_admin_password)
            self.assertIsNotNone(authenticated)
            self.assertEqual(authenticated.role, "admin")

    def test_admin_user_crud_storage_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            admin = storage.bootstrap_admin(config.bootstrap_admin_email, config.bootstrap_admin_password)
            assert admin is not None

            created = storage.create_user("New.User@Example.TEST", "temporary-password", "user")
            self.assertEqual(created["email"], "new.user@example.test")
            self.assertEqual(created["role"], "user")
            self.assertTrue(created["has_password"])
            self.assertNotIn("password_hash", created)

            users = storage.list_users(current_user_id=admin.id)
            self.assertTrue(any(user["is_current"] for user in users if user["id"] == admin.id))

            updated = storage.update_user(
                created["id"],
                email="Changed.User@Example.TEST",
                role="admin",
                password="new-password",
                current_admin_id=admin.id,
            )
            self.assertEqual(updated["email"], "changed.user@example.test")
            self.assertEqual(updated["role"], "admin")
            authenticated = storage.authenticate("changed.user@example.test", "new-password")
            self.assertIsNotNone(authenticated)
            self.assertEqual(authenticated.role, "admin")

            storage.delete_user(updated["id"], current_admin_id=admin.id)
            self.assertIsNone(storage.authenticate("changed.user@example.test", "new-password"))

    def test_admin_user_crud_guards_current_and_last_admin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            admin = storage.bootstrap_admin(config.bootstrap_admin_email, config.bootstrap_admin_password)
            assert admin is not None

            with self.assertRaises(ValueError):
                storage.delete_user(admin.id, current_admin_id=admin.id)
            with self.assertRaises(ValueError):
                storage.update_user(admin.id, role="user", current_admin_id=admin.id)
            with self.assertRaises(ValueError):
                storage.delete_user(admin.id, current_admin_id=999)

            second_admin = storage.create_user("second-admin@example.test", "password", "admin")
            storage.delete_user(second_admin["id"], current_admin_id=admin.id)
            remaining = storage.list_users(current_user_id=admin.id)
            self.assertEqual([user["role"] for user in remaining].count("admin"), 1)

    def test_chat_session_crud_respects_owner_and_admin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            admin = storage.bootstrap_admin(config.bootstrap_admin_email, config.bootstrap_admin_password)
            owner = storage.ensure_demo_user()
            storage.create_user("other-user@example.test", "password", "user")
            other = storage.authenticate("other-user@example.test", "password")
            assert admin is not None
            assert other is not None

            session_id = storage.create_chat_session(owner.id, "  Исходный чат  ")
            updated = storage.update_chat_session(session_id, owner, "  Переименованный чат  ")
            self.assertEqual(updated["title"], "Переименованный чат")

            with self.assertRaises(PermissionError):
                storage.update_chat_session(session_id, other, "Чужое название")

            admin_updated = storage.update_chat_session(session_id, admin, "Admin rename")
            self.assertEqual(admin_updated["title"], "Admin rename")

            storage.add_message(session_id, "user", "test")
            with self.assertRaises(PermissionError):
                storage.delete_chat_session(session_id, other)
            storage.delete_chat_session(session_id, admin)
            self.assertFalse(storage.can_access_session(session_id, admin))
            self.assertEqual(storage.list_messages(session_id), [])

    def test_storage_schema_has_migrations_indexes_and_turn_message_fks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            owner = storage.ensure_demo_user()
            session_id = storage.create_chat_session(owner.id, "Schema test")
            user_message_id = storage.add_message(session_id, "user", "request")
            assistant_message_id = storage.add_message(session_id, "assistant", "answer")
            storage.save_turn_result(
                session_id,
                user_message_id,
                assistant_message_id,
                {"user_answer": "answer"},
                {"trace": "ok"},
            )

            with storage.connect() as conn:
                version = conn.execute("SELECT MAX(version) AS version FROM schema_migrations").fetchone()["version"]
                fk_rows = conn.execute("PRAGMA foreign_key_list(turn_results)").fetchall()
                fk_targets = {(row["from"], row["table"], row["on_delete"]) for row in fk_rows}
                message_indexes = {row["name"] for row in conn.execute("PRAGMA index_list(messages)").fetchall()}
                turn_indexes = {row["name"] for row in conn.execute("PRAGMA index_list(turn_results)").fetchall()}

                self.assertEqual(version, 1)
                self.assertIn(("user_message_id", "messages", "SET NULL"), fk_targets)
                self.assertIn(("assistant_message_id", "messages", "SET NULL"), fk_targets)
                self.assertIn("idx_messages_session_id_id", message_indexes)
                self.assertIn("idx_turn_results_session_id_id", turn_indexes)
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO turn_results(
                            session_id, user_message_id, assistant_message_id, structured_output, trace, created_at
                        ) VALUES (?, ?, ?, '{}', '{}', ?)
                        """,
                        (session_id, 999_001, assistant_message_id, "2026-05-27T00:00:00+00:00"),
                    )

    def test_storage_migrates_legacy_turn_results_without_losing_valid_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "legacy.sqlite"
            now = "2026-05-27T00:00:00+00:00"
            conn = sqlite3.connect(db_path)
            try:
                conn.executescript(
                    """
                    PRAGMA foreign_keys = ON;
                    CREATE TABLE roles (name TEXT PRIMARY KEY);
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT,
                        role TEXT NOT NULL REFERENCES roles(name),
                        created_at TEXT NOT NULL
                    );
                    CREATE TABLE auth_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token_hash TEXT UNIQUE NOT NULL,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        expires_at TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                    CREATE TABLE chat_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    CREATE TABLE messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                    CREATE TABLE turn_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                        user_message_id INTEGER,
                        assistant_message_id INTEGER,
                        structured_output TEXT NOT NULL,
                        trace TEXT NOT NULL,
                        document_draft TEXT,
                        created_at TEXT NOT NULL
                    );
                    INSERT INTO roles(name) VALUES ('user'), ('admin');
                    INSERT INTO users(id, email, password_hash, role, created_at) VALUES (1, 'legacy@example.test', NULL, 'user', '2026-05-27T00:00:00+00:00');
                    INSERT INTO chat_sessions(id, title, owner_user_id, created_at, updated_at) VALUES (1, 'Legacy', 1, '2026-05-27T00:00:00+00:00', '2026-05-27T00:00:00+00:00');
                    INSERT INTO messages(id, session_id, role, content, created_at) VALUES (1, 1, 'user', 'request', '2026-05-27T00:00:00+00:00');
                    INSERT INTO messages(id, session_id, role, content, created_at) VALUES (2, 1, 'assistant', 'answer', '2026-05-27T00:00:00+00:00');
                    """
                )
                conn.execute(
                    """
                    INSERT INTO turn_results(
                        id, session_id, user_message_id, assistant_message_id, structured_output, trace, document_draft, created_at
                    ) VALUES (1, 1, 1, 2, ?, '{}', NULL, ?)
                    """,
                    (json.dumps({"user_answer": "valid"}), now),
                )
                conn.execute(
                    """
                    INSERT INTO turn_results(
                        id, session_id, user_message_id, assistant_message_id, structured_output, trace, document_draft, created_at
                    ) VALUES (2, 1, 999, 1000, ?, '{}', NULL, ?)
                    """,
                    (json.dumps({"user_answer": "legacy-invalid"}), now),
                )
                conn.commit()
            finally:
                conn.close()

            storage = Storage(db_path)
            with storage.connect() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT id, user_message_id, assistant_message_id FROM turn_results ORDER BY id"
                ).fetchall()
                fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()

            self.assertEqual((rows[0]["user_message_id"], rows[0]["assistant_message_id"]), (1, 2))
            self.assertEqual((rows[1]["user_message_id"], rows[1]["assistant_message_id"]), (None, None))
            self.assertEqual(fk_errors, [])

    def test_placeholder_bootstrap_values_are_not_ready(self) -> None:
        config = make_test_config(Path("unused.sqlite"), api_key="<GEMINI_API_KEY>")
        config = AppConfig(
            **{
                **config.__dict__,
                "bootstrap_admin_email": "<BOOTSTRAP_ADMIN_EMAIL>",
                "bootstrap_admin_password": "<BOOTSTRAP_ADMIN_PASSWORD>",
                "auth_session_secret": "<AUTH_SESSION_SECRET>",
            }
        )
        self.assertFalse(config.bootstrap_ready)
        self.assertFalse(config.auth_ready)
        self.assertFalse(config.llm_ready)

    def test_session_cookie_header_secure_contract(self) -> None:
        secure_cookie = build_session_cookie_header(COOKIE_NAME, "signed-token", max_age=604800, secure=True)
        local_cookie = build_session_cookie_header(COOKIE_NAME, "signed-token", max_age=604800, secure=False)
        prefixed_cookie = build_session_cookie_header(
            COOKIE_NAME,
            "signed-token",
            max_age=604800,
            secure=False,
            path="/mvp",
        )

        self.assertIn("HttpOnly", secure_cookie)
        self.assertIn("SameSite=Lax", secure_cookie)
        self.assertIn("Path=/", secure_cookie)
        self.assertIn("Path=/mvp", prefixed_cookie)
        self.assertIn("Max-Age=604800", secure_cookie)
        self.assertIn("Secure", secure_cookie)
        self.assertNotIn("Secure", local_cookie)

    def test_route_domain_contracts_keep_protected_routes_explicit(self) -> None:
        contracts = {(item.method, item.path): item for item in ROUTE_DOMAIN_CONTRACTS}
        self.assertEqual(len(contracts), len(ROUTE_DOMAIN_CONTRACTS))
        expected = {
            ("GET", "/api/config"): ("config", "public"),
            ("HEAD", "/api/config"): ("config", "public"),
            ("GET", "/api/me"): ("auth", "public"),
            ("POST", "/api/login"): ("auth", "public"),
            ("POST", "/api/demo-login"): ("auth", "public"),
            ("POST", "/api/logout"): ("auth", "public"),
            ("GET", "/api/admin/users"): ("admin", "admin"),
            ("POST", "/api/admin/users"): ("admin", "admin"),
            ("PATCH", "/api/admin/users/{user_id}"): ("admin", "admin"),
            ("DELETE", "/api/admin/users/{user_id}"): ("admin", "admin"),
            ("GET", "/api/admin/dashboard"): ("admin", "admin"),
            ("GET", "/api/admin/context"): ("admin", "admin"),
            ("GET", "/api/sessions"): ("chat", "user"),
            ("POST", "/api/sessions"): ("chat", "user"),
            ("GET", "/api/sessions/{session_id}"): ("chat", "user"),
            ("PATCH", "/api/sessions/{session_id}"): ("chat", "user"),
            ("DELETE", "/api/sessions/{session_id}"): ("chat", "user"),
            ("POST", "/api/sessions/{session_id}/messages"): ("chat", "user"),
            ("GET", "/api/sessions/{session_id}/inspector"): ("context", "user"),
            ("POST", "/api/transcribe"): ("voice", "user"),
            ("POST", "/api/live-voice/token"): ("voice", "user"),
            ("GET", "/api/live-voice/ws/{session_id}"): ("voice", "user"),
        }

        for key, (domain, guard) in expected.items():
            self.assertIn(key, contracts)
            self.assertEqual(contracts[key].domain, domain)
            self.assertEqual(contracts[key].guard, guard)
            self.assertIn(".", contracts[key].handler)

    def test_route_modules_keep_provider_and_sql_boundaries_out(self) -> None:
        for path in (REPO_ROOT / "app" / "routes").glob("*_routes.py"):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("Gemini", source, path.name)
            self.assertNotIn("sqlite3", source, path.name)
            self.assertNotIn("connect_gemini_live_websocket", source, path.name)

    def test_session_cookie_auto_secure_uses_forwarded_https(self) -> None:
        class FakeState:
            def __init__(self, config: AppConfig, storage: Storage):
                self.config = config
                self.storage = storage

        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            config = AppConfig(
                **{
                    **config.__dict__,
                    "app_base_url": "https://coocking-cart.speechbattle.com",
                    "session_cookie_secure": "auto",
                }
            )
            storage = Storage(config.sqlite_db_path)
            state = FakeState(config, storage)
            original_state = getattr(DemoMvpHandler, "state", None)
            DemoMvpHandler.state = state
            server = ThreadingHTTPServer(("127.0.0.1", 0), DemoMvpHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = server.server_address
                https_connection = HTTPConnection(host, port, timeout=3)
                https_connection.request("POST", "/api/demo-login", body="", headers={"X-Forwarded-Proto": "https"})
                https_response = https_connection.getresponse()
                https_payload = json.loads(https_response.read().decode("utf-8"))
                https_cookie = https_response.getheader("Set-Cookie") or ""
                https_connection.close()

                local_connection = HTTPConnection(host, port, timeout=3)
                local_connection.request("POST", "/api/demo-login", body="")
                local_response = local_connection.getresponse()
                local_payload = json.loads(local_response.read().decode("utf-8"))
                local_cookie = local_response.getheader("Set-Cookie") or ""
                local_connection.close()

                self.assertEqual(https_response.status, 200)
                self.assertTrue(https_payload["ok"])
                self.assertIn("Secure", https_cookie)
                self.assertEqual(local_response.status, 200)
                self.assertTrue(local_payload["ok"])
                self.assertNotIn("Secure", local_cookie)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
                if original_state is not None:
                    DemoMvpHandler.state = original_state

    def test_demo_login_consumes_json_body_before_keep_alive_next_request(self) -> None:
        class FakeState:
            def __init__(self, config: AppConfig, storage: Storage):
                self.config = config
                self.storage = storage

        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            state = FakeState(config, storage)
            original_state = getattr(DemoMvpHandler, "state", None)
            DemoMvpHandler.state = state
            server = ThreadingHTTPServer(("127.0.0.1", 0), DemoMvpHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = server.server_address
                connection = HTTPConnection(host, port, timeout=3)
                connection.request(
                    "POST",
                    "/api/demo-login",
                    body="{}",
                    headers={"Content-Type": "application/json"},
                )
                login_response = connection.getresponse()
                login_payload = json.loads(login_response.read().decode("utf-8"))
                cookie = (login_response.getheader("Set-Cookie") or "").split(";", 1)[0]

                connection.request("GET", "/api/sessions", headers={"Cookie": cookie})
                sessions_response = connection.getresponse()
                sessions_payload = json.loads(sessions_response.read().decode("utf-8"))
                connection.close()

                self.assertEqual(login_response.status, 200)
                self.assertTrue(login_payload["ok"])
                self.assertEqual(sessions_response.status, 200)
                self.assertTrue(sessions_payload["ok"])
                self.assertIn("sessions", sessions_payload)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
                if original_state is not None:
                    DemoMvpHandler.state = original_state
                else:
                    delattr(DemoMvpHandler, "state")

    def test_mvp_base_path_mount_routes_assets_api_and_cookie_path(self) -> None:
        class FakeState:
            def __init__(self, config: AppConfig, storage: Storage):
                self.config = config
                self.storage = storage

        with tempfile.TemporaryDirectory() as tmp:
            config = replace(make_test_config(Path(tmp) / "demo.sqlite", api_key=""), app_base_path="/mvp")
            storage = Storage(config.sqlite_db_path)
            state = FakeState(config, storage)
            original_state = getattr(DemoMvpHandler, "state", None)
            DemoMvpHandler.state = state
            server = ThreadingHTTPServer(("127.0.0.1", 0), DemoMvpHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = server.server_address
                connection = HTTPConnection(host, port, timeout=3)

                connection.request("GET", "/mvp")
                index_response = connection.getresponse()
                index_html = index_response.read().decode("utf-8")

                connection.request("GET", "/")
                root_response = connection.getresponse()
                root_response.read()

                connection.request("GET", "/mvp/static/app.js")
                static_response = connection.getresponse()
                static_source = static_response.read().decode("utf-8")

                connection.request("POST", "/mvp/api/demo-login", body="{}", headers={"Content-Type": "application/json"})
                login_response = connection.getresponse()
                login_payload = json.loads(login_response.read().decode("utf-8"))
                cookie_header = login_response.getheader("Set-Cookie") or ""
                cookie = cookie_header.split(";", 1)[0]

                connection.request("GET", "/mvp/api/sessions", headers={"Cookie": cookie})
                sessions_response = connection.getresponse()
                sessions_payload = json.loads(sessions_response.read().decode("utf-8"))

                connection.request("POST", "/mvp/api/logout", body="{}", headers={"Cookie": cookie})
                logout_response = connection.getresponse()
                logout_payload = json.loads(logout_response.read().decode("utf-8"))
                logout_cookie_header = logout_response.getheader("Set-Cookie") or ""

                connection.request("GET", "/api/sessions", headers={"Cookie": cookie})
                root_api_response = connection.getresponse()
                root_api_response.read()
                connection.close()

                self.assertEqual(index_response.status, 200)
                self.assertIn('href="/mvp/static/styles.css"', index_html)
                self.assertIn('window.__MVP_BASE_PATH__ = "/mvp";', index_html)
                self.assertIn('src="/mvp/static/app.js"', index_html)
                self.assertEqual(root_response.status, 404)
                self.assertEqual(static_response.status, 200)
                self.assertIn("function appPath(path)", static_source)
                self.assertEqual(login_response.status, 200)
                self.assertTrue(login_payload["ok"])
                self.assertIn("Path=/mvp", cookie_header)
                self.assertIn("Path=/; Max-Age=0", cookie_header)
                self.assertEqual(sessions_response.status, 200)
                self.assertTrue(sessions_payload["ok"])
                self.assertEqual(logout_response.status, 200)
                self.assertTrue(logout_payload["ok"])
                self.assertIn("Path=/mvp; Max-Age=0", logout_cookie_header)
                self.assertIn("Path=/; Max-Age=0", logout_cookie_header)
                self.assertEqual(root_api_response.status, 404)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
                if original_state is not None:
                    DemoMvpHandler.state = original_state
                else:
                    delattr(DemoMvpHandler, "state")

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
                config = make_test_config(Path(tmp) / "demo.sqlite", api_key="fake-key")
                GeminiAdapter(config).call("assembled context", STRUCTURED_OUTPUT_SCHEMA)
        finally:
            urllib.request.urlopen = original_urlopen  # type: ignore[assignment]

        generation_config = captured["payload"]["generationConfig"]
        self.assertEqual(generation_config["responseMimeType"], "application/json")
        self.assertEqual(generation_config["responseJsonSchema"]["type"], "object")
        self.assertIn("user_answer", generation_config["responseJsonSchema"]["properties"])

    def test_gemini_stt_adapter_sends_inline_audio_payload(self) -> None:
        captured: dict[str, Any] = {}

        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: Any) -> None:
                return None

            def read(self) -> bytes:
                body = {"candidates": [{"content": {"parts": [{"text": "200 грамм курицы"}]}}]}
                return json.dumps(body).encode("utf-8")

        original_urlopen = urllib.request.urlopen

        def fake_urlopen(request: urllib.request.Request, timeout: int = 0) -> FakeResponse:
            captured["payload"] = json.loads(request.data.decode("utf-8"))  # type: ignore[union-attr]
            captured["headers"] = dict(request.header_items())
            captured["timeout"] = timeout
            return FakeResponse()

        try:
            urllib.request.urlopen = fake_urlopen  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp:
                config = make_test_config(Path(tmp) / "demo.sqlite", api_key="fake-key")
                result = GeminiSttAdapter(config).transcribe(b"RIFFfakewav", "audio/wav", duration_ms=1000)
        finally:
            urllib.request.urlopen = original_urlopen  # type: ignore[assignment]

        self.assertTrue(result.ok)
        self.assertEqual(result.text, "200 грамм курицы")
        self.assertIn("audio/wav", SUPPORTED_STT_MIME_TYPES)
        parts = captured["payload"]["contents"][0]["parts"]
        self.assertIn("Предпочтительный язык транскрипта: русский.", parts[0]["text"])
        self.assertIn("Предпочтительный алфавит/скрипт: кириллица.", parts[0]["text"])
        self.assertIn("iiko, r_keeper, StoreHouse, HACCP", parts[0]["text"])
        self.assertEqual(parts[1]["inlineData"]["mimeType"], "audio/wav")
        self.assertTrue(parts[1]["inlineData"]["data"])
        self.assertEqual(captured["timeout"], 5)

    def test_stt_mime_normalization_accepts_m4a_aliases(self) -> None:
        self.assertEqual(normalize_mime_type("audio/m4a"), "audio/mp4")
        self.assertEqual(normalize_mime_type("audio/x-m4a; codecs=mp4a.40.2"), "audio/mp4")
        self.assertIn("audio/mp4", SUPPORTED_STT_MIME_TYPES)

    def test_voice_transcription_policy_is_configurable_for_batch_and_live(self) -> None:
        config = make_test_config(Path("unused.sqlite"), api_key="fake-key")
        custom = replace(
            config,
            voice_transcription_language="русский язык",
            voice_transcription_script="кириллица",
            voice_transcription_latin_allowlist="iiko, SKU-42",
            voice_transcription_domain_terms="нетто, выход",
            voice_transcription_extra_instruction="Не заменяй проценты словами.",
        )

        batch_prompt = build_batch_transcription_prompt(custom)
        live_prompt = build_live_voice_transcription_instruction(custom)

        self.assertIn("русский язык", batch_prompt)
        self.assertIn("кириллица", batch_prompt)
        self.assertIn("iiko, SKU-42", batch_prompt)
        self.assertIn("нетто, выход", batch_prompt)
        self.assertIn("Не заменяй проценты словами.", live_prompt)
        self.assertIn("черновик сообщения в чат", live_prompt)
        self.assertNotIn("Верни только текст транскрипта.", live_prompt)

        override = replace(config, voice_transcription_prompt_override="FULL CUSTOM PROMPT")
        self.assertEqual(build_batch_transcription_prompt(override), "FULL CUSTOM PROMPT")
        self.assertEqual(build_live_voice_transcription_instruction(override), "FULL CUSTOM PROMPT")

    def test_runtime_transcribe_audio_validates_limits_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="fake-key")
            config = AppConfig(**{**config.__dict__, "stt_max_audio_bytes": 4})
            storage = Storage(config.sqlite_db_path)
            user = storage.ensure_demo_user()
            runtime = DemoRuntime(config, storage)

            oversized = runtime.transcribe_audio(user, b"12345", "audio/wav", duration_ms=1000)
            unsupported = runtime.transcribe_audio(user, b"123", "audio/webm", duration_ms=1000)
            too_long = runtime.transcribe_audio(user, b"123", "audio/wav", duration_ms=181000)

        self.assertFalse(oversized["ok"])
        self.assertEqual(oversized["status"], 413)
        self.assertFalse(unsupported["ok"])
        self.assertEqual(unsupported["status"], 415)
        self.assertFalse(too_long["ok"])
        self.assertEqual(too_long["status"], 413)

    def test_live_voice_proxy_websocket_framing_preserves_payload(self) -> None:
        masked = build_websocket_frame(
            b'{"setup":{}}',
            opcode=0x1,
            mask=True,
            mask_key=b"\x01\x02\x03\x04",
        )
        browser_frame = read_websocket_frame(io.BytesIO(masked), expect_masked=True)

        self.assertEqual(browser_frame.payload, b'{"setup":{}}')
        self.assertEqual(browser_frame.opcode, 0x1)
        self.assertTrue(browser_frame.masked)

        unmasked = build_websocket_frame(browser_frame.payload, opcode=browser_frame.opcode, mask=False)
        upstream_frame = read_websocket_frame(io.BytesIO(unmasked), expect_masked=False)

        self.assertEqual(upstream_frame.payload, b'{"setup":{}}')
        self.assertFalse(upstream_frame.masked)
        self.assertEqual(websocket_accept_value("dGhlIHNhbXBsZSBub25jZQ=="), "s3pPLMBiTxaQ9kYGzzhZRbK+xOo=")

    def test_live_voice_proxy_uses_socks5_auth_for_upstream_websocket(self) -> None:
        def recv_exact(sock: socket.socket, size: int) -> bytes:
            chunks = bytearray()
            while len(chunks) < size:
                chunk = sock.recv(size - len(chunks))
                if not chunk:
                    raise AssertionError("socket closed")
                chunks.extend(chunk)
            return bytes(chunks)

        requested: dict[str, Any] = {}
        errors: list[BaseException] = []
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        server_sock.listen(1)
        proxy_host, proxy_port = server_sock.getsockname()

        def fake_socks5_proxy() -> None:
            client: socket.socket | None = None
            try:
                server_sock.settimeout(5)
                client, _addr = server_sock.accept()
                client.settimeout(5)
                greeting = recv_exact(client, 4)
                self.assertEqual(greeting, b"\x05\x02\x00\x02")
                client.sendall(b"\x05\x02")
                auth_version = recv_exact(client, 1)
                username = recv_exact(client, recv_exact(client, 1)[0])
                password = recv_exact(client, recv_exact(client, 1)[0])
                self.assertEqual(auth_version, b"\x01")
                self.assertEqual(username, b"proxy-user")
                self.assertEqual(password, b"proxy-pass")
                client.sendall(b"\x01\x00")

                header = recv_exact(client, 4)
                self.assertEqual(header[:3], b"\x05\x01\x00")
                self.assertEqual(header[3], 0x03)
                host = recv_exact(client, recv_exact(client, 1)[0]).decode("ascii")
                port = int.from_bytes(recv_exact(client, 2), "big")
                requested["host"] = host
                requested["port"] = port
                client.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")

                request = bytearray()
                while b"\r\n\r\n" not in request:
                    request.extend(recv_exact(client, 1))
                request_text = bytes(request).decode("iso-8859-1")
                self.assertIn("GET /ws/live?access_token=test HTTP/1.1", request_text)
                key_line = next(line for line in request_text.split("\r\n") if line.lower().startswith("sec-websocket-key:"))
                accept = websocket_accept_value(key_line.split(":", 1)[1].strip())
                client.sendall(
                    (
                        "HTTP/1.1 101 Switching Protocols\r\n"
                        "Upgrade: websocket\r\n"
                        "Connection: Upgrade\r\n"
                        f"Sec-WebSocket-Accept: {accept}\r\n"
                        "\r\n"
                    ).encode("ascii")
                )
            except BaseException as exc:
                errors.append(exc)
            finally:
                if client is not None:
                    client.close()

        thread = threading.Thread(target=fake_socks5_proxy, daemon=True)
        thread.start()
        try:
            config = make_test_config(Path("unused.sqlite"), api_key="fake-key")
            config = AppConfig(
                **{
                    **config.__dict__,
                    "live_voice_transport": "server_proxy",
                    "live_voice_socks5_host": proxy_host,
                    "live_voice_socks5_port": proxy_port,
                    "live_voice_socks5_username": "proxy-user",
                    "live_voice_socks5_password": "proxy-pass",
                }
            )
            upstream = connect_gemini_live_websocket("ws://gemini.example/ws/live?access_token=test", config)
            upstream.sock.close()
            thread.join(timeout=3)
        finally:
            server_sock.close()

        if errors:
            raise errors[0]
        self.assertEqual(requested, {"host": "gemini.example", "port": 80})

    def test_live_voice_factory_and_anti_drift_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="fake-key")
            adapter = make_live_voice_adapter(config)

        self.assertIsInstance(adapter, GeminiLiveVoiceAdapter)
        self.assertIn("make_live_voice_adapter", FACTORY_REQUIRED)
        self.assertIn("DO_NOT_CALL_GEMINI_LIVE_TOKEN_ENDPOINT", FORBIDDEN)
        main_source = (REPO_ROOT / "app" / "main.py").read_text(encoding="utf-8")
        self.assertNotIn("/v1alpha/auth_tokens", main_source)

    def test_voice_ui_keeps_batch_and_live_visual_contracts(self) -> None:
        js_source = (REPO_ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (REPO_ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("Sticky Voice UI contract", js_source)
        self.assertIn("currentVoiceUiMode", js_source)
        self.assertIn('classList.toggle("voice-live"', js_source)
        self.assertIn('classList.toggle("voice-batch"', js_source)
        self.assertIn("voiceBtn.dataset.voiceMode", js_source)
        self.assertIn(".voice-btn.voice-live.streaming .voice-pulse", css_source)
        self.assertIn(".voice-btn.voice-batch.recording", css_source)
        self.assertNotIn("server_proxy", js_source)
        self.assertNotIn("SOCKS5", js_source)

    def test_chat_send_uses_optimistic_typing_contract(self) -> None:
        js_source = (REPO_ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (REPO_ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("Sticky chat turn UI contract", js_source)
        self.assertIn("appendOptimisticChatTurn", js_source)
        self.assertIn('appendMessageBubble("user", text, {pending: true})', js_source)
        self.assertIn('appendMessageBubble("assistant", "", {pending: true, typing: true})', js_source)
        self.assertIn('aria-label", "Ассистент печатает"', js_source)
        self.assertIn(".typing-dots", css_source)
        self.assertIn("@keyframes typing-dot", css_source)
        self.assertNotIn("Формирую ответ", js_source)
        self.assertNotIn("Формирую ответ", css_source)

    def test_chat_renders_markdown_only_for_assistant_output(self) -> None:
        index_source = (REPO_ROOT / "app" / "templates" / "index.html").read_text(encoding="utf-8")
        js_source = (REPO_ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (REPO_ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertLess(index_source.index("/static/vendor/markdown-it.min.js"), index_source.index("/static/app.js"))
        self.assertTrue((REPO_ROOT / "app" / "static" / "vendor" / "markdown-it.min.js").exists())
        self.assertTrue((REPO_ROOT / "app" / "static" / "vendor" / "markdown-it.LICENSE.txt").exists())
        self.assertIn("createChatMarkdownRenderer", js_source)
        self.assertIn("window.markdownit", js_source)
        self.assertIn("html: false", js_source)
        self.assertIn("linkify: false", js_source)
        self.assertIn("md.renderer.rules.image", js_source)
        self.assertIn("md.utils.escapeHtml", js_source)
        self.assertIn("md.validateLink = isSafeMarkdownUrl", js_source)
        self.assertIn('compact.startsWith("javascript:")', js_source)
        self.assertIn('token.attrSet("rel", "noopener noreferrer")', js_source)
        self.assertRegex(js_source, r'else if \(role === "assistant"\) \{\s+renderAssistantMarkdown\(node, content\);\s+\} else \{\s+node\.textContent = content;')
        self.assertIn(".message.markdown-body", css_source)
        self.assertIn(".markdown-body pre", css_source)
        self.assertIn(".markdown-body table", css_source)

    def test_live_voice_server_proxy_token_route_hides_gemini_token(self) -> None:
        class FakeRuntime:
            def create_live_voice_token(self, _user: Any) -> dict[str, Any]:
                return {
                    "ok": True,
                    "provider": "gemini",
                    "model": "gemini-3.1-flash-live-preview",
                    "token": "auth_tokens/test-token",
                    "websocket_url": "wss://generativelanguage.googleapis.com/ws/test?access_token=secret",
                    "setup": {"model": "models/gemini-3.1-flash-live-preview"},
                    "input_sample_rate": 16000,
                    "max_audio_seconds": 180,
                }

        class FakeState:
            def __init__(self, config: AppConfig, storage: Storage):
                self.config = config
                self.storage = storage
                self.runtime = FakeRuntime()
                self.live_voice_sessions: dict[str, dict[str, Any]] = {}
                self.live_voice_sessions_lock = threading.Lock()

        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="fake-key")
            config = AppConfig(
                **{
                    **config.__dict__,
                    "app_base_path": "/mvp",
                    "live_voice_transport": "server_proxy",
                    "live_voice_socks5_host": "127.0.0.10",
                    "live_voice_socks5_username": "proxy-user",
                    "live_voice_socks5_password": "proxy-pass",
                }
            )
            storage = Storage(config.sqlite_db_path)
            user = storage.ensure_demo_user()
            raw_token = session_token()
            storage.create_auth_session(raw_token, user.id)
            cookie = sign_cookie(raw_token, config.auth_session_secret).value
            state = FakeState(config, storage)
            original_state = getattr(DemoMvpHandler, "state", None)
            DemoMvpHandler.state = state
            server = ThreadingHTTPServer(("127.0.0.1", 0), DemoMvpHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = server.server_address
                headers = {
                    "Cookie": f"{COOKIE_NAME}={cookie}",
                    "Content-Type": "application/json",
                }
                connection = HTTPConnection(host, port, timeout=3)
                connection.request("POST", "/mvp/api/live-voice/token", body="{}", headers=headers)
                response = connection.getresponse()
                payload = json.loads(response.read().decode("utf-8"))

                self.assertEqual(response.status, 200)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["transport"], "server_proxy")
                self.assertNotIn("token", payload)
                self.assertTrue(payload["websocket_url"].startswith(f"ws://{host}:{port}/mvp/api/live-voice/ws/"))
                self.assertEqual(len(state.live_voice_sessions), 1)
                session = next(iter(state.live_voice_sessions.values()))
                self.assertEqual(session["user_id"], user.id)
                self.assertIn("access_token=secret", session["websocket_url"])

                connection.request("POST", "/mvp/api/live-voice/token", body="{}", headers=headers)
                second_response = connection.getresponse()
                second_payload = json.loads(second_response.read().decode("utf-8"))
                connection.close()

                self.assertEqual(second_response.status, 200)
                self.assertTrue(second_payload["ok"])
                self.assertEqual(second_payload["transport"], "server_proxy")
                self.assertNotIn("token", second_payload)
                self.assertEqual(len(state.live_voice_sessions), 2)

                session_id = payload["websocket_url"].rsplit("/", 1)[-1]
                connection = HTTPConnection(host, port, timeout=3)
                connection.request("GET", f"/mvp/api/live-voice/ws/{session_id}", headers={"Cookie": f"{COOKIE_NAME}={cookie}"})
                invalid_upgrade = connection.getresponse()
                invalid_payload = json.loads(invalid_upgrade.read().decode("utf-8"))
                connection.close()

                self.assertEqual(invalid_upgrade.status, 400)
                self.assertFalse(invalid_payload["ok"])
                self.assertEqual(len(state.live_voice_sessions), 2)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
                if original_state is not None:
                    DemoMvpHandler.state = original_state
                else:
                    delattr(DemoMvpHandler, "state")

    def test_gemini_live_voice_adapter_creates_constrained_ephemeral_token(self) -> None:
        captured: dict[str, Any] = {}

        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: Any) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps({"name": "auth_tokens/test-token"}).encode("utf-8")

        original_urlopen = urllib.request.urlopen

        def fake_urlopen(request: urllib.request.Request, timeout: int = 0) -> FakeResponse:
            captured["url"] = request.full_url
            captured["payload"] = json.loads(request.data.decode("utf-8"))  # type: ignore[union-attr]
            captured["headers"] = dict(request.header_items())
            captured["timeout"] = timeout
            return FakeResponse()

        try:
            urllib.request.urlopen = fake_urlopen  # type: ignore[assignment]
            with tempfile.TemporaryDirectory() as tmp:
                config = make_test_config(Path(tmp) / "demo.sqlite", api_key="fake-key")
                result = GeminiLiveVoiceAdapter(config).create_token()
        finally:
            urllib.request.urlopen = original_urlopen  # type: ignore[assignment]

        self.assertTrue(result.ok)
        self.assertEqual(result.token, "auth_tokens/test-token")
        self.assertIn("/v1alpha/auth_tokens", captured["url"])
        self.assertEqual(captured["headers"]["X-goog-api-key"], "fake-key")
        self.assertEqual(captured["timeout"], 5)
        payload = captured["payload"]
        self.assertEqual(payload["uses"], 1)
        setup = payload["bidiGenerateContentSetup"]
        self.assertEqual(setup["model"], "models/gemini-3.1-flash-live-preview")
        self.assertEqual(setup["generationConfig"]["responseModalities"], ["AUDIO"])
        self.assertEqual(setup["inputAudioTranscription"], {})
        instruction = setup["systemInstruction"]["parts"][0]["text"]
        self.assertIn("Предпочтительный язык транскрипта: русский.", instruction)
        self.assertIn("Предпочтительный алфавит/скрипт: кириллица.", instruction)
        self.assertIn("Не транслитерируй", instruction)
        self.assertIn("access_token=auth_tokens%2Ftest-token", result.websocket_url)

    def test_runtime_live_voice_token_returns_user_safe_error_for_missing_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_test_config(Path(tmp) / "demo.sqlite", api_key="")
            storage = Storage(config.sqlite_db_path)
            user = storage.ensure_demo_user()
            result = DemoRuntime(config, storage).create_live_voice_token(user)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 502)
        self.assertNotIn("admin_hint", {key: value for key, value in result.items() if value is not None})

    def test_live_voice_setup_enables_input_transcription(self) -> None:
        config = make_test_config(Path("unused.sqlite"), api_key="fake-key")
        setup = live_voice_setup(config)

        self.assertEqual(setup["model"], "models/gemini-3.1-flash-live-preview")
        self.assertEqual(setup["generationConfig"]["responseModalities"], ["AUDIO"])
        self.assertEqual(setup["inputAudioTranscription"], {})
        self.assertIn("realtimeInputConfig", setup)
        self.assertIn("Предпочтительный язык транскрипта: русский.", setup["systemInstruction"]["parts"][0]["text"])

    def test_structured_json_is_derived_when_draft_exists(self) -> None:
        normalized = normalize_structured_output(
            {
                "user_answer": "Проект готов.",
                "workflow_status": "draft_generation",
                "known_facts": [],
                "open_questions": [],
                "warnings": [],
                "data_statuses": [],
                "document_draft": {
                    "title": "Яичница",
                    "document_type": "ТК",
                    "project_status": "Проект, требует проверки",
                    "sections": [{"title": "Технология", "content": "Приготовить и подать сразу."}],
                },
                "structured_json": None,
                "next_step": "Проверить ответственным лицом.",
            }
        )
        self.assertIsInstance(normalized["structured_json"], dict)
        self.assertEqual(normalized["structured_json"]["integration_status"], "not_an_accounting_system_import_format")


if __name__ == "__main__":
    unittest.main()
