from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

STATUS_READY = "COMMERCE_READY"
STATUS_NORMALIZE = "NORMALIZE"
STATUS_MANUAL = "MANUAL_REVIEW"
STATUS_LOW_RES = "SOURCE_TOO_LOW_RES"
STATUS_ERROR = "ERROR"


@dataclass(frozen=True)
class Profile:
    name: str
    target_occupancy: float
    min_occupancy: float
    max_occupancy: float
    safe_margin: float


@dataclass(frozen=True)
class Policy:
    canvas_rgb: tuple[int, int, int]
    min_source_px: int
    white_threshold: int
    min_border_white_ratio: float
    uniform_background_spread_max: float
    background_tolerance: float
    fringe_blend: float
    profiles: dict[str, Profile]

    @classmethod
    def load(cls, path: Path) -> "Policy":
        raw = json.loads(path.read_text(encoding="utf-8"))
        profiles = {
            name: Profile(name=name, **values)
            for name, values in raw["geometry_profiles"].items()
        }
        return cls(
            canvas_rgb=tuple(raw["canvas_rgb"]),
            min_source_px=int(raw["min_source_px"]),
            white_threshold=int(raw["white_threshold"]),
            min_border_white_ratio=float(raw["min_border_white_ratio"]),
            uniform_background_spread_max=float(raw["uniform_background_spread_max"]),
            background_tolerance=float(raw["background_tolerance"]),
            fringe_blend=float(raw["fringe_blend"]),
            profiles=profiles,
        )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_image(source: str) -> tuple[Image.Image, str]:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        response = requests.get(source, timeout=60)
        response.raise_for_status()
        payload = response.content
    else:
        payload = Path(source).read_bytes()
    image = Image.open(io.BytesIO(payload)).convert("RGB")
    return image, sha256_bytes(payload)


def _border_pixels(a: np.ndarray, band: int) -> np.ndarray:
    top = a[:band, :, :].reshape(-1, 3)
    bottom = a[-band:, :, :].reshape(-1, 3)
    middle = a[band:-band, :, :] if a.shape[0] > 2 * band else a[0:0, :, :]
    left = middle[:, :band, :].reshape(-1, 3)
    right = middle[:, -band:, :].reshape(-1, 3)
    return np.concatenate([top, bottom, left, right], axis=0).astype(np.float32)


def _foreground_mask(a: np.ndarray, background_rgb: np.ndarray, spread: float) -> np.ndarray:
    distance = np.sqrt(np.sum((a.astype(np.float32) - background_rgb) ** 2, axis=2))
    return distance > max(24.0, spread * 2.2)


def infer_geometry(foreground_bbox: list[int] | None) -> str:
    if not foreground_bbox:
        return "compact_object"
    x0, y0, x1, y1 = foreground_bbox
    w = max(1, x1 - x0 + 1)
    h = max(1, y1 - y0 + 1)
    ratio = w / h
    if ratio >= 2.45:
        return "long_accessory"
    if ratio >= 1.55:
        return "wide_object"
    if ratio <= 0.62:
        return "tall_object"
    return "compact_object"


