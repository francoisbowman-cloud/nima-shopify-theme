# Nima Commerce Media Factory v1

Production pipeline for Nima product imagery. The goal is to stop repairing catalog images inside the theme and make media quality a deterministic pre-publication contract.

## Authority model

- **Commerce Media Factory** owns policy, classification, normalization, quality gates, publish plans and evidence.
- **OMNI** is an exception/treatment adapter for assets that need advanced product-preserving work. OMNI does not decide whether an asset is publishable.
- **Theme** only renders approved assets. CSS is never used to hide embedded beige/gray backgrounds or supplier-image defects.
- **Shopify** receives only candidates that have passed the media gates and a staging/render check.

## State machine

`RAW -> ANALYZED -> NORMALIZED -> FIDELITY_PASS -> COMMERCE_PASS -> SHOPIFY_STAGING -> RENDER_PASS -> PUBLISHED`

Exception states are `SOURCE_TOO_LOW_RES`, `MANUAL_REVIEW`, and `ERROR`.

## Contract

`policy.json` is the single source of truth for:

- pure `#FFFFFF` commerce canvas;
- minimum source resolution;
- white-background threshold;
- safe margins;
- geometry-specific optical occupancy;
- background-uniformity thresholds;
- conservative edge decontamination.

The featured image is a factual product representation. The factory never generates a different product, changes number of pieces, invents materials/features, or converts a weak supplier image into lifestyle art.

## Geometry profiles

The factory supports `compact_object`, `wide_object`, `tall_object`, `long_accessory`, `soft_goods`, and `flat_ground`. Products can override automatic geometry inference in the catalog manifest.

This is intentionally different from a one-size-fits-all pixel scale: a leash, a feeding mat and a grooming glove should have consistent *optical* weight, not identical bounding boxes.

## Baseline audit

The repository snapshot at `catalog/commerce-media-active.json` contains the current active-product featured media captured from Shopify. Run:

```bash
python tools/nima_commerce_media/factory.py \
  --manifest catalog/commerce-media-active.json \
  --out commerce-media-evidence \
  --normalize-safe
```

Outputs:

- `audit.json` — machine-readable classification and metrics;
- `REPORT.md` — catalog-level summary;
- `normalized/*.png` — only deterministic safe-normalization candidates;
- `contact-sheet.jpg` — one-review surface for the batch;
- `publish-plan.json` — candidates that passed factory checks, still requiring Shopify staging + Render Gate.

The factory never publishes merely because a file was generated.

## OMNI exception routing

After an audit:

```bash
python tools/nima_commerce_media/omni_adapter.py \
  --audit commerce-media-evidence/audit.json \
  --output commerce-media-evidence/omni-exceptions.json
```

Only unresolved `NORMALIZE` / `MANUAL_REVIEW` assets are routed to the existing `nima-product` OMNI preset. The request explicitly requires product-preserving output on pure white and forbids generative product replacement.

Any OMNI result must re-enter the Factory at `ANALYZED`; it does not bypass Fidelity or Commerce gates.

## Golden tests

The grooming-gloves defect is the first production golden regression. Its live featured image is marked `golden_test: embedded-background` in the active manifest. CI must fail until that source can be normalized to a candidate satisfying the contract without clipping or geometry loss.

Synthetic tests additionally cover:

- beige/off-white embedded background;
- pure-white border output;
- preservation of core product color;
- low-resolution blocking;
- clipping -> manual review;
- complex backgrounds -> manual review;
- publication plan cannot skip Shopify staging or Render Gate.

## Import-to-publication operating model

1. Supplier/AutoDS media enters **quarantine**, never directly trusted as featured media.
2. Preserve immutable source + source hash.
3. Analyze and classify.
4. Deterministically normalize safe cases.
5. Route genuine exceptions to OMNI or manual review.
6. Re-analyze all returned assets.
7. Require Fidelity + Commerce PASS.
8. Upload approved candidate to Shopify staging without deleting the previous image.
9. Verify card, Collection, Search, PDP, Cart and mobile through Render Gate.
10. Promote to featured media only after Render PASS; keep rollback reference.

## Non-negotiable rules

- Commerce primary imagery: clean pure-white canvas.
- Lifestyle/editorial imagery: separate media class and pipeline.
- No CSS background masking as a media fix.
- No screenshot-derived replacement assets.
- No silent upscaling of inadequate sources.
- No global algorithm change for one SKU without golden regression coverage.
- No automatic deletion of the previous Shopify featured media before verification.

This turns catalog media from a recurring design repair task into a controlled production system.
