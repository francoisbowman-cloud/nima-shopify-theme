# Changelog — PetDrop (RFC-007, Atlas Comerce)

Formato basado en [Keep a Changelog](https://keepachangelog.com/) —
convención estándar en proyectos de software: agrupa los cambios por
tipo (Added/Changed/Fixed/Removed) en vez de una lista cronológica
plana, así es más fácil escanear "qué se rompió y se arregló" vs "qué
es nuevo" de un vistazo.

## [Unreleased] - 2026-07-17 (tanda 3 — decisión de moneda)

### Changed
- Moneda de la tienda cambiada de DOP a USD en el admin de Shopify, siguiendo la
  recomendación de `docs/07_INVESTIGACION_DECISIONES_DE_NEGOCIO.md` (sección 3).
  Confirmado por API de solo lectura tras el cambio.

## [Unreleased] - 2026-07-17 (tanda 2 — auditoría técnica + investigación de negocio)

### Fixed
- `sections/header.liquid`: el logo tenía `height="auto"`, un valor inválido para
  ese atributo HTML (debe ser un entero). El linter de `ImgWidthAndHeight` no lo
  detectaba porque solo chequea que el atributo exista, no que su valor sea válido.
  Se corrigió usando las dimensiones reales de la imagen + `style="width:120px;height:auto"`.

### Added
- `docs/07_INVESTIGACION_DECISIONES_DE_NEGOCIO.md`: investigación de las 4 decisiones
  de negocio pendientes (imágenes faltantes, desfase de conteo AutoDS→Shopify,
  recomendación de moneda DOP vs USD, propuesta de mercados/pagos/políticas), más
  la lista final de acciones manuales para Brey.
- Auditoría técnica completa: se revisaron todos los templates/secciones no
  chequeados en la tanda anterior (Magazine, Catálogo, carrito, header, footer,
  blog, búsqueda, 404) — la limpieza de `base.css` de la tanda 1 no rompió nada ahí.
  Se verificó también que `es.default.json`/`en.json` tienen las mismas 36 claves
  y que ninguna clave de traducción usada en el Liquid del theme está ausente.

### Investigated (hallazgos confirmados vía API de solo lectura contra
  `petdrop-9236.myshopify.com`, sin escribir nada)
- Las 4 fichas sin imagen (Cat Litter Mat, Dog Birthday Hat, Dog Car Seat Cover,
  Dog Water Bottle) tienen `images: []` en Shopify — cero imágenes cargadas, no es
  un problema de theme ni de caché.
- La tienda tiene 13 productos en total (9 Draft + 4 Archived), no 11 Draft + 4
  Archived como decía el registro anterior. De los 15 supuestamente importados en
  AutoDS, 2 no llegaron a Shopify en ningún estado — lista completa de los 13
  existentes en `docs/07_...md` para cruzar contra AutoDS.
- Shopify Payments no está disponible para comercios registrados en República
  Dominicana (confirmado en la documentación pública de Shopify) — aplica sin
  importar la moneda de la tienda; hace falta un gateway de terceros (PayPal o
  Payoneer Checkout recomendados).

### Known issues / Pending (sin cambios respecto a la tanda anterior salvo lo de arriba)
- Moneda, mercados, métodos de pago y políticas: recomendación lista en
  `docs/07_INVESTIGACION_DECISIONES_DE_NEGOCIO.md`, decisión y ejecución pendientes de Brey.
- `theme push` sigue sin poder ejecutarse desde este entorno (requiere login OAuth interactivo).

## [Unreleased] - 2026-07-17

### Added
- Definiciones de metafields `ovl.*` (`dominant_emotion`,
  `functional_benefit`, `emotional_benefit`, `visual_profile`)
  cargadas en 9 productos activos/draft.
- Theme `PetDrop_OVL` subido a Shopify como borrador (unpublished),
  ID `198713933905`, tienda `petdrop-9236.myshopify.com`.
- Nueva paleta de color "clínico y confiable" (acento `#3E8FA6`, texto
  `#1F2E33`, fondos/bordes en tonos teal suaves) reemplazando el verde
  OVL original.
- Tipografía de encabezados actualizada a Georgia Pro (`georgia_pro_n4`).

### Changed
- 4 descripciones de producto reescritas por contener basura de
  scraping (tablas de comparación de Amazon, botones "Add to Cart"
  residuales): Dog Poop Bag Holder, Dog Birthday Hat, Dog Water
  Bottle, Foam Soccer Balls Cat Toys.
- Regla arquitectónica nueva (documentada en `CLAUDE.md`): los custom
  properties de color/tipografía viven solo en los layouts
  (`theme.liquid`/`password.liquid`), nunca en `base.css`.

### Fixed
- Font handle inválido en `settings_schema.json` (`"georgia"` →
  `"georgia_pro_n4"`).
- Coma faltante en `settings_data.json` (error de sintaxis JSON tras
  edición manual).
- Nombre de sección demasiado largo en `product-ovl-story.liquid`
  (excedía el máximo de 25 caracteres del schema).
- Bug: `@font-face` renderizándose como texto plano visible en pantalla
  (`font_face` fuera de un bloque `<style>`) en `theme.liquid` y
  `password.liquid`.
- Bug: el color de acento no se actualizaba en pantalla — variables
  duplicadas en `base.css` pisaban los valores del Customizer.
- 3 instancias de `ImgWidthAndHeight` corregidas (atributos
  `width`/`height` agregados a tags `<img>`).

### Removed / Archived
- 4 productos archivados (no eliminados) por no encajar en el nicho o
  estar mal importados: Selenium (suplemento humano), Dog T-Shirt "I
  Love My Mom", Reflective Service Dog Patches, Prime Saltwater
  Conditioner.
- 11 productos importados desde AutoDS fueron revertidos de `Active` a
  `Draft` tras detectarse que se habían publicado sin pasar por
  revisión humana (RFC-002) — medida de contención de riesgo.

### Known issues / Pending
- 4 productos sin imagen real (Cat Litter Mat, Dog Birthday Hat, Dog
  Car Seat Cover, Dog Water Bottle) — requieren resincronización desde
  AutoDS.
- Desfase de conteo: 15 productos importados en AutoDS, solo 11
  sincronizados a Shopify — causa sin investigar todavía.
- Moneda de la tienda en DOP; mercado de envío es EE.UU. — decisión
  pendiente (DOP vs USD).
- Mercados de envío, métodos de pago, políticas de devolución sin
  configurar.
- Nombre de marca y dominio real aún pendientes (codename `PetDrop`).
- 2 fuentes marcadas como deprecated por Shopify (`georgia_pro_n4`,
  `helvetica_n4`) — funcionan bien, evaluar migración a futuro, sin
  urgencia.
