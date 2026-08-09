from src import demo_v03


def test_run_demo_v03_produces_passing_result(tmp_path):
    out_dir = tmp_path / "demo-output-v03"
    result = demo_v03.run_demo(out_dir)

    assert result.perspective_applied is True
    assert result.gate_report["status"] == "pass"
    assert result.contact_sheet_path.exists()
    assert result.comparison_path.exists()


def test_main_runs_end_to_end(tmp_path, capsys):
    out_dir = tmp_path / "demo-output-v03"
    exit_code = demo_v03.main(["--out", str(out_dir)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Demo v0.3 complete" in captured.out
