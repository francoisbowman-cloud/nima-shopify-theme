"""v0.2 Block 8 — visual debug outputs.

Every composition run can emit a numbered package of intermediate images
plus a single labeled contact sheet, so a person can judge what the system
did without reading any code or JSON. This is treated as a first-class
deliverable, not an afterthought: see the v0.2 prompt's "MUY IMPORTANTE —
RESULTADO VISUAL".
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

THUMB_SIZE = (300, 300)
LABEL_HEIGHT = 44


def _label_font():
    return ImageFont.load_default()


def draw_bbox_preview(base: Image.Image, bbox: tuple[int, int, int, int], *, color=(220, 40, 40)) -> Image.Image:
    preview = base.convert("RGB").copy()
    draw = ImageDraw.Draw(preview)
    draw.rectangle(bbox, outline=color, width=max(2, base.width // 300))
    return preview


def build_step_outputs(
    *,
    output_dir: Path,
    source: Image.Image,
    mask: Image.Image,
    cutout: Image.Image,
    background: Image.Image,
    placement_spec: dict,
    shadow_preview: Image.Image,
    final_composite: Image.Image,
    gate_report: dict,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    def _save(name: str, img: Image.Image, fmt: str) -> None:
        path = output_dir / name
        if fmt == "JPEG":
            img.convert("RGB").save(path, fmt, quality=90)
        else:
            img.save(path, fmt)
        paths[name] = path

    _save("01-source.jpg", source, "JPEG")
    _save("02-mask.png", mask, "PNG")
    _save("03-cutout.png", cutout, "PNG")
    _save("04-background.jpg", background, "JPEG")

    bbox = placement_spec["product"]["final_bbox"]
    bbox_tuple = (bbox["left"], bbox["top"], bbox["right"], bbox["bottom"])
    placement_preview = draw_bbox_preview(background, bbox_tuple)
    _save("05-placement-preview.png", placement_preview, "PNG")

    shadow_on_white = Image.new("RGB", shadow_preview.size, "white")
    shadow_on_white.paste(shadow_preview, (0, 0), shadow_preview)
    _save("06-shadow-preview.png", shadow_on_white, "PNG")

    _save("07-final-composite.png", final_composite, "PNG")

    gate_color = (40, 180, 80) if gate_report["passed"] else (220, 40, 40)
    gate_overlay = draw_bbox_preview(final_composite, bbox_tuple, color=gate_color)
    draw = ImageDraw.Draw(gate_overlay)
    label = f"COMPOSITION GATE: {gate_report['status'].upper()}"
    draw.rectangle((0, 0, gate_overlay.width, 28), fill=gate_color)
    draw.text((8, 6), label, fill="white", font=_label_font())
    _save("08-gate-overlay.png", gate_overlay, "PNG")

    return paths


def thumb(img: Image.Image, size: tuple[int, int] = THUMB_SIZE) -> Image.Image:
    """Public since v0.3 — reused by benchmark.py for the v0.2/v0.3 comparison sheet."""
    if img.mode == "RGBA":
        # Composite onto white first — a bare .convert("RGB") on RGBA just
        # drops the alpha channel and lets whatever RGB values sit under a
        # transparent pixel show through (e.g. a segmented-out background
        # region reappearing in a cutout's thumbnail even though it was
        # correctly made transparent).
        opaque = Image.new("RGB", img.size, "white")
        opaque.paste(img, (0, 0), img)
        img = opaque
    else:
        img = img.convert("RGB").copy()
    img.thumbnail(size)
    canvas = Image.new("RGB", size, "white")
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    canvas.paste(img, offset)
    return canvas


_thumb = thumb  # internal alias, kept so existing call sites in this module read unchanged


def build_composition_contact_sheet(
    *,
    source: Image.Image,
    cutout: Image.Image,
    background: Image.Image,
    placement_preview: Image.Image,
    final_composite: Image.Image,
    gate_report: dict,
    output_path: Path,
) -> Path:
    cells = [
        ("SOURCE", source),
        ("CUTOUT", cutout),
        ("BACKGROUND", background),
        ("PLACEMENT", placement_preview),
        ("FINAL", final_composite),
        (f"GATE RESULT: {gate_report['status'].upper()}", final_composite),
    ]
    columns = 3
    rows = (len(cells) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * THUMB_SIZE[0], rows * (THUMB_SIZE[1] + LABEL_HEIGHT)), "white")
    draw = ImageDraw.Draw(sheet)
    font = _label_font()

    for index, (label, img) in enumerate(cells):
        col, row = index % columns, index // columns
        x, y = col * THUMB_SIZE[0], row * (THUMB_SIZE[1] + LABEL_HEIGHT)
        sheet.paste(_thumb(img), (x, y))
        text_color = "black"
        if label.startswith("GATE RESULT"):
            text_color = "green" if gate_report["passed"] else "red"
        draw.text((x + 6, y + THUMB_SIZE[1] + 8), label, fill=text_color, font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, "JPEG", quality=90)
    return output_path
