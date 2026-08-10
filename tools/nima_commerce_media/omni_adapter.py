from __future__ import annotations

import argparse
import json
from pathlib import Path

OMNI_PRESET = "nima-product"


def load_semantic(path: Path | None) -> dict[str, dict]:
    if not path or not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("decisions", {})


def build_omni_batch(audit: dict, semantic: dict[str, dict] | None = None) -> dict:
    semantic = semantic or {}
    items = []
    for row in audit.get("results", []):
        decision = semantic.get(row.get("handle"), {"status": "REVIEW_REQUIRED"})
        unresolved_technical = row.get("status") in {"MANUAL_REVIEW", "NORMALIZE"} and not row.get("candidate_pass")
        unresolved_semantic = bool(row.get("candidate_pass")) and decision.get("status") != "PASS"
        if not (unresolved_technical or unresolved_semantic):
            continue
        items.append({
            "product_id": row.get("product_id"),
            "image": row.get("normalized_file") if unresolved_semantic else row["source"],
            "preset": OMNI_PRESET,
            "consumer_metadata": {
                "image_id": row.get("handle"),
                "nima_media_status": row.get("status"),
                "nima_media_reasons": row.get("reasons", []),
                "semantic_gate": decision,
                "contract": "Nima Commerce Media Contract v1",
                "required_output": "product-preserving commerce asset; pure white background; product-only primary image; no generative product replacement"
            }
        })
    return {
        "batch_id": "nima-commerce-media-omni-review",
        "policy": "OMNI is a treatment/semantic adapter, not the publication authority",
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Route Nima media exceptions to OMNI")
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--semantic", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    batch = build_omni_batch(audit, load_semantic(args.semantic))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OMNI exceptions prepared: {len(batch['items'])}")


if __name__ == "__main__":
    main()
