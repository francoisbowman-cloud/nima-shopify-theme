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


# v0.3 Block 5 — surface-aware shadow. build_shadow_layer's shape already
# follows whatever silhouette it's given (see compositor_v03.py, which now
# passes the perspective-warped product so the shadow inherits the same
# trapezoid footprint for free) — this table only tunes blur/opacity/offset
# per geometry_class + surface_plane, since a flat mat lying flush on the
# ground needs a tighter, more perimeter-only contact shadow than a
# volumetric bowl or a soft bed casting more ambient occlusion.
_SURFACE_AWARE_PRESETS: dict[tuple[str, str], ShadowParams] = {
    ("ground", "flat"): ShadowParams(blur_radius=10, opacity=0.28, offset_x=0, offset_y=4),
    ("ground", "soft"): ShadowParams(blur_radius=22, opacity=0.24, offset_x=2, offset_y=10),
    ("ground", "volumetric"): ShadowParams(blur_radius=16, opacity=0.30, offset_x=3, offset_y=8),
    ("ground", "upright"): ShadowParams(blur_radius=14, opacity=0.26, offset_x=2, offset_y=6),
    ("ground", "deformable"): ShadowParams(blur_radius=20, opacity=0.20, offset_x=2, offset_y=8),
}
# Anything not resting on the ground plane (tabletop/wall/shelf/hanging)
# gets a smaller, tighter shadow by default — less vertical drop, since it's
# not sitting in open floor light.
_NON_GROUND_DEFAULT = ShadowParams(blur_radius=8, opacity=0.16, offset_x=1, offset_y=3)


def build_surface_aware_shadow_params(surface_model: dict) -> ShadowParams:
    """Selects shadow params from `surface-model.json` (surface.py) instead
    of the v0.2 generic default — see the preset table above for the
    reasoning per geometry_class/surface_plane combination."""
    key = (surface_model["surface_plane"], surface_model["geometry_class"])
    return _SURFACE_AWARE_PRESETS.get(key, _NON_GROUND_DEFAULT)
