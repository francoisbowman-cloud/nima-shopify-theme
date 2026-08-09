import argparse
from pathlib import Path

import pytest

from src import cli
from src.config import Config


def _args(**overrides):
    defaults = dict(
        input=None,
        outputs="refined,lifestyle,in-use",
        dry_run=False,
        max_attempts=None,
        max_cost_usd=None,
        force=False,
        yes=False,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _config(**overrides):
    defaults = dict(openai_api_key="sk-test", max_attempts=2, max_cost_usd=5.0, dry_run=False)
    defaults.update(overrides)
    return Config(**defaults)


def test_dry_run_never_calls_image_generation(product_dir, fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    args = _args(input=str(product_dir), dry_run=True)
    result = cli.run_pipeline(args, client=fake_client, config=_config(dry_run=True))

    assert fake_client.edit_calls == []
    assert result["outputs_state"]["refined"]["state"] == "pending"
    assert result["outputs_state"]["lifestyle"]["state"] == "pending"
    assert result["outputs_state"]["in-use"]["state"] == "omitted"  # not eligible per DEFAULT_ANALYSIS


def test_real_run_requires_yes_flag(product_dir, fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    args = _args(input=str(product_dir), dry_run=False, yes=False)
    with pytest.raises(Exception, match="--yes"):
        cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False))
    assert fake_client.edit_calls == []


def test_real_run_generates_and_records_outcomes(product_dir, fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    fake_client.fidelity_decision = "approved_candidate"
    args = _args(input=str(product_dir), outputs="refined,lifestyle", dry_run=False, yes=True)
    result = cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False))

    assert len(fake_client.edit_calls) == 2  # refined + lifestyle, one attempt each
    assert result["outputs_state"]["refined"]["state"] == "approved_candidate"
    assert result["outputs_state"]["lifestyle"]["state"] == "approved_candidate"


def test_idempotent_second_run_reuses_approved_output(product_dir, fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    fake_client.fidelity_decision = "approved_candidate"
    args = _args(input=str(product_dir), outputs="refined", dry_run=False, yes=True)

    cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False))
    assert len(fake_client.edit_calls) == 1

    cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False))
    assert len(fake_client.edit_calls) == 1  # unchanged — reused, not regenerated


def test_force_flag_bypasses_idempotency(product_dir, fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    fake_client.fidelity_decision = "approved_candidate"
    args = _args(input=str(product_dir), outputs="refined", dry_run=False, yes=True)
    cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False))
    assert len(fake_client.edit_calls) == 1

    args_forced = _args(input=str(product_dir), outputs="refined", dry_run=False, yes=True, force=True)
    cli.run_pipeline(args_forced, client=fake_client, config=_config(dry_run=False))
    assert len(fake_client.edit_calls) == 2


def test_attempt_limit_never_exceeds_configured_max(product_dir, fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    fake_client.fidelity_decision = "reject"
    args = _args(input=str(product_dir), outputs="refined", dry_run=False, yes=True, max_attempts=2)
    result = cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False, max_attempts=2))

    assert len(fake_client.edit_calls) == 2
    assert result["outputs_state"]["refined"]["state"] == "rejected"
    assert len(result["outputs_state"]["refined"]["attempts"]) == 2


def test_in_use_omitted_without_extra_api_call(product_dir, fake_client, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    args = _args(input=str(product_dir), outputs="in-use", dry_run=False, yes=True)
    result = cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False))

    assert result["outputs_state"]["in-use"]["state"] == "omitted"
    assert fake_client.edit_calls == []


def test_review_readme_lists_only_this_runs_requested_outputs(product_dir, tmp_path, monkeypatch):
    from tests.conftest import FakeOpenAIClient

    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    client = FakeOpenAIClient(analysis_overrides={"eligible_outputs": {"refined": True, "lifestyle": True, "in_use": True}})

    # First run (dry-run) caches a generation-plan.json with all three output types.
    args_dry = _args(input=str(product_dir), outputs="refined,lifestyle,in-use", dry_run=True)
    cli.run_pipeline(args_dry, client=client, config=_config(dry_run=True))

    # Second run only requests two of them — the cached plan still has all three.
    client.fidelity_decision = "approved_candidate"
    args_real = _args(input=str(product_dir), outputs="refined,lifestyle", dry_run=False, yes=True)
    result = cli.run_pipeline(args_real, client=client, config=_config(dry_run=False))

    readme = (Path(result["package_dir"]) / "README.md").read_text(encoding="utf-8")
    assert "Outputs requested this run: ['refined', 'lifestyle']" in readme
    assert "in-use" not in readme.split("Outputs requested this run:")[1].split("\n")[0]


def test_cache_invalidated_when_overrides_change_but_not_analysis(product_dir, tmp_path, monkeypatch):
    import json

    monkeypatch.setattr(cli, "OUTPUT_ROOT", tmp_path / "output")
    from tests.conftest import FakeOpenAIClient

    client = FakeOpenAIClient(fidelity_decision="approved_candidate")
    args = _args(input=str(product_dir), outputs="refined", dry_run=False, yes=True)

    cli.run_pipeline(args, client=client, config=_config(dry_run=False))
    assert len(client.edit_calls) == 1
    assert client.structured_calls.count("product_analysis") == 1

    # Same input, same config — reused, no new image call.
    cli.run_pipeline(args, client=client, config=_config(dry_run=False))
    assert len(client.edit_calls) == 1
    assert client.structured_calls.count("product_analysis") == 1

    # Adding a product-overrides.json changes the plan/output cache key but
    # not the analysis one — analysis should stay cached, output should not.
    (product_dir / "product-overrides.json").write_text(
        json.dumps({"wordmark_exact_text": "Moki Found"}), encoding="utf-8"
    )
    cli.run_pipeline(args, client=client, config=_config(dry_run=False))
    assert len(client.edit_calls) == 2  # regenerated
    assert client.structured_calls.count("product_analysis") == 1  # analysis NOT re-run


def test_all_outputs_confined_to_output_root(product_dir, fake_client, tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    monkeypatch.setattr(cli, "OUTPUT_ROOT", output_root)
    fake_client.fidelity_decision = "approved_candidate"
    args = _args(input=str(product_dir), outputs="refined", dry_run=False, yes=True)
    cli.run_pipeline(args, client=fake_client, config=_config(dry_run=False))

    for path in output_root.rglob("*"):
        if path.is_file():
            assert output_root.resolve() in path.resolve().parents
