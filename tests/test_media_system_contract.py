from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"


def _read(path: str) -> str:
    return (THEME / path).read_text(encoding="utf-8")


def test_premium_hardening_is_loaded_after_gallery_and_white_contracts():
    layout = _read("layout/theme.liquid")
    assert "premium-hardening.css" in layout
    assert layout.index("commerce-white.css") < layout.index("pdp-gallery-fix.css")
    assert layout.index("pdp-gallery-fix.css") < layout.index("premium-hardening.css")


def test_commercial_media_uses_white_contain_geometry_without_browser_crop():
    css = _read("assets/premium-hardening.css").replace(" ", "").lower()
    required = (
        ".pcard__media",
        ".template-product.gallery__main",
        ".template-product.gallery__thumbs",
        ".template-cart.cart-item__media",
    )
    for selector in required:
        assert selector in css
    assert css.count("object-fit:contain!important") >= 4
    assert "background:#fff!important" in css
    assert "max-width:100%!important" in css
    assert "max-height:100%!important" in css
    assert "object-position:center!important" in css
    assert "transform:none!important" in css


def test_editorial_media_is_explicitly_separate_from_commerce_media():
    css = _read("assets/premium-hardening.css").replace(" ", "").lower()
    assert ".template-collection.collection-visualimg" in css
    assert ".mag-grid.feature__media" in css
    assert "object-fit:cover!important" in css
    assert ".pcard__mediaimg" in css
    assert "object-fit:contain!important" in css


def test_magazine_legibility_motion_and_link_contract():
    css = _read("assets/premium-hardening.css").replace(" ", "").lower()
    source = _read("sections/magazine-grid.liquid")
    assert ".mag-grid.mag-media-scrim" in css
    assert ".mag-grid.feature__contenth2{color:#fff" in css
    assert "prefers-reduced-motion:reduce" in css
    assert 'class="mag-media-scrim"' in source
    assert "feature_button_url != blank" in source
    assert "side-story--linked" in source
    assert "side-story__arrow" in source
    assert "default: '#'" not in source


def test_pdp_assurance_iconography_is_semantic_and_decorative_to_at():
    source = _read("sections/main-product.liquid")
    assert 'class="trust trust--center"' in source
    assert source.count('class="trust__icon"') >= 5
    assert source.count('aria-hidden="true"') >= 5
    assert "products.purchase_assurances" in source


def test_cart_product_images_have_stable_semantic_media_wrapper():
    source = _read("sections/main-cart.liquid")
    assert 'class="cart-item__media"' in source
    assert 'class="cart-item__actions"' in source
    assert 'class="cart-summary"' in source
    assert 'loading="lazy"' in source


def test_search_uses_premium_structure_without_inline_layout_styles():
    source = _read("sections/main-search.liquid")
    assert 'class="search-page"' in source
    assert 'class="search-page__intro"' in source
    assert 'class="search-form"' in source
    assert "style=" not in source
