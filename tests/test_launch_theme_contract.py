from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"


def _load_shopify_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").lstrip()
    if text.startswith("/*"):
        end = text.find("*/")
        assert end != -1, f"unterminated leading comment in {path}"
        text = text[end + 2 :].lstrip()
    return json.loads(text)


def _lookup(data: dict, dotted_key: str):
    value = data
    for part in dotted_key.split("."):
        value = value[part]
    return value


def test_launch_templates_reference_existing_sections():
    for template_name in ("index.json", "product.json"):
        template = _load_shopify_json(THEME / "templates" / template_name)
        for section in template["sections"].values():
            section_file = THEME / "sections" / f"{section['type']}.liquid"
            assert section_file.exists(), f"missing section {section_file}"


def test_launch_locale_key_parity():
    en = _load_shopify_json(THEME / "locales" / "en.json")
    es = _load_shopify_json(THEME / "locales" / "es.default.json")
    required = (
        "announcement.shipping_returns",
        "home.shop_window.kicker",
        "home.shop_window.heading",
        "home.shop_window.text",
        "home.shop_window.view_all",
        "products.cross_sell.kicker",
        "products.cross_sell.heading",
        "products.cross_sell.text",
        "products.cross_sell.view_all",
    )
    for key in required:
        assert _lookup(en, key)
        assert _lookup(es, key)


def test_launch_liquid_translation_keys_exist_in_both_locales():
    en = _load_shopify_json(THEME / "locales" / "en.json")
    es = _load_shopify_json(THEME / "locales" / "es.default.json")
    files = (
        THEME / "sections" / "editorial-shop-window.liquid",
        THEME / "sections" / "product-routine-cross-sell.liquid",
    )
    pattern = re.compile(r"['\"]([a-z0-9_.-]+)['\"]\s*\|\s*t\b")
    for path in files:
        for key in pattern.findall(path.read_text(encoding="utf-8")):
            assert _lookup(en, key), f"missing EN key {key} from {path.name}"
            assert _lookup(es, key), f"missing ES key {key} from {path.name}"


def test_launch_stylesheet_is_loaded_after_base_css():
    layout = (THEME / "layout" / "theme.liquid").read_text(encoding="utf-8")
    base = layout.index("base.css")
    launch = layout.index("launch.css")
    assert base < launch


def test_home_shop_window_precedes_editorial_discovery_blocks():
    template = _load_shopify_json(THEME / "templates" / "index.json")
    order = template["order"]
    assert order.index("shop-window") < order.index("split")
    assert order.index("shop-window") < order.index("magazine-teaser")


def test_product_cross_sell_is_last_product_template_section():
    template = _load_shopify_json(THEME / "templates" / "product.json")
    assert template["order"][-1] == "routine-cross-sell"


def test_product_cross_sell_has_real_catalog_fallback():
    section = (THEME / "sections" / "product-routine-cross-sell.liquid").read_text(encoding="utf-8")
    assert "collections['all']" in section
    assert "rendered_count == 0" in section
    assert "source_collection.handle != 'all'" in section


def test_home_shop_window_has_catalog_fallback():
    section = (THEME / "sections" / "editorial-shop-window.liquid").read_text(encoding="utf-8")
    assert "collections['all']" in section
    assert "routes.all_products_collection_url" in section
