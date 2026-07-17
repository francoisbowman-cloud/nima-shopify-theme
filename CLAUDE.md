# PetDrop OVL — CLAUDE.md

Tienda de dropshipping de artículos para mascotas sobre **Shopify** (Online Store 2.0). Segundo producto del sistema Atlas Comerce (junto a Aromia) — a diferencia de Aromia, este SÍ incluye venta transaccional directa (carrito, checkout, pagos).

## Stack

- **Shopify Online Store 2.0** theme (Liquid + JSON templates/sections, sin build step de JS/CSS).
- Vanilla JS (`theme/assets/global.js`) y CSS (`theme/assets/base.css`) — sin framework ni bundler.
- Capa de contenido "OVL" (Omni Visual Language) implementada sobre **metafields de producto**, namespace `ovl` (ver `skills/omni-visual-language/SKILL.md`).
- `prototype/*.html` es el prototipo estático original (pre-Shopify) — se mantiene como referencia de diseño, ya no es el entregable activo.

## Estructura del repo

```
theme/            # theme Shopify activo (Online Store 2.0)
  layout/          # theme.liquid, password.liquid
  sections/        # secciones editables desde el Customizer
  snippets/        # product-card.liquid, etc.
  templates/       # *.json que ensamblan secciones por tipo de página
  config/          # settings_schema.json / settings_data.json (colores, tipografía OVL)
  locales/         # es.default.json (idioma por defecto), en.json
  assets/          # base.css, global.js
  README.md        # mapeo prototipo→theme, metafields OVL, setup inicial en Shopify
prototype/         # HTML estático original (index, product, magazine) — referencia de diseño
docs/              # 01-06: visión, arquitectura, especificación OVL, modelo de contenido, roadmap
skills/omni-visual-language/  # definición del sistema OVL (skill)
references/        # imágenes de referencia visual
ESTADO-tienda-mascotas.md  # estado del proyecto (nivel producto, dentro de Atlas Comerce)
```

## Mapeo prototipo → theme

| Prototipo | Plantilla Shopify | Secciones |
|---|---|---|
| `index.html` | `templates/index.json` | hero, dual-mode-split, feature-cards |
| `product.html` | `templates/product.json` | main-product (Zona 1: compra rápida), product-ovl-story (Zona 2: experiencia OVL) |
| `magazine.html` | `templates/page.magazine.json` | magazine-hero, magazine-grid, ovl-story-split |

## Comandos

Requiere [Shopify CLI](https://shopify.dev/docs/themes/tools/cli). Todos los comandos se corren **dentro de `theme/`**, no en la raíz del repo:

```bash
cd theme
shopify theme dev                  # servidor local con hot reload contra tienda de desarrollo
shopify theme check                # linter de temas
shopify theme push --unpublished   # sube como tema no publicado para revisión
```

## Metafields OVL (namespace `ovl`)

Definidos en Configuración → Metafields personalizados → Productos:

| Metafield | Uso en el theme |
|---|---|
| `ovl.dominant_emotion` | Kicker de producto y badge OVL / kicker en tarjetas |
| `ovl.functional_benefit` | Subtítulo bajo el nombre del producto |
| `ovl.emotional_benefit` | Badge OVL en Zona 2 |
| `ovl.visual_profile` | Badge OVL en Zona 2 |

El conjunto completo previsto (story_id, risk_level, etc.) está en `docs/04_MODELO_DE_CONTENIDO.md` y `docs/05_IMPLEMENTACION_SHOPIFY_AUTODS.md`.

## Setup inicial en Shopify (checklist)

1. Crear menú `main-menu`: Comprar (`/collections/all`), Descubrir (página Magazine), Colecciones, Ayuda.
2. Crear página y asignarle la plantilla `page.magazine`.
3. Definir namespace `ovl` (metafields arriba) y cargar datos por producto.
4. Ajustar colores/tipografía en Customizer → Configuración del tema.

## Pendientes conocidos

- `templates/gift_card.liquid` y `templates/customers/*` no incluidos — agregar solo si se habilitan tarjetas de regalo o cuentas de cliente.
- Selección de variante sin JS cae siempre a la primera variante; con JS (`global.js`) funciona completo (galería + variantes + add-to-cart AJAX).
- Filtros de colección (por mascota/necesidad/tamaño) descritos en `docs/02_ARQUITECTURA_DE_EXPERIENCIA.md` — requieren `filter`/`facets`, no incluidos en esta primera pasada.
- Nombre de marca y dominio: aún sin definir (codename temporal "PetDrop").

## Convenciones

- Español como idioma por defecto (`es.default.json`); inglés disponible (`en.json`).
- No hay tests ni CI configurados — verificación es manual vía `shopify theme dev` / `theme check`.
