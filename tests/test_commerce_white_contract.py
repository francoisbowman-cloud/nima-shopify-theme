from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"


def test_commerce_white_stylesheet_is_loaded_last():
    layout = (THEME / "layout" / "theme.liquid").read_text(encoding="utf-8")
    assert "commerce-white.css" in layout
    assert layout.index("audit-polish.css") < layout.index("commerce-white.css")


def test_commerce_white_contract_covers_commercial_surfaces():
    css = (THEME / "assets" / "commerce-white.css").read_text(encoding="utf-8")
    required_selectors = (
        ".pcard__media",
        ".shop-window__item .pcard__media",
        ".routine-cross-sell__item .pcard__media",
        ".template-collection .pcard__media",
        ".template-search .pcard__media",
        ".template-product .gallery__main",
        ".template-product .gallery__thumbs",
    )
    for selector in required_selectors:
        assert selector in css, f"commerce white selector missing: {selector}"


def test_commerce_media_never_uses_cover():
    css = (THEME / "assets" / "commerce-white.css").read_text(encoding="utf-8").lower()
    assert "object-fit:contain" in css
    assert "object-fit:cover" not in css
    assert "--nima-commerce-white:#fff" in css
