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
    # Identity mapping: a=1,b=0,c=0,d=0,e=1,f=0,g=0,h=0
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
    assert alpha.getbbox() is not None  # some opaque content landed on the canvas


def test_apply_perspective_match_transparent_outside_quad():
    cutout = _cutout()
    quad = perspective.compute_ground_quad((300, 700, 700, 1000))
    result = perspective.apply_perspective_match(cutout, quad, canvas_size=(1024, 1024))
    assert result.getpixel((10, 10))[3] == 0  # far corner, outside the warped quad


def test_apply_perspective_match_requires_rgba():
    cutout = Image.new("RGB", (100, 50), (1, 2, 3))
    quad = perspective.compute_ground_quad((0, 0, 100, 50))
    with pytest.raises(perspective.PerspectiveError):
        perspective.apply_perspective_match(cutout, quad, canvas_size=(200, 200))


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
