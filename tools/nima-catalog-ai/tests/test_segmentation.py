from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from src import segmentation


def _make_product_photo(path: Path) -> None:
    img = Image.new("RGB", (200, 160), (250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle((40, 40, 160, 120), fill=(30, 30, 30))
    img.save(path, "JPEG")


def test_segment_product_returns_mask_and_metadata(tmp_path):
    photo = tmp_path / "source.jpg"
    _make_product_photo(photo)

    result = segmentation.segment_product(photo)

    assert result.cutout.mode == "RGBA"
    assert result.mask.mode == "RGBA"
    meta = result.metadata
    assert meta["source_width"] == 200
    assert meta["source_height"] == 160
    assert meta["product_pixel_width"] > 0
    assert meta["product_pixel_height"] > 0
    assert meta["has_transparency"] is True
    assert meta["backend"] == "heuristic"
    assert 0 <= meta["product_area_ratio"] <= 1
    assert 0 <= meta["edge_confidence"] <= 1


def test_segment_product_cutout_preserves_product_pixels(tmp_path):
    photo = tmp_path / "source.jpg"
    _make_product_photo(photo)
    original = Image.open(photo).convert("RGB")

    result = segmentation.segment_product(photo)
    bbox = result.metadata["bounding_box"]
    cx = (bbox["left"] + bbox["right"]) // 2
    cy = (bbox["top"] + bbox["bottom"]) // 2

    cutout_pixel = result.cutout.getpixel((cx, cy))
    original_pixel = original.getpixel((cx, cy))
    assert cutout_pixel[:3] == original_pixel
    assert cutout_pixel[3] == 255


def test_segment_product_unknown_backend_raises(tmp_path):
    photo = tmp_path / "source.jpg"
    _make_product_photo(photo)
    with pytest.raises(ValueError):
        segmentation.segment_product(photo, backend="does-not-exist")


def test_register_backend_extension_point(tmp_path):
    photo = tmp_path / "source.jpg"
    _make_product_photo(photo)

    def fake_backend(image_path):
        img = Image.open(image_path).convert("RGB")
        mask = Image.new("RGBA", img.size, (0, 0, 0, 255))
        return mask, ["fake backend used"]

    segmentation.register_backend("fake", fake_backend)
    result = segmentation.segment_product(photo, backend="fake")
    assert result.metadata["backend"] == "fake"
    assert result.metadata["warnings"] == ["fake backend used"]


def test_segment_product_flat_uniform_image_flags_warning(tmp_path):
    photo = tmp_path / "flat.jpg"
    Image.new("RGB", (100, 100), (128, 128, 128)).save(photo, "JPEG")
    result = segmentation.segment_product(photo)
    assert result.metadata["has_transparency"] is False


def test_save_segmentation_writes_files_and_validates_schema(tmp_path):
    photo = tmp_path / "source.jpg"
    _make_product_photo(photo)
    result = segmentation.segment_product(photo)

    schemas_dir = Path(__file__).resolve().parent.parent / "schemas"
    out = tmp_path / "out"
    segmentation.save_segmentation(
        result,
        cutout_path=out / "product-cutout.png",
        mask_path=out / "product-mask.png",
        metadata_path=out / "segmentation-metadata.json",
        schemas_dir=schemas_dir,
    )
    assert (out / "product-cutout.png").exists()
    assert (out / "product-mask.png").exists()
    assert (out / "segmentation-metadata.json").exists()
