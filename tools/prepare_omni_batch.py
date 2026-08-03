#!/usr/bin/env python3
"""Create an OMNI batch manifest from locally exported Shopify product images."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def safe_id(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-") or "product-image"


def build_manifest(images_dir: Path, preset: str) -> dict:
    images = sorted(
        path.resolve()
        for path in images_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    return {
        "batch_id": "nima-catalog-review",
        "items": [
            {
                "image": str(path),
                "preset": preset,
                "consumer_metadata": {"image_id": f"{safe_id(path)}-{index:03d}"},
            }
            for index, path in enumerate(images, start=1)
        ],
    }


def build_shopify_manifest(source_csv: Path, preset: str, *, primary_only: bool = False) -> dict:
    """Build a deterministic remote-image batch from a Shopify product export."""

    with source_csv.open(newline="", encoding="utf-8-sig") as source:
        rows = list(csv.DictReader(source))
    if not rows or "Handle" not in rows[0] or "Image Src" not in rows[0]:
        raise ValueError("Expected a Shopify CSV containing Handle and Image Src")

    items: list[dict[str, object]] = []
    seen_urls: set[str] = set()
    seen_handles: set[str] = set()
    for row in rows:
        handle = row.get("Handle", "").strip()
        image_url = row.get("Image Src", "").strip()
        if not handle or not image_url or image_url in seen_urls:
            continue
        if primary_only and handle in seen_handles:
            continue
        parsed = urlparse(image_url)
        if parsed.scheme != "https" or not parsed.netloc:
            continue
        position = row.get("Image Position", "").strip() or "1"
        extension = Path(parsed.path).suffix.lower()
        if extension not in IMAGE_EXTENSIONS:
            continue
        items.append(
            {
                "product_id": safe_id(Path(handle)),
                "image": image_url,
                "preset": preset,
                "consumer_metadata": {
                    "image_id": f"{safe_id(Path(handle))}-{position}",
                    "source": "shopify-csv",
                    "image_position": position,
                },
            }
        )
        seen_urls.add(image_url)
        seen_handles.add(handle)

    return {"batch_id": "nima-shopify-catalog-review", "items": items}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Image directory or Shopify product CSV")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preset", default="nima-product")
    parser.add_argument(
        "--primary-only",
        action="store_true",
        help="For Shopify CSV input, include only the first image per product.",
    )
    args = parser.parse_args()
    if args.source.is_dir():
        manifest = build_manifest(args.source, args.preset)
    elif args.source.suffix.lower() == ".csv":
        manifest = build_shopify_manifest(
            args.source, args.preset, primary_only=args.primary_only
        )
    else:
        raise SystemExit("Source must be an image directory or Shopify CSV")
    if not manifest["items"]:
        raise SystemExit("No supported JPG, PNG or WebP images found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(manifest['items'])} image(s): {args.output}")


if __name__ == "__main__":
    main()
