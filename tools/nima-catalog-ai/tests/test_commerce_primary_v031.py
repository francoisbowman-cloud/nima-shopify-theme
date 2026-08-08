from PIL import Image, ImageDraw

from src.commerce_primary_v031 import render_commerce_primary


def _source(path):
    image = Image.new("RGB", (320, 240), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((60, 70, 260, 180), radius=15, fill=(70, 70, 75))
    image.save(path)


def test_commerce_primary_is_square_exact_white_and_passes_gate(tmp_path):
    source = tmp_path / "source.png"
    _source(source)
    result = render_commerce_primary(source_image_path=source, canvas_size=(512, 512))
    assert result.image.size == (512, 512)
    assert result.image.mode == "RGB"
    assert result.image.getpixel((0, 0)) == (255, 255, 255)
    assert result.image.getpixel((511, 511)) == (255, 255, 255)
    assert result.gate_report["passed"] is True
    assert result.gate_report["required_background"] == "#FFFFFF"


def test_commerce_primary_preserves_nonwhite_product_pixels(tmp_path):
    source = tmp_path / "source.png"
    _source(source)
    result = render_commerce_primary(source_image_path=source, canvas_size=(512, 512))
    pixels = list(result.image.getdata())
    assert any(max(px) < 150 for px in pixels)


def test_commerce_primary_rejects_extreme_occupancy(tmp_path):
    source = tmp_path / "source.png"
    _source(source)
    try:
        render_commerce_primary(source_image_path=source, target_occupancy=0.95)
        assert False, "expected ValueError"
    except ValueError:
        pass
