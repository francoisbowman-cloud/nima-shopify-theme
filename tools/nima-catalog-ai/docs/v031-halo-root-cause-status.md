# Nima Catalog AI v0.3.1 — Halo Root Cause Status

Base v0.3 validated: `42b3361`
Branch: `fix/nima-catalog-ai-v031-production-image-readiness`
Current branch HEAD: `15720557474eaed134b036fad9cf6b4392e93db5`
Last fully executed suite on the real local checkout: `207/207 PASS` at `7ed47ca`

## Hallazgos confirmados

- La hipótesis de premultiplicación manual para Pillow BICUBIC fue descartada — Pillow 12.3.0 ya premultiplica internamente en `Image.transform` con resampling; agregarla a mano duplica el efecto y empeora el resultado.
- `perspective.py` no origina el halo.
- `shadow.py` no origina el halo (la capa de sombra es siempre negra pura, `rgb_max=[0,0,0]`).
- Primera fuente confirmada: `edge_refinement.decontaminate_color`, verificada con el asset real `nima-catalog-images/batch-02/waterproof-pet-feeding-mats-.../original/01-original.jpg`.
- El cutoff `<64` en `refine_alpha` elimina la cola dominante de fringe.
- Saturación post-warp global medida antes del nuevo matte candidato: 23.7% → 5.3%.
- Fringe difuso dominante eliminado por el cutoff ya validado.
- Sigue existiendo fringe residual (más tenue, localizado) en la última validación real ejecutada.

## Dos causas residuales confirmadas

### 1. Alfa 64–127

`decontaminate_color` usa el alfa sintético del Gaussian feather como si representara la mezcla física original del JPEG. Esto puede generar extrapolación incorrecta y saturación RGB a 255 (~18% de los píxeles de esa banda en el asset real, tras el warp).

### 2. Contaminación opaque-edge

Una pequeña fracción de píxeles `alpha=255` (~0.11% de los píxeles opacos en el asset real) ya está contaminada con RGB del fondo blanco desde la máscara/segmentación original (`masking.py`). Ejemplo observado: `rgb(250,254,255), alpha=255`.

## Fix validado hasta `7ed47ca`

Implementado y validado con el asset real:

`DEFAULT_FEATHER_ALPHA_CUTOFF = 64`

Después del `GaussianBlur`, cualquier `0 < alpha < 64` colapsa a `0`.

Resultado medido:

- bandas alfa 1–31 → 0 píxeles (eran 5285)
- banda alfa 32–63 → 0 píxeles (eran 193)
- saturación del cutout pre-warp: 9.4% → 5.5%
- saturación post-warp: 23.7% → 5.3%
- banda 1–31 post-warp: 93.9% saturada → 6.6%
- halo difuso dominante eliminado

## Candidato de follow-up implementado — PENDIENTE DE VALIDACIÓN REAL

Commits:

- `398b6c6` — `fix: add conservative background-aware edge matte`
- `1572055` — `test: cover background-aware edge matte guards`

Se añadió `refine_background_edge_matte` entre `refine_alpha` y `decontaminate_color`.

Diseño:

- usa la distancia RGB al fondo de estudio muestreado;
- solo puede actuar en la banda geométrica de borde;
- cubre tanto píxeles semi-transparentes como la frontera de un píxel del hard mask;
- reduce alpha de píxeles claramente parecidos al fondo;
- no recolorea ni reconstruye el producto;
- el interior profundo queda fuera del algoritmo aunque tenga un color parecido al fondo;
- el umbral RGB (`24`) es deliberadamente inferior a la tolerancia de foreground de `masking.py` (`28`), para que sea cleanup y no una segunda segmentación.

Regresiones añadidas para comprobar:

- opaque-edge contaminado parecido al fondo puede colapsar a transparente;
- opaque-edge con color claramente de producto se conserva;
- interior profundo nunca se modifica por similitud de color;
- borde semi-transparente parecido al fondo puede colapsar;
- parámetros inválidos fallan de forma cerrada.

### Estado de validación

**NO declarar PASS todavía.**

El entorno ChatGPT que realizó estos commits tiene acceso de escritura/lectura al repo mediante GitHub, pero no tiene acceso al directorio local no trackeado `nima-catalog-images/`. Además, su runtime no puede resolver `github.com` para crear un checkout temporal y ejecutar pytest. Por tanto:

- `207/207 PASS` sigue siendo el último resultado ejecutado y confirmado sobre el checkout real antes de estos dos commits;
- los tests nuevos están escritos pero todavía no se deben contabilizar como ejecutados;
- el matte candidato requiere una ejecución local sobre el mismo feeding mat antes de considerarse validado.

## Gate requerido para cerrar el halo

Ejecutar la suite completa y el diagnóstico real del feeding mat sobre `1572055` o posterior y comparar contra las métricas de `7ed47ca`.

PASS solo si:

1. toda la suite pasa;
2. el fringe residual desaparece o cae a nivel visual no apreciable sobre gris/oscuro;
3. no hay erosión perceptible del producto;
4. el interior del producto permanece intacto;
5. el warp no reintroduce halo;
6. shadow continúa exonerada.

## Restricciones

- No tocar `main`.
- No tocar Shopify.
- No consumir OpenAI API innecesariamente.
- No reintroducir premultiplicación manual en `perspective.py`.
- No alterar imágenes fuente para esconder el problema.
- No declarar validación visual sin ejecutar sobre los assets reales.

**Veredicto actual: `RESIDUAL HALO — EDGE MATTE CANDIDATE IMPLEMENTED, REAL-ASSET VALIDATION PENDING`**
