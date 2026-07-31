# Changelog — Nima (ex-PetDrop, RFC-007, Atlas Commerce)

Formato basado en [Keep a Changelog](https://keepachangelog.com/) —
convención estándar en proyectos de software: agrupa los cambios por
tipo (Added/Changed/Fixed/Removed) en vez de una lista cronológica
plana, así es más fácil escanear "qué se rompió y se arregló" vs "qué
es nuevo" de un vistazo.

## [Unreleased] - 2026-07-29 (tanda 14 — diagnóstico formal del sistema de diseño vía Omni + OVKB)

**Actor:** Code. Solo diagnóstico, no se implementó nada nuevo (instrucción explícita de
Brey de no implementar salvo correcciones triviales) — el único cambio de código de esta
tanda ya estaba commiteado antes de este diagnóstico (ver tanda 13).

### Investigated
- **Re-ejecutado `generate_web_design_system` sobre `theme/`** (ya con la evolución de la
  tanda 13 empujada a GitHub): confirma que la paleta/tipografía real de Nima se lee
  correctamente (`#8a5a3b`/`#fbf8f3`/`#2b2621`, confianza "high", trazado a
  `settings_data.json`) — no hay drift entre lo que Omni detecta y lo que el theme
  realmente usa. Detecta como brecha pendiente: **20 colores literales sin tokenizar**
  (`#fff`×12, `rgba(0,0,0,.55)`×3, `#c0392b`×2, etc.) y **20 valores de spacing en `px`
  crudo** (`40px`×20, `24px`×18, `16px`×17, `80px`×14...), ninguno con reemplazo
  automático propuesto. Faltan también 3 componentes sin contrato de estados formal:
  `Input`, `Feedback`, `Navigation`.
- **Consultado `query_omni_knowledge`** (corpus `omni.professional-foundation` v1.0.0, 14
  objetos): devolvió 9 principios/patrones de composición editorial general (jerarquía
  antes que disrupción, grid roto controlado, stack editorial responsive, overlap
  controlado) — el corpus es de composición visual genérica, no tiene dominio e-commerce
  específico. Aplicables como criterio de revisión para Magazine/hero split, no como
  checklist técnico.
- **Probada la herramienta nueva `preview_targeted_web_composition`** (reportada por otro
  canal como ya compatible con Shopify OS2, con 14 templates detectados y
  Header/Collection/Product/Cart en `SAFE`): al ejecutarla acá contra `theme/` con
  `authorized_surfaces:["index","collection","product","cart"]` el resultado real fue
  **0 zonas de composición, 0 cambios, los 47 archivos del theme marcados `UNKNOWN`**
  ("no evidence that this source participates in the active product"). Ya no confunde el
  prototipo viejo (mejora real sobre el bug de la tanda 13), pero tampoco logra trazar qué
  archivo arma qué página real — el `SAFE/SAFE/SAFE` que devuelve es consecuencia de no
  haber compuesto nada, no de una composición validada. **No se pudo reproducir el reporte
  de "14 templates READY"** con los parámetros probados — queda como hallazgo sin
  verificar, no como hecho confirmado.

### Pending — decisión de Brey, no bloqueante
- Tokenizar los ~20 colores/spacing literales detectados arriba en `base.css` — mismo
  patrón de riesgo bajo que la tanda 13 (normalización 1:1, sin cambio visual). Identificado
  como el siguiente cambio de mayor impacto, pendiente de confirmación antes de ejecutar.
- Sigue sin resolverse cuál de los tres duplicados de theme sin publicar priorizar (ver
  ESTADO sección 7) — no cambia con esta tanda.

## [Unreleased] - 2026-07-29 (tanda 13 — evolución del sistema visual vía Omni, motor de composición no sirve para Liquid)

**Actor:** Code.

### Investigated — bug real en Omni, no aplicado
- Se probó `preview_web_composition`/`apply_web_composition` (Omni Web Composition Engine)
  apuntando al repo completo (`repository_url`): el motor necesita páginas HTML de un solo
  archivo para poder "componer". Como este theme arma cada página desde
  `templates/*.json` + `sections/*.liquid` + `snippets/*.liquid`, no encontró nada así y
  cayó a usar los 3 únicos HTML monolíticos del repo — `prototype/index.html`,
  `magazine.html`, `product.html` — que además siguen con la marca vieja "PetDrop" y la
  paleta descartada (verde `#0c6b45`, fondo blanco puro). Confirmado el diagnóstico
  repitiendo la llamada con `project_subdirectory:"theme"`: ahí no detecta ninguna página
  parseable y colapsa Home/Magazine/Producto/Catálogo en un solo arquetipo genérico
  "catalog" sobre `assets/base.css`. **No se aplicó ese change_set** — hubiera reescrito
  solo archivos muertos (el prototipo, no el theme real) con datos de marca incorrectos,
  cero efecto en `nimapets.com`.
- `generate_web_design_system`/`audit_web_project` sí funcionan bien contra este repo
  (leen los tokens reales desde `config/settings_data.json`) — la propuesta de evolución
  que generaron se subió a Claude Design (proyecto "Nima") como referencia, sin tocar la
  captura fiel existente del sistema real.

### Changed — evolución manual del sistema visual (`theme/assets/base.css`)
Ante la limitación de arriba, se aplicó a mano un alcance acotado y de bajo riesgo,
verificado con `shopify theme check` (0 errores nuevos):
- **Capa de fundamentos nueva**: `--radius-sm/md/lg/pill`, `--shadow-sm/md`,
  `--focus-ring` — no redeclara ningún token de color/tipografía existente (respeta la
  regla de `CLAUDE.md` sobre `:root` en `base.css`).
- **Foco visible global** (`:focus-visible{box-shadow:var(--focus-ring)}`) — gap de
  accesibilidad real que no existía antes (botones, inputs, swatches no tenían ningún
  estado de foco explícito).
- **19 valores de `border-radius` literales normalizados** a los tokens nuevos — mismo
  valor visual exacto (6px→`--radius-sm`, 8px→`--radius-md`, 12px→`--radius-lg`,
  999px→`--radius-pill`), cero cambio de layout.
- **Tipografía fluida** (`clamp()`) en 5 títulos que seguían en `px` fijo: `.feature h2`,
  `.buy h1`, `.mag-teaser__h`, `.split--b__h`, `.story--b__h` — el valor máximo del
  `clamp()` es el mismo `px` original, así que en desktop se ve idéntico; solo mejora el
  comportamiento en viewports intermedios.
- Sombra sutil en hover de tarjetas de catálogo (`.pcard:hover`) — antes solo cambiaba
  el color de borde, sin feedback de profundidad.
- **No se tocaron** colores de marca, contenido, ni se recompuso el layout de ninguna
  página — eso requiere QA visual página por página, no algo para hacer a ciegas contra
  una tienda en producción.

### Cómo se aplicó
Subido vía Admin GraphQL API (`themeFilesUpsert`) a un **nuevo theme duplicado sin
publicar**, "Nima — Evolucion fundamentos (Code)" (ID `199238025297`, duplicado del MAIN
`198963363921`) — Shopify bloquea escritura por API sobre el theme publicado. Pendiente
que Brey lo previsualice y publique.

### Pending
- Publicar (o no) el duplicado `199238025297`.
- Sigue sin resolverse qué hacer con el theme `Nima_Cowork` (`199221641297`) de la tanda
  anterior — ahora hay **tres** duplicados sin publicar en paralelo
  (`199060881489` fix de padding, `199221641297` Nima_Cowork, `199238025297` esta tanda),
  todos partiendo del mismo MAIN. Brey debe decidir cuál publicar y en qué orden, o si
  conviene consolidarlos en uno solo antes de publicar — publicarlos fuera de orden podría
  hacer que uno pise el trabajo de otro.

## [Unreleased] - 2026-07-29 (tanda 12 — Cowork, optimización integral, theme Nima_Cowork)

**Actor:** Cowork. **No se hizo ningún `git commit`/`push`** (autoridad exclusiva de Code) —
los cambios de theme viven en el theme Shopify `Nima_Cowork` (UNPUBLISHED, no en el repo
todavía), y los de producto directo en Shopify Admin. Code debe revisar y decidir si
sincroniza el repo con este theme antes de commitear.

### Discrepancia encontrada vs. `ESTADO-tienda-mascotas.md` (corregir en sección 6)
- El catálogo activo real tiene **25 productos**, no 14: 11 productos nuevos (vendor "Nima")
  se agregaron el 26/07/2026 sin documentar en el ESTADO ni auditar nunca.
- El theme MAIN publicado real es `198963363921` ("Nima — Fix contraste Magazine Hero").
  El fix de padding mobile del Hero (`199060881489`, ESTADO decisión #45) **seguía sin
  publicarse** — no se publicó en esta sesión (Cowork no tiene esa autoridad); en cambio
  se fusionó el fix a un theme de trabajo nuevo (ver abajo).
- Existe un theme `Development (d0428a-DESKTOP-2KBPIGU)` (`199058718801`) no documentado
  en el ESTADO — no se tocó, solo se detectó.
- Los productos "Reflective Service Dog in Training Patches" y "Dog Clothes I Love My Mom"
  mencionados en el ticket original **no existen en la tienda** — no se encontraron
  imágenes procesadas en el repo ni en el workspace. Tratado como dato desactualizado del
  ticket, no como pendiente real.

### Added
- **Theme `Nima_Cowork`** (`gid://shopify/OnlineStoreTheme/199221641297`, UNPUBLISHED)
  creado como duplicado de trabajo del MAIN (`198963363921`), con el fix de padding mobile
  del Hero (`.hero-copy{padding:48px 24px}` en `@media(max-width:800px)`, decisión #45)
  ya fusionado en `assets/base.css`. A partir de acá, todo el trabajo de auditoría/fix de
  esta tanda se hizo sobre este theme, no sobre el MAIN.
- `GUIA-ESTILO-IMAGENES-NIMA.md` (raíz del repo) — guía de estilo de imágenes por sección
  (ratios oficiales, object-fit, pesos objetivo, checklist previo a subir imagen), basada
  en `skills/nima-image-art-direction/SKILL.md` y verificada contra el CSS real del theme.
- `PLAN-VENTAS-Y-TRAFICO-NIMA.md` (raíz del repo) — plan de precios/upsell/checkout y plan
  de SEO/redes/Magazine, con prioridad de bajo costo/alto impacto para operador único.

### Fixed (aplicado sobre `Nima_Cowork`, vía `themeFilesUpsert`)
- `snippets/product-card.liquid`: atributo `height="500"` no coincidía con el
  `aspect-ratio:1/1` real de `.pcard__media` (era 400×500) — corregido a 400×400.
- `assets/global.js`: comentario de cabecera "PetDrop theme" → "Nima theme".
- `sections/magazine-grid.liquid` y `sections/main-blog.liquid`: scrims con
  `rgba(0,0,0,...)` hardcodeado migrados a `color-mix(in srgb, var(--text) N%, transparent)`,
  siguiendo la convención ya establecida en CLAUDE.md.
- 6 productos con contenido de scraping/marca de competidor real limpiado (ver detalle
  en sección "Contenido de producto" abajo) — aplicado directo en Shopify Admin
  (`productUpdate`), no en el repo.

### Contenido de producto corregido (Shopify Admin, catálogo real)
Los 6 productos son parte de la tanda nueva del 26/07, nunca auditada:
- **Bird Chewing Toy (Parrot):** marca de competidor real "Kintor" repetida en toda la
  descripción — reescrita.
- **Dog Bed Crate Pad:** marca "Mora Pets" + referencia a tienda de Amazon ajena — reescrita.
- **Pet Memorial Picture Frame:** marca "KCRasan" en título/bullets — reescrita, se
  conservó el poema (contenido genérico).
- **Critter Nation (jaula):** branding completo del fabricante real "MidWest Homes for
  Pets" — reescrita a specs neutras.
- **Waterproof Pet Feeding Mats:** fragmento de marca ajena mal raspado + tablas HTML de
  scraping — reescrita.
- **Feather Teaser Cat Toy / 1 Teaspoon Measuring Spoon:** tablas HTML comparando SKUs
  ajenos de Amazon — reescritas.

### Flaggeado — sin tocar, requiere decisión de Brey
- **1 Teaspoon Measuring Spoon ($5.25, sin imagen):** nicho ambiguo, candidato a archivar.
- **Critter Nation ($404.82) y Original Elevated Dog Bed ($165.01):** precios ~10-25x el
  resto del catálogo — confirmar si es error de importación (mismo patrón que el bug
  DOP→USD ya visto con el Christmas Bandana) o intencional.
- **Título "Critter Nation by [espacio vacío] Double Unit...":** título roto, falta el
  nombre del fabricante donde debería ir texto — no corregido (cambio de título, no de
  descripción, se dejó para no tocar más de lo pedido).
- **Sección `dual-mode-split.liquid` está `disabled:true`** en `templates/index.json` —
  no documentado como decisión intencional en el ESTADO, confirmar con Brey.
- **Copy de envío gratis "desde $50"** en `announcement-bar.liquid` — no confirmado como
  política real, no se tocó.
- 5 productos con metafields OVL incompletos (falta `functional_benefit`/`visual_profile`
  en Portable Hammock, Dog Leash, Grooming Gloves, Dog Poop Bags 280ct) — no corregido,
  implica escribir copy nuevo.

### Verified
- Bug histórico "Agotado": `inventoryPolicy: CONTINUE` confirmado en variantes de
  Anti-Splash Water Bowl, Dog Leash (17 variantes) y Critter Nation — sigue resuelto.
- Locales (`es.default.json`/`en.json`): sin placeholders viejos tipo "€50" o cantidades
  desactualizadas.
- Los 22 templates JSON del theme apuntan a secciones existentes, sin referencias rotas.
- El bullet de "highlights" genérico (ESTADO sección 6, tanda 19/07) no se repite en los
  14 productos originales — ya estaba corregido de una sesión anterior.
- Badges OVL (`ovl.dominant_emotion`/`ovl.emotional_benefit`) de los 25 productos activos
  coinciden temáticamente con su descripción.

## [Unreleased] - 2026-07-26 (tanda 11 — verificación visual del recorte de Hero mobile)

### Verified — cierra pendiente de la tanda 10
- **Recorte horizontal del Hero en mobile (pendiente desde la tanda anterior) confirmado
  sin problema — no corta a las mascotas.** El browser pane, que había fallado toda la
  sesión anterior, funcionó esta vez. Se navegó a `nimapets.com/?preview_theme_id=199060881489`
  (Shopify mantiene el preview activo vía cookie aunque la URL visible se limpie a la raíz)
  y se confirmó por inspección de estilos computados que ese duplicado sirve
  `.hero-copy{padding:48px 24px}` en mobile — verificado también leyendo `assets/base.css`
  directo de ambos themes vía Admin API (el MAIN publicado `198963363921` no tiene esa
  regla, el duplicado `199060881489` sí). El screenshot del navegador (`computer` tool)
  siguió fallando ("Browser pane is not displayed") — en su lugar se descargó la imagen
  real del Hero (`01-hero.png`, 1400×933) y se recortó localmente con Pillow replicando
  la matemática exacta de `object-fit:cover` a 375px de viewport (~20% recortado por lado).
  El recorte simulado muestra al gato y al perro completos — solo se pierde fondo
  decorativo (jarrón/planta a la izquierda, cortina a la derecha). Conclusión: no hace
  falta ajustar `object-position`, el fix de padding de la tanda 10 es suficiente tal
  como está.

### Verified — cierra pendiente histórico
- **Checkout real confirmado con el nombre "Nima" visible al cliente.** Se agregó un
  producto de prueba al carrito (Anti-Splash Water Bowl) y se avanzó hasta la pantalla de
  checkout sin llenar ni enviar ningún dato personal o de pago — título de pestaña
  "Checkout - Nima", header "Nima Checkout", método de pago PayPal visible, sin rastro de
  "PetDrop" ni "Atlas Commerce" en ningún punto del flujo.

### Verified — cierra pendientes históricos adicionales
- **"Adendas v3-v5" del protocolo confirmadas inexistentes** — grep completo de
  `PROTOCOLO-comunicacion-actores.md` y de toda la carpeta `Atlas E-Commerce/` sin ningún
  resultado. No hace falta seguir buscando salvo que Brey aporte una ubicación concreta.

### Investigated
- **Handle de Instagram `@nimapets` ya existe** — pertenece a una cuenta llamada "NIMA
  PETS". No se pudo confirmar de quién es (Instagram bloqueó la carga completa sin sesión
  iniciada). No se probaron más plataformas de forma automatizada para evitar scraping
  contra los términos de servicio — queda para que Brey lo confirme manualmente.

### Pending
- Sigue pendiente que Brey publique manualmente el duplicado `199060881489` — ya no hay
  ningún ajuste de código adicional bloqueando esa publicación.
- Se preserva explícitamente la contraseña del sitio activa — Brey pidió no tocarla en
  esta tanda (26/07).
- Tratamiento de las 5 imágenes de producto crudas de AutoDS puesto en pausa — Brey va a
  traer un plan propio antes de que se ejecute nada (`imagetoolkit` o `image-server/`).
- Confirmar de quién es la cuenta `@nimapets` en Instagram.

## [Unreleased] - 2026-07-25 (tanda 10 — bug "Agotado" en catálogo + exploración de tratamiento de imagen)

### Fixed — rompe la experiencia de compra
- **Todo el catálogo mostraba "Agotado" en el storefront publicado**, pese a que el Admin
  API confirmaba inventario real (`availableForSale: true`, `inventoryPolicy: CONTINUE`
  en las variantes probadas) y el código del theme (`main-product.liquid`) resultó
  idéntico byte a byte entre el repo y el theme MAIN — descartado bug de código o de
  caché. Causa raíz real: **el mercado primario de la tienda (República Dominicana) no
  tenía ninguna zona de envío configurada** — solo existía zona de envío para Estados
  Unidos. Cualquier visita cuya sesión resolviera al mercado por defecto (RD) veía todo
  como agotado, sin importar el stock real. Confirmado leyendo el JSON público del
  storefront (`/products/<handle>.js` → `available: false`), no solo el HTML — y
  reproducido con y sin la contraseña del sitio, descartando también un problema de
  caché de página. La API de Shopify no expone ningún mutation para cambiar el mercado
  primario (`MarketUpdateInput` no tiene ese campo) — resuelto manualmente por Brey en
  Configuración → Mercados (RD a Borrador, Estados Unidos como predeterminado). Verificado
  en vivo tras el cambio: `available: true`, botón "Add to cart" habilitado.

### Fixed — imagen de fondo del Hero (Home)
- **`.hero-copy` no reducía su padding en mobile** (`assets/base.css`): mantenía
  `padding:80px ... 80px` fijo (heredado del valor desktop) dentro del breakpoint
  `@media(max-width:800px)`, generando un bloque de ~545px de alto (padding + kicker +
  h1 + párrafo + botón) antes de llegar a la imagen del Hero — la "franja vacía de fondo
  crema" reportada por Brey. Auditadas las 22 secciones del theme (cobertura completa vía
  skill `director-de-diseno`) — solo 4 usan imagen de fondo (`hero.liquid`,
  `magazine-hero.liquid`, `magazine-grid.liquid`, `main-blog.liquid`); las otras 3 no
  tenían el mismo problema (altura controlada por padding/min-height razonable, no por un
  padding vertical duplicado sin breakpoint). Corregido agregando
  `.hero-copy{padding:48px 24px}` al breakpoint mobile existente.
- **Pendiente sin resolver, requiere verificación visual de Brey:** el posible recorte
  horizontal de la foto del Hero (`01-hero.png`, gato + perro lado a lado, 1400×933)
  en viewports angostos — con `object-fit:cover` + `object-position:center` por defecto,
  el cálculo geométrico da hasta ~45% de recorte de ancho a 375px de viewport. No se pudo
  confirmar por captura de pantalla si esto corta a las mascotas (la herramienta de
  screenshot del navegador falló durante toda la sesión) — verificado solo por inspección
  de DOM/rects, no visualmente.
- **Tratamiento de imagen de producto** (Portable Pet Grooming Hammock, como caso de
  prueba antes de escalar a las otras 4 fotos crudas de AutoDS pendientes de la tanda 9):
  se probó la herramienta MCP `imagetoolkit` para recorte + quitar fondo + color de fondo
  del tema + ajuste 1:1. Encontrados 2 límites reales: (a) solo acepta `input_path` como
  URL pública, sin soporte para archivos locales — se resolvió parcialmente usando los
  parámetros de recorte del CDN de Shopify (`?width=&height=&crop=left`) sobre la imagen
  ya pública en vez de subir un recorte propio; (b) no había forma de bajar el resultado
  tratado — resuelto a mitad de sesión con una tool nueva del mismo servidor,
  `get_result_base64` (con la salvedad de que hay que mantener el archivo bajo ~35KB o la
  respuesta se trunca). El resultado final quedó en el scratchpad de la sesión, no en el
  repo ni subido a Shopify — decisión pendiente de si vale la pena terminar este camino o
  usar directamente el servicio propio (`image-server/`, ver abajo).
- Un intento previo de subir el recorte directo a Shopify vía `stagedUploadsCreate` +
  POST a Google Cloud Storage falló de forma reproducible: la política firmada que
  devuelve el API de Shopify no incluye `x-goog-credential` entre las condiciones, pero
  GCS exige ese campo — un bug del lado de Shopify, no algo corregible ajustando la
  request. Documentado en memoria (`shopify_staged_upload_signature_bug`).

### Added
- `image-server/` (FastAPI + Pillow + rembg): servicio propio de tratamiento de imagen
  para reemplazar la dependencia de `imagetoolkit` — recibe el archivo directo por HTTP
  (multipart) y devuelve el resultado directo en la respuesta, sin el rodeo de URLs
  públicas intermedias ni el límite de tamaño de `imagetoolkit`. Endpoints: `/crop`,
  `/remove-bg`, `/replace-bg`, `/resize`, `/palette`, `/process` (pipeline encadenado).
  Documentado en `image-server/README.md`, incluye instrucciones de deploy en Railway.
  **Todavía no desplegado.**

### Cómo se aplicó
El fix de `.hero-copy` se subió vía Admin GraphQL API (`themeFilesUpsert`) a un **theme
duplicado sin publicar**, "Nima — Fix hero mobile padding (Code)" (ID `199060881489`,
duplicado desde el MAIN `198963363921`) — Shopify bloquea escritura por API sobre el
theme publicado. Pendiente que Brey lo previsualice y publique.

### Aclarado (sin cambios, solo diagnóstico)
- El email público de la página de Contacto (`hola@nima.pet`) es un alias de marca, no
  el Gmail real de Brey — ese último solo lo usa Shopify internamente para notificaciones
  y nunca se expone al público.
- Confirmado que la protección por contraseña del sitio (`/password`) sigue activa —
  cualquier visita nueva sin la contraseña cae ahí, incluida la verificación en vivo del
  bug de "Agotado" en esta misma tanda.

## [Unreleased] - 2026-07-23 (tanda 9 — auditoría del theme "Nima — Dirección B")

### Contexto
El theme que este repo trackeaba (`PetDrop_OVL`) ya no era el publicado — Design lo
había reemplazado por uno nuevo, "Nima — Dirección B (Design)" (ID `198916800593`,
`role: MAIN`), construido a partir del mismo código base pero con paleta cálida propia
y páginas nuevas (Sobre Nima, Contacto, teaser de Magazine). Se resincronizó el repo
leyendo el theme real vía Admin GraphQL API (`theme.files`, solo lectura) — `shopify
theme pull` no es viable en este entorno (requiere login OAuth interactivo).

### Fixed — rompe la experiencia de compra
- **Selector de color roto en productos con 2+ opciones** (`sections/main-product.liquid`):
  el bloque de swatches iteraba sobre `product.variants` en vez de sobre valores de color
  únicos. En productos con Color + otra opción (Dog Leash: 17 variantes por largo/color;
  Portable Pet Grooming Hammock: 9 variantes por talla/color) esto generaba círculos de
  color duplicados sin indicar la segunda opción, dejando al comprador sin forma de elegir
  talla. Restringido el swatch a productos donde Color es la única opción; el resto cae al
  selector genérico por variante (ya funcional, muestra el nombre completo, ej. "Terracota
  / M").
- **Galería de producto sin retorno a la imagen principal** (`sections/main-product.liquid`):
  el loop de miniaturas usaba `offset: 1`, excluyendo la primera imagen de la tira de
  miniaturas. Una vez el comprador hacía clic en otra miniatura, no había forma de volver
  a ver la imagen principal sin recargar la página. Quitado el offset.
- **Formulario de contacto en inglés roto** (`locales/en.json`): faltaba el bloque
  `"contact"` completo (presente en `es.default.json`) — los campos del formulario
  mostraban literalmente las claves de traducción (`contact.name`, `contact.email`, etc.)
  en vez de las etiquetas ("Name", "Email", "Message", "Send message").
- **Logo del header con `height="auto"`** (`sections/header.liquid`): regresión — el fork
  de Design partió de una versión del código anterior a este fix. Corregido igual que antes
  (dimensiones reales + `style="width:120px;height:auto"`).
- **3 imágenes sin `width`/`height`** (`sections/dual-mode-split.liquid` x2,
  `sections/magazine-teaser.liquid` x1) — nuevas en el fork de Design, no tenían los
  atributos. `shopify theme check` pasó de 7 errores a 0.
- Swatches y pills de variante sin estado visual para "sin stock" — se veían igual
  disponibles que agotadas salvo por no poder seleccionarlas. Agregado estilo disabled
  (opacidad + diagonal tachada en swatches, tachado en pills).

### Fixed — responsive
- **Grid del blog no colapsaba en mobile** (`sections/main-blog.liquid`): un `style`
  inline (`grid-template-columns:1fr 1fr`) pisaba el breakpoint de `.mag-grid` que
  colapsa a 1 columna en pantallas angostas, dejando 2 columnas fijas y cramped en
  mobile. Movido a una clase dedicada (`.mag-grid--blog`) que sí respeta el breakpoint.

### Changed — consistencia visual / duplicación
- Unificados `main-search.liquid` y `main-list-collections.liquid` al mismo patrón de
  tarjeta que ya usa el Catálogo (`product-grid--b` + `pcard__body`) — antes usaban un
  grid/card distinto (`product-grid` viejo), dando resultados visualmente distintos
  para el mismo tipo de contenido en 3 pantallas diferentes.
- Eliminado el bloque CSS viejo de `.pcard`/`.pcard__media`/`.product-grid` que había
  quedado parcial y silenciosamente superpuesto (misma clase, dos definiciones no
  contiguas) con el bloque nuevo "Catálogo — Dirección B" — sin cambio visual, menos
  superficie para bugs futuros.
- Colores hardcodeados que coincidían exactamente con variables de tema (`#EDE0D0`,
  `#FBF8F3`, `rgba(43,38,33,...)`, `rgba(251,248,243,...)`) migrados a
  `var(--bg)`/`var(--text)`/`var(--green2)` vía clases reutilizables (`.on-dark-kicker`,
  `.on-dark-heading`, `.on-dark-text`) y `color-mix()` para las variantes translúcidas —
  incluye el footer, los botones (`.btn`/`.btn--light`), las pills de variante
  (`.option`), y el split oscuro de Magazine (`ovl-story-split`, que antes usaba negro
  puro en vez de `--text`). Antes, cambiar la paleta en el Customizer no afectaba estos
  elementos.

### Changed — limpieza
- `settings_schema.json`: `theme_name`/`theme_author`/colores por defecto actualizados
  a "Nima OVL — Dirección B"/"Atlas Commerce"/paleta cálida real (antes decían "PetDrop
  OVL"/"Atlas Comerce"/verde OVL viejo #0c6b45 — nunca se habían actualizado tras el
  rebrand ni el cambio de paleta).
- `announcement-bar.liquid`: default corregido de "€50" a "$50" (la tienda opera en USD).
- `main-collection.liquid`: quitado el "Seis objetos" hardcodeado del copy de fallback —
  ya no coincide con las 14 fichas reales del catálogo.

### Cómo se aplicó
Los fixes se subieron vía Admin GraphQL API (`themeFilesUpsert`) a un **theme duplicado
sin publicar**, "Nima — Dirección B (Auditoría Code)" (ID `198934265937`) — Shopify
bloquea escritura por API sobre el theme MAIN/publicado. `shopify theme check` local:
0 errores (antes 7), 2 warnings ya conocidos (fuentes deprecated).

### Known issues / Pending
- **El duplicado con los fixes no está publicado todavía** — Brey debe previsualizarlo
  y publicarlo manualmente desde el admin de Shopify si aprueba los cambios (ver
  `ESTADO-tienda-mascotas.md`, sección 9, para la checklist de qué revisar).
- No se pudo verificar visualmente en navegador (sin herramientas de browser/preview
  disponibles en esta sesión) — la verificación fue por lectura de código, `theme check`,
  y consistencia de CSS/Liquid, no por captura de pantalla real.

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
