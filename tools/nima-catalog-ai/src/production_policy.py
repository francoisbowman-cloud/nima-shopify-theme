"""Production Image Readiness policy for Nima Catalog AI v0.3.1.

This module is deliberately small and deterministic. It separates commerce
assets from contextual/editorial assets so the pipeline cannot silently turn a
catalog-primary image into a lifestyle composition.

Policy established for v0.3.1:
- `refined` is the commerce-primary/catalog packshot and MUST resolve to a
  consistent pure-white background (#FFFFFF).
- `lifestyle` and `in-use` are contextual/editorial assets and MAY use Scene
  Intelligence plus generated environments.
"""

from __future__ import annotations

from dataclasses import dataclass


COMMERCE_WHITE_BACKGROUND = "commerce-white-background"
CONTEXTUAL_SCENE_BACKGROUND = "contextual-scene-background"
PURE_WHITE_HEX = "#FFFFFF"

_COMMERCE_PRIMARY_TYPES = {"refined"}
_CONTEXTUAL_TYPES = {"lifestyle", "in-use"}


class ProductionPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class ProductionImagePolicy:
    output_type: str
    asset_role: str
    background_policy: str
    required_background: str | None
    contextual_composition_allowed: bool


def resolve_production_image_policy(output_type: str) -> ProductionImagePolicy:
    """Return the immutable production policy for one output type."""
    if output_type in _COMMERCE_PRIMARY_TYPES:
        return ProductionImagePolicy(
            output_type=output_type,
            asset_role="commerce-primary",
            background_policy=COMMERCE_WHITE_BACKGROUND,
            required_background=PURE_WHITE_HEX,
            contextual_composition_allowed=False,
        )
    if output_type in _CONTEXTUAL_TYPES:
        return ProductionImagePolicy(
            output_type=output_type,
            asset_role="contextual-editorial",
            background_policy=CONTEXTUAL_SCENE_BACKGROUND,
            required_background=None,
            contextual_composition_allowed=True,
        )
    raise ProductionPolicyError(f"Unknown output type for production image policy: {output_type}")


def assert_contextual_composition_allowed(output_type: str) -> ProductionImagePolicy:
    """Fail closed if a commerce-primary asset is routed into Scene Intelligence.

    `composition_pipeline_v03` creates contextual environments. A refined
    catalog-primary image must never enter that path because doing so would
    violate commerce-white-background even if every downstream gate passed.
    """
    policy = resolve_production_image_policy(output_type)
    if not policy.contextual_composition_allowed:
        raise ProductionPolicyError(
            f"Output type '{output_type}' is {policy.asset_role} and requires "
            f"{policy.background_policy} ({policy.required_background}); "
            "contextual Scene Intelligence composition is not allowed."
        )
    return policy
