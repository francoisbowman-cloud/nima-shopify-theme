from src.build_brief import build_generation_plan, detect_product_preserving
from src.config import TOOL_ROOT
from tests.conftest import DEFAULT_ANALYSIS

SCHEMAS_DIR = TOOL_ROOT / "schemas"

WORDMARK_ANALYSIS = {
    **DEFAULT_ANALYSIS,
    "critical_visual_features": [
        "A single integrated paw-shaped tab with one central pad and four toe pads",
        "A small embossed wordmark near the corner",
    ],
}


def test_in_use_omitted_when_not_eligible():
    plan = build_generation_plan(
        analysis=DEFAULT_ANALYSIS,  # eligible_outputs.in_use is False
        outputs_requested=["refined", "lifestyle", "in-use"],
        schemas_dir=SCHEMAS_DIR,
    )
    types_present = {o["type"] for o in plan["outputs"]}
    assert types_present == {"refined", "lifestyle"}
    assert "in-use" not in types_present


def test_in_use_included_when_eligible():
    analysis = {**DEFAULT_ANALYSIS, "eligible_outputs": {"refined": True, "lifestyle": True, "in_use": True}}
    plan = build_generation_plan(
        analysis=analysis, outputs_requested=["in-use"], schemas_dir=SCHEMAS_DIR
    )
    assert {o["type"] for o in plan["outputs"]} == {"in-use"}


def test_secondary_references_exclude_primary():
    plan = build_generation_plan(
        analysis=DEFAULT_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR
    )
    entry = plan["outputs"][0]
    assert entry["primary_reference"] == "01-original.jpg"
    assert "01-original.jpg" not in entry["secondary_references"]


def test_mandatory_rules_include_forbidden_changes():
    plan = build_generation_plan(
        analysis=DEFAULT_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR
    )
    rules = " ".join(plan["outputs"][0]["mandatory_rules"])
    assert "do not change the mat shape" in rules


def test_detect_product_preserving_true_for_wordmark_and_small_parts():
    assert detect_product_preserving(WORDMARK_ANALYSIS) is True


def test_detect_product_preserving_false_for_plain_product():
    assert detect_product_preserving(DEFAULT_ANALYSIS) is False


def test_refined_gets_background_only_mask_strategy_when_preserving():
    plan = build_generation_plan(
        analysis=WORDMARK_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR
    )
    entry = plan["outputs"][0]
    assert entry["strategy"] == "product-preserving"
    assert entry["mask_strategy"] == "background-only"
    assert entry["secondary_references"] == []  # masking only supports a single reference image


def test_lifestyle_gets_no_mask_but_hardened_rules_when_preserving():
    plan = build_generation_plan(
        analysis=WORDMARK_ANALYSIS, outputs_requested=["lifestyle"], schemas_dir=SCHEMAS_DIR
    )
    entry = plan["outputs"][0]
    assert entry["strategy"] == "product-preserving"
    assert entry["mask_strategy"] == "none"
    assert any("do not redraw" in rule.lower() for rule in entry["mandatory_rules"])


def test_plain_product_uses_full_generate_strategy():
    plan = build_generation_plan(
        analysis=DEFAULT_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR
    )
    entry = plan["outputs"][0]
    assert entry["strategy"] == "full-generate"
    assert entry["mask_strategy"] == "none"


def test_framing_rules_present_and_card_aspect_ratio_matches_theme():
    plan = build_generation_plan(
        analysis=DEFAULT_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR
    )
    framing = plan["outputs"][0]["framing_rules"]
    assert framing["card_aspect_ratio"] == "1:1"
    assert framing["target_occupancy_pct_min"] < framing["target_occupancy_pct_max"]


# --- product-overrides.json -------------------------------------------------

import copy
import json

from src.build_brief import load_overrides


def test_load_overrides_reads_file(tmp_path):
    (tmp_path / "product-overrides.json").write_text(
        json.dumps({"wordmark_exact_text": "Moki Found"}), encoding="utf-8"
    )
    overrides = load_overrides(tmp_path, schemas_dir=SCHEMAS_DIR)
    assert overrides == {"wordmark_exact_text": "Moki Found"}


def test_load_overrides_missing_file_returns_empty(tmp_path):
    assert load_overrides(tmp_path, schemas_dir=SCHEMAS_DIR) == {}


def test_load_overrides_validates_against_schema(tmp_path):
    (tmp_path / "product-overrides.json").write_text(
        json.dumps({"part_counts": {"toe_pads": "four"}}),  # wrong type — schema wants integer
        encoding="utf-8",
    )
    try:
        load_overrides(tmp_path, schemas_dir=SCHEMAS_DIR)
        assert False, "expected a schema validation error"
    except Exception:
        pass


def test_override_takes_priority_over_inference_in_mandatory_rules():
    overrides = {
        "wordmark_exact_text": "Moki Found",
        "part_counts": {"paw_tab_toe_pads": 4},
    }
    plan_with = build_generation_plan(
        analysis=DEFAULT_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR, overrides=overrides
    )
    rules = " ".join(plan_with["outputs"][0]["mandatory_rules"])
    assert 'wordmark/logo text reads exactly "Moki Found"' in rules
    assert "exact count of paw_tab_toe_pads is 4" in rules

    plan_without = build_generation_plan(
        analysis=DEFAULT_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR
    )
    rules_without = " ".join(plan_without["outputs"][0]["mandatory_rules"])
    assert "Moki Found" not in rules_without


def test_overrides_trigger_product_preserving_even_without_analysis_keywords():
    # DEFAULT_ANALYSIS has no wordmark/tab keywords, so on its own it uses full-generate.
    assert detect_product_preserving(DEFAULT_ANALYSIS) is False
    plan_without = build_generation_plan(
        analysis=DEFAULT_ANALYSIS, outputs_requested=["refined"], schemas_dir=SCHEMAS_DIR
    )
    assert plan_without["outputs"][0]["strategy"] == "full-generate"

    plan_with = build_generation_plan(
        analysis=DEFAULT_ANALYSIS,
        outputs_requested=["refined"],
        schemas_dir=SCHEMAS_DIR,
        overrides={"wordmark_exact_text": "Moki Found"},
    )
    assert plan_with["outputs"][0]["strategy"] == "product-preserving"


def test_building_plan_with_overrides_never_mutates_analysis():
    analysis_copy = copy.deepcopy(DEFAULT_ANALYSIS)
    build_generation_plan(
        analysis=DEFAULT_ANALYSIS,
        outputs_requested=["refined", "lifestyle"],
        schemas_dir=SCHEMAS_DIR,
        overrides={"wordmark_exact_text": "Moki Found", "human_corrections": ["fix the thing"]},
    )
    assert DEFAULT_ANALYSIS == analysis_copy  # untouched — overrides never get written into it
