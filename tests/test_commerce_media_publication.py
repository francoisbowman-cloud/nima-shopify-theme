from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


publish_gate = load_module("nima_publish_gate", ROOT / "tools" / "nima_commerce_media" / "publish_gate.py")
omni_adapter = load_module("nima_omni_adapter", ROOT / "tools" / "nima_commerce_media" / "omni_adapter.py")


class CommerceMediaPublicationTests(unittest.TestCase):
    def audit(self):
        return {"results": [
            {
                "product_id": "gid://shopify/Product/1",
                "handle": "clean-product",
                "source": "https://example.com/source.jpg",
                "source_sha256": "abc",
                "status": "NORMALIZE",
                "candidate_pass": True,
                "normalized_file": "out/clean.png",
                "reasons": ["embedded_nonwhite_background"],
            },
            {
                "product_id": "gid://shopify/Product/2",
                "handle": "lifestyle-composite",
                "source": "https://example.com/source2.jpg",
                "source_sha256": "def",
                "status": "NORMALIZE",
                "candidate_pass": True,
                "normalized_file": "out/composite.png",
                "reasons": ["embedded_nonwhite_background"],
            },
            {
                "product_id": "gid://shopify/Product/3",
                "handle": "complex-source",
                "source": "https://example.com/source3.jpg",
                "source_sha256": "ghi",
                "status": "MANUAL_REVIEW",
                "candidate_pass": False,
                "reasons": ["complex_or_nonuniform_background"],
            },
        ]}

    def test_semantic_pass_is_required_for_publication(self):
        semantic = {
            "clean-product": {"status": "PASS", "reason": "product only"},
            "lifestyle-composite": {"status": "FAIL", "reason": "contains lifestyle subject"},
        }
        plan = publish_gate.build_publish_plan(self.audit(), semantic)
        self.assertEqual([x["handle"] for x in plan["approved_candidates"]], ["clean-product"])
        self.assertEqual([x["handle"] for x in plan["blocked_candidates"]], ["lifestyle-composite"])
        self.assertIn("SEMANTIC_PASS", plan["approved_candidates"][0]["required_gates"])
        self.assertIn("RENDER_PASS", plan["approved_candidates"][0]["required_gates"])

    def test_missing_semantic_decision_defaults_closed(self):
        plan = publish_gate.build_publish_plan(self.audit(), {})
        self.assertEqual(len(plan["approved_candidates"]), 0)
        self.assertEqual(len(plan["blocked_candidates"]), 2)
        self.assertTrue(all(x["semantic_gate"]["status"] == "REVIEW_REQUIRED" for x in plan["blocked_candidates"]))

    def test_omni_receives_technical_and_semantic_exceptions(self):
        semantic = {
            "clean-product": {"status": "PASS"},
            "lifestyle-composite": {"status": "FAIL", "reason": "contains lifestyle subject"},
        }
        batch = omni_adapter.build_omni_batch(self.audit(), semantic)
        handles = [x["consumer_metadata"]["image_id"] for x in batch["items"]]
        self.assertEqual(set(handles), {"lifestyle-composite", "complex-source"})
        composite = next(x for x in batch["items"] if x["consumer_metadata"]["image_id"] == "lifestyle-composite")
        self.assertEqual(composite["image"], "out/composite.png")


if __name__ == "__main__":
    unittest.main()
