from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "nima_commerce_media" / "factory.py"
SPEC = importlib.util.spec_from_file_location("nima_commerce_media_factory", MODULE_PATH)
factory = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = factory
SPEC.loader.exec_module(factory)
POLICY = factory.Policy.load(ROOT / "tools" / "nima_commerce_media" / "policy.json")


class CommerceMediaFactoryTests(unittest.TestCase):
    def make_product(self, bg=(236, 229, 219), size=(1000, 1000), box=(220, 260, 780, 740)):
        image = Image.new("RGB", size, bg)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(box, radius=80, fill=(28, 80, 142))
        draw.rectangle((460, 360, 540, 640), fill=(25, 25, 25))
        return image

    def test_nonwhite_uniform_background_is_normalize(self):
        image = self.make_product()
        metrics = factory.analyze_image(image, POLICY)
        status, reasons = factory.classify(metrics, POLICY)
        self.assertEqual(status, factory.STATUS_NORMALIZE)
        self.assertIn("embedded_nonwhite_background", reasons)

    def test_normalization_produces_pure_white_border(self):
        image = self.make_product()
        metrics = factory.analyze_image(image, POLICY)
        normalized = factory.normalize(image, POLICY, metrics["geometry_profile"])
        after = factory.analyze_image(normalized, POLICY, metrics["geometry_profile"])
        self.assertGreaterEqual(after["border_white_ratio"], 0.995)
        self.assertFalse(after["clipped"])

    def test_product_core_color_is_preserved(self):
        image = self.make_product()
        metrics = factory.analyze_image(image, POLICY)
        normalized = factory.normalize(image, POLICY, metrics["geometry_profile"])
        colors = normalized.getcolors(maxcolors=2_000_000)
        self.assertIsNotNone(colors)
        palette = [color for _, color in colors]
        self.assertTrue(any(abs(c[0]-28) < 8 and abs(c[1]-80) < 8 and abs(c[2]-142) < 8 for c in palette))

    def test_low_resolution_is_blocked(self):
        image = self.make_product(size=(500, 500), box=(100, 120, 400, 380))
        metrics = factory.analyze_image(image, POLICY)
        status, reasons = factory.classify(metrics, POLICY)
        self.assertEqual(status, factory.STATUS_LOW_RES)
        self.assertIn("source_resolution_below_contract", reasons)

    def test_clipped_foreground_requires_manual_review(self):
        image = self.make_product(box=(0, 200, 700, 800))
        metrics = factory.analyze_image(image, POLICY)
        status, reasons = factory.classify(metrics, POLICY)
        self.assertEqual(status, factory.STATUS_MANUAL)
        self.assertIn("foreground_touches_safe_edge", reasons)

    def test_complex_background_not_auto_normalized(self):
        image = Image.new("RGB", (1000, 1000), (240, 240, 240))
        draw = ImageDraw.Draw(image)
        for x in range(0, 1000, 20):
            draw.rectangle((x, 0, x + 9, 1000), fill=(170, 180, 190))
        draw.ellipse((250, 250, 750, 750), fill=(25, 90, 150))
        metrics = factory.analyze_image(image, POLICY)
        status, reasons = factory.classify(metrics, POLICY)
        self.assertEqual(status, factory.STATUS_MANUAL)
        self.assertIn("complex_or_nonuniform_background", reasons)

    def test_pipeline_writes_publish_plan_but_does_not_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "glove-like.png"
            self.make_product().save(source)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"items": [{
                "product_id": "gid://shopify/Product/1",
                "handle": "glove-like",
                "title": "Glove Like Golden",
                "source": str(source),
                "golden_test": "embedded-background"
            }]}), encoding="utf-8")
            out = root / "out"
            code = factory.run(manifest, ROOT / "tools" / "nima_commerce_media" / "policy.json", out, True)
            self.assertEqual(code, 0)
            plan = json.loads((out / "publish-plan.json").read_text(encoding="utf-8"))
            self.assertEqual(len(plan["candidates"]), 1)
            self.assertIn("SHOPIFY_STAGING", plan["candidates"][0]["required_gates"])
            self.assertIn("RENDER_PASS", plan["candidates"][0]["required_gates"])


if __name__ == "__main__":
    unittest.main()
