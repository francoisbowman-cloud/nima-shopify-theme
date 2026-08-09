# nima-catalog-ai (v0.1)

Local pipeline that turns one Nima product folder (originals + manifest + brief) into a
human-reviewable package of AI-generated catalog images, using the OpenAI API. It never
publishes or modifies Shopify — see `docs/08_FLUJO_CATALOGO_Y_OMNI.md` for the sibling
OMNI-based flow this does *not* replace.

## Setup

```bash
cd tools/nima-catalog-ai
python -m venv .venv && . .venv/Scripts/activate   # or source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY (never commit this file)
```

## Usage

Dry run (analysis + plan only, no API cost for image generation):

```bash
python -m src.cli --input "../../nima-catalog-images/batch-02/<handle>" \
  --outputs refined,lifestyle,in-use --dry-run
```

Real run (spends API budget — requires `--yes`):

```bash
python -m src.cli --input "../../nima-catalog-images/batch-02/<handle>" \
  --outputs refined,lifestyle,in-use --max-attempts 2 --max-cost-usd 5 --yes
```

Outputs land under `tools/nima-catalog-ai/output/<handle>/`:

```
analysis/product-analysis.json
analysis/generation-plan.json
generated/<handle>__<type>__v<N>.png
reviews/<type>-fidelity-report.json
run/run-manifest.json
run/cost-report.json
run/state.json          # idempotency state — pass --force to ignore and regenerate
review-package/         # the human-facing deliverable (see FASE 6 of the spec)
```

## Models (verify before relying on this doc — re-check developers.openai.com/api/docs)

- Text/vision (analysis, fidelity review): `gpt-5.6-sol` — flagship reasoning+vision model.
- Image generation/edit: `gpt-image-2` via `images/generations` and `images/edits`.

Verified 2026-08-06 against `developers.openai.com/api/docs/models` and independent web
search. Do not assume `gpt-4o` / `gpt-image-1` without re-checking — these move fast.

## Estrategia product-preserving

Descubierta a partir de la primera generación real: `refined` y `lifestyle` fueron
rechazados por el fidelity gate por defectos sutiles pero reales — el número de dedos de
una pestaña con forma de pata (4 reales vs. ~6 generados) y una letra cambiada en un
wordmark grabado ("Moki Found" → "Hoki Found"). Un regenerado completo desde texto no
garantiza reproducir ese tipo de detalle exacto.

`build_brief.detect_product_preserving()` escanea `product-analysis.json` en busca de
palabras clave (wordmark, logo, relieve/emboss, y piezas pequeñas críticas: pestañas, pads,
cierres, mecanismos, perforaciones...). Si encuentra alguna, marca la salida como
`strategy: "product-preserving"` en `generation-plan.json`:

- **`refined`** (`mask_strategy: "background-only"`): se genera una máscara de preservación
  (`src/masking.py`, heurística de color de fondo — sin ML, sin dependencias pesadas) que
  bloquea los píxeles del producto y solo permite editar el fondo. Esto es una garantía real
  a nivel de píxel, no una instrucción de prompt que el modelo puede ignorar. Solo funciona
  con una única imagen de referencia (limitación de la API de `images/edits` con `mask`) y
  solo es fiable sobre fondos de estudio razonablemente uniformes — no sirve para fondos
  complejos o multi-objeto.
- **`lifestyle` / `in-use`**: el encuadre cambia (el producto se reubica en una escena nueva),
  así que una máscara de un solo fotograma no aplica. En su lugar, el prompt se endurece con
  las reglas "product-preserving" explícitas (texto exacto del wordmark, conteo exacto de
  partes pequeñas) en vez de instrucciones genéricas — es una mejora de probabilidad, no una
  garantía de píxel como en `refined`.

Cada intento sobre una salida enmascarada guarda su máscara en `output/<handle>/masks/` y
registra `reference_occupancy_pct` / `candidate_occupancy_pct` en `run-manifest.json` como
diagnóstico (no como gate automático).

## product-overrides.json — correcciones humanas verificadas

