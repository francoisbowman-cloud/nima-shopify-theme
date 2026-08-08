"""v0.3 Block 4 — Edge Integration Engine.

v0.2's mask (`masking.build_background_mask`) is a hard binary cutoff — a
pixel is either fully product or fully background, no in-between. That
produces two visible defects once composited onto a new background: a
faint white/light halo (leftover studio-background color bleeding into
edge pixels that are really a blend of product+background in the source
JPEG), and jagged, non-anti-aliased edges. This module is a second,
optional refinement pass over an existing cutout+mask — it never re-derives
the mask from scratch, only softens and cleans up the edge band.

Two independent steps, both small and reproducible:
1. `refine_alpha` — feathers the hard 0/255 alpha edge with a small blur.
2. `decontaminate_color` — removes sampled background contribution only where
   alpha is high enough for the inverse blend to be numerically stable.

Important: the feathered alpha is a geometric coverage estimate, not a measured
source compositing alpha. Very small feathered alpha values must therefore not
be used as divisors for aggressive color extrapolation; doing so can clamp RGB
channels to 0/255 and manufacture a fringe before the perspective warp.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

SCHEMA_NAME = "edge-refinement-metadata.schema.json"

DEFAULT_FEATHER_RADIUS = 1.2
_MAX_FEATHER_RADIUS = 3.0
# Below this alpha, decontamination is intentionally skipped. These pixels
# contribute very little visually, while inverse-blend extrapolation becomes
# unstable because feathered alpha is not the original source blend fraction.
MIN_DECONTAMINATION_ALPHA = 64


class EdgeRefinementError(ValueError):
    pass


def sample_background_color(image_path: Path) -> tuple[int, int, int]:
    """Corner-average background color estimate."""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    corners = [img.getpixel((0, 0)), img.getpixel((w - 1, 0)), img.getpixel((0, h - 1)), img.getpixel((w - 1, h - 1))]
    r = sum(c[0] for c in corners) // 4
    g = sum(c[1] for c in corners) // 4
    b = sum(c[2] for c in corners) // 4
    return (r, g, b)


def refine_alpha(mask: Image.Image, *, feather_radius: float = DEFAULT_FEATHER_RADIUS) -> Image.Image:
    if not (0 <= feather_radius <= _MAX_FEATHER_RADIUS):
        raise EdgeRefinementError(f"feather_radius {feather_radius} outside [0, {_MAX_FEATHER_RADIUS}]")
    alpha = mask.split()[-1]
    feathered = alpha.filter(ImageFilter.GaussianBlur(radius=feather_radius))
    refined = mask.convert("RGBA").copy()
    refined.putalpha(feathered)
    return refined


def decontaminate_color(cutout: Image.Image, refined_mask: Image.Image, bg_color: tuple[int, int, int]) -> Image.Image:
    """Reduce sampled-background contamination in the feathered edge band.

    Fully opaque pixels are preserved exactly. For very low feathered alpha,
    RGB is preserved rather than inverse-extrapolated because dividing by a
    near-zero geometric alpha can create artificial 0/255 channel saturation.
    """
    if cutout.size != refined_mask.size:
        raise EdgeRefinementError("cutout and refined_mask must be the same size")

    rgb = cutout.convert("RGB")
    alpha = refined_mask.split()[-1]

    rgb_px = rgb.load()
    alpha_px = alpha.load()
    out = Image.new("RGBA", cutout.size)
    out_px = out.load()
    bg_r, bg_g, bg_b = bg_color

    width, height = cutout.size
    for y in range(height):
        for x in range(width):
            a = alpha_px[x, y]
            if a == 0:
                out_px[x, y] = (0, 0, 0, 0)
                continue

            r, g, b = rgb_px[x, y]
            if a == 255 or a < MIN_DECONTAMINATION_ALPHA:
                out_px[x, y] = (r, g, b, a)
                continue

            a_frac = a / 255.0
            new_r = max(0, min(255, round(bg_r + (r - bg_r) / a_frac)))
            new_g = max(0, min(255, round(bg_g + (g - bg_g) / a_frac)))
            new_b = max(0, min(255, round(bg_b + (b - bg_b) / a_frac)))
            out_px[x, y] = (new_r, new_g, new_b, a)
    return out


def refine_edges(
    cutout: Image.Image,
    mask: Image.Image,
    source_image_path: Path,
    *,
    feather_radius: float = DEFAULT_FEATHER_RADIUS,
) -> tuple[Image.Image, Image.Image, dict]:
    """Full Block 4 pass: feather + guarded decontamination."""
    bg_color = sample_background_color(source_image_path)
    refined_mask = refine_alpha(mask, feather_radius=feather_radius)
    refined_cutout = decontaminate_color(cutout, refined_mask, bg_color)

    metadata = {
        "feather_radius": feather_radius,
        "background_color_rgb": list(bg_color),
        "decontamination_applied": True,
    }
    return refined_cutout, refined_mask, metadata
