"""v0.2 Block 10 — offline demonstration, no real API calls.

Runs the full v0.2 pipeline (segmentation -> placement -> scene ->
background -> compositor -> shadow -> gates -> review package) end to end
against a synthetic product photo and a synthetic background fixture, so the
demo is self-contained and doesn't depend on nima-catalog-images/ (untracked,
per CLAUDE.md) or on the v0.1 output/ directory (gitignored, may not exist
until v0.1 is actually run).

Usage: python -m src.demo_v02 [--out demo-output]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from . import composition_batch
from .background_provider import FixtureBackgroundProvider

TOOL_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = TOOL_ROOT / "schemas"


def _make_synthetic_product_photo(path: Path) -> None:
    """A gray rectangular mat with a raised lip on a near-white studio
    background — deliberately similar in shape to the real waterproof
    feeding mat used in the v0.1 demo, so the fixture is representative of
    a real Nima product photo without depending on any tracked/untracked
    real asset."""
    img = Image.new("RGB", (900, 700), (250, 249, 246))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((150, 220, 750, 560), radius=24, fill=(96, 94, 90))
    draw.rounded_rectangle((150, 220, 750, 270), radius=24, fill=(120, 118, 114))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=95)


def _make_synthetic_background_fixture(path: Path, size: tuple[int, int]) -> None:
    """Warm cream living-room-toned flat background — stands in for a
    background-generation API result without calling one."""
    img = Image.new("RGB", size, (233, 224, 206))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, round(size[1] * 0.78), size[0], size[1]), fill=(214, 200, 176))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=95)


def run_demo(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    fixtures_dir = out_dir / "fixtures"

    source_path = fixtures_dir / "demo-product-source.jpg"
    _make_synthetic_product_photo(source_path)

    canvas_size = (1536, 1536)
    background_fixture_path = fixtures_dir / "demo-background-fixture.jpg"
    _make_synthetic_background_fixture(background_fixture_path, canvas_size)

    provider = FixtureBackgroundProvider(fixture_path=background_fixture_path)

    product = composition_batch.BatchProductSpec(
        handle="demo-waterproof-pet-feeding-mat",
        source_image_path=source_path,
        product_category="pet feeding mat",
        environment_description=(
            "Warm editorial pet-friendly living room. Cream linen textures. "
            "Empty floor area reserved in lower center."
        ),
    )

    summary = composition_batch.run_batch(
        products=[product],
        background_provider=provider,
        catalog_dir=out_dir,
        schemas_dir=SCHEMAS_DIR,
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(TOOL_ROOT / "demo-output"))
    args = parser.parse_args(argv)

    out_dir = Path(args.out).resolve()
    summary = run_demo(out_dir)

    print(f"Demo complete. Output: {out_dir}")
    print(f"Products: {summary['products']}  passed={summary['passed']}  review={summary['review']}  rejected={summary['rejected']}")
    for r in summary["results"]:
        print(f"  {r['handle']}: {r.get('status')} — contact sheet: {r.get('contact_sheet')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
