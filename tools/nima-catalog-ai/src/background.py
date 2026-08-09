"""v0.2 Block 4 — background generation contract.

The AI's job in v0.2 is narrowed to one thing: generate the environment,
with the product's reserved zone left empty. This module turns a scene spec
+ placement spec into a structured background-generation request and a
human-readable prompt string. No network call happens here — see
background_provider.py (Block 13) for how a structured request eventually
becomes an actual background image.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils

SCHEMA_NAME = "background-request.schema.json"

_INTERACTION_CONSTRAINT_BY_LEVEL = {
    0: "No animal or person touching or occupying the reserved zone. Passive presence only.",
    1: "Animal or person may be near the reserved zone but not touching its contents.",
    2: "Active use is expected in the reserved zone — do not leave it empty.",
    3: "Close manipulation expected in the reserved zone — do not leave it empty.",
}

_DEFAULT_NEGATIVE_OBJECTS = [
    "feeding mats",
    "pet pads",
    "similar or competing products",
    "text, logos, or watermarks",
]


def build_background_request(
    *,
    scene_spec: dict,
    placement_spec: dict,
    product_category: str,
    environment: str,
    lighting: str = "Natural golden-hour side light.",
    camera: str = "Editorial lifestyle photography, eye-level, shallow depth of field.",
    extra_negative_objects: list[str] | None = None,
) -> dict:
    bbox = placement_spec["product"]["final_bbox"]
    canvas = placement_spec["canvas"]
    reserved_zone_desc = (
        f"Empty floor/surface area reserved at pixel region "
        f"({bbox['left']}, {bbox['top']}) to ({bbox['right']}, {bbox['bottom']}) "
        f"on a {canvas['width']}x{canvas['height']} canvas — this region must remain unoccupied "
        f"so the real product can be composited into it afterward."
    )

    negative_objects = list(_DEFAULT_NEGATIVE_OBJECTS) + [f"another {product_category}"] + list(extra_negative_objects or [])
    interaction_constraints = [_INTERACTION_CONSTRAINT_BY_LEVEL[scene_spec["interaction_level"]]]
    if scene_spec["scene_type"] == "lifestyle":
        interaction_constraints.append("Do not depict the product itself — only the surrounding environment.")

    return {
        "environment": environment,
        "lighting": lighting,
        "camera": camera,
        "reserved_zone": reserved_zone_desc,
        "negative_objects": negative_objects,
        "interaction_constraints": interaction_constraints,
        "canvas": {"width": canvas["width"], "height": canvas["height"]},
    }


def render_prompt(request: dict) -> str:
    """Human-readable prompt string built from the structured request — this
    is what would actually be sent to an image-generation API in a future
    version, but v0.2 never sends it anywhere."""
    lines = [
        request["environment"],
        request["lighting"],
        request["camera"],
        request["reserved_zone"],
    ]
    for obj in request["negative_objects"]:
        lines.append(f"Do not include {obj}.")
    for constraint in request["interaction_constraints"]:
        lines.append(constraint)
    return "\n".join(lines)


# v0.3 Block 6 — scene-intelligence-aware background request. Two upgrades
# over v0.2's build_background_request, both learned from Real Pilot 01
# (decision #79): (1) the environment comes from scene_intelligence's
# top-ranked, commercially-appropriate choice instead of a hand-picked
# generic one; (2) the reserved zone is phrased in relative frame
# percentages instead of raw pixel coordinates — an image-generation model
# has no spatial grounding for literal pixel numbers, but "lower-center
# third of the frame" is something it can actually follow.
def build_scene_aware_background_request(
    *,
    scene_spec: dict,
    placement_spec: dict,
    scene_intel: dict,
    product_category: str,
    top_environment: str,
    lighting: str = "Soft natural side light, warm golden undertone, gentle diffused shadows.",
    camera: str = "Editorial lifestyle photography, eye-level, 50mm-equivalent, shallow depth of field.",
    extra_negative_objects: list[str] | None = None,
) -> dict:
    bbox = placement_spec["product"]["final_bbox"]
    canvas = placement_spec["canvas"]
    left_pct = round(100 * bbox["left"] / canvas["width"])
    right_pct = round(100 * bbox["right"] / canvas["width"])
    top_pct = round(100 * bbox["top"] / canvas["height"])
    bottom_pct = round(100 * bbox["bottom"] / canvas["height"])

    surfaces = ", ".join(scene_intel.get("preferred_surfaces", [])) or "a plausible floor surface"
    environment = (
        f"Premium editorial lifestyle photograph of a {top_environment} for a high-end pet brand "
        f"named Nima, styled with {surfaces}. Sophisticated, minimal, uncluttered composition with "
        f"generous negative space, photorealistic, no illustration, no CGI look."
    )
    reserved_zone_desc = (
        f"Leave the lower-center portion of the frame as clear, empty, unobstructed floor or surface "
        f"space — roughly the middle {max(1, right_pct - left_pct)}% of the frame width, centered "
        f"horizontally, from about {top_pct}% down to {bottom_pct}% of the frame height. Nothing should "
        f"rest in or cross into that reserved area."
    )

    negative_objects = list(_DEFAULT_NEGATIVE_OBJECTS) + [f"another {product_category}"] + list(extra_negative_objects or [])
    interaction_constraints = [_INTERACTION_CONSTRAINT_BY_LEVEL[scene_spec["interaction_level"]]]
    if scene_spec["scene_type"] == "lifestyle":
        interaction_constraints.append("Do not depict the product itself — only the surrounding environment.")

    return {
        "environment": environment,
        "lighting": lighting,
        "camera": camera,
        "reserved_zone": reserved_zone_desc,
        "negative_objects": negative_objects,
        "interaction_constraints": interaction_constraints,
        "canvas": {"width": canvas["width"], "height": canvas["height"]},
    }


def save_background_request(request: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(request, schema)
    file_utils.write_json(path, request)
