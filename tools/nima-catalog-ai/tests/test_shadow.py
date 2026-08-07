from PIL import Image

from src.shadow import ShadowParams, build_shadow_layer


def _cutout(size=(80, 60)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    for y in range(10, 50):
        for x in range(10, 70):
            img.putpixel((x, y), (100, 90, 80, 255))
    return img


def test_disabled_shadow_returns_fully_transparent_layer():
    cutout = _cutout()
    layer = build_shadow_layer(cutout, (200, 200), params=ShadowParams(enabled=False))
    assert layer.size == (200, 200)
    assert layer.getextrema()[3] == (0, 0)  # alpha channel entirely zero


def test_enabled_shadow_produces_nonzero_alpha():
    cutout = _cutout()
    layer = build_shadow_layer(cutout, (200, 200), params=ShadowParams(enabled=True, opacity=0.3))
    alpha_max = layer.getextrema()[3][1]
    assert alpha_max > 0


def test_shadow_opacity_caps_max_alpha():
    cutout = _cutout()
    layer = build_shadow_layer(cutout, (200, 200), params=ShadowParams(enabled=True, opacity=0.2, blur_radius=1))
    alpha_max = layer.getextrema()[3][1]
    assert alpha_max <= round(255 * 0.2) + 2  # +2 tolerance for blur edge rounding


def test_shadow_offset_shifts_layer():
    cutout = _cutout()
    layer_a = build_shadow_layer(cutout, (200, 200), params=ShadowParams(offset_x=0, offset_y=0, blur_radius=1))
    layer_b = build_shadow_layer(cutout, (200, 200), params=ShadowParams(offset_x=50, offset_y=50, blur_radius=1))
    bbox_a = layer_a.split()[-1].getbbox()
    bbox_b = layer_b.split()[-1].getbbox()
    assert bbox_a != bbox_b


def test_shadow_params_as_dict_roundtrip():
    params = ShadowParams(blur_radius=10, opacity=0.5, offset_x=2, offset_y=3)
    d = params.as_dict()
    assert d == {"enabled": True, "blur_radius": 10, "opacity": 0.5, "offset_x": 2, "offset_y": 3}
