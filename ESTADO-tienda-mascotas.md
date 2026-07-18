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
Code (sin división de actores desde la decisión #11) está ejecutando en esta sesión:
auditoría técnica completa del theme, investigación de las decisiones de negocio
pendientes (imágenes faltantes, desfase de conteo AutoDS, moneda DOP/USD, mercados/pagos/
políticas), y va a dejar una lista final de acciones manuales para Brey (logins y CLI).
Esta sección se cierra con el resultado concreto al terminar esa tanda de trabajo.

---

## 7. Pendientes / preguntas abiertas
- Nombre de marca y dominio.
- 4 productos sin imagen real (Cat Litter Mat, Dog Birthday Hat, Dog Car Seat Cover,
  Dog Water Bottle) — investigación en curso, ver `CHANGELOG.md`.
- Desfase de conteo AutoDS→Shopify (15 importados, 11 sincronizados) — investigación en curso.
- Moneda DOP vs USD — investigación en curso.
- Mercados de envío, métodos de pago, políticas de devolución sin configurar — propuesta en curso.
- `theme push` a Shopify requiere login OAuth interactivo — no ejecutable por Code, lo corre Brey manualmente.
- Acceso al admin de Shopify (mercados/pagos) y al panel de AutoDS — fuera del alcance de Code, requieren login manual de Brey.

---

*Este documento sigue la plantilla del `PROTOCOLO-comunicacion-actores.md`. Referencia al sistema padre (Atlas Comerce) sin duplicar su contenido — ver sección 5.*
