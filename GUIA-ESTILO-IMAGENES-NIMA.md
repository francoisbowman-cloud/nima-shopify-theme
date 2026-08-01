# Guía de estilo de imágenes — Nima

Guía profesional de tamaños, ratios y tratamiento fotográfico por sección del sitio, basada en el sistema real del theme (`assets/base.css`, tema "Nima_Cowork") y en la skill `checklist-auditoria` (ex `nima-image-art-direction`) ya definida en el repo (`skills/checklist-auditoria/SKILL.md`). Esta guía no inventa reglas nuevas — traduce esa dirección de arte a specs concretas por sección, verificadas contra el CSS real.

Paleta y luz de referencia (ver skill completa para el detalle por categoría de producto): tonos cálidos — crema, marfil, arena, terracota suave — luz difusa lateral, evitar blanco clínico, negro puro y saturación alta.

---

## 1. Hero (Home)

- **Selector:** `.hero-art img`, sección `hero.liquid`
- **Ratio real del contenedor:** `78vh` de alto × columna derecha del grid (`1fr 1.15fr`) — en la práctica se comporta como panorámico ancho en desktop.
- **Recomendado:** `21:9` en desktop, variante `4:5` o `1:1` recortada para mobile (el fix de padding ya aplicado en Nima_Cowork reserva 48px/24px de aire en mobile — la imagen no debe depender de ese espacio para "respirar").
- **object-fit:** `cover`, sin `object-position` custom salvo que el producto principal quede cortado (revisar caso a caso, como se hizo con el hero actual gato/perro).
- **Peso objetivo:** 180–450 KB.
- **Foco:** debe dejar zona segura a la izquierda para el texto (`.hero-copy`), no centrar el sujeto principal ahí.

## 2. Producto — Galería principal

- **Selector:** `.gallery--b .gallery__main img`, sección `main-product.liquid`
- **Ratio:** `1:1` (fijado por CSS: `aspect-ratio:1/1`).
- **object-fit:** `cover`.
- **Miniaturas (`.gallery__thumbs--b img`):** también `1:1`, grid de 4 columnas.
- **Tratamiento:** packshot sobre fondo unificado (crema `#FBF8F3`, ya definido como estándar del pipeline Omni), producto ocupando 60–75% del cuadro, margen 8–12%, sin recortar asas/correas/etiquetas.
- **Origen mínimo:** 1600×1600 px (según pipeline Omni ya documentado: remove-bg → replace-bg → autotrim → resize 1600×1600 → shadow).
- **Peso objetivo:** 60–180 KB por imagen ya optimizada.

## 3. Producto — Zona OVL Story (Zona 2)

- **Selector:** `.story-grid--b img`, sección `product-ovl-story.liquid`
- **Ratio:** `4:5` (fijado por CSS: `aspect-ratio:4/5`).
- **object-fit:** `cover`.
- **Tratamiento:** lifestyle o editorial, no packshot — este es el bloque narrativo/emocional, coherente con los badges `ovl.emotional_benefit` / `ovl.visual_profile` del producto.

## 4. Catálogo / Colección / Búsqueda — Tarjeta de producto

- **Selector:** `.pcard__media img`, snippet `product-card.liquid`, usado en `main-collection`, `main-search`, `main-list-collections`.
- **Ratio:** `1:1` (fijado por CSS: `aspect-ratio:1/1`), excepto tarjeta destacada `.pcard--featured` que usa `min-height:260px` con `aspect-ratio:auto` (2×2 en el grid).
- **object-fit:** `cover`.
- **Atributos `<img>`:** usar `width`/`height` numéricos reales (no `"auto"` — regla ya documentada en CLAUDE.md), coherentes con el ratio 1:1 renderizado. El audit de Bloque 1 ya corrigió un caso (`product-card.liquid` tenía 400×500 en vez de 400×400).
- **Grid responsive:** 4 columnas desktop → 3 columnas ≤1000px → 2 columnas ≤800px (`.product-grid--b`).
- **Peso objetivo:** 60–180 KB.

## 5. Magazine — Hero

