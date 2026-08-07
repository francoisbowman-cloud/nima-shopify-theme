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


def save_background_request(request: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(request, schema)
    file_utils.write_json(path, request)
