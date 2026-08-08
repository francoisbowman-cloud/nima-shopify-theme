"""Nima Catalog AI v0.3.1 production-ready generation plan.

Additive wrapper over v0.1/v0.2/v0.3 planning contracts. The legacy
`build_generation_plan` remains untouched; this layer applies the v0.3.1
production-image policy after the existing plan has already passed its legacy
schema validation.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils
from .build_brief import build_generation_plan
from .production_policy import (
    COMMERCE_WHITE_BACKGROUND,
    PURE_WHITE_HEX,
    resolve_production_image_policy,
)

SCHEMA_NAME = "production-generation-plan-v031.schema.json"

_WHITE_BACKGROUND_RULE = (
    "Commerce primary image policy: background must be uniform pure white "
    f"{PURE_WHITE_HEX}; no cream, gray, gradient, texture, room, props, horizon, "
    "environment, or generated lifestyle context is allowed."
)


def _apply_policy_to_output(entry: dict) -> dict:
    output = dict(entry)
    policy = resolve_production_image_policy(output["type"])
    output["asset_role"] = policy.asset_role
    output["background_policy"] = policy.background_policy
    output["required_background"] = policy.required_background

    if policy.background_policy == COMMERCE_WHITE_BACKGROUND:
        output["background"] = (
            f"Uniform pure white studio background ({PURE_WHITE_HEX}), edge-to-edge and visually neutral. "
            "No cream/off-white tint, gray cast, gradient, texture, room, props, horizon line, or contextual scene."
        )
        output["mandatory_rules"] = list(output["mandatory_rules"]) + [_WHITE_BACKGROUND_RULE]
        output["rejection_criteria"] = list(output["rejection_criteria"]) + [
            f"Commerce-primary background is not uniform {PURE_WHITE_HEX}",
            "Any contextual/lifestyle environment appears in the commerce-primary image",
        ]
    return output


def build_production_generation_plan_v031(
    *,
    analysis: dict,
    outputs_requested: list[str],
    schemas_dir: Path,
    overrides: dict | None = None,
) -> dict:
    """Build the legacy plan, then enforce v0.3.1 production-image policy."""
    legacy_plan = build_generation_plan(
        analysis=analysis,
        outputs_requested=outputs_requested,
        schemas_dir=schemas_dir,
        overrides=overrides,
    )
    plan = {
        "handle": legacy_plan["handle"],
        "policy_version": "0.3.1",
        "outputs": [_apply_policy_to_output(entry) for entry in legacy_plan["outputs"]],
    }
    schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
    file_utils.validate_against_schema(plan, schema)
    return plan
