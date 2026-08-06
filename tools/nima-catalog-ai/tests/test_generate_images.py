from src import cost_control, generate_images


def test_cost_limit_stops_before_call(product_dir, fake_client):
    tracker = cost_control.CostTracker(max_cost_usd=0.01)  # below any real image price
    plan_entry = {
        "type": "refined",
        "primary_reference": "01-original.jpg",
        "secondary_references": [],
        "goal": "g",
        "composition": "c",
        "background": "b",
        "lighting": "l",
        "aspect_ratio": "1:1",
        "mandatory_rules": ["Preserve shape"],
        "risks": [],
        "rejection_criteria": [],
    }
    record, path = generate_images.generate_attempt(
        plan_entry=plan_entry,
        handle="test-product",
        input_dir=product_dir,
        generated_dir=product_dir / "generated",
        client=fake_client,
        model="gpt-image-2",
        attempt_number=1,
        cost_tracker=tracker,
    )
    assert record is None
    assert path is None
    assert tracker.stop_reason is not None
    assert fake_client.edit_calls == []


def test_generate_attempt_saves_file_and_records_cost(product_dir, fake_client):
    tracker = cost_control.CostTracker(max_cost_usd=5.0)
    plan_entry = {
        "type": "refined",
        "primary_reference": "01-original.jpg",
        "secondary_references": ["02-original.jpg"],
        "goal": "g",
        "composition": "c",
        "background": "b",
        "lighting": "l",
        "aspect_ratio": "1:1",
        "mandatory_rules": ["Preserve shape"],
        "risks": [],
        "rejection_criteria": [],
    }
    generated_dir = product_dir / "generated"
    record, path = generate_images.generate_attempt(
        plan_entry=plan_entry,
        handle="test-product",
        input_dir=product_dir,
        generated_dir=generated_dir,
        client=fake_client,
        model="gpt-image-2",
        attempt_number=1,
        cost_tracker=tracker,
    )
    assert record is not None
    assert path.exists()
    assert path.name == "test-product__refined__v1.png"
    assert tracker.total_estimated_cost_usd > 0
    assert len(fake_client.edit_calls) == 1
    assert record["diagnostics"] == {"strategy": "full-generate"}
    assert fake_client.edit_calls[0]["mask"] is None


def test_next_version_increments(product_dir):
    generated_dir = product_dir / "generated"
    generated_dir.mkdir()
    (generated_dir / "test-product__refined__v1.png").write_bytes(b"x")
    assert generate_images.next_version(generated_dir, "test-product", "refined") == 2


def test_product_preserving_uses_single_masked_reference(product_dir, fake_client):
    from PIL import Image

    def fake_mask_builder(image_path):
        # Match the real image's size (conftest's synthetic originals are 64x64)
        # with a smaller centered "product" region, so the crop step has real
        # background margin to work with — like an actual studio photo.
        w, h = Image.open(image_path).size
        mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for y in range(h // 4, 3 * h // 4):
            for x in range(w // 4, 3 * w // 4):
                mask.putpixel((x, y), (0, 0, 0, 255))
        return mask

    tracker = cost_control.CostTracker(max_cost_usd=5.0)
    plan_entry = {
        "type": "refined",
        "primary_reference": "01-original.jpg",
        "secondary_references": [],
        "goal": "g",
        "composition": "c",
        "background": "b",
        "lighting": "l",
        "aspect_ratio": "1:1",
        "mandatory_rules": ["Preserve shape"],
        "risks": [],
        "rejection_criteria": [],
        "strategy": "product-preserving",
        "mask_strategy": "background-only",
        "framing_rules": {
            "target_occupancy_pct_min": 75,
            "target_occupancy_pct_max": 88,
            "margins": "balanced",
            "centering": "optical",
            "card_aspect_ratio": "1:1",
        },
    }
    record, path = generate_images.generate_attempt(
        plan_entry=plan_entry,
        handle="test-product",
        input_dir=product_dir,
        generated_dir=product_dir / "generated",
        client=fake_client,
        model="gpt-image-2",
        attempt_number=1,
        cost_tracker=tracker,
        mask_builder=fake_mask_builder,
    )
    assert record is not None
    assert path is not None
    assert len(fake_client.edit_calls) == 1
    call = fake_client.edit_calls[0]
    assert len(call["images"]) == 1  # single reference only — mask requires it
    assert call["images"][0] != "01-original.jpg"  # cropped copy, not the original file
    assert call["mask"] is not None
    assert record["diagnostics"]["strategy"] == "product-preserving"
    assert "framing" in record["diagnostics"]
    assert record["diagnostics"]["framing"]["occupancy_before_pct"] == 25.0  # 32x32 product in 64x64 frame
    mask_files = list((product_dir / "masks").glob("*.png"))
    assert len(mask_files) == 1
    crop_files = list((product_dir / "crops").glob("*.jpg"))
    assert len(crop_files) == 1


def test_mask_builder_failure_falls_back_to_unmasked_instead_of_crashing(product_dir, fake_client):
    def broken_mask_builder(image_path):
        raise RuntimeError("simulated: no distinct product region found")

    tracker = cost_control.CostTracker(max_cost_usd=5.0)
    plan_entry = {
        "type": "refined",
        "primary_reference": "01-original.jpg",
        "secondary_references": [],
        "goal": "g",
        "composition": "c",
        "background": "b",
        "lighting": "l",
        "aspect_ratio": "1:1",
        "mandatory_rules": ["Preserve shape"],
        "risks": [],
        "rejection_criteria": [],
        "strategy": "product-preserving",
        "mask_strategy": "background-only",
        "framing_rules": {
            "target_occupancy_pct_min": 75,
            "target_occupancy_pct_max": 88,
            "margins": "balanced",
            "centering": "optical",
            "card_aspect_ratio": "1:1",
        },
    }
    record, path = generate_images.generate_attempt(
        plan_entry=plan_entry,
        handle="test-product",
        input_dir=product_dir,
        generated_dir=product_dir / "generated",
        client=fake_client,
        model="gpt-image-2",
        attempt_number=1,
        cost_tracker=tracker,
        mask_builder=broken_mask_builder,
    )
    assert record is not None  # did not crash / propagate the exception
    assert path is not None
    assert "mask_error" in record["diagnostics"]
    call = fake_client.edit_calls[0]
    assert call["mask"] is None  # fell back to an unmasked call
