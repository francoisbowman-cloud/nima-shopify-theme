from src import scene_intelligence, shadow, surface


def _surface_model(category="pet feeding mat"):
    intel = scene_intelligence.build_scene_intelligence(
        {"title": "x", "product_category": category, "critical_functional_features": [], "critical_visual_features": []}
    )
    return surface.build_surface_model(intel)


def test_flat_ground_gets_tighter_shadow_than_soft_ground():
    flat_params = shadow.build_surface_aware_shadow_params(_surface_model("pet feeding mat"))
    soft_params = shadow.build_surface_aware_shadow_params(_surface_model("dog bed"))
    assert flat_params.blur_radius < soft_params.blur_radius


def test_hanging_product_gets_non_ground_default():
    params = shadow.build_surface_aware_shadow_params(_surface_model("dog leash"))
    assert params == shadow._NON_GROUND_DEFAULT


def test_surface_aware_params_are_shadow_params_instance():
    params = shadow.build_surface_aware_shadow_params(_surface_model())
    assert isinstance(params, shadow.ShadowParams)
    assert params.enabled is True
