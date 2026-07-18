# Estado del proyecto: [NOMBRE PENDIENTE — codename temporal: PetDrop]
Última actualización: 17 de julio de 2026 — por: Code
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
| 4 | Paleta "clínico y confiable": acento `#3E8FA6`, texto `#1F2E33`, fondos/bordes teal suaves — reemplaza verde OVL original | Brey + Chat |
| 5 | Tipografía encabezados: Georgia Pro (`georgia_pro_n4`); cuerpo sin cambios (Helvetica); Hero mantiene sans-serif por decisión de diseño, no unificar | Brey + Chat |
| 6 | Theme `PetDrop_OVL` subido a Shopify vía CLI como borrador (unpublished), ID `198713933905` | Chat |
| 7 | 3 bugs post-push resueltos (font-face fuera de estilo, color pisado por base.css, fuente Hero) — causa raíz y regla nueva documentadas en CLAUDE.md | Code |
| 8 | 4 productos archivados por no encajar en el nicho o estar mal importados | Brey (con análisis de Chat) |
| 9 | 4 descripciones de producto reescritas por contener basura de scraping | Chat |
| 10 | Metafields `ovl.*` cargados en 9 productos activos/draft | Chat |
| 11 | Se descarta la división de trabajo entre actores (Cowork/Code) para las tareas pendientes — Code continúa solo con todo, incluida la investigación de decisiones de negocio (sin ejecutar login a cuentas externas) | Brey |
| 12 | Moneda de la tienda cambiada de DOP a USD, siguiendo la recomendación de Code | Brey |

Detalle completo de cada tanda de cambios técnicos: ver `CHANGELOG.md` en la raíz del repo.

---

## 4. Artefactos generados hasta ahora

| Artefacto | Actor que lo creó | Ubicación/link |
|---|---|---|
| Sesión Cowork "Shopify store setup" | Cowork | [pegar link] |
| Theme `PetDrop_OVL` (unpublished) | Chat (push) + Code (fixes) | Shopify admin, tienda `petdrop-9236.myshopify.com`, theme ID `198713933905` |
| `CHANGELOG.md` (raíz del repo) | Code | Historial detallado de cambios técnicos, actualizado por tanda |
| `CLAUDE.md` (raíz del repo) | Code | Memoria técnica del repo (arquitectura, convenciones, causas raíz de bugs) |

---

## 5. Dependencias externas

| Dependencia | Tipo | Referencia |
|---|---|---|
| **Sistema Atlas Comerce** | Sistema padre | `ESTADO-atlas-comerce.md` — Project Atlas-Comerce-Lab |
| **Image Toolkit** | Herramienta genérica (posible, a confirmar si aplica a fotos de producto) | `ESTADO-image-toolkit.md` — Project Image-Toolkit-Lab |

---

## 6. Próximo paso
Todo lo técnicamente resoluble por Code está hecho: auditoría completa del theme
(sin roturas encontradas fuera de un bug menor ya corregido — logo del header con
`height="auto"` inválido), `theme check` limpio, e investigación de las 4 decisiones
de negocio pendientes con datos reales de la tienda (no solo preguntas genéricas).
Ver el detalle completo y la lista de acciones ordenada en
`docs/07_INVESTIGACION_DECISIONES_DE_NEGOCIO.md`, sección 0.
Próximo paso real: que Brey ejecute esa lista (decisiones de producto + logins
manuales a Shopify/AutoDS + el `theme push` final).

---

## 7. Pendientes / preguntas abiertas
- Nombre de marca y dominio.
- 4 productos sin imagen real (Cat Litter Mat, Dog Birthday Hat, Dog Car Seat Cover,
  Dog Water Bottle) — confirmado por API que no tienen ninguna imagen cargada en
  Shopify; falta que Brey revise en AutoDS si el proveedor tiene fotos o no
  (ver `docs/07_...md`, sección 1).
- Desfase de conteo AutoDS→Shopify: confirmado por API que hay 13 productos en
  Shopify (9 Draft + 4 Archived), no 11+4 como se pensaba — de los 15 supuestamente
  importados en AutoDS, 2 no llegaron en ningún estado. Falta que Brey cruce la
  lista de 13 (en `docs/07_...md`, sección 2) contra su lista de 15 en AutoDS.
- ~~Moneda DOP vs USD~~ — **hecho**: Brey cambió la moneda de la tienda a USD (confirmado por API el 17/07).
- Mercados de envío, métodos de pago (Shopify Payments no disponible para RD —
  se necesita PayPal o Payoneer Checkout), políticas de devolución/envío — propuesta
  completa lista para pegar en el admin, ver `docs/07_...md`, sección 4.
- `theme push` a Shopify requiere login OAuth interactivo — no ejecutable por Code, lo corre Brey manualmente.
- Acceso al admin de Shopify (mercados/pagos) y al panel de AutoDS — fuera del alcance de Code, requieren login manual de Brey.

---

*Este documento sigue la plantilla del `PROTOCOLO-comunicacion-actores.md`. Referencia al sistema padre (Atlas Comerce) sin duplicar su contenido — ver sección 5.*
