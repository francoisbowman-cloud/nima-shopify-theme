# Continuidad — Nima (ex-PetDrop, RFC-007, Atlas Commerce)
Pegar como primer mensaje en la sesión nueva de Code, junto con
`ESTADO-tienda-mascotas.md` (ya actualizado en el repo, no hace falta
adjuntarlo aparte si la sesión abre con acceso a la carpeta).

## Estado al cierre de esta sesión (7 de agosto de 2026)

Repo: `C:\Users\user\Claude\Projects\OVL_PetDrop`, sincronizado con
`github.com/francoisbowman-cloud/nima-shopify-theme` (privado). Rama
`feat/nima-catalog-ai-v02-lifestyle-composition`, HEAD `71cc6f2` —
**pusheada a `origin` al cierre de esta sesión, sin PR, no mergeada a
`main`** (`main` sigue en `6a48a20`). Directorio sin trackear:
`nima-catalog-images/` (sigue sin decidirse si se commitea o se deja
fuera del repo vía `.gitignore` — no tocado esta sesión).

### Lo más importante para entender antes de tocar nada
**El theme publicado (MAIN) en Shopify puede divergir del código de este
repo.** Antes de auditar o tocar cualquier archivo de `theme/`, verificar
contra la API real cuál es el theme `MAIN` actual (procedimiento en
`CLAUDE.md`, sección "⚠️ El theme publicado puede divergir del repo").
No se tocó nada de `theme/` ni de Shopify en esta sesión — todo el
trabajo fue en `tools/nima-catalog-ai/`.

### Punto de entrada más reciente: Nima Catalog AI v0.2 implementado + 1 pilot real — y v0.3 ya solicitado, sin empezar
Ver decisiones #78/#79 de `ESTADO-tienda-mascotas.md` para el detalle completo. Resumen de lo
que importa para retomar:

