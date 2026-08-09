"""v0.3 Block 4 — Edge Integration Engine.

v0.2's mask (`masking.build_background_mask`) is a hard binary cutoff — a
pixel is either fully product or fully background, no in-between. That
produces two visible defects once composited onto a new background: a
faint white/light halo (leftover studio-background color bleeding into
edge pixels that are really a blend of product+background in the source
JPEG), and jagged, non-anti-aliased edges. This module is a second,
optional refinement pass over an existing cutout+mask — it never re-derives
the mask from scratch, only softens and cleans up the edge band.

Three small, reproducible steps:
1. `refine_alpha` feathers the hard 0/255 alpha edge and collapses the
   synthetic low-alpha tail that is known to carry studio-background RGB.
2. `refine_background_edge_matte` suppresses only boundary pixels whose
   source RGB is still very close to the sampled studio background. It is
   constrained to the geometric edge band so product interior pixels are
   never modified.
3. `decontaminate_color` removes sampled background contribution where alpha
   is high enough for inverse blending to remain numerically stable.

Important: the feathered alpha is a geometric coverage estimate, not a measured
source compositing alpha. The matte therefore uses source RGB evidence only to
reduce coverage near the boundary; it does not infer or redraw product color.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

SCHEMA_NAME = "edge-refinement-metadata.schema.json"

DEFAULT_FEATHER_RADIUS = 1.2
_MAX_FEATHER_RADIUS = 3.0
MIN_DECONTAMINATION_ALPHA = 64
DEFAULT_FEATHER_ALPHA_CUTOFF = 64

# Conservative distance in RGB Euclidean space. Only pixels within the
# geometric edge band AND this close to the sampled studio background have
# their coverage reduced. The value is intentionally below masking.py's
# foreground tolerance (28): this is a cleanup for obvious background carry,
# not a second segmentation pass.
DEFAULT_BACKGROUND_EDGE_DISTANCE = 24.0


class EdgeRefinementError(ValueError):
    pass


def _color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def sample_background_color(image_path: Path) -> tuple[int, int, int]:
    """Corner-average background color estimate."""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    corners = [
        img.getpixel((0, 0)),
        img.getpixel((w - 1, 0)),
        img.getpixel((0, h - 1)),
        img.getpixel((w - 1, h - 1)),
    ]
    r = sum(c[0] for c in corners) // 4
    g = sum(c[1] for c in corners) // 4
    b = sum(c[2] for c in corners) // 4
    return (r, g, b)


def refine_alpha(
    mask: Image.Image,
    *,
    feather_radius: float = DEFAULT_FEATHER_RADIUS,
    alpha_cutoff: int = DEFAULT_FEATHER_ALPHA_CUTOFF,
) -> Image.Image:
    if not (0 <= feather_radius <= _MAX_FEATHER_RADIUS):
        raise EdgeRefinementError(
            f"feather_radius {feather_radius} outside [0, {_MAX_FEATHER_RADIUS}]"
        )
    if not (0 <= alpha_cutoff <= 255):
        raise EdgeRefinementError("alpha_cutoff must be within [0, 255]")

    alpha = mask.split()[-1]
    feathered = alpha.filter(ImageFilter.GaussianBlur(radius=feather_radius))
    cut = feathered.point(lambda a: 0 if 0 < a < alpha_cutoff else a)
    refined = mask.convert("RGBA").copy()
    refined.putalpha(cut)
    return refined


def refine_background_edge_matte(
    cutout: Image.Image,
    refined_mask: Image.Image,
    bg_color: tuple[int, int, int],
    *,
    background_edge_distance: float = DEFAULT_BACKGROUND_EDGE_DISTANCE,
    alpha_cutoff: int = DEFAULT_FEATHER_ALPHA_CUTOFF,
) -> Image.Image:
    """Reduce alpha only for background-like pixels in the product edge band.

    Two edge classes are eligible:
    - semi-transparent pixels introduced by `refine_alpha`;
    - one-pixel-wide boundary pixels from the original hard product mask.

    For eligible pixels whose source RGB remains close to the sampled studio
    background, alpha is scaled by color distance/background_edge_distance.
    If that pushes coverage below `alpha_cutoff`, it collapses to zero.

    This addresses both residual halo mechanisms found on the real feeding-mat
    asset: partially-transparent white carry and a small number of fully opaque
    hard-mask boundary pixels that were actually studio-background transition
    pixels. Deep interior pixels are never touched.
    """
    if cutout.size != refined_mask.size:
        raise EdgeRefinementError("cutout and refined_mask must be the same size")
    if background_edge_distance <= 0:
        raise EdgeRefinementError("background_edge_distance must be > 0")
    if not (0 <= alpha_cutoff <= 255):
        raise EdgeRefinementError("alpha_cutoff must be within [0, 255]")

    rgb = cutout.convert("RGB")
    hard_alpha = cutout.split()[-1]
    refined_alpha = refined_mask.split()[-1]

    # MinFilter erodes the binary hard mask by one pixel. A hard-mask pixel
    # that disappears under this erosion lies on the geometric boundary.
    eroded_hard_alpha = hard_alpha.filter(ImageFilter.MinFilter(3))

    rgb_px = rgb.load()
    hard_px = hard_alpha.load()
    eroded_px = eroded_hard_alpha.load()
    alpha_px = refined_alpha.load()

    out_alpha = refined_alpha.copy()
    out_px = out_alpha.load()

    width, height = cutout.size
    for y in range(height):
        for x in range(width):
            a = alpha_px[x, y]
            if a == 0:
                continue

            is_semitransparent_edge = a < 255
            is_hard_mask_boundary = hard_px[x, y] > 0 and eroded_px[x, y] == 0
            if not (is_semitransparent_edge or is_hard_mask_boundary):
                continue

            distance = _color_distance(rgb_px[x, y], bg_color)
            if distance >= background_edge_distance:
                continue

            scaled_alpha = round(a * (distance / background_edge_distance))
            out_px[x, y] = 0 if 0 < scaled_alpha < alpha_cutoff else scaled_alpha

    refined = refined_mask.convert("RGBA").copy()
    refined.putalpha(out_alpha)
    return refined


def decontaminate_color(
    cutout: Image.Image,
    refined_mask: Image.Image,
    bg_color: tuple[int, int, int],
) -> Image.Image:
    """Reduce sampled-background contamination in the refined edge band.

    Fully opaque pixels are preserved exactly. Very low alpha is preserved
    rather than inverse-extrapolated because dividing by a near-zero geometric
    alpha can create artificial channel saturation.
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
    """Full Block 4 pass: feather, edge-matte suppression, decontamination."""
    bg_color = sample_background_color(source_image_path)
    refined_mask = refine_alpha(mask, feather_radius=feather_radius)
    refined_mask = refine_background_edge_matte(cutout, refined_mask, bg_color)
    refined_cutout = decontaminate_color(cutout, refined_mask, bg_color)

    metadata = {
        "feather_radius": feather_radius,
        "background_color_rgb": list(bg_color),
        "decontamination_applied": True,
    }
    return refined_cutout, refined_mask, metadata
