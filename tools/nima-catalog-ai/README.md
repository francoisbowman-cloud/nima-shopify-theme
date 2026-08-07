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
