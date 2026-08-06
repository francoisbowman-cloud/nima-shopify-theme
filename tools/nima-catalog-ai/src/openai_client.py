"""Thin wrapper around the OpenAI SDK — the only module that touches the network.

Kept small and mockable on purpose: tests replace this whole class with a
fake so no test ever makes a real API call (see tests/conftest.py).
"""

from __future__ import annotations

import base64
import mimetypes
import time
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI


def _as_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


@dataclass
class ImageEditResult:
    image_bytes: bytes
    request_id: str | None
    usage: dict | None
    model: str
    duration_seconds: float


class OpenAIClient:
    def __init__(self, api_key: str):
        self._client = OpenAI(api_key=api_key)

    def structured_json(
        self,
        *,
        model: str,
        system_prompt: str,
        user_text: str,
        image_paths: list[Path],
        json_schema: dict,
        schema_name: str,
    ) -> dict:
        """Call the Responses API asking for output matching `json_schema`."""
        content = [{"type": "input_text", "text": user_text}]
        for image_path in image_paths:
            content.append({"type": "input_image", "image_url": _as_data_url(image_path)})

        response = self._client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": json_schema,
                    "strict": True,
                }
            },
        )
        return _extract_json_output(response)

    def edit_image(
        self,
        *,
        model: str,
        prompt: str,
        image_paths: list[Path],
        size: str,
        quality: str,
        mask_path: Path | None = None,
    ) -> ImageEditResult:
        if mask_path is not None and len(image_paths) != 1:
            raise ValueError("A mask can only be paired with exactly one reference image")

        started = time.monotonic()  # request duration, not a substitute for Date.now()-style timestamps
        files = [open(p, "rb") for p in image_paths]
        mask_file = open(mask_path, "rb") if mask_path is not None else None
        try:
            kwargs = dict(model=model, image=files, prompt=prompt, size=size, quality=quality, n=1)
            if mask_file is not None:
                kwargs["mask"] = mask_file
            response = self._client.images.edit(**kwargs)
        finally:
            for f in files:
                f.close()
            if mask_file is not None:
                mask_file.close()
        duration = time.monotonic() - started
        b64 = response.data[0].b64_json
        usage = None
        if getattr(response, "usage", None) is not None:
            usage = response.usage.model_dump() if hasattr(response.usage, "model_dump") else dict(response.usage)
        request_id = getattr(response, "id", None) or getattr(response, "_request_id", None)
        return ImageEditResult(
            image_bytes=base64.b64decode(b64),
            request_id=request_id,
            usage=usage,
            model=model,
            duration_seconds=duration,
        )


def _extract_json_output(response) -> dict:
    """Pull the structured JSON payload out of a Responses API result."""
    import json

    output_text = getattr(response, "output_text", None)
    if output_text:
        return json.loads(output_text)

    for item in getattr(response, "output", []):
        for content in getattr(item, "content", []):
            text = getattr(content, "text", None)
            if text:
                return json.loads(text)
    raise ValueError("No structured JSON payload found in Responses API output")
