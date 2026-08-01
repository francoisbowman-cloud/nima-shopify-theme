# Nima (ex-PetDrop) OVL — CLAUDE.md

Tienda de dropshipping de artículos para mascotas sobre **Shopify** (Online Store 2.0). Segundo producto del sistema Atlas Commerce (junto a Aromia) — a diferencia de Aromia, este SÍ incluye venta transaccional directa (carrito, checkout, pagos).

Nombre de marca final: **Nima** (dominio `nimapets.com`). El codename `PetDrop` sigue viviendo en el nombre de la carpeta del repo, el subdominio `petdrop-9236.myshopify.com`, y el theme ID `PetDrop_OVL` en Shopify — ninguno de esos requiere renombrarse, son identificadores internos. El texto visible al cliente dentro del theme (locales, nombre del theme, comentarios) ya se rebrandeó a "Nima".

## ✅ Checklist de coherencia de diseño — verificación obligatoria (toda tarea de diseño/frontend)

Antes de dar por cerrada **cualquier** auditoría o corrección visual/frontend, repasar
`checklist-coherencia-diseno.md` (raíz del repo) punto por punto contra el trabajo hecho.
No es solo para una sesión puntual — aplica siempre que se toque `theme/sections`,
`theme/assets/base.css`, templates, o contenido de producto visible al cliente.

Reglas no negociables de ese checklist:
1. **Cobertura completa (punto 1):** generar la lista real y completa de secciones del
   theme desde el código/API antes de auditar — nunca trabajar de memoria sobre qué
   secciones existen (ya pasó una vez: una sección quedó fuera de una auditoría por no
   estar en la lista mental).
2. **Publicar y verificar en vivo (punto 4):** ninguna tarea se marca como terminada si
   el cambio quedó en un theme/borrador sin publicar, o si no se confirmó visualmente en
   el sitio real (no alcanza con preview). Ver la sección "⚠️ El theme publicado puede
   divergir del repo" más abajo para el flujo seguro de escritura (duplicar → aplicar →
   Brey publica manualmente).

## Stack

