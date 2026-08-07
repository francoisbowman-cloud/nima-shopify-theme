from pathlib import Path

from PIL import Image

from src import visual_debug


def test_build_composition_contact_sheet_creates_file(tmp_path):
    img = Image.new("RGB", (100, 100), (200, 100, 50))
    gate_report = {"passed": True, "status": "pass"}
    out = tmp_path / "composition-contact-sheet.jpg"
    result = visual_debug.build_composition_contact_sheet(
        source=img,
        cutout=img,
        background=img,
        placement_preview=img,
        final_composite=img,
        gate_report=gate_report,
        output_path=out,
    )
    assert result == out
    assert out.exists()


def test_draw_bbox_preview_returns_rgb_image_same_size():
    img = Image.new("RGB", (100, 80), (255, 255, 255))
    preview = visual_debug.draw_bbox_preview(img, (10, 10, 50, 50))
    assert preview.size == (100, 80)
    assert preview.mode == "RGB"


def test_build_step_outputs_writes_all_eight_files(tmp_path):
    img = Image.new("RGB", (100, 100), (200, 100, 50))
    cutout = Image.new("RGBA", (100, 100), (200, 100, 50, 255))
    placement_spec = {
        "canvas": {"width": 100, "height": 100},
        "product": {"final_bbox": {"left": 10, "top": 10, "right": 60, "bottom": 60}},
    }
    gate_report = {"passed": False, "status": "fail"}
    paths = visual_debug.build_step_outputs(
        output_dir=tmp_path / "visual-debug",
        source=img,
        mask=cutout,
        cutout=cutout,
        background=img,
        placement_spec=placement_spec,
        shadow_preview=cutout,
        final_composite=img,
        gate_report=gate_report,
    )
    assert len(paths) == 8
    for path in paths.values():
        assert path.exists()
