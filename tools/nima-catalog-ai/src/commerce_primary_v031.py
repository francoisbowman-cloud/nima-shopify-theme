"""v0.3.1 deterministic commerce-primary renderer.

Primary catalog imagery is not a lifestyle generation problem. The product's
real pixels are segmented, edge-refined, cropped to the foreground bounds,
scaled into a square commerce canvas, and composited onto exact #FFFFFF.
No model call occurs here and no perspective warp is applied: the source view
is preserved for a clean packshot rather than reinterpreted as a scene.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from . import edge_refinement, segmentation
from .commerce_background_gate import evaluate_commerce_white_background

DEFAULT_CANVAS_SIZE = (1536, 1536)
DEFAULT_OCCUPANCY = 0.82


@dataclass
class CommercePrimaryResult:
    image: Image.Image
    product_mask: Image.Image
    gate_report: dict
    segmentation_metadata: dict
    edge_refinement_metadata: dict


def _foreground_crop(image: Image.Image) -> Image.Image:
    bbox = image.split()[-1].getbbox()
    if bbox is None:
        raise ValueError("Cannot build commerce-primary: segmentation found no foreground")
    return image.crop(bbox)


def render_commerce_primary(
    *,
    source_image_path: Path,
    canvas_size: tuple[int, int] = DEFAULT_CANVAS_SIZE,
    target_occupancy: float = DEFAULT_OCCUPANCY,
) -> CommercePrimaryResult:
    if not 0.5 <= target_occupancy <= 0.9:
        raise ValueError("target_occupancy must be between 0.5 and 0.9")

    seg = segmentation.segment_product(source_image_path)
    refined_cutout, refined_mask, edge_meta = edge_refinement.refine_edges(
        seg.cutout, seg.mask, source_image_path
    )
    product = _foreground_crop(refined_cutout)

    max_w = max(1, round(canvas_size[0] * target_occupancy))
    max_h = max(1, round(canvas_size[1] * target_occupancy))
    scale = min(max_w / product.width, max_h / product.height)
    new_size = (max(1, round(product.width * scale)), max(1, round(product.height * scale)))
    product = product.resize(new_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", canvas_size, (255, 255, 255))
    x = (canvas_size[0] - product.width) // 2
    y = (canvas_size[1] - product.height) // 2
    canvas.paste(product.convert("RGB"), (x, y), product.split()[-1])

    mask_canvas = Image.new("L", canvas_size, 0)
    mask_canvas.paste(product.split()[-1], (x, y))
    gate = evaluate_commerce_white_background(canvas, mask_canvas)

    return CommercePrimaryResult(
        image=canvas,
        product_mask=mask_canvas,
        gate_report=gate,
        segmentation_metadata=seg.metadata,
        edge_refinement_metadata=edge_meta,
    )


def save_commerce_primary(result: CommercePrimaryResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    result.image.save(output_dir / "commerce-primary.png", "PNG")
    result.product_mask.save(output_dir / "commerce-primary-mask.png", "PNG")
