"""v0.2 Block 7 — Composition Gate: deterministic geometry + scene checks that
run BEFORE the (existing, unchanged) Fidelity Gate.

    Composition Gate -> Fidelity Gate -> Human Review

The Fidelity Gate (evaluate_fidelity.py) remains the authority on visual
identity (does the candidate still look like the real product); this module
only checks things that are computable from the specs themselves, with no
model call and no ambiguity — a product placed outside the canvas is
unarguably wrong regardless of what an LLM thinks of the picture.
"""

from __future__ import annotations

from . import placement as placement_mod
from . import scene as scene_mod
from . import file_utils
from pathlib import Path

SCHEMA_NAME = "composition-gate-report.schema.json"


def check_geometry(placement_spec: dict) -> dict:
    checks = {
        "out_of_canvas": placement_mod.check_clipping(placement_spec),
        "safe_zone_violation": placement_mod.check_safe_zone_violation(placement_spec),
        "aspect_ratio_altered": not placement_mod.check_aspect_ratio_preserved(placement_spec),
        "occupancy_out_of_range": not placement_mod.check_occupancy_in_range(placement_spec),
        "scale_implausible": not placement_mod.check_scale_plausible(placement_spec),
    }
    violations = [name for name, is_bad in checks.items() if is_bad]
    return {"checks": checks, "violations": violations, "passed": not violations}


def check_scene(scene_spec: dict, placement_spec: dict) -> dict:
    checks = {
        "lifestyle_interaction_incompatible": (
            scene_spec["scene_type"] == "lifestyle" and not scene_mod.is_lifestyle_compatible(scene_spec)
        ),
        # A product resting on nothing (bbox bottom above the ground plane's
        # own y) reads as floating — this only applies to the bottom-center
        # anchor, where the bbox bottom is expected to sit on the ground line.
        "floating_without_ground_plane": (
            placement_spec["product"]["anchor"] == "bottom-center"
            and placement_spec["product"]["final_bbox"]["bottom"] != placement_spec["ground_plane"]["y"]
        ),
    }
    violations = [name for name, is_bad in checks.items() if is_bad]
    return {"checks": checks, "violations": violations, "passed": not violations}


def run_composition_gate(*, scene_spec: dict, placement_spec: dict) -> dict:
    geometry = check_geometry(placement_spec)
    scene_result = check_scene(scene_spec, placement_spec)
    passed = geometry["passed"] and scene_result["passed"]
    report = {
        "passed": passed,
        "geometry": geometry,
        "scene": scene_result,
        "status": "pass" if passed else "fail",
    }
    return report


def save_composition_gate_report(report: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(report, schema)
    file_utils.write_json(path, report)
