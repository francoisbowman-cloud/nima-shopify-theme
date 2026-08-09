from __future__ import annotations

import io
import json
import math
import os
from collections import deque
from pathlib import Path

import numpy as np
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "catalog" / "commerce-media-manifest.json"
OUT = Path(os.getenv("NIMA_MEDIA_OUT", ROOT / "commerce-media-evidence"))
OUT.mkdir(parents=True, exist_ok=True)


def download(url: str) -> Image.Image:
    r = requests.get(url, timeout=45)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def border_pixels(a: np.ndarray, band: int) -> np.ndarray:
    top = a[:band, :, :].reshape(-1, 3)
    bottom = a[-band:, :, :].reshape(-1, 3)
    left = a[band:-band, :band, :].reshape(-1, 3) if a.shape[0] > 2 * band else np.empty((0, 3))
    right = a[band:-band, -band:, :].reshape(-1, 3) if a.shape[0] > 2 * band else np.empty((0, 3))
    return np.concatenate([top, bottom, left, right], axis=0).astype(np.float32)


def metrics(img: Image.Image) -> dict:
    a = np.asarray(img).astype(np.float32)
    h, w, _ = a.shape
    band = max(2, int(min(w, h) * 0.025))
    border = border_pixels(a, band)
    bg = np.median(border, axis=0)
    white_ratio = float(np.mean(np.all(border >= 245, axis=1)))
    border_spread = float(np.mean(np.std(border, axis=0)))
    dist = np.sqrt(np.sum((a - bg) ** 2, axis=2))
    foreground = dist > max(26.0, border_spread * 2.25)
    ys, xs = np.where(foreground)
    if len(xs):
        x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
        bbox_area = max(1, (x1 - x0 + 1) * (y1 - y0 + 1))
        occupancy = bbox_area / float(w * h)
        edge_margin = min(x0 / w, (w - 1 - x1) / w, y0 / h, (h - 1 - y1) / h)
        clipped = edge_margin < 0.012
    else:
        x0 = x1 = y0 = y1 = 0
        occupancy = 0.0
        edge_margin = 0.0
        clipped = True
    bg_neutrality = float(max(bg) - min(bg))
    bg_luma = float(np.mean(bg))
    return {
        "width": w,
        "height": h,
        "background_rgb": [round(float(v), 1) for v in bg],
        "background_luma": round(bg_luma, 2),
        "background_neutrality": round(bg_neutrality, 2),
        "border_white_ratio": round(white_ratio, 4),
        "border_spread": round(border_spread, 2),
        "occupancy": round(float(occupancy), 4),
        "edge_margin": round(float(edge_margin), 4),
        "clipped": bool(clipped),
    }


def classify(m: dict, target_min: float, target_max: float) -> tuple[str, list[str]]:
    reasons = []
    if m["clipped"]:
        reasons.append("foreground_touches_safe_edge")
    if m["occupancy"] < target_min:
        reasons.append("optically_too_small")
    if m["occupancy"] > target_max:
        reasons.append("optically_too_large")
    if m["border_white_ratio"] < 0.85:
        reasons.append("embedded_nonwhite_background")
    if m["border_spread"] > 35:
        reasons.append("complex_or_nonuniform_background")

    if m["clipped"] or m["border_spread"] > 55:
        return "MANUAL_REVIEW", reasons
    if "embedded_nonwhite_background" in reasons:
        return "NORMALIZE", reasons
    if reasons:
        return "NORMALIZE", reasons
    return "COMMERCE_READY", reasons


def flood_background_mask(a: np.ndarray, tolerance: float = 42.0) -> np.ndarray:
    h, w, _ = a.shape
    band = max(2, int(min(w, h) * 0.02))
    border = border_pixels(a, band)
    bg = np.median(border, axis=0)
    dist = np.sqrt(np.sum((a.astype(np.float32) - bg) ** 2, axis=2))
    candidate = dist <= tolerance
    seen = np.zeros((h, w), dtype=np.bool_)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        if candidate[0, x]: q.append((0, x)); seen[0, x] = True
        if candidate[h - 1, x] and not seen[h - 1, x]: q.append((h - 1, x)); seen[h - 1, x] = True
    for y in range(h):
        if candidate[y, 0] and not seen[y, 0]: q.append((y, 0)); seen[y, 0] = True
        if candidate[y, w - 1] and not seen[y, w - 1]: q.append((y, w - 1)); seen[y, w - 1] = True
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and candidate[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return seen


def normalize_background(img: Image.Image) -> Image.Image:
    a = np.asarray(img).copy()
    mask = flood_background_mask(a)
    # Conservative edge blend: only whiten pixels connected to the canvas background.
    out = a.astype(np.float32)
    out[mask] = 255.0
    # One-pixel neighbor decontamination suppresses beige edge fringe without changing product geometry.
    neighbor = mask.copy()
    for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
        neighbor |= np.roll(mask, shift=(dy, dx), axis=(0,1))
    fringe = neighbor & ~mask
    out[fringe] = out[fringe] * 0.88 + 255.0 * 0.12
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target_min = manifest["canvas"]["target_occupancy_min"]
    target_max = manifest["canvas"]["target_occupancy_max"]
    results = []
    failures = 0

    for p in manifest["products"]:
        row = {k: p[k] for k in ("id", "handle", "title", "url")}
        try:
            img = download(p["url"])
            before = metrics(img)
            grade, reasons = classify(before, target_min, target_max)
            row.update({"grade": grade, "reasons": reasons, "before": before})

            if p.get("normalize"):
                normalized = normalize_background(img)
                filename = f'{p["handle"]}-refined-v2.png'
                target = OUT / filename
                normalized.save(target, format="PNG", optimize=True)
                after = metrics(normalized)
                after_grade, after_reasons = classify(after, target_min, target_max)
                row.update({
                    "normalized_file": filename,
                    "after": after,
                    "after_grade": after_grade,
                    "after_reasons": after_reasons,
                    "golden_test": p.get("golden_test"),
                })
                if after["border_white_ratio"] < 0.985 or after["clipped"]:
                    failures += 1
                    row["golden_pass"] = False
                else:
                    row["golden_pass"] = True
        except Exception as exc:
            row.update({"grade": "ERROR", "reasons": [str(exc)]})
            failures += 1
        results.append(row)

    (OUT / "audit.json").write_text(json.dumps({"policy": manifest["policy"], "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {}
    for row in results:
        counts[row["grade"]] = counts.get(row["grade"], 0) + 1
    lines = ["# Nima Commerce Media Audit", "", f"Products audited: **{len(results)}**", ""]
    for key in sorted(counts):
        lines.append(f"- {key}: **{counts[key]}**")
    lines += ["", "## Product results", "", "| Product | Grade | Occupancy | White border | Reasons |", "|---|---:|---:|---:|---|"]
    for row in results:
        m = row.get("before", {})
        lines.append(f'| {row["title"]} | {row["grade"]} | {m.get("occupancy", "—")} | {m.get("border_white_ratio", "—")} | {", ".join(row.get("reasons", [])) or "—"} |')
    golden = [r for r in results if r.get("golden_test")]
    if golden:
        lines += ["", "## Golden tests", ""]
        for row in golden:
            lines.append(f'- {row["title"]}: **{"PASS" if row.get("golden_pass") else "FAIL"}** → {row.get("normalized_file", "—")}')
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
