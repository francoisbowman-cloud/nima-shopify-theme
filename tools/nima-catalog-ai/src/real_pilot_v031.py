"""Real Pilot v0.3.1 runner.

One product, one contextual background API call, zero retries, zero Shopify.
Also emits a deterministic commerce-primary asset on exact white without an
additional model call.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from . import file_utils
from .background_provider_v031 import OpenAIBackgroundProviderV031
from .commerce_primary_v031 import render_commerce_primary, save_commerce_primary
from .composition_pipeline_v031 import run_composition_v031_for_image
from .openai_client import OpenAIClient


def run_real_pilot_v031(
    *,
    handle: str,
    source_image_path: Path,
    analysis_path: Path,
    output_dir: Path,
    api_key: str,
    schemas_dir: Path,
) -> dict:
    analysis = file_utils.read_json(analysis_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # A. Commerce-primary: deterministic, no model call.
    commerce_dir = output_dir / "commerce-primary"
    commerce = render_commerce_primary(source_image_path=source_image_path)
    save_commerce_primary(commerce, commerce_dir)
    file_utils.write_json(commerce_dir / "commerce-background-gate.json", commerce.gate_report)
    if not commerce.gate_report["passed"]:
        raise RuntimeError("commerce-primary failed commerce-white-background gate")

    # B. Contextual lifestyle: exactly one gpt-image-2 background call.
    provider = OpenAIBackgroundProviderV031(client=OpenAIClient(api_key=api_key))
    lifestyle_dir = output_dir / "lifestyle"
    lifestyle = run_composition_v031_for_image(
        handle=handle,
        output_type="lifestyle",
        source_image_path=source_image_path,
        analysis=analysis,
        background_provider=provider,
        output_dir=lifestyle_dir,
        schemas_dir=schemas_dir,
    )

    summary = {
        "pilot": "nima-catalog-ai-v0.3.1-real-pilot",
        "handle": handle,
        "shopify_touched": False,
        "api": provider.audit_metadata(),
        "commerce_primary": {
            "path": str(commerce_dir / "commerce-primary.png"),
            "background_gate": commerce.gate_report,
        },
        "lifestyle": {
            "path": str(lifestyle.final_composite_path),
            "composition_gate": lifestyle.gate_report,
            "scene_intelligence": lifestyle.scene_intelligence,
            "surface_model": lifestyle.surface_model,
            "perspective_applied": lifestyle.perspective_applied,
            "contact_sheet": str(lifestyle.contact_sheet_path),
            "comparison": str(lifestyle.comparison_path),
        },
        "acceptance": {
            "max_api_calls": 1,
            "actual_api_calls": provider.call_count,
            "no_retries": provider.call_count == 1,
            "commerce_white_background_pass": commerce.gate_report["passed"],
            "composition_gate_pass": lifestyle.gate_report["passed"],
            "manual_visual_checks_required": [
                "no visible post-perspective white halo",
                "real product identity and geometry preserved",
                "perspective reads as flat product resting on ground",
                "kitchen feeding area remains commercially plausible",
                "commerce-primary is clean, centered, exact-white and free of contextual scenery",
            ],
        },
    }
    file_utils.write_json(output_dir / "pilot-summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Nima Catalog AI Real Pilot v0.3.1")
    parser.add_argument("--handle", required=True)
    parser.add_argument("--source-image", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--schemas-dir", type=Path, default=Path(__file__).resolve().parents[1] / "schemas")
    parser.add_argument(
        "--allow-api",
        action="store_true",
        help="Required safety switch. The runner makes exactly one gpt-image-2 background call and never retries.",
    )
    args = parser.parse_args()

    if not args.allow_api:
        parser.error("Real Pilot v0.3.1 requires explicit --allow-api")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        parser.error("OPENAI_API_KEY is not set")

    summary = run_real_pilot_v031(
        handle=args.handle,
        source_image_path=args.source_image,
        analysis_path=args.analysis,
        output_dir=args.output_dir,
        api_key=api_key,
        schemas_dir=args.schemas_dir,
    )
    print(file_utils.json.dumps(summary, indent=2) if hasattr(file_utils, "json") else summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
