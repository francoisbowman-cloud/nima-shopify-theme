"""Nima Catalog AI v0.3.1 contextual composition entrypoint.

This wrapper keeps v0.3 frozen and adds one production-readiness invariant:
commerce-primary/refined assets cannot enter the Scene Intelligence compositor.
Lifestyle and in-use remain eligible for contextual composition.
"""

from __future__ import annotations

from .composition_pipeline_v03 import CompositionRunResultV03, run_composition_v03_for_image
from .production_policy import assert_contextual_composition_allowed


def run_composition_v031_for_image(**kwargs) -> CompositionRunResultV03:
    output_type = kwargs.get("output_type")
    if not output_type:
        raise ValueError("run_composition_v031_for_image requires output_type")
    assert_contextual_composition_allowed(output_type)
    return run_composition_v03_for_image(**kwargs)
