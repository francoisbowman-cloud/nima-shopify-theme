"""Automatic commerce-white-background gate for Nima Catalog AI v0.3.1."""

from __future__ import annotations

from PIL import Image


class CommerceBackgroundGateError(ValueError):
    pass


def _mask_alpha(product_mask: Image.Image) -> Image.Image:
    """Return a single-channel product-opacity mask for common PIL modes."""
    if product_mask.mode == "L":
        return product_mask
    if product_mask.mode in {"RGBA", "LA"}:
        return product_mask.split()[-1]
    return product_mask.convert("L")


def evaluate_commerce_white_background(
    image: Image.Image,
    product_mask: Image.Image,
    *,
    channel_tolerance: int = 6,
    min_white_ratio: float = 0.995,
    background_alpha_max: int = 8,
) -> dict:
    """Measure whether known background pixels are consistently pure white.

    `product_mask` follows the Catalog AI convention: product pixels are opaque
    and background pixels transparent/zero. Grayscale (`L`) and alpha-bearing
    masks are accepted. Only confidently-background pixels (value <=
    background_alpha_max) are scored, so anti-aliased product edges do not
    create false failures.
    """
    if image.size != product_mask.size:
        raise CommerceBackgroundGateError("image and product_mask must have the same size")
    if not (0 <= channel_tolerance <= 32):
        raise CommerceBackgroundGateError("channel_tolerance must be within [0, 32]")
    if not (0.0 < min_white_ratio <= 1.0):
        raise CommerceBackgroundGateError("min_white_ratio must be within (0, 1]")
    if not (0 <= background_alpha_max <= 64):
        raise CommerceBackgroundGateError("background_alpha_max must be within [0, 64]")

    rgb = image.convert("RGB")
    alpha = _mask_alpha(product_mask)
    rgb_px = rgb.load()
    alpha_px = alpha.load()

    background_pixels = 0
    white_pixels = 0
    worst_channel_distance = 0

    threshold = 255 - channel_tolerance
    for y in range(image.height):
        for x in range(image.width):
            if alpha_px[x, y] > background_alpha_max:
                continue
            background_pixels += 1
            r, g, b = rgb_px[x, y]
            distance = max(255 - r, 255 - g, 255 - b)
            worst_channel_distance = max(worst_channel_distance, distance)
            if r >= threshold and g >= threshold and b >= threshold:
                white_pixels += 1

    if background_pixels == 0:
        raise CommerceBackgroundGateError("product_mask exposes no confident background pixels to evaluate")

    white_ratio = white_pixels / background_pixels
    passed = white_ratio >= min_white_ratio
    return {
        "gate": "commerce-white-background",
        "passed": passed,
        "status": "pass" if passed else "reject",
        "required_background": "#FFFFFF",
        "background_pixels_evaluated": background_pixels,
        "white_pixels": white_pixels,
        "white_ratio": round(white_ratio, 6),
        "min_white_ratio": min_white_ratio,
        "channel_tolerance": channel_tolerance,
        "worst_channel_distance": worst_channel_distance,
    }
