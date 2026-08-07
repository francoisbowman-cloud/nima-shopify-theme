from pathlib import Path

import pytest

from src import scene

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def test_default_lifestyle_scene_is_interaction_level_zero():
    spec = scene.build_scene_spec()
    assert spec["scene_type"] == "lifestyle"
    assert spec["interaction_level"] == 0
    assert spec["product_contact_allowed"] is False
    assert spec["animal_contact_allowed"] is False
    assert spec["human_contact_allowed"] is False


def test_lifestyle_with_nonzero_interaction_level_rejected():
    with pytest.raises(scene.SceneSpecError):
        scene.build_scene_spec(scene_type="lifestyle", interaction_level=1)


def test_in_use_requires_nonzero_interaction_level():
    with pytest.raises(scene.SceneSpecError):
        scene.build_scene_spec(scene_type="in-use", interaction_level=0)


def test_lifestyle_scene_cannot_allow_any_contact():
    with pytest.raises(scene.SceneSpecError):
        scene.build_scene_spec(scene_type="lifestyle", interaction_level=0, animal_contact_allowed=True)


def test_in_use_scene_defaults_to_contact_allowed():
    spec = scene.build_scene_spec(scene_type="in-use", interaction_level=2)
    assert spec["product_contact_allowed"] is True
    assert spec["animal_contact_allowed"] is True


def test_is_lifestyle_compatible_true_for_passive_scene():
    spec = scene.build_scene_spec()
    assert scene.is_lifestyle_compatible(spec)


def test_is_lifestyle_compatible_false_for_in_use_scene():
    spec = scene.build_scene_spec(scene_type="in-use", interaction_level=1)
    assert not scene.is_lifestyle_compatible(spec)


def test_is_supported_by_v02_compositor():
    lifestyle = scene.build_scene_spec()
    in_use = scene.build_scene_spec(scene_type="in-use", interaction_level=1)
    assert scene.is_supported_by_v02_compositor(lifestyle)
    assert not scene.is_supported_by_v02_compositor(in_use)


def test_unknown_scene_type_rejected():
    with pytest.raises(scene.SceneSpecError):
        scene.build_scene_spec(scene_type="studio", interaction_level=0)


def test_unknown_interaction_level_rejected():
    with pytest.raises(scene.SceneSpecError):
        scene.build_scene_spec(scene_type="in-use", interaction_level=9)


def test_save_scene_spec_validates_against_schema(tmp_path):
    spec = scene.build_scene_spec()
    out = tmp_path / "scene-spec.json"
    scene.save_scene_spec(spec, out, schemas_dir=SCHEMAS_DIR)
    assert out.exists()
