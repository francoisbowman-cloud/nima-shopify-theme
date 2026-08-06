"""Fase 4 — fidelity gate. Never lets the model auto-approve an in-use image or
auto-decide a Shopify-facing outcome; approved_candidate always means
"eligible for human review", nothing more.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import file_utils

PROMPT_NAME = "fidelity-review.md"
SCHEMA_NAME = "fidelity-report.schema.json"


def evaluate_candidate(
    *,
    handle: str,
    output_type: str,
    candidate_path: Path,
    analysis: dict,
    plan_entry: dict,
    input_dir: Path,
    prompts_dir: Path,
    schemas_dir: Path,
    client,
    model: str,
) -> dict:
    system_prompt = (prompts_dir / PROMPT_NAME).read_text(encoding="utf-8")
    schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)

    reference_images = file_utils.list_original_images(input_dir)
    user_payload = {
        "handle": handle,
        "output_type": output_type,
        "product_analysis": analysis,
        "generation_plan_entry": plan_entry,
        "candidate_file": candidate_path.name,
    }
    user_text = (
        "Original reference images first, then the generated candidate (last image). "
        "Context JSON follows.\n\n" + json.dumps(user_payload, indent=2, ensure_ascii=False)
    )

    report = client.structured_json(
        model=model,
        system_prompt=system_prompt,
        user_text=user_text,
        image_paths=[*reference_images, candidate_path],
        json_schema=schema,
        schema_name="fidelity_report",
    )

    report.setdefault("handle", handle)
    report.setdefault("output_type", output_type)
    report.setdefault("candidate_file", candidate_path.name)

    # Hard policy clamp — never trust the model alone on the "never auto-approve
    # in-use" and "never auto-approve Shopify publication" rules from FASE 4.
    if output_type == "in-use" and report.get("decision") == "approved_candidate":
        report["decision"] = "review"
        report.setdefault("uncertain_features", []).append(
            "in-use output — decision forced to review; this output type is never auto-approved."
        )

    file_utils.validate_against_schema(report, schema)
    return report


def state_for_decision(decision: str) -> str:
    """Map a fidelity decision straight to a run-manifest output state.

    The orchestrator (cli.py) decides separately whether a "rejected" result
    gets a retry — this only names what the last attempt's outcome was.
    """
    mapping = {
        "approved_candidate": "approved_candidate",
        "review": "review",
        "reject": "rejected",
    }
    try:
        return mapping[decision]
    except KeyError as exc:
        raise ValueError(f"Unknown fidelity decision: {decision}") from exc
