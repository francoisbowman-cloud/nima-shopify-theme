"""v0.3 Block 3 — Perspective Match Engine.

v0.2's compositor only ever applied a uniform scale — correct for occupancy,
but wrong for a product photographed top-down/frontal once it's placed into
a scene shot at eye level: it reads as a flat card leaning upright rather
than a mat lying on the floor (see Real Pilot 01, decision #79). This module
warps the product's real pixels with a planar perspective transform instead
of a uniform scale, for products classified `surface_plane=ground` +
`geometry_class=flat` (see surface.py) — never redraws anything, only
geometrically remaps the same pixels.

No numpy/opencv dependency (keeps this tool isolated, same philosophy as
masking.py) — `find_coeffs` solves the 8x8 perspective-coefficient system
with a small pure-Python Gaussian elimination, the same approach commonly
used in the PIL "quad transform" cookbook recipe.

Known limitation, stated plainly: `compute_ground_quad` is a heuristic
foreshortening formula (tilt + vertical compression), not a real homography
derived from the background photo's actual vanishing points/camera
calibration — v0.3 has no scene depth estimation. It produces a
*plausible* floor-perspective trapezoid, not a *measured* one. See
README.md "Known limitations of v0.3".
"""

from __future__ import annotations

from PIL import Image

Point = tuple[float, float]

DEFAULT_TILT = 0.22
DEFAULT_FORESHORTEN = 0.62
# Guard rails — outside this range the trapezoid reads as a geometry error,
# not a plausible camera angle, so apply_perspective_match refuses instead
# of producing a visibly broken warp.
_TILT_RANGE = (0.0, 0.45)
_FORESHORTEN_RANGE = (0.35, 1.0)


class PerspectiveError(ValueError):
    pass


def _solve_linear_system(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    n = len(rhs)
    augmented = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]

    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(augmented[r][col]))
        if abs(augmented[pivot_row][col]) < 1e-9:
            raise PerspectiveError("Degenerate point configuration — cannot solve perspective coefficients")
        augmented[col], augmented[pivot_row] = augmented[pivot_row], augmented[col]

        pivot = augmented[col][col]
        augmented[col] = [v / pivot for v in augmented[col]]
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor:
                augmented[row] = [mv - factor * cv for mv, cv in zip(augmented[row], augmented[col])]

    return [augmented[i][n] for i in range(n)]


def find_coeffs(dst_quad: list[Point], src_quad: list[Point]) -> list[float]:
    """8 coefficients for PIL's Image.transform(..., Image.PERSPECTIVE, coeffs) —
    dst_quad are 4 points in OUTPUT space, src_quad the corresponding 4 points
    in the SOURCE image, both ordered the same way (e.g. TL, TR, BR, BL)."""
    if len(dst_quad) != 4 or len(src_quad) != 4:
        raise PerspectiveError("Both quads must have exactly 4 points")

    matrix: list[list[float]] = []
    rhs: list[float] = []
    for (x, y), (src_x, src_y) in zip(dst_quad, src_quad):
        matrix.append([x, y, 1, 0, 0, 0, -src_x * x, -src_x * y])
        rhs.append(src_x)
        matrix.append([0, 0, 0, x, y, 1, -src_y * x, -src_y * y])
        rhs.append(src_y)

    return _solve_linear_system(matrix, rhs)


def compute_ground_quad(
    bbox: tuple[int, int, int, int],
    *,
    tilt: float = DEFAULT_TILT,
    foreshorten: float = DEFAULT_FORESHORTEN,
) -> list[Point]:
    """Heuristic floor-perspective trapezoid for a flat object resting on the
    ground, viewed at roughly eye level: the far (top) edge is narrower and
    higher, the near (bottom) edge stays the bbox's full width — mimicking
    the visual convergence a flat mat shows when photographed from a
    standing height instead of top-down.

    tilt: how much narrower the top edge is vs. the bottom (0 = no taper).
    foreshorten: vertical compression of the whole shape (1 = no compression,
    lower = flatter-looking, as a plane receding away from the camera would).
    """
    if not (_TILT_RANGE[0] <= tilt <= _TILT_RANGE[1]):
        raise PerspectiveError(f"tilt {tilt} outside plausible range {_TILT_RANGE}")
    if not (_FORESHORTEN_RANGE[0] <= foreshorten <= _FORESHORTEN_RANGE[1]):
        raise PerspectiveError(f"foreshorten {foreshorten} outside plausible range {_FORESHORTEN_RANGE}")

    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        raise PerspectiveError(f"Degenerate bbox: {bbox}")

    cx = (left + right) / 2
    top_width = width * (1 - tilt)
    new_height = height * foreshorten
    new_top = bottom - new_height

    return [
        (cx - top_width / 2, new_top),  # top-left
        (cx + top_width / 2, new_top),  # top-right
        (right, bottom),  # bottom-right
        (left, bottom),  # bottom-left
    ]


def apply_perspective_match(
    cutout: Image.Image,
    dst_quad: list[Point],
    *,
    canvas_size: tuple[int, int],
) -> Image.Image:
    """Warps `cutout` (RGBA) so its own rectangle maps onto `dst_quad` in a
    `canvas_size` output canvas — real pixels remapped geometrically, never
    redrawn. Returns a canvas-sized RGBA image, transparent outside the
    warped region, ready to be alpha-composited onto a background."""
    if cutout.mode != "RGBA":
        raise PerspectiveError("apply_perspective_match requires an RGBA cutout with real alpha")

    src_quad = [(0, 0), (cutout.width, 0), (cutout.width, cutout.height), (0, cutout.height)]
    coeffs = find_coeffs(dst_quad, src_quad)
    return cutout.transform(
        canvas_size,
        Image.PERSPECTIVE,
        coeffs,
        resample=Image.BICUBIC,
        fillcolor=(0, 0, 0, 0),
    )


def warped_bbox(dst_quad: list[Point]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in dst_quad]
    ys = [p[1] for p in dst_quad]
    return min(xs), min(ys), max(xs), max(ys)
