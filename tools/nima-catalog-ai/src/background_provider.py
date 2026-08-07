"""v0.2 Block 13 — swappable background-generation backend.

`BackgroundProvider` is the seam between a background_request (Block 4) and
an actual background image. v0.2 ships and uses only `FixtureBackgroundProvider`
(local files / synthetic images, offline). `OpenAIBackgroundProvider` exists
so the interface is proven out, but it is inert by construction: calling it
raises instead of touching the network. Wiring it up for real is future work,
explicitly out of scope for this phase (see PASO 0 / "NO consumir API de
OpenAI sin autorización explícita posterior").
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PIL import Image


class BackgroundProvider(Protocol):
    def generate_background(self, request: dict) -> Image.Image:
        ...


class FixtureBackgroundProvider:
    """Returns a pre-existing local image, or a flat-color synthetic image if
    no fixture path is given — used by tests and the offline demo (Block 10).
    """

    def __init__(self, fixture_path: Path | None = None, *, fallback_color: tuple[int, int, int] = (235, 227, 211)):
        self.fixture_path = fixture_path
        self.fallback_color = fallback_color

    def generate_background(self, request: dict) -> Image.Image:
        canvas = request["canvas"]
        size = (canvas["width"], canvas["height"])
        if self.fixture_path is not None:
            img = Image.open(self.fixture_path).convert("RGB")
            if img.size != size:
                img = img.resize(size)
            return img
        return Image.new("RGB", size, self.fallback_color)


class OpenAIBackgroundProvider:
    """Placeholder for a future real backend. Deliberately never calls the
    network in v0.2 — instantiating it is fine, but generate_background()
    always raises so it cannot be used by accident in an offline pipeline
    or test run."""

    def __init__(self, *, api_key: str | None = None, model: str = "gpt-image-2"):
        self.api_key = api_key
        self.model = model

    def generate_background(self, request: dict) -> Image.Image:
        raise NotImplementedError(
            "OpenAIBackgroundProvider is a v0.2 interface placeholder only. "
            "Real API calls are out of scope for this phase — see CLAUDE.md / "
            "the v0.2 prompt's safety rules. Use FixtureBackgroundProvider for "
            "offline pipeline runs and tests."
        )
