from pathlib import Path

from PIL import Image, ImageDraw

from src import composition_pipeline_v03
from src.background_provider import FixtureBackgroundProvider

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

ANALYSIS_MAT = {
    "handle": "test-mat",
    "title": "Waterproof Feeding Mat",
    "product_category": "pet feeding mat",
    "critical_functional_features": ["raised lip contains spills"],
    "critical_visual_features": ["rectangular gray mat"],
}

ANALYSIS_BOWL = {
    "handle": "test-bowl",
    "title": "Anti-Splash Water Bowl",
    "product_category": "water bowl",
    "critical_functional_features": [],
    "critical_visual_features": [],
}


def _make_product_photo(path: Path) -> None:
    img = Image.new("RGB", (600, 500), (250, 250, 248))
    draw = ImageDraw.Draw(img)
    draw.rectangle((100, 150, 500, 400), fill=(70, 65, 60))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG")


def test_run_v03_flat_ground_product_applies_perspective(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    result = composition_pipeline_v03.run_composition_v03_for_image(
        handle="test-mat",
        output_type="lifestyle",
        source_image_path=source,
        analysis=ANALYSIS_MAT,
        background_provider=FixtureBackgroundProvider(),
        output_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
        canvas_size=(1024, 1024),
    )
    assert result.perspective_applied is True
    assert result.surface_model["geometry_class"] == "flat"
    assert result.top_environment in result.scene_intelligence["primary_environments"]


def test_run_v03_volumetric_product_skips_perspective(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    result = composition_pipeline_v03.run_composition_v03_for_image(
        handle="test-bowl",
        output_type="lifestyle",
        source_image_path=source,
        analysis=ANALYSIS_BOWL,
        background_provider=FixtureBackgroundProvider(),
        output_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
        canvas_size=(1024, 1024),
    )
    assert result.perspective_applied is False
    # Falls back to v0.2-style composition — must still produce a valid composite.
    assert result.final_composite_path.exists()


def test_run_v03_produces_all_required_artifacts(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    result = composition_pipeline_v03.run_composition_v03_for_image(
        handle="test-mat",
        output_type="lifestyle",
        source_image_path=source,
        analysis=ANALYSIS_MAT,
        background_provider=FixtureBackgroundProvider(),
        output_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
        canvas_size=(1024, 1024),
    )
    assert (out_dir / "scene-intelligence.json").exists()
    assert (out_dir / "surface-model.json").exists()
    assert (out_dir / "segmentation-metadata.json").exists()
    assert (out_dir / "edge-refinement-metadata.json").exists()
    assert (out_dir / "placement-spec.json").exists()
    assert (out_dir / "scene-spec.json").exists()
    assert (out_dir / "background-request.json").exists()
    assert (out_dir / "composition-gate-report.json").exists()
    assert (out_dir / "review-entry.json").exists()
    assert result.contact_sheet_path.exists()
    assert result.comparison_path.exists()
    for name in [
        "01-source.jpg",
        "02-mask.png",
        "03-cutout.png",
        "04-background.jpg",
        "05-perspective-preview.png",
        "06-edge-preview.png",
        "07-shadow-preview.png",
        "08-final-composite.png",
        "09-gate-overlay.png",
    ]:
        assert (out_dir / "visual-debug" / name).exists(), name


def test_run_v03_review_entry_includes_scene_intelligence_block(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    result = composition_pipeline_v03.run_composition_v03_for_image(
        handle="test-mat",
        output_type="lifestyle",
        source_image_path=source,
        analysis=ANALYSIS_MAT,
        background_provider=FixtureBackgroundProvider(),
        output_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
        canvas_size=(1024, 1024),
    )
    assert result.review_entry["generation_strategy"] == "protected-product-composition-v03"
    assert result.review_entry["scene_intelligence"]["perspective_applied"] is True


def test_run_v03_never_calls_real_api(tmp_path):
    import pytest

    from src.background_provider import OpenAIBackgroundProvider

    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    with pytest.raises(NotImplementedError):
        composition_pipeline_v03.run_composition_v03_for_image(
            handle="test-mat",
            output_type="lifestyle",
            source_image_path=source,
            analysis=ANALYSIS_MAT,
            background_provider=OpenAIBackgroundProvider(),
            output_dir=out_dir,
            schemas_dir=SCHEMAS_DIR,
            canvas_size=(1024, 1024),
        )
