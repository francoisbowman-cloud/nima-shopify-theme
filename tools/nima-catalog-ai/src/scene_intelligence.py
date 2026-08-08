"""v0.3 Block 1 — Scene Intelligence Engine.

v0.2 asked the AI for "a nice-looking environment" with no reasoning about
whether that environment made commercial sense for the product. The real
pilot's living-room choice for a *feeding* mat was plausible but not the
best commercial context — a kitchen feeding corner or a covered patio reads
more like where a buyer would actually put this. This module infers a small,
structured `scene-intelligence.json` from the same `product-analysis.json`
v0.1/v0.2 already produce — no new API call, no new LLM planner: a local
keyword taxonomy is enough for the categories Nima actually sells in.

Deliberately not exhaustive across all possible pet-product categories —
covers Nima's real catalog vocabulary (feeding, bedding, walking/leash,
grooming, toys, litter) plus a generic fallback. Extending the taxonomy for
a new category is a matter of adding one entry to `_TAXONOMY`.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils

SCHEMA_NAME = "scene-intelligence.schema.json"

# Ordered by specificity — first keyword match wins. Each entry describes,
# for a product role, where it commercially/functionally makes sense to
# photograph it and what surface it sits on.
_TAXONOMY = [
    {
        "match_keywords": ("feeding mat", "feeding station", "placemat", "spill mat", "food mat"),
        "product_role": "pet feeding mat",
        "usage_mode": "feeding area accessory",
        "primary_environments": [
            "kitchen feeding area",
            "covered patio",
            "mudroom",
            "pet feeding station",
        ],
        "secondary_environments": ["utility corner", "minimal dining side-area"],
        "preferred_surfaces": ["wood floor", "stone floor", "tile floor"],
        "placement_plane": "ground",
        "geometry_class": "flat",
    },
    {
        "match_keywords": ("bowl", "feeder", "water fountain", "food dispenser"),
        "product_role": "pet feeding vessel",
        "usage_mode": "feeding area accessory",
        "primary_environments": ["kitchen feeding area", "mudroom", "pet feeding station"],
        "secondary_environments": ["covered patio"],
        "preferred_surfaces": ["tile floor", "stone floor", "wood floor"],
        "placement_plane": "ground",
        "geometry_class": "volumetric",
    },
    {
        "match_keywords": ("bed", "crate pad", "cushion", "donut", "mat for sleeping"),
        "product_role": "pet bed",
        "usage_mode": "resting accessory",
        "primary_environments": ["living room reading corner", "bedroom window nook", "sunroom"],
        "secondary_environments": ["covered patio"],
        "preferred_surfaces": ["wood floor", "area rug"],
        "placement_plane": "ground",
        "geometry_class": "soft",
    },
    {
        "match_keywords": ("leash", "harness", "collar", "walking"),
        "product_role": "walking accessory",
        "usage_mode": "outdoor/walking accessory",
        "primary_environments": ["entryway with leash hook", "front porch", "garden path"],
        "secondary_environments": ["mudroom"],
        "preferred_surfaces": ["wall hook", "bench", "wood floor"],
        "placement_plane": "hanging",
        "geometry_class": "deformable",
    },
    {
        "match_keywords": ("grooming", "brush", "glove", "nail clipper", "comb"),
        "product_role": "grooming tool",
        "usage_mode": "grooming accessory",
        "primary_environments": ["bathroom counter", "grooming station", "utility counter"],
        "secondary_environments": ["mudroom"],
        "preferred_surfaces": ["countertop", "tabletop"],
        "placement_plane": "tabletop",
        "geometry_class": "volumetric",
    },
    {
        "match_keywords": ("toy", "chew", "teaser", "plush"),
        "product_role": "pet toy",
        "usage_mode": "play accessory",
        "primary_environments": ["living room floor", "garden lawn", "playroom corner"],
        "secondary_environments": ["covered patio"],
        "preferred_surfaces": ["wood floor", "area rug", "grass"],
        "placement_plane": "ground",
        "geometry_class": "volumetric",
    },
    {
        "match_keywords": ("litter", "waste bag", "poop bag"),
        "product_role": "sanitation accessory",
        "usage_mode": "utility accessory",
        "primary_environments": ["utility corner", "mudroom", "laundry nook"],
        "secondary_environments": ["covered patio"],
        "preferred_surfaces": ["tile floor", "stone floor"],
        "placement_plane": "ground",
        "geometry_class": "volumetric",
    },
]

_DEFAULT_ENTRY = {
    "match_keywords": (),
    "product_role": "general pet accessory",
    "usage_mode": "general home accessory",
    "primary_environments": ["minimal editorial living room", "covered patio"],
    "secondary_environments": ["mudroom"],
    "preferred_surfaces": ["wood floor", "tabletop"],
    "placement_plane": "ground",
    "geometry_class": "volumetric",
}

_RANK_STEP = 0.06


def _haystack(analysis: dict) -> str:
    return " ".join(
        [analysis.get("title", ""), analysis.get("product_category", "")]
        + analysis.get("critical_functional_features", [])
        + analysis.get("critical_visual_features", [])
    ).lower()


def _select_taxonomy_entry(analysis: dict) -> tuple[dict, list[str]]:
    haystack = _haystack(analysis)
    warnings: list[str] = []
    for entry in _TAXONOMY:
        if any(kw in haystack for kw in entry["match_keywords"]):
            return entry, warnings
    warnings.append(
        "No taxonomy keyword matched product_category/title/features — falling back to the generic "
        "pet-accessory scene profile. Consider extending scene_intelligence._TAXONOMY for this product."
    )
    return _DEFAULT_ENTRY, warnings


def build_scene_intelligence(analysis: dict, *, interaction_level: int = 0) -> dict:
    entry, warnings = _select_taxonomy_entry(analysis)

    environment_rankings = []
    for index, env in enumerate(entry["primary_environments"]):
        environment_rankings.append({"environment": env, "score": round(0.95 - index * _RANK_STEP, 2)})
    base_secondary_score = 0.95 - len(entry["primary_environments"]) * _RANK_STEP
    for index, env in enumerate(entry["secondary_environments"]):
        environment_rankings.append({"environment": env, "score": round(base_secondary_score - index * _RANK_STEP, 2)})

    return {
        "product_role": entry["product_role"],
        "usage_mode": entry["usage_mode"],
        "primary_environments": list(entry["primary_environments"]),
        "secondary_environments": list(entry["secondary_environments"]),
        "preferred_surfaces": list(entry["preferred_surfaces"]),
        "placement_plane": entry["placement_plane"],
        "geometry_class": entry["geometry_class"],
        "camera_requirement": "floor-compatible perspective" if entry["placement_plane"] == "ground" else "eye-level perspective",
        "interaction_level": interaction_level,
        "environment_rankings": environment_rankings,
        "warnings": warnings,
    }


def top_environment(scene_intel: dict) -> str:
    if not scene_intel["environment_rankings"]:
        raise ValueError("scene_intelligence has no environment_rankings to choose from")
    return max(scene_intel["environment_rankings"], key=lambda r: r["score"])["environment"]


def save_scene_intelligence(scene_intel: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(scene_intel, schema)
    file_utils.write_json(path, scene_intel)