def analyze_image(image: Image.Image, policy: Policy, geometry_override: str | None = None) -> dict[str, Any]:
    a = np.asarray(image.convert("RGB"), dtype=np.float32)
    h, w, _ = a.shape
    band = max(2, int(min(w, h) * 0.025))
    border = _border_pixels(a, band)
    background = np.median(border, axis=0)
    spread = float(np.mean(np.std(border, axis=0)))
    border_white = float(np.mean(np.all(border >= policy.white_threshold, axis=1)))
    foreground = _foreground_mask(a, background, spread)
    ys, xs = np.where(foreground)
    bbox: list[int] | None = None
    occupancy = 0.0
    edge_margin = 0.0
    clipped = True
    if len(xs):
        x0, x1 = int(xs.min()), int(xs.max())
        y0, y1 = int(ys.min()), int(ys.max())
        bbox = [x0, y0, x1, y1]
        bbox_area = (x1 - x0 + 1) * (y1 - y0 + 1)
        occupancy = bbox_area / float(w * h)
        edge_margin = min(x0 / w, (w - 1 - x1) / w, y0 / h, (h - 1 - y1) / h)
        clipped = edge_margin < 0.012
    geometry = geometry_override or infer_geometry(bbox)
    if geometry not in policy.profiles:
        geometry = "compact_object"
    profile = policy.profiles[geometry]
    return {
        "width": w,
        "height": h,
        "min_dimension": min(w, h),
        "background_rgb": [round(float(v), 2) for v in background],
        "background_neutrality": round(float(max(background) - min(background)), 2),
        "border_white_ratio": round(border_white, 5),
        "border_spread": round(spread, 3),
        "foreground_bbox": bbox,
        "occupancy": round(float(occupancy), 5),
        "edge_margin": round(float(edge_margin), 5),
        "clipped": clipped,
        "geometry_profile": geometry,
        "target_occupancy": profile.target_occupancy,
    }


def classify(metrics: dict[str, Any], policy: Policy) -> tuple[str, list[str]]:
    profile = policy.profiles[metrics["geometry_profile"]]
    reasons: list[str] = []
    if metrics["min_dimension"] < policy.min_source_px:
        reasons.append("source_resolution_below_contract")
        return STATUS_LOW_RES, reasons
    if metrics["foreground_bbox"] is None:
        reasons.append("foreground_not_detected")
        return STATUS_MANUAL, reasons
    if metrics["clipped"]:
        reasons.append("foreground_touches_safe_edge")
    if metrics["occupancy"] < profile.min_occupancy:
        reasons.append("optically_too_small")
    if metrics["occupancy"] > profile.max_occupancy:
        reasons.append("optically_too_large")
    if metrics["border_white_ratio"] < policy.min_border_white_ratio:
        reasons.append("embedded_nonwhite_background")
    if metrics["border_spread"] > policy.uniform_background_spread_max:
        reasons.append("complex_or_nonuniform_background")

    if metrics["clipped"] or metrics["border_spread"] > policy.uniform_background_spread_max * 1.6:
        return STATUS_MANUAL, reasons
    if reasons:
        return STATUS_NORMALIZE, reasons
    return STATUS_READY, reasons


def flood_background_mask(image: Image.Image, tolerance: float) -> np.ndarray:
    a = np.asarray(image.convert("RGB"), dtype=np.float32)
    h, w, _ = a.shape
    band = max(2, int(min(w, h) * 0.02))
    border = _border_pixels(a, band)
    background = np.median(border, axis=0)
    distance = np.sqrt(np.sum((a - background) ** 2, axis=2))
    candidate = distance <= tolerance
    seen = np.zeros((h, w), dtype=np.bool_)
    queue: deque[tuple[int, int]] = deque()

    def seed(y: int, x: int) -> None:
        if candidate[y, x] and not seen[y, x]:
            seen[y, x] = True
            queue.append((y, x))

    for x in range(w):
        seed(0, x)
        seed(h - 1, x)
    for y in range(h):
        seed(y, 0)
        seed(y, w - 1)

    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and candidate[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                queue.append((ny, nx))
    return seen


def normalize_background(image: Image.Image, policy: Policy) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    background = flood_background_mask(image, policy.background_tolerance)
    alpha = Image.fromarray((~background * 255).astype(np.uint8), "L")
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.55))
    alpha_a = np.asarray(alpha, dtype=np.float32) / 255.0

    product = rgb.astype(np.float32)
    # Decontaminate only the narrow transition ring. Fully opaque product pixels are untouched.
    transition = (alpha_a > 0.02) & (alpha_a < 0.98)
    if np.any(transition):
        strength = policy.fringe_blend * (1.0 - alpha_a[transition, None])
        product[transition] = product[transition] * (1.0 - strength) + 255.0 * strength

    canvas = np.full_like(product, 255.0)
    out = product * alpha_a[:, :, None] + canvas * (1.0 - alpha_a[:, :, None])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def _white_bbox(image: Image.Image, threshold: int = 248) -> tuple[int, int, int, int] | None:
    a = np.asarray(image.convert("RGB"))
    foreground = np.any(a < threshold, axis=2)
    ys, xs = np.where(foreground)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def reframe(image: Image.Image, profile: Profile) -> Image.Image:
    bbox = _white_bbox(image)
    if not bbox:
        return image
    crop = image.crop(bbox)
    cw, ch = crop.size
    side = max(image.width, image.height)
    max_span = int(side * math.sqrt(profile.target_occupancy))
    scale = min(max_span / max(cw, 1), max_span / max(ch, 1), 1.25)
    nw, nh = max(1, round(cw * scale)), max(1, round(ch * scale))
    crop = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (side, side), (255, 255, 255))
    x = (side - nw) // 2
    y = (side - nh) // 2
    canvas.paste(crop, (x, y))
    return canvas


