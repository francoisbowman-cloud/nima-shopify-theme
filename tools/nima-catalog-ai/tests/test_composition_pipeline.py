from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from src import composition_pipeline
from src.background_provider import FixtureBackgroundProvider, OpenAIBackgroundProvider

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _make_product_photo(path: Path) -> None:
    img = Image.new("RGB", (600, 500), (250, 250, 248))
    draw = ImageDraw.Draw(img)
    draw.rectangle((100, 150, 500, 400), fill=(70, 65, 60))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG")


def test_run_composition_for_image_produces_all_artifacts(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    result = composition_pipeline.run_composition_for_image(
        handle="test-product",
        output_type="lifestyle",
        source_image_path=source,
        product_category="pet mat",
        environment_description="Warm room.",
        background_provider=FixtureBackgroundProvider(),
        output_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
    )

    assert result.final_composite_path.exists()
    assert result.contact_sheet_path.exists()
    assert (out_dir / "segmentation-metadata.json").exists()
    assert (out_dir / "placement-spec.json").exists()
    assert (out_dir / "scene-spec.json").exists()
    assert (out_dir / "background-request.json").exists()
    assert (out_dir / "composition-gate-report.json").exists()
    assert (out_dir / "review-entry.json").exists()
    for name in [
        "01-source.jpg",
        "02-mask.png",
        "03-cutout.png",
        "04-background.jpg",
        "05-placement-preview.png",
        "06-shadow-preview.png",
        "07-final-composite.png",
        "08-gate-overlay.png",
    ]:
        assert (out_dir / "visual-debug" / name).exists(), name


def test_run_composition_for_image_review_entry_marks_protected_strategy(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    result = composition_pipeline.run_composition_for_image(
        handle="test-product",
        output_type="lifestyle",
        source_image_path=source,
        product_category="pet mat",
        environment_description="Warm room.",
        background_provider=FixtureBackgroundProvider(),
        output_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
    )
    assert result.review_entry["generation_strategy"] == "protected-product-composition"
    assert result.review_entry["generation_kind"] == "LIFESTYLE COMPOSITE"


def test_run_composition_for_image_scene_is_always_lifestyle_level_zero_in_v02(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    result = composition_pipeline.run_composition_for_image(
        handle="test-product",
        output_type="lifestyle",
        source_image_path=source,
        product_category="pet mat",
        environment_description="Warm room.",
        background_provider=FixtureBackgroundProvider(),
        output_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
    )
    assert result.scene_spec["interaction_level"] == 0
    assert result.scene_spec["scene_type"] == "lifestyle"


def test_run_composition_for_image_never_calls_real_api(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)
    out_dir = tmp_path / "out"

    # Using the inert OpenAI provider proves the pipeline itself never makes
    # the background call implicitly — it only fails because *this specific*
    # provider refuses to run, not because the pipeline reached the network.
    with pytest.raises(NotImplementedError):
        composition_pipeline.run_composition_for_image(
            handle="test-product",
            output_type="lifestyle",
            source_image_path=source,
            product_category="pet mat",
            environment_description="Warm room.",
            background_provider=OpenAIBackgroundProvider(),
            output_dir=out_dir,
            schemas_dir=SCHEMAS_DIR,
        )


def test_run_composition_idempotent_given_same_inputs(tmp_path):
    source = tmp_path / "source.jpg"
    _make_product_photo(source)

    result_a = composition_pipeline.run_composition_for_image(
        handle="test-product",
        output_type="lifestyle",
        source_image_path=source,
        product_category="pet mat",
        environment_description="Warm room.",
        background_provider=FixtureBackgroundProvider(),
        output_dir=tmp_path / "out-a",
        schemas_dir=SCHEMAS_DIR,
    )
    result_b = composition_pipeline.run_composition_for_image(
        handle="test-product",
        output_type="lifestyle",
        source_image_path=source,
        product_category="pet mat",
        environment_description="Warm room.",
        background_provider=FixtureBackgroundProvider(),
        output_dir=tmp_path / "out-b",
        schemas_dir=SCHEMAS_DIR,
    )
    assert result_a.placement_spec == result_b.placement_spec
    assert result_a.gate_report == result_b.gate_report
