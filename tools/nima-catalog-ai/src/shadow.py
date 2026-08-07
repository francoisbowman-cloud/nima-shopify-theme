"""v0.2 Block 6 — contact shadow: a first, deliberately simple pass at
grounding the composited product in its new scene.

Pipeline: product alpha -> shadow mask -> blur -> offset -> opacity -> composited
under the product, over the background. No perspective/relighting modeling —
just enough to keep the product from reading as "pasted on".
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageFilter


@dataclass
class ShadowParams:
    enabled: bool = True
    blur_radius: int = 18
    opacity: float = 0.22
    offset_x: int = 4
    offset_y: int = 12

    def as_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "blur_radius": self.blur_radius,
            "opacity": self.opacity,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
        }


def build_shadow_layer(cutout: Image.Image, canvas_size: tuple[int, int], *, params: ShadowParams) -> Image.Image:
    """Returns an RGBA layer, canvas-sized, with a soft dark shadow shaped
    like the product's own silhouette (offset + blurred), ready to be pasted
    under the product onto the background."""
    if not params.enabled:
        return Image.new("RGBA", canvas_size, (0, 0, 0, 0))

    alpha = cutout.split()[-1]
    silhouette = Image.new("RGBA", cutout.size, (0, 0, 0, 0))
    black = Image.new("RGBA", cutout.size, (0, 0, 0, 255))
    silhouette.paste(black, (0, 0), alpha)

    layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    layer.paste(silhouette, (params.offset_x, params.offset_y), silhouette)
    blurred = layer.filter(ImageFilter.GaussianBlur(radius=params.blur_radius))

    faded_alpha = blurred.split()[-1].point(lambda a: round(a * params.opacity))
    blurred.putalpha(faded_alpha)
    return blurred
