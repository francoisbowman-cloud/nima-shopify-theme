"""v0.3 Block 9 — offline demonstration, no real API calls.

Same self-contained-fixtures approach as demo_v02.py — a synthetic product
photo and a synthetic background, run through the full v0.3 pipeline
(scene intelligence -> surface model -> segmentation -> edge refinement ->
perspective match -> surface-aware shadow -> Composition Gate v0.3 ->
visual debug -> benchmark comparison), so this is runnable and verifiable
without nima-catalog-images/ or a v0.1/v0.2 real run.

Usage: python -m src.demo_v03 [--out demo-output-v03]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from . import composition_pipeline_v03
from .background_provider import FixtureBackgroundProvider

TOOL_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = TOOL_ROOT / "schemas"

DEMO_ANALYSIS = {
    "handle": "demo-waterproof-pet-feeding-mat",
    "title": "Waterproof Feeding Mat — Gray, 19 x 12 Inches",
    "product_category": "pet feeding mat",
    "critical_visual_features": ["rectangular gray mat with raised lip"],
    "critical_functional_features": ["raised perimeter contains spills", "used flat on the floor"],
}


def _make_synthetic_product_photo(path: Path) -> None:
    img = Image.new("RGB", (900, 700), (250, 249, 246))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((150, 220, 750, 560), radius=24, fill=(96, 94, 90))
    draw.rounded_rectangle((150, 220, 750, 270), radius=24, fill=(120, 118, 114))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=95)


def _make_synthetic_kitchen_background(path: Path, size: tuple[int, int]) -> None:
    """Warm kitchen-feeding-area-toned flat background — stands in for the
    scene-intelligence-selected environment without calling a real API."""
    img = Image.new("RGB", size, (238, 231, 217))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, round(size[1] * 0.55), size[0], size[1]), fill=(212, 196, 172))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=95)


def run_demo(out_dir: Path) -> composition_pipeline_v03.CompositionRunResultV03:
    out_dir.mkdir(parents=True, exist_ok=True)
    fixtures_dir = out_dir / "fixtures"

    source_path = fixtures_dir / "demo-product-source.jpg"
    _make_synthetic_product_photo(source_path)

    canvas_size = (1536, 1536)
    background_fixture_path = fixtures_dir / "demo-kitchen-fixture.jpg"
    _make_synthetic_kitchen_background(background_fixture_path, canvas_size)

    provider = FixtureBackgroundProvider(fixture_path=background_fixture_path)

    return composition_pipeline_v03.run_composition_v03_for_image(
        handle=DEMO_ANALYSIS["handle"],
        output_type="lifestyle",
        source_image_path=source_path,
        analysis=DEMO_ANALYSIS,
        background_provider=provider,
        output_dir=out_dir / DEMO_ANALYSIS["handle"],
        schemas_dir=SCHEMAS_DIR,
        canvas_size=canvas_size,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(TOOL_ROOT / "demo-output-v03"))
    args = parser.parse_args(argv)

    out_dir = Path(args.out).resolve()
    result = run_demo(out_dir)

    print(f"Demo v0.3 complete. Output: {result.output_dir}")
    print(f"Scene: {result.top_environment} | surface_plane={result.surface_model['surface_plane']} "
          f"geometry_class={result.surface_model['geometry_class']} | perspective_applied={result.perspective_applied}")
    print(f"Composition Gate v0.3: {result.gate_report['status']}")
    print(f"Contact sheet: {result.contact_sheet_path}")
    print(f"Comparison v0.2-vs-v0.3: {result.comparison_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
