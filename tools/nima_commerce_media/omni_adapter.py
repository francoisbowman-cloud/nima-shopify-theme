from __future__ import annotations

import argparse
import json
from pathlib import Path

OMNI_PRESET = "nima-product"


def build_omni_batch(audit: dict) -> dict:
    items = []
    for row in audit.get("results", []):
        if row.get("status") not in {"MANUAL_REVIEW", "NORMALIZE"}:
            continue
        if row.get("candidate_pass"):
            continue
        items.append({
            "product_id": row.get("product_id"),
            "image": row["source"],
            "preset": OMNI_PRESET,
            "consumer_metadata": {
                "image_id": row.get("handle"),
                "nima_media_status": row.get("status"),
                "nima_media_reasons": row.get("reasons", []),
                "contract": "Nima Commerce Media Contract v1",
                "required_output": "product-preserving commerce asset; pure white background; no generative product replacement"
            }
        })
    return {
        "batch_id": "nima-commerce-media-omni-review",
        "policy": "OMNI is a treatment adapter, not the publication authority",
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Route Nima media exceptions to OMNI")
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    batch = build_omni_batch(audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OMNI exceptions prepared: {len(batch['items'])}")


if __name__ == "__main__":
    main()
