import pytest
from PIL import Image

from src.background_provider import FixtureBackgroundProvider, OpenAIBackgroundProvider


def test_fixture_provider_returns_flat_color_when_no_fixture_given():
    provider = FixtureBackgroundProvider()
    img = provider.generate_background({"canvas": {"width": 100, "height": 80}})
    assert img.size == (100, 80)
    assert img.mode == "RGB"


def test_fixture_provider_loads_and_resizes_given_fixture(tmp_path):
    fixture_path = tmp_path / "bg.jpg"
    Image.new("RGB", (50, 50), (10, 20, 30)).save(fixture_path, "JPEG")
    provider = FixtureBackgroundProvider(fixture_path=fixture_path)
    img = provider.generate_background({"canvas": {"width": 200, "height": 150}})
    assert img.size == (200, 150)


def test_openai_provider_never_calls_network_and_raises():
    provider = OpenAIBackgroundProvider(api_key="fake-not-real")
    with pytest.raises(NotImplementedError):
        provider.generate_background({"canvas": {"width": 100, "height": 100}})
