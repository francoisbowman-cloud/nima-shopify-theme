from src import composition_gates, composition_review, placement, scene


def _specs():
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
    p_spec = placement.build_placement_spec(meta)
    s_spec = scene.build_scene_spec()
    gate = composition_gates.run_composition_gate(scene_spec=s_spec, placement_spec=p_spec)
    return p_spec, s_spec, gate


def test_build_review_entry_lifestyle_composite():
    p_spec, s_spec, gate = _specs()
    entry = composition_review.build_review_entry(
        handle="h", output_type="lifestyle", placement_spec=p_spec, scene_spec=s_spec, gate_report=gate
    )
    assert entry["generation_kind"] == "LIFESTYLE COMPOSITE"
    assert entry["composition"]["interaction_level"] == 0
    assert entry["composition"]["placement_status"] == "pass"


def test_classify_generation_kind_in_use():
    s_spec = scene.build_scene_spec(scene_type="in-use", interaction_level=2)
    kind = composition_review.classify_generation_kind(
        scene_spec=s_spec, generation_strategy=composition_review.GENERATION_STRATEGY_PROTECTED
    )
    assert kind == "IN-USE"


def test_classify_generation_kind_refined_when_not_protected():
    s_spec = scene.build_scene_spec()
    kind = composition_review.classify_generation_kind(scene_spec=s_spec, generation_strategy="full-generate")
    assert kind == "REFINED"


def test_write_review_entry_writes_json(tmp_path):
    p_spec, s_spec, gate = _specs()
    entry = composition_review.build_review_entry(
        handle="h", output_type="lifestyle", placement_spec=p_spec, scene_spec=s_spec, gate_report=gate
    )
    out = tmp_path / "review-entry.json"
    composition_review.write_review_entry(entry, out)
    assert out.exists()
