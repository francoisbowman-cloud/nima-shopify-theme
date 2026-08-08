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


def test_refine_edges_metadata_validates_schema(tmp_path):
    from src import file_utils

    photo = tmp_path / "p.jpg"
    _make_product_photo(photo)
    seg = segmentation.segment_product(photo)
    _, _, meta = edge_refinement.refine_edges(seg.cutout, seg.mask, photo)
    schema = file_utils.load_schema(SCHEMAS_DIR, edge_refinement.SCHEMA_NAME)
    file_utils.validate_against_schema(meta, schema)
