# Nima (ex-PetDrop) OVL — CLAUDE.md

Tienda de dropshipping de artículos para mascotas sobre **Shopify** (Online Store 2.0). Segundo producto del sistema Atlas Commerce (junto a Aromia) — a diferencia de Aromia, este SÍ incluye venta transaccional directa (carrito, checkout, pagos).

Nombre de marca final: **Nima** (dominio `nimapets.com`). El codename `PetDrop` sigue viviendo en el nombre de la carpeta del repo, el subdominio `petdrop-9236.myshopify.com`, y el theme ID `PetDrop_OVL` en Shopify — ninguno de esos requiere renombrarse, son identificadores internos. El texto visible al cliente dentro del theme (locales, nombre del theme, comentarios) ya se rebrandeó a "Nima".

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
ESTADO-tienda-mascotas.md  # estado del proyecto (nivel producto, dentro de Atlas Commerce)
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
- Nombre de marca: **Nima** (dominio `nimapets.com`, ya definido y conectado — ver ESTADO decisión #18). El `theme push` final que propaga el rebrand al theme publicado en Shopify sigue pendiente (requiere login OAuth interactivo, lo ejecuta Brey).

## Convenciones

- Español como idioma por defecto (`es.default.json`); inglés disponible (`en.json`).
- No hay tests ni CI configurados — verificación es manual vía `shopify theme dev` / `theme check`.

## Colores y tipografía: dónde viven y por qué NO deben duplicarse

Los custom properties de color/tipografía (`--bg`, `--text`, `--green`, `--serif`, `--sans`, etc.)
se definen **una sola vez**, dinámicamente, en un bloque `{%- style -%}...{%- endstyle -%}` dentro
de `:root` en `layout/theme.liquid` y `layout/password.liquid`, leyendo de `settings.*`
(`config/settings_data.json` vía `config/settings_schema.json`).

`assets/base.css` se carga **después** de ese bloque inline en el `<head>` (mismo orden en
ambos layouts). Si `base.css` redeclara esos mismos custom properties en su propio `:root`
con valores fijos, esas declaraciones ganan la cascada (mismo selector, llegan después) y
**pisan silenciosamente** los valores configurados en el Customizer — el color de acento o
la tipografía elegida dejan de reflejarse aunque `settings_data.json` esté bien. Esto ya pasó
una vez (color verde `#0c6b45` hardcodeado sobreviviendo al cambio de paleta) — `base.css`
no debe volver a tener un bloque `:root{...}` con estos tokens; solo los layouts los definen.

`font_face` (filtro de Liquid para `settings.heading_font` / `settings.body_font`) genera
**CSS crudo** (una declaración `@font-face`), no HTML — por eso siempre tiene que ir envuelto
en `{%- style -%}...{%- endstyle -%}` (o `<style>...</style>`). Si se llama suelto en el
`<head>`, el navegador lo renderiza como texto plano visible en la página en vez de aplicarlo.
Ambos layouts (`theme.liquid`, `password.liquid`) ya lo hacen así — mantené el patrón si se
agregan más fuentes o layouts.

Nota de diseño (no bug): `.hero h1` en `assets/base.css` no fija `font-family` — hereda el
`--sans` del body por diseño heredado del prototipo original (igual que `prototype/styles.css`).
Solo `.big`, `.mag-hero h1` y `.story h2` usan `--serif`. Si el Hero debería usar la tipografía
de titulares (serif), es una decisión de diseño a confirmar con el producto, no un fix de código.

## Atributos `width`/`height` en `<img>`: deben ser números, no "auto"

El atributo HTML `height` (o `width`) espera un entero en píxeles — `height="auto"` es un
valor inválido que el navegador simplemente ignora (no rompe la página, pero tampoco reserva
espacio y hace inútil el atributo). Si necesitás que la imagen escale proporcionalmente,
poné las dimensiones reales del archivo en los atributos (`{{ image.width }}` / `{{ image.height }}`,
para el aspect-ratio) y el ancho/alto final deseado en `style` (`style="width:120px;height:auto"`),
como se hizo en `sections/header.liquid` para el logo. El linter de `theme check`
(`ImgWidthAndHeight`) solo verifica que el atributo *exista*, no que su valor sea válido —
no asumas que pasar ese chequeo significa que el markup es correcto.
