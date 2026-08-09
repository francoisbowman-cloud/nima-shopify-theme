"""Budget tracking and cost estimation.

OpenAI's images/generations and images/edits responses do not return a direct
dollar cost (see FASE 5 of the spec) — only base64 image data, and sometimes a
token usage object. This module estimates cost from a configurable price
table instead of inventing precision the API doesn't provide.

PRICING TABLE — estimate, not official confirmation
-----------------------------------------------------
Source: third-party aggregation (unifically.com/blogs/gpt-image-2, accessed
2026-08-06) citing OpenAI's per-resolution rates for gpt-image-2. OpenAI's own
pricing page (openai.com/api/pricing) returned HTTP 403 to automated fetch at
the time this was written and could not be read directly. TREAT THESE NUMBERS
AS UNCONFIRMED — re-verify against openai.com/api/pricing before relying on
this for real budget decisions, and update `PRICE_SOURCE_DATE` when you do.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PRICE_SOURCE = "unifically.com/blogs/gpt-image-2 (third-party, UNCONFIRMED against openai.com/api/pricing)"
PRICE_SOURCE_DATE = "2026-08-06"

# USD per generated image, by requested resolution tier.
IMAGE_PRICE_USD_BY_RESOLUTION = {
    "1024x1024": 0.03,  # "1K"
    "1536x1024": 0.03,
    "1024x1536": 0.03,
    "2048x2048": 0.05,  # "2K"
    "3840x2160": 0.06,  # "4K"
}
DEFAULT_IMAGE_PRICE_USD = 0.03


def estimate_image_cost_usd(size: str) -> float:
    return IMAGE_PRICE_USD_BY_RESOLUTION.get(size, DEFAULT_IMAGE_PRICE_USD)


@dataclass
class CallRecord:
    output_type: str
    attempt: int
    model: str
    parameters: dict
    request_id: str | None
    date: str
    duration_seconds: float
    usage: dict | None
    estimated_cost_usd: float
    succeeded: bool


@dataclass
class CostTracker:
    max_cost_usd: float
    calls: list[CallRecord] = field(default_factory=list)
    stop_reason: str | None = None

    @property
    def total_estimated_cost_usd(self) -> float:
        return round(sum(c.estimated_cost_usd for c in self.calls if c.succeeded), 6)

    @property
    def remaining_budget_usd(self) -> float:
        return round(self.max_cost_usd - self.total_estimated_cost_usd, 6)

    def can_afford(self, estimated_cost_usd: float) -> bool:
        return (self.total_estimated_cost_usd + estimated_cost_usd) <= self.max_cost_usd

    def record(self, call: CallRecord) -> None:
        self.calls.append(call)

    def stop(self, reason: str) -> None:
        self.stop_reason = reason

    def to_report(self, *, model: str, budget_available_usd: float) -> dict:
        failed = [c for c in self.calls if not c.succeeded]
        succeeded = [c for c in self.calls if c.succeeded]
        return {
            "calls_made": len(self.calls),
            "calls_failed": len(failed),
            "model": model,
            "price_source": PRICE_SOURCE,
            "price_source_date": PRICE_SOURCE_DATE,
            "is_estimate": True,
            "usage_reported": [c.usage for c in succeeded if c.usage],
            "estimated_cost_per_call_usd": [c.estimated_cost_usd for c in succeeded],
            "total_estimated_cost_usd": self.total_estimated_cost_usd,
            "budget_available_usd": budget_available_usd,
            "stop_reason": self.stop_reason,
        }
