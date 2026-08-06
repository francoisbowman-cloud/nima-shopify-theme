from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
FORBIDDEN_TOKENS = ["myshopify.com", "/admin/api/", "graphql", "shopify_staged_upload", "requests.post", "requests.get"]


def test_no_shopify_or_network_calls_outside_openai_client():
    offending = []
    for path in SRC_DIR.glob("*.py"):
        if path.name == "openai_client.py":
            continue  # the only module allowed to make network calls, and only to OpenAI
        text = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_TOKENS:
            if token in text:
                offending.append((path.name, token))
    assert offending == []
