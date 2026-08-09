"""v0.2 — orchestrates Blocks 1-9 for one product image, fully offline.

    segmentation -> placement -> scene -> background request -> background
    -> compositor -> shadow -> composition gate -> visual debug -> review entry

Used by both the offline demo (Block 10) and the batch runner (Block 14).
Never calls a real API: `background_provider` must be a `FixtureBackgroundProvider`
(or any provider whose `generate_background` doesn't hit the network) —
`OpenAIBackgroundProvider` raises if used, by design.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from . import background as background_mod
from . import composition_gates
from . import composition_review
from . import compositor as compositor_mod
from . import file_utils
from . import placement as placement_mod
from . import scene as scene_mod
from . import segmentation as segmentation_mod
from . import visual_debug
from .background_provider import BackgroundProvider
from .shadow import ShadowParams


@dataclass
class CompositionRunResult:
    handle: str
    output_type: str
    segmentation_metadata: dict
    placement_spec: dict
    scene_spec: dict
    background_request: dict
    gate_report: dict
    review_entry: dict
    output_dir: Path
    final_composite_path: Path
    contact_sheet_path: Path


def run_composition_for_image(
    *,
    handle: str,
    output_type: str,
    source_image_path: Path,
    product_category: str,
    environment_description: str,
    background_provider: BackgroundProvider,
    output_dir: Path,
    schemas_dir: Path | None = None,
    canvas_size: tuple[int, int] = (1536, 1536),
    shadow_params: ShadowParams | None = None,
) -> CompositionRunResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Block 1
    seg_result = segmentation_mod.segment_product(source_image_path)
    segmentation_mod.save_segmentation(
        seg_result,
        cutout_path=output_dir / "product-cutout.png",
        mask_path=output_dir / "product-mask.png",
        metadata_path=output_dir / "segmentation-metadata.json",
        schemas_dir=schemas_dir,
    )

    # Block 2
    placement_spec = placement_mod.build_placement_spec(
        seg_result.metadata, canvas_width=canvas_size[0], canvas_height=canvas_size[1]
    )
    placement_mod.save_placement_spec(placement_spec, output_dir / "placement-spec.json", schemas_dir=schemas_dir)

    # Block 3
    scene_spec = scene_mod.build_scene_spec(scene_type="lifestyle", interaction_level=0)
    scene_mod.save_scene_spec(scene_spec, output_dir / "scene-spec.json", schemas_dir=schemas_dir)

    # Block 4
    background_request = background_mod.build_background_request(
        scene_spec=scene_spec,
        placement_spec=placement_spec,
        product_category=product_category,
        environment=environment_description,
    )
    background_mod.save_background_request(
        background_request, output_dir / "background-request.json", schemas_dir=schemas_dir
    )

    # Background generation (fixture-backed in v0.2 — see background_provider.py)
    background_image = background_provider.generate_background(background_request)

    # Block 5 + 6
    compose_result = compositor_mod.compose_scene(
        background=background_image,
        cutout=seg_result.cutout,
        placement_spec=placement_spec,
        shadow_params=shadow_params,
    )
    compositor_mod.save_composite(compose_result["composite"], output_dir / "composite-base.png")

    # Block 7
    gate_report = composition_gates.run_composition_gate(scene_spec=scene_spec, placement_spec=placement_spec)
    composition_gates.save_composition_gate_report(
        gate_report, output_dir / "composition-gate-report.json", schemas_dir=schemas_dir
    )

    # Block 8
    debug_dir = output_dir / "visual-debug"
    source_image = Image.open(source_image_path).convert("RGB")
    visual_debug.build_step_outputs(
        output_dir=debug_dir,
        source=source_image,
        mask=seg_result.mask,
        cutout=seg_result.cutout,
        background=background_image,
        placement_spec=placement_spec,
        shadow_preview=compose_result["shadow_layer"],
        final_composite=compose_result["composite"],
        gate_report=gate_report,
    )
    bbox = placement_spec["product"]["final_bbox"]
    bbox_tuple = (bbox["left"], bbox["top"], bbox["right"], bbox["bottom"])
    placement_preview = visual_debug.draw_bbox_preview(background_image, bbox_tuple)
    contact_sheet_path = visual_debug.build_composition_contact_sheet(
        source=source_image,
        cutout=seg_result.cutout,
        background=background_image,
        placement_preview=placement_preview,
        final_composite=compose_result["composite"],
        gate_report=gate_report,
        output_path=output_dir / "composition-contact-sheet.jpg",
    )

    # Block 9
    review_entry = composition_review.build_review_entry(
        handle=handle,
        output_type=output_type,
        placement_spec=placement_spec,
        scene_spec=scene_spec,
        gate_report=gate_report,
    )
    composition_review.write_review_entry(review_entry, output_dir / "review-entry.json")

    return CompositionRunResult(
        handle=handle,
        output_type=output_type,
        segmentation_metadata=seg_result.metadata,
        placement_spec=placement_spec,
        scene_spec=scene_spec,
        background_request=background_request,
        gate_report=gate_report,
        review_entry=review_entry,
        output_dir=output_dir,
        final_composite_path=output_dir / "composite-base.png",
        contact_sheet_path=contact_sheet_path,
    )
