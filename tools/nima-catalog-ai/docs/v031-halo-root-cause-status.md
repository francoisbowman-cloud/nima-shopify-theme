# Nima Catalog AI v0.3.1 — Halo Root Cause Status

Base v0.3 validated: `42b3361`
Branch: `fix/nima-catalog-ai-v031-production-image-readiness`
HEAD: `7ed47ca0bee83787c42d83101ccf1bf246ab2973`
Tests: `207/207`

## Hallazgos confirmados

- La hipótesis de premultiplicación manual para Pillow BICUBIC fue descartada — Pillow 12.3.0 ya premultiplica internamente en `Image.transform` con resampling; agregarla a mano duplica el efecto y empeora el resultado.
- `perspective.py` no origina el halo.
- `shadow.py` no origina el halo (la capa de sombra es siempre negra pura, `rgb_max=[0,0,0]`).
- Primera fuente confirmada: `edge_refinement.decontaminate_color`, verificada con el asset real `nima-catalog-images/batch-02/waterproof-pet-feeding-mats-.../original/01-original.jpg`.
- El cutoff `<64` en `refine_alpha` elimina la cola dominante de fringe.
- Saturación post-warp global: 23.7% → 5.3%.
- Fringe difuso dominante eliminado.
- Sigue existiendo fringe residual (más tenue, localizado).

## Dos causas residuales confirmadas

### 1. Alfa 64–127

`decontaminate_color` usa el alfa sintético del Gaussian feather como si representara la mezcla física original del JPEG. Esto puede generar extrapolación incorrecta y saturación RGB a 255 (~18% de los píxeles de esa banda en el asset real, tras el warp). **No modificar aún la fórmula sin nueva validación.**

### 2. Contaminación opaque-edge

Una pequeña fracción de píxeles `alpha=255` (~0.11% de los píxeles opacos en el asset real) ya está contaminada con RGB del fondo blanco desde la máscara/segmentación original (`masking.py`), antes de que `refine_alpha` o `decontaminate_color` intervengan. Ejemplo observado: `rgb(250,254,255), alpha=255`. Estos píxeles quedan fuera de cualquier decontaminación basada únicamente en alfa parcial, porque nunca son parcialmente transparentes.

## Estado del fix actual

Implementado: `DEFAULT_FEATHER_ALPHA_CUTOFF = 64` en `refine_alpha` (`src/edge_refinement.py`). Después del `GaussianBlur`, cualquier `0 < alpha < 64` colapsa a `0`; `alpha=0` y `alpha>=64` quedan sin tocar (`decontaminate_color` no se modificó).

Resultado, medido sobre el asset real:

- bandas alfa 1–31 → 0 píxeles (eran 5285)
- banda alfa 32–63 → 0 píxeles (eran 193)
- saturación del cutout pre-warp: 9.4% → 5.5%
- saturación post-warp: 23.7% → 5.3%
- banda 1–31 post-warp: 93.9% saturada → 6.6%
- halo difuso dominante eliminado

**Veredicto: `RESIDUAL HALO — DECONTAMINATION MODEL REQUIRES FOLLOW-UP`**

## Restricciones

- No tocar `main`.
- No tocar Shopify.
- No consumir OpenAI API innecesariamente.
- No reintroducir premultiplicación manual en `perspective.py`.
- No asumir que perspectiva o sombra son culpables — ya descartadas con evidencia.
- Trabajar primero sobre diagnóstico reproducible con los assets reales locales (`nima-catalog-images/`, sin trackear en git) antes de proponer una solución.

## Próximo problema técnico

Diseñar una solución correcta para:

- **A.** contaminación cromática en píxeles parcialmente transparentes, alfa 64–254.
- **B.** contaminación de RGB en algunos píxeles totalmente opacos del borde de la segmentación.

La solución debe preservar los píxeles reales del producto y no erosionar detalles válidos. No implementado todavía — pendiente de diseño y validación en una sesión futura.
