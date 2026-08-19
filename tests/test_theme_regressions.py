import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ThemeRegressionTests(unittest.TestCase):
    def test_shopify_json_templates_are_valid_after_generated_header(self):
        paths = sorted((ROOT / "theme").rglob("*.json"))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                source = path.read_text(encoding="utf-8")
                source = re.sub(r"^\s*/\*.*?\*/\s*", "", source, flags=re.DOTALL)
                json.loads(source)

    def test_search_schema_does_not_put_template_braces_in_filter_string(self):
        source = (ROOT / "theme/snippets/structured-data.liquid").read_text(encoding="utf-8")
        self.assertIn("capture schema_search_target", source)
        self.assertNotRegex(source, r"append:\s*['\"][^'\"]*\{search_term_string\}")

    def test_dual_split_resets_generic_split_grid_and_child_padding(self):
        css = (ROOT / "theme/assets/base.css").read_text(encoding="utf-8")
        self.assertIn(".split--b{display:block;min-height:0", css)
        self.assertIn(".split--b>div{padding:0}", css)

    def test_add_to_cart_feedback_does_not_restore_stale_variant_state(self):
        source = (ROOT / "theme/assets/global.js").read_text(encoding="utf-8")
        self.assertIn("submittedVariantId", source)
        self.assertIn("syncAddButtonToCurrentVariant(form, btn)", source)
        self.assertIn("idInput.value === submittedVariantId", source)
        self.assertIn("id: submittedVariantId", source)
        self.assertNotIn("setTimeout(function () {\n          if (btn) { btn.disabled = false; btn.textContent = original; }", source)

    def test_product_cards_guard_against_supplier_listing_alt_text(self):
        helper = (ROOT / "theme/snippets/product-image-alt.liquid").read_text(encoding="utf-8")
        card = (ROOT / "theme/snippets/product-card.liquid").read_text(encoding="utf-8")
        self.assertIn("safe_alt.size > 140", helper)
        self.assertIn("assign safe_alt = product.title", helper)
        self.assertIn("render 'product-image-alt'", card)
        self.assertNotIn("product.featured_image.alt | default: product.title", card)

    def test_product_and_collection_meta_descriptions_have_content_fallbacks(self):
        source = (ROOT / "theme/layout/theme.liquid").read_text(encoding="utf-8")
        self.assertIn("when 'product'", source)
        self.assertIn("product.description | strip_html | strip_newlines | truncate: 160", source)
        self.assertIn("when 'collection'", source)
        self.assertIn("collection.description | strip_html | strip_newlines | truncate: 160", source)

    def test_css_override_layer_budget_cannot_silently_grow(self):
        source = (ROOT / "theme/layout/theme.liquid").read_text(encoding="utf-8")
        stylesheets = re.findall(r"\{\{\s*'([^']+\.css)'\s*\|\s*asset_url\s*\|\s*stylesheet_tag\s*\}\}", source)
        expected = [
            "base.css",
            "launch.css",
            "premium.css",
            "premium-home.css",
            "release-hotfix.css",
            "audit-polish.css",
            "commerce-white.css",
            "pdp-gallery-fix.css",
            "home-b.css",
        ]
        self.assertEqual(stylesheets, expected)
        self.assertLessEqual(len(stylesheets), 9)


if __name__ == "__main__":
    unittest.main()