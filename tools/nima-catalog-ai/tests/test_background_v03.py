from pathlib import Path

from src import background, placement, scene, scene_intelligence

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


def _scene_intel():
    return scene_intelligence.build_scene_intelligence(
        {"title": "x", "product_category": "pet feeding mat", "critical_functional_features": [], "critical_visual_features": []}
    )


def test_scene_aware_request_uses_top_environment_in_prompt():
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    scene_intel = _scene_intel()
    top_env = scene_intelligence.top_environment(scene_intel)
    request = background.build_scene_aware_background_request(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        scene_intel=scene_intel,
        product_category=scene_intel["product_role"],
        top_environment=top_env,
    )
    assert top_env in request["environment"]


def test_scene_aware_request_reserved_zone_uses_relative_percentages_not_pixels():
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    scene_intel = _scene_intel()
    request = background.build_scene_aware_background_request(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        scene_intel=scene_intel,
        product_category=scene_intel["product_role"],
        top_environment="kitchen feeding area",
    )
    assert "%" in request["reserved_zone"]
    bbox = placement_spec["product"]["final_bbox"]
    assert str(bbox["left"]) not in request["reserved_zone"]


def test_scene_aware_request_mentions_preferred_surfaces():
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    scene_intel = _scene_intel()
    request = background.build_scene_aware_background_request(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        scene_intel=scene_intel,
        product_category=scene_intel["product_role"],
        top_environment="kitchen feeding area",
    )
    assert any(surface in request["environment"] for surface in scene_intel["preferred_surfaces"])


def test_scene_aware_request_validates_against_existing_schema(tmp_path):
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    scene_intel = _scene_intel()
    request = background.build_scene_aware_background_request(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        scene_intel=scene_intel,
        product_category=scene_intel["product_role"],
        top_environment="kitchen feeding area",
    )
    out = tmp_path / "background-request.json"
    background.save_background_request(request, out, schemas_dir=SCHEMAS_DIR)
    assert out.exists()
