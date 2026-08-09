# Generation plan — in-use

Goal: show the product functioning as intended, so a buyer understands how it works. This
output type is only generated when `product-analysis.json` sets
`eligible_outputs.in_use = true` — if it is `false`, skip this plan entirely (state `omitted`
in the run manifest, do not attempt a generation call).

Composition rules:

- Depict exactly the interaction described in `interaction_constraints` from the analysis —
  do not invent a different interaction, grip, or usage pattern.
- Correct functional orientation is mandatory (e.g. the contact surface named in
  `interaction_constraints` must be the surface actually touching the pet/user).
- One clear, legible interaction — no busy multi-action scenes.

Mandatory rules:

- All `refined`/`lifestyle` fidelity rules apply (shape, color, material, count, function).
- Anatomically correct human/animal depiction — reject any output with malformed limbs, paws,
  hands, or incorrect number of digits/limbs.
- Scale of any person/pet must match `scale_constraints`.
- This output type always requires human review before it can be used anywhere — the pipeline
  must never mark an `in-use` image `approved_candidate` without a review step downstream.

Rejection criteria: wrong interaction, wrong contact surface, anatomical defects, product
alteration, or implausible scale.
