import pytest

from src.production_policy import (
    COMMERCE_WHITE_BACKGROUND,
    CONTEXTUAL_SCENE_BACKGROUND,
    PURE_WHITE_HEX,
    ProductionPolicyError,
    assert_contextual_composition_allowed,
    resolve_production_image_policy,
)


def test_refined_is_commerce_primary_with_required_pure_white_background():
    policy = resolve_production_image_policy("refined")
    assert policy.asset_role == "commerce-primary"
    assert policy.background_policy == COMMERCE_WHITE_BACKGROUND
    assert policy.required_background == PURE_WHITE_HEX
    assert policy.contextual_composition_allowed is False


@pytest.mark.parametrize("output_type", ["lifestyle", "in-use"])
def test_contextual_outputs_keep_scene_background_policy(output_type):
    policy = resolve_production_image_policy(output_type)
    assert policy.asset_role == "contextual-editorial"
    assert policy.background_policy == CONTEXTUAL_SCENE_BACKGROUND
    assert policy.required_background is None
    assert policy.contextual_composition_allowed is True


def test_refined_fails_closed_if_routed_to_contextual_compositor():
    with pytest.raises(ProductionPolicyError, match="commerce-white-background"):
        assert_contextual_composition_allowed("refined")


def test_lifestyle_is_allowed_into_contextual_compositor():
    policy = assert_contextual_composition_allowed("lifestyle")
    assert policy.contextual_composition_allowed is True


def test_unknown_output_type_is_rejected():
    with pytest.raises(ProductionPolicyError):
        resolve_production_image_policy("hero")
