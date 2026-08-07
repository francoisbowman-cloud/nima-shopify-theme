"""v0.2 Block 3 — scene-spec.json and the interaction model.

Separates "lifestyle" (product present, no contact) from "in-use" (contact
with a person or animal) via an explicit interaction_level, so a lifestyle
scene can never silently become an in-use scene through a permissive prompt.
v0.2's compositor only produces interaction_level 0 scenes — levels 1-3 are
named here so the schema and gate logic don't need to change when in-use
composition is added later, but nothing in this module or the pipeline can
currently produce or approve them.
"""

from __future__ import annotations

from pathlib import Path

from . import file_utils

SCHEMA_NAME = "scene-spec.schema.json"

# 0 = passive presence (product sits in the scene, nothing touches it)
# 1 = proximity / contextual interaction (near a pet/person, not touching)
# 2 = active use (pet/person actively using the product)
# 3 = close manipulation (hands directly manipulating the product)
INTERACTION_LEVELS = (0, 1, 2, 3)

_SCENE_TYPES = ("lifestyle", "in-use")

# v0.2's compositor is a lifestyle-only pipeline — this is the ceiling until
# a future version adds controlled in-use composition.
MAX_SUPPORTED_INTERACTION_LEVEL = 0


class SceneSpecError(ValueError):
    pass


def build_scene_spec(
    *,
    scene_type: str = "lifestyle",
    interaction_level: int = 0,
    product_contact_allowed: bool | None = None,
    animal_contact_allowed: bool | None = None,
    human_contact_allowed: bool | None = None,
) -> dict:
    if scene_type not in _SCENE_TYPES:
        raise SceneSpecError(f"Unknown scene_type: {scene_type!r} (valid: {_SCENE_TYPES})")
    if interaction_level not in INTERACTION_LEVELS:
        raise SceneSpecError(f"interaction_level must be one of {INTERACTION_LEVELS}, got {interaction_level}")

    # A lifestyle scene is, by definition, passive presence — level 0. Any
    # higher level requires scene_type="in-use". This is the rule the prompt
    # explicitly calls out: never let a lifestyle scene be approved with
    # active use.
    if scene_type == "lifestyle" and interaction_level != 0:
        raise SceneSpecError(
            f"scene_type='lifestyle' requires interaction_level=0, got {interaction_level} "
            "— use scene_type='in-use' for any contact/interaction scene."
        )
    if scene_type == "in-use" and interaction_level == 0:
        raise SceneSpecError("scene_type='in-use' requires interaction_level >= 1")

    default_contact = scene_type == "in-use"
    spec = {
        "scene_type": scene_type,
        "interaction_level": interaction_level,
        "product_contact_allowed": product_contact_allowed if product_contact_allowed is not None else default_contact,
        "animal_contact_allowed": animal_contact_allowed if animal_contact_allowed is not None else default_contact,
        "human_contact_allowed": human_contact_allowed if human_contact_allowed is not None else default_contact,
    }

    if scene_type == "lifestyle" and any(
        [spec["product_contact_allowed"], spec["animal_contact_allowed"], spec["human_contact_allowed"]]
    ):
        raise SceneSpecError(
            "scene_type='lifestyle' cannot have any *_contact_allowed=True — "
            "that combination describes an in-use scene."
        )

    return spec


def is_lifestyle_compatible(spec: dict) -> bool:
    """Composition Gate's scene check (Block 7 calls this directly): a
    lifestyle scene is only valid if it is genuinely passive on every axis."""
    return (
        spec["scene_type"] == "lifestyle"
        and spec["interaction_level"] == 0
        and not spec["product_contact_allowed"]
        and not spec["animal_contact_allowed"]
        and not spec["human_contact_allowed"]
    )


def is_supported_by_v02_compositor(spec: dict) -> bool:
    return spec["scene_type"] == "lifestyle" and spec["interaction_level"] <= MAX_SUPPORTED_INTERACTION_LEVEL


def save_scene_spec(spec: dict, path: Path, *, schemas_dir: Path | None = None) -> None:
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, SCHEMA_NAME)
        file_utils.validate_against_schema(spec, schema)
    file_utils.write_json(path, spec)
