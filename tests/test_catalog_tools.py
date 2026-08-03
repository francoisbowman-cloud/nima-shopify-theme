import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.catalog_copy_generator import clean_title, generate, proposal_for
from tools.prepare_omni_batch import build_manifest


class CatalogCopyTests(unittest.TestCase):
    def test_removes_supplier_noise_without_translating_facts(self):
        self.assertEqual(clean_title("Dog Leash | AutoDS Fast Shipping"), "Dog Leash")

    def test_blocks_missing_image(self):
        result = proposal_for({"Handle": "x", "Title": "Dog Bed", "Body (HTML)": "A padded bed for daily rest.", "Image Src": ""})
        self.assertEqual(result["Status"], "BLOCKED")
        self.assertIn("missing_image", result["Review Notes"])

    def test_body_uses_only_existing_evidence(self):
        result = proposal_for({"Handle": "x", "Title": "Dog Bed", "Body (HTML)": "Soft padded surface for daily rest. Removable cover for cleaning.", "Image Src": "https://example.test/x.jpg"})
        self.assertIn("Soft padded surface", result["Proposed Body (HTML)"])
        self.assertIn("Removable cover", result["Proposed Body (HTML)"])
        self.assertEqual(result["Status"], "REVIEW_REQUIRED")

    def test_generates_one_proposal_per_handle(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "products.csv"
            output = Path(temp) / "review.csv"
            with source.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=["Handle", "Title", "Body (HTML)", "Image Src"])
                writer.writeheader()
                writer.writerows([
                    {"Handle": "bed", "Title": "Dog Bed", "Body (HTML)": "A padded bed for daily rest.", "Image Src": ""},
                    {"Handle": "bed", "Title": "Dog Bed", "Body (HTML)": "", "Image Src": "y.jpg"},
                ])
            self.assertEqual(generate(source, output), 1)
            with output.open(newline="", encoding="utf-8-sig") as file:
                proposal = next(csv.DictReader(file))
            self.assertEqual(proposal["Image Src"], "y.jpg")
            self.assertEqual(proposal["Status"], "REVIEW_REQUIRED")


class OmniManifestTests(unittest.TestCase):
    def test_manifest_only_includes_supported_images(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "dog bed.jpg").write_bytes(b"image")
            (root / "notes.txt").write_text("skip")
            manifest = build_manifest(root, "nima-product")
            self.assertEqual(len(manifest["items"]), 1)
            self.assertEqual(manifest["items"][0]["preset"], "nima-product")


if __name__ == "__main__":
    unittest.main()
