from __future__ import annotations

import argparse
import json
from pathlib import Path

SEMANTIC_PASS = "PASS"
SEMANTIC_REVIEW = "REVIEW_REQUIRED"


def load_semantic(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("decisions", {})


def build_publish_plan(audit: dict, semantic: dict[str, dict]) -> dict:
    approved = []
    blocked = []
    for row in audit.get("results", []):
        if not row.get("candidate_pass"):
            continue
        handle = row.get("handle")
        decision = semantic.get(handle, {"status": SEMANTIC_REVIEW, "reason": "semantic_gate_not_recorded"})
        entry = {
            "product_id": row.get("product_id"),
            "handle": handle,
            "source_sha256": row.get("source_sha256"),
            "candidate_file": row.get("normalized_file"),
            "semantic_gate": decision,
        }
        if decision.get("status") == SEMANTIC_PASS:
            entry["required_gates"] = [
                "FIDELITY_PASS",
                "COMMERCE_PASS",
                "SEMANTIC_PASS",
                "SHOPIFY_STAGING",
                "RENDER_PASS",
            ]
            approved.append(entry)
        else:
            blocked.append(entry)
    return {
        "version": 2,
        "policy": "No technical candidate can reach Shopify publication without an explicit semantic PASS.",
        "approved_candidates": approved,
        "blocked_candidates": blocked,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply semantic publication gate to Nima media candidates")
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--semantic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    plan = build_publish_plan(audit, load_semantic(args.semantic))
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Semantic-approved candidates: {len(plan['approved_candidates'])}")
    print(f"Semantic-blocked candidates: {len(plan['blocked_candidates'])}")


if __name__ == "__main__":
    main()