`product-analysis.json` es siempre el output crudo del análisis automático (Fase 1) — **nunca
se edita a mano**. Cuando una revisión humana descubre un dato verificado que el análisis no
capturó (ej. el texto exacto de un wordmark, tras ver que un candidato lo generó mal), se
registra en un archivo separado, opcional, junto al `manifest.json` del producto:

```
<input_dir>/product-overrides.json
```

Esquema: `schemas/product-overrides.schema.json`. Campos soportados: `wordmark_exact_text`,
`part_counts` (objeto pieza→conteo entero), `confirmed_colors`, `functional_constraints`,
`human_corrections` (notas libres). Ejemplo real (nacido de una corrección tras el primer
intento real de `waterproof-pet-feeding-mats-...`):

```json
{
  "wordmark_exact_text": "Moki Found",
  "part_counts": {"paw_tab_toe_pads": 4}
}
```

`build_brief.build_generation_plan()` combina `product-analysis.json` + `product-overrides.json`
solo al construir `generation-plan.json` — las reglas de override se agregan al final de
`mandatory_rules` (leen como la última palabra si contradicen algo inferido) y basta con tener
cualquier override para activar `strategy: "product-preserving"`, aunque el análisis automático
no haya detectado palabras clave. El análisis original nunca se toca ni se sobrescribe.

**Caché en dos niveles** (`src/cli.py`): el análisis (Fase 1, la llamada cara) se cachea solo
por `input_hash` (manifest + brief + imágenes) — los overrides no lo invalidan, porque no
cambian lo que el modelo ve en Fase 1. El plan y el estado de outputs cacheados (Fase 2 en
adelante) se cachean por `combined_hash` (`input_hash` + hash de los overrides) — cambiar
`product-overrides.json` invalida el plan y fuerza una nueva generación, sin gastar una
llamada de análisis extra. `--force` sigue ignorando cualquier caché.

## Reglas de encuadre y storefront framing

`generation-plan.json` incluye `framing_rules` por salida: ocupación objetivo 75–88%,
márgenes equilibrados, centrado óptico, y `card_aspect_ratio: "1:1"` — verificado contra el
theme real, no asumido (`theme/assets/base.css:221`, `.pcard__media{aspect-ratio:1/1}`).

**Punto 6 de la auditoría — de dónde sale el espacio blanco en una tarjeta de catálogo:**

- **(A) Del archivo generado**: lo que este pipeline controla — cuánto aire deja alrededor
  del producto dentro del PNG que produce `gpt-image-2`. `framing_rules` apunta a esto.
- **(B) Del CSS de la tarjeta** (`theme/assets/base.css`):
  - `.pcard__media{aspect-ratio:1/1; background:var(--soft); overflow:hidden}` (línea 221) —
    la tarjeta es siempre un cuadro 1:1 con un color de fondo propio detrás.
  - `.pcard__media img{width:100%;height:100%;object-fit:contain;padding:var(--space-12)}`
    (línea 222) — **el `<img>` tiene `padding: 12px` fijo por CSS**, aplicado a *todas* las
    tarjetas sin importar cuán ajustado venga el archivo. Además, `object-fit:contain` dentro
    de un cuadro 1:1 agrega letterboxing extra si el archivo no es exactamente cuadrado.

Conclusión: incluso con un archivo generado perfectamente encuadrado (ocupación 88%), la
tarjeta va a mostrar un margen adicional de 12px por el padding del CSS, más cualquier
letterbox si el aspect ratio del archivo no es 1:1 exacto. Esto **no se tocó** — es
documentación, no un cambio de theme (fuera de alcance de esta tarea).

## Cost estimates are estimates

`images/*` responses don't return a dollar cost. `src/cost_control.py` uses a small
price table sourced from a third-party aggregation, **not** confirmed against OpenAI's own
pricing page (which returned HTTP 403 to automated fetch when this was written). Re-verify
before trusting it for a real budget decision — see the module docstring.

## Safety

- `OPENAI_API_KEY` is read only from the environment (`.env`, gitignored). The tool exits
  with a clear error if it's missing — it is never logged, printed, or written to any output
  file, even partially.
