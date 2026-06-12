from __future__ import annotations

import json
import re
import shutil
from hashlib import sha256
from pathlib import Path
from typing import Any

from .contracts import ProviderImage


MIME_EXTENSIONS = {
    "image/png": ".png",
    "image/webp": ".webp",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
}


class LocalAssetStore:
    def __init__(self, root: Path):
        self.root = root

    def save_candidate(self, candidate: dict[str, Any], image: ProviderImage) -> dict[str, Any]:
        candidate_id = _safe_segment(str(candidate["id"]), "candidate id")
        candidate_dir = self.root / "candidates" / candidate_id
        candidate_dir.mkdir(parents=True, exist_ok=False)

        ext = MIME_EXTENSIONS.get(image.mime_type.lower(), ".bin")
        original_path = candidate_dir / f"original{ext}"
        original_path.write_bytes(image.data)

        stored = dict(candidate)
        stored.update(
            {
                "mimeType": image.mime_type,
                "originalPath": str(original_path),
                "metadataPath": str(candidate_dir / "metadata.json"),
                "sizeBytes": len(image.data),
                "checksum": sha256(image.data).hexdigest(),
            }
        )
        self._write_metadata(candidate_dir / "metadata.json", stored)
        return stored

    def list_candidates(self) -> list[dict[str, Any]]:
        candidates_dir = self.root / "candidates"
        if not candidates_dir.exists():
            return []
        rows: list[dict[str, Any]] = []
        for metadata_path in sorted(candidates_dir.glob("*/metadata.json")):
            rows.append(self._read_metadata(metadata_path))
        return rows

    def inspect_candidate(self, candidate_id: str) -> dict[str, Any]:
        candidate_id = _safe_segment(candidate_id, "candidate id")
        metadata_path = self.root / "candidates" / candidate_id / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Candidate not found: {candidate_id}")
        return self._read_metadata(metadata_path)

    def approve_candidate(self, candidate_id: str, asset_key: str, *, approved_by: str, approved_at: str) -> dict[str, Any]:
        candidate = self.inspect_candidate(candidate_id)
        validation = candidate.get("contractValidation")
        if isinstance(validation, dict) and not validation.get("ok", True):
            raise ValueError("Candidate violates visual asset contract and cannot be approved.")
        safe_asset_key = _safe_segment(asset_key, "asset key")
        source = Path(str(candidate["originalPath"]))
        if not source.exists():
            raise FileNotFoundError(f"Candidate original file not found: {source}")

        approved_dir = self.root / "approved" / safe_asset_key / "v1"
        approved_dir.mkdir(parents=True, exist_ok=True)
        target = approved_dir / source.name
        shutil.copy2(source, target)

        approved = dict(candidate)
        approved.update(
            {
                "status": "approved",
                "approvalStatus": "approved",
                "targetAssetKey": asset_key,
                "approvedBy": approved_by,
                "approvedAt": approved_at,
                "approvedOriginalPath": str(target),
                "approvedMetadataPath": str(approved_dir / "metadata.json"),
            }
        )
        self._write_metadata(approved_dir / "metadata.json", approved)
        self._write_metadata(Path(str(candidate["metadataPath"])), approved)
        return approved

    @staticmethod
    def _read_metadata(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_metadata(path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_segment(value: str, label: str) -> str:
    if not value or not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise ValueError(f"Invalid {label}.")
    if "/" in value or "\\" in value or value in {".", ".."}:
        raise ValueError(f"Invalid {label}.")
    return value
