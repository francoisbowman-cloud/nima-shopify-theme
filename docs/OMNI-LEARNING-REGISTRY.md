# OMNI Learning Registry — Nima

Este registro convierte defectos reales en protecciones permanentes. No es una memoria informal: cada aprendizaje debe contener evidencia, causa, corrección, prueba y alcance de reutilización.

## Flujo obligatorio

1. Observar un defecto real.
2. Registrar evidencia reproducible.
3. Separar causa específica del proyecto y principio reutilizable.
4. Corregir en una rama o tema de vista previa.
5. Añadir una prueba de regresión.
6. Validar idiomas, viewports y estados afectados.
7. Promover a OVKB únicamente el aprendizaje general; nunca datos específicos de Nima.
8. Publicar solo después de aprobación humana cuando corresponda.

## Caso NIMA-LEARN-001 — Texto editorial recortado en móvil

- Fecha: 2026-08-11
- Superficie: Home → Magazine teaser
- Evidencia: captura móvil aportada por el usuario.
- Síntoma: “Una vida más tranquila, mejor compartida” y el párrafo excedían el borde derecho.
- Causa: tamaño fijo de 46 px, ancho editorial estrecho y un ancestro con `overflow:hidden`; el control global de ancho no detectaba recorte interno.
- Corrección específica: tipografía móvil fluida, ancho máximo explícito y `overflow-wrap:anywhere`.
- Protección: `.github/omni_render_gate_v2.py::assert_text_containment` compara tamaño desplazable y límites contra el ancestro que recorta.
- Cobertura: kicker, título, párrafo y CTA del teaser; EN/ES; móvil/escritorio mediante el Render Gate.
- Principio reutilizable: “La ausencia de overflow global no demuestra que el texto sea visible; verificar contención local en componentes con overflow.”
- Estado: implementado en PR #15; requiere Render Gate contra una vista previa inequívoca antes del merge.

## Política de memoria

- Los casos permanecen aquí como historial específico de Nima.
- Los principios generales se promueven a OMNI/OVKB con procedencia y limitaciones.
- Un aprendizaje no autoriza modificar, fusionar o publicar automáticamente.
- Una corrección sin prueba no se considera aprendizaje cerrado.