- `--dry-run` never calls image generation.
- Any real (non-dry-run) run that would call image generation requires `--yes`.
- `in-use` outputs are only planned when `product-analysis.json` marks them eligible, and a
  fidelity decision of `approved_candidate` is force-downgraded to `review` for that output
  type — this pipeline never auto-approves an in-use image.
- `approved_candidate` anywhere means "ready for human review", never "ready to publish".
  Nothing in this tool uploads to Shopify.

## Known limitations of v0.1

Confirmed against the two real generation runs on `waterproof-pet-feeding-mats-...`
(2026-08-06) — not theoretical:

- **`refined` framing depends entirely on the source photo's own margins.** The
  crop-to-target-occupancy step (`masking.crop_to_target_occupancy`) can only *remove*
  background — it cannot add margin the source photo doesn't have. On our real test image,
  the product already filled ~900 of 911px width, so no crop could reach the 75–88%
  occupancy target without either exceeding the image's shorter dimension or cutting the
  product. The pipeline correctly refuses to cut the product in that case (see `note` in
  `framing_rules` diagnostics) — but the result is a framing violation the fidelity gate will
  keep flagging until a better-margined source photo is supplied. This is a source-image
  problem, not a pipeline bug.
- **No outpainting.** This pipeline never fabricates canvas beyond the source image's own
  pixels. If a tighter framing requires *more* background than exists in the original photo
  (rather than less), v0.1 cannot produce it — that would need a genuinely different technique
  (canvas extension / outpainting), out of scope here.
- **`lifestyle` (and `in-use`) have no pixel-level protection.** Masking only works for
  `refined` because the framing stays close to the original photo. Once the product is
  relocated into a new scene, there's no single-frame mask that corresponds to both the old
  and new composition, so `lifestyle`/`in-use` rely entirely on prompt hardening (exact text,
  exact counts) — a probability improvement, not a guarantee. Confirmed failure mode: our real
  `lifestyle` run generated the mat at roughly 25–30" instead of the specified 19", a scale
  error a pixel mask would have prevented but prompt text alone did not catch before
  generation (the fidelity gate caught it after, correctly).
- **`lifestyle` can be confused with `in-use` by the model.** The same real run showed active
  product interaction (a dog drinking mid-frame) in an output whose plan explicitly said
  "passive/ambient presence only" — the fidelity gate correctly rejected it, but the
  generation step itself did not reliably respect the passive/active distinction from text
  instructions alone.
- **A full-frame preservation mask stops helping once the whole scene changes.** This is the
  general form of the two points above: `mask_strategy: "background-only"` is a real
  pixel-level guarantee only when the edit is "same photo, different background" — the moment
  composition, camera angle, or scene context change (as they do for `lifestyle`/`in-use`),
  there's no mask that maps cleanly between "what must stay" and "what may change," and the
  pipeline has to fall back to prompt-based hardening instead.

## Out of scope for v0.1

Shopify upload/reorder/delete, AutoDS, theme changes, prices/variants/inventory, the rest of
the catalog beyond one product at a time, OMNI's general architecture, a database, a dashboard.

## Nima Catalog AI v0.2 — Protected Lifestyle Composition

v0.2 lives alongside v0.1 in the same `src/` tree (v0.1's own modules and tests are
untouched — see "Known limitations of v0.1" above, this section exists to fix exactly
those points). It does not replace `src/cli.py`; it is a second, independent pipeline
entered via `src/composition_pipeline.py` / `src/composition_batch.py` /
`src/demo_v02.py`.

### Why: what v0.1's `lifestyle` output actually got wrong

v0.1's `lifestyle`/`in-use` outputs ask an image model to redraw the entire scene,
product included, from a hardened text prompt. Confirmed failures from the real run
(see above): the product's scale drifted (~25–30" generated vs. 19" real), and a
supposedly passive scene generated active use instead. Both failures are inherent to
asking a generative model to reproduce a specific object's exact geometry from
description alone — no amount of prompt hardening closes that gap completely.

### What changed

```
Before (v0.1 lifestyle/in-use):
    AI regenerates product + AI regenerates scenario, together, from text

Now (v0.2):
    real product pixels (segmented from the source photo)
    + AI-generated scenario (product-free)
    + deterministic local compositor
    = final image
```