def normalize(image: Image.Image, policy: Policy, geometry: str) -> Image.Image:
    cleaned = normalize_background(image, policy)
    return reframe(cleaned, policy.profiles[geometry])


def audit_item(item: dict[str, Any], policy: Policy, output_dir: Path, normalize_safe: bool) -> dict[str, Any]:
    row = {
        "product_id": item.get("product_id"),
        "handle": item.get("handle"),
        "title": item.get("title") or item.get("handle") or item.get("source"),
        "source": item["source"],
        "source_kind": item.get("source_kind", "supplier_or_shopify"),
    }
    try:
        image, source_hash = load_image(item["source"])
        geometry_override = item.get("geometry_profile")
        before = analyze_image(image, policy, geometry_override)
        status, reasons = classify(before, policy)
        row.update({"source_sha256": source_hash, "status": status, "reasons": reasons, "before": before})

        should_normalize = normalize_safe and status == STATUS_NORMALIZE and "complex_or_nonuniform_background" not in reasons
        if item.get("golden_test"):
            should_normalize = True
        if should_normalize:
            normalized = normalize(image, policy, before["geometry_profile"])
            output_name = f"{item.get('handle') or source_hash[:12]}-commerce-white.png"
            output_path = output_dir / "normalized" / output_name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            normalized.save(output_path, format="PNG", optimize=True)
            after = analyze_image(normalized, policy, before["geometry_profile"])
            after_status, after_reasons = classify(after, policy)
            fidelity = fidelity_guard(image, normalized)
            candidate_pass = (
                after_status == STATUS_READY
                and fidelity["pass"]
                and after["border_white_ratio"] >= 0.995
                and not after["clipped"]
            )
            row.update({
                "normalized_file": str(output_path),
                "after": after,
                "after_status": after_status,
                "after_reasons": after_reasons,
                "fidelity": fidelity,
                "candidate_pass": candidate_pass,
                "golden_test": item.get("golden_test"),
            })
    except Exception as exc:
        row.update({"status": STATUS_ERROR, "reasons": [f"{type(exc).__name__}: {exc}"]})
    return row


def fidelity_guard(source: Image.Image, candidate: Image.Image) -> dict[str, Any]:
    """Conservative non-generative guard.

    It does not claim semantic identity. It verifies that the normalized asset contains a
    substantial foreground with a compatible aspect signature instead of an empty/eroded cutout.
    """
    sb = _white_bbox(normalize_background(source, Policy(
        canvas_rgb=(255,255,255), min_source_px=1, white_threshold=245,
        min_border_white_ratio=0.0, uniform_background_spread_max=999.0,
        background_tolerance=42.0, fringe_blend=0.0,
        profiles={"compact_object": Profile("compact_object", .55, .1, .95, .06)}
    )))
    cb = _white_bbox(candidate)
    if not sb or not cb:
        return {"pass": False, "reason": "foreground_missing"}
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    cw, ch = cb[2] - cb[0], cb[3] - cb[1]
    source_ratio = sw / max(sh, 1)
    candidate_ratio = cw / max(ch, 1)
    ratio_delta = abs(math.log(max(candidate_ratio, 1e-6) / max(source_ratio, 1e-6)))
    passed = ratio_delta <= 0.18 and min(cw, ch) >= 16
    return {
        "pass": passed,
        "source_aspect": round(source_ratio, 4),
        "candidate_aspect": round(candidate_ratio, 4),
        "log_aspect_delta": round(ratio_delta, 4),
        "reason": "ok" if passed else "foreground_geometry_changed",
    }


