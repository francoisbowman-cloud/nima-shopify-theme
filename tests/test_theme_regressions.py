import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ThemeRegressionTests(unittest.TestCase):
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
