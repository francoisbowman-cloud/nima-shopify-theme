# PetDrop OVL — Theme Shopify

Theme Online Store 2.0 que porta el prototipo (`prototype/*.html`) a Shopify:
secciones editables desde el Customizer, plantillas JSON y capa OVL sobre metafields.

## Estructura

```
theme/
├── layout/
│   ├── theme.liquid            # layout principal (inyecta tokens OVL desde settings)
│   └── password.liquid         # layout de la página de contraseña
├── sections/
│   ├── header-group.json       # grupo: barra de anuncio + header (editable en Customizer)
│   ├── footer-group.json       # grupo: footer
│   ├── announcement-bar.liquid
│   ├── header.liquid
│   ├── footer.liquid
│   ├── hero.liquid                 # home
│   ├── dual-mode-split.liquid      # home: Comprar / Descubrir
│   ├── feature-cards.liquid        # home: tarjetas de valor
│   ├── main-product.liquid         # producto Zona 1 (compra rápida)
│   ├── product-ovl-story.liquid    # producto Zona 2 (experiencia OVL)
│   ├── magazine-hero.liquid        # magazine
│   ├── magazine-grid.liquid        # magazine
│   ├── ovl-story-split.liquid      # magazine: split oscuro
│   ├── main-collection.liquid
│   ├── main-cart.liquid
│   ├── main-page.liquid / main-blog / main-article / main-search
│   ├── main-list-collections.liquid / main-404 / main-password
├── snippets/
│   └── product-card.liquid
├── templates/                  # *.json que ensamblan secciones
│   ├── index.json  product.json  collection.json  cart.json
│   ├── page.magazine.json      # plantilla de página "Magazine"
│   ├── page.json  blog.json  article.json  search.json
│   ├── list-collections.json  404.json  password.json
├── config/
│   ├── settings_schema.json    # colores OVL, tipografía, ancho de página
│   └── settings_data.json
├── locales/
│   ├── es.default.json         # idioma por defecto
│   └── en.json
└── assets/
    ├── base.css                # portado de prototype/styles.css + estados nuevos
    └── global.js               # menú móvil, galería, variantes, add-to-cart AJAX
```

## Mapeo prototipo → theme

| Prototipo            | Plantilla Shopify        | Secciones |
|----------------------|--------------------------|-----------|
| `index.html`         | `templates/index.json`   | hero, dual-mode-split, feature-cards |
| `product.html`       | `templates/product.json` | main-product (Zona 1), product-ovl-story (Zona 2) |
| `magazine.html`      | `templates/page.magazine.json` | magazine-hero, magazine-grid, ovl-story-split |

## Metafields OVL (namespace `ovl`)

El theme lee metafields de **producto** (tipo *Una línea de texto*, salvo indicación):

| Metafield                     | Uso en el theme |
|-------------------------------|-----------------|
| `ovl.dominant_emotion`        | Kicker de producto y badge OVL / kicker en tarjetas |
| `ovl.functional_benefit`      | Subtítulo bajo el nombre del producto |
| `ovl.emotional_benefit`       | Badge OVL en Zona 2 |
| `ovl.visual_profile`          | Badge OVL en Zona 2 |

Crear en **Configuración → Metafields personalizados → Productos** con el namespace `ovl`
y esas claves. Ver `docs/04_MODELO_DE_CONTENIDO.md` y `docs/05_IMPLEMENTACION_SHOPIFY_AUTODS.md`
para el conjunto completo de campos previstos (story_id, risk_level, etc.).

## Previsualizar / desarrollar

Requiere [Shopify CLI](https://shopify.dev/docs/themes/tools/cli):

```bash
cd theme
shopify theme dev            # servidor local con hot reload contra una tienda de desarrollo
shopify theme check          # linter de temas
shopify theme push --unpublished   # sube como tema no publicado para revisión
```

La carpeta del tema es `theme/` (no la raíz del repo), por eso los comandos se corren dentro de `theme/`.

## Configuración inicial en Shopify

1. **Navegación**: crear el menú `main-menu` con: Comprar (`/collections/all`),
   Descubrir (página Magazine), Colecciones, Ayuda.
2. **Página Magazine**: crear una página y asignarle la plantilla `page.magazine`.
3. **Metafields OVL**: definir el namespace `ovl` (arriba) y cargar datos por producto.
4. **Colores/tipografía**: ajustables en Customizer → Configuración del tema.

## Pendientes conocidos (fuera del alcance de esta conversión)

- `templates/gift_card.liquid` y `templates/customers/*` no incluidos: agregar si se
  habilitan tarjetas de regalo o cuentas de cliente.
- Selección de variante sin JS cae siempre a la primera variante; con JS funciona
  (galería + variantes + add-to-cart AJAX vía `assets/global.js`).
- Filtros de colección (por mascota/necesidad/tamaño) descritos en la arquitectura:
  requieren `filter`/`facets` — no incluidos en esta primera pasada.