The product is never redrawn. The only thing an image model is asked to produce is the
*environment* — with an explicitly reserved empty region where the real product gets
pasted in afterward, locally, by `src/compositor.py`.

### Pipeline

```
source photo
  -> segmentation (src/segmentation.py)         product-cutout.png, product-mask.png,
                                                  segmentation-metadata.json
  -> placement (src/placement.py)                placement-spec.json — deterministic
                                                  bbox/occupancy math, no API call
  -> scene (src/scene.py)                        scene-spec.json — lifestyle (interaction_level=0)
                                                  vs in-use (>=1), explicit and mutually exclusive
  -> background request (src/background.py)      structured prompt asking ONLY for the
                                                  environment, product's zone reserved empty
  -> background provider (src/background_provider.py)
                                                  BackgroundProvider interface; v0.2 only
                                                  ever runs FixtureBackgroundProvider
  -> compositor (src/compositor.py)               pastes the real cutout into the
                                                  background at the planned bbox — a single
                                                  uniform (never distorting) scale, no redraw
  -> shadow (src/shadow.py)                       soft offset+blurred contact shadow under
                                                  the product, first-pass grounding only
  -> composition gate (src/composition_gates.py)  deterministic geometry + scene checks
  -> [existing Fidelity Gate, unchanged]          visual-identity authority, still last word
  -> review package (src/composition_review.py)   composition + generation_strategy fields
```

Orchestrated end to end by `src/composition_pipeline.run_composition_for_image()` for a
single image, and `src/composition_batch.run_batch()` for a product list (Block 14 —
writes `catalog-review/<handle>/` + `catalog-composition-summary.json`).

### Segmentation

`src/segmentation.py` exposes one function, `segment_product()`, with a pluggable
`backend` argument. v0.2 ships and uses only `"heuristic"` — it reuses v0.1's
`masking.py` background-color + largest-connected-component approach, so it inherits
the same known limitation (only reliable when the product is the frame's largest
distinct-colored region). `register_backend()` is the extension point for `rembg`, SAM,
or a manually supplied mask later — no caller of `segment_product()` needs to change
when that happens.

### Interaction model — why lifestyle can never become in-use silently

`src/scene.py` defines `interaction_level` 0-3 (passive presence / proximity / active
use / close manipulation) and enforces at construction time that
`scene_type="lifestyle"` **requires** `interaction_level=0` and all three
`*_contact_allowed` flags `False` — the exact combination that failed in v0.1's real
run (a "passive" lifestyle scene that generated a dog drinking) is now a
`SceneSpecError` at spec-build time, not just a Fidelity Gate rejection after the fact.
v0.2's compositor only ever produces `interaction_level=0` scenes
(`scene.MAX_SUPPORTED_INTERACTION_LEVEL = 0`); levels 1-3 are modeled in the schema so a
future in-use-composition version doesn't need a schema break, but nothing in v0.2 can
produce or approve one.

### Composition Gate vs. Fidelity Gate

```
Composition Gate  ->  Fidelity Gate  ->  Human Review
(deterministic,        (unchanged from       (unchanged —
 no model call)         v0.1, model call)      still mandatory)
```

The Composition Gate (`src/composition_gates.py`) catches what's computable from the
specs alone and needs no judgment call: product outside the canvas, safe-zone
violation, non-uniform aspect-ratio distortion, occupancy outside the plausible
0.05-0.60 range, or (for a `bottom-center` anchor) a product not resting on the ground
plane. The Fidelity Gate remains the sole authority on visual identity — whether the
composited result still *looks like* the real product — and is untouched by v0.2.

### Review package additions

`src/composition_review.py` adds a `composition` block (`occupancy`, `clipping`,
`interaction_level`, `scale_status`, `placement_status`) and a `generation_strategy` /
`generation_kind` field to each candidate's review entry. `generation_kind` is always
one of `REFINED` / `LIFESTYLE COMPOSITE` / `IN-USE` — a candidate built by the v0.2
compositor is always labeled `generation_strategy: "protected-product-composition"`, so
a reviewer never has to guess which pipeline produced a given image.

