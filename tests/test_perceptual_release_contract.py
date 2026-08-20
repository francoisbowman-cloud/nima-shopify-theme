from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"


def read(path):
    return (THEME / path).read_text(encoding="utf-8")


def test_footer_navigation_is_locale_driven_not_hardcoded_menu_copy():
    footer = read("sections/footer.liquid")
    en = read("locales/en.json")
    es = read("locales/es.default.json")
    assert "sections.footer.menu_" in footer
    assert "sections.footer.links." in footer
    for token in ['"menu_1_heading":"Shop"', '"menu_2_heading":"Help"', '"about":"About Nima"']:
        assert token in en
    for token in ['"menu_1_heading":"Tienda"', '"menu_2_heading":"Ayuda"', '"about":"Sobre Nima"']:
        assert token in es


def test_internal_omni_vocabulary_cannot_leak_into_product_story():
    story = read("sections/product-ovl-story.liquid")
    customer_markup = story.split("{% schema %}", 1)[0].lower()
    for forbidden in ("experiencia ovl", "omni visual language", "visual profile"):
        assert forbidden not in customer_markup
    assert "products.story.kicker" in story
    assert "products.story.heading" in story


def test_product_emotion_badges_are_locale_driven():
    story = read("sections/product-ovl-story.liquid")
    en = read("locales/en.json")
    es = read("locales/es.default.json")
    assert "products.emotions.tranquility" in story
    assert "products.emotions.security" in story
    assert "products.emotions.comfort" in story
    assert "products.emotions.tenderness" in story
    assert "products.emotions.freshness" in story
    assert "products.emotions.care" in story
    for token in ['"tranquility":"Calm"', '"security":"Security"', '"care":"Care"']:
        assert token in en
    for token in ['"tranquility":"Tranquilidad"', '"security":"Seguridad"', '"care":"Cuidado"']:
        assert token in es


def test_commercial_media_has_last_loaded_containment_guard():
    layout = read("layout/theme.liquid")
    css = read("assets/perceptual-hotfix.css")
    assert "perceptual-hotfix.css" in layout
    assert layout.index("perceptual-hotfix.css") > layout.index("home-b.css")
    assert "object-fit:contain!important" in css
    assert "overflow:hidden!important" in css
    assert "max-width:100%!important" in css
    assert "max-height:100%!important" in css
