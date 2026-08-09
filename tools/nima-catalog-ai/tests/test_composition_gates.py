from src import composition_gates, placement, scene


def _seg_meta(w=400, h=200):
    return {
        "source_width": 1000,
        "source_height": 800,
        "bounding_box": {"left": 0, "top": 0, "right": w, "bottom": h},
        "product_pixel_width": w,
        "product_pixel_height": h,
        "product_area_ratio": 0.3,
        "edge_confidence": 0.9,
        "has_transparency": True,
        "backend": "heuristic",
        "warnings": [],
    }


def test_composition_gate_passes_for_valid_lifestyle_placement():
    p_spec = placement.build_placement_spec(_seg_meta())
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    assert report["passed"] is True
    assert report["status"] == "pass"


def test_composition_gate_catches_out_of_canvas_bbox():
    p_spec = placement.build_placement_spec(_seg_meta())
    p_spec["product"]["final_bbox"] = {"left": -10, "top": 0, "right": 400, "bottom": 200}
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    assert report["passed"] is False
    assert "out_of_canvas" in report["geometry"]["violations"]


def test_composition_gate_catches_undersized_product():
    p_spec = placement.build_placement_spec(_seg_meta())
    p_spec["product"]["final_occupancy"] = 0.001
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    assert "occupancy_out_of_range" in report["geometry"]["violations"]


def test_composition_gate_catches_oversized_product():
    p_spec = placement.build_placement_spec(_seg_meta())
    p_spec["product"]["final_occupancy"] = 0.5  # above max_occupancy (0.42) but within the 0.60 absolute ceiling
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    assert "occupancy_out_of_range" in report["geometry"]["violations"]
    assert "scale_implausible" not in report["geometry"]["violations"]


def test_composition_gate_catches_altered_aspect_ratio():
    p_spec = placement.build_placement_spec(_seg_meta(w=400, h=200))
    p_spec["product"]["final_bbox"] = {"left": 0, "top": 0, "right": 400, "bottom": 400}  # squished to 1:1
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    assert "aspect_ratio_altered" in report["geometry"]["violations"]


def test_composition_gate_catches_floating_product():
    p_spec = placement.build_placement_spec(_seg_meta())
    p_spec["product"]["final_bbox"]["bottom"] -= 100  # no longer touching ground_plane.y
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    assert "floating_without_ground_plane" in report["scene"]["violations"]


def test_composition_gate_scene_check_only_flags_incompatible_lifestyle():
    p_spec = placement.build_placement_spec(_seg_meta())
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    assert "lifestyle_interaction_incompatible" not in report["scene"]["violations"]


def test_save_composition_gate_report_validates_schema(tmp_path):
    from pathlib import Path

    schemas_dir = Path(__file__).resolve().parent.parent / "schemas"
    p_spec = placement.build_placement_spec(_seg_meta())
    s_spec = scene.build_scene_spec()
    report = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    out = tmp_path / "composition-gate-report.json"
    composition_gates.save_composition_gate_report(report, out, schemas_dir=schemas_dir)
    assert out.exists()
