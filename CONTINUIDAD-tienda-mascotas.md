# Continuidad — Nima (ex-PetDrop, RFC-007, Atlas Commerce)
Pegar como primer mensaje en la sesión nueva de Code, junto con
`ESTADO-tienda-mascotas.md` (ya actualizado en el repo, no hace falta
adjuntarlo aparte si la sesión abre con acceso a la carpeta).

## Estado al cierre de esta sesión (6 de agosto de 2026)

Repo: `C:\Users\user\Claude\Projects\OVL_PetDrop`, sincronizado con
`github.com/francoisbowman-cloud/nima-shopify-theme` (privado). Rama
`feat/nima-catalog-api-pipeline-v01`, con el commit `ccc4b6b` del
pipeline de IA — **pusheada a `origin` al cierre de esta sesión, no
mergeada a `main`**. Directorio sin trackear: `nima-catalog-images/`
(203 imágenes + índices, ~150MB — sigue sin decidirse si se commitea o
se deja fuera del repo vía `.gitignore`).

### Lo más importante para entender antes de tocar nada
**El theme publicado (MAIN) en Shopify puede divergir del código de este
repo.** Antes de auditar o tocar cualquier archivo de `theme/`, verificar
contra la API real cuál es el theme `MAIN` actual (procedimiento en
`CLAUDE.md`, sección "⚠️ El theme publicado puede divergir del repo").

### Punto de entrada más reciente: pipeline de imágenes por API de OpenAI — cerrado técnicamente
**Implementado, testeado (49 tests) y validado con dos corridas reales ($0.09 USD de gasto
total) sobre `waterproof-pet-feeding-mats-...`.** Ver decisión #77 de
`ESTADO-tienda-mascotas.md` para el detalle completo. Resumen de lo que importa para retomar:

- **`refined`**: validado técnicamente (llegó a `review`, score 92, usando una máscara de
  preservación de píxeles + recorte determinista). **No publicado en Shopify** — el encuadre
  quedó con ocupación 59.8%, por debajo del rango objetivo 75-88%, porque la foto fuente no
  tiene margen lateral suficiente (no es un bug del código, es un límite de la foto original).
  Brey decidió no reintentar con la misma fuente.
- **`lifestyle`**: rechazado (escala del mat incorrecta, perro en interacción activa en vez de
  presencia pasiva). Brey decidió no reintentar con el mismo método — es un límite conocido de
  v0.1 (sin máscara posible cuando cambia toda la escena, el endurecimiento de prompt solo no
  alcanza para controlar escala/tipo de interacción). Documentado en
  `tools/nima-catalog-ai/README.md`.
- **No consumir más API de OpenAI en esta rama** — instrucción explícita de Brey al cierre.
- Nada tocado en Shopify. Rama sin mergear a `main` — pendiente autorización explícita para
  cualquiera de las dos cosas (merge, o retomar con presupuesto nuevo).

### Completado en esta sesión
1. **`tools/nima-catalog-ai/` implementado de punta a punta**: análisis de producto (Fase 1,
   `gpt-5.6-sol`), plan de generación determinístico (Fase 2), generación de imagen
   (`gpt-image-2` vía `images.edit`, Fase 3), fidelity gate automático (Fase 4, nunca aprueba
   Shopify ni `in-use` automáticamente), control de coste/intentos (Fase 5), paquete de
   revisión local (Fase 6). CLI: `python -m src.cli --input <carpeta> --outputs
   refined,lifestyle,in-use [--dry-run] [--yes] [--force]`.
2. **Estrategia `product-preserving` agregada a pedido de Brey tras la primera corrida real**
   (que salió `reject` en ambas salidas): máscara de preservación a nivel de píxel para
   `refined` (`src/masking.py`, heurística de color de fondo, sin ML), recorte determinista
   hacia el rango de ocupación 75-88% (verificado contra `theme/assets/base.css:221`, sin
   nunca cortar el producto), endurecimiento de reglas de prompt para `lifestyle`/`in-use`
   (sin máscara — la escena cambia por completo).
3. **`product-overrides.json` agregado**: capa separada para correcciones humanas verificadas
   (texto exacto de wordmark, conteos de piezas) que se combina con el análisis automático
   solo al construir el plan — nunca edita `product-analysis.json`. Caché en dos niveles
   (overrides invalidan el plan/outputs, no fuerzan un nuevo análisis).
4. **49 tests**, todos con mocks — ninguna llamada real a la API en los tests.
5. **Dos corridas reales autorizadas por Brey** (ver arriba) — $0.09 USD total, dentro de los
   topes de presupuesto autorizados en cada corrida ($1 c/u).
6. **Commit `ccc4b6b`** en `feat/nima-catalog-api-pipeline-v01` — sin mergear a `main`.

### Pendiente exacto al momento de migrar
1. **Brey decide próximo paso del pipeline de IA**: mergear la rama a `main`, retomar con
   presupuesto nuevo (mejorar `lifestyle`, o probar `refined` con una foto fuente con más
   margen lateral), o dejarlo en pausa. Ninguna imagen de este pipeline está lista para
   publicarse en Shopify todavía.
2. **21 de los 24 productos con imágenes siguen sin pasar por ningún pipeline visual**
   (3 de `pilot-01` tienen imágenes IA aprobadas en Shopify vía el flujo manual con ChatGPT;
   el producto de prueba del pipeline de API, `waterproof-pet-feeding-mats-...`, tiene
   candidatos generados pero no publicados) — no avanzar sobre el resto del catálogo sin que
   Brey lo pida explícitamente.
3. **5 productos sin ninguna imagen en el CSV** (Premium Cat Litter Mat, Dog Clothes Puppy
   Shirts, Dog Birthday Hat, Dog Water Bottle, Dog Car Seat Cover) necesitan una fuente de
   imagen distinta antes de poder trabajarse — no resuelto, no bloqueante para el resto.
4. **Decidir qué hacer con `nima-catalog-images/` en git** (150MB sin trackear) — commitear,
   mover a un remote separado, o `.gitignore`. No decidido esta sesión.
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
  mano** — patrón nuevo de esta sesión (decisión #77), para no perder
  el rastro de qué generó el modelo vs. qué corrigió un humano.
- **Un pipeline de generación de imagen puede quedar "cerrado
  técnicamente" (validado, funcionando) sin que ninguna imagen esté
  lista para publicar** — no asumir que "el pipeline funciona" implica
  autorización para subir nada a Shopify; son decisiones separadas.
- Autoridad exclusiva de `git commit`/`push` es de Code, sin excepción.
- Numeración de decisiones nuevas en `ESTADO`: la asigna quien commitea
  (Code), nunca quien la propone.
- Español neutro, sin coloquialismos. Brey es principiante en
  programación — explicar conceptos técnicos con contexto, sin asumir
  jerga previa.
