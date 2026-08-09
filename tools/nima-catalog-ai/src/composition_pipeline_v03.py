"""v0.3 — orchestrates Blocks 1-9 for one product image, fully offline.

    scene intelligence -> surface model -> segmentation -> edge refinement
    -> placement -> scene spec -> scene-aware background request -> background
    -> perspective match (if eligible) -> surface-aware shadow
    -> Composition Gate v0.3 -> visual debug -> review entry
    -> v0.2-vs-v0.3 benchmark comparison

Mirrors composition_pipeline.py's structure and safety contract exactly:
never calls a real API itself (only whatever `background_provider` does —
pass a FixtureBackgroundProvider for offline runs; OpenAIBackgroundProvider
still raises NotImplementedError by construction).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from . import background as background_mod
from . import benchmark as benchmark_mod
from . import composition_gates
from . import composition_pipeline as pipeline_v02
from . import composition_review
from . import compositor as compositor_mod
from . import edge_refinement
from . import file_utils
from . import perspective as perspective_mod
from . import placement as placement_mod
from . import scene as scene_mod
from . import scene_intelligence as scene_intel_mod
from . import segmentation as segmentation_mod
from . import shadow as shadow_mod
from . import surface as surface_mod
from . import visual_debug
from .background_provider import BackgroundProvider, FixtureBackgroundProvider


@dataclass
class CompositionRunResultV03:
    handle: str
    output_type: str
    scene_intelligence: dict
    surface_model: dict
    segmentation_metadata: dict
    edge_refinement_metadata: dict
    placement_spec: dict
    scene_spec: dict
    background_request: dict
    top_environment: str
    perspective_applied: bool
    gate_report: dict
    review_entry: dict
    output_dir: Path
    final_composite_path: Path
    contact_sheet_path: Path
    comparison_path: Path


def _compose_with_perspective(
    *,
    refined_cutout: Image.Image,
    background_image: Image.Image,
    placement_spec: dict,
    shadow_params: shadow_mod.ShadowParams,
) -> tuple[Image.Image, Image.Image, list, float]:
    canvas = placement_spec["canvas"]
    canvas_size = (canvas["width"], canvas["height"])
    bbox = placement_spec["product"]["final_bbox"]
    bbox_tuple = (bbox["left"], bbox["top"], bbox["right"], bbox["bottom"])

    dst_quad = perspective_mod.compute_ground_quad(bbox_tuple)
    warped_product = perspective_mod.apply_perspective_match(refined_cutout, dst_quad, canvas_size=canvas_size)

    if background_image.size != canvas_size:
        background_image = background_image.resize(canvas_size)

    shadow_layer = shadow_mod.build_shadow_layer(warped_product, canvas_size, params=shadow_params)

    composite = background_image.convert("RGBA")
    composite = Image.alpha_composite(composite, shadow_layer)
    composite = Image.alpha_composite(composite, warped_product)

    warped_left, warped_top, warped_right, warped_bottom = perspective_mod.warped_bbox(dst_quad)
    warped_area = max(0.0, warped_right - warped_left) * max(0.0, warped_bottom - warped_top)

    return composite.convert("RGB"), warped_product, dst_quad, warped_area


def run_composition_v03_for_image(
    *,
    handle: str,
    output_type: str,
    source_image_path: Path,
    analysis: dict,
    background_provider: BackgroundProvider,
    output_dir: Path,
    schemas_dir: Path | None = None,
    canvas_size: tuple[int, int] = (1536, 1536),
) -> CompositionRunResultV03:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Block 1 + 2
    scene_intel = scene_intel_mod.build_scene_intelligence(analysis, interaction_level=0)
    scene_intel_mod.save_scene_intelligence(scene_intel, output_dir / "scene-intelligence.json", schemas_dir=schemas_dir)
    surface_model = surface_mod.build_surface_model(scene_intel)
    surface_mod.save_surface_model(surface_model, output_dir / "surface-model.json", schemas_dir=schemas_dir)
    top_environment = scene_intel_mod.top_environment(scene_intel)

    # Block 1 (segmentation, reused from v0.2) + Block 4 (edge refinement)
    seg_result = segmentation_mod.segment_product(source_image_path)
    refined_cutout, refined_mask, edge_meta = edge_refinement.refine_edges(
        seg_result.cutout, seg_result.mask, source_image_path
    )
    segmentation_mod.save_segmentation(
        seg_result,
        cutout_path=output_dir / "product-cutout.png",
        mask_path=output_dir / "product-mask.png",
        metadata_path=output_dir / "segmentation-metadata.json",
        schemas_dir=schemas_dir,
    )
    refined_cutout.save(output_dir / "product-cutout-refined.png", "PNG")
    file_utils.write_json(output_dir / "edge-refinement-metadata.json", edge_meta)
    if schemas_dir is not None:
        schema = file_utils.load_schema(schemas_dir, edge_refinement.SCHEMA_NAME)
        file_utils.validate_against_schema(edge_meta, schema)

    # Placement + scene spec (same contracts as v0.2)
    placement_spec = placement_mod.build_placement_spec(
        seg_result.metadata, canvas_width=canvas_size[0], canvas_height=canvas_size[1]
    )
    placement_mod.save_placement_spec(placement_spec, output_dir / "placement-spec.json", schemas_dir=schemas_dir)
    scene_spec = scene_mod.build_scene_spec(scene_type="lifestyle", interaction_level=0)
    scene_mod.save_scene_spec(scene_spec, output_dir / "scene-spec.json", schemas_dir=schemas_dir)

    # Block 6 — scene-aware background request
    background_request = background_mod.build_scene_aware_background_request(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        scene_intel=scene_intel,
        product_category=scene_intel["product_role"],
        top_environment=top_environment,
    )
    background_mod.save_background_request(background_request, output_dir / "background-request.json", schemas_dir=schemas_dir)

    background_image = background_provider.generate_background(background_request)

    # Block 3 + 5 — perspective match + surface-aware shadow (or v0.2 fallback)
    shadow_params = shadow_mod.build_surface_aware_shadow_params(surface_model)
    perspective_applied = surface_mod.requires_perspective_match(surface_model)

    if perspective_applied:
        composite, warped_product, dst_quad, warped_area = _compose_with_perspective(
            refined_cutout=refined_cutout,
            background_image=background_image,
            placement_spec=placement_spec,
            shadow_params=shadow_params,
        )
        shadow_layer_for_debug = shadow_mod.build_shadow_layer(warped_product, canvas_size, params=shadow_params)
    else:
        compose_result = compositor_mod.compose_scene(
            background=background_image,
            cutout=refined_cutout,
            placement_spec=placement_spec,
            shadow_params=shadow_params,
        )
        composite = compose_result["composite"]
        # compose_scene already positions this correctly (canvas-sized,
        # shadow at the product's actual paste location) — reuse it
        # directly instead of recomputing from the small scaled_cutout,
        # which has no positioning information of its own.
        shadow_layer_for_debug = compose_result["shadow_layer"]
        dst_quad = None
        warped_area = None

    compositor_mod.save_composite(composite, output_dir / "composite-base.png")

    # Block 7 — Composition Gate v0.3
    gate_report = composition_gates.run_composition_gate_v03(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        scene_intel=scene_intel,
        top_environment=top_environment,
        surface_model=surface_model,
        perspective_applied=perspective_applied,
        warped_area=warped_area,
        edge_refinement_applied=True,
        shadow_is_surface_aware=True,
    )
    composition_gates.save_composition_gate_report_v03(
        gate_report, output_dir / "composition-gate-report.json", schemas_dir=schemas_dir
    )

    # Block 11 — visual debug package (9 files: v0.2's 8 + perspective preview)
    debug_dir = output_dir / "visual-debug"
    source_image = Image.open(source_image_path).convert("RGB")
    bbox = placement_spec["product"]["final_bbox"]
    bbox_tuple = (bbox["left"], bbox["top"], bbox["right"], bbox["bottom"])

    debug_dir.mkdir(parents=True, exist_ok=True)
    source_image.convert("RGB").save(debug_dir / "01-source.jpg", "JPEG", quality=90)
    refined_mask.save(debug_dir / "02-mask.png", "PNG")
    refined_cutout.save(debug_dir / "03-cutout.png", "PNG")
    background_image.convert("RGB").save(debug_dir / "04-background.jpg", "JPEG", quality=90)

    if dst_quad is not None:
        perspective_preview = visual_debug.draw_bbox_preview(background_image, bbox_tuple, color=(60, 100, 220))
        draw = ImageDraw.Draw(perspective_preview)
        draw.polygon(dst_quad, outline=(220, 40, 40), width=3)
    else:
        perspective_preview = visual_debug.draw_bbox_preview(background_image, bbox_tuple)
    perspective_preview.save(debug_dir / "05-perspective-preview.png", "PNG")

    edge_preview = visual_debug.thumb(refined_cutout, (refined_cutout.width, refined_cutout.height))
    edge_preview.save(debug_dir / "06-edge-preview.png", "PNG")

    shadow_only = Image.new("RGB", canvas_size, "white")
    shadow_only.paste(shadow_layer_for_debug, (0, 0), shadow_layer_for_debug)
    shadow_only.save(debug_dir / "07-shadow-preview.png", "PNG")

    composite.save(debug_dir / "08-final-composite.png", "PNG")

    gate_color = (40, 180, 80) if gate_report["passed"] else (220, 40, 40)
    gate_overlay = visual_debug.draw_bbox_preview(composite, bbox_tuple, color=gate_color)
    draw2 = ImageDraw.Draw(gate_overlay)
    draw2.rectangle((0, 0, gate_overlay.width, 28), fill=gate_color)
    draw2.text((8, 6), f"COMPOSITION GATE v0.3: {gate_report['status'].upper()}", fill="white")
    gate_overlay.save(debug_dir / "09-gate-overlay.png", "PNG")

    contact_sheet_path = visual_debug.build_composition_contact_sheet(
        source=source_image,
        cutout=refined_cutout,
        background=background_image,
        placement_preview=perspective_preview,
        final_composite=composite,
        gate_report={"passed": gate_report["passed"], "status": gate_report["status"]},
        output_path=output_dir / "composition-contact-sheet.jpg",
    )

    # Block 9 review entry (reuses v0.2's composition_review contract)
    review_entry = composition_review.build_review_entry(
        handle=handle,
        output_type=output_type,
        placement_spec=placement_spec,
        scene_spec=scene_spec,
        gate_report={
            "passed": gate_report["passed"],
            "status": gate_report["status"],
            "geometry": gate_report["geometry"],
            "scene": gate_report["scene"],
        },
        generation_strategy="protected-product-composition-v03",
    )
    review_entry["scene_intelligence"] = {
        "product_role": scene_intel["product_role"],
        "top_environment": top_environment,
        "surface_plane": surface_model["surface_plane"],
        "geometry_class": surface_model["geometry_class"],
        "perspective_applied": perspective_applied,
    }
    file_utils.write_json(output_dir / "review-entry.json", review_entry)

    # Block 8 — benchmark vs v0.2, using the SAME background so the
    # comparison isolates what v0.3 actually changed (perspective/edges/
    # shadow/scene choice), not a different random background.
    v02_bg_path = output_dir / "_v02_background_for_comparison.png"
    background_image.save(v02_bg_path, "PNG")
    v02_result = pipeline_v02.run_composition_for_image(
        handle=handle,
        output_type=output_type,
        source_image_path=source_image_path,
        product_category=scene_intel["product_role"],
        environment_description=top_environment,
        background_provider=FixtureBackgroundProvider(fixture_path=v02_bg_path),
        output_dir=output_dir / "_v02_comparison_run",
        schemas_dir=schemas_dir,
        canvas_size=canvas_size,
    )
    v02_bg_path.unlink(missing_ok=True)

    comparison_path = benchmark_mod.build_full_comparison_contact_sheet(
        source=source_image,
        cutout=refined_cutout,
        background=background_image,
        v02_result=Image.open(v02_result.final_composite_path),
        v03_result=composite,
        output_path=output_dir / "comparison-v02-v03.jpg",
    )

    return CompositionRunResultV03(
        handle=handle,
        output_type=output_type,
        scene_intelligence=scene_intel,
        surface_model=surface_model,
        segmentation_metadata=seg_result.metadata,
        edge_refinement_metadata=edge_meta,
        placement_spec=placement_spec,
        scene_spec=scene_spec,
        background_request=background_request,
        top_environment=top_environment,
        perspective_applied=perspective_applied,
        gate_report=gate_report,
        review_entry=review_entry,
        output_dir=output_dir,
        final_composite_path=output_dir / "composite-base.png",
        contact_sheet_path=contact_sheet_path,
        comparison_path=comparison_path,
    )
