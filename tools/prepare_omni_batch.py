#!/usr/bin/env python3
"""Create an OMNI batch manifest from locally exported Shopify product images."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


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
            {"image_id": f"{safe_id(path)}-{index:03d}", "image": str(path), "preset": preset}
            for index, path in enumerate(images, start=1)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preset", default="nima-product")
    args = parser.parse_args()
    manifest = build_manifest(args.images_dir, args.preset)
    if not manifest["items"]:
        raise SystemExit("No JPG, PNG or WebP images found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(manifest['items'])} image(s): {args.output}")


if __name__ == "__main__":
    main()
