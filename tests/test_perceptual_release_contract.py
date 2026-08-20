from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; THEME=ROOT/'theme'
def read(path): return (THEME/path).read_text(encoding='utf-8')

def test_footer_navigation_uses_route_identity_not_admin_titles_or_handles():
    footer=read('sections/footer.liquid'); en=read('locales/en.json'); es=read('locales/es.default.json')
    assert "normalized_path = link.url" in footer
    assert "normalized_path == '/' or normalized_path == routes.root_url" in footer
    assert "link.handle" not in footer
    assert "sections.footer.links.home" in footer
    for token in ['"home":"Home"','"catalog":"Catalog"','"about":"About Nima"']: assert token in en
    for token in ['"home":"Inicio"','"catalog":"Catálogo"','"about":"Sobre Nima"']: assert token in es

def test_internal_omni_vocabulary_cannot_leak_into_product_story():
    story=read('sections/product-ovl-story.liquid'); customer=story.split('{% schema %}',1)[0].lower()
    for forbidden in ('experiencia ovl','omni visual language','visual profile'): assert forbidden not in customer
    assert 'products.story.kicker' in story and 'products.story.heading' in story

def test_product_emotion_badges_are_locale_driven():
    story=read('sections/product-ovl-story.liquid'); en=read('locales/en.json'); es=read('locales/es.default.json')
    for key in ('tranquility','security','comfort','tenderness','freshness','care'): assert f'products.emotions.{key}' in story
    for token in ['"tranquility":"Calm"','"security":"Security"','"care":"Care"']: assert token in en
    for token in ['"tranquility":"Tranquilidad"','"security":"Seguridad"','"care":"Cuidado"']: assert token in es

def test_commercial_media_has_last_loaded_containment_guard():
    layout=read('layout/theme.liquid'); css=read('assets/perceptual-hotfix.css')
    assert 'perceptual-hotfix.css' in layout and layout.index('perceptual-hotfix.css')>layout.index('home-b.css')
    for rule in ('object-fit:contain!important','overflow:hidden!important','max-width:100%!important','max-height:100%!important'): assert rule in css
