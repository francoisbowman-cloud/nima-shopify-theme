from PIL import Image

from src import masking


def _studio_photo(tmp_path, *, bg=(250, 248, 243), product_box=(20, 20, 44, 44), product_color=(60, 90, 140)):
    img = Image.new("RGB", (64, 64), color=bg)
    for y in range(product_box[1], product_box[3]):
        for x in range(product_box[0], product_box[2]):
            img.putpixel((x, y), product_color)
    path = tmp_path / "studio.jpg"
    img.save(path, "JPEG")
    return path


def test_mask_marks_product_opaque_and_background_transparent(tmp_path):
    path = _studio_photo(tmp_path)
    mask = masking.build_background_mask(path)

    # background corner -> transparent (editable)
    assert mask.getpixel((0, 0))[3] == 0
    # product center -> opaque (preserved)
    assert mask.getpixel((32, 32))[3] == 255


def test_measure_occupancy_matches_product_area_fraction(tmp_path):
    # product_box avoids all four corners so background color sampling stays clean
    path = _studio_photo(tmp_path, product_box=(8, 0, 40, 64))  # half the frame, corners untouched
    mask = masking.build_background_mask(path)
    occupancy = masking.measure_occupancy_pct(mask)
    assert 45 <= occupancy <= 55


def test_save_mask_writes_png(tmp_path):
    path = _studio_photo(tmp_path)
    mask = masking.build_background_mask(path)
    out = masking.save_mask(mask, tmp_path / "sub" / "mask.png")
    assert out.exists()
    assert Image.open(out).mode == "RGBA"
