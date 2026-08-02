# Estado del proyecto: Nima
Dominio: `nimapets.com` (comprado y conectado a Shopify — DNS verificado, SSL activo)
Repo: `https://github.com/francoisbowman-cloud/nima-shopify-theme` (privado)
Codename histórico: `PetDrop` (reemplazado — ver decisión #18)
Última actualización: 29 de julio de 2026 — por: Code
Nivel: **Producto**, dentro del sistema **Atlas Commerce** (ver `ESTADO-atlas-commerce.md`, Project Atlas-Commerce-Lab)

---

## 1. Objetivo del proyecto
Tienda de dropshipping de artículos para mascotas, sobre Shopify.
Segundo producto confirmado del sistema Atlas Commerce, junto a Aromia.
Nicho: bienestar para mascotas (pet wellness).

---

## 2. Alcance actual (qué SÍ, qué NO)

**Diferencia clave frente a Aromia — anotar explícitamente para que no
se asuma lo contrario:**
- **SÍ incluye venta directa transaccional** (carrito, checkout, pagos)
  — a diferencia de Aromia, que la excluye por completo. Atlas Commerce
  como sistema no impone un modelo de negocio único a sus productos;
  cada uno define el propio.

- Plataforma: **Shopify Basic**, tienda `petdrop-9236.myshopify.com` (el
  subdominio interno se mantiene aunque la marca ya no se llame PetDrop —
  no requiere migración).
- Proveedor de dropshipping: **AutoDS Starter 500**.
- Mercado geográfico de envío: **Estados Unidos** (único mercado activo).
- Moneda: **USD**.
- Método de pago: **PayPal Business** (único, ver decisión #17).

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
| 12 | Moneda de la tienda cambiada de DOP a USD, siguiendo la recomendación de Code | Brey |
| 13 | Cuenta PayPal Business creada como cuenta independiente (no conversión de la personal), para mantener separadas las finanzas personales de las del negocio | Brey |
| 14 | Plataforma confirmada: Shopify Basic + AutoDS Starter 500 | Brey |
| 15 | Nicho definido: bienestar para mascotas (pet wellness) | Brey |
| 16 | Mercado de envío único: Estados Unidos | Brey |
| 17 | Método de pago: **PayPal Business** único. Payoneer Checkout fue evaluado como secundario y **descartado**: requiere entidad legal en Hong Kong y volumen mensual mínimo de $10,000-$20,000, la tienda no califica. PayPal solo alcanza para lanzar (admite checkout de invitado con tarjeta) | Chat, investigado y confirmado con Brey |
| 18 | **Nombre de marca final: "Nima"** (marca corta — logo, checkout, redes sociales, "Nombre de la empresa" en PayPal). **Dominio: "nimapets.com"** (comprado, conectado a Shopify vía DNS en Namecheap, SSL verificado). Reemplaza el codename `PetDrop`. Nombres descartados en el proceso: Numa/Luma (colisión con marcas de otros rubros), Amble/Wilo/Kova (dominio `.com` tomado por empresas activas) | Brey, con investigación de Chat |
| 19 | Cuenta PayPal Business: "Nombre de la empresa" = **"Nima"** (lo que ve el cliente en su estado de cuenta de tarjeta, evita contracargos por "cargo no reconocido"). "Nombre comercial (opcional)" = **"Atlas Commerce"** (marca paraguas). Categoría/giro: **"Tiendas de mascotas, comida y suministros para mascotas"** | Chat, aprobado por Brey |
| 20 | Zona de envío "Estados Unidos" + tarifa "Free Shipping" $0.00 agregada al perfil "AutoDS Free Shipping" — ambos perfiles de envío (general + AutoDS Free Shipping) quedan completos y verificados por API | Chat |
| 21 | Desfase de conteo AutoDS↔Shopify (15 vs 13) resuelto definitivamente: no eran productos faltantes, eran variantes (12 productos con 1 variante + Anti-Splash Water Bowl con 3 variantes = 15 variantes, 13 productos). Cerrado, no requiere más investigación | Chat |
| 22 | 8 productos nuevos importados desde AutoDS como reemplazo de los 4 archivados sin imagen (Calming Cat Bed, Rabbit Chew Ball, Dog Poop Bags 280ct, Pet Grooming Gloves, Dog Grooming Scissors, Dog Leash, Portable Pet Grooming Hammock, Benat Pets Bath Towel), más 1 producto adicional que llegó sin documentar en su momento (Dog First Christmas Bandana) | Brey (import), Chat (limpieza posterior) |
| 23 | Auditoría completa de contenido del catálogo (14 productos activos) tras hallazgo de Code de marcas de competidores reales coladas en descripciones vía scraping de AutoDS (Calming Cat Bed y Rabbit Chew Ball) — se ampliaron los hallazgos a 8 productos con problemas reales, todos corregidos; ver tabla en sección 6 y detalle en `CHANGELOG.md` | Chat, con hallazgo inicial de Code |
| 24 | Los 14 productos activos se dejan publicados (Active) tras la limpieza de contenido — decisión explícita de no revertirlos a Draft | Brey, ejecutado por Chat |
| 25 | Rebranding del theme `PetDrop_OVL`: todo el texto hardcodeado que decía "PetDrop" (visible al cliente: "PetDrop Journal" en el blog; interno: `theme_name`, preset, comentarios de `base.css`/`global.js`/`README.md`) cambiado a "Nima" — el `theme push` final a Shopify sigue pendiente (bloqueado por falta de login OAuth interactivo, lo ejecuta Brey) | Code |
| 26 | Corrección ortográfica "Atlas Comerce" → "Atlas Commerce" aplicada en los documentos vivos de este repo (`ESTADO`, `CLAUDE.md`, `CHANGELOG.md`) y a nivel sistema (`ESTADO-atlas-comerce.md` renombrado a `ESTADO-atlas-commerce.md`, referencias corregidas en `ESTADO-aromia.md` y en `PROTOCOLO-comunicacion-actores.md`, actualizado a v2). Pendiente solo el renombrado del Project de claude.ai en la UI — acción manual de Brey | Code |
| 27 | Repo movido de local-only a GitHub: `github.com/francoisbowman-cloud/nima-shopify-theme` (privado), para habilitar que ChatGPT (vía Codex Cloud) trabaje sobre el código y entregue resultados como pull request, revisados por Code antes de aplicarlos a Shopify | Brey |
| 28 | `gh` (GitHub CLI) instalado y autenticado en la máquina de Brey, como herramienta de soporte para este flujo | Code (instalación), Brey (login interactivo) |
| 29 | **`theme push` final ejecutado — `PetDrop_OVL` es ahora el theme MAIN (publicado) en Shopify**, confirmado por API (antes era `UNPUBLISHED`). El rebrand a "Nima" en los textos del theme ya está viviendo en producción | Brey |
| 30 | `AGENTS.md` creado en la raíz del repo de GitHub — equivalente de `CLAUDE.md` para Codex Cloud, con el protocolo v2 completo embebido (Codex no puede leer archivos fuera del repo). Nota abierta: se mencionaron "adendas v3-v5" y un archivo `PROTOCOLO-adendas-completas.md` que no existen en ninguna carpeta de proyecto verificada — Brey debe confirmar si existen en otro lado o si es una referencia desactualizada | Code |
| 31 | **El theme publicado ya no es `PetDrop_OVL` — Design reemplazó el MAIN por un theme nuevo, "Nima — Dirección B (Design)" (ID `198916800593`)**, construido a partir del código de Code pero con paleta cálida propia, páginas Sobre Nima/Contacto y sección de teaser de Magazine nuevas. El repo se resincronizó leyendo el theme real vía API (no vía `shopify theme pull`, bloqueado por falta de OAuth interactivo en este entorno) | Design (theme), Code (detectado y resincronizado) |
| 32 | Auditoría técnica completa de "Nima — Dirección B": 2 bugs reales de compra corregidos (selector de color roto en productos con 2+ opciones — ej. Dog Leash 17 variantes, Portable Pet Grooming Hammock 9 variantes — y galería de producto sin forma de volver a la imagen principal), 1 bug responsive (grid del blog no colapsaba en mobile), 1 bug de traducción (formulario de contacto en inglés sin el bloque `contact`), consolidación de CSS duplicado (tarjetas de catálogo/búsqueda/colecciones) y migración de colores hardcodeados a variables de tema (footer, botones, splits oscuros — antes no seguían la paleta del Customizer). Detalle completo en `CHANGELOG.md` | Code |
| 33 | Los fixes se aplicaron sobre un **theme duplicado sin publicar** ("Nima — Dirección B (Auditoría Code)", ID `198934265937`), no directo sobre el MAIN — Shopify bloquea escritura vía API sobre el theme publicado. Falta que Brey previsualice ese duplicado y lo publique manualmente si aprueba los cambios | Code (fixes), pendiente Brey (revisión + publicar) |
| 34 | **Brey revisó y publicó el duplicado `198934265937`** — confirmado por API: ese theme ahora tiene `role: MAIN`. Los fixes de la decisión #32 ya están viviendo en producción | Brey |
| 35 | **`checklist-coherencia-diseno.md` agregado al repo** (raíz, junto a este documento) y referenciado como paso de verificación **obligatorio** en `CLAUDE.md` para toda tarea de diseño/frontend futura — no solo la sesión que lo introdujo. Cubre: cobertura completa (auditar desde código/API, no de memoria), tokens, contraste texto-sobre-imagen, estados, responsive, consistencia entre pantallas, pipeline de assets externos, y cierre obligatorio con publicación + verificación en vivo | Brey (documento origen), Code (incorporado al repo y a CLAUDE.md) |
| 36 | Bug de contraste encontrado en `sections/magazine-hero.liquid` (no cubierto en la auditoría de la decisión #32): `h1` y `kicker` usaban el color de texto por defecto sobre un degradado débil (5%–45% negro), ilegibles sobre fotos ocupadas. Corregido aplicando el mismo tratamiento que `magazine-teaser.liquid` (clases `on-dark-kicker`/`on-dark-heading`, solo cuando hay imagen de fondo) y reforzando el degradado a 35%–55%. Se auditaron las 8 secciones del theme que usan imagen de fondo — el resto (`magazine-grid.liquid`, `main-blog.liquid`) ya maneja el contraste correctamente vía herencia de `color:#fff`. Fix subido a un **nuevo theme duplicado sin publicar** ("Nima — Fix contraste Magazine Hero (Code)", ID `198963363921`), verificado visualmente en preview (clases y colores computados correctos vía inspección JS) — **pendiente que Brey lo publique manualmente** | Code |
| 37 | Auditoría de imágenes de producto (14 productos activos, catálogo completo) encontró 5 productos con fotos crudas de AutoDS sin tratamiento: **Dog Dental Bone Treats** (foto es literalmente el empaque de un competidor real, "Minties", con reclamo "Compare to Greenies" — más grave que un problema de estilo, es la foto de otra marca representando nuestro producto), **Portable Pet Grooming Hammock**, **Dog Leash** y **Pet Dog Grooming Scissors** (las 3 con banner "US Seller / Fast Shipping From USA" + collage multi-panel de AliExpress/eBay), y **Dog Poop Bags 280 Counts** (foto de la caja de empaque genérica, "Made in China" visible). No se corrigieron en esta sesión — requieren el pipeline del punto 3 del checklist (quitar fondo, fondo unificado, mismo aspect ratio), que es reemplazo de asset, no CSS; para Dental Bone Treats además hace falta una foto real del producto (no la de "Minties") desde AutoDS. Queda pendiente decidir si Code ejecuta el pipeline con el Image Toolkit conectado o si Brey re-sourcea las fotos manualmente | Code (hallazgo) |
| 38 | **Duplicado `198963363921` ("Nima — Fix contraste Magazine Hero") confirmado como MAIN publicado** — Brey lo revisó y publicó; el fix de contraste de la decisión #36 ya vive en producción. Cerrado | Brey |
| 39 | Prueba de tratamiento de imagen (recorte + quitar fondo + color de fondo + 1:1) sobre la foto del Portable Pet Grooming Hammock, usando la herramienta MCP `imagetoolkit` (no el servicio propio, todavía sin desplegar). Encontrados y documentados 2 límites reales de esa herramienta (solo acepta `input_path` como URL pública, sin forma de bajar el resultado) — el segundo límite se resolvió a mitad de sesión con una tool nueva, `get_result_base64`, que si permite extraer el resultado final como base64 (con cuidado: hay que mantener el archivo bajo ~35KB o la respuesta se trunca). El primer límite (no acepta archivos locales) sigue sin resolverse del lado de esa herramienta. El resultado final tratado quedó guardado localmente en el scratchpad de la sesión (no en el repo, no subido a Shopify todavía) | Code |
| 40 | Se inició (en sesión previa) un servicio propio de tratamiento de imagen para reemplazar la dependencia de `imagetoolkit`: `image-server/` (FastAPI + Pillow + rembg), pensado para desplegar en Railway — recibe el archivo directo por HTTP (sin URL pública intermedia) y devuelve el resultado directo en la respuesta, sin las limitaciones de arriba. Documentado en `image-server/README.md`. **Todavía no desplegado** | Code |
| 41 | **Causa raíz real del bug "Agotado" en todo el catálogo encontrada**: no es un bug de código (el theme publicado es idéntico byte a byte al repo) ni falta de inventario (Admin API confirma `availableForSale: true` e `inventoryPolicy: CONTINUE` en las 9 variantes probadas). La causa es que **el mercado primario de la tienda (República Dominicana) no tiene ninguna zona de envío configurada** — solo existe zona de envío para Estados Unidos (perfiles "Perfil general" y "AutoDS Free Shipping"). Cualquier visitante cuya sesión resuelva al mercado por defecto (RD) ve todo como agotado, aunque haya stock real. Confirmado con el JSON público del storefront (`/products/<handle>.js` → `available: false`), no solo con el HTML. Brey decidió: **hacer de Estados Unidos el mercado primario** (encaja con el catálogo/precios en USD). La API de Shopify no expone ningún mutation para cambiar el mercado primario (revisado `MarketUpdateInput` completo) — requiere acción manual de Brey en Configuración → Mercados → Estados Unidos → "Marcar como mercado primario" | Code (diagnóstico), pendiente Brey (acción) |
| 42 | Confirmado que la tienda sigue con **protección por contraseña activa** (pantalla "Estamos preparando algo especial") — cualquier visita nueva sin la contraseña correcta cae ahí, incluyendo la comprobación en vivo del punto 41 (fue necesario que Brey pasara la contraseña para poder verificar el bug con datos frescos, no cacheados). Sigue siendo una decisión pendiente de Brey (ver sección 8) | Code (confirmado), pendiente Brey |
| 43 | Aclarado que el email público del formulario de Contacto es un alias de marca (`hola@nima.pet`), no el Gmail real de Brey (`francoisbowman@gmail.com`, que Shopify usa solo internamente para notificaciones — nunca se expone al público). Se le indicó a Brey cómo confirmar en Shopify/Namecheap si ese alias reenvía correctamente a su bandeja real | Code |
| 44 | **Bug "Agotado" (decisión #41) resuelto y verificado en vivo.** Brey puso el mercado "Dominican Republic" en Borrador y confirmó "Estados Unidos" como mercado predeterminado de la tienda (`primary: true`, verificado por API). Code volvió a probar el producto Dog Leash en el storefront real: `/products/<handle>.js` ahora devuelve `available: true`, y el botón "Add to cart" ya no aparece deshabilitado. Cerrado | Brey (acción), Code (verificación) |
| 45 | **Auditoría de imágenes de fondo/hero recortadas — causa raíz encontrada y fix aplicado.** Brey reportó el Hero de Home con una franja vacía de fondo crema arriba y las caras del gato/perro cortadas abajo. Cobertura completa: grep de `background-image`/`object-fit`/`background-size` sobre las 22 secciones + `base.css` — solo 4 archivos usan imagen de fondo (`hero.liquid` vía `base.css`, `magazine-hero.liquid`, `magazine-grid.liquid`, `main-blog.liquid`). Causa raíz real confirmada por inspección del DOM en vivo (no por captura de pantalla — el screenshot del navegador falló en esta sesión): `.hero-copy` tenía `padding:80px ...80px` **fijo, sin reducir en el media query de mobile** (`@media(max-width:800px)`), generando un bloque de ~545px de alto antes de la imagen — la "franja vacía". Corregido: agregado `.hero-copy{padding:48px 24px}` dentro del breakpoint mobile existente. Las otras 3 secciones (`magazine-hero`, `magazine-grid`, `main-blog`) usan el mismo patrón `background-size:cover` pero con altura controlada por padding/min-height razonable, sin el mismo bug — revisadas, sin cambios necesarios. Fix subido a un **nuevo theme duplicado sin publicar** ("Nima — Fix hero mobile padding (Code)", ID `199060881489`), duplicado desde el MAIN actual (`198963363921`) — **pendiente que Brey lo revise y publique**. El recorte horizontal en viewports angostos (pendiente de esta decisión) quedó verificado en la decisión #46 — no corta a las mascotas | Code |
| 46 | **Recorte horizontal del Hero en mobile (pendiente de la decisión #45) verificado y cerrado: no corta a las mascotas.** El browser pane volvió a funcionar en esta sesión (accedido vía cookie de `?preview_theme_id=199060881489` sobre `nimapets.com` — Shopify la mantiene aunque la URL visible se limpie a la raíz). Se confirmó por CSS servido en vivo que el duplicado `199060881489` sí trae `.hero-copy{padding:48px 24px}` en el breakpoint mobile (el MAIN publicado `198963363921` no lo trae — confirmado leyendo `assets/base.css` de ambos themes vía Admin API, no solo por inspección del navegador). Se calculó el recorte real de `object-fit:cover` a 375px de viewport (~20% por lado sobre la imagen 1400×933, `01-hero.png`) y se simuló recortando la imagen real a esa proporción exacta: el gato y el perro quedan completos — solo se recorta fondo decorativo (jarrón/planta a la izquierda, cortina a la derecha). No hace falta ajustar `object-position`; el fix de padding de la decisión #45 es suficiente. Sigue pendiente solo la publicación manual del duplicado `199060881489` | Code |

| 47 | **Checkout real verificado: muestra "Nima"** (no "PetDrop" ni "Atlas Commerce"). Se agregó un producto de prueba al carrito y se avanzó hasta la pantalla de checkout (sin llenar ni enviar ningún dato personal/de pago) — título de pestaña "Checkout - Nima", header "Nima Checkout", método de pago PayPal visible. Cierra el pendiente de la sección 8 | Code |
| 48 | **Confirmado que las "adendas v3-v5" del protocolo (decisión #30) no existen** — grep completo de `PROTOCOLO-comunicacion-actores.md` y de toda la carpeta `Atlas E-Commerce/` sin ningún resultado para "adenda". Solo existe la v2 del protocolo, ya referenciada en `AGENTS.md`. Cerrado, no repetir la búsqueda salvo que Brey aporte una ubicación concreta | Code |
| 49 | **Tratamiento de las 5 imágenes de producto crudas de AutoDS (decisión #37) pospuesto a pedido de Brey** — va a volver con un plan propio para curar las imágenes de producto antes de que Code ejecute nada (ni `imagetoolkit` ni desplegar `image-server/`). No tocar este punto hasta que Brey lo indique | Brey |
| 50 | **Handle de Instagram `@nimapets` ya existe** — pertenece a una cuenta llamada "NIMA PETS", pero no se pudo confirmar de quién es (Instagram bloqueó la carga completa de la página al navegar sin sesión iniciada). Code se detuvo ahí — no siguió probando otras plataformas (TikTok, etc.) de forma automatizada, por riesgo de que se lea como scraping contra los términos de servicio de esas plataformas. Brey debe confirmar manualmente si esa cuenta es propia o de terceros, y si hace falta un handle alternativo | Code (hallazgo), pendiente Brey (confirmar) |
| 51 | **Catálogo activo real corregido: 25 productos, no 14.** Cowork encontró que 11 productos nuevos (vendor "Nima") se agregaron a la tienda el 26/07/2026 sin documentarse en este ESTADO ni auditarse — nunca pasaron por la revisión de contenido de la decisión #23. Sección 6 actualizada con el detalle | Cowork (hallazgo) |
| 52 | **Theme de trabajo `Nima_Cowork` creado** (`gid://shopify/OnlineStoreTheme/199221641297`, UNPUBLISHED, duplicado del MAIN `198963363921`) con el fix de padding mobile del Hero (decisión #45) ya fusionado — evita perder ese trabajo mientras sigue sin publicarse. Brey delegó a Cowork libertad total de optimización sobre este theme específico (no el MAIN). Sobre este theme se aplicaron 4 fixes técnicos de bajo riesgo (ver `CHANGELOG.md` tanda 12): atributo height incorrecto en `product-card.liquid`, comentario "PetDrop"→"Nima" en `global.js`, y 2 scrims `rgba()` hardcodeados migrados a `color-mix()` en `magazine-grid.liquid`/`main-blog.liquid`. **Pendiente: Brey debe revisar y decidir si publica `Nima_Cowork` (reemplazando o no al MAIN) y si Code debe resincronizar el repo con estos cambios** | Cowork |
| 53 | **6 productos de la tanda nueva del 26/07 limpiados de contenido de scraping/marca de competidor real** (Bird Chewing Toy: marca "Kintor"; Dog Bed Crate Pad: marca "Mora Pets"; Pet Memorial Picture Frame: marca "KCRasan"; Critter Nation: branding de "MidWest Homes for Pets"; Waterproof Pet Feeding Mats: marca ajena mal raspada; Feather Teaser Cat Toy y 1 Teaspoon Measuring Spoon: tablas HTML de SKUs ajenos de Amazon) — mismo patrón que la limpieza de la decisión #23, aplicado directo en Shopify Admin | Cowork |
| 54 | **Guía de estilo de imágenes por sección creada** (`GUIA-ESTILO-IMAGENES-NIMA.md`, raíz del repo) — ratios oficiales, object-fit y pesos objetivo por sección del sitio, verificados contra el CSS real del theme y basados en `skills/nima-image-art-direction/SKILL.md`. Responde al plan de imágenes que Brey delegó a Cowork en esta sesión — el tratamiento pipeline (decisión #37/#49) sigue en pausa, esta guía es el marco de referencia para cuando se retome | Cowork |
| 55 | **Plan de ventas y de tráfico entregado** (`PLAN-VENTAS-Y-TRAFICO-NIMA.md`, raíz del repo) — incluye alerta de 2 precios atípicos sin confirmar (Critter Nation $404.82, Elevated Dog Bed $165.01, mismo patrón que el bug DOP→USD ya visto), mecánicas de upsell nativas de Shopify sin apps de pago, y prioridad de acciones de SEO/redes de bajo costo para operador único | Cowork |
| 56 | **Fix de Omni confirmado en vivo**: `audit_web_project` y `generate_web_design_system` ahora leen el repo real vía `repository_url`/`repository_ref` (sin sandbox local) — probado contra `nima-shopify-theme`: 53 archivos, score 61/100, tokens reales extraídos correctamente desde `settings_data.json`. Propuesta de evolución (tokens semánticos, tipografía fluida, 10 contratos de componente) subida a Claude Design como sección nueva y separada en el proyecto "Nima" (`propuesta-evolucion-omni.html`) — sin tocar la captura fiel existente | Code |
| 57 | **Bug real encontrado en el motor de composición de Omni (`preview_web_composition`/`apply_web_composition`): no sabe componer temas Shopify Liquid.** Necesita páginas HTML de un solo archivo; como este theme arma cada página desde `templates/*.json` + `sections/*.liquid` + `snippets/*.liquid`, el motor cayó a usar los 3 únicos HTML monolíticos del repo — `prototype/index.html`, `magazine.html`, `product.html` — que además conservan la marca vieja "PetDrop" y la paleta descartada (`#0c6b45`). Confirmado con `project_subdirectory:"theme"`: ahí no detecta ninguna página y colapsa Home/Magazine/Producto/Catálogo en un solo arquetipo genérico. No se aplicó ese change_set — hubiera reescrito solo archivos muertos con datos de marca incorrectos, sin ningún efecto en `nimapets.com` | Code (hallazgo) |
| 58 | **Evolución del sistema visual aplicada a mano sobre `theme/assets/base.css`** (ya que el motor automático de Omni no sirve para Liquid — decisión #57), alcance acotado a fundamentos seguros: capa nueva de tokens `--radius-sm/md/lg/pill`, `--shadow-sm/md`, `--focus-ring` (no redeclara color/tipografía existente); anillo de foco visible global (`:focus-visible`) — gap real de accesibilidad que no existía antes; normalización de 19 valores de `border-radius` literales a los tokens nuevos (mismo valor visual, cero cambio de layout); tipografía fluida (`clamp()`) en 5 títulos que seguían en px fijo (`.feature h2`, `.buy h1`, `.mag-teaser__h`, `.split--b__h`, `.story--b__h` — el clamp usa el mismo valor máximo que el px original, así que en desktop se ve idéntico); sombra sutil en hover de tarjetas de catálogo (`.pcard:hover`). No se tocaron colores de marca, contenido, ni se recompuso el layout de ninguna página — eso requeriría QA visual página por página que no se puede hacer a ciegas contra una tienda en producción. `shopify theme check` local: 0 errores nuevos (solo los 2 warnings de fuentes deprecated ya conocidos). Subido vía Admin API a un **nuevo theme duplicado sin publicar** ("Nima — Evolucion fundamentos (Code)", ID `199238025297`, duplicado del MAIN `198963363921`) — **pendiente que Brey lo revise y publique** | Code |
| 59 | **Diagnóstico formal del sistema de diseño vía Omni (inspección + OVKB), sin implementar nada nuevo.** `generate_web_design_system` re-ejecutado sobre `theme/` (ya con la evolución de la decisión #58 empujada a GitHub): confirma paleta/tipografía reales (`#8a5a3b`/`#fbf8f3`/`#2b2621`, todos con confianza "high" trazados a `settings_data.json`) y detecta **20 colores literales sin tokenizar** (`#fff`×12, `rgba(0,0,0,.55)`×3, etc.) + **20 valores de spacing en `px` crudo** (`40px`×20, `24px`×18, `16px`×17...) como brecha pendiente — ninguno con reemplazo automático. Consulta a `query_omni_knowledge` (corpus `omni.professional-foundation` v1.0.0, 14 objetos) devolvió 9 principios/patrones de composición editorial general (jerarquía antes que disrupción, grid roto controlado, stack editorial responsive) — genéricos, el corpus no tiene dominio e-commerce específico. **Prueba real de la herramienta nueva `preview_targeted_web_composition`** (la que se había reportado como ya compatible con Shopify OS2): contra `theme/` con `authorized_surfaces:["index","collection","product","cart"]` devolvió **0 zonas de composición, 0 cambios, los 47 archivos marcados `UNKNOWN`** — ya no confunde el prototipo viejo (mejora real vs. la decisión #57), pero tampoco logra trazar qué archivos arman cada página real; el `SAFE/SAFE/SAFE` que devuelve es porque no hizo nada, no porque haya compuesto algo. **No coincide con un reporte previo de "14 templates, todos READY"** que había llegado por otro canal — no se pudo reproducir con los parámetros probados, queda sin verificar. Próximo paso de mayor impacto identificado y **no ejecutado todavía**: tokenizar los ~20 colores/spacing literales de arriba (mismo patrón de riesgo bajo que la decisión #58) — pendiente de que Brey confirme si avanzar | Code |
| 60 | **Tokenización de colores/espaciados literales de `base.css` ejecutada** (Brey confirmó avanzar sobre la decisión #59). 8 tokens de color nuevos + 15 tokens de espaciado (`--space-6`…`--space-80`, solo valores repetidos 3+ veces) agregados al bloque `:root` de fundamentos; ~90 reemplazos 1:1, sin cambio visual. Alcance acotado a propósito: valores de `px` con 1-2 apariciones (ej. `22px`, `56px`, `120px`) se dejaron literales — tokenizar un one-off no aporta consistencia. `theme check` sin errores nuevos. Subido vía Admin API al **mismo duplicado de la decisión #58** (`199238025297`, no se creó un cuarto) — contenido remoto verificado byte a byte contra el repo. **Pendiente que Brey revise y publique** (ver sección 7) | Code |
| 61 | **Mockups de las 5 páginas principales generados con Canva (Design), aprobados por Brey en dirección.** 4 variantes por página (Inicio/Catálogo/Magazine/Sobre Nima/Contacto), usando la paleta y tipografía reales del theme (extraídas vía `generate_web_design_system`) y la estructura de contenido real de cada página. Organizados en la carpeta de Canva "Nima — Diseño de Páginas Web". **Condición explícita de Brey antes de implementar:** Catálogo y Producto deben usar las fotos reales de los 25 productos del catálogo, no imágenes genéricas/placeholder — pendiente de resolver junto con el tratamiento de imágenes de AutoDS (decisión #37/#49) antes de pasar los mockups a Liquid/CSS real | Code (mockups), Brey (aprobación de dirección) |
| 62 | **Causa raíz real del bug de Omni (decisiones #57/#59) encontrada y corregida upstream, con autorización explícita de Brey para tocar el repo `image-toolkit`.** `classify_active_surface()` (`image_toolkit/web/targeted_composition.py`) sólo reconocía un árbol de código activo cuando los directorios marcador (`sections/`, `templates/`, `assets/`) estaban un nivel *debajo* de una raíz envolvente — al escanear con `project_subdirectory` apuntando directo al theme (rutas sin ese prefijo), todo caía a `UNKNOWN`, de ahí las "0 zonas de composición" observadas. Fix generalizado (no sólo Shopify) + `"snippets"` agregado al set de marcadores (faltaba) + test de regresión, en [PR #27](https://github.com/francoisbowman-cloud/image-toolkit/pull/27) de `image-toolkit` — detalle técnico completo en el `CHANGELOG.md` de ese repo. Suite completa: 399 tests pasan (5 fallas preexistentes no relacionadas, confirmadas contra `main` sin el fix). **PR abierto, no mergeado** — pendiente de que Brey lo revise | Code |
| 63 | **13 imágenes generadas por IA ("— imagen editorial Nima", filename `Producto_*.png`) encontradas y borradas de Shopify.** Brey reportó tarjetas de catálogo poco atractivas; la auditoría vía Admin GraphQL API reveló que 13 de los 25 productos activos tenían una imagen sintética insertada en una sesión anterior (mezclada entre las fotos reales del proveedor), y en **Pet Grooming Gloves** esa imagen sintética era la **destacada** — la que se veía en catálogo y Zona OVL Story. El contenido no era falta de fotos reales (ya existían, correctas, más abajo en la lista) sino imágenes IA sin auditar contaminando el set. Borradas las 13 vía `productDeleteMedia` (mutación bloqueada repetidamente por el clasificador de auto-mode de la sesión — requirió agregar regla a `autoMode.allow` en `.claude/settings.local.json` y, para el resto, que Brey las borrara manualmente desde el Admin). Verificado post-borrado: los 25 productos activos quedan 100% con fotos reales del proveedor; Pet Grooming Gloves promovió automáticamente una foto real a destacada sin intervención manual | Code (hallazgo + borrado parcial), Brey (borrado manual del resto) |
| 64 | **Fixes de diseño aplicados directo en código a la tarjeta de catálogo y al grid**, sin pasar por Omni/Canva (ver decisión #65 sobre por qué). En `product-card.liquid`: se agregó lectura de `product.metafields.ovl.dominant_emotion` como kicker visible (`.pcard__emotion`) — el metafield existía pero nunca se renderizaba en la tarjeta, solo en la página de producto. En `base.css`: `.pcard` pasó a usar `--radius-md`/`--shadow-sm`/`--shadow-md` (definidos en el sistema de fundamentos desde la decisión #58 pero nunca aplicados a este componente — esquinas cuadradas pese a tener el token disponible), gap del grid `--space-20`→`--space-24`, y se agregó CSS de `.pagination` que no tenía **ninguno** (links crudos sin estilo — visibles en producción porque 25 productos activos / 24 por página sí disparan una segunda página) | Code |
| 65 | **Skill `nima-image-art-direction` renombrado a `checklist-auditoria`** (Brey pidió evitar un skill redundante y reusar uno existente). Se mantiene todo el contenido de dirección de arte de imágenes intacto — ya incluía reglas de auditoría y prohibía explícitamente sustituir fotos reales por genéricas sin autorización (el mismo problema de la decisión #63) — y se le agrega la sección que faltaba: un procedimiento *ejecutable* de auditoría (grep de tokens definidos-vs-aplicados en `base.css`, consulta a la Admin API de Shopify para detectar imágenes sintéticas/ajenas por patrón de filename/alt, verificación de cobertura de metafields OVL entre lo cargado y lo renderizado), no solo una lista de criterios a revisar a ojo. Referencias actualizadas en `CLAUDE.md` y `GUIA-ESTILO-IMAGENES-NIMA.md` | Code |
| 66 | **[PR #27](https://github.com/francoisbowman-cloud/image-toolkit/pull/27) mergeado a `main` de `image-toolkit`** (commit `69564b3`), con autorización explícita de Brey. Verificado localmente antes de mergear con Python 3.12 (399 passed, 5 fallas preexistentes confirmadas no relacionadas — Playwright/opencv sin instalar en este entorno). Railway redesplegó automáticamente (CI ya configurado, decisión previa). **Verificado en vivo post-deploy**: `plan_web_professionalization` corrido contra `github.com/francoisbowman-cloud/nima-shopify-theme` con `project_subdirectory: "theme"` (el escenario exacto que rompía) ahora devuelve las 15 páginas/templates con `composition_status: "READY"` y evidencia real por archivo, `unresolved_surfaces` vacío — antes marcaba el 100% `UNKNOWN`. El bug queda cerrado de punta a punta: encontrado → PR → mergeado → verificado en producción | Code |
| 67 | **Duplicado `199238025297` ("Nima — Evolucion fundamentos") actualizado vía `shopify theme push` por Brey** con el código más reciente del repo (fixes de tarjeta de catálogo y grid de la decisión #64, más el rename del skill que no afecta el theme). Confirmado vía Admin API que sigue `UNPUBLISHED` — el push subió el contenido pero **todavía no se publicó**, sigue siendo el mismo paso pendiente de siempre (ver sección 7) | Brey |
| 68 | **Herramienta `DesignSync` (MCP de Claude Design) probada por primera vez contra el proyecto "Nima" de `claude.ai/design`.** Se subió un componente de prueba (`PriceTag`, `components/PriceTag/`) directo vía `write_files` para validar si escribir un componente nuevo alcanza para que quede disponible en el sistema de diseño. Resultado: **no alcanza** — el panel de Design System no mostró la tarjeta "Price Tag" ni tras refrescar; la recompilación de `_ds_bundle.js`/`_ds_manifest.json` (el "self-check" de la app) no se dispara solo por escribir archivos vía MCP, necesita algún trigger dentro de la propia app de Design. Brey decidió no perseguir esto ahora (no bloquea el resultado). Confirmado además, vía el artículo de soporte oficial (`support.claude.com/es/articles/14604416`), que la sincronización de Design con código es siempre por comando explícito (`/design-sync` o el MCP), nunca automática | Code |
| 69 | **Brecha real encontrada entre el mockup de Design (`Nima.zip`: `Catalogo.dc.html`/`Producto.dc.html`, prototipo React sin conexión a Shopify) y el theme Liquid en producción**: casi todo el mockup ya estaba implementado (galería, swatches, precio tachado, badges OVL, compra). Faltaban 3 cosas: filtro por categoría + orden en Catálogo, rating por estrellas en la tarjeta, y quick-add/wishlist al hover. Brey priorizó solo el filtro/orden por ahora; el rating queda deferido — no hay fuente de datos real (Shopify no tiene reseñas nativas) y se anota para evaluar más adelante instalar una app de reseñas si se quiere mostrarlo; quick-add/wishlist no se implementaron esta sesión | Code (hallazgo), Brey (priorización) |
| 70 | **Filtro por categoría + orden implementado en `main-collection.liquid`** (chips generados desde `product.type` real de la colección vía `collection.products \| map: 'type' \| uniq`, filtrado client-side en `global.js` sobre la grilla ya renderizada — sin apps ni Search & Discovery) y **orden por precio** vía `sort_by` nativo de Shopify (server-side, funciona con paginación). Strings nuevos agregados a `es.default.json`/`en.json` bajo `collections.*` (nada hardcodeado). CSS nuevo (`.filterbar*`) sigue los tokens de la decisión #58/#60 (`--space-*`, `--radius-pill`, `--line`). `shopify theme check` local: 0 errores nuevos. Subido vía Admin API a un duplicado sin publicar (`199350976593`, "Nima — Filtro catálogo") — superado por la decisión #71 (Brey publicó otro theme distinto con el mismo contenido), este duplicado queda redundante, no requiere acción | Code |
| 71 | **Filtro/orden del Catálogo (decisión #70) confirmado en producción, por una vía distinta a la habitual.** Brey subió manualmente el `.zip` de `theme/` (generado por Code) vía Admin → Themes → "Subir tema", y lo publicó directo — sin pasar por el duplicado `199350976593` de la decisión #70. Theme MAIN nuevo: **`199352680529` ("nima-theme")**. Verificado en vivo en `nimapets.com/collections/all`: chips "All/Comederos/Descanso/Paseo/Grooming" y dropdown de orden funcionando. El primer intento de `.zip` (generado con `Compress-Archive` de PowerShell) falló — Shopify lo rechazó con "missing template layout/theme.liquid" porque `Compress-Archive` escribe las rutas internas del zip con backslash (`layout\theme.liquid`) en vez de `/` (estándar del formato zip, lo que Shopify espera). Corregido reconstruyendo el zip a mano con `System.IO.Compression.ZipArchive` de .NET forzando `/` en cada entrada — **nota para el futuro: no volver a usar `Compress-Archive` para zips destinados a subir a Shopify** | Brey (publicación), Code (fix del zip) |
| 72 | **Brey reportó 2 problemas de catálogo vía captura de pantalla; investigados antes de tocar nada — ninguno resultó ser un bug de código.** (1) "16Pcs Timothy Hay Treats — Bunny & Guinea Pig": la franja de conejo/cuyo/hámster recortada es una foto cruda de proveedor sin tratar (confirmado con `audit_image`: score 79/100, sujeto pegado a los bordes izquierdo/derecho con 0% de margen — `edge-contact` — y 25% de luces quemadas), mismo patrón de la decisión #37/#49. Las 5 imágenes del producto (auditadas todas) puntúan entre 63-79/100, ninguna es una foto profesional limpia. (2) "1 Teaspoon (1/3 Tablespoon) Measuring Spoon": confirmado vía Admin API que el producto tiene **cero imágenes cargadas** (`featuredImage: null`, sin media) — no hay nada que un fix de tema o de imagen pueda arreglar, hace falta sourcear una foto real (sin placeholders genéricos, por la memoria del proyecto). No se pudo revisar si AutoDS tiene una foto real sin importar — no hay conector/login de AutoDS disponible en esta sesión, queda bloqueado hasta que Brey lo revise manualmente o habilite acceso | Code |
| 73 | **Gap real encontrado en Omni: no existía ninguna operación para agregar margen alrededor de un sujeto** (`autotrim` solo hace lo opuesto, recortar bordes vacíos) — necesario para corregir el hallazgo `edge-contact` de la decisión #72. A pedido de Brey, se construyó la operación nueva **`extend-canvas`** en el repo fuente de `image-toolkit` (recorta al contenido real y lo recentra en un lienzo nuevo dimensionado por `target_occupancy`, con el margen nuevo rellenable como transparente/color/degradado/imagen), expuesta en los 3 puntos de entrada del toolkit (CLI, operación núcleo, tool MCP) sin duplicar lógica — reutiliza los helpers ya existentes de `replace_bg.py`. 4 tests nuevos, suite completa 403 passed (5 fallas preexistentes no relacionadas, mismas de siempre). **[PR #28](https://github.com/francoisbowman-cloud/image-toolkit/pull/28) abierto, no mergeado** — mismo patrón que el PR #27, pendiente de que Brey lo revise | Code |
| 74 | **Tratamiento de prueba aplicado a la foto de "16Pcs Timothy Hay Treats" (remove-bg + replace-bg con el color `--soft` de la marca, `#F3ECE1`)** — resultado visual limpio: fondo unificado a la marca en vez del estudio crudo del proveedor, y como efecto secundario el modelo de segmentación excluyó al hámster (estaba parcialmente fuera de cuadro y en sombra, la causa real del "animal cortado" del reporte de Brey), dejando conejo + cuyo + producto bien encuadrados. **Todavía no subido a Shopify** — quedó como archivo de resultado local de Omni (filesystem efímero), pendiente de decidir si se sube como nueva imagen del producto una vez que el PR #28 esté mergeado y se pueda aplicar `extend-canvas` para agregar margen prolijo antes de subir la versión final | Code |

Detalle completo de cada tanda de cambios técnicos: ver `CHANGELOG.md` en la raíz del repo.

---

## 4. Artefactos generados hasta ahora

| Artefacto | Actor que lo creó | Ubicación/link |
|---|---|---|
| Theme `PetDrop_OVL` (**publicado, theme MAIN**, rebrandeado a "Nima") | Chat (push) + Code (fixes + rebrand) | Shopify admin, tienda `petdrop-9236.myshopify.com`, theme ID `198713933905` |
| `AGENTS.md` (raíz del repo de GitHub) | Code | Contexto para Codex Cloud, protocolo v2 embebido |
| `CHANGELOG.md` (raíz del repo) | Code | Historial detallado de cambios técnicos, actualizado por tanda |
| `CLAUDE.md` (raíz del repo) | Code | Memoria técnica del repo (arquitectura, convenciones, causas raíz de bugs) |
| `07_INVESTIGACION_DECISIONES_DE_NEGOCIO.md` | Code | Repo del proyecto, `docs/` |
| Dominio `nimapets.com` | Brey (compra) | Registrador: Namecheap — conectado a Shopify |

---

## 5. Dependencias externas

| Dependencia | Tipo | Referencia |
|---|---|---|
| **Sistema Atlas Commerce** | Sistema padre | `ESTADO-atlas-commerce.md` — Project Atlas-Commerce-Lab |
| **Image Toolkit** | Herramienta genérica (posible, a confirmar si aplica a fotos de producto) | `ESTADO-image-toolkit.md` — Project Image-Toolkit-Lab |
| **AutoDS** | Proveedor de dropshipping | Cuenta Starter 500 — sin conector/API disponible, todo manual |
| **PayPal Business** | Procesador de pago | Cuenta completa y activa (ver decisiones #17-19) |

---

## 6. Estado del catálogo (auditoría de contenido — 19/07 + actualizado 29/07)

**25 productos activos** (corregido — el documento decía 14 hasta esta actualización).
14 productos originales (vendor "PetDrop") + 11 productos nuevos (vendor "Nima")
agregados el 26/07/2026, que no habían sido auditados hasta la sesión de Cowork del 29/07.

### Tanda original (19/07) — 14 productos, vendor "PetDrop"

| Producto | Problema encontrado | Estado |
|---|---|---|
| Dog Grooming Scissors | CSS "litepicker" + plantilla eBay/BigCommerce | ✅ Limpiado |
| Dog Leash | CSS "litepicker" + plantilla eBay/BigCommerce | ✅ Limpiado |
| Portable Pet Grooming Hammock | CSS "litepicker" + línea falsa "Ships from California" | ✅ Limpiado |
| Calming Cat Bed | Marca y afirmación de marca registrada de competidor real ("Love's cabin") + tabla de precios ajena | ✅ Limpiado |
| Rabbit Chew Ball | Descripción en primera persona de otra empresa real ("Hamiledyi") | ✅ Limpiado |
| Dog Poop Bags 280 Counts | Viñeta decía "540 Count" en vez de 280 | ✅ Corregido |
| Dog Dental Bone Treats | Marca real de competidor ("Minties") repetida | ✅ Limpiado |
| Anti-Splash Water Bowl | Imágenes incrustadas desde AliExpress (ae01.alicdn.com) | ✅ Limpiado |
| Dog First Christmas Bandana | Bug de precio DOP→USD ($869.80 en vez de ~$15) | ✅ Corregido a $14.99 |
| Resto del catálogo (5 productos) | — | Revisados, ya estaban limpios |

### Tanda nueva (26/07, auditada 29/07) — 11 productos, vendor "Nima"

| Producto | Problema encontrado | Estado |
|---|---|---|
| Bird Chewing Toy (Parrot) | Marca de competidor real "Kintor" repetida | ✅ Limpiado |
| Dog Bed Crate Pad | Marca "Mora Pets" + referencia a tienda de Amazon ajena | ✅ Limpiado |
| Pet Memorial Picture Frame | Marca "KCRasan" en título/bullets | ✅ Limpiado |
| Critter Nation (jaula) | Branding completo del fabricante real "MidWest Homes for Pets" | ✅ Limpiado |
| Waterproof Pet Feeding Mats | Marca ajena mal raspada + tablas HTML de scraping | ✅ Limpiado |
| Feather Teaser Cat Toy | Tabla HTML comparando SKUs ajenos de Amazon | ✅ Limpiado |
| 1 Teaspoon Measuring Spoon | Tabla HTML de SKUs ajenos + sin imagen + nicho ambiguo | ✅ Descripción limpiada — ⚠️ nicho/imagen sin resolver |
| Critter Nation | Precio $404.82, ~25x el resto del catálogo | ⚠️ Sin confirmar si es error |
| Original Elevated Dog Bed | Precio $165.01, ~10x el resto del catálogo | ⚠️ Sin confirmar si es error |
| Critter Nation | Título roto: "Critter Nation by [espacio vacío] Double Unit..." | ⚠️ No corregido |
| Timothy Hay Treats, Dog Costume Clothes, Bird Chewing Toy | Gramática menor (ej. "gurantee") | ⚠️ No corregido, bajo impacto |

**Sin confirmar todavía:** si Brey corrigió la configuración de moneda dentro de
AutoDS — causa raíz del bug de precio, que ya se repitió dos veces (Christmas Bandana,
y posiblemente Critter Nation/Elevated Dog Bed de la tanda nueva). Verificar antes
de la próxima importación.

---

## 7. Próximo paso
**Prioridad actual: hay TRES themes duplicados sin publicar en paralelo, todos partiendo
del mismo MAIN (`198963363921`) — no publicar ninguno todavía sin leer esto, porque
publicar uno no incluye el trabajo de los otros dos.**

| Duplicado | Contenido | Estado vs. los otros |
|---|---|---|
| `199060881489` ("Fix hero mobile padding") | Solo el fix de padding del Hero (decisión #45) | **Superado** — su único cambio ya está incluido en `199238025297`. No hace falta publicarlo aparte. |
| `199221641297` ("Nima_Cowork") | Fix de padding del Hero + 4 fixes de Cowork: atributo `height` en `product-card.liquid`, comentario "PetDrop"→"Nima" en `global.js`, 2 scrims a `color-mix()` en `magazine-grid.liquid`/`main-blog.liquid` (decisión #52) | No se solapa con `199238025297` — toca archivos `.liquid`/`global.js` distintos a `base.css`. |
| `199238025297` ("Evolucion fundamentos") | Fix de padding del Hero + evolución de fundamentos en `base.css` (decisión #58) + tokenización de colores/espaciados (decisión #60) + tarjeta de catálogo (radio/sombra/kicker OVL) y grid/paginación (decisión #64) — **ya actualizado vía `theme push` (decisión #67), sigue `UNPUBLISHED`** | No se solapa con `199221641297` — toca solo `assets/base.css` y `snippets/product-card.liquid`. |

Como `Nima_Cowork` y `Evolucion fundamentos` tocan archivos distintos sin conflicto,
**se pueden fusionar en un solo duplicado final** antes de publicar, para no perder
ninguno de los dos. Retomar así:

1. **Brey decide el camino:** (a) publicar `Nima_Cowork` y pedirle a Code que reaplique
   la evolución de `base.css` sobre ese mismo theme después, o (b) pedirle a Code que
   fusione los 4 fixes de Cowork sobre `199238025297` primero y publicar un solo
   duplicado consolidado. La opción (b) evita publicar dos veces.
2. **Brey**: previsualizar el duplicado elegido en Shopify → Online Store → Themes antes
   de publicar — aplicar el checklist de coherencia de diseño completo (punto 5 de abajo).
3. **Brey**: confirmar si los precios de Critter Nation ($404.82) y Original Elevated
   Dog Bed ($165.01) son correctos o error de importación (decisiones #51/#53).
4. **Brey**: decidir qué hacer con "1 Teaspoon Measuring Spoon" (sin imagen, nicho
   ambiguo) y si la sección `dual-mode-split` debe seguir `disabled` en el Home.
5. Revisar `GUIA-ESTILO-IMAGENES-NIMA.md` y `PLAN-VENTAS-Y-TRAFICO-NIMA.md` (decisiones
   #54/#55) — son insumos para retomar el tratamiento de imágenes (decisión #49) y las
   promociones/checkout cuando Brey esté listo.
6. Aplicar el checklist de coherencia de diseño completo antes de publicar cualquier
   theme — falta siempre el paso de "publicar y verificar en vivo".

**Ya cerrado en esta sesión** (no repetir):
- Bug "Agotado" en todo el catálogo — resuelto y verificado en vivo (decisión #44).
- Fix de contraste de `magazine-hero.liquid` — publicado por Brey (decisión #38).
- Causa raíz del padding mobile del Hero encontrada y corregida (decisión #45) — falta
  solo publicar.
- Recorte horizontal del Hero en mobile — verificado, no corta a las mascotas, cerrado
  sin necesidad de cambios adicionales (decisión #46).
- Motor de composición automática de Omni probado y descartado para este theme (no sabe
  componer Liquid) — evolución de fundamentos aplicada a mano en su lugar (decisiones
  #57/#58).
- Diagnóstico formal del sistema de diseño (inspección + OVKB) completado, sin implementar
  nada nuevo — ver decisión #59.
- Tokenización de colores/espaciados literales de `base.css` ejecutada y subida al mismo
  duplicado de la decisión #58 — ver decisión #60.
- **13 imágenes generadas por IA encontradas y borradas de los 25 productos activos**
  (una era la destacada de Pet Grooming Gloves) — catálogo 100% con fotos reales del
  proveedor, verificado vía API. Ver decisión #63.
- **Tarjeta de catálogo y grid corregidos**: kicker OVL de emoción visible, radio/sombra
  aplicados (el token existía, no se usaba), gap del grid ampliado, `.pagination` estilizada
  (no tenía CSS). Ver decisión #64.
- **Skill `nima-image-art-direction` renombrado a `checklist-auditoria`**, con procedimiento
  ejecutable de auditoría agregado (no solo criterios a revisar a ojo) — ver decisión #65.
- **[PR #27](https://github.com/francoisbowman-cloud/image-toolkit/pull/27) mergeado y
  verificado en producción** — el bug de Omni/Liquid queda cerrado de punta a punta. Ver
  decisión #66.
- **Duplicado `199238025297` actualizado vía `theme push`** con todo lo anterior — ver
  decisión #67. Sigue pendiente **publicarlo**.

**Para retomar la próxima sesión — punto de entrada directo:**
El duplicado `199238025297` ("Nima — Evolucion fundamentos") ya tiene el código más reciente
subido (radio/sombra/foco, tokenización, tarjeta de catálogo, grid/paginación) — el único
paso que falta es que Brey lo **previsualice y publique** desde el Admin de Shopify (Online
Store → Themes). No hay ninguna decisión de diseño pendiente de confirmación antes de eso.

**Pendientes de tandas anteriores, todavía abiertos:**
- Tratamiento de las 5 imágenes de producto con marca de competidor visible de AutoDS
  (decisión #37, distinto de las imágenes IA de la decisión #63 — estas son fotos reales del
  proveedor pero con branding ajeno/collages de AliExpress) — **en pausa, Brey va a traer un
  plan propio** (decisión #49). No iniciar `imagetoolkit` ni el deploy de `image-server/`
  hasta entonces.
- Conectar ChatGPT (Codex Cloud) al repo de GitHub para pull requests.
- Confirmar si Brey corrigió la configuración de moneda en AutoDS (bug de precios recurrente).
- Decidir cuándo quitar la contraseña del sitio para abrirlo al público (sigue activa,
  decisión #42) — ahora que el mercado primario es Estados Unidos, tiene más sentido
  priorizar esto pronto.

---

## 8. Pendientes / preguntas abiertas
*(Ver sección 7 para el detalle completo y el orden de prioridad — esta lista es solo
un índice rápido.)*
- **Antes de implementar los mockups de Catálogo/Producto (decisión #61) en Liquid real:
  reemplazar las fotos genéricas de los mockups por las fotos reales de los 25 productos**
  — condición explícita de Brey. Depende de resolver primero el tratamiento de las 5 fotos
  crudas de AutoDS (decisión #37/#49, en pausa esperando plan de Brey) para no implementar
  dos veces.
- ~~Revisar y mergear el PR #27 de `image-toolkit`~~ — **cerrado, mergeado y verificado en
  producción (decisión #66)**.
- **Publicar el duplicado `199238025297`** ("Nima — Evolucion fundamentos") — ya actualizado
  vía `theme push` (decisión #67) con todos los fixes acumulados; solo falta que Brey lo
  previsualice y publique. El duplicado `199060881489` (solo fix de padding del Hero) sigue
  superado, no hace falta publicarlo aparte.
- Tratamiento de las 5 fotos de producto con marca de competidor visible de AutoDS — en
  pausa, esperando plan de Brey (decisión #49). Distinto del hallazgo de imágenes IA de la
  decisión #63, ya resuelto.
- Conectar Codex Cloud (ChatGPT) al repo de GitHub — flujo de trabajo nuevo, primer uso.
- Decidir cuándo quitar la contraseña de la tienda para abrirla al público (decisión #42)
  — **explícitamente no tocar todavía, a pedido de Brey (26/07)**.
- Confirmar si Brey corrigió la configuración de moneda en AutoDS (causa raíz del bug
  de precios, recurrente).
- Confirmar que el alias `hola@nima.pet` reenvía correctamente al Gmail real de Brey
  (decisión #43) — pendiente de que Brey lo revise en Shopify/Namecheap.
- **Confirmar de quién es la cuenta de Instagram `@nimapets`** (ya existe, nombre "NIMA
  PETS") — Code no pudo determinarlo sin sesión iniciada (decisión #50).
- Acceso al admin de Shopify (mercados/pagos) y al panel de AutoDS — fuera del alcance
  de Code, requieren login manual de Brey.
- Renombrar el Project de claude.ai "Atlas-Comerce-Lab" → "Atlas-Commerce-Lab" en la UI
  — acción manual de Brey, es lo único que falta de la corrección ortográfica (ver
  decisión #26).
- **Recordatorio operativo:** de acá en adelante, si Design vuelve a tocar el theme
  directo en Shopify, avisar a Code antes de pedirle auditorías — el repo solo refleja
  la realidad si se resincroniza primero (pasó antes: el repo apuntaba a un theme que
  ya no existía).
- **Recordatorio operativo nuevo (25/07):** antes de asumir que un problema reportado por
  Brey es un bug de código, verificar primero contra el theme publicado real y los datos
  de Shopify (Admin API) — el bug "Agotado" de esta sesión parecía de código pero la causa
  real era de configuración de mercado/envío (decisión #41). Mismo criterio aplica a
  cualquier síntoma nuevo: no asumir la causa más obvia sin descartar primero divergencia
  de theme, caché, y configuración de tienda.

---

## 9. Qué revisar antes de publicar el duplicado `198963363921`
- **Magazine (`/pages/magazine`):** el kicker y el título de la sección Hero ahora se leen
  con texto claro sobre la foto de fondo, con un degradado algo más marcado que antes.
  Confirmar que se ve bien tanto con fotos claras como oscuras (el tratamiento solo se
  activa cuando la sección tiene imagen configurada).
- Este duplicado se creó a partir del MAIN ya publicado (decisión #34) — no debería traer
  ninguna otra diferencia visual. Si aparece algo más distinto, avisar a Code antes de
  publicar.

---

*Este documento sigue la plantilla del `PROTOCOLO-comunicacion-actores.md` (v2). Referencia al sistema padre (Atlas Commerce) sin duplicar su contenido — ver sección 5.*
