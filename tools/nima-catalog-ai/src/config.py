"""Configuration loading: env vars first, CLI flags override. Never logs the API key."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is a listed dependency
    load_dotenv = None

TOOL_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MAX_ATTEMPTS = 2
ABSOLUTE_MAX_ATTEMPTS = 3
DEFAULT_MAX_COST_USD = 5.0

# Verified against developers.openai.com/api/docs/models and independent web search on
# 2026-08-06 — do not assume older names (gpt-4o, gpt-image-1) without re-checking.
# gpt-5.6-sol: flagship reasoning+vision model, used for analysis and fidelity review
# (both need careful multi-image comparison, so the flagship tier is worth the cost here).
# gpt-image-2: current image generation/edit model (successor to gpt-image-1, April 2026).
TEXT_MODEL = "gpt-5.6-sol"
IMAGE_MODEL = "gpt-image-2"

VALID_OUTPUT_TYPES = ("refined", "lifestyle", "in-use")


class ConfigError(Exception):
    """Raised for any configuration problem; message is always safe to print."""


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number, got: {raw!r}") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got: {raw!r}") from exc


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


@dataclass
class Config:
    openai_api_key: str
    max_attempts: int
    max_cost_usd: float
    dry_run: bool
    text_model: str = TEXT_MODEL
    image_model: str = IMAGE_MODEL

    def redacted(self) -> dict:
        """Safe-to-log view of this config — the key is never included, not even partially."""
        return {
            "max_attempts": self.max_attempts,
            "max_cost_usd": self.max_cost_usd,
            "dry_run": self.dry_run,
            "text_model": self.text_model,
            "image_model": self.image_model,
        }


def load_config(
    *,
    max_attempts_flag: int | None = None,
    max_cost_usd_flag: float | None = None,
    dry_run_flag: bool = False,
    env_file: Path | None = None,
) -> Config:
    if load_dotenv is not None:
        load_dotenv(dotenv_path=env_file or (TOOL_ROOT / ".env"))

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "OPENAI_API_KEY is not set. Export it in your shell or add it to "
            f"{TOOL_ROOT / '.env'} (see .env.example). This tool refuses to run without it."
        )

    max_attempts = max_attempts_flag if max_attempts_flag is not None else _env_int(
        "NIMA_AI_MAX_ATTEMPTS", DEFAULT_MAX_ATTEMPTS
    )
    if max_attempts < 1 or max_attempts > ABSOLUTE_MAX_ATTEMPTS:
        raise ConfigError(
            f"max_attempts must be between 1 and {ABSOLUTE_MAX_ATTEMPTS}, got {max_attempts}"
        )

    max_cost_usd = max_cost_usd_flag if max_cost_usd_flag is not None else _env_float(
        "NIMA_AI_MAX_COST_USD", DEFAULT_MAX_COST_USD
    )
    if max_cost_usd <= 0:
        raise ConfigError(f"max_cost_usd must be positive, got {max_cost_usd}")

    dry_run = dry_run_flag or _env_bool("NIMA_AI_DRY_RUN", False)

    return Config(
        openai_api_key=api_key,
        max_attempts=max_attempts,
        max_cost_usd=max_cost_usd,
        dry_run=dry_run,
    )
