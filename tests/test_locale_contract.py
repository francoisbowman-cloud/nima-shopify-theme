import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"
LOCALES = {
    "en": THEME / "locales" / "en.json",
    "es": THEME / "locales" / "es.default.json",
}

TRANSLATION_RE = re.compile(r"(['\"])([A-Za-z0-9_.-]+)\1\s*\|\s*t\b")

DYNAMIC_REQUIRED_KEYS = {
    "sections.footer.newsletter_kicker",
    "sections.footer.newsletter_heading",
    "sections.footer.newsletter_placeholder",
    "sections.footer.newsletter_button",
    "sections.footer.newsletter_success",
    "sections.footer.tagline",
    "sections.magazine.kicker",
    "sections.magazine.heading",
    "sections.magazine.intro",
    "sections.magazine.feature_kicker",
    "sections.magazine.feature_heading",
    "sections.magazine.feature_text",
    "sections.magazine.feature_button",
    "sections.magazine.story_1_kicker",
    "sections.magazine.story_1_heading",
    "sections.magazine.story_1_text",
    "sections.magazine.story_2_kicker",
    "sections.magazine.story_2_heading",
    "sections.magazine.story_2_text",
    "sections.magazine.story_3_kicker",
    "sections.magazine.story_3_heading",
    "sections.magazine.story_3_text",
}


def _load_json_with_shopify_comment(path: Path):
    text = path.read_text(encoding="utf-8").lstrip()
    if text.startswith("/*"):
        end = text.find("*/")
        assert end != -1, f"Unclosed leading comment in {path}"
        text = text[end + 2 :].lstrip()
    return json.loads(text)


def _flatten(value, prefix=""):
    out = set()
    if isinstance(value, dict):
        for key, child in value.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            out |= _flatten(child, new_prefix)
    else:
        out.add(prefix)
    return out


def _liquid_translation_keys():
    keys = set()
    for path in THEME.rglob("*.liquid"):
        text = path.read_text(encoding="utf-8")
        keys.update(match.group(2) for match in TRANSLATION_RE.finditer(text))
    return keys


def _locale_key_sets():
    return {
        locale: _flatten(_load_json_with_shopify_comment(path))
        for locale, path in LOCALES.items()
    }


def test_all_literal_translation_keys_exist_in_en_and_es():
    used = _liquid_translation_keys()
    assert used, "No literal translation keys were detected in Liquid."

    locale_keys = _locale_key_sets()
    failures = []
    for locale, available in locale_keys.items():
        missing = sorted(used - available)
        if missing:
            failures.append(f"{locale}: {', '.join(missing)}")

    assert not failures, "Missing translation keys:\n" + "\n".join(failures)


def test_dynamic_magazine_and_footer_translation_keys_exist_in_en_and_es():
    locale_keys = _locale_key_sets()
    failures = []
    for locale, available in locale_keys.items():
        missing = sorted(DYNAMIC_REQUIRED_KEYS - available)
        if missing:
            failures.append(f"{locale}: {', '.join(missing)}")

    assert not failures, "Missing dynamic translation keys:\n" + "\n".join(failures)


def test_en_and_es_locale_structures_match():
    en = _flatten(_load_json_with_shopify_comment(LOCALES["en"]))
    es = _flatten(_load_json_with_shopify_comment(LOCALES["es"]))

    only_en = sorted(en - es)
    only_es = sorted(es - en)
    assert not only_en and not only_es, (
        "Locale key sets differ. "
        f"Only EN: {only_en or 'none'}; Only ES: {only_es or 'none'}"
    )
