"""v0.2 Block 2 — placement-spec.json: deterministic math for where/how big the
product appears in the final composite.

Nothing here calls an API — occupancy targets, anchoring, and clipping are
all plain arithmetic over the segmentation metadata (Block 1) so the same
inputs always produce the same placement.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils

SCHEMA_NAME = "placement-spec.schema.json"

DEFAULT_TARGET_OCCUPANCY = 0.34
DEFAULT_MIN_OCCUPANCY = 0.24
DEFAULT_MAX_OCCUPANCY = 0.42
# Below this, a product reads as "lost in the scene"; above 0.60 it starts
# looking pasted-in regardless of composition quality — hard rails, not just
# the target/min/max used for the primary occupancy check.
ABSOLUTE_MIN_OCCUPANCY = 0.05
ABSOLUTE_MAX_OCCUPANCY = 0.60


def build_placement_spec(
    segmentation_metadata: dict,
    *,
    canvas_width: int = 1536,
    canvas_height: int = 1536,
    anchor: str = "bottom-center",
    target_occupancy: float = DEFAULT_TARGET_OCCUPANCY,
    min_occupancy: float = DEFAULT_MIN_OCCUPANCY,
    max_occupancy: float = DEFAULT_MAX_OCCUPANCY,
    allow_crop: bool = False,
    margin_pct: float = 0.06,
) -> dict:
    warnings: list[str] = []
    if not (ABSOLUTE_MIN_OCCUPANCY <= min_occupancy <= target_occupancy <= max_occupancy <= ABSOLUTE_MAX_OCCUPANCY):
        raise ValueError(
            f"occupancy bounds out of order/range: min={min_occupancy} target={target_occupancy} "
            f"max={max_occupancy} (must satisfy {ABSOLUTE_MIN_OCCUPANCY} <= min <= target <= max <= {ABSOLUTE_MAX_OCCUPANCY})"
        )

    product_w = segmentation_metadata["product_pixel_width"]
    product_h = segmentation_metadata["product_pixel_height"]
    if product_w <= 0 or product_h <= 0:
        warnings.append("segmentation produced an empty bounding box — placement cannot be computed reliably")
        aspect_ratio = 1.0
    else:
        aspect_ratio = product_w / product_h

    safe_left = round(canvas_width * margin_pct)
    safe_top = round(canvas_height * margin_pct)
    safe_zone = {
        "left": safe_left,
        "top": safe_top,
        "right": canvas_width - safe_left,
        "bottom": canvas_height - safe_top,
    }
    safe_width = safe_zone["right"] - safe_zone["left"]
    safe_height = safe_zone["bottom"] - safe_zone["top"]

    canvas_area = canvas_width * canvas_height
    target_area = canvas_area * target_occupancy
    # Solve for a bbox at the product's own aspect ratio whose area matches
    # target_area: w*h = target_area, w/h = aspect_ratio -> h = sqrt(area/ratio).
    target_h = (target_area / aspect_ratio) ** 0.5
    target_w = target_h * aspect_ratio

    if target_w > safe_width or target_h > safe_height:
        scale = min(safe_width / target_w, safe_height / target_h)
        target_w *= scale
        target_h *= scale
        warnings.append("target occupancy exceeded the safe zone — bbox scaled down to fit")

    bbox_w, bbox_h = round(target_w), round(target_h)

    ground_plane = {"y": safe_zone["bottom"], "depth": round(canvas_height * 0.18)}

    if anchor == "bottom-center":
        bbox_left = round((canvas_width - bbox_w) / 2)
        bbox_bottom = safe_zone["bottom"]
        bbox_top = bbox_bottom - bbox_h
    elif anchor == "center":
        bbox_left = round((canvas_width - bbox_w) / 2)
        bbox_top = round((canvas_height - bbox_h) / 2)
        bbox_bottom = bbox_top + bbox_h
    else:
        raise ValueError(f"Unsupported anchor: {anchor!r} (supported: bottom-center, center)")
    bbox_right = bbox_left + bbox_w

    final_bbox = {"left": bbox_left, "top": bbox_top, "right": bbox_right, "bottom": bbox_bottom}
    final_occupancy = (bbox_w * bbox_h) / canvas_area if canvas_area else 0.0

    spec = {
        "canvas": {"width": canvas_width, "height": canvas_height},
        "product": {
            "anchor": anchor,
            "target_occupancy": round(target_occupancy, 4),
            "min_occupancy": round(min_occupancy, 4),
            "max_occupancy": round(max_occupancy, 4),
            "rotation_degrees": 0,
            "allow_crop": allow_crop,
            "aspect_ratio": round(aspect_ratio, 4),
            "final_bbox": final_bbox,
            "final_occupancy": round(final_occupancy, 4),
        },
        "safe_zone": safe_zone,
        "ground_plane": ground_plane,
        "warnings": warnings,
    }
    return spec


def compute_final_bbox(spec: dict) -> tuple[int, int, int, int]:
    b = spec["product"]["final_bbox"]
    return b["left"], b["top"], b["right"], b["bottom"]


def check_clipping(spec: dict) -> bool:
    """True if the placed bbox would extend outside the canvas."""
    left, top, right, bottom = compute_final_bbox(spec)
    canvas = spec["canvas"]
    return left < 0 or top < 0 or right > canvas["width"] or bottom > canvas["height"]


def check_safe_zone_violation(spec: dict) -> bool:
    left, top, right, bottom = compute_final_bbox(spec)
    zone = spec["safe_zone"]
    return left < zone["left"] or top < zone["top"] or right > zone["right"] or bottom > zone["bottom"]


def measure_occupancy(spec: dict) -> float:
    return spec["product"]["final_occupancy"]


def check_occupancy_in_range(spec: dict) -> bool:
    product = spec["product"]
    return product["min_occupancy"] <= product["final_occupancy"] <= product["max_occupancy"]


def check_aspect_ratio_preserved(spec: dict, *, tolerance: float = 0.02) -> bool:
    """True if the final bbox's aspect ratio still matches the product's own
    (i.e. no non-uniform stretch was introduced when scaling to fit)."""
    left, top, right, bottom = compute_final_bbox(spec)
    bbox_w, bbox_h = right - left, bottom - top
    if bbox_h == 0:
        return False
    bbox_ratio = bbox_w / bbox_h
    return abs(bbox_ratio - spec["product"]["aspect_ratio"]) <= tolerance


def check_scale_plausible(spec: dict) -> bool:
    occupancy = spec["product"]["final_occupancy"]
    return ABSOLUTE_MIN_OCCUPANCY <= occupancy <= ABSOLUTE_MAX_OCCUPANCY


def save_placement_spec(spec: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(spec, schema)
    file_utils.write_json(path, spec)
