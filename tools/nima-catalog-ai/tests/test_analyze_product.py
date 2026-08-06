from pathlib import Path

from src.analyze_product import analyze_product
from src.config import TOOL_ROOT

PROMPTS_DIR = TOOL_ROOT / "prompts"
SCHEMAS_DIR = TOOL_ROOT / "schemas"


def test_analyze_product_uses_primary_reference_from_analysis(product_dir, fake_client):
    analysis = analyze_product(
        input_dir=product_dir,
        prompts_dir=PROMPTS_DIR,
        schemas_dir=SCHEMAS_DIR,
        client=fake_client,
        model="gpt-5.6-sol",
    )
    assert analysis["primary_reference"] == "01-original.jpg"
    assert analysis["handle"] == "test-product"
    assert fake_client.structured_calls == ["product_analysis"]


def test_analyze_product_missing_manifest_raises(tmp_path, fake_client):
    empty_dir = tmp_path / "no-manifest"
    empty_dir.mkdir()
    try:
        analyze_product(
            input_dir=empty_dir,
            prompts_dir=PROMPTS_DIR,
            schemas_dir=SCHEMAS_DIR,
            client=fake_client,
            model="gpt-5.6-sol",
        )
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_analyze_product_notes_missing_brief(tmp_path, fake_client):
    from tests.conftest import make_product_dir

    product_dir = make_product_dir(tmp_path, handle="no-brief-product", with_brief=False)
    analysis = analyze_product(
        input_dir=product_dir,
        prompts_dir=PROMPTS_DIR,
        schemas_dir=SCHEMAS_DIR,
        client=fake_client,
        model="gpt-5.6-sol",
    )
    assert any("product-brief.json missing" in u for u in analysis["unknowns"])
