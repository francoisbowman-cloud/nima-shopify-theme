import json

import pytest

from src import file_utils


def test_read_manifest_json(tmp_path):
    manifest = {"handle": "x", "title": "X"}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert file_utils.read_json(path) == manifest


def test_schema_validation_rejects_invalid_data():
    schema = {
        "type": "object",
        "required": ["handle"],
        "properties": {"handle": {"type": "string"}},
    }
    with pytest.raises(Exception):
        file_utils.validate_against_schema({}, schema)
    file_utils.validate_against_schema({"handle": "ok"}, schema)  # should not raise


def test_ensure_within_blocks_path_traversal(tmp_path):
    base = tmp_path / "output"
    base.mkdir()
    outside = tmp_path / "somewhere-else" / "leak.json"
    with pytest.raises(ValueError):
        file_utils.ensure_within(base, outside)

    inside = base / "sub" / "file.json"
    assert file_utils.ensure_within(base, inside) == inside.resolve()


def test_list_original_images_sorted(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    for name in ["02-original.jpg", "01-original.jpg", "readme.txt"]:
        (original / name).write_bytes(b"x")
    images = file_utils.list_original_images(tmp_path)
    assert [p.name for p in images] == ["01-original.jpg", "02-original.jpg"]
