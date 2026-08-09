"""v0.3 Block 2 — surface/plane model.

Derives `surface-model.json` from the scene-intelligence output (Block 1) —
a separate artifact rather than duplicated taxonomy, because it's consumed
by different downstream stages: perspective.py (Block 3) and shadow.py
(Block 5) only care about `surface_plane`/`geometry_class`, not the full
environment-selection reasoning.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils

SCHEMA_NAME = "surface-model.schema.json"

SURFACE_PLANES = ("ground", "tabletop", "wall", "shelf", "hanging")
GEOMETRY_CLASSES = ("flat", "soft", "volumetric", "upright", "deformable")

# Only a flat object resting on the ground plane benefits from a planar
# perspective warp (Block 3) — a volumetric object (a bowl) or something
# already hanging/upright doesn't have a single dominant flat face to warp,
# and warping it would distort it rather than integrate it.
_PERSPECTIVE_ELIGIBLE = {("ground", "flat")}


def build_surface_model(scene_intel: dict) -> dict:
    plane = scene_intel["placement_plane"]
    geometry_class = scene_intel.get("geometry_class")
    if geometry_class is None:
        raise ValueError(
            "scene_intel is missing geometry_class — build_scene_intelligence must be called with "
            "the v0.3 taxonomy (each entry now carries geometry_class)."
        )
    if plane not in SURFACE_PLANES:
        raise ValueError(f"Unknown surface_plane: {plane!r} (valid: {SURFACE_PLANES})")
    if geometry_class not in GEOMETRY_CLASSES:
        raise ValueError(f"Unknown geometry_class: {geometry_class!r} (valid: {GEOMETRY_CLASSES})")

    eligible = (plane, geometry_class) in _PERSPECTIVE_ELIGIBLE
    return {
        "surface_plane": plane,
        "geometry_class": geometry_class,
        "preferred_surfaces": list(scene_intel.get("preferred_surfaces", [])),
        "perspective_match_eligible": eligible,
        "warnings": [] if eligible or plane != "ground" else [
            f"geometry_class={geometry_class!r} on surface_plane='ground' is not planar-warp eligible — "
            "shape isn't a single dominant flat face, so v0.3 skips the perspective warp for this product "
            "and falls back to the v0.2 uniform-scale placement."
        ],
    }


def is_ground_flat(surface_model: dict) -> bool:
    return surface_model["surface_plane"] == "ground" and surface_model["geometry_class"] == "flat"


def requires_perspective_match(surface_model: dict) -> bool:
    return surface_model["perspective_match_eligible"]


def save_surface_model(surface_model: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(surface_model, schema)
    file_utils.write_json(path, surface_model)