def make_contact_sheet(results: list[dict[str, Any]], output_dir: Path) -> None:
    candidates = [r for r in results if r.get("normalized_file") and Path(r["normalized_file"]).exists()]
    if not candidates:
        return
    cell_w, cell_h = 360, 430
    cols = 3
    rows = math.ceil(len(candidates) / cols)
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), (246, 243, 238))
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(candidates):
        x0 = (i % cols) * cell_w
        y0 = (i // cols) * cell_h
        img = Image.open(row["normalized_file"]).convert("RGB")
        img.thumbnail((320, 320), Image.Resampling.LANCZOS)
        px = x0 + (cell_w - img.width) // 2
        py = y0 + 16
        sheet.paste(img, (px, py))
        title = str(row["title"])[:42]
        status = "PASS" if row.get("candidate_pass") else row.get("after_status", "REVIEW")
        draw.text((x0 + 18, y0 + 350), title, fill=(34, 31, 28))
        draw.text((x0 + 18, y0 + 380), status, fill=(80, 73, 66))
    sheet.save(output_dir / "contact-sheet.jpg", quality=92)


def write_reports(results: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter(r["status"] for r in results)
    candidates = [r for r in results if r.get("candidate_pass")]
    publish_plan = [
        {
            "product_id": r["product_id"],
            "handle": r["handle"],
            "source_sha256": r["source_sha256"],
            "candidate_file": r["normalized_file"],
            "required_gates": ["FIDELITY_PASS", "COMMERCE_PASS", "SHOPIFY_STAGING", "RENDER_PASS"],
        }
        for r in candidates
    ]
    (output_dir / "audit.json").write_text(json.dumps({"counts": counts, "results": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "publish-plan.json").write_text(json.dumps({"version": 1, "candidates": publish_plan}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Nima Commerce Media Factory — Audit", "", f"Assets audited: **{len(results)}**", ""]
    for key in sorted(counts):
        lines.append(f"- {key}: **{counts[key]}**")
    lines += ["", f"Safe normalized candidates: **{len(candidates)}**", "", "| Product | Status | Geometry | Occupancy | White border | Reasons |", "|---|---|---|---:|---:|---|"]
    for row in results:
        m = row.get("before", {})
        lines.append(
            f"| {row['title']} | {row['status']} | {m.get('geometry_profile','—')} | {m.get('occupancy','—')} | {m.get('border_white_ratio','—')} | {', '.join(row.get('reasons', [])) or '—'} |"
        )
    lines += ["", "## Publication rule", "", "A candidate is not publishable merely because it was normalized. It must pass Fidelity + Commerce, be staged in Shopify, and pass the storefront Render Gate before becoming featured media."]
    (output_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    make_contact_sheet(results, output_dir)


def run(manifest_path: Path, policy_path: Path, output_dir: Path, normalize_safe: bool) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    policy = Policy.load(policy_path)
    results = [audit_item(item, policy, output_dir, normalize_safe) for item in manifest["items"]]
    write_reports(results, output_dir)
    golden = [r for r in results if r.get("golden_test")]
    failures = [r for r in golden if not r.get("candidate_pass")]
    errors = [r for r in results if r["status"] == STATUS_ERROR]
    print((output_dir / "REPORT.md").read_text(encoding="utf-8"))
    return 1 if failures or errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Nima Commerce Media Factory: audit and safely normalize commerce assets")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path(__file__).with_name("policy.json"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--normalize-safe", action="store_true")
    args = parser.parse_args()
    return run(args.manifest, args.policy, args.out, args.normalize_safe)


if __name__ == "__main__":
    raise SystemExit(main())
