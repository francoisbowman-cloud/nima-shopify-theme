"""v0.2 Block 5 — deterministic compositor.

Takes a generated/fixture background, a product cutout (Block 1), and a
placement spec (Block 2), and produces composite-base.png by pasting the
product's real pixels onto the background at the planned bbox — no
resampling of the product beyond a single uniform scale to fit its target
box, no redrawing, no AI involved in this step at all.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from . import placement as placement_mod
from . import shadow as shadow_mod
from .shadow import ShadowParams


def _scale_cutout_to_bbox(cutout: Image.Image, bbox_w: int, bbox_h: int) -> Image.Image:
    """Uniform scale preserving aspect ratio — never a non-uniform stretch,
    so the product's real proportions are never distorted."""
    src_w, src_h = cutout.size
    if src_w == 0 or src_h == 0:
        raise ValueError("Cannot scale an empty cutout")
    scale = min(bbox_w / src_w, bbox_h / src_h)
    new_size = (max(1, round(src_w * scale)), max(1, round(src_h * scale)))
    return cutout.resize(new_size, Image.LANCZOS)


def compose_scene(
    *,
    background: Image.Image,
    cutout: Image.Image,
    placement_spec: dict,
    shadow_params: ShadowParams | None = None,
) -> dict:
    """Returns {"composite": Image, "shadow_layer": Image, "scaled_cutout": Image,
    "paste_box": (l,t,r,b)} — callers save whichever layers they need for
    visual-debug output (Block 8)."""
    canvas = placement_spec["canvas"]
    canvas_size = (canvas["width"], canvas["height"])
    if background.size != canvas_size:
        background = background.resize(canvas_size)
    bg = background.convert("RGB")

    left, top, right, bottom = placement_mod.compute_final_bbox(placement_spec)
    bbox_w, bbox_h = right - left, bottom - top
    scaled_cutout = _scale_cutout_to_bbox(cutout, bbox_w, bbox_h)

    # Center the scaled cutout within its bbox (aspect-preserving scale can
    # leave one dimension smaller than the bbox — center rather than stretch).
    paste_x = left + (bbox_w - scaled_cutout.width) // 2
    paste_y = top + (bbox_h - scaled_cutout.height) // 2
    paste_box = (paste_x, paste_y, paste_x + scaled_cutout.width, paste_y + scaled_cutout.height)

    shadow_params = shadow_params or ShadowParams()
    shadow_layer = shadow_mod.build_shadow_layer(scaled_cutout, canvas_size, params=shadow_params)
    # The shadow was built at (0,0)-relative offset; reposition it under the
    # actual paste location by pasting the layer shifted to paste_box origin.
    positioned_shadow = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    positioned_shadow.paste(shadow_layer, (paste_x, paste_y), shadow_layer)

    composite = bg.convert("RGBA")
    composite = Image.alpha_composite(composite, positioned_shadow)
    composite.paste(scaled_cutout, (paste_x, paste_y), scaled_cutout)

    return {
        "composite": composite.convert("RGB"),
        "shadow_layer": positioned_shadow,
        "scaled_cutout": scaled_cutout,
        "paste_box": paste_box,
    }


def save_composite(composite: Image.Image, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    composite.save(path, "PNG")
    return path
