#!/usr/bin/env python3
"""Generate review-ready Shopify copy proposals without inventing facts.

The input is Shopify's product CSV export. The source file is never modified.
Rows with insufficient source evidence are explicitly blocked for manual review.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
from html.parser import HTMLParser
from pathlib import Path


TITLE_NOISE = (
    r"\b(?:us seller|fast shipping|free shipping|hot sale|best seller)\b",
    r"\b(?:for dogs? cats?|for cats? dogs?)\b(?=\s*$)",
    r"\s*[|/]\s*(?:autods|amazon|ebay|walmart).*$",
)
SPACE_RE = re.compile(r"\s+")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "br"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in BLOCK_TAGS:
            self.parts.append(". ")


def truncate_words(value: str, limit: int) -> str:
    """Shorten text without cutting a word or leaving trailing punctuation."""

    value = SPACE_RE.sub(" ", value).strip()
    if len(value) <= limit:
        return value.rstrip(" ,;:-|")
    shortened = value[: limit + 1].rsplit(" ", 1)[0]
    return shortened.rstrip(" ,;:-|")


def html_to_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(value or "")
    return SPACE_RE.sub(" ", html.unescape(" ".join(parser.parts))).strip()


def clean_title(value: str) -> str:
    title = html_to_text(value)
    for pattern in TITLE_NOISE:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)
    title = title.split("|", 1)[0]
    title = re.sub(r"^[\s'\"-]+|\s*[-–—,:;]+\s*$", "", title)
    title = SPACE_RE.sub(" ", title).strip()
    return truncate_words(title, 70)


def evidence_sentences(body_html: str, limit: int = 4) -> list[str]:
    text = html_to_text(body_html)
    if not text:
        return []
    sentences: list[str] = []
    for sentence in SENTENCE_RE.split(text):
        candidate = SPACE_RE.sub(" ", sentence).strip(" -•\t")
        if len(candidate) < 18:
            continue
        if re.search(r"\b(?:guaranteed|best|perfect|miracle|cure|100%)\b", candidate, re.I):
            continue
        sentences.append(truncate_words(candidate, 240))
        if len(sentences) == limit:
            break
    return sentences


def proposed_body(title: str, body_html: str) -> tuple[str, str]:
    facts = evidence_sentences(body_html)
    if not facts:
        return "", "NEEDS_EVIDENCE"
    intro = facts[0]
    bullets = facts[1:]
    body = [f"<p>{html.escape(intro)}</p>"]
    if bullets:
        body.append("<h2>Lo esencial</h2><ul>")
        body.extend(f"<li>{html.escape(item)}</li>" for item in bullets)
        body.append("</ul>")
    body.append(
        "<p><strong>Antes de comprar:</strong> revisa las variantes, medidas y "
        "recomendaciones disponibles en esta ficha.</p>"
    )
    return "".join(body), "REVIEW_REQUIRED"


def seo_description(title: str, body_html: str) -> str:
    facts = evidence_sentences(body_html, limit=1)
    if not facts:
        return ""
    value = f"{title}: {facts[0]}"
    return truncate_words(value, 155)


def proposal_for(row: dict[str, str]) -> dict[str, str]:
    source_title = row.get("Title", "")
    source_body = row.get("Body (HTML)", "")
    title = clean_title(source_title)
    body, status = proposed_body(title, source_body)
    reasons: list[str] = []
    if title != source_title.strip():
        reasons.append("supplier_title_cleaned")
    if not body:
        reasons.append("missing_verified_description")
    if not row.get("Image Src", "").strip():
        reasons.append("missing_image")
        status = "BLOCKED"
    return {
        "Handle": row.get("Handle", ""),
        "Source Title": source_title,
        "Proposed Title": title,
        "Proposed Body (HTML)": body,
        "Proposed SEO Title": (f"{title} | Nima" if title else "")[:70],
        "Proposed SEO Description": seo_description(title, source_body),
        "Image Src": row.get("Image Src", ""),
        "Status": status,
        "Review Notes": ",".join(reasons),
    }


FIELDS = [
    "Handle",
    "Source Title",
    "Proposed Title",
    "Proposed Body (HTML)",
    "Proposed SEO Title",
    "Proposed SEO Description",
    "Image Src",
    "Status",
    "Review Notes",
]


def generate(source: Path, output: Path) -> int:
    with source.open(newline="", encoding="utf-8-sig") as infile:
        rows = list(csv.DictReader(infile))
    if not rows or "Title" not in rows[0] or "Handle" not in rows[0]:
        raise ValueError("Expected a Shopify product CSV containing Handle and Title")

    # Shopify exports one row per variant/image. Propose copy once per product.
    first_by_handle: dict[str, dict[str, str]] = {}
    for row in rows:
        handle = row.get("Handle", "").strip()
        if not handle:
            continue
        if handle not in first_by_handle:
            first_by_handle[handle] = dict(row)
            continue
        product = first_by_handle[handle]
        for field in ("Title", "Body (HTML)", "Image Src"):
            if not product.get(field, "").strip() and row.get(field, "").strip():
                product[field] = row[field]

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(proposal_for(row) for row in first_by_handle.values())
    return len(first_by_handle)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Shopify product CSV export")
    parser.add_argument("--output", type=Path, required=True, help="Review proposal CSV")
    args = parser.parse_args()
    count = generate(args.source, args.output)
    print(f"Generated {count} review proposal(s): {args.output}")


if __name__ == "__main__":
    main()