- **Selector:** imagen de fondo de `magazine-hero.liquid` (background-image vía CSS, no `<img>`)
- **Ratio recomendado:** `16:9` o `21:9`.
- **Tratamiento de contraste:** ya corregido (decisión #36 del ESTADO) — degradado 35%–55% negro + clases `.on-dark-kicker`/`.on-dark-heading`. Cualquier imagen nueva en esta sección debe mantener suficiente área oscura/neutra en la zona donde cae el texto, o el degradado no alcanza para el contraste WCAG.

## 6. Magazine — Grid / historia destacada

- **Selector:** `.feature--image`, `.mag-grid` en `magazine-grid.liquid`
- **Ratio:** `.feature` tiene `min-height:620px` con imagen de fondo `background-size:cover` — comportamiento equivalente a `4:5` o `3:2` según el crop real.
- **Scrim:** ya migrado en el Bloque 1 de esta auditoría a `color-mix(in srgb, var(--text) N%, transparent)` (antes `rgba(0,0,0,...)` hardcodeado) — mantener esa convención para imágenes nuevas.

## 7. Home — Split Dirección B (dual-mode-split)

- **Selector:** `.split--b__img` (lado claro), `.split--b__bgimg` (lado oscuro, fondo con scrim)
- **Ratio lado claro:** `4:3` (fijado por CSS).
- **Ratio lado oscuro:** cubre `min-height:520px` completo, `object-fit:cover`.
- **Nota de estado:** esta sección está actualmente `disabled:true` en `templates/index.json` (hallazgo del Bloque 1) — confirmar con Brey si es intencional antes de curar imágenes para ella.

## 8. Home — Teaser de Magazine

- **Selector:** `.mag-teaser__img`
- **Ratio:** `min-height:420px` sobre ancho completo del contenedor — equivalente a `21:9`/`16:9` amplio.
- **Tratamiento:** scrim + card con blur (`backdrop-filter`), mismo criterio de contraste que el Magazine Hero.

## 9. Sobre Nima

- No usa imágenes de producto — la sección `main-page-about.liquid` es tipográfica (pilares M/V/V + franja de valores). Si se agrega imagen en el futuro, usar `4:5` o `1:1` para mantener consistencia con el resto del sistema.

## 10. Blog / Artículo

- **Selector:** tarjetas de `main-blog.liquid` con imagen de fondo — mismo patrón que Magazine Grid (`background-size:cover`, scrim ya corregido a `color-mix`).
- **Ratio recomendado:** `4:5` o `3:2`.

---

## Resumen de ratios oficiales (no mezclar dentro de una misma sección)

| Sección | Ratio | object-fit |
|---|---|---|
| Hero Home | 21:9 (desktop) / 4:5 (mobile) | cover |
| Producto — galería principal | 1:1 | cover |
| Producto — Zona OVL Story | 4:5 | cover |
| Tarjeta catálogo/búsqueda | 1:1 | cover |
| Tarjeta destacada (2×2) | auto (min-height 260px) | cover |
| Magazine Hero | 16:9 / 21:9 | cover (bg) |
| Magazine Grid / historia | ~4:5 / 3:2 | cover (bg) |
| Split Home (lado claro) | 4:3 | cover |
| Split Home (lado oscuro) | libre, min-height 520px | cover |
| Teaser Magazine (Home) | ~21:9 | cover (bg) |
| Blog / Artículo | 4:5 / 3:2 | cover (bg) |

## Checklist rápido antes de subir una imagen nueva

1. ¿Coincide con el ratio oficial de esa sección? (tabla arriba)
2. ¿Fondo crema `#FBF8F3` unificado si es packshot de producto?
3. ¿Producto completo, sin cortar accesorios/etiquetas/orejas/patas?
4. ¿Origen ≥1600×1600 px para producto, ≥1000×1000 para tarjetas?
5. ¿Peso dentro del presupuesto (60–180 KB tarjeta/producto, 180–450 KB hero)?
6. ¿`alt` descriptivo y fiel (sin palabras clave forzadas)?
7. ¿`width`/`height` numéricos en el `<img>`, no `"auto"`?
8. Si hay texto superpuesto: ¿contraste WCAG verificado con el scrim real, no a ojo?

---

*Basada en `skills/checklist-auditoria/SKILL.md` (dirección de arte completa, ADN visual por categoría de producto, pipeline Omni, tokens) y en `assets/base.css` del theme Nima_Cowork (verificado 29/07/2026). Referencia complementaria, no reemplaza el `checklist-coherencia-diseno.md` de la raíz del repo.*
