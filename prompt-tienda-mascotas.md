# Prompt de handoff para Code — PetDrop (Fase 1, MVP Utility)

Este es el documento de estado del proyecto PetDrop (tienda de dropshipping de
mascotas, dentro de Atlas Comerce). Léelo como contexto antes de responder.
Al final de esta sesión te voy a pedir que resumas las decisiones nuevas para
actualizar el `ESTADO`.

Nota: este ESTADO es distinto del CLAUDE.md que puedas generar en el repo. El
ESTADO es el documento de producto cross-actor; el CLAUDE.md es tu memoria
técnica exclusiva dentro del repo. No los confundas ni los mezcles.

# Estado del proyecto: [NOMBRE PENDIENTE — codename temporal: PetDrop]
Última actualización: 12 de julio de 2026 — por: Chat
Nivel: **Producto**, dentro del sistema **Atlas Comerce** (ver `ESTADO-atlas-comerce.md`, Project Atlas-Comerce-Lab)

---

## 1. Objetivo del proyecto
Tienda de dropshipping de artículos para mascotas, sobre Shopify.
Segundo producto confirmado del sistema Atlas Comerce, junto a Aromia.
[Completar: propuesta de valor, nicho específico dentro de "mascotas"
si ya está definido — tipo de producto, mercado objetivo]

---

## 2. Alcance actual (qué SÍ, qué NO)

**Diferencia clave frente a Aromia — anotar explícitamente para que no
se asuma lo contrario:**
- **SÍ incluye venta directa transaccional** (carrito, checkout, pagos)
  — a diferencia de Aromia, que la excluye por completo. Atlas Comerce
  como sistema no impone un modelo de negocio único a sus productos;
  cada uno define el propio.

[Completar con Cowork: alcance específico — catálogo inicial,
proveedor(es) de dropshipping, mercados de envío, métodos de pago]

---

## 3. Decisiones tomadas

| # | Decisión | Tomada por |
|---|---|---|
| 1 | Es un producto dentro de Atlas Comerce, no un proyecto aislado — mismo nivel jerárquico que Aromia | Brey |
| 2 | A diferencia de Aromia, este producto SÍ incluye venta directa transaccional (dropshipping vía Shopify) | Brey |
| 3 | Nombre de marca/dominio: pendiente de definir — se usa codename `PetDrop` hasta entonces | Brey |

[Continuar acá con lo que ya se decidió en la sesión de Cowork
"Shopify store setup" — pegar el resumen de cierre de esa sesión]

---

## 4. Artefactos generados hasta ahora

| Artefacto | Actor que lo creó | Ubicación/link |
|---|---|---|
| Sesión Cowork "Shopify store setup" | Cowork | [pegar link] |

---

## 5. Dependencias externas

| Dependencia | Tipo | Referencia |
|---|---|---|
| **Sistema Atlas Comerce** | Sistema padre | `ESTADO-atlas-comerce.md` — Project Atlas-Comerce-Lab |
| **Image Toolkit** | Herramienta genérica (posible, a confirmar si aplica a fotos de producto) | `ESTADO-image-toolkit.md` — Project Image-Toolkit-Lab |

---

## 6. Próximo paso
[Completar una vez traído el resumen de la sesión de Cowork]

---

## 7. Pendientes / preguntas abiertas
- Nombre de marca y dominio
- [Completar el resto según lo que arroje la sesión de Cowork]

---

*Este documento sigue la plantilla del `PROTOCOLO-comunicacion-actores.md`. Referencia al sistema padre (Atlas Comerce) sin duplicar su contenido — ver sección 5.*


---

## Instrucción específica de tu rol (Code)

Actuás como implementador. Partí del prompt técnico y del prototipo adjunto
(carpeta `prototype/`, export estático de Design/ChatGPT). No definas scope
nuevo por tu cuenta — si ves ambigüedad de producto (no técnica), señalala y
esperá definición en vez de asumir. Además de programar, generá o actualizá el
`CLAUDE.md` del repo con lo técnico-operativo (stack, comandos de build/test,
estructura, convenciones). Al terminar, actualizá el `ESTADO` con lo que quedó
funcional, lo que quedó pendiente, y cómo correr/probar lo hecho.

