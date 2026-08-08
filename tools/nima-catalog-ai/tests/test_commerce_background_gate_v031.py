import pytest
from PIL import Image, ImageDraw

from src.commerce_background_gate import (
    CommerceBackgroundGateError,
    evaluate_commerce_white_background,
)


def _mask(size=(100, 100)):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((30, 30, 70, 70), fill=255)
    return mask


def test_uniform_white_background_passes():
    image = Image.new("RGB", (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 30, 70, 70), fill=(60, 50, 40))
    report = evaluate_commerce_white_background(image, _mask())
    assert report["passed"] is True
    assert report["status"] == "pass"
    assert report["required_background"] == "#FFFFFF"
    assert report["white_ratio"] == 1.0


def test_off_white_background_rejects():
    image = Image.new("RGB", (100, 100), (242, 240, 236))
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 30, 70, 70), fill=(60, 50, 40))
    report = evaluate_commerce_white_background(image, _mask())
    assert report["passed"] is False
    assert report["status"] == "reject"


def test_small_isolated_nonwhite_noise_can_stay_within_ratio_tolerance():
    image = Image.new("RGB", (100, 100), (255, 255, 255))
    image.putpixel((0, 0), (250, 250, 250))
    report = evaluate_commerce_white_background(image, _mask())
    assert report["passed"] is True


def test_large_gray_patch_rejects_even_when_corners_are_white():
    image = Image.new("RGB", (100, 100), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 20, 99), fill=(230, 230, 230))
    report = evaluate_commerce_white_background(image, _mask())
    assert report["passed"] is False
    assert report["white_ratio"] < report["min_white_ratio"]


def test_size_mismatch_is_rejected():
    with pytest.raises(CommerceBackgroundGateError):
        evaluate_commerce_white_background(Image.new("RGB", (10, 10)), Image.new("L", (9, 10)))


def test_no_background_pixels_is_rejected():
    with pytest.raises(CommerceBackgroundGateError):
        evaluate_commerce_white_background(Image.new("RGB", (10, 10), "white"), Image.new("L", (10, 10), 255))
