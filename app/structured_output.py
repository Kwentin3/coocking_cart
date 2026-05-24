from __future__ import annotations

import json
import re
from typing import Any


STRUCTURED_OUTPUT_FIELDS = [
    "user_answer",
    "workflow_status",
    "known_facts",
    "open_questions",
    "warnings",
    "data_statuses",
    "document_draft",
    "structured_json",
    "next_step",
]


STRUCTURED_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "user_answer": {
            "type": "string",
            "description": "Russian user-facing chat answer. It can ask clarifying questions or summarize the draft.",
        },
        "workflow_status": {
            "type": "string",
            "description": "Current workflow stage, for example idea_received, format_clarification, draft_generation, review_required.",
        },
        "known_facts": {
            "type": "array",
            "description": "Known or confirmed facts from the dialogue.",
            "items": {"type": "string"},
        },
        "open_questions": {
            "type": "array",
            "description": "Questions that must be clarified before the next step.",
            "items": {"type": "string"},
        },
        "warnings": {
            "type": "array",
            "description": "Warnings about unconfirmed data, demo limitations, storage, losses, or legal/project status.",
            "items": {"type": "string"},
        },
        "data_statuses": {
            "type": "array",
            "description": "Important data statuses.",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "confirmed_by_user",
                            "calculated_by_system",
                            "from_reference",
                            "needs_review",
                            "needs_production_test",
                            "missing",
                        ],
                    },
                    "comment": {"type": "string"},
                },
                "required": ["field", "status", "comment"],
            },
        },
        "document_draft": {
            "type": ["object", "null"],
            "description": "Draft ТК/ТТК object, or null if the draft is not ready.",
            "properties": {
                "title": {"type": "string"},
                "document_type": {"type": "string"},
                "project_status": {"type": "string"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["title", "content"],
                    },
                },
            },
        },
        "structured_json": {
            "type": ["object", "null"],
            "description": "Neutral machine-readable representation for future integrations, or null if draft is not ready.",
        },
        "next_step": {
            "type": "string",
            "description": "Logical next action in Russian.",
        },
    },
    "required": [
        "user_answer",
        "workflow_status",
        "known_facts",
        "open_questions",
        "warnings",
        "data_statuses",
        "document_draft",
        "structured_json",
        "next_step",
    ],
}


TURN_TASK_INSTRUCTION = """
Continue the current turn using the supplied markdown context, dialogue history, and latest user message.
Do not use this text for output formatting; the provider adapter supplies the structured output schema separately.
"""


def empty_structured_output(user_answer: str, *, workflow_status: str = "error") -> dict[str, Any]:
    return {
        "user_answer": user_answer,
        "workflow_status": workflow_status,
        "known_facts": [],
        "open_questions": [],
        "warnings": [],
        "data_statuses": [],
        "document_draft": None,
        "structured_json": None,
        "next_step": "",
    }


def normalize_structured_output(value: dict[str, Any]) -> dict[str, Any]:
    normalized = empty_structured_output("", workflow_status=str(value.get("workflow_status") or "in_progress"))
    for field in STRUCTURED_OUTPUT_FIELDS:
        if field in value:
            normalized[field] = value[field]
    if not isinstance(normalized["user_answer"], str) or not normalized["user_answer"].strip():
        normalized["user_answer"] = "Не удалось получить понятный ответ ассистента."
    for list_field in ["known_facts", "open_questions", "warnings", "data_statuses"]:
        if normalized[list_field] is None:
            normalized[list_field] = []
        elif not isinstance(normalized[list_field], list):
            normalized[list_field] = [normalized[list_field]]
    if isinstance(normalized["document_draft"], dict) and not normalized["structured_json"]:
        normalized["structured_json"] = structured_json_from_draft(normalized["document_draft"])
    return normalized


def structured_json_from_draft(document_draft: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "demo_mvp_neutral_tech_card_v0.1",
        "integration_status": "not_an_accounting_system_import_format",
        "title": document_draft.get("title", ""),
        "document_type": document_draft.get("document_type", ""),
        "project_status": document_draft.get("project_status", "Проект, требует проверки"),
        "sections": document_draft.get("sections", []),
    }


def _extract_json(text: str) -> str:
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
    if fence:
        return fence.group(1)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


def parse_structured_output(text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        parsed = json.loads(_extract_json(text))
        if not isinstance(parsed, dict):
            return None, "Structured output is not a JSON object."
        return normalize_structured_output(parsed), None
    except json.JSONDecodeError as exc:
        return None, f"Structured output parse error: {exc.msg}"
