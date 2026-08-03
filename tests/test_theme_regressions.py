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


if __name__ == "__main__":
    unittest.main()