- **v0.2 ("Protected Lifestyle Composition") implementado y testeado (120/120 tests)** —
  resuelve el límite de v0.1 (decisión #77) componiendo el producto real, segmentado, sobre un
  fondo generado por IA que nunca ve el producto, en vez de regenerar todo desde texto.
- **1 pilot real ejecutado** sobre `waterproof-pet-feeding-mats-...` (mismo producto de v0.1):
  1 llamada real a `images.generate` (~$0.03, sin reintentos), Composition Gate: PASS. Bug real
  de visualización encontrado y corregido en el mismo pilot (`visual_debug._thumb()` perdía
  alfa). **Hallazgo principal**: el producto se ve "pegado"/parado, no apoyado en el piso — la
  foto fuente es una toma cenital y v0.2 no tiene transformación de perspectiva.
- **Instrucción explícita recibida al cierre de esta sesión: construir v0.3** ("Scene
  Intelligence + Perspective Match + Edge Integration") — prompt maestro completo ya recibido,
  **todavía no ejecutado, cero código escrito**. Objetivo: (1) elegir escena coherente con el
  producto (para una feeding mat: cocina/mudroom/patio, no living room), (2) transformar
  geométricamente el producto real para que coincida con la perspectiva del fondo (sin
  redibujarlo), (3) mejorar integración de bordes (halo blanco actual), (4) sombra
  surface-aware. Nueva rama sugerida: `feat/nima-catalog-ai-v03-scene-intelligence-perspective`,
  base = `71cc6f2` (HEAD actual de v0.2). Autoriza 1 sola llamada real de generación de fondo al
  final, mismas reglas de seguridad que v0.2 (no Shopify, no `main`, no PR/merge automático).
  **El prompt completo del usuario para v0.3 debe pegarse en la sesión nueva** — no está
  resumido en ningún archivo del repo todavía, solo en esta conversación que se va a cerrar.
- **Instrucción adicional recibida en el mismo mensaje, también sin empezar**: auditoría
  completa de traducción EN/ES del theme (`BLOCK — GLOBAL TRANSLATION & LOCALE AUDIT`) — ya se
  detectó que en locale EN el catálogo muestra filtros de categoría en español ("Comederos",
  "Descanso", "Paseo" en vez de sus equivalentes en inglés). Alcance: solo consistencia EN/ES
  del theme (nav, catálogo, filtros, product cards/page, Magazine, About, Contact, footer,
  cart, search, aria-labels) — explícitamente NO autoriza traducción automática de
  descripciones vía API, ni cambios de contenido de producto, ni publicación en Shopify.

### Completado en esta sesión
1. **`tools/nima-catalog-ai/` v0.2 implementado de punta a punta** (Blocks 1-15 del prompt
   maestro v0.2): segmentación (`src/segmentation.py`), placement (`src/placement.py`), scene
   spec (`src/scene.py`), background contract + provider (`src/background.py`,
   `src/background_provider.py`), compositor (`src/compositor.py`), sombra (`src/shadow.py`),
   Composition Gate (`src/composition_gates.py`), visual debug (`src/visual_debug.py`), review
   package extendido (`src/composition_review.py`), orquestador (`src/composition_pipeline.py`),
   batch (`src/composition_batch.py`), demo offline (`src/demo_v02.py`). v0.1 queda intacto y
   congelado (49/49 tests siguen pasando sin tocarse).
2. **71 tests nuevos** (120 total, todos pasando).
3. **Checkpoint verificado y rama pusheada a `origin`** antes del pilot real (branch, HEAD,
   tests, `main` intacto, Shopify intacto).
4. **1 pilot real autorizado y ejecutado** sobre `waterproof-pet-feeding-mats-...`: segmentación
   real correcta (excluyó automáticamente la grilla de swatches), 1 llamada real a
   `images.generate` (sin reintentos), Composition Gate: PASS, evaluación visual honesta
   (perspectiva es el cuello de botella real).
5. **Bug real encontrado y corregido en el pilot**: `visual_debug._thumb()` perdía el canal
   alfa (`.convert("RGB")` sin componer sobre blanco primero) — corregido, 120/120 tests
   siguen pasando.
6. **Commits `91c1cd4` (v0.2) y `71cc6f2` (fix + `generate_image`)**, pusheados a `origin` —
   sin PR, sin merge a `main`.
7. **`ESTADO-tienda-mascotas.md` y `CHANGELOG.md` actualizados** con decisiones #78/#79 y
   tanda 22 — este archivo (`CONTINUIDAD`) reescrito para el cierre de sesión.

### Pendiente exacto al momento de migrar
1. **Ejecutar v0.3** (prompt maestro completo recibido, no resumido en ningún archivo salvo
   esta conversación) — scene intelligence, perspective match, edge integration, surface-aware
   shadow, 1 pilot real adicional autorizado. Rama nueva desde `71cc6f2`.
2. **Ejecutar la auditoría de traducción EN/ES** (mismo mensaje, alcance separado de v0.3) —
   filtros de categoría del catálogo ya confirmados mezclando idiomas en locale EN.
3. **Brey decide sobre v0.2**: si vale la pena seguir invirtiendo antes de resolver el problema
   de perspectiva, cuándo mergear `feat/nima-catalog-ai-v02-lifestyle-composition` (o la v0.3
   que salga de ella) a `main`, y cuándo autorizar más llamadas API o publicación a Shopify.
4. **21 de los 24 productos con imágenes descargadas siguen sin pasar por ningún pipeline
   visual** (no tocado esta sesión, ver `ESTADO` sección 8 para el detalle completo).
5. Sigue pendiente de sesiones anteriores (no tocado esta sesión, ver
   `ESTADO-tienda-mascotas.md` sección 7/8 para el detalle completo): publicar el duplicado de
   theme `199238025297` ("Nima — Evolucion fundamentos"), tratamiento de las 5 fotos de AutoDS
   con marca de competidor (decisión #37/#49, en pausa), conectar Codex Cloud al repo,
   confirmar moneda en AutoDS, decidir cuándo quitar la contraseña del sitio.

## Reglas de esta sesión, ya en memoria (no hace falta repetirlas)
- **Verificar contra el repo/API real antes de reportar algo como
  pendiente o roto** — no asumir desde memoria de sesión.
- **Nunca escribir directo sobre el theme MAIN/publicado vía API** —
  Shopify lo bloquea. Flujo seguro: duplicar → aplicar fixes en el
  duplicado → Brey revisa y publica manualmente.
- **Nunca mutar Shopify (subir imágenes, reordenar, etc.) sin
  autorización explícita y punto por punto** — el flujo de `pilot-01`
  (revisión humana → confirmación → ejecución → validación → registro
  de rollback) es el patrón a repetir para cualquier escritura futura
  a Shopify, no solo para imágenes.
- **No dar por hecho nombres de modelo/endpoints de APIs externas
  (OpenAI, etc.) desde memoria de entrenamiento** — verificar contra
  documentación oficial vigente antes de programar, con fecha de
  verificación anotada (regla explícita de Brey para el pipeline de
  IA, decisión #76/#77).
- **Correcciones humanas verificadas sobre un producto van en
  `product-overrides.json`, nunca editando `product-analysis.json` a
  mano** — patrón de v0.1 (decisión #77), sigue vigente en v0.2.
- **Un pipeline de generación de imagen puede quedar "cerrado
  técnicamente" (validado, funcionando) sin que ninguna imagen esté
  lista para publicar** — no asumir que "el pipeline funciona" implica
  autorización para subir nada a Shopify; son decisiones separadas.
- **Antes de cualquier llamada real a una API paga: verificar checkpoint
  completo primero** (branch/HEAD/tests/`main` intacto/Shopify intacto),
  hacer push del punto de partida, y respetar el límite exacto de
  llamadas autorizado — nunca reintentar automáticamente ni encadenar
  una segunda llamada "para mejorar" sin autorización nueva. Patrón
  usado en el pilot real de v0.2 (decisión #79), a repetir en v0.3.
- **Un pilot real es para diagnosticar la arquitectura, no para perseguir
  una imagen perfecta** — no consumir una segunda llamada para arreglar
  lo que salió mal en la primera; documentarlo como hallazgo y seguir.
- Autoridad exclusiva de `git commit`/`push` es de Code, sin excepción.
- Numeración de decisiones nuevas en `ESTADO`: la asigna quien commitea
  (Code), nunca quien la propone.
- Español neutro, sin coloquialismos. Brey es principiante en
  programación — explicar conceptos técnicos con contexto, sin asumir
  jerga previa.
