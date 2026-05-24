from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ContextLayer:
    order: int
    file: str
    role: str
    source: str
    status: str
    description: str
    text: str


@dataclass(frozen=True)
class ContextPack:
    manifest_path: str
    version: str
    purpose: str
    layers: list[ContextLayer]

    def static_text(self) -> str:
        parts: list[str] = []
        for layer in self.layers:
            parts.append(
                "\n".join(
                    [
                        f"## Context layer {layer.order}: {layer.file}",
                        f"role: {layer.role}",
                        f"source: {layer.source}",
                        f"status: {layer.status}",
                        layer.text.strip(),
                    ]
                )
            )
        return "\n\n".join(parts)

    def public_layers(self, include_text: bool = False) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for layer in self.layers:
            item: dict[str, Any] = {
                "order": layer.order,
                "file": layer.file,
                "role": layer.role,
                "source": layer.source,
                "status": layer.status,
                "description": layer.description,
            }
            if include_text:
                item["text"] = layer.text
            result.append(item)
        return result


class ContextLoadError(RuntimeError):
    pass


def _strip_quotes(value: str) -> str:
    return value.strip().strip('"').strip("'")


def _parse_simple_manifest(text: str) -> dict[str, Any]:
    version = ""
    purpose = ""
    layers: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            if key == "version":
                version = _strip_quotes(value)
            elif key == "purpose":
                purpose = _strip_quotes(value)
            continue
        if stripped.startswith("- "):
            if current:
                layers.append(current)
            current = {}
            body = stripped[2:]
            if ":" in body:
                key, value = body.split(":", 1)
                current[key.strip()] = _strip_quotes(value)
            continue
        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = _strip_quotes(value)
    if current:
        layers.append(current)
    return {"version": version, "purpose": purpose, "layers": layers}


class ContextLoader:
    def __init__(self, manifest_path: Path, layers_dir: Path):
        self.manifest_path = manifest_path
        self.layers_dir = layers_dir

    def load(self) -> ContextPack:
        if not self.manifest_path.exists():
            raise ContextLoadError(f"Context manifest not found: {self.manifest_path}")
        manifest = _parse_simple_manifest(self.manifest_path.read_text(encoding="utf-8"))
        layers: list[ContextLayer] = []
        for raw_layer in manifest["layers"]:
            file_name = str(raw_layer.get("file", ""))
            if not file_name:
                raise ContextLoadError("Context layer without file in manifest.")
            layer_path = self.layers_dir / file_name
            if not layer_path.exists():
                raise ContextLoadError(f"Context layer not found: {layer_path}")
            try:
                order = int(raw_layer.get("order", len(layers)))
            except ValueError as exc:
                raise ContextLoadError(f"Invalid layer order for {file_name}.") from exc
            layers.append(
                ContextLayer(
                    order=order,
                    file=file_name,
                    role=str(raw_layer.get("role", "")),
                    source=str(raw_layer.get("source", "")),
                    status=str(raw_layer.get("status", "")),
                    description=str(raw_layer.get("description", "")),
                    text=layer_path.read_text(encoding="utf-8"),
                )
            )
        layers.sort(key=lambda layer: layer.order)
        return ContextPack(
            manifest_path=str(self.manifest_path),
            version=str(manifest.get("version", "")),
            purpose=str(manifest.get("purpose", "")),
            layers=layers,
        )
