from io import BytesIO

import pytest
from PIL import Image

from src.background_provider_v031 import OpenAIBackgroundProviderV031, PilotCallBudgetExceeded
from src.openai_client import ImageEditResult


class FakeClient:
    def __init__(self):
        self.calls = 0

    def generate_image(self, **kwargs):
        self.calls += 1
        image = Image.new("RGB", (1024, 1024), (220, 210, 195))
        buf = BytesIO()
        image.save(buf, "PNG")
        return ImageEditResult(
            image_bytes=buf.getvalue(),
            request_id="fake-request",
            usage={"images": 1},
            model=kwargs["model"],
            duration_seconds=0.1,
        )


def _request():
    return {
        "environment": "kitchen feeding area",
        "lighting": "soft natural light",
        "camera": "editorial",
        "reserved_zone": "leave lower center empty",
        "negative_objects": ["feeding mats"],
        "interaction_constraints": ["Do not depict the product itself"],
        "canvas": {"width": 1536, "height": 1536},
    }


def test_provider_makes_one_call_and_resizes_to_canvas():
    client = FakeClient()
    provider = OpenAIBackgroundProviderV031(client=client)
    image = provider.generate_background(_request())
    assert image.size == (1536, 1536)
    assert client.calls == 1
    assert provider.audit_metadata()["call_count"] == 1


def test_provider_refuses_retry_after_budget_exhausted():
    provider = OpenAIBackgroundProviderV031(client=FakeClient())
    provider.generate_background(_request())
    with pytest.raises(PilotCallBudgetExceeded):
        provider.generate_background(_request())


def test_provider_refuses_relaxed_call_budget():
    with pytest.raises(ValueError):
        OpenAIBackgroundProviderV031(client=FakeClient(), max_calls=2)
