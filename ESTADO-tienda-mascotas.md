# Estado del proyecto: Nima
Dominio: `nimapets.com` (comprado y conectado a Shopify — DNS verificado, SSL activo)
Repo: `https://github.com/francoisbowman-cloud/nima-shopify-theme` (privado)
Codename histórico: `PetDrop` (reemplazado — ver decisión #18)
Última actualización: 25 de julio de 2026 — por: Code
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
| 45 | **Auditoría de imágenes de fondo/hero recortadas — causa raíz encontrada y fix aplicado (parcial).** Brey reportó el Hero de Home con una franja vacía de fondo crema arriba y las caras del gato/perro cortadas abajo. Cobertura completa: grep de `background-image`/`object-fit`/`background-size` sobre las 22 secciones + `base.css` — solo 4 archivos usan imagen de fondo (`hero.liquid` vía `base.css`, `magazine-hero.liquid`, `magazine-grid.liquid`, `main-blog.liquid`). Causa raíz real confirmada por inspección del DOM en vivo (no por captura de pantalla — el screenshot del navegador falló en esta sesión): `.hero-copy` tenía `padding:80px ...80px` **fijo, sin reducir en el media query de mobile** (`@media(max-width:800px)`), generando un bloque de ~545px de alto antes de la imagen — la "franja vacía". Corregido: agregado `.hero-copy{padding:48px 24px}` dentro del breakpoint mobile existente. Las otras 3 secciones (`magazine-hero`, `magazine-grid`, `main-blog`) usan el mismo patrón `background-size:cover` pero con altura controlada por padding/min-height razonable, sin el mismo bug — revisadas, sin cambios necesarios. **Pendiente sin resolver:** el recorte horizontal de la imagen del hero en viewports angostos (`object-position:center` por defecto sobre una foto panorámica 1400×933 forzada a un contenedor casi cuadrado en mobile, hasta ~45% de recorte de ancho) — no se pudo confirmar visualmente si esto corta a las mascotas porque la herramienta de captura de pantalla no funcionó en esta sesión; Brey debe revisar en el sitio (mobile y desktop) tras publicar el fix y confirmar si además hace falta ajustar `object-position`. Fix subido a un **nuevo theme duplicado sin publicar** ("Nima — Fix hero mobile padding (Code)", ID `199060881489`), duplicado desde el MAIN actual (`198963363921`) — **pendiente que Brey lo revise y publique** | Code |

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

## 6. Estado del catálogo (auditoría de contenido, 19/07)

**14 productos activos.** Tras un hallazgo de Code (marcas de competidores coladas
por scraping de AutoDS en 2 productos), Chat auditó el catálogo completo. Resultado:

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

**Sin confirmar todavía:** si Brey corrigió la configuración de moneda dentro de
AutoDS — causa raíz del bug de precio, que ya se repitió dos veces. Verificar antes
de la próxima importación.

---

## 7. Próximo paso
**Prioridad actual: previsualizar y publicar el duplicado `199060881489` con el fix de
padding mobile del Hero (decisión #45), y confirmar visualmente si además hace falta
ajustar el encuadre horizontal de la imagen.**

Retomar así:
1. **Brey**: previsualizar el theme `199060881489` ("Nima — Fix hero mobile padding
   (Code)") en Shopify → Online Store → Themes, revisar el Home en mobile (real o
   simulado, ancho <800px) — la franja vacía sobre la imagen debería haber desaparecido.
   Si se ve bien, publicar.
2. **Revisar con más cuidado, en mobile y en desktop angosto (~900-1150px):** si la foto
   del hero (`01-hero.png`, gato + perro lado a lado) corta a los animales por los bordes
   — no se pudo confirmar visualmente en esta sesión porque la herramienta de captura de
   pantalla del navegador falló repetidamente ("Browser pane is not displayed"). Si se
   confirma que sí corta mal, decirle a Code el punto exacto (¿se corta la oreja del gato?
   ¿la cara del perro?) para ajustar `object-position` en `.hero-art img` con precisión,
   en vez de adivinar.
3. Aplicar el checklist de coherencia de diseño completo antes de cerrar (cobertura ya
   hecha esta sesión — ver decisión #45 — falta el paso de "publicar y verificar en vivo").

**Ya cerrado en esta sesión** (no repetir):
- Bug "Agotado" en todo el catálogo — resuelto y verificado en vivo (decisión #44).
- Fix de contraste de `magazine-hero.liquid` — publicado por Brey (decisión #38).
- Causa raíz del padding mobile del Hero encontrada y corregida (decisión #45) — falta
  solo publicar.

**Pendientes de tandas anteriores, todavía abiertos:**
- Decidir cómo resolver las 5 imágenes de producto crudas de AutoDS (decisión #37) — en
  particular Dog Dental Bone Treats, que muestra el empaque de un competidor real
  ("Minties"). Hay dos caminos evaluados esta sesión: la tool MCP `imagetoolkit` (limitada,
  ver decisión #39) o el servicio propio `image-server/` (armado, no desplegado — ver
  decisión #40, requiere que Brey lo despliegue en Railway).
- Conectar ChatGPT (Codex Cloud) al repo de GitHub para pull requests.
- Confirmar existencia real de las "adendas v3-v5" del protocolo — no encontradas.
- Verificar en el checkout real que el nombre visible al cliente sea "Nima".
- Confirmar si Brey corrigió la configuración de moneda en AutoDS (bug de precios recurrente).
- Decidir cuándo quitar la contraseña del sitio para abrirlo al público (sigue activa,
  decisión #42) — ahora que el mercado primario es Estados Unidos, tiene más sentido
  priorizar esto pronto.

---

## 8. Pendientes / preguntas abiertas
*(Ver sección 7 para el detalle completo y el orden de prioridad — esta lista es solo
un índice rápido.)*
- **Publicar el duplicado `199060881489`** con el fix de padding mobile del Hero, y
  confirmar visualmente si además hace falta ajustar `object-position` de la imagen
  (decisión #45).
- Decidir el tratamiento para las 5 imágenes de producto crudas de AutoDS (decisión #37).
- Desplegar `image-server/` en Railway si se opta por ese camino para el punto anterior
  (decisión #40) — o descartarlo si Brey prefiere re-sourcear fotos manualmente.
- Conectar Codex Cloud (ChatGPT) al repo de GitHub — flujo de trabajo nuevo, primer uso.
- Confirmar existencia real de "adendas v3-v5" / `PROTOCOLO-adendas-completas.md` (ver
  decisión #30) — de no existir, aclarar de dónde salió la referencia para evitar que se
  repita en futuros mensajes.
- Verificar que el checkout muestre "Nima" al cliente (no "Atlas Commerce" ni "PetDrop").
- Decidir cuándo quitar la contraseña de la tienda para abrirla al público (decisión #42).
- Confirmar si Brey corrigió la configuración de moneda en AutoDS (causa raíz del bug
  de precios, recurrente).
- Confirmar que el alias `hola@nima.pet` reenvía correctamente al Gmail real de Brey
  (decisión #43) — pendiente de que Brey lo revise en Shopify/Namecheap.
- Verificar disponibilidad de handle "nima"/"nimapets" en redes sociales, si importa
  consistencia de marca entre plataformas.
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
