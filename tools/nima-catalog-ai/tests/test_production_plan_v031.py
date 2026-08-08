from src.config import TOOL_ROOT
from src.production_plan_v031 import build_production_generation_plan_v031
from tests.conftest import DEFAULT_ANALYSIS

SCHEMAS_DIR = TOOL_ROOT / "schemas"


def _entry(plan, output_type):
    return next(item for item in plan["outputs"] if item["type"] == output_type)


def test_refined_plan_requires_uniform_pure_white_background():
    plan = build_production_generation_plan_v031(
        analysis=DEFAULT_ANALYSIS,
        outputs_requested=["refined"],
        schemas_dir=SCHEMAS_DIR,
    )
    refined = _entry(plan, "refined")
    assert plan["policy_version"] == "0.3.1"
    assert refined["asset_role"] == "commerce-primary"
    assert refined["background_policy"] == "commerce-white-background"
    assert refined["required_background"] == "#FFFFFF"
    assert "pure white" in refined["background"].lower()
    assert "#FFFFFF" in refined["background"]
    assert any("no cream" in rule.lower() for rule in refined["mandatory_rules"])
    assert any("not uniform #FFFFFF" in criterion for criterion in refined["rejection_criteria"])


def test_lifestyle_plan_remains_contextual_editorial():
    plan = build_production_generation_plan_v031(
        analysis=DEFAULT_ANALYSIS,
        outputs_requested=["lifestyle"],
        schemas_dir=SCHEMAS_DIR,
    )
    lifestyle = _entry(plan, "lifestyle")
    assert lifestyle["asset_role"] == "contextual-editorial"
    assert lifestyle["background_policy"] == "contextual-scene-background"
    assert lifestyle["required_background"] is None
    assert "home environment" in lifestyle["background"].lower()


def test_policy_is_applied_per_output_in_mixed_plan():
    plan = build_production_generation_plan_v031(
        analysis=DEFAULT_ANALYSIS,
        outputs_requested=["refined", "lifestyle"],
        schemas_dir=SCHEMAS_DIR,
    )
    refined = _entry(plan, "refined")
    lifestyle = _entry(plan, "lifestyle")
    assert refined["background_policy"] != lifestyle["background_policy"]
    assert refined["asset_role"] != lifestyle["asset_role"]
