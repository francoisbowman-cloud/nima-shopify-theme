"""Entry point: python -m src.cli --input <product-folder> --outputs refined,lifestyle,in-use [--dry-run]

Orchestrates fases 1-6. Never touches Shopify. See tools/nima-catalog-ai/README.md.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from . import build_brief, cost_control, evaluate_fidelity, file_utils, generate_images, package_review
from .analyze_product import analyze_product
from .config import ABSOLUTE_MAX_ATTEMPTS, VALID_OUTPUT_TYPES, Config, ConfigError, load_config
from .openai_client import OpenAIClient

TOOL_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = TOOL_ROOT / "prompts"
SCHEMAS_DIR = TOOL_ROOT / "schemas"
OUTPUT_ROOT = TOOL_ROOT / "output"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to a product folder (manifest.json, original/, optional product-brief.json)")
    parser.add_argument("--outputs", default="refined,lifestyle,in-use", help="Comma-separated: refined,lifestyle,in-use")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=None)
    parser.add_argument("--max-cost-usd", type=float, default=None)
    parser.add_argument("--force", action="store_true", help="Ignore cached state and regenerate")
    parser.add_argument("--yes", action="store_true", help="Confirm spending real API cost (required for any non-dry-run image generation)")
    return parser.parse_args(argv)


def _handle_from_manifest(input_dir: Path) -> str:
    manifest = file_utils.read_json(input_dir / "manifest.json")
    return manifest.get("handle") or input_dir.name


def _load_state(run_dir: Path) -> dict | None:
    state_path = run_dir / "state.json"
    if state_path.exists():
        return file_utils.read_json(state_path)
    return None


def run_pipeline(args: argparse.Namespace, *, client=None, config: Config | None = None) -> dict:
    input_dir = Path(args.input).resolve()
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found in {input_dir}")

    requested_outputs = [o.strip() for o in args.outputs.split(",") if o.strip()]
    unknown = [o for o in requested_outputs if o not in VALID_OUTPUT_TYPES]
    if unknown:
        raise ValueError(f"--outputs contains unknown type(s): {unknown}. Valid: {VALID_OUTPUT_TYPES}")

    if config is None:
        config = load_config(
            max_attempts_flag=args.max_attempts,
            max_cost_usd_flag=args.max_cost_usd,
            dry_run_flag=args.dry_run,
        )
    if client is None:
        client = OpenAIClient(config.openai_api_key)

    handle = _handle_from_manifest(input_dir)
    output_dir = file_utils.ensure_within(OUTPUT_ROOT, OUTPUT_ROOT / handle)
    analysis_dir = output_dir / "analysis"
    generated_dir = output_dir / "generated"
    reviews_dir = output_dir / "reviews"
    run_dir = output_dir / "run"
    package_dir = output_dir / "review-package"

    brief_path = input_dir / "product-brief.json"
    images = file_utils.list_original_images(input_dir)
    input_hash = file_utils.sha256_of_inputs(
        manifest_path, brief_path if brief_path.exists() else None, images
    )
    overrides = build_brief.load_overrides(input_dir, schemas_dir=SCHEMAS_DIR)
    overrides_hash = file_utils.sha256_of_json(overrides)
    # Two-tier cache key: analysis only depends on the product's own sources
    # (manifest/brief/images) — overrides don't change what Fase 1 sees, so
    # they shouldn't force a re-analysis API call. The plan and any cached
    # output state DO depend on overrides (they change the generation
    # prompt), so they're gated on input_hash + overrides_hash together.
    combined_hash = file_utils.sha256_of_json({"input_hash": input_hash, "overrides_hash": overrides_hash})

    previous_state = _load_state(run_dir)
    analysis_reuse = bool(previous_state) and previous_state.get("input_hash") == input_hash and not args.force
    reuse = (
        bool(previous_state) and previous_state.get("combined_hash") == combined_hash and not args.force
    )

    analysis_path = analysis_dir / "product-analysis.json"
    if analysis_reuse and analysis_path.exists():
        analysis = file_utils.read_json(analysis_path)
        print(f"[{handle}] analysis: reused (input unchanged, use --force to regenerate)")
    else:
        analysis = analyze_product(
            input_dir=input_dir,
            prompts_dir=PROMPTS_DIR,
            schemas_dir=SCHEMAS_DIR,
            client=client,
            model=config.text_model,
        )
        file_utils.write_json(analysis_path, analysis)
        print(f"[{handle}] analysis: generated -> {analysis_path}")

    plan_path = analysis_dir / "generation-plan.json"
    if reuse and plan_path.exists():
        generation_plan = file_utils.read_json(plan_path)
    else:
        generation_plan = build_brief.build_generation_plan(
            analysis=analysis, outputs_requested=requested_outputs, schemas_dir=SCHEMAS_DIR, overrides=overrides
        )
        file_utils.write_json(plan_path, generation_plan)
    plan_by_type = {o["type"]: o for o in generation_plan["outputs"]}
    print(f"[{handle}] generation-plan: {list(plan_by_type)} (requested: {requested_outputs})")
    if overrides:
        print(f"[{handle}] product-overrides.json applied: {sorted(overrides)}")

    eligible = analysis.get("eligible_outputs", {})
    cost_tracker = cost_control.CostTracker(max_cost_usd=config.max_cost_usd)
    outputs_state: dict[str, dict] = {}
    fidelity_reports: list[dict] = []

    if not config.dry_run and requested_outputs and any(
        eligible.get(t.replace("-", "_"), False) for t in requested_outputs
    ):
        if not args.yes:
            raise ConfigError(
                f"Real image generation requested (budget up to ${config.max_cost_usd:.2f}, "
                f"model {config.image_model}) but --yes was not passed. Re-run with --yes to confirm, "
                "or use --dry-run to only analyze and plan."
            )

    for output_type in requested_outputs:
        key = output_type.replace("-", "_")
        previous_output_state = (previous_state or {}).get("outputs", {}).get(output_type, {})

        if not eligible.get(key, False):
            outputs_state[output_type] = {"type": output_type, "state": "omitted", "attempts": []}
            print(f"[{handle}] {output_type}: omitted (not eligible per product-analysis.json)")
            continue

        if config.dry_run:
            outputs_state[output_type] = {"type": output_type, "state": "pending", "attempts": []}
            continue

        if reuse and previous_output_state.get("state") in ("approved_candidate", "review"):
            outputs_state[output_type] = previous_output_state
            print(f"[{handle}] {output_type}: reused ({previous_output_state['state']})")
            continue

        plan_entry = plan_by_type[output_type]
        attempts: list[dict] = []
        final_state = "failed"
        for attempt_number in range(1, config.max_attempts + 1):
            if cost_tracker.stop_reason:
                final_state = "pending"
                break
            attempt_record, saved_path = generate_images.generate_attempt(
                plan_entry=plan_entry,
                handle=handle,
                input_dir=input_dir,
                generated_dir=generated_dir,
                client=client,
                model=config.image_model,
                attempt_number=attempt_number,
                cost_tracker=cost_tracker,
            )
            if attempt_record is None:
                final_state = "pending"
                break
            if attempt_record.get("failed"):
                final_state = "failed"
                break

            attempts.append(attempt_record)
            report = evaluate_fidelity.evaluate_candidate(
                handle=handle,
                output_type=output_type,
                candidate_path=saved_path,
                analysis=analysis,
                plan_entry=plan_entry,
                input_dir=input_dir,
                prompts_dir=PROMPTS_DIR,
                schemas_dir=SCHEMAS_DIR,
                client=client,
                model=config.text_model,
            )
            file_utils.write_json(
                reviews_dir / f"{output_type}-fidelity-report.json", report
            )
            fidelity_reports.append(report)
            final_state = evaluate_fidelity.state_for_decision(report["decision"])
            print(
                f"[{handle}] {output_type} attempt {attempt_number}: {report['decision']} "
                f"(score={report.get('overall_score')})"
            )
            if final_state != "rejected":
                break
            if attempt_number == ABSOLUTE_MAX_ATTEMPTS:
                break

        outputs_state[output_type] = {
            "type": output_type,
            "state": final_state,
            "attempts": attempts,
        }

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    run_manifest = {
        "handle": handle,
        "run_started_at": now,
        "run_finished_at": now,
        "dry_run": config.dry_run,
        "input_hash": input_hash,
        "overrides_hash": overrides_hash,
        "combined_hash": combined_hash,
        "brief_hash": file_utils.sha256_file(brief_path) if brief_path.exists() else "",
        "config": {
            "max_attempts": config.max_attempts,
            "max_cost_usd": config.max_cost_usd,
            "outputs_requested": requested_outputs,
            "model": config.image_model,
        },
        "outputs": [
            {"type": s["type"], "state": s["state"], "attempts": s["attempts"]}
            for s in outputs_state.values()
        ],
        "stop_reason": cost_tracker.stop_reason,
    }
    cost_report = cost_tracker.to_report(model=config.image_model, budget_available_usd=config.max_cost_usd)

    file_utils.write_json(run_dir / "run-manifest.json", run_manifest)
    file_utils.write_json(run_dir / "cost-report.json", cost_report)

    state_to_persist = {
        "input_hash": input_hash,
        "combined_hash": combined_hash,
        "outputs": outputs_state,
    }
    file_utils.write_json(run_dir / "state.json", state_to_persist)

    package_review.assemble_review_package(
        handle=handle,
        input_dir=input_dir,
        analysis=analysis,
        generation_plan=generation_plan,
        fidelity_reports=fidelity_reports,
        run_manifest=run_manifest,
        cost_report=cost_report,
        generated_dir=generated_dir,
        package_dir=package_dir,
        dry_run=config.dry_run,
        requested_outputs=requested_outputs,
    )

    print(f"[{handle}] done. dry_run={config.dry_run} total_estimated_cost=${cost_tracker.total_estimated_cost_usd:.4f}")
    if cost_tracker.stop_reason:
        print(f"[{handle}] STOPPED: {cost_tracker.stop_reason}")

    return {
        "handle": handle,
        "analysis": analysis,
        "generation_plan": generation_plan,
        "outputs_state": outputs_state,
        "fidelity_reports": fidelity_reports,
        "run_manifest": run_manifest,
        "cost_report": cost_report,
        "package_dir": str(package_dir),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_pipeline(args)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
