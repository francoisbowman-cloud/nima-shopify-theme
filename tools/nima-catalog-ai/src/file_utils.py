"""Local filesystem helpers: hashing, JSON I/O, schema validation, output containment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_schema(schemas_dir: Path, name: str) -> dict:
    return read_json(schemas_dir / name)


def validate_against_schema(data: dict, schema: dict) -> None:
    jsonschema.validate(instance=data, schema=schema)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_of_inputs(manifest_path: Path, brief_path: Path | None, image_paths: list[Path]) -> str:
    """Stable hash of everything that defines a product's input state.

    Used for idempotency: if this hash is unchanged between runs, existing
    outputs are reused unless --force is passed.
    """
    hasher = hashlib.sha256()
    hasher.update(manifest_path.read_bytes())
    if brief_path is not None and brief_path.exists():
        hasher.update(brief_path.read_bytes())
    for image_path in sorted(image_paths):
        hasher.update(image_path.name.encode("utf-8"))
        hasher.update(sha256_file(image_path).encode("utf-8"))
    return hasher.hexdigest()


def sha256_of_json(data: Any) -> str:
    """Stable hash of a JSON-serializable value — order-independent for dict keys."""
    return sha256_bytes(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def list_original_images(input_dir: Path) -> list[Path]:
    original_dir = input_dir / "original"
    if not original_dir.is_dir():
        return []
    return sorted(
        p for p in original_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def ensure_within(base_dir: Path, target: Path) -> Path:
    """Resolve `target` and raise if it would escape `base_dir`.

    Guards against any accidental path traversal when writing pipeline
    outputs (tests #11 rely on this).
    """
    base_resolved = base_dir.resolve()
    target_resolved = target.resolve()
    if base_resolved != target_resolved and base_resolved not in target_resolved.parents:
        raise ValueError(f"Refusing to write outside {base_resolved}: {target_resolved}")
    return target_resolved
