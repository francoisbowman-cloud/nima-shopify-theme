from pathlib import Path

import pytest

from src import placement

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _seg_meta(width=400, height=200):
    return {
        "source_width": 1000,
        "source_height": 800,
        "bounding_box": {"left": 0, "top": 0, "right": width, "bottom": height},
        "product_pixel_width": width,
        "product_pixel_height": height,
        "product_area_ratio": 0.3,
        "edge_confidence": 0.9,
        "has_transparency": True,
        "backend": "heuristic",
        "warnings": [],
    }


def test_build_placement_spec_hits_target_occupancy_within_tolerance():
    spec = placement.build_placement_spec(_seg_meta())
    occupancy = placement.measure_occupancy(spec)
    assert abs(occupancy - placement.DEFAULT_TARGET_OCCUPANCY) < 0.05


def test_build_placement_spec_no_clipping_by_default():
    spec = placement.build_placement_spec(_seg_meta())
    assert placement.check_clipping(spec) is False


def test_build_placement_spec_preserves_aspect_ratio():
    spec = placement.build_placement_spec(_seg_meta(width=400, height=200))
    assert placement.check_aspect_ratio_preserved(spec)


def test_build_placement_spec_respects_safe_zone():
    spec = placement.build_placement_spec(_seg_meta())
    assert placement.check_safe_zone_violation(spec) is False


def test_build_placement_spec_bottom_center_anchor_sits_on_ground_plane():
    spec = placement.build_placement_spec(_seg_meta(), anchor="bottom-center")
    assert spec["product"]["final_bbox"]["bottom"] == spec["ground_plane"]["y"]


def test_build_placement_spec_rejects_invalid_occupancy_bounds():
    with pytest.raises(ValueError):
        placement.build_placement_spec(_seg_meta(), min_occupancy=0.5, max_occupancy=0.3, target_occupancy=0.4)


def test_build_placement_spec_scales_down_when_target_exceeds_safe_zone():
    # A large margin_pct shrinks the safe zone well below the target bbox
    # size — the spec must scale the bbox down to fit rather than clip or crash.
    spec = placement.build_placement_spec(
        _seg_meta(width=900, height=900),
        target_occupancy=0.6,
        min_occupancy=0.05,
        max_occupancy=0.6,
        margin_pct=0.3,
    )
    assert placement.check_clipping(spec) is False
    assert any("safe zone" in w for w in spec["warnings"])


def test_check_scale_plausible_rejects_absurd_target():
    spec = placement.build_placement_spec(
        _seg_meta(), target_occupancy=0.05, min_occupancy=0.05, max_occupancy=0.05
    )
    assert placement.check_scale_plausible(spec)  # 0.05 is at the absolute floor, still plausible


def test_undersized_product_flagged_out_of_range_when_min_is_tight():
    spec = placement.build_placement_spec(_seg_meta(), target_occupancy=0.3, min_occupancy=0.29, max_occupancy=0.31)
    assert placement.check_occupancy_in_range(spec)


def test_save_placement_spec_validates_against_schema(tmp_path):
    spec = placement.build_placement_spec(_seg_meta())
    out = tmp_path / "placement-spec.json"
    placement.save_placement_spec(spec, out, schemas_dir=SCHEMAS_DIR)
    assert out.exists()


def test_empty_bounding_box_produces_warning():
    meta = _seg_meta(width=0, height=0)
    meta["product_pixel_width"] = 0
    meta["product_pixel_height"] = 0
    spec = placement.build_placement_spec(meta)
    assert any("empty bounding box" in w for w in spec["warnings"])
