from src import demo_v02


def test_run_demo_produces_passing_summary_and_contact_sheet(tmp_path):
    out_dir = tmp_path / "demo-output"
    summary = demo_v02.run_demo(out_dir)

    assert summary["products"] == 1
    assert summary["rejected"] == 0
    assert (out_dir / "catalog-composition-summary.json").exists()

    product_dir = out_dir / "demo-waterproof-pet-feeding-mat"
    assert (product_dir / "composite-base.png").exists()
    assert (product_dir / "composition-contact-sheet.jpg").exists()
    assert (product_dir / "composition-gate-report.json").exists()


def test_main_runs_end_to_end(tmp_path, capsys):
    out_dir = tmp_path / "demo-output"
    exit_code = demo_v02.main(["--out", str(out_dir)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Demo complete" in captured.out
