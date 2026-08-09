from pathlib import Path

from src import scene_intelligence

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _analysis(category="pet feeding mat", title="Waterproof Feeding Mat"):
    return {
        "title": title,
        "product_category": category,
        "critical_functional_features": ["raised lip contains spills"],
        "critical_visual_features": ["rectangular gray mat"],
    }


def test_feeding_mat_selects_feeding_taxonomy():
    intel = scene_intelligence.build_scene_intelligence(_analysis())
    assert intel["product_role"] == "pet feeding mat"
    assert intel["placement_plane"] == "ground"
    assert intel["geometry_class"] == "flat"
    assert "kitchen feeding area" in intel["primary_environments"]
    assert not intel["warnings"]


def test_bed_product_selects_resting_taxonomy():
    intel = scene_intelligence.build_scene_intelligence(_analysis(category="dog bed", title="Donut Bed"))
    assert intel["product_role"] == "pet bed"
    assert intel["geometry_class"] == "soft"


def test_leash_product_selects_hanging_plane():
    intel = scene_intelligence.build_scene_intelligence(_analysis(category="dog leash", title="Nylon Leash"))
    assert intel["placement_plane"] == "hanging"
    assert intel["geometry_class"] == "deformable"


def test_unknown_product_falls_back_to_generic_with_warning():
    intel = scene_intelligence.build_scene_intelligence(_analysis(category="mystery gadget", title="Thing"))
    assert intel["product_role"] == "general pet accessory"
    assert intel["warnings"]


def test_environment_rankings_are_sorted_descending_by_construction():
    intel = scene_intelligence.build_scene_intelligence(_analysis())
    scores = [r["score"] for r in intel["environment_rankings"]]
    assert scores == sorted(scores, reverse=True)


def test_top_environment_returns_highest_score():
    intel = scene_intelligence.build_scene_intelligence(_analysis())
    top = scene_intelligence.top_environment(intel)
    assert top == intel["primary_environments"][0]


def test_top_environment_raises_on_empty_rankings():
    intel = scene_intelligence.build_scene_intelligence(_analysis())
    intel["environment_rankings"] = []
    try:
        scene_intelligence.top_environment(intel)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_interaction_level_propagates():
    intel = scene_intelligence.build_scene_intelligence(_analysis(), interaction_level=0)
    assert intel["interaction_level"] == 0


def test_save_scene_intelligence_validates_schema(tmp_path):
    intel = scene_intelligence.build_scene_intelligence(_analysis())
    out = tmp_path / "scene-intelligence.json"
    scene_intelligence.save_scene_intelligence(intel, out, schemas_dir=SCHEMAS_DIR)
    assert out.exists()
