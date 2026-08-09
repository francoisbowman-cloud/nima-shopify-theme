from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_premium_experience_assets_load_after_hardening():
    layout = read(THEME / "layout" / "theme.liquid")
    hardening = layout.index("premium-hardening.css")
    experience = layout.index("premium-experience.css")
    motion = layout.index("premium-motion.js")
    assert hardening < experience < motion


def test_commerce_images_use_border_box_containment():
    css = read(THEME / "assets" / "premium-experience.css")
    for selector in (
        ".pcard__media img",
        ".template-product .gallery__main>img",
        ".template-product [data-gallery-main]",
        ".template-cart .cart-item__media img",
    ):
        assert selector in css
    assert "box-sizing:border-box!important" in css
    assert "object-fit:contain!important" in css
    assert "background:#fff!important" in css


def test_supplier_media_gets_larger_safety_margin_than_refined_media():
    css = read(THEME / "assets" / "premium-experience.css").replace(" ", "")
    card = read(THEME / "snippets" / "product-card.liquid")
    assert 'data-media-grade="{{ media_grade }}"' in card
    assert "media_probe contains '-refined-'" in card
    assert '[data-media-grade="source"]' in css
    assert '[data-media-grade="refined"]' in css
    assert "padding:clamp(30px,14%,62px)!important" in css
    assert "padding:clamp(20px,9%,44px)!important" in css


def test_pdp_refined_media_can_use_tighter_safe_area_without_changing_fit_mode():
    css = read(THEME / "assets" / "premium-experience.css")
    assert '[data-gallery-main][src*="refined"]' in css
    assert "padding:clamp(28px,8%,62px)!important" in css
    assert "object-fit:contain!important" in css
    assert "object-fit:cover" not in "\n".join(
        line for line in css.splitlines() if "gallery__main" in line or "data-gallery-main" in line
    )


def test_magazine_has_real_scrim_and_white_copy():
    css = read(THEME / "assets" / "premium-experience.css")
    assert ".mag-hero:before" in css
    assert "linear-gradient" in css
    assert ".mag-hero .on-dark-heading{color:#fff!important" in css
    assert ".mag-hero__intro{color:rgba(255,255,255,.94)!important" in css


def test_premium_layer_transforms_all_priority_commerce_surfaces():
    css = read(THEME / "assets" / "premium-experience.css")
    for selector in (
        ".template-index .shop-window",
        ".template-collection .collection-head",
        ".template-product .product",
        ".template-search .search-form",
        ".template-cart .cart-summary",
    ):
        assert selector in css


def test_motion_is_progressive_and_reduced_motion_safe():
    js = read(THEME / "assets" / "premium-motion.js")
    css = read(THEME / "assets" / "premium-experience.css")
    assert "IntersectionObserver" in js
    assert "prefers-reduced-motion: reduce" in js
    assert "@media(prefers-reduced-motion:reduce)" in css
    assert "data-nima-reveal" in js
