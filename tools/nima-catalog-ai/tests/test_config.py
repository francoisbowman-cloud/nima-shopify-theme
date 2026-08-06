import pytest

from src.config import ABSOLUTE_MAX_ATTEMPTS, ConfigError, load_config


def test_missing_api_key_raises_clear_error(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    missing_env_file = tmp_path / "does-not-exist.env"
    with pytest.raises(ConfigError, match="OPENAI_API_KEY is not set"):
        load_config(env_file=missing_env_file)


def test_valid_config_parses_env_and_flags(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    monkeypatch.setenv("NIMA_AI_MAX_ATTEMPTS", "2")
    monkeypatch.setenv("NIMA_AI_MAX_COST_USD", "3.5")
    cfg = load_config(env_file=tmp_path / "missing.env")
    assert cfg.max_attempts == 2
    assert cfg.max_cost_usd == 3.5
    assert cfg.dry_run is False


def test_max_attempts_cannot_exceed_absolute_cap(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    with pytest.raises(ConfigError):
        load_config(max_attempts_flag=ABSOLUTE_MAX_ATTEMPTS + 1, env_file=tmp_path / "missing.env")


def test_config_redacted_never_includes_key(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-super-secret-value")
    cfg = load_config(env_file=tmp_path / "missing.env")
    dumped = str(cfg.redacted())
    assert "sk-super-secret-value" not in dumped
    assert "openai_api_key" not in cfg.redacted()
