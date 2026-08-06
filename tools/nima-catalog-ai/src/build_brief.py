"""Fase 2 — deterministic generation-plan.json assembly from product-analysis.json.

No API call here: the plan is assembled from the static per-type templates
(prompts/refined.md, lifestyle.md, in-use.md) plus the product-specific
constraints already produced by analyze_product. Keeping this deterministic
avoids spending budget twice on the same information and keeps the plan
traceable to a fixed rule set.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils
from .config import VALID_OUTPUT_TYPES

# Card aspect ratio verified against the live theme, not assumed:
# theme/assets/base.css:221 `.pcard__media{aspect-ratio:1/1; ...}` — every
# catalog card is a fixed 1:1 box. See README.md "Storefront framing" for
# the full finding, including the CSS-driven whitespace this pipeline
# cannot control (theme/assets/base.css:222 `padding: var(--space-12)` on
# the <img> itself).
CARD_ASPECT_RATIO = "1:1"
TARGET_OCCUPANCY_PCT = (75.0, 88.0)

# Keyword families that mark a product as needing product-preserving
# treatment — anything an image model tends to redraw slightly wrong on a
# full regenerate: wordmarks/logos/relief work, and small functional parts
# whose exact count/shape matters (this is exactly what failed in the first
# real run — see ESTADO decision on the paw-tab and wordmark rejections).
_MARK_KEYWORDS = ("wordmark", "logo", "emboss", "engrav", "relief", "brand mark")
_SMALL_PART_KEYWORDS = (
    "tab",
    "pad",
    "clasp",
    "closure",
    "hook-and-loop",
    "buckle",
    "zipper",
    "mechanism",
    "hinge",
    "baffle",
    "perforation",
)


def load_overrides(input_dir: Path, *, schemas_dir: Path | None = None) -> dict:
    """Read <input_dir>/product-overrides.json if present; {} otherwise.

    Overrides are a separate, human-authored file — never written into or
    merged onto product-analysis.json. build_generation_plan reads both and
    combines them only in the generation plan it produces.
    """
    overrides_path = input_dir / "product-overrides.json"
    if not overrides_path.exists():
        return {}
    overrides = file_utils.read_json(overrides_path)
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, "product-overrides.schema.json")
        file_utils.validate_against_schema(overrides, schema)
    return overrides


def _override_rules(overrides: dict) -> list[str]:
    rules = []
    if overrides.get("wordmark_exact_text"):
        rules.append(
            f'Human-confirmed (overrides analysis on conflict): wordmark/logo text reads exactly '
            f'"{overrides["wordmark_exact_text"]}" — not an approximation or a different spelling.'
        )
    for part, count in overrides.get("part_counts", {}).items():
        rules.append(f"Human-confirmed (overrides analysis on conflict): exact count of {part} is {count}.")
    for color in overrides.get("confirmed_colors", []):
        rules.append(f"Human-confirmed (overrides analysis on conflict): confirmed color is {color}.")
    for constraint in overrides.get("functional_constraints", []):
        rules.append(f"Human-confirmed (overrides analysis on conflict): {constraint}")
    for correction in overrides.get("human_corrections", []):
        rules.append(f"Human correction from a prior rejected candidate: {correction}")
    return rules


def detect_product_preserving(analysis: dict) -> bool:
    """True if this product has details a full regenerate is likely to get wrong.

    Heuristic keyword scan over the analysis text fields — not a model call,
    so it's free and deterministic. False negatives are safe (falls back to
    the existing full-generate strategy); false positives just mean a
    background-only edit is used where a full regenerate would have been
    fine too, which is not a fidelity risk.
    """
    haystack = " ".join(
        analysis.get("critical_visual_features", [])
        + analysis.get("critical_functional_features", [])
        + analysis.get("forbidden_changes", [])
    ).lower()
    return any(kw in haystack for kw in _MARK_KEYWORDS + _SMALL_PART_KEYWORDS)


def _framing_rules() -> dict:
    return {
        "target_occupancy_pct_min": TARGET_OCCUPANCY_PCT[0],
        "target_occupancy_pct_max": TARGET_OCCUPANCY_PCT[1],
        "margins": "balanced on all sides, no single side more than 1.5x another",
        "centering": "optical (account for the paw-tab/handle visual weight, not just the bounding box)",
        "card_aspect_ratio": CARD_ASPECT_RATIO,
    }


_TYPE_TEMPLATES = {
    "refined": {
        "goal": "Catalog packshot. Priority order: (1) clean up the original — remove dust/props/reflections, "
        "(2) replace or clean the background, (3) correct lighting, (4) preserve the product exactly. "
        "This is background/lighting cleanup of the real photo, not a from-scratch redraw.",
        "composition": "Product fully visible, optically centered, occupying the target framing range — see framing_rules.",
        "background": "Neutral studio background (light/cream) unless analysis marks a different background as an allowed_changes item.",
        "lighting": "Even studio lighting, no harsh shadows.",
        "aspect_ratio": "1:1",
        "rejection_criteria": [
            "Product category changed",
            "Any critical visual/functional feature altered",
            "Item count changed",
            "Invented props, packaging, or text added",
            "Product occupancy far outside the framing_rules target range",
        ],
    },
    "lifestyle": {
        "goal": "Secondary home-context image, product remains focal point.",
        "composition": "Product in a plausible home setting, scale-consistent with the product's real dimensions, "
        "optically centered within the framing_rules target range.",
        "background": "Home environment (floor, windowsill, countertop) matching Nima's lifestyle tone.",
        "lighting": "Warm natural light.",
        "aspect_ratio": "4:5",
        "rejection_criteria": [
            "Product altered or occluded beyond recognition",
            "Implausible scale for any pet/person shown",
            "Interaction beyond passive/ambient presence",
        ],
    },
    "in-use": {
        "goal": "Show the product functioning as intended, exactly as described in interaction_constraints.",
        "composition": "One clear interaction, correct contact surface and orientation.",
        "background": "Home environment consistent with lifestyle tone.",
        "lighting": "Warm natural light.",
        "aspect_ratio": "4:5",
        "rejection_criteria": [
            "Wrong interaction or contact surface",
            "Anatomical defects in any person/pet shown",
            "Product altered",
            "Implausible scale",
        ],
    },
}

# Only `refined` keeps the original framing/crop closely enough for a pixel
# mask to make sense — lifestyle/in-use relocate the product into a new
# scene, so masking isn't technically applicable there (see README.md
# "Estrategia product-preserving" for why). For those, product-preserving
# instead means: harden the prompt with the literal preserved details.
_MASKABLE_TYPES = {"refined"}


def _mandatory_rules(
    analysis: dict, output_type: str, *, product_preserving: bool, overrides: dict | None = None
) -> list[str]:
    rules = [f"Preserve: {feature}" for feature in analysis.get("critical_visual_features", [])]
    rules += [f"Preserve function: {feature}" for feature in analysis.get("critical_functional_features", [])]
    rules += [f"Forbidden: {change}" for change in analysis.get("forbidden_changes", [])]
    # Override rules come last so they read as the final word when they
    # conflict with something inferred above — analysis.json itself is
    # never edited to make this true, only the plan's rule ordering.
    rules += _override_rules(overrides or {})
    if product_preserving:
        if output_type in _MASKABLE_TYPES:
            rules.append(
                "Product-preserving mode: only the background is being edited via a preservation mask — "
                "the product's own pixels (including any wordmark/logo/relief and small functional parts) "
                "are locked and cannot be redrawn by this call."
            )
        else:
            rules.append(
                "Product-preserving mode: do not redraw or approximate the wordmark/logo/relief or any small "
                "functional part named above — reproduce them exactly as described, not as a generic "
                "stand-in shape."
            )
    if output_type == "in-use":
        rules += [f"Interaction rule: {rule}" for rule in analysis.get("interaction_constraints", [])]
        rules.append("Requires human review before any downstream use — never auto-approved.")
    return rules


def _secondary_references(analysis: dict, primary: str, limit: int = 2) -> list[str]:
    return [img for img in analysis.get("reference_images", []) if img != primary][:limit]


def build_generation_plan(
    *,
    analysis: dict,
    outputs_requested: list[str],
    schemas_dir: Path,
    overrides: dict | None = None,
) -> dict:
    unknown_requested = [o for o in outputs_requested if o not in VALID_OUTPUT_TYPES]
    if unknown_requested:
        raise ValueError(f"Unknown output type(s) requested: {unknown_requested}")

    overrides = overrides or {}
    eligible = analysis.get("eligible_outputs", {})
    primary = analysis["primary_reference"]
    # A human override on a wordmark/part-count/etc. is itself evidence this
    # product needs preserving treatment, even if the automated analysis
    # text didn't happen to use one of the trigger keywords.
    product_preserving = detect_product_preserving(analysis) or bool(overrides)

    outputs = []
    for output_type in outputs_requested:
        key = output_type.replace("-", "_")
        if not eligible.get(key, False):
            continue  # not eligible per analysis — omitted downstream, no plan entry
        template = _TYPE_TEMPLATES[output_type]
        strategy = "product-preserving" if product_preserving else "full-generate"
        mask_strategy = (
            "background-only" if (product_preserving and output_type in _MASKABLE_TYPES) else "none"
        )
        outputs.append(
            {
                "type": output_type,
                "primary_reference": primary,
                "secondary_references": [] if mask_strategy != "none" else _secondary_references(analysis, primary),
                "goal": template["goal"],
                "composition": template["composition"],
                "background": template["background"],
                "lighting": template["lighting"],
                "aspect_ratio": template["aspect_ratio"],
                "mandatory_rules": _mandatory_rules(
                    analysis, output_type, product_preserving=product_preserving, overrides=overrides
                )
                or ["No product-specific rules extracted — treat analysis.unknowns as open risk."],
                "risks": analysis.get("unknowns", []) + ([f"risk_level: {analysis['risk_level']}"] if analysis.get("risk_level") else []),
                "rejection_criteria": template["rejection_criteria"],
                "strategy": strategy,
                "mask_strategy": mask_strategy,
                "framing_rules": _framing_rules(),
            }
        )

    plan = {"handle": analysis["handle"], "outputs": outputs}
    schema = file_utils.load_schema(schemas_dir, "generation-plan.schema.json")
    file_utils.validate_against_schema(plan, schema)
    return plan