### Visual debug output — the point of v0.2 you can actually look at

Every composition run writes a `visual-debug/` folder (`01-source.jpg` through
`08-gate-overlay.png`) plus a single `composition-contact-sheet.jpg` (SOURCE / CUTOUT /
BACKGROUND / PLACEMENT / FINAL / GATE RESULT, labeled). This is deliberately not
optional or test-only — see `src/visual_debug.py` and `src/demo_v02.py`.

### Offline demo

```bash
cd tools/nima-catalog-ai
python -m src.demo_v02              # writes to tools/nima-catalog-ai/demo-output/ (gitignored)
python -m src.demo_v02 --out /tmp/x # or any other output path
```

Builds a synthetic product photo and a synthetic background fixture in-process (no
dependency on `nima-catalog-images/`, which is untracked, or on v0.1's `output/`, which
only exists after a real v0.1 run) and runs the full pipeline above end to end. No
network call happens anywhere in this path — `demo_v02.py` only ever constructs a
`FixtureBackgroundProvider`.

### Future API wiring (interface only — not connected)

`src/background_provider.py` defines the `BackgroundProvider` seam: anything with a
`generate_background(request) -> Image` method. `OpenAIBackgroundProvider` exists to
prove the interface fits a real backend, but its `generate_background()` always raises
`NotImplementedError` — it is inert by construction, not just by convention, so it
cannot be accidentally wired into an offline run or test. Connecting it for real is
future work requiring explicit authorization (see the v0.2 phase's safety rules) —
not part of this phase.

### Known limitations of v0.2

- Segmentation is the same heuristic as v0.1's masking — a busy, low-contrast, or
  multi-object source photo can still produce a poor cutout. `edge_confidence` in
  `segmentation-metadata.json` is a rough proxy, not a real segmentation confidence
  score; it's not wired to any automatic reject.
- The contact shadow is a single soft blob (offset + Gaussian blur), not a physically
  modeled shadow — no perspective, no light-direction awareness. Good enough to avoid a
  "pasted-on" look at a glance, not a substitute for real relighting.
- No 3D perspective: the compositor places the product at a single anchor
  (`bottom-center` or `center`) with a flat ground plane — a background with strong
  perspective (e.g. a hallway shot) can still look geometrically off even when every
  Composition Gate check passes.
- In-use composition (interaction_level >= 1) is modeled in the schema but not
  implemented — `scene.MAX_SUPPORTED_INTERACTION_LEVEL = 0` is the hard ceiling for
  this version.
- `OpenAIBackgroundProvider` has never been exercised against a real background — its
  first real call is explicitly deferred (see "Next step" in the v0.2 final report).

## Nima Catalog AI v0.3 — Scene Intelligence + Perspective Match + Edge Integration

v0.3 lives alongside v0.1 and v0.2 in the same `src/` tree, entered via
`composition_pipeline_v03.run_composition_v03_for_image()` /
`src/demo_v03.py`. **v0.1's and v0.2's own modules are untouched** (all
120 of their tests still pass unmodified) — v0.3 only adds new modules
plus small, additive extensions to `shadow.py`, `background.py`, and
`composition_gates.py` (new functions alongside the existing v0.2 ones,
nothing removed or changed in place).

### Why: what Real Pilot 01 (v0.2) actually got wrong

Real Pilot 01 (decision #79) confirmed v0.2's Composition Gate passing
doesn't mean the result looks integrated. Three concrete defects, all
visible in that pilot's output:

1. **Perspective mismatch.** The product photo was shot top-down/frontal;
   the AI background was shot at eye level. v0.2 only ever applied a
   uniform scale, so the product read as a flat card leaning upright
   against the scene, not a mat lying on the floor.
2. **Scene mismatch.** v0.2 asked for "a nice-looking environment" with no
   reasoning about commercial fit — a living room is plausible for a
   *feeding* mat, but a kitchen feeding corner or covered patio is the
   better commercial context, and nothing in v0.2 could make that call.
3. **Edge integration.** v0.2's mask is a hard 0/255 binary cutoff, with no
   anti-aliasing and no removal of the studio background's color bleeding
   into edge pixels — visible as a faint white halo around the product.

### What changed

```
Before (v0.2):
    real product pixels, uniformly scaled, pasted onto any decent-looking AI background

Now (v0.3):
    real product pixels, geometrically perspective-matched to the scene's ground plane,
    edge-refined, shadow tuned to the product's own physical geometry,
    placed into a scene chosen because it fits the product commercially
```

### Pipeline

```
product-analysis.json (reused, no new API call)
  -> scene intelligence (src/scene_intelligence.py)   scene-intelligence.json — product_role,
                                                        ranked environments, placement_plane,
                                                        geometry_class, from a local keyword
                                                        taxonomy over Nima's real catalog vocabulary
  -> surface model (src/surface.py)                    surface-model.json — is this product
                                                        perspective-match eligible? (only
                                                        surface_plane=ground + geometry_class=flat)
  -> segmentation (v0.2, reused)                       product-cutout.png, product-mask.png
  -> edge refinement (src/edge_refinement.py)          feathered alpha + background-color
                                                        decontamination — same product pixels,
                                                        cleaner edges, no visible blur
  -> scene-aware background request (src/background.py's
     build_scene_aware_background_request)             environment = scene intelligence's top
                                                        pick; reserved zone phrased in relative
                                                        frame percentages, not raw pixel coords
  -> background provider (v0.2, reused)                still only ever FixtureBackgroundProvider
                                                        in offline runs; OpenAIBackgroundProvider
                                                        still inert by construction
  -> perspective match (src/perspective.py)             IF eligible: geometric warp of the real
                                                        product pixels onto a floor-perspective
                                                        trapezoid — no redraw, no numpy/opencv
                                                        dependency (pure-Python 8x8 solver)
  -> surface-aware shadow (shadow.py's
     build_surface_aware_shadow_params)                 blur/opacity/offset tuned by geometry_class
                                                        + surface_plane instead of one generic preset
  -> Composition Gate v0.3 (composition_gates.py's
     run_composition_gate_v03)                          v0.2's checks + scene-product fit,
                                                        perspective plausibility, edge/shadow
                                                        pass confirmation
  -> [existing Fidelity Gate, unchanged]
  -> visual debug (9 files, 01-09) + composition-contact-sheet.jpg
  -> benchmark comparison (src/benchmark.py)             comparison-v02-v03.jpg — the same
                                                        background run through both pipelines,
                                                        side by side
```

### Scene Intelligence — a local taxonomy, not a new LLM call

`src/scene_intelligence.py` matches `product-analysis.json`'s
title/category/features against a small keyword taxonomy covering Nima's
real catalog vocabulary (feeding, bedding, walking/leash, grooming, toys,
sanitation), each entry carrying its own ranked environment list,
preferred surfaces, `placement_plane`, and `geometry_class`. No API call —
deterministic and free. A product that matches nothing falls back to a
generic profile with a `warnings` entry rather than guessing; extending
coverage for a new category is one new taxonomy entry, not a new prompt.

### Perspective Match Engine — the core of v0.3

`src/perspective.py` is the piece that actually fixes the "pasted-on
sticker" look. For a product classified `surface_plane=ground` +
`geometry_class=flat` (see `surface.py` — a feeding mat, not a bowl or a
leash), `compute_ground_quad()` derives a floor-perspective trapezoid from
the placement bbox (narrower/higher top edge, full-width bottom edge,
vertical foreshortening), and `apply_perspective_match()` warps the real
product pixels onto that trapezoid with a standard 4-point homography.

**No numpy or OpenCV dependency** — `find_coeffs()` solves the 8x8
perspective-coefficient linear system with a small pure-Python Gaussian
elimination (same approach as the well-known PIL "quad transform" cookbook
recipe), keeping this an isolated tool like `masking.py`. Verified visually
during development: a synthetic flat rectangle warped through this path
reads immediately as "lying on the floor, receding into the scene" instead
of "flat card standing upright."

**Stated plainly, this is a heuristic, not a measured homography** — v0.3
has no camera calibration or vanishing-point detection on the *background*
image, so `compute_ground_quad`'s tilt/foreshorten parameters are a
plausible approximation, not derived from the actual scene geometry. See
"Known limitations of v0.3" below.

### Edge Integration Engine

`src/edge_refinement.py` is a second, optional pass over an existing
cutout+mask (never re-derives the mask): `refine_alpha()` feathers the hard
binary edge with a small (~1.2px, capped at 3px) Gaussian blur — enough to
remove jagged pixel-stair edges, nowhere near enough to visibly soften the
product itself. `decontaminate_color()` then removes the sampled studio
background color's contribution from the now-semi-transparent edge band
(standard alpha-unpremultiply color decontamination), removing the white
halo a light studio backdrop leaves around a darker product edge.

### Surface-aware shadow

`shadow.build_surface_aware_shadow_params()` selects blur/opacity/offset
from a small preset table keyed on `(surface_plane, geometry_class)`
instead of v0.2's one-size-fits-all default — a flat mat flush on the
ground gets a tighter, more perimeter-only contact shadow; a soft bed gets
a larger, softer one. The shadow's *shape* was already free: v0.2's
`build_shadow_layer()` derives its silhouette from whatever image it's
given, so passing it the perspective-warped product (not the
axis-aligned original) makes the shadow inherit the same trapezoid
footprint automatically, with no change to `build_shadow_layer()` itself.

### Composition Gate v0.3

`composition_gates.run_composition_gate_v03()` runs all of v0.2's checks
(geometry, scene) plus four new ones: does the chosen environment actually
appear in the product's own scene-intelligence taxonomy; if perspective
match was eligible, was it actually applied, and is the warped area
plausible relative to the un-warped placement bbox (catches a degenerate
or wildly wrong warp); was perspective applied to something *not* eligible
(would itself be the bug); and were the edge-refinement and surface-aware
shadow passes actually run. Still strictly additive to v0.2's checks — a
v0.3 result never gets a pass that a v0.2-only check would have failed.

### Benchmark comparison mode

`src/benchmark.py` runs the *same* AI-generated background through both
the v0.2 and v0.3 compositors and renders them side by side
(`comparison-v02-v03.jpg`) — using the same background isolates what v0.3
actually changed (perspective, edges, shadow, scene choice) rather than
confounding the comparison with a different random background each time.

### Known limitations of v0.3

- `compute_ground_quad`'s trapezoid is a plausible heuristic, not a
  measured homography — v0.3 has no vanishing-point or camera-angle
  detection on the background image itself. A background shot at a very
  different angle than the default assumption can still look geometrically
  off even after the warp.
- Perspective match only applies to `surface_plane=ground` +
  `geometry_class=flat` products (mats, placemats). Bowls, beds, leashes,
  and everything else fall back to v0.2's uniform-scale placement
  unchanged — this is deliberate (warping a volumetric or soft object's
  2D photo the same way would distort it, not integrate it), but it means
  v0.3's biggest visual improvement is scoped to one geometry class so far.
- Edge decontamination assumes a roughly uniform sampled background color
  (same corner-sampling heuristic as `masking.py`) — a gradient or textured
  studio backdrop will decontaminate less accurately.
- No in-use composition, same as v0.2 — `scene.MAX_SUPPORTED_INTERACTION_LEVEL`
  is still 0.
- Scene Intelligence's taxonomy is hand-authored and covers Nima's current
  catalog vocabulary — a genuinely novel product category falls back to a
  generic profile rather than failing, but won't get a tailored environment
  list until the taxonomy is extended.

## Nima Catalog AI v0.3.1 — Halo Root Cause Status

The white-halo defect flagged in "Known limitations of v0.3" above has a
confirmed root cause and a partial fix, both tracked in
[`docs/v031-halo-root-cause-status.md`](docs/v031-halo-root-cause-status.md)
(branch `fix/nima-catalog-ai-v031-production-image-readiness`) — current
verdict: `RESIDUAL HALO — DECONTAMINATION MODEL REQUIRES FOLLOW-UP`.
