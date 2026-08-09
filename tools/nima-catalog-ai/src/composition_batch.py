"""v0.2 Block 14 — offline batch runner over multiple products.

Runs composition_pipeline.run_composition_for_image per product and writes
catalog-review/<handle>/ plus a catalog-composition-summary.json. Does not
call any real image-generation API — the batch is only as offline as the
BackgroundProvider it's given (pass a FixtureBackgroundProvider for local
runs, never OpenAIBackgroundProvider).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import composition_pipeline, file_utils
from .background_provider import BackgroundProvider


@dataclass
class BatchProductSpec:
    handle: str
    source_image_path: Path
    product_category: str
    environment_description: str
    output_type: str = "lifestyle"


def run_batch(
    *,
    products: list[BatchProductSpec],
    background_provider: BackgroundProvider,
    catalog_dir: Path,
    schemas_dir: Path | None = None,
) -> dict:
    catalog_dir.mkdir(parents=True, exist_ok=True)
    results = []
    passed = 0
    review = 0
    rejected = 0

    for spec in products:
        product_dir = catalog_dir / spec.handle
        try:
            result = composition_pipeline.run_composition_for_image(
                handle=spec.handle,
                output_type=spec.output_type,
                source_image_path=spec.source_image_path,
                product_category=spec.product_category,
                environment_description=spec.environment_description,
                background_provider=background_provider,
                output_dir=product_dir,
                schemas_dir=schemas_dir,
            )
        except Exception as exc:  # a single bad product must not abort the whole batch
            file_utils.write_json(product_dir / "error.json", {"handle": spec.handle, "error": str(exc)})
            rejected += 1
            results.append({"handle": spec.handle, "status": "error", "error": str(exc)})
            continue

        if result.gate_report["passed"]:
            passed += 1
            status = "passed"
        else:
            review += 1
            status = "review"
        results.append(
            {
                "handle": spec.handle,
                "status": status,
                "gate_status": result.gate_report["status"],
                "occupancy": result.review_entry["composition"]["occupancy"],
                "output_dir": str(result.output_dir),
                "contact_sheet": str(result.contact_sheet_path),
            }
        )

    summary = {
        "products": len(products),
        "passed": passed,
        "review": review,
        "rejected": rejected,
        "results": results,
    }
    file_utils.write_json(catalog_dir / "catalog-composition-summary.json", summary)
    return summary
