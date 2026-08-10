# Nima Commerce Media Normalization Contract

Status: Web Premium Hardening staging contract

## Objective

Nima commercial product imagery must read as one controlled catalogue system even when source assets arrive from different suppliers. Runtime presentation must never crop product imagery or allow supplier framing differences to dictate card/PDP geometry.

Editorial and lifestyle assets are a separate system and may use intentional crop/cover behavior.

## Media grades

The theme exposes three presentation grades through `data-media-grade`:

- `refined`: source filename follows the Nima refinement convention (`-refined-`, `_refined_`, or `refined-v`). These assets have already been through a product-preserving visual refinement pass and may use a tighter safe area.
- `source`: a commerce image exists but is still a supplier/original asset. It receives the most conservative safe area.
- `missing`: no featured commerce image exists.

This is a presentation signal, not a substitute for visual QA.

## Runtime invariants

1. Commerce surfaces use a true white studio canvas.
2. Product imagery uses `object-fit: contain`; commercial selectors must not use `cover`.
3. Image padding must be included in the declared media box (`box-sizing: border-box`) so safe-area padding cannot create clipping.
4. Unknown/source imagery gets more breathing room than refined imagery.
5. PDP thumbnails inherit the same product-preserving policy.
6. Cart imagery follows the commerce-white/contain policy.
7. Editorial collection and magazine imagery remains independent and may intentionally crop.
8. Motion must never change product fidelity or geometry and must respect `prefers-reduced-motion`.

## Safe-area targets

Current storefront defaults:

| Surface | Source / unknown | Refined |
| --- | --- | --- |
| Product card | ~14% | ~9% |
| PDP main | ~11% | ~8% |
| PDP thumbnail | 10px | 7px |
| Cart | 12% | 12% |

These values are presentation defaults. A refined asset should itself provide enough native white margin that the storefront does not need to compensate for an edge-to-edge crop.

## Asset-level production standard

A commerce asset is not considered production-ready merely because it is displayed on a white CSS container. The source file should satisfy all of the following:

- product identity and geometry preserved;
- entire sellable product visible unless the product inherently exceeds the frame;
- true or visually neutral white background for the primary commercial asset;
- no supplier logos, watermarks, badges, UI, text overlays, or unrelated props;
- no AI substitution or redesign of the real product;
- consistent optical scale relative to other products in the catalogue;
- sufficient negative space around all product edges;
- no halo, edge contamination, transparency artifacts, or obvious extraction seams;
- color variants remain faithful to the actual sellable variant.

Recommended filename convention: `<product-slug>-refined-vN.<ext>`.

## Separation of commerce and editorial media

Primary catalogue / collection card / PDP / cart media:
- controlled white background;
- product-first;
- fidelity-first;
- contain geometry.

Home storytelling / Magazine / lifestyle modules:
- contextual scenes are allowed;
- crop/cover is allowed when intentional;
- lighting and composition may be editorial;
- these assets must never silently replace the primary product image.

## Release gates

A media-related release can progress only when:

1. automated locale, media-system and premium-experience contracts pass;
2. Theme Validation passes;
3. Launch Contract passes;
4. staging RC remains unpublished during validation;
5. real Desktop/Mobile Render Gate confirms Home, Collection, PDP, Search and populated Cart in EN and ES;
6. Render Gate checks product containment, white commercial canvases, thumbnail behavior, horizontal overflow, translation markers and interaction states;
7. any source asset whose embedded background/framing violates the production standard is logged for upstream normalization rather than hidden with CSS tricks.

Until step 5 is executed with a real browser, visual closure is not granted.
