"""Explicit, one-call OpenAI background provider for the v0.3.1 real pilot.

Unlike the inert legacy provider, this class is opt-in and requires an already
constructed OpenAIClient. It hard-stops after one generation call so the pilot
cannot silently retry or overspend. The model generates only the empty
contextual environment; the real product is composited afterward.
"""

from __future__ import annotations

from io import BytesIO

from PIL import Image

from . import background
from .openai_client import OpenAIClient, ImageEditResult


class PilotCallBudgetExceeded(RuntimeError):
    pass


class OpenAIBackgroundProviderV031:
    def __init__(
        self,
        *,
        client: OpenAIClient,
        model: str = "gpt-image-2",
        size: str = "1024x1024",
        quality: str = "high",
        max_calls: int = 1,
    ):
        if max_calls != 1:
            raise ValueError("v0.3.1 real pilot is intentionally limited to exactly one allowed API call")
        self.client = client
        self.model = model
        self.size = size
        self.quality = quality
        self.max_calls = max_calls
        self.call_count = 0
        self.last_result: ImageEditResult | None = None

    def generate_background(self, request: dict) -> Image.Image:
        if self.call_count >= self.max_calls:
            raise PilotCallBudgetExceeded("Real Pilot v0.3.1 API budget exhausted; retries are disabled")
        self.call_count += 1
        result = self.client.generate_image(
            model=self.model,
            prompt=background.render_prompt(request),
            size=self.size,
            quality=self.quality,
        )
        self.last_result = result
        image = Image.open(BytesIO(result.image_bytes)).convert("RGB")
        canvas = request["canvas"]
        target_size = (canvas["width"], canvas["height"])
        if image.size != target_size:
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        return image

    def audit_metadata(self) -> dict:
        result = self.last_result
        return {
            "provider": "openai-background-v031",
            "model": self.model,
            "size": self.size,
            "quality": self.quality,
            "max_calls": self.max_calls,
            "call_count": self.call_count,
            "request_id": result.request_id if result else None,
            "usage": result.usage if result else None,
            "duration_seconds": result.duration_seconds if result else None,
        }
