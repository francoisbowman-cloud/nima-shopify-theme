"""Fase 6 — assemble the local review-package/ directory.

Rejected candidates are copied alongside everything else, clearly labeled in
the contact sheet and fidelity-summary.json — never into a separate
"approved" folder, and never silently dropped.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import file_utils

THUMB_SIZE = (360, 360)
LABEL_HEIGHT = 60


def _thumb(path: Path) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail(THUMB_SIZE)
    canvas = Image.new("RGB", THUMB_SIZE, "white")
    offset = ((THUMB_SIZE[0] - img.width) // 2, (THUMB_SIZE[1] - img.height) // 2)
    canvas.paste(img, offset)
    return canvas


def build_contact_sheet(
    *,
    handle: str,
    originals: list[Path],
    candidates: list[tuple[Path, dict]],
    output_path: Path,
) -> None:
    """candidates: list of (image_path, {"output_type", "decision", "overall_score", "version"})."""
    cells = [("original", p, None) for p in originals] + [
        ("candidate", p, meta) for p, meta in candidates
    ]
    if not cells:
        return

    columns = 4
    rows = (len(cells) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (columns * THUMB_SIZE[0], rows * (THUMB_SIZE[1] + LABEL_HEIGHT)),
        "white",
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, (kind, path, meta) in enumerate(cells):
        col, row = index % columns, index // columns
        x, y = col * THUMB_SIZE[0], row * (THUMB_SIZE[1] + LABEL_HEIGHT)
        sheet.paste(_thumb(path), (x, y))
        if kind == "original":
            label = f"original: {path.name}"
        else:
            label = (
                f"{meta['output_type']} v{meta['version']} — {meta['decision']} "
                f"({meta.get('overall_score', '?')})"
            )
        draw.text((x + 4, y + THUMB_SIZE[1] + 4), label, fill="black", font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, "JPEG", quality=85)


def assemble_review_package(
    *,
    handle: str,
    input_dir: Path,
    analysis: dict,
    generation_plan: dict,
    fidelity_reports: list[dict],
    run_manifest: dict,
    cost_report: dict,
    generated_dir: Path,
    package_dir: Path,
    dry_run: bool,
    requested_outputs: list[str],
) -> Path:
    package_dir.mkdir(parents=True, exist_ok=True)
    originals_dir = package_dir / "originals"
    candidates_dir = package_dir / "candidates"
    originals_dir.mkdir(exist_ok=True)
    candidates_dir.mkdir(exist_ok=True)

    originals = file_utils.list_original_images(input_dir)
    for src in originals:
        shutil.copy2(src, file_utils.ensure_within(originals_dir, originals_dir / src.name))

    candidate_entries: list[tuple[Path, dict]] = []
    if not dry_run:
        for report in fidelity_reports:
            candidate_path = generated_dir / report["candidate_file"]
            if not candidate_path.exists():
                continue
            dest = file_utils.ensure_within(candidates_dir, candidates_dir / candidate_path.name)
            shutil.copy2(candidate_path, dest)
            version = candidate_path.stem.rsplit("v", 1)[-1]
            candidate_entries.append(
                (
                    dest,
                    {
                        "output_type": report["output_type"],
                        "decision": report["decision"],
                        "overall_score": report.get("overall_score"),
                        "version": version,
                    },
                )
            )

    if candidate_entries or originals:
        build_contact_sheet(
            handle=handle,
            originals=originals,
            candidates=candidate_entries,
            output_path=package_dir / "contact-sheet.jpg",
        )

    file_utils.write_json(package_dir / "product-analysis.json", analysis)
    file_utils.write_json(package_dir / "generation-plan.json", generation_plan)
    file_utils.write_json(
        package_dir / "fidelity-summary.json",
        {"handle": handle, "reports": fidelity_reports},
    )
    file_utils.write_json(package_dir / "run-manifest.json", run_manifest)
    file_utils.write_json(package_dir / "cost-report.json", cost_report)

    readme_lines = [
        f"# Review package — {handle}",
        "",
        "Generated locally by tools/nima-catalog-ai. Nothing here has been published "
        "to Shopify or anywhere else — every candidate requires human review.",
        "",
        f"- Dry run: {dry_run}",
        f"- Outputs requested this run: {requested_outputs}",
        f"- Fidelity decisions: "
        + ", ".join(f"{r['output_type']}={r['decision']}" for r in fidelity_reports)
        if fidelity_reports
        else "- No candidates generated in this run.",
        "",
        "Rejected candidates are included in candidates/ and marked in contact-sheet.jpg "
        "and fidelity-summary.json — they are not hidden or moved to a separate folder.",
    ]
    (package_dir / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    return package_dir
