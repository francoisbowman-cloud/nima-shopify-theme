# Changelog — PetDrop (RFC-007, Atlas Comerce)

Formato basado en [Keep a Changelog](https://keepachangelog.com/) —
convención estándar en proyectos de software: agrupa los cambios por
tipo (Added/Changed/Fixed/Removed) en vez de una lista cronológica
plana, así es más fácil escanear "qué se rompió y se arregló" vs "qué
es nuevo" de un vistazo.

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
