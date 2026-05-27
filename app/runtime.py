from __future__ import annotations

from typing import Any

from .config import AppConfig
from .context_loader import ContextLoader, ContextPack
from .live_voice import make_live_voice_adapter
from .llm import GeminiAdapter
from .stt import SUPPORTED_STT_MIME_TYPES, make_stt_adapter, normalize_mime_type
from .storage import Storage, User, estimate_tokens, utc_now
from .structured_output import STRUCTURED_OUTPUT_SCHEMA, TURN_TASK_INSTRUCTION, empty_structured_output, parse_structured_output


class DemoRuntime:
    def __init__(self, config: AppConfig, storage: Storage):
        self.config = config
        self.storage = storage
        self.context_loader = ContextLoader(config.context_manifest_path, config.context_layers_dir)
        self.llm_adapter = GeminiAdapter(config)
        self.stt_adapter = make_stt_adapter(config)
        self.live_voice_adapter = make_live_voice_adapter(config)

    def load_context_pack(self) -> ContextPack:
        return self.context_loader.load()

    def assemble_context_window(
        self,
        context_pack: ContextPack,
        history: list[dict[str, Any]],
        last_user_message: str,
    ) -> tuple[str, dict[str, Any]]:
        history_text = "\n".join(f"{item['role']}: {item['content']}" for item in history)
        assembled = "\n\n".join(
            [
                "# Static markdown context pack",
                context_pack.static_text(),
                "# Dialogue history",
                history_text or "История диалога пока пуста.",
                "# Last user message",
                last_user_message,
                "# Task instruction",
                TURN_TASK_INSTRUCTION.strip(),
            ]
        )
        trace_base = {
            "session_id": None,
            "turn_id": None,
            "context_manifest": {
                "path": context_pack.manifest_path,
                "version": context_pack.version,
                "purpose": context_pack.purpose,
            },
            "context_layers": context_pack.public_layers(include_text=False),
            "history_count": len(history),
            "last_user_message": last_user_message,
            "structured_output_schema": STRUCTURED_OUTPUT_SCHEMA,
            "assembled_context_preview": assembled[:8000],
            "timestamp": utc_now(),
        }
        return assembled, trace_base

    def process_user_message(self, session_id: int, user: User, message: str) -> dict[str, Any]:
        if not self.storage.can_access_session(session_id, user):
            return {"ok": False, "error": "Нет доступа к сессии."}

        user_message_id = self.storage.add_message(session_id, "user", message)
        history = [item for item in self.storage.list_messages(session_id, limit=10) if item["id"] != user_message_id]

        try:
            context_pack = self.load_context_pack()
            assembled_context, trace = self.assemble_context_window(context_pack, history, message)
        except Exception as exc:
            structured = empty_structured_output(
                "Контекст ассистента не собран. Администратор может посмотреть debug details.",
                workflow_status="context_error",
            )
            structured["warnings"] = ["Ошибка сборки context pack."]
            trace = {
                "session_id": session_id,
                "error": str(exc),
                "timestamp": utc_now(),
                "provider": self.config.llm_provider,
                "model": self.config.llm_model,
            }
            assistant_message_id = self.storage.add_message(session_id, "assistant", structured["user_answer"])
            turn_id = self.storage.save_turn_result(session_id, user_message_id, assistant_message_id, structured, trace)
            trace["turn_id"] = turn_id
            return {"ok": True, "structured_output": structured, "trace": self._trace_for_user(trace, user)}

        trace["session_id"] = session_id
        llm_result = self.llm_adapter.call(
            assembled_context,
            STRUCTURED_OUTPUT_SCHEMA,
            request_metadata={"session_id": session_id, "history_count": len(history)},
        )
        trace.update(
            {
                "provider": llm_result.provider,
                "model": llm_result.model,
                "llm_timestamp": llm_result.timestamp,
                "llm_ok": llm_result.ok,
                "llm_admin_hint": llm_result.admin_hint,
                "llm_metadata": llm_result.metadata or {},
            }
        )

        if not llm_result.ok:
            structured = empty_structured_output(
                "LLM сейчас не настроена или недоступна. Проверьте конфигурацию и повторите запрос.",
                workflow_status="llm_error",
            )
            structured["warnings"] = [llm_result.error or "Ошибка LLM provider."]
        else:
            parsed, parse_error = parse_structured_output(llm_result.text)
            if parsed is None:
                structured = empty_structured_output(
                    "Ассистент вернул ответ в неверном формате. Попробуйте повторить запрос.",
                    workflow_status="parse_error",
                )
                structured["warnings"] = ["Structured output parse error."]
                trace["parse_error"] = parse_error
                trace["raw_llm_text_preview"] = llm_result.text[:2000]
            else:
                structured = parsed

        assistant_message_id = self.storage.add_message(session_id, "assistant", structured["user_answer"])
        turn_id = self.storage.save_turn_result(session_id, user_message_id, assistant_message_id, structured, trace)
        trace["turn_id"] = turn_id
        return {
            "ok": True,
            "message": {"id": assistant_message_id, "role": "assistant", "content": structured["user_answer"]},
            "structured_output": structured,
            "trace": self._trace_for_user(trace, user),
        }

    def transcribe_audio(self, user: User, audio_bytes: bytes, mime_type: str, duration_ms: int) -> dict[str, Any]:
        if not self.config.stt_enabled:
            return {"ok": False, "error": "Голосовой ввод выключен.", "status": 503}
        if duration_ms <= 0:
            return {"ok": False, "error": "Длительность аудио не указана.", "status": 400}
        if duration_ms > self.config.stt_max_audio_seconds * 1000:
            return {"ok": False, "error": "Запись слишком длинная.", "status": 413}
        if not audio_bytes:
            return {"ok": False, "error": "Аудио пустое.", "status": 400}
        if len(audio_bytes) > self.config.stt_max_audio_bytes:
            return {"ok": False, "error": "Аудиофайл слишком большой.", "status": 413}
        normalized_mime = normalize_mime_type(mime_type)
        if normalized_mime not in SUPPORTED_STT_MIME_TYPES:
            return {"ok": False, "error": "Формат аудио не поддерживается.", "status": 415}

        result = self.stt_adapter.transcribe(audio_bytes, normalized_mime, duration_ms=duration_ms)
        if not result.ok:
            return {
                "ok": False,
                "error": result.error or "Не удалось распознать аудио.",
                "status": 502,
                "provider": result.provider,
                "model": result.model,
                "admin_hint": result.admin_hint if user.role == "admin" else None,
            }
        return {
            "ok": True,
            "text": result.text,
            "provider": result.provider,
            "model": result.model,
        }

    def create_live_voice_token(self, user: User) -> dict[str, Any]:
        if not self.config.live_voice_enabled:
            return {"ok": False, "error": "Потоковый голосовой ввод выключен.", "status": 503}

        result = self.live_voice_adapter.create_token()
        if not result.ok:
            return {
                "ok": False,
                "error": result.error or "Не удалось подготовить потоковый голосовой ввод.",
                "status": 502,
                "provider": result.provider,
                "model": result.model,
                "admin_hint": result.admin_hint if user.role == "admin" else None,
            }

        return {
            "ok": True,
            "provider": result.provider,
            "model": result.model,
            "token": result.token,
            "websocket_url": result.websocket_url,
            "setup": result.setup or {},
            "expires_at": result.expires_at,
            "new_session_expires_at": result.new_session_expires_at,
            "input_sample_rate": self.config.live_voice_input_sample_rate,
            "max_audio_seconds": self.config.stt_max_audio_seconds,
        }

    def context_inspector_payload(self, session_id: int, user: User) -> dict[str, Any]:
        if user.role != "admin":
            return {"ok": False, "error": "Context Inspector доступен только admin."}
        if not self.storage.can_access_session(session_id, user):
            return {"ok": False, "error": "Нет доступа к сессии."}
        context_pack = self.load_context_pack()
        latest_turn = self.storage.latest_turn_result(session_id)
        return {
            "ok": True,
            "manifest": {
                "path": context_pack.manifest_path,
                "version": context_pack.version,
                "purpose": context_pack.purpose,
            },
            "layers": context_pack.public_layers(include_text=True),
            "latest_turn": latest_turn,
            "messages": self.storage.list_messages(session_id),
        }

    def admin_context_payload(self, user: User) -> dict[str, Any]:
        if user.role != "admin":
            return {"ok": False, "error": "Context workspace доступен только admin."}
        context_pack = self.load_context_pack()
        static_context = context_pack.static_text()
        latest_turn = self.storage.latest_turn_result_any()
        return {
            "ok": True,
            "manifest": {
                "path": context_pack.manifest_path,
                "version": context_pack.version,
                "purpose": context_pack.purpose,
                "layer_count": len(context_pack.layers),
            },
            "layers": context_pack.public_layers(include_text=True),
            "static_context_preview": static_context,
            "static_context_estimated_tokens": estimate_tokens(static_context),
            "structured_output_schema": STRUCTURED_OUTPUT_SCHEMA,
            "latest_turn": latest_turn,
            "health": {
                "manifest_readable": True,
                "layers_loaded": len(context_pack.layers),
                "empty_layers": [layer.file for layer in context_pack.layers if not layer.text.strip()],
            },
            "token_policy": "provider_usage_when_available_otherwise_estimated_not_billing_usage",
        }

    @staticmethod
    def _trace_for_user(trace: dict[str, Any], user: User) -> dict[str, Any] | None:
        if user.role != "admin":
            return None
        safe_trace = dict(trace)
        safe_trace.pop("raw_env", None)
        return safe_trace
