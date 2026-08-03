import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.catalog_copy_generator import (
    clean_title,
    generate,
    proposal_for,
    seo_description,
    truncate_words,
)
from tools.prepare_omni_batch import build_manifest, build_shopify_manifest


class CatalogCopyTests(unittest.TestCase):
    def test_removes_supplier_noise_without_translating_facts(self):
        self.assertEqual(clean_title("Dog Leash | AutoDS Fast Shipping"), "Dog Leash")

    def test_title_shortening_never_cuts_a_word(self):
        title = clean_title(
            "Dog Bed Crate Pad Ultra Soft Pet Mat Star Print 22 Inch Brown Washable Crate Mat"
        )
        self.assertLessEqual(len(title), 70)
        self.assertFalse(title.endswith("Washab"))
        self.assertEqual(truncate_words("one two three", 8), "one two")

    def test_seo_description_never_cuts_a_word(self):
        description = seo_description(
            "Dog Bed",
            "A padded surface designed for everyday rest and a removable washable cover "
            "that simplifies routine care in homes with dogs.",
        )
        self.assertLessEqual(len(description), 155)
        self.assertFalse(description.endswith("dog"))

    def test_html_blocks_become_reviewable_bullets(self):
        result = proposal_for(
            {
                "Handle": "x",
                "Title": "Dog Bed",
                "Body (HTML)": "<p>A padded bed for daily rest.</p><ul><li>Removable washable cover</li><li>Non-slip base for smooth floors</li></ul>",
                "Image Src": "x.jpg",
            }
        )
        self.assertIn("<h2>Lo esencial</h2>", result["Proposed Body (HTML)"])
        self.assertIn("Removable washable cover", result["Proposed Body (HTML)"])

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
            self.assertNotIn("image_id", manifest["items"][0])
            self.assertEqual(
                manifest["items"][0]["consumer_metadata"]["image_id"],
                "dog-bed-001",
            )

    def test_shopify_manifest_can_select_one_primary_image_per_product(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "products.csv"
            with source.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file, fieldnames=["Handle", "Image Src", "Image Position"]
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {"Handle": "dog-bed", "Image Src": "https://cdn.test/bed-1.jpg", "Image Position": "1"},
                        {"Handle": "dog-bed", "Image Src": "https://cdn.test/bed-2.jpg", "Image Position": "2"},
                        {"Handle": "cat-toy", "Image Src": "https://cdn.test/toy.png", "Image Position": "1"},
                    ]
                )
            manifest = build_shopify_manifest(source, "nima-product", primary_only=True)
            self.assertEqual(len(manifest["items"]), 2)
            self.assertEqual(manifest["items"][0]["product_id"], "dog-bed")
            self.assertEqual(manifest["items"][0]["consumer_metadata"]["source"], "shopify-csv")
            self.assertEqual(
                manifest["items"][0]["consumer_metadata"]["image_id"],
                "dog-bed-1",
            )


if __name__ == "__main__":
    unittest.main()
