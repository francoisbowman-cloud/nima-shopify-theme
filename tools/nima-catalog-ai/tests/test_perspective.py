import pytest
from PIL import Image, ImageDraw

from src import perspective


def _cutout(size=(200, 100)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, size[0] - 1, size[1] - 1), fill=(80, 60, 40, 255))
    return img


def test_compute_ground_quad_produces_narrower_top_than_bottom():
    bbox = (300, 700, 700, 1000)
    quad = perspective.compute_ground_quad(bbox)
    top_left, top_right, bottom_right, bottom_left = quad
    top_width = top_right[0] - top_left[0]
    bottom_width = bottom_right[0] - bottom_left[0]
    assert top_width < bottom_width


def test_compute_ground_quad_bottom_edge_matches_bbox():
    bbox = (300, 700, 700, 1000)
    quad = perspective.compute_ground_quad(bbox)
    _, _, bottom_right, bottom_left = quad
    assert bottom_left == (300, 1000)
    assert bottom_right == (700, 1000)


def test_compute_ground_quad_rejects_out_of_range_tilt():
    with pytest.raises(perspective.PerspectiveError):
        perspective.compute_ground_quad((0, 0, 100, 100), tilt=0.9)


def test_compute_ground_quad_rejects_out_of_range_foreshorten():
    with pytest.raises(perspective.PerspectiveError):
        perspective.compute_ground_quad((0, 0, 100, 100), foreshorten=0.1)


def test_compute_ground_quad_rejects_degenerate_bbox():
    with pytest.raises(perspective.PerspectiveError):
        perspective.compute_ground_quad((100, 100, 100, 100))


def test_find_coeffs_identity_transform_is_stable():
    quad = [(0, 0), (100, 0), (100, 100), (0, 100)]
    coeffs = perspective.find_coeffs(quad, quad)
    assert coeffs[0] == pytest.approx(1, abs=1e-6)
    assert coeffs[4] == pytest.approx(1, abs=1e-6)
    assert coeffs[2] == pytest.approx(0, abs=1e-6)
    assert coeffs[5] == pytest.approx(0, abs=1e-6)


def test_apply_perspective_match_returns_canvas_sized_rgba():
    cutout = _cutout()
    quad = perspective.compute_ground_quad((300, 700, 700, 1000))
    result = perspective.apply_perspective_match(cutout, quad, canvas_size=(1024, 1024))
    assert result.size == (1024, 1024)
    assert result.mode == "RGBA"


def test_apply_perspective_match_preserves_product_pixels_present():
    cutout = _cutout()
    quad = perspective.compute_ground_quad((300, 700, 700, 1000))
    result = perspective.apply_perspective_match(cutout, quad, canvas_size=(1024, 1024))
    alpha = result.split()[-1]
    assert alpha.getbbox() is not None


def test_apply_perspective_match_transparent_outside_quad():
    cutout = _cutout()
    quad = perspective.compute_ground_quad((300, 700, 700, 1000))
    result = perspective.apply_perspective_match(cutout, quad, canvas_size=(1024, 1024))
    assert result.getpixel((10, 10))[3] == 0


def test_apply_perspective_match_requires_rgba():
    cutout = Image.new("RGB", (100, 50), (1, 2, 3))
    quad = perspective.compute_ground_quad((0, 0, 100, 50))
    with pytest.raises(perspective.PerspectiveError):
        perspective.apply_perspective_match(cutout, quad, canvas_size=(200, 200))


def test_perspective_warp_does_not_reintroduce_white_halo_from_hidden_rgb():
    """Regression for v0.3.1: transparent studio-white RGB must not bleed
    into semi-transparent pixels created by the bicubic perspective warp."""
    cutout = Image.new("RGBA", (80, 50), (255, 255, 255, 0))
    draw = ImageDraw.Draw(cutout)
    draw.rectangle((10, 10, 69, 39), fill=(35, 45, 55, 255))

    quad = [(45, 45), (155, 45), (170, 125), (30, 125)]
    warped = perspective.apply_perspective_match(cutout, quad, canvas_size=(200, 160))

    edge_pixels = []
    for r, g, b, a in warped.getdata():
        if 0 < a < 255:
            edge_pixels.append((r, g, b, a))

    assert edge_pixels, "warp should create anti-aliased semi-transparent edge pixels"
    # Product RGB is dark. A white fringe would push one or more channels
    # toward the studio-white source color. Premultiplied resampling keeps
    # those edge colors tied to the product instead.
    assert max(max(r, g, b) for r, g, b, _ in edge_pixels) < 120


def test_fully_transparent_pixels_are_normalized_to_transparent_black_after_warp():
    cutout = Image.new("RGBA", (40, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(cutout)
    draw.rectangle((10, 10, 29, 29), fill=(50, 60, 70, 255))
    quad = [(20, 20), (80, 20), (90, 80), (10, 80)]
    warped = perspective.apply_perspective_match(cutout, quad, canvas_size=(100, 100))
    assert warped.getpixel((0, 0)) == (0, 0, 0, 0)


def test_find_coeffs_rejects_wrong_length_quads():
    with pytest.raises(perspective.PerspectiveError):
        perspective.find_coeffs([(0, 0)], [(0, 0)])


def test_warped_bbox_matches_quad_extents():
    quad = [(10, 20), (90, 25), (95, 80), (5, 75)]
    left, top, right, bottom = perspective.warped_bbox(quad)
    assert left == 5
    assert top == 20
    assert right == 95
    assert bottom == 80
