from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"


def test_gallery_fix_loaded_after_commerce_white():
    layout = (THEME / "layout" / "theme.liquid").read_text(encoding="utf-8")
    assert "pdp-gallery-fix.css" in layout
    assert layout.index("commerce-white.css") < layout.index("pdp-gallery-fix.css")


def test_mobile_thumbnails_cannot_wrap():
    css = (THEME / "assets" / "pdp-gallery-fix.css").read_text(encoding="utf-8").lower()
    assert "@media(max-width:800px)" in css
    assert "flex-wrap:nowrap!important" in css
    assert "overflow-x:auto" in css
    assert "position:static!important" in css
    assert "order:2" in css


def test_desktop_thumbnails_are_isolated_column():
    css = (THEME / "assets" / "pdp-gallery-fix.css").read_text(encoding="utf-8").lower()
    assert "@media(min-width:801px)" in css
    assert "flex-direction:column" in css
    assert "padding-left:84px" in css
    assert "position:absolute" in css
    assert "overflow-y:auto" in css