- **Shopify Online Store 2.0** theme (Liquid + JSON templates/sections, sin build step de JS/CSS).
- Vanilla JS (`theme/assets/global.js`) y CSS (`theme/assets/base.css`) — sin framework ni bundler.
- Capa de contenido "OVL" (Omni Visual Language) implementada sobre **metafields de producto**, namespace `ovl` (ver `skills/omni-visual-language/SKILL.md`).
- Dirección de arte, sistema de imágenes de catálogo y auditoría de coherencia de diseño: ver `skills/checklist-auditoria/SKILL.md` (ex `nima-image-art-direction`, renombrado el 31/07 para reflejar que también es el comando de auditoría — "correr auditoría", "checklist de diseño", "auditoría OMNI") — úsala para cualquier auditoría, tratamiento o implementación de fotografía de producto (roles de imagen, paleta/luz por categoría, ratios, tokens visuales, rendimiento y accesibilidad) y para verificar tokens/imágenes/metafields contra el estado real de la tienda. Complementa, no reemplaza, el `checklist-coherencia-diseno.md` de la raíz.
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
skills/checklist-auditoria/  # dirección de arte + comando de auditoría de diseño/imágenes (ex nima-image-art-direction)
references/        # imágenes de referencia visual
ESTADO-tienda-mascotas.md  # estado del proyecto (nivel producto, dentro de Atlas Commerce)
```

## Mapeo prototipo → theme

**Nota (23/07):** el theme publicado real ("Nima — Dirección B", ver sección siguiente)
diverge del prototipo original — Design agregó secciones y páginas nuevas. Esta tabla
refleja el estado actual del repo, ya resincronizado con lo publicado.

| Página | Plantilla Shopify | Secciones |
|---|---|---|
| Home | `templates/index.json` | hero, dual-mode-split (`.split--b`), magazine-teaser |
| Producto | `templates/product.json` | main-product (Zona 1, con variantes `--b`: swatches de color, galería en grid), product-ovl-story (Zona 2, variante `story--b`) |
| Magazine | `templates/page.magazine.json` | magazine-hero, magazine-grid, ovl-story-split |
| Catálogo | `templates/collection.json` | main-collection (grid `product-grid--b`, tarjeta destacada 2x2 vía tag `bestseller`/`nuevo`) |
| Sobre Nima | `templates/page.about-nima.json` | main-page-about (pilares M/V/V + franja de valores) |
| Contacto | `templates/page.contact.json` | main-page-contact (formulario nativo `{% form 'contact' %}`) |
| Búsqueda / Lista de colecciones | `templates/search.json` / `templates/list-collections.json` | main-search, main-list-collections — ambas reusan el mismo patrón de tarjeta (`product-grid--b` + `pcard__body`) que el Catálogo |

`feature-cards.liquid` sigue existiendo en el repo pero **ya no está en ningún template** —
quedó fuera del Home al pasar a "Dirección B". No borrado por si se reusa.

## Comandos

Requiere [Shopify CLI](https://shopify.dev/docs/themes/tools/cli). Todos los comandos se corren **dentro de `theme/`**, no en la raíz del repo:

```bash
cd theme
shopify theme dev                  # servidor local con hot reload contra tienda de desarrollo
shopify theme check                # linter de temas
shopify theme push --unpublished   # sube como tema no publicado para revisión
```

## Repositorio remoto

El repo vive en GitHub: `github.com/francoisbowman-cloud/nima-shopify-theme` (privado), rama `main` sincronizada. Se agregó para que ChatGPT (vía Codex Cloud) pueda trabajar sobre el código de forma remota y entregar cambios como pull request — Code los revisa antes de aplicarlos al theme real en Shopify (`shopify theme push` sigue siendo la única forma de que un cambio llegue a la tienda, y sigue requiriendo login OAuth interactivo, así que ese paso lo ejecuta siempre Brey).

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

## ⚠️ El theme publicado puede divergir del repo — verificar antes de auditar/tocar nada

El 23/07 se descubrió que el theme publicado (MAIN) en Shopify ya no era el que este
repo trackeaba: Design lo había reemplazado por uno nuevo ("Nima — Dirección B"),
partiendo del mismo código pero con cambios propios. `shopify theme pull` no funciona
en este entorno (requiere login OAuth interactivo), así que la única forma de detectar
esto y resincronizar es vía **Admin GraphQL API, solo lectura**:

```graphql
query { themes(first: 10) { edges { node { id name role } } } }
query { theme(id: "gid://shopify/OnlineStoreTheme/ID") {
  files(first: 250, filenames: ["*"]) { nodes { filename body { __typename ... on OnlineStoreThemeFileBodyText { content } } } }
} }
```

**Antes de cualquier auditoría o fix de theme, confirmá que `role: MAIN` corresponde al
mismo `id` que dice `ESTADO-tienda-mascotas.md`** (sección 1, línea "Theme publicado").
Si no coincide, resincronizar el repo primero (sobreescribir `theme/` con el contenido
real vía la query de arriba) antes de tocar nada — si no, se audita/corrige código que
no es el que está en producción.

**Escribir cambios de vuelta:** Shopify bloquea `themeFilesUpsert` sobre el theme MAIN/
publicado (solo permite escritura en themes no publicados). El flujo seguro: `themeDuplicate`
(mutation) → aplicar fixes con `themeFilesUpsert` sobre el duplicado → Brey previsualiza
y publica manualmente desde el admin si aprueba. Nunca commitear en el repo sin haber
verificado primero contra el theme real.

## Pendientes conocidos

- `templates/gift_card.liquid` y `templates/customers/*` no incluidos — agregar solo si se habilitan tarjetas de regalo o cuentas de cliente.
- Selección de variante sin JS cae siempre a la primera variante; con JS (`global.js`) funciona completo (galería + variantes + add-to-cart AJAX).
- Filtros de colección (por mascota/necesidad/tamaño) descritos en `docs/02_ARQUITECTURA_DE_EXPERIENCIA.md` — requieren `filter`/`facets`, no incluidos en esta primera pasada.
- Nombre de marca: **Nima** (dominio `nimapets.com`, ya definido y conectado). El `theme push` que lleva el rebrand a producción **ya se ejecutó** (ver ESTADO decisión #29) — pendiente distinto ahora: publicar el duplicado con los fixes de la auditoría del 23/07 (ver ESTADO decisión #33).

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

**Convención agregada (23/07):** para texto/fondos "claros sobre oscuro" (paneles dark,
scrims sobre imagen), no hardcodees el hex — usá las clases utilitarias ya definidas
(`.on-dark-kicker`, `.on-dark-heading`, `.on-dark-text`) o `color-mix(in srgb, var(--bg) N%, transparent)`
/ `color-mix(in srgb, var(--text) N%, transparent)` para variantes translúcidas (scrims,
overlays). Ya se aplicó en footer, `.btn`/`.btn--light`, `.option`, `.split .dark`, y los
componentes `--b` (split, teaser de magazine) — no reintroducir `rgba(43,38,33,...)` ni
`rgba(251,248,243,...)` hardcodeado, son `--text`/`--bg` disfrazados.

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
