from pathlib import Path

import pytest

from src import scene_intelligence, surface

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _scene_intel(category="pet feeding mat"):
    return scene_intelligence.build_scene_intelligence(
        {"title": "x", "product_category": category, "critical_functional_features": [], "critical_visual_features": []}
    )


def test_flat_ground_product_is_perspective_eligible():
    model = surface.build_surface_model(_scene_intel())
    assert model["surface_plane"] == "ground"
    assert model["geometry_class"] == "flat"
    assert model["perspective_match_eligible"] is True
    assert not model["warnings"]


def test_volumetric_ground_product_is_not_perspective_eligible():
    model = surface.build_surface_model(_scene_intel(category="water bowl"))
    assert model["geometry_class"] == "volumetric"
    assert model["perspective_match_eligible"] is False
    assert model["warnings"]


def test_hanging_product_is_not_perspective_eligible():
    model = surface.build_surface_model(_scene_intel(category="dog leash"))
    assert model["surface_plane"] == "hanging"
    assert model["perspective_match_eligible"] is False


def test_is_ground_flat_helper():
    flat_model = surface.build_surface_model(_scene_intel())
    assert surface.is_ground_flat(flat_model)
    bowl_model = surface.build_surface_model(_scene_intel(category="water bowl"))
    assert not surface.is_ground_flat(bowl_model)


def test_requires_perspective_match_matches_field():
    model = surface.build_surface_model(_scene_intel())
    assert surface.requires_perspective_match(model) == model["perspective_match_eligible"]


def test_missing_geometry_class_raises():
    intel = _scene_intel()
    del intel["geometry_class"]
    with pytest.raises(ValueError):
        surface.build_surface_model(intel)


def test_save_surface_model_validates_schema(tmp_path):
    model = surface.build_surface_model(_scene_intel())
    out = tmp_path / "surface-model.json"
    surface.save_surface_model(model, out, schemas_dir=SCHEMAS_DIR)
    assert out.exists()
