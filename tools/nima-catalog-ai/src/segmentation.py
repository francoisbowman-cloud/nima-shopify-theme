"""v0.2 Block 1 — product segmentation & cutout.

Isolates the real product from its source photo so downstream composition
reuses the product's actual pixels instead of asking an image model to
redraw them. The contract (`segment_product`) is deliberately backend-agnostic:
v0.2 ships one heuristic backend (reusing the connected-component approach
from `masking.py`), but callers select a backend by name so `rembg`, SAM, or
a manually supplied mask can be swapped in later without touching any
caller of `segment_product`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from . import file_utils, masking

SCHEMA_NAME = "segmentation-metadata.schema.json"


@dataclass
class SegmentationResult:
    cutout: Image.Image  # RGBA, background transparent, product pixels untouched
    mask: Image.Image  # RGBA, product opaque / background transparent (same convention as masking.py)
    metadata: dict


def _edge_confidence(mask: Image.Image) -> float:
    """Heuristic proxy: fraction of the mask's bounding box actually covered by
    opaque pixels — a tight, solid blob scores near 1.0, a sparse/noisy one
    scores lower. Not a substitute for a real segmentation confidence score,
    but gives the metadata a value that responds to how clean the cut was.
    """
    alpha = mask.split()[-1]
    bbox = alpha.getbbox()
    if bbox is None:
        return 0.0
    left, top, right, bottom = bbox
    box_area = max(1, (right - left) * (bottom - top))
    opaque = sum(1 for v in alpha.crop(bbox).getdata() if v > 127)
    return round(min(1.0, opaque / box_area), 3)


def _heuristic_backend(image_path: Path) -> tuple[Image.Image, dict]:
    """Reuses masking.py's background-color + largest-connected-component
    heuristic. Returns (mask, warnings)."""
    warnings: list[str] = []
    try:
        mask = masking.build_background_mask(image_path)
    except Exception as exc:  # pragma: no cover - PIL only raises on unreadable files
        raise ValueError(f"segmentation failed for {image_path}: {exc}") from exc

    alpha = mask.split()[-1]
    if alpha.getbbox() is None:
        warnings.append("no foreground pixels found — background color sampling likely failed on a low-contrast photo")
    return mask, warnings


_BACKENDS = {
    "heuristic": _heuristic_backend,
}


def register_backend(name: str, fn) -> None:
    """Extension point for rembg/SAM/manual-mask backends — not wired to any
    default in v0.2, but callers (and future providers) can register one and
    pass backend=name to segment_product without any change here."""
    _BACKENDS[name] = fn


def segment_product(image_path: Path, *, backend: str = "heuristic") -> SegmentationResult:
    if backend not in _BACKENDS:
        raise ValueError(f"Unknown segmentation backend {backend!r}. Registered: {sorted(_BACKENDS)}")

    img = Image.open(image_path).convert("RGB")
    mask, warnings = _BACKENDS[backend](image_path)

    cutout = Image.new("RGBA", img.size)
    cutout.paste(img.convert("RGBA"), (0, 0))
    cutout.putalpha(mask.split()[-1])

    bbox = mask.split()[-1].getbbox()
    has_transparency = bbox is not None and bbox != (0, 0, img.width, img.height)
    if bbox is not None:
        left, top, right, bottom = bbox
        product_pixel_width, product_pixel_height = right - left, bottom - top
    else:
        left = top = right = bottom = 0
        product_pixel_width = product_pixel_height = 0

    metadata = {
        "source_width": img.width,
        "source_height": img.height,
        "bounding_box": {"left": left, "top": top, "right": right, "bottom": bottom},
        "product_pixel_width": product_pixel_width,
        "product_pixel_height": product_pixel_height,
        "product_area_ratio": masking.measure_occupancy_pct(mask) / 100.0,
        "edge_confidence": _edge_confidence(mask),
        "has_transparency": has_transparency,
        "backend": backend,
        "warnings": warnings,
    }
    return SegmentationResult(cutout=cutout, mask=mask, metadata=metadata)


def save_segmentation(
    result: SegmentationResult,
    *,
    cutout_path: Path,
    mask_path: Path,
    metadata_path: Path,
    schemas_dir: Path | None = None,
) -> None:
    cutout_path.parent.mkdir(parents=True, exist_ok=True)
    result.cutout.save(cutout_path, "PNG")
    masking.save_mask(result.mask, mask_path)
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(result.metadata, schema)
    file_utils.write_json(metadata_path, result.metadata)
