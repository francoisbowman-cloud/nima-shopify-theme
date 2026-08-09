from PIL import Image

from src import compositor, placement
from src.shadow import ShadowParams


def _placement_spec_for(product_w, product_h, canvas=(1000, 1000)):
    meta = {
        "source_width": 2000,
        "source_height": 2000,
        "bounding_box": {"left": 0, "top": 0, "right": product_w, "bottom": product_h},
        "product_pixel_width": product_w,
        "product_pixel_height": product_h,
        "product_area_ratio": 0.3,
        "edge_confidence": 0.9,
        "has_transparency": True,
        "backend": "heuristic",
        "warnings": [],
    }
    return placement.build_placement_spec(meta, canvas_width=canvas[0], canvas_height=canvas[1])


def _opaque_cutout(size=(200, 100), color=(200, 50, 50, 255)):
    return Image.new("RGBA", size, color)


def test_compose_scene_returns_canvas_sized_composite():
    spec = _placement_spec_for(200, 100)
    background = Image.new("RGB", (1000, 1000), (240, 240, 240))
    cutout = _opaque_cutout()
    result = compositor.compose_scene(background=background, cutout=cutout, placement_spec=spec)
    assert result["composite"].size == (1000, 1000)


def test_compose_scene_product_visible_at_paste_location():
    spec = _placement_spec_for(200, 100)
    background = Image.new("RGB", (1000, 1000), (240, 240, 240))
    cutout = _opaque_cutout(color=(10, 200, 10, 255))
    result = compositor.compose_scene(background=background, cutout=cutout, placement_spec=spec)
    l, t, r, b = result["paste_box"]
    cx, cy = (l + r) // 2, (t + b) // 2
    pixel = result["composite"].getpixel((cx, cy))
    assert pixel == (10, 200, 10)


def test_compose_scene_background_untouched_outside_product_area():
    spec = _placement_spec_for(100, 100)
    background = Image.new("RGB", (1000, 1000), (5, 5, 5))
    cutout = _opaque_cutout(size=(100, 100), color=(250, 250, 250, 255))
    result = compositor.compose_scene(
        background=background, cutout=cutout, placement_spec=spec, shadow_params=ShadowParams(enabled=False)
    )
    corner_pixel = result["composite"].getpixel((5, 5))
    assert corner_pixel == (5, 5, 5)


def test_compose_scene_preserves_aspect_ratio_no_stretch():
    spec = _placement_spec_for(400, 100)  # 4:1 aspect ratio
    background = Image.new("RGB", (1000, 1000), (240, 240, 240))
    cutout = _opaque_cutout(size=(400, 100))
    result = compositor.compose_scene(background=background, cutout=cutout, placement_spec=spec)
    scaled = result["scaled_cutout"]
    assert abs((scaled.width / scaled.height) - 4.0) < 0.05


def test_compose_scene_with_shadow_enabled_darkens_area_near_product():
    spec = _placement_spec_for(200, 100)
    background = Image.new("RGB", (1000, 1000), (240, 240, 240))
    cutout = _opaque_cutout()
    result = compositor.compose_scene(
        background=background, cutout=cutout, placement_spec=spec, shadow_params=ShadowParams(enabled=True, opacity=0.4)
    )
    shadow_alpha_max = result["shadow_layer"].getextrema()[3][1]
    assert shadow_alpha_max > 0


def test_save_composite_writes_png(tmp_path):
    img = Image.new("RGB", (10, 10), (1, 2, 3))
    out = tmp_path / "composite-base.png"
    compositor.save_composite(img, out)
    assert out.exists()
