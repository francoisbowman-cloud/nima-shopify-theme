# Estado del proyecto: Nima
Dominio: `nimapets.com` (comprado y conectado a Shopify — DNS verificado, SSL activo)
Repo: `https://github.com/francoisbowman-cloud/nima-shopify-theme` (privado)
Codename histórico: `PetDrop` (reemplazado — ver decisión #18)
Última actualización: 23 de julio de 2026 — por: Code
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
**Prioridad actual: revisar y publicar la auditoría del theme "Nima — Dirección B".**
Code auditó el theme real publicado (no el que tenía en el repo — Design lo había
reemplazado, ver decisión #31), encontró y corrigió bugs reales de compra, responsive,
traducción y consistencia visual (decisión #32), y subió los fixes a un **duplicado sin
publicar** ("Nima — Dirección B (Auditoría Code)", ID `198934265937`) porque Shopify
bloquea escritura por API sobre el theme MAIN.
Falta ejecutar de parte de Brey:
1. **Previsualizar el duplicado `198934265937` en Shopify y, si aprueba los cambios,
   publicarlo manualmente** (Online Store → Themes → ese theme → "Publicar"). Ver sección 9
   más abajo para qué revisar puntualmente.
2. Conectar ChatGPT (Codex Cloud) al repo de GitHub para que pueda tomar temas nuevos
   y entregarlos como pull request — Code los revisa antes de aplicarlos a Shopify.
3. Confirmar si existen las "adendas v3-v5" del protocolo (`PROTOCOLO-adendas-completas.md`)
   mencionadas en un mensaje reciente — no se encontraron en ninguna carpeta de proyecto
   verificada; si existen, pasárselas a Code para incorporarlas a `AGENTS.md`.
4. Verificar en el checkout real de Shopify que el nombre visible al cliente sea "Nima".
5. Confirmar si ya corrigió la configuración de moneda en AutoDS.

---

## 8. Pendientes / preguntas abiertas
- **Revisar y publicar el duplicado `198934265937`** con los fixes de la auditoría (ver
  sección 9) — sin esto, los bugs corregidos siguen viviendo en el theme publicado real.
- Conectar Codex Cloud (ChatGPT) al repo de GitHub — flujo de trabajo nuevo, primer uso.
- Confirmar existencia real de "adendas v3-v5" / `PROTOCOLO-adendas-completas.md` (ver
  decisión #30) — de no existir, aclarar de dónde salió la referencia para evitar que se
  repita en futuros mensajes.
- Verificar que el checkout muestre "Nima" al cliente (no "Atlas Commerce" ni "PetDrop").
- Quitar la contraseña de la tienda para abrirla al público — decisión de Brey.
- Confirmar si Brey corrigió la configuración de moneda en AutoDS (causa raíz del bug
  de precios, recurrente).
- Verificar disponibilidad de handle "nima"/"nimapets" en redes sociales, si importa
  consistencia de marca entre plataformas.
- Acceso al admin de Shopify (mercados/pagos) y al panel de AutoDS — fuera del alcance
  de Code, requieren login manual de Brey.
- Renombrar el Project de claude.ai "Atlas-Comerce-Lab" → "Atlas-Commerce-Lab" en la UI
  — acción manual de Brey, es lo único que falta de la corrección ortográfica (ver
  decisión #26).
- **Recordatorio operativo:** de acá en adelante, si Design vuelve a tocar el theme
  directo en Shopify, avisar a Code antes de pedirle auditorías — el repo solo refleja
  la realidad si se resincroniza primero (pasó en esta sesión: el repo apuntaba a un
  theme que ya no existía).

---

## 9. Qué revisar antes de publicar el duplicado `198934265937`
- **Producto:** en un producto con Color + otra opción (ej. talla), el selector ahora
  muestra pills con el nombre completo de la variante en vez de círculos de color — antes
  mostraba círculos duplicados sin indicar la opción secundaria. Confirmar que se ve bien.
- **Producto:** la galería ahora muestra también la miniatura de la imagen principal
  (antes no se podía volver a ella tras hacer clic en otra).
- **Contacto (en inglés):** el formulario ahora muestra "Name/Email/Message/Send message"
  en vez de las claves de traducción sin resolver.
- **Blog en mobile:** la grilla de artículos ahora colapsa a una columna en pantallas
  angostas.
- **Catálogo, Búsqueda, Colecciones:** las tarjetas deberían verse visualmente idénticas
  entre sí (mismo estilo de card que ya tenía el Catálogo).
- **Cambio de color/tipografía en el Customizer:** botones, footer y los paneles oscuros
  (Home, Magazine) deberían seguir el color elegido — antes quedaban fijos en negro/blanco
  sin importar la paleta configurada.

---

*Este documento sigue la plantilla del `PROTOCOLO-comunicacion-actores.md` (v2). Referencia al sistema padre (Atlas Commerce) sin duplicar su contenido — ver sección 5.*
