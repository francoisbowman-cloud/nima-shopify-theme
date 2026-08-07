from pathlib import Path

from PIL import Image, ImageDraw

from src import composition_batch
from src.background_provider import FixtureBackgroundProvider

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _make_product_photo(path: Path) -> None:
    img = Image.new("RGB", (400, 300), (250, 250, 248))
    draw = ImageDraw.Draw(img)
    draw.rectangle((80, 80, 320, 220), fill=(70, 65, 60))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG")


def test_run_batch_processes_multiple_products(tmp_path):
    products = []
    for handle in ("product-a", "product-b", "product-c"):
        source = tmp_path / handle / "source.jpg"
        _make_product_photo(source)
        products.append(
            composition_batch.BatchProductSpec(
                handle=handle,
                source_image_path=source,
                product_category="pet accessory",
                environment_description="Warm room.",
            )
        )

    summary = composition_batch.run_batch(
        products=products,
        background_provider=FixtureBackgroundProvider(),
        catalog_dir=tmp_path / "catalog-review",
        schemas_dir=SCHEMAS_DIR,
    )

    assert summary["products"] == 3
    assert summary["passed"] + summary["review"] + summary["rejected"] == 3
    assert (tmp_path / "catalog-review" / "catalog-composition-summary.json").exists()
    for handle in ("product-a", "product-b", "product-c"):
        assert (tmp_path / "catalog-review" / handle / "composite-base.png").exists()


def test_run_batch_isolates_a_failing_product(tmp_path):
    good_source = tmp_path / "good" / "source.jpg"
    _make_product_photo(good_source)
    bad_source = tmp_path / "bad" / "source.jpg"  # never created -> segmentation will fail to open it

    products = [
        composition_batch.BatchProductSpec(
            handle="good-product",
            source_image_path=good_source,
            product_category="mat",
            environment_description="Room.",
        ),
        composition_batch.BatchProductSpec(
            handle="bad-product",
            source_image_path=bad_source,
            product_category="mat",
            environment_description="Room.",
        ),
    ]

    summary = composition_batch.run_batch(
        products=products,
        background_provider=FixtureBackgroundProvider(),
        catalog_dir=tmp_path / "catalog-review",
        schemas_dir=SCHEMAS_DIR,
    )

    assert summary["rejected"] == 1
    assert summary["passed"] == 1
    statuses = {r["handle"]: r["status"] for r in summary["results"]}
    assert statuses["good-product"] == "passed"
    assert statuses["bad-product"] == "error"
