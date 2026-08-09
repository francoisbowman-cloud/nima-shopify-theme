# Generation plan — refined

Goal: a clean catalog packshot, produced as a cleanup/edit of the real product photo — not a
from-scratch redraw. This image replaces or supplements the primary product photo, so any
deviation from the real product is a defect, not a stylistic choice.

Priority order (do these in order, not all at once):

1. **Clean up the original** — remove dust, staging props (water droplets, kibble, bowls used
   only for demonstration), reflections, or stray marketplace text/badges.
2. **Replace or clean the background** — this is the main job of this output type.
3. **Correct lighting** — even studio light, no harsh shadows, no blown highlights.
4. **Preserve the product exactly** — this is a constraint on 1–3, not a separate creative step.

## Product-preserving mode

When `product-analysis.json` shows a wordmark, logo, embossing/relief, or a small functional
part whose exact shape/count matters (a paw-shaped tab, a clasp, a baffle, a perforation
pattern — anything an image model tends to redraw slightly wrong), `generation-plan.json`
marks this output `strategy: "product-preserving"` with `mask_strategy: "background-only"`.
In that mode the product's own pixels are locked by a preservation mask before the edit call —
the model is only allowed to touch the background. Do not attempt to "improve" or redraw
anything inside the masked (preserved) region even if asked to in general terms; the mask
makes that a no-op, but the prompt should not fight the mask either.

## Composition rules

- Product fully visible, optically centered, occupying the target range given in
  `framing_rules` (not just its bounding box — account for asymmetric visual weight like a
  handle or tab). No cropping of any part listed in `critical_visual_features`.
- Neutral, uncluttered studio background (light/cream, consistent with Nima's catalog style)
  unless `product-analysis.json` marks the background as an `allowed_changes` item with a
  different instruction.
- No added props, no added text, no added packaging, no watermarks.
- No people, no animals, unless the product cannot be understood without one AND
  `eligible_outputs.refined` still says true (it should almost always be a bare product shot).
- Avoid excessive white canvas around the product — `framing_rules.target_occupancy_pct_min/max`
  gives the acceptable range; too small an occupancy wastes the frame, too large crowds it
  against the card's own padding (see README.md "Storefront framing").

## Mandatory rules

(merge with `forbidden_changes` and `critical_functional_features` from the analysis — this
prompt does not override those, it is generic scaffolding)

- Preserve exact shape, proportions, color(s), material texture, and any functional part named
  in `critical_visual_features` / `critical_functional_features` — including exact wordmark
  text and exact small-part counts (e.g. a 4-toe paw tab stays 4 toes, not 5 or 6).
- Preserve item count exactly (a "pair" stays a pair, a multi-pack keeps its depicted count).
- Do not invent geometry, seams, closures, or labels not present in the reference.

Rejection criteria: any violation of the above, a result that reads as a different product
category than the source, or product occupancy far outside the `framing_rules` target range.
