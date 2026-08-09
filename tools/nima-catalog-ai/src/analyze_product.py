"""Fase 1 — product analysis from manifest.json + product-brief.json + original images."""

from __future__ import annotations

import json
from pathlib import Path

from . import file_utils

PROMPT_NAME = "analyze-product.md"
SCHEMA_NAME = "product-analysis.schema.json"


def _load_brief(input_dir: Path) -> dict | None:
    brief_path = input_dir / "product-brief.json"
    if not brief_path.exists():
        return None
    return file_utils.read_json(brief_path)


def analyze_product(
    *,
    input_dir: Path,
    prompts_dir: Path,
    schemas_dir: Path,
    client,
    model: str,
) -> dict:
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found in {input_dir}")

    manifest = file_utils.read_json(manifest_path)
    brief = _load_brief(input_dir)
    images = file_utils.list_original_images(input_dir)
    if not images:
        raise FileNotFoundError(f"No original images found under {input_dir / 'original'}")

    system_prompt = (prompts_dir / PROMPT_NAME).read_text(encoding="utf-8")
    schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)

    user_payload = {
        "manifest": manifest,
        "product_brief": brief,
        "product_brief_present": brief is not None,
        "reference_image_filenames": [p.name for p in images],
    }
    user_text = (
        "Product sources follow as JSON, then the reference images in position order.\n\n"
        + json.dumps(user_payload, indent=2, ensure_ascii=False)
    )

    analysis = client.structured_json(
        model=model,
        system_prompt=system_prompt,
        user_text=user_text,
        image_paths=images,
        json_schema=schema,
        schema_name="product_analysis",
    )

    if brief is None and "product-brief.json missing" not in " ".join(analysis.get("unknowns", [])):
        analysis.setdefault("unknowns", []).append(
            "product-brief.json missing for this product — analysis is based on manifest.json and images only."
        )

    file_utils.validate_against_schema(analysis, schema)
    return analysis
