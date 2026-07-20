# Changelog — Nima (ex-PetDrop, RFC-007, Atlas Commerce)

Formato basado en [Keep a Changelog](https://keepachangelog.com/) —
convención estándar en proyectos de software: agrupa los cambios por
tipo (Added/Changed/Fixed/Removed) en vez de una lista cronológica
plana, así es más fácil escanear "qué se rompió y se arregló" vs "qué
es nuevo" de un vistazo.

## [Unreleased] - 2026-07-19 (tanda 8 — AGENTS.md + confirmación de theme publicado)

### Added
- `AGENTS.md` en la raíz del repo: contexto de protocolo (v2 completo, embebido) y reglas
  duras para Codex Cloud — solo pull request, nunca push directo a `main`.

### Changed
- Confirmado por API que `PetDrop_OVL` es ahora el theme `MAIN` (publicado) en Shopify,
  no `UNPUBLISHED` como en la tanda anterior — el `theme push` final ya se ejecutó
  (fuera de esta sesión, por Brey). El rebrand a "Nima" ya vive en producción.

### Known issues / Pending
- Un mensaje reciente mencionó "adendas v3-v5" del protocolo y un archivo
  `PROTOCOLO-adendas-completas.md` — no se encontraron en ninguna carpeta de proyecto
  local verificada (solo existe la v2 de `PROTOCOLO-comunicacion-actores.md`). `AGENTS.md`
  deja esto marcado como gap conocido en vez de inventar contenido.
- Un mensaje reciente pidió recrear el repo de GitHub y re-aplicar la corrección
  "Atlas Comerce"→"Atlas Commerce" — ambas ya estaban hechas (tandas 6 y 7); se verificó
  contra el estado real antes de repetir el trabajo, y no se recreó el repo ni se duplicaron
  los cambios de ortografía.

## [Unreleased] - 2026-07-19 (tanda 7 — repo movido a GitHub)

### Added
- Repo publicado en GitHub como privado: `github.com/francoisbowman-cloud/nima-shopify-theme`.
  `main` local sincronizado con `origin/main`. Objetivo: habilitar que ChatGPT (vía Codex
  Cloud) trabaje sobre el código de forma remota, entregando cambios como pull request para
  que Code los revise antes de aplicarlos a Shopify.
- `gh` (GitHub CLI) instalado vía `winget` y autenticado (cuenta `francoisbowman-cloud`,
  scope `repo`) — usado para crear el repo (`gh repo create ... --source=. --remote=origin`).

### Known issues / Pending
- Primer `git push` a GitHub se colgó indefinidamente reusando una conexión HTTPS
  keep-alive stale (`Reusing existing https: connection` seguido de silencio en el body
  POST) — se resolvió reintentando (funcionó al segundo intento) tras subir
  `http.postBuffer` y fijar `http.version HTTP/1.1`. Si vuelve a pasar, reintentar
  primero antes de investigar más a fondo.
- Falta que Brey conecte Codex Cloud al repo — primer uso de este flujo, sin probar todavía.

## [Unreleased] - 2026-07-19 (tanda 6 — rebrand del theme + corrección ortográfica)

### Added
- Reconciliado el `ESTADO-tienda-mascotas.md` con toda la sesión de Chat del 19/07
  (rename a "Nima", dominio conectado, PayPal completo, envíos cerrados, catálogo
  auditado) — asignando numeración de decisiones nueva (14-26) en vez de aceptar la
  numeración que traía el documento transportado, siguiendo la regla del protocolo v2
  de evitar colisiones de numeración entre sesiones que no se vieron entre sí.

### Changed
- **Rebranding del theme `PetDrop_OVL`:** todo el texto hardcodeado "PetDrop" cambiado
  a "Nima" — `locales/es.default.json` y `en.json` ("PetDrop Journal" → "Nima Journal",
  visible en la página de blog), `config/settings_schema.json` (`theme_name`,
  `theme_author`), `config/settings_data.json` (nombre del preset), y comentarios
  internos en `assets/base.css`, `assets/global.js`, `theme/README.md`.
- Corrección ortográfica "Atlas Comerce" → "Atlas Commerce" (dos "m") en todos los
  documentos vivos de este repo: este `CHANGELOG.md`, `ESTADO-tienda-mascotas.md`,
  `CLAUDE.md`. `prompt-tienda-mascotas.md` se deja sin tocar por ser un documento
  histórico (transporte textual de una sesión pasada).
- A nivel sistema (Project "Atlas E-Commerce", fuera de este repo):
  `ESTADO-atlas-comerce.md` renombrado a `ESTADO-atlas-commerce.md` y su contenido
  actualizado; referencias corregidas en `ESTADO-aromia.md`;
  `PROTOCOLO-comunicacion-actores.md` actualizado a la v2 provista por Brey.

### Known issues / Pending
- `theme push` final del theme `PetDrop_OVL` — sigue bloqueado por falta de login
  OAuth interactivo, lo ejecuta Brey.
- Verificar en el checkout real de Shopify que el nombre visible al cliente sea
  "Nima" (no "PetDrop" ni "Atlas Commerce").
- Renombrar el Project de claude.ai "Atlas-Comerce-Lab" → "Atlas-Commerce-Lab" en la
  UI — única parte de la corrección ortográfica que sigue siendo manual.
- Sin confirmar si Brey corrigió la configuración de moneda en AutoDS (causa raíz del
  bug de precios DOP→USD, recurrente — ver historial abajo).

## [Unreleased] - 2026-07-19 (tanda 5 — rename a Nima, envíos, catálogo)

### Added
- 8 productos nuevos importados desde AutoDS como reemplazo de los 4
  archivados por falta de imagen: Calming Cat Bed, Rabbit Chew Ball, Dog Poop
  Bags (280ct), Pet Grooming Gloves, Dog Grooming Scissors, Dog Leash (17
  variantes por largo/color), Portable Pet Grooming Hammock (9 variantes por
  talla/color), Benat Pets Bath Towel — más un 9º producto no documentado en
  su momento (Dog First Christmas Bandana).
- Zona de envío "Estados Unidos" + tarifa "Free Shipping" $0.00 USD agregada
  al perfil "AutoDS Free Shipping" (el perfil general ya tenía su zona
  resuelta). Ambos perfiles de envío quedan completos y verificados por API.
- Dominio `nimapets.com` comprado por Brey y conectado a Shopify (DNS en
  Namecheap, SSL verificado).

### Changed
- **Nombre de marca cambiado de "PetDrop" a "Nima"**, con dominio
  `nimapets.com`. Decisión tomada tras evaluar que "PetDrop" revelaba el
  modelo de negocio (dropshipping) y no encajaba con el posicionamiento
  "clínico y confiable" ya definido. Candidatos descartados: Numa, Luma,
  Amble, Wilo, Kova (dominio `.com` tomado o colisión de marca en otro rubro).
- Cuenta PayPal Business completada: cuenta Empresas independiente, nombre
  de la empresa "Nima", nombre comercial "Atlas Commerce", categoría "Tiendas
  de mascotas, comida y suministros para mascotas", sitio web `nimapets.com`.
- Los 14 productos activos del catálogo se dejan publicados (Active) tras
  limpiar su contenido, en vez de revertirlos a Draft.

### Fixed
- Precios recalculados en los 8 productos nuevos (26 variantes en total).
  Se repitió el bug de conversión DOP→USD de la sesión anterior — corregidos
  dividiendo por el tipo de cambio de referencia (~58.5 DOP/USD).
- Los 8 productos nuevos llegaron publicados como "Active" en vez de "Draft"
  (saltándose la revisión humana de RFC-002) — revertidos a Draft de
  inmediato como contención, y luego vueltos a publicar tras la limpieza
  (ver "Changed" arriba).
- Desfase de conteo AutoDS↔Shopify (15 vs 13) resuelto definitivamente: no
  eran productos faltantes, eran variantes (12 productos con 1 variante +
  Anti-Splash Water Bowl con 3 variantes = 15 variantes, 13 productos).
- Auditoría de contenido del catálogo completo (14 productos activos) tras
  un hallazgo de Code de marcas de competidores reales coladas por scraping
  de AutoDS: Calming Cat Bed (marca "Love's cabin" + tabla de precios ajena),
  Rabbit Chew Ball (descripción de otra empresa, "Hamiledyi"), Dog Dental
  Bone Treats (marca "Minties"), Anti-Splash Water Bowl (imágenes incrustadas
  desde AliExpress), Dog Poop Bags 280 Counts ("540 Count" incorrecto en una
  viñeta), Dog Grooming Scissors / Dog Leash / Portable Pet Grooming Hammock
  (CSS "litepicker" y restos de plantilla eBay/BigCommerce). Todos corregidos;
  5 productos revisados ya estaban limpios.
- Bug de precio DOP→USD también en Dog First Christmas Bandana ($869.80 en
  vez de ~$15) — corregido a $14.99.

### Removed / Archived
- 4 productos sin imagen real archivados (reversible, no eliminados): Cat
  Litter Mat, Dog Birthday Hat, Dog Car Seat Cover, Dog Water Bottle.

### Known issues / Pending
- Sin confirmar si Brey corrigió la configuración de moneda dentro de AutoDS
  (causa raíz del bug de precios recurrente) — verificar antes de la próxima
  importación.
- Payoneer Checkout evaluado como método de pago secundario y descartado:
  requiere entidad legal en Hong Kong y volumen mensual mínimo de
  $10,000-$20,000, no califica.
- `theme push` final del theme `PetDrop_OVL` — sigue pendiente (ver tanda 6).

## [Unreleased] - 2026-07-18 (tanda 4 — cuenta PayPal Business)

### Added
- Cuenta PayPal Business creada como cuenta independiente (no conversión de la
  personal), bajo el nombre "Atlas Commerce" (grafía corregida, dos "m").

### Known issues / Pending
- Falta conectar la cuenta PayPal en el admin de Shopify y verificar en el checkout
  que el nombre visible al cliente sea "Nima" (actualizado — antes decía "PetDrop"),
  no "Atlas Commerce".
- ~~Corrección documental pendiente a nivel sistema: "Atlas Comerce" → "Atlas Commerce"~~
  — hecho en tanda 6.

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
