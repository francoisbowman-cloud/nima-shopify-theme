"""v0.3 Block 8 — benchmark comparison mode.

Produces a single labeled image so a person can judge whether v0.3 actually
improved on v0.2, without reading any JSON or code — same "don't just say
tests pass" principle as visual_debug.py in v0.2.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .visual_debug import thumb

LARGE_SIZE = (480, 480)
LABEL_HEIGHT = 50


def build_comparison_image(
    *,
    v02_result: Image.Image,
    v03_result: Image.Image,
    v02_label: str = "V0.2 RESULT",
    v03_label: str = "V0.3 RESULT",
    output_path: Path,
) -> Path:
    font = ImageFont.load_default()
    sheet = Image.new("RGB", (2 * LARGE_SIZE[0], LARGE_SIZE[1] + LABEL_HEIGHT), "white")
    draw = ImageDraw.Draw(sheet)

    left_thumb = thumb(v02_result, LARGE_SIZE)
    right_thumb = thumb(v03_result, LARGE_SIZE)
    sheet.paste(left_thumb, (0, 0))
    sheet.paste(right_thumb, (LARGE_SIZE[0], 0))

    draw.line([(LARGE_SIZE[0], 0), (LARGE_SIZE[0], LARGE_SIZE[1])], fill="black", width=2)
    draw.rectangle((0, LARGE_SIZE[1], LARGE_SIZE[0], LARGE_SIZE[1] + LABEL_HEIGHT), fill=(40, 40, 40))
    draw.rectangle((LARGE_SIZE[0], LARGE_SIZE[1], 2 * LARGE_SIZE[0], LARGE_SIZE[1] + LABEL_HEIGHT), fill=(30, 110, 60))
    draw.text((16, LARGE_SIZE[1] + 16), v02_label, fill="white", font=font)
    draw.text((LARGE_SIZE[0] + 16, LARGE_SIZE[1] + 16), v03_label, fill="white", font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, "JPEG", quality=92)
    return output_path


def build_full_comparison_contact_sheet(
    *,
    source: Image.Image,
    cutout: Image.Image,
    background: Image.Image,
    v02_result: Image.Image,
    v03_result: Image.Image,
    output_path: Path,
) -> Path:
    """Extended version with source/cutout/background context alongside the
    v0.2-vs-v0.3 comparison — used by the real pilot (Block 11) where the
    extra context matters for judging *why* v0.3 differs, not just *that*
    it does."""
    cells = [
        ("SOURCE", source),
        ("CUTOUT", cutout),
        ("BACKGROUND", background),
        ("V0.2 RESULT", v02_result),
        ("V0.3 RESULT", v03_result),
    ]
    thumb_size = (300, 300)
    label_height = 40
    columns = 3
    rows = (len(cells) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_size[0], rows * (thumb_size[1] + label_height)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, (label, img) in enumerate(cells):
        col, row = index % columns, index // columns
        x, y = col * thumb_size[0], row * (thumb_size[1] + label_height)
        sheet.paste(thumb(img, thumb_size), (x, y))
        color = "black"
        if label == "V0.3 RESULT":
            color = "green"
        elif label == "V0.2 RESULT":
            color = "#555555"
        draw.text((x + 6, y + thumb_size[1] + 8), label, fill=color, font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, "JPEG", quality=92)
    return output_path
