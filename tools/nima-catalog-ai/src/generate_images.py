"""Fase 3 — one image-edit call per attempt.

Orchestration (how many attempts, when to stop, budget checks) lives in
cli.py because it has to interleave with the fidelity gate (evaluate one
attempt before deciding whether a second is worth spending on). This module
only knows how to make a single attempt and save its result.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from PIL import Image

from . import cost_control, file_utils, masking

SIZE_BY_ASPECT_RATIO = {
    "1:1": "1024x1024",
    "4:5": "auto",
}
QUALITY_BY_OUTPUT_TYPE = {
    "refined": "high",  # catalog packshot — fidelity is the only priority
    "lifestyle": "medium",
    "in-use": "medium",
}


def build_prompt(plan_entry: dict) -> str:
    lines = [
        f"Goal: {plan_entry['goal']}",
        f"Composition: {plan_entry['composition']}",
        f"Background: {plan_entry['background']}",
        f"Lighting: {plan_entry['lighting']}",
        "Mandatory rules:",
        *[f"- {rule}" for rule in plan_entry["mandatory_rules"]],
    ]
    return "\n".join(lines)


def next_version(output_dir: Path, handle: str, output_type: str) -> int:
    existing = list(output_dir.glob(f"{handle}__{output_type}__v*.png"))
    if not existing:
        return 1
    versions = []
    for path in existing:
        try:
            versions.append(int(path.stem.rsplit("v", 1)[-1]))
        except ValueError:
            continue
    return (max(versions) if versions else 0) + 1


def generate_attempt(
    *,
    plan_entry: dict,
    handle: str,
    input_dir: Path,
    generated_dir: Path,
    client,
    model: str,
    attempt_number: int,
    cost_tracker: cost_control.CostTracker,
    mask_builder=masking.build_background_mask,
) -> tuple[dict, Path | None]:
    """Make one images.edit call and save the result. Returns (attempt_record, saved_path)."""
    output_type = plan_entry["type"]
    size = SIZE_BY_ASPECT_RATIO.get(plan_entry.get("aspect_ratio", "1:1"), "auto")
    quality = QUALITY_BY_OUTPUT_TYPE.get(output_type, "medium")
    estimated_cost = cost_control.estimate_image_cost_usd(size)

    if not cost_tracker.can_afford(estimated_cost):
        cost_tracker.stop(
            f"Budget exhausted before attempt {attempt_number} of '{output_type}': "
            f"estimated ${estimated_cost:.4f}, remaining ${cost_tracker.remaining_budget_usd:.4f}"
        )
        return None, None

    is_masked = plan_entry.get("mask_strategy") == "background-only"
    primary_path = input_dir / "original" / plan_entry["primary_reference"]
    if is_masked:
        reference_paths = [primary_path]
    else:
        reference_paths = [primary_path] + [
            input_dir / "original" / name for name in plan_entry.get("secondary_references", [])
        ]
    reference_paths = [p for p in reference_paths if p.exists()]

    diagnostics: dict = {"strategy": plan_entry.get("strategy", "full-generate")}
    mask_path = None
    if is_masked and primary_path.exists():
        try:
            mask_image = mask_builder(primary_path)
            masks_dir = generated_dir.parent / "masks"

            framing = plan_entry.get("framing_rules")
            if framing:
                ref_image = Image.open(primary_path).convert("RGB")
                cropped_image, cropped_mask, crop_diag = masking.crop_to_target_occupancy(
                    ref_image,
                    mask_image,
                    target_min_pct=framing["target_occupancy_pct_min"],
                    target_max_pct=framing["target_occupancy_pct_max"],
                )
                diagnostics["framing"] = crop_diag
                crops_dir = generated_dir.parent / "crops"
                crops_dir.mkdir(parents=True, exist_ok=True)
                cropped_ref_path = crops_dir / f"{handle}__{output_type}__attempt{attempt_number}__crop.jpg"
                cropped_image.save(cropped_ref_path, "JPEG", quality=95)
                reference_paths = [cropped_ref_path]
                mask_image = cropped_mask
            else:
                diagnostics["reference_occupancy_pct"] = masking.measure_occupancy_pct(mask_image)

            mask_path = masking.save_mask(
                mask_image, masks_dir / f"{handle}__{output_type}__attempt{attempt_number}__mask.png"
            )
        except Exception as exc:
            # The background-color heuristic can't find a product region on
            # some sources (e.g. a near-uniform-color photo) — fall back to
            # an unmasked full-generate for this attempt rather than
            # crashing the whole run. Recorded so it's visible, not silent.
            diagnostics["mask_error"] = str(exc)
            mask_path = None
            reference_paths = [p for p in [primary_path] if p.exists()]

    prompt = build_prompt(plan_entry)
    date = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        result = client.edit_image(
            model=model,
            prompt=prompt,
            image_paths=reference_paths,
            size=size,
            quality=quality,
            mask_path=mask_path,
        )
    except Exception as exc:  # network/API failure — record and stop this output, not the run
        cost_tracker.record(
            cost_control.CallRecord(
                output_type=output_type,
                attempt=attempt_number,
                model=model,
                parameters={"size": size, "quality": quality},
                request_id=None,
                date=date,
                duration_seconds=0.0,
                usage=None,
                estimated_cost_usd=0.0,
                succeeded=False,
            )
        )
        return {"failed": True, "error": str(exc)}, None

    version = next_version(generated_dir, handle, output_type)
    generated_dir.mkdir(parents=True, exist_ok=True)
    saved_path = file_utils.ensure_within(
        generated_dir, generated_dir / f"{handle}__{output_type}__v{version}.png"
    )
    saved_path.write_bytes(result.image_bytes)

    if saved_path.exists() and is_masked:
        try:
            candidate_mask = mask_builder(saved_path)
            diagnostics["candidate_occupancy_pct"] = masking.measure_occupancy_pct(candidate_mask)
        except Exception as exc:
            diagnostics.setdefault("mask_error", str(exc))

    cost_tracker.record(
        cost_control.CallRecord(
            output_type=output_type,
            attempt=attempt_number,
            model=model,
            parameters={"size": size, "quality": quality},
            request_id=result.request_id,
            date=date,
            duration_seconds=result.duration_seconds,
            usage=result.usage,
            estimated_cost_usd=estimated_cost,
            succeeded=True,
        )
    )

    attempt_record = {
        "attempt": attempt_number,
        "model": model,
        "parameters": {"size": size, "quality": quality},
        "request_id": result.request_id,
        "date": date,
        "duration_seconds": result.duration_seconds,
        "usage": result.usage,
        "estimated_cost_usd": estimated_cost,
        "diagnostics": diagnostics,
    }
    return attempt_record, saved_path
