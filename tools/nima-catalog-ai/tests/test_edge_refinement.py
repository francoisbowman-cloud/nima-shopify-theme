from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from src import edge_refinement, segmentation

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _make_product_photo(path: Path) -> None:
    img = Image.new("RGB", (200, 160), (250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle((40, 40, 160, 120), fill=(30, 30, 30))
    img.save(path, "JPEG")


def _make_edge_fixture() -> tuple[Image.Image, Image.Image]:
    cutout = Image.new("RGBA", (7, 7), (255, 255, 255, 0))
    mask = Image.new("RGBA", (7, 7), (0, 0, 0, 0))
    for y in range(1, 6):
        for x in range(1, 6):
            cutout.putpixel((x, y), (30, 30, 30, 255))
            mask.putpixel((x, y), (0, 0, 0, 255))
    return cutout, mask


def test_sample_background_color_reads_corners(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    color = edge_refinement.sample_background_color(photo)
    assert color == (250, 250, 250)


def test_refine_alpha_produces_intermediate_alpha_values(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    refined_mask = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5)
    alpha_values = set(refined_mask.split()[-1].getdata())
    assert any(0 < v < 255 for v in alpha_values)


def test_refine_alpha_rejects_excessive_radius():
    mask = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
    with pytest.raises(edge_refinement.EdgeRefinementError):
        edge_refinement.refine_alpha(mask, feather_radius=10)


def test_refine_alpha_rejects_invalid_cutoff():
    mask = Image.new("RGBA", (10, 10), (0, 0, 0, 255))
    with pytest.raises(edge_refinement.EdgeRefinementError):
        edge_refinement.refine_alpha(mask, alpha_cutoff=300)


def test_decontaminate_color_leaves_fully_opaque_pixels_unchanged(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    refined_mask = edge_refinement.refine_alpha(seg.mask, feather_radius=1.0)
    decontaminated = edge_refinement.decontaminate_color(seg.cutout, refined_mask, (250, 250, 250))
    center_pixel = decontaminated.getpixel((100, 80))
    assert center_pixel[3] == 255
    assert center_pixel[:3] == (30, 30, 30)


def test_decontaminate_color_preserves_low_alpha_rgb_instead_of_saturating():
    cutout = Image.new("RGBA", (1, 1), (240, 180, 120, 255))
    refined_mask = Image.new("RGBA", (1, 1), (0, 0, 0, 8))
    result = edge_refinement.decontaminate_color(cutout, refined_mask, (200, 200, 200))
    assert result.getpixel((0, 0)) == (240, 180, 120, 8)


def test_decontaminate_color_still_operates_in_stable_alpha_band():
    cutout = Image.new("RGBA", (1, 1), (180, 180, 180, 255))
    refined_mask = Image.new("RGBA", (1, 1), (0, 0, 0, 128))
    result = edge_refinement.decontaminate_color(cutout, refined_mask, (250, 250, 250))
    r, g, b, a = result.getpixel((0, 0))
    assert a == 128
    assert (r, g, b) != (180, 180, 180)
    assert max(r, g, b) < 180


def test_decontaminate_color_requires_matching_sizes():
    cutout = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
    mask = Image.new("RGBA", (60, 60), (0, 0, 0, 255))
    with pytest.raises(edge_refinement.EdgeRefinementError):
        edge_refinement.decontaminate_color(cutout, mask, (255, 255, 255))


def test_refine_edges_returns_metadata_with_params(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    refined_cutout, refined_mask, meta = edge_refinement.refine_edges(seg.cutout, seg.mask, photo)
    assert meta["feather_radius"] == edge_refinement.DEFAULT_FEATHER_RADIUS
    assert meta["background_color_rgb"] == [250, 250, 250]
    assert meta["decontamination_applied"] is True
    assert refined_cutout.size == seg.cutout.size
    assert refined_mask.size == seg.mask.size


def test_refine_alpha_produces_no_pixels_below_cutoff(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    refined_mask = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5)
    alpha_values = set(refined_mask.split()[-1].getdata())
    assert not any(0 < v < edge_refinement.DEFAULT_FEATHER_ALPHA_CUTOFF for v in alpha_values)


def test_refine_alpha_zero_stays_zero(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    refined_mask = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5)
    assert refined_mask.getpixel((0, 0))[3] == 0


def test_refine_alpha_preserves_values_at_or_above_cutoff(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    cutoff_alpha = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5).split()[-1]
    raw_alpha = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5, alpha_cutoff=0).split()[-1]
    w, h = cutoff_alpha.size
    cutoff_px, raw_px = cutoff_alpha.load(), raw_alpha.load()
    for y in range(h):
        for x in range(w):
            raw_v = raw_px[x, y]
            if raw_v >= edge_refinement.DEFAULT_FEATHER_ALPHA_CUTOFF:
                assert cutoff_px[x, y] == raw_v


def test_refine_alpha_leaves_opaque_center_untouched(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    refined_mask = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5)
    assert refined_mask.getpixel((100, 80))[3] == 255


def test_refine_alpha_cutoff_does_not_materially_shrink_product_bbox(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    hard_bbox = seg.mask.split()[-1].getbbox()
    refined_bbox = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5).split()[-1].getbbox()
    tolerance = 3
    assert refined_bbox[0] >= hard_bbox[0] - tolerance
    assert refined_bbox[1] >= hard_bbox[1] - tolerance
    assert refined_bbox[2] <= hard_bbox[2] + tolerance
    assert refined_bbox[3] <= hard_bbox[3] + tolerance


def test_decontaminate_color_after_refine_alpha_has_no_low_alpha_saturation(tmp_path):
    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    refined_mask = edge_refinement.refine_alpha(seg.mask, feather_radius=1.5)
    bg_color = edge_refinement.sample_background_color(photo)
    decontaminated = edge_refinement.decontaminate_color(seg.cutout, refined_mask, bg_color)
    for _, _, _, a in decontaminated.getdata():
        assert not (0 < a < edge_refinement.MIN_DECONTAMINATION_ALPHA)


def test_background_edge_matte_collapses_background_like_opaque_boundary_pixel():
    cutout, mask = _make_edge_fixture()
    cutout.putpixel((1, 3), (250, 254, 255, 255))
    refined = edge_refinement.refine_background_edge_matte(cutout, mask, (255, 255, 255))
    assert refined.getpixel((1, 3))[3] == 0


def test_background_edge_matte_preserves_distinct_opaque_boundary_pixel():
    cutout, mask = _make_edge_fixture()
    refined = edge_refinement.refine_background_edge_matte(cutout, mask, (255, 255, 255))
    assert refined.getpixel((1, 3))[3] == 255


def test_background_edge_matte_never_touches_deep_interior_even_if_background_like():
    cutout, mask = _make_edge_fixture()
    cutout.putpixel((3, 3), (250, 254, 255, 255))
    refined = edge_refinement.refine_background_edge_matte(cutout, mask, (255, 255, 255))
    assert refined.getpixel((3, 3))[3] == 255


def test_background_edge_matte_collapses_background_like_semitransparent_pixel():
    cutout, hard_mask = _make_edge_fixture()
    refined_mask = hard_mask.copy()
    refined_mask.putpixel((1, 3), (0, 0, 0, 87))
    cutout.putpixel((1, 3), (240, 252, 255, 255))
    refined = edge_refinement.refine_background_edge_matte(cutout, refined_mask, (255, 255, 255))
    assert refined.getpixel((1, 3))[3] == 0


def test_background_edge_matte_rejects_invalid_distance():
    cutout, mask = _make_edge_fixture()
    with pytest.raises(edge_refinement.EdgeRefinementError):
        edge_refinement.refine_background_edge_matte(cutout, mask, (255, 255, 255), background_edge_distance=0)


def test_refine_edges_metadata_validates_schema(tmp_path):
    from src import file_utils

    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    _, _, meta = edge_refinement.refine_edges(seg.cutout, seg.mask, photo)
    schema = file_utils.load_schema(SCHEMAS_DIR, edge_refinement.SCHEMA_NAME)
    file_utils.validate_against_schema(meta, schema)
