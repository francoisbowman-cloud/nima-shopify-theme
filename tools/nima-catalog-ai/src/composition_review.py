"""v0.2 Block 9 — review package extension for the protected-composition path.

A separate module rather than editing package_review.py in place: v0.1's
package assembly is frozen (see CLAUDE.md/the v0.2 prompt — the v0.1 branch
must not be touched), and lifestyle candidates built by the new compositor
need composition-specific fields (occupancy, clipping, interaction_level,
generation_strategy) that a refined/full-generate candidate never has.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils

GENERATION_STRATEGY_PROTECTED = "protected-product-composition"


def build_composition_entry(
    *,
    placement_spec: dict,
    scene_spec: dict,
    gate_report: dict,
) -> dict:
    return {
        "occupancy": placement_spec["product"]["final_occupancy"],
        "clipping": gate_report["geometry"]["checks"]["out_of_canvas"],
        "interaction_level": scene_spec["interaction_level"],
        "scale_status": "pass" if not gate_report["geometry"]["checks"]["scale_implausible"] else "fail",
        "placement_status": "pass" if gate_report["geometry"]["passed"] else "fail",
    }


def classify_generation_kind(*, scene_spec: dict, generation_strategy: str) -> str:
    """REFINED / LIFESTYLE COMPOSITE / IN-USE — the three buckets the review
    package must clearly distinguish, per the v0.2 prompt Block 9."""
    if scene_spec["scene_type"] == "in-use":
        return "IN-USE"
    if generation_strategy == GENERATION_STRATEGY_PROTECTED:
        return "LIFESTYLE COMPOSITE"
    return "REFINED"


def build_review_entry(
    *,
    handle: str,
    output_type: str,
    placement_spec: dict,
    scene_spec: dict,
    gate_report: dict,
    fidelity_report: dict | None = None,
    generation_strategy: str = GENERATION_STRATEGY_PROTECTED,
) -> dict:
    entry = {
        "handle": handle,
        "output_type": output_type,
        "generation_strategy": generation_strategy,
        "generation_kind": classify_generation_kind(scene_spec=scene_spec, generation_strategy=generation_strategy),
        "composition": build_composition_entry(placement_spec=placement_spec, scene_spec=scene_spec, gate_report=gate_report),
        "composition_gate": gate_report,
        "fidelity_report": fidelity_report,
    }
    return entry


def write_review_entry(entry: dict, path: Path) -> None:
    file_utils.write_json(path, entry)
