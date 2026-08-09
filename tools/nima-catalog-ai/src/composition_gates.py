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


# v0.3 Block 7 — extends the gate with checks the v0.2 gate had no concept
# of: does the chosen scene actually fit the product (Scene Intelligence),
# is the perspective warp geometrically sane, is the product actually
# grounded (not floating) in its warped footprint, and were the edge/shadow
# refinement passes actually applied where they should have been. Runs
# strictly in addition to the v0.2 checks — never relaxes them.
SCHEMA_NAME_V03 = "composition-gate-report-v03.schema.json"

_PLAUSIBLE_WARPED_AREA_RATIO = (0.4, 1.6)  # vs. the un-warped placement bbox area


def check_scene_product_fit(scene_intel: dict, top_environment: str) -> dict:
    checks = {
        "environment_not_in_taxonomy": top_environment not in (
            scene_intel["primary_environments"] + scene_intel["secondary_environments"]
        ),
        "used_fallback_taxonomy": bool(scene_intel["warnings"]),
    }
    violations = [name for name, is_bad in checks.items() if is_bad]
    # used_fallback_taxonomy is informational, not disqualifying — a
    # fallback profile is still coherent, just not category-specific.
    passed = not checks["environment_not_in_taxonomy"]
    return {"checks": checks, "violations": violations, "passed": passed}


def check_perspective(*, surface_model: dict, perspective_applied: bool, placement_bbox_area: float, warped_area: float | None) -> dict:
    checks: dict[str, bool] = {}
    if surface_model["perspective_match_eligible"]:
        checks["perspective_eligible_but_not_applied"] = not perspective_applied
        if perspective_applied and warped_area is not None and placement_bbox_area > 0:
            ratio = warped_area / placement_bbox_area
            checks["warped_area_implausible"] = not (
                _PLAUSIBLE_WARPED_AREA_RATIO[0] <= ratio <= _PLAUSIBLE_WARPED_AREA_RATIO[1]
            )
        else:
            checks["warped_area_implausible"] = False
    else:
        # Not eligible (e.g. a volumetric bowl) — applying a planar warp
        # here would itself be the bug, not skipping it.
        checks["perspective_applied_when_ineligible"] = perspective_applied
    violations = [name for name, is_bad in checks.items() if is_bad]
    return {"checks": checks, "violations": violations, "passed": not violations}


def check_edge_and_shadow(*, edge_refinement_applied: bool, shadow_is_surface_aware: bool) -> dict:
    checks = {
        "edge_refinement_missing": not edge_refinement_applied,
        "shadow_not_surface_aware": not shadow_is_surface_aware,
    }
    violations = [name for name, is_bad in checks.items() if is_bad]
    return {"checks": checks, "violations": violations, "passed": not violations}


def run_composition_gate_v03(
    *,
    scene_spec: dict,
    placement_spec: dict,
    scene_intel: dict,
    top_environment: str,
    surface_model: dict,
    perspective_applied: bool,
    warped_area: float | None,
    edge_refinement_applied: bool,
    shadow_is_surface_aware: bool,
) -> dict:
    base = run_composition_gate(scene_spec=scene_spec, placement_spec=placement_spec)

    placement_bbox = placement_spec["product"]["final_bbox"]
    placement_bbox_area = (placement_bbox["right"] - placement_bbox["left"]) * (
        placement_bbox["bottom"] - placement_bbox["top"]
    )

    scene_fit = check_scene_product_fit(scene_intel, top_environment)
    perspective = check_perspective(
        surface_model=surface_model,
        perspective_applied=perspective_applied,
        placement_bbox_area=placement_bbox_area,
        warped_area=warped_area,
    )
    edge_shadow = check_edge_and_shadow(
        edge_refinement_applied=edge_refinement_applied, shadow_is_surface_aware=shadow_is_surface_aware
    )

    passed = base["passed"] and scene_fit["passed"] and perspective["passed"] and edge_shadow["passed"]
    return {
        "passed": passed,
        "status": "pass" if passed else "fail",
        "geometry": base["geometry"],
        "scene": base["scene"],
        "scene_product_fit": scene_fit,
        "perspective": perspective,
        "edge_and_shadow": edge_shadow,
    }


def save_composition_gate_report_v03(report: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME_V03)
        file_utils.validate_against_schema(report, schema)
    file_utils.write_json(path, report)
