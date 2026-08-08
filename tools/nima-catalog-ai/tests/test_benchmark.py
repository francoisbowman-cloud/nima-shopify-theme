from PIL import Image

from src import benchmark


def test_build_comparison_image_creates_file(tmp_path):
    v02 = Image.new("RGB", (100, 100), (200, 100, 50))
    v03 = Image.new("RGB", (100, 100), (50, 200, 100))
    out = tmp_path / "comparison-v02-v03.jpg"
    result = benchmark.build_comparison_image(v02_result=v02, v03_result=v03, output_path=out)
    assert result == out
    assert out.exists()


def test_build_full_comparison_contact_sheet_creates_file(tmp_path):
    img = Image.new("RGB", (100, 100), (150, 150, 150))
    out = tmp_path / "comparison-full.jpg"
    result = benchmark.build_full_comparison_contact_sheet(
        source=img, cutout=img, background=img, v02_result=img, v03_result=img, output_path=out
    )
    assert result == out
    assert out.exists()
