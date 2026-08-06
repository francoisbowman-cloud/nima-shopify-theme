"""Background-only edit masks for the `product-preserving` strategy.

Heuristic, not ML segmentation: samples the four corners of a studio product
photo as the background color, marks any pixel far from it as foreground,
then keeps only the LARGEST connected foreground blob — everything else is
also treated as editable background. This matters in practice: several Nima
source photos have a secondary element (a color-swatch strip, a dimension
diagram) elsewhere in frame that is not part of the product. Without the
connected-component step, that secondary element gets locked in as
"preserved" right alongside the product, which is wrong — see README.md
"Estrategia product-preserving" for the real example this was found on
(`waterproof-pet-feeding-mats-...` / `01-original.jpg`'s color-swatch grid).

Still deliberately lightweight (PIL + a bounded BFS, no numpy/rembg/
onnxruntime) to keep this an isolated, small tool. Known limitation: only
reliable when the product is the largest distinct-colored region in frame —
a busy multi-object lifestyle shot is not a good `mask_builder` input (which
is why masking is only used for `refined`, never `lifestyle`/`in-use`).
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image

# Connected-component analysis runs on a downsampled copy so the BFS stays
# fast (bounded to at most this many pixels) regardless of the source
# photo's real resolution.
_COMPONENT_ANALYSIS_MAX_DIM = 256


def _color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def _sample_background_color(img: Image.Image) -> tuple[int, int, int]:
    w, h = img.size
    corners = [img.getpixel((0, 0)), img.getpixel((w - 1, 0)), img.getpixel((0, h - 1)), img.getpixel((w - 1, h - 1))]
    r = sum(c[0] for c in corners) // 4
    g = sum(c[1] for c in corners) // 4
    b = sum(c[2] for c in corners) // 4
    return (r, g, b)


def _largest_component_mask(foreground: Image.Image) -> Image.Image:
    """foreground: mode "1" (or "L" thresholded), True/255 = candidate foreground.

    Returns a same-size mode "1" image with only the largest 4-connected
    foreground blob kept, everything else cleared — drops disconnected
    secondary elements (swatch strips, diagrams) that happen to also differ
    from the sampled background color.
    """
    w, h = foreground.size
    pixels = foreground.load()
    visited = bytearray(w * h)
    best_component: list[int] = []
    best_size = 0

    for start_y in range(h):
        for start_x in range(w):
            idx = start_y * w + start_x
            if visited[idx] or not pixels[start_x, start_y]:
                continue
            component: list[int] = []
            queue = deque([(start_x, start_y)])
            visited[idx] = 1
            while queue:
                x, y = queue.popleft()
                component.append(y * w + x)
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        nidx = ny * w + nx
                        if not visited[nidx] and pixels[nx, ny]:
                            visited[nidx] = 1
                            queue.append((nx, ny))
            if len(component) > best_size:
                best_size = len(component)
                best_component = component

    result = Image.new("1", (w, h), 0)
    result_pixels = result.load()
    for flat_idx in best_component:
        result_pixels[flat_idx % w, flat_idx // w] = 1
    return result


def build_background_mask(image_path: Path, *, tolerance: float = 28.0) -> Image.Image:
    """Return an RGBA mask: product opaque (preserved), background transparent (editable).

    Only the single largest connected non-background blob is preserved —
    secondary elements elsewhere in frame are treated as editable background.
    """
    img = Image.open(image_path).convert("RGB")
    bg_color = _sample_background_color(img)

    scale = min(1.0, _COMPONENT_ANALYSIS_MAX_DIM / max(img.size))
    small_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    small_img = img.resize(small_size) if scale < 1.0 else img

    small_pixels = small_img.load()
    candidate = Image.new("1", small_img.size, 0)
    candidate_pixels = candidate.load()
    for y in range(small_img.height):
        for x in range(small_img.width):
            candidate_pixels[x, y] = 0 if _color_distance(small_pixels[x, y], bg_color) <= tolerance else 1

    kept_small = _largest_component_mask(candidate)
    kept_full = kept_small.resize(img.size, Image.NEAREST)

    mask = Image.new("RGBA", img.size)
    mask_pixels = mask.load()
    kept_pixels = kept_full.load()
    for y in range(img.height):
        for x in range(img.width):
            mask_pixels[x, y] = (0, 0, 0, 255 if kept_pixels[x, y] else 0)
    return mask


def save_mask(mask: Image.Image, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    mask.save(path, "PNG")
    return path


def bounding_box(mask: Image.Image) -> tuple[int, int, int, int]:
    """(left, top, right, bottom) of the opaque (preserved/product) region."""
    alpha = mask.split()[-1]
    bbox = alpha.point(lambda a: 255 if a > 127 else 0).getbbox()
    if bbox is None:
        raise ValueError("Mask has no opaque (product) pixels — cannot compute a bounding box")
    return bbox


def crop_to_target_occupancy(
    image: Image.Image,
    mask: Image.Image,
    *,
    target_min_pct: float,
    target_max_pct: float,
) -> tuple[Image.Image, Image.Image, dict]:
    """Deterministic square (1:1) crop, no resampling of product pixels — a
    pure window move over the same-resolution source. The crop window is
    never smaller than the product's own bounding box, so this can only
    remove background, never cut into the product.

    Square-only (matches the storefront card's fixed 1:1 `.pcard__media` box
    — see README "Storefront framing"). Returns (cropped_image, cropped_mask,
    diagnostics) with occupancy_before_pct / occupancy_after_pct / crop_box /
    hit_target_range.
    """
    occupancy_before = measure_occupancy_pct(mask)
    left, top, right, bottom = bounding_box(mask)
    box_w, box_h = right - left, bottom - top
    product_area = sum(1 for value in mask.split()[-1].getdata() if value > 127)

    target_mid_pct = (target_min_pct + target_max_pct) / 2
    ideal_side = (product_area / (target_mid_pct / 100)) ** 0.5
    # Hard floor: the crop can never be smaller than the product's own
    # bounding box in either dimension, or it would cut the product.
    min_side_for_containment = max(box_w, box_h)
    side = max(ideal_side, min_side_for_containment)

    max_square_side = min(image.width, image.height)
    if min_side_for_containment > max_square_side:
        # A square crop containing the full product would exceed the source
        # image's shorter dimension — cropping further would cut the
        # product, so leave the frame as-is instead of risking that.
        diagnostics = {
            "occupancy_before_pct": occupancy_before,
            "occupancy_after_pct": occupancy_before,
            "crop_box": [0, 0, image.width, image.height],
            "hit_target_range": target_min_pct <= occupancy_before <= target_max_pct,
            "note": "product bounding box exceeds the source image's shorter side — no crop applied to avoid cutting the product",
        }
        return image.copy(), mask.copy(), diagnostics

    crop_w = crop_h = min(round(side), max_square_side)

    cx, cy = (left + right) / 2, (top + bottom) / 2
    crop_left = max(0, min(image.width - crop_w, round(cx - crop_w / 2)))
    crop_top = max(0, min(image.height - crop_h, round(cy - crop_h / 2)))
    # If the product bbox is near an edge, the centered window may still clip
    # it — nudge the window (never shrink it) so the full bbox stays inside.
    crop_left = min(crop_left, left)
    crop_top = min(crop_top, top)
    crop_right = max(crop_left + crop_w, right)
    crop_bottom = max(crop_top + crop_h, bottom)
    crop_right = min(crop_right, image.width)
    crop_bottom = min(crop_bottom, image.height)
    crop_left = max(0, crop_right - crop_w)
    crop_top = max(0, crop_bottom - crop_h)
    box = (crop_left, crop_top, crop_left + crop_w, crop_top + crop_h)

    cropped_image = image.crop(box)
    cropped_mask = mask.crop(box)
    occupancy_after = measure_occupancy_pct(cropped_mask)

    diagnostics = {
        "occupancy_before_pct": occupancy_before,
        "occupancy_after_pct": occupancy_after,
        "crop_box": list(box),
        "hit_target_range": target_min_pct <= occupancy_after <= target_max_pct,
    }
    return cropped_image, cropped_mask, diagnostics


def measure_occupancy_pct(mask: Image.Image) -> float:
    """% of pixels marked as product (opaque) — a proxy for how much of the
    frame the product occupies, used as a framing diagnostic, not an
    automated pass/fail gate."""
    alpha = mask.split()[-1]
    histogram = alpha.histogram()
    total = sum(histogram)
    if total == 0:
        return 0.0
    opaque = sum(count for value, count in enumerate(histogram) if value > 127)
    return round(100 * opaque / total, 1)
