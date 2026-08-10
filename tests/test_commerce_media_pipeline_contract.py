import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "catalog" / "commerce-media-manifest.json"
SCRIPT = ROOT / ".github" / "commerce_media_normalizer.py"
WORKFLOW = ROOT / ".github" / "workflows" / "commerce-media-gate.yml"
DOC = ROOT / "docs" / "nima-commerce-media-normalization.md"


def test_manifest_is_full_active_catalog_snapshot():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["policy"] == "commerce-white-background"
    assert len(data["products"]) == 23
    handles = [p["handle"] for p in data["products"]]
    assert len(handles) == len(set(handles))
    assert all(p["url"].startswith("https://cdn.shopify.com/") for p in data["products"])


def test_grooming_gloves_are_permanent_golden_regression():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    gloves = next(p for p in data["products"] if p["handle"].startswith("pet-grooming-gloves"))
    assert gloves["normalize"] is True
    assert gloves["golden_test"] == "embedded-background"


def test_pipeline_is_conservative_and_white_canvas_enforced():
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'p.get("normalize")' in text
    assert 'border_white_ratio' in text
    assert 'MANUAL_REVIEW' in text
    assert 'COMMERCE_READY' in text
    assert 'NORMALIZE' in text
    assert 'out[mask] = 255.0' in text
    assert 'golden_pass' in text


def test_gate_exports_visual_evidence_artifact():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "commerce_media_normalizer.py" in text
    assert "nima-commerce-media-evidence" in text
    assert "upload-artifact@v4" in text


def test_documented_asset_standard_rejects_css_only_fixes():
    text = DOC.read_text(encoding="utf-8").lower()
    assert "not considered production-ready merely because it is displayed on a white css container" in text
    assert "halo" in text
    assert "upstream normalization" in text
