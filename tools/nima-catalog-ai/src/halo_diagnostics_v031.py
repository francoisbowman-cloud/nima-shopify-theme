"""Offline v0.3.1 halo root-cause diagnostic using a real local source asset.

No API calls. The command writes stage images and edge statistics so a real
`nima-catalog-images/` asset can be inspected before/after segmentation,
edge refinement and perspective warp.

Usage:
  python -m src.halo_diagnostics_v031 path/to/source.jpg --out halo-diagnostic
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from . import edge_refinement, perspective, segmentation


def _edge_stats(image: Image.Image) -> dict:
    rgba = image.convert("RGBA")
    partial = []
    low_alpha = []
    saturated = []
    for r, g, b, a in rgba.getdata():
        if 0 < a < 255:
            partial.append((r, g, b, a))
            if a < edge_refinement.MIN_DECONTAMINATION_ALPHA:
                low_alpha.append((r, g, b, a))
            if r in (0, 255) or g in (0, 255) or b in (0, 255):
                saturated.append((r, g, b, a))
    return {
        "partial_alpha_pixels": len(partial),
        "low_alpha_pixels": len(low_alpha),
        "saturated_partial_alpha_pixels": len(saturated),
        "max_rgb_partial_alpha": max((max(r, g, b) for r, g, b, _ in partial), default=None),
    }


def _composite_preview(layer: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    bg = Image.new("RGBA", layer.size, (*color, 255))
    return Image.alpha_composite(bg, layer.convert("RGBA")).convert("RGB")


def run(source: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    seg = segmentation.segment_product(source)
    refined_cutout, refined_mask, edge_meta = edge_refinement.refine_edges(seg.cutout, seg.mask, source)

    seg.cutout.save(out_dir / "01-segmented-cutout.png", "PNG")
    refined_mask.save(out_dir / "02-refined-mask.png", "PNG")
    refined_cutout.save(out_dir / "03-refined-cutout.png", "PNG")

    w, h = refined_cutout.size
    canvas_size = (w, h)
    margin_x = max(1, round(w * 0.08))
    margin_y = max(1, round(h * 0.08))
    bbox = (margin_x, margin_y, w - margin_x, h - margin_y)
    quad = perspective.compute_ground_quad(bbox)
    warped = perspective.apply_perspective_match(refined_cutout, quad, canvas_size=canvas_size)
    warped.save(out_dir / "04-perspective-warp.png", "PNG")

    _composite_preview(refined_cutout, (255, 255, 255)).save(out_dir / "05-refined-on-white.png", "PNG")
    _composite_preview(refined_cutout, (32, 32, 32)).save(out_dir / "06-refined-on-dark.png", "PNG")
    _composite_preview(warped, (255, 255, 255)).save(out_dir / "07-warped-on-white.png", "PNG")
    _composite_preview(warped, (32, 32, 32)).save(out_dir / "08-warped-on-dark.png", "PNG")

    report = {
        "source": str(source),
        "background_color_rgb": edge_meta["background_color_rgb"],
        "min_decontamination_alpha": edge_refinement.MIN_DECONTAMINATION_ALPHA,
        "segmented": _edge_stats(seg.cutout),
        "refined": _edge_stats(refined_cutout),
        "warped": _edge_stats(warped),
        "interpretation": {
            "refined_saturation_increase": "points to edge decontamination",
            "warp_only_saturation_increase": "points to geometric resampling",
            "no_numeric_saturation_but_visible_fringe": "inspect source RGB contamination / mask geometry visually",
        },
    }
    (out_dir / "halo-diagnostic.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, default=Path("halo-diagnostic-v031"))
    args = parser.parse_args(argv)
    report = run(args.source, args.out)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
