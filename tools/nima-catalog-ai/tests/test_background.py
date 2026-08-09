from pathlib import Path

from src import background, placement, scene

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


def test_build_background_request_reserves_product_zone():
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    request = background.build_background_request(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        product_category="pet feeding mat",
        environment="Warm editorial living room.",
    )
    bbox = placement_spec["product"]["final_bbox"]
    assert str(bbox["left"]) in request["reserved_zone"]
    assert "another pet feeding mat" in request["negative_objects"]


def test_lifestyle_scene_excludes_product_from_background_prompt():
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    request = background.build_background_request(
        scene_spec=scene_spec, placement_spec=placement_spec, product_category="mat", environment="Room."
    )
    assert any("do not depict the product" in c.lower() for c in request["interaction_constraints"])


def test_in_use_scene_requires_occupied_reserved_zone():
    scene_spec = scene.build_scene_spec(scene_type="in-use", interaction_level=2)
    placement_spec = _placement_spec()
    request = background.build_background_request(
        scene_spec=scene_spec, placement_spec=placement_spec, product_category="mat", environment="Room."
    )
    assert any("do not leave it empty" in c.lower() for c in request["interaction_constraints"])


def test_render_prompt_includes_all_negative_objects():
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    request = background.build_background_request(
        scene_spec=scene_spec, placement_spec=placement_spec, product_category="mat", environment="Room."
    )
    prompt = background.render_prompt(request)
    for obj in request["negative_objects"]:
        assert f"Do not include {obj}." in prompt


def test_save_background_request_validates_against_schema(tmp_path):
    scene_spec = scene.build_scene_spec()
    placement_spec = _placement_spec()
    request = background.build_background_request(
        scene_spec=scene_spec, placement_spec=placement_spec, product_category="mat", environment="Room."
    )
    out = tmp_path / "background-request.json"
    background.save_background_request(request, out, schemas_dir=SCHEMAS_DIR)
    assert out.exists()