---

## Tarea concreta

**Objetivo:** convertir el prototipo estático adjunto (`prototype/index.html`,
`product.html`, `magazine.html`, `styles.css`) en un theme de Shopify (Liquid)
funcional para la tienda PetDrop, plan Basic.

**Alcance — Fase 1 (Utility Commerce), NO incluir todavía:**
- ❌ No implementar el sistema OVL completo (motor de interpretación de
  esencia, perfiles visuales dinámicos, generación automática de copy). Eso es
  Fase 2/3 — ver `docs/03_ESPECIFICACION_OVL.md` y `docs/06_ROADMAP_Y_GOBERNANZA.md`
  solo como referencia de hacia dónde escala esto, no como requerimiento actual.
- ❌ No armar el modelo de "Ediciones OVL" descrito en la visión editorial —
  sigue sin formalizar a nivel de Atlas Comerce (ver pendientes del `ESTADO`).

**Sí incluir en esta fase:**
1. Theme de Shopify con al menos estas plantillas, basadas en el prototipo:
   - `index` (home) — a partir de `prototype/index.html`.
   - `product` — a partir de `prototype/product.html`. Debe integrarse con el
     sistema estándar de producto/variantes de Shopify (no hardcodear datos).
   - Una página tipo `page.magazine` simple — a partir de `prototype/magazine.html`,
     como versión inicial del "Journal", sin la lógica de Ediciones todavía
     (ver Decisión #11 del ESTADO: esta página es base a evolucionar, no
     versión final).
2. Estructura de secciones editables desde el Theme Editor de Shopify (no
   hardcodear texto/imágenes donde el usuario deba poder cambiarlos sin código).
3. Conexión con el catálogo importado vía AutoDS (productos ya existentes o
   de prueba) — confirmar con Brey si ya hay productos cargados antes de
   asumir estructura de datos.
4. Dejar preparados (aunque vacíos) los metafields sugeridos en
   `docs/05_IMPLEMENTACION_SHOPIFY_AUTODS.md` bajo el namespace `ovl` (para no
   tener que re-trabajar el modelo de datos cuando llegue la Fase 2):
   `ovl.dominant_emotion`, `ovl.functional_benefit`, `ovl.emotional_benefit`,
   `ovl.visual_profile`, `ovl.story_id`, `ovl.risk_level`, `ovl.content_status`,
   `ovl.review_status`, `ovl.editorial_priority`.
5. Checklist de revisión humana antes de publicar cualquier producto real
   (criterio RFC-002 "calidad sobre velocidad"): dejar esto documentado en el
   `CLAUDE.md` o en un comentario visible del theme, no como gate automático
   de código — la revisión la hace Brey, no un script.

**Nota sobre assets:** el prototipo referencia `assets/store-direction.png` y
`assets/ovl-example.png` que no existen todavía en este paquete — usar
placeholders o las imágenes sí incluidas (`source-products.png`,
`mockup-reference.png`) y señalarlo como pendiente en tu resumen final, no
inventar ni generar imágenes por tu cuenta sin que Brey lo confirme.

**Adjunto:** `handoff-code-tienda-mascotas.zip` — contiene `docs/` (los 6
documentos de visión/arquitectura/especificación OVL, como contexto de hacia
dónde escala el proyecto) y `prototype/` (el HTML/CSS/imágenes a convertir).

---

## Al terminar esta sesión

Resumí en 10-15 líneas: qué decisiones técnicas tomaste, qué quedó
funcional, qué quedó pendiente (incluyendo lo de los assets faltantes), y qué
archivos/artefactos generaste. Formato: texto plano listo para pegar en el
`ESTADO-tienda-mascotas.md`.
