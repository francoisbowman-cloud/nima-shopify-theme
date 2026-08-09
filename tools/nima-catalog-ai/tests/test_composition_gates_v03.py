from pathlib import Path

from src import composition_gates, placement, scene, scene_intelligence, surface

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _placement_spec():
    meta = {
        "source_width": 1000,
        "source_height": 800,
        "bounding_box": {"left": 0, "top": 0, "right": 400, "bottom": 200},
        "product_pixel_width": 400,
        "product_pixel_height": 200,
        "product_area_ratio": 0.3,
        "edge_confidence": 0.9,
        "has_transparency": True,
        "backend": "heuristic",
        "warnings": [],
    }
    return placement.build_placement_spec(meta)


def _scene_intel(category="pet feeding mat"):
    return scene_intelligence.build_scene_intelligence(
        {"title": "x", "product_category": category, "critical_functional_features": [], "critical_visual_features": []}
    )


def test_v03_gate_passes_for_valid_flat_ground_perspective_case():
    p_spec = _placement_spec()
    s_spec = scene.build_scene_spec()
    scene_intel = _scene_intel()
    surface_model = surface.build_surface_model(scene_intel)
    top_env = scene_intelligence.top_environment(scene_intel)
    bbox = p_spec["product"]["final_bbox"]
    area = (bbox["right"] - bbox["left"]) * (bbox["bottom"] - bbox["top"])

    report = composition_gates.run_composition_gate_v03(
        scene_spec=s_spec,
        placement_spec=p_spec,
        scene_intel=scene_intel,
        top_environment=top_env,
        surface_model=surface_model,
        perspective_applied=True,
        warped_area=area * 0.9,
        edge_refinement_applied=True,
        shadow_is_surface_aware=True,
    )
    assert report["passed"] is True


def test_v03_gate_flags_perspective_eligible_but_not_applied():
    p_spec = _placement_spec()
    s_spec = scene.build_scene_spec()
    scene_intel = _scene_intel()
    surface_model = surface.build_surface_model(scene_intel)

    report = composition_gates.run_composition_gate_v03(
        scene_spec=s_spec,
        placement_spec=p_spec,
        scene_intel=scene_intel,
        top_environment=scene_intelligence.top_environment(scene_intel),
        surface_model=surface_model,
        perspective_applied=False,
        warped_area=None,
        edge_refinement_applied=True,
        shadow_is_surface_aware=True,
    )
    assert "perspective_eligible_but_not_applied" in report["perspective"]["violations"]
    assert report["passed"] is False


def test_v03_gate_flags_perspective_applied_when_ineligible():
    p_spec = _placement_spec()
    s_spec = scene.build_scene_spec()
    scene_intel = _scene_intel(category="water bowl")
    surface_model = surface.build_surface_model(scene_intel)
    assert not surface_model["perspective_match_eligible"]

    report = composition_gates.run_composition_gate_v03(
        scene_spec=s_spec,
        placement_spec=p_spec,
        scene_intel=scene_intel,
        top_environment=scene_intelligence.top_environment(scene_intel),
        surface_model=surface_model,
        perspective_applied=True,
        warped_area=1000,
        edge_refinement_applied=True,
        shadow_is_surface_aware=True,
    )
    assert "perspective_applied_when_ineligible" in report["perspective"]["violations"]


def test_v03_gate_flags_implausible_warped_area():
    p_spec = _placement_spec()
    s_spec = scene.build_scene_spec()
    scene_intel = _scene_intel()
    surface_model = surface.build_surface_model(scene_intel)
    bbox = p_spec["product"]["final_bbox"]
    area = (bbox["right"] - bbox["left"]) * (bbox["bottom"] - bbox["top"])

    report = composition_gates.run_composition_gate_v03(
        scene_spec=s_spec,
        placement_spec=p_spec,
        scene_intel=scene_intel,
        top_environment=scene_intelligence.top_environment(scene_intel),
        surface_model=surface_model,
        perspective_applied=True,
        warped_area=area * 5,  # way outside the plausible ratio range
        edge_refinement_applied=True,
        shadow_is_surface_aware=True,
    )
    assert "warped_area_implausible" in report["perspective"]["violations"]


def test_v03_gate_flags_missing_edge_refinement():
    p_spec = _placement_spec()
    s_spec = scene.build_scene_spec()
    scene_intel = _scene_intel()
    surface_model = surface.build_surface_model(scene_intel)

    report = composition_gates.run_composition_gate_v03(
        scene_spec=s_spec,
        placement_spec=p_spec,
        scene_intel=scene_intel,
        top_environment=scene_intelligence.top_environment(scene_intel),
        surface_model=surface_model,
        perspective_applied=True,
        warped_area=(p_spec["product"]["final_bbox"]["right"] - p_spec["product"]["final_bbox"]["left"])
        * (p_spec["product"]["final_bbox"]["bottom"] - p_spec["product"]["final_bbox"]["top"]),
        edge_refinement_applied=False,
        shadow_is_surface_aware=True,
    )
    assert "edge_refinement_missing" in report["edge_and_shadow"]["violations"]
    assert report["passed"] is False


def test_v03_gate_still_enforces_v02_geometry_checks():
    p_spec = _placement_spec()
    p_spec["product"]["final_bbox"] = {"left": -10, "top": 0, "right": 400, "bottom": 200}
    s_spec = scene.build_scene_spec()
    scene_intel = _scene_intel()
    surface_model = surface.build_surface_model(scene_intel)

    report = composition_gates.run_composition_gate_v03(
        scene_spec=s_spec,
        placement_spec=p_spec,
        scene_intel=scene_intel,
        top_environment=scene_intelligence.top_environment(scene_intel),
        surface_model=surface_model,
        perspective_applied=False,
        warped_area=None,
        edge_refinement_applied=True,
        shadow_is_surface_aware=True,
    )
    assert "out_of_canvas" in report["geometry"]["violations"]
    assert report["passed"] is False


def test_save_v03_gate_report_validates_schema(tmp_path):
    p_spec = _placement_spec()
    s_spec = scene.build_scene_spec()
    scene_intel = _scene_intel()
    surface_model = surface.build_surface_model(scene_intel)
    bbox = p_spec["product"]["final_bbox"]
    area = (bbox["right"] - bbox["left"]) * (bbox["bottom"] - bbox["top"])

    report = composition_gates.run_composition_gate_v03(
        scene_spec=s_spec,
        placement_spec=p_spec,
        scene_intel=scene_intel,
        top_environment=scene_intelligence.top_environment(scene_intel),
        surface_model=surface_model,
        perspective_applied=True,
        warped_area=area * 0.9,
        edge_refinement_applied=True,
        shadow_is_surface_aware=True,
    )
    out = tmp_path / "composition-gate-report-v03.json"
    composition_gates.save_composition_gate_report_v03(report, out, schemas_dir=SCHEMAS_DIR)
    assert out.exists()
