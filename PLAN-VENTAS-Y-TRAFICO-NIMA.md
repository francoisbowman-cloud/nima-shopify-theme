# Nima — Plan de ventas y de atracción de tráfico

Basado en el catálogo real verificado hoy (25 productos activos, USD, envío solo EE.UU., pago único PayPal Business, operador único: Brey). No incluye acciones que requieran presupuesto de ads ni apps de pago adicionales, salvo que se marque explícitamente como opcional.

---

## Bloque 4 — Plan de ventas

### 1. Estructura de precios — hallazgo urgente primero

El catálogo tiene una dispersión de precio muy grande: la mayoría de los 14 productos originales están entre $5.99 y $22.56, pero 2 de los 11 productos agregados el 26/07 rompen ese rango — Critter Nation cage a $404.82 y Original Elevated Dog Bed a $165.01. Antes de diseñar cualquier promoción, confirmar si esos precios son correctos (pueden ser errores de importación de AutoDS, el mismo tipo de bug que ya pasó una vez con el Christmas Bandana a $869.80 por confusión DOP→USD). Si son correctos, tratarlos como una categoría de precio distinta (ver punto 3) en vez de mezclarlos con el resto del catálogo en la misma promoción.

### 2. Tiers de precio sugeridos (una vez confirmados los precios reales)

- **Entrada ($5–15):** la mayoría del catálogo — accesorios, juguetes, higiene. Es el volumen principal de conversión por impulso.
- **Medio ($15–25):** grooming, camas pequeñas, correas largas.
- **Premium ($100+):** jaulas grandes, camas elevadas de marca. Si se confirman, necesitan su propia página/tratamiento (más fotos, más confianza — reseñas, garantía) porque el ticket promedio es 10-40x el resto del catálogo y el comprador de ese tier compra distinto.

### 3. Mecánicas de upsell/cross-sell sin apps de pago

Shopify Basic permite nativamente, sin apps adicionales:

- **Descuento por cantidad vía código automático:** crear un descuento automático "Compra 2, 10% off" o "Compra 3, 15% off" aplicable a toda la tienda o a colecciones específicas (ej. juguetes, accesorios de paseo) — se configura en Descuentos → Automático, no requiere app.
- **Bundles manuales como producto propio:** crear un producto "combo" (ej. Dog Leash + Poop Bag Holder + Grooming Gloves) con su propia ficha y precio con descuento leve frente a comprar por separado. Es 100% nativo (solo requiere crear el producto), pero pierde inventario sincronizado automáticamente con AutoDS — hay que actualizarlo a mano si el proveedor cambia.
- **Free shipping threshold:** ya existe el copy "Envío gratis desde $50" en `announcement-bar.liquid` (hallazgo del Bloque 1) — confirmar si es política real. Si el ticket promedio actual es ~$15-20, ese umbral empuja a añadir un segundo producto al carrito, que es la forma más simple de subir AOV sin tocar nada más.
- **Cross-sell en la ficha de producto:** Shopify permite "productos relacionados" nativamente en `main-product.liquid` vía `product.metafields` o recomendaciones automáticas (`{% recommendations %}` de Shopify, sin app). No está implementado hoy — es una mejora de bajo esfuerzo a futuro.

### 4. Fricción de checkout — PayPal como único método

Es el mayor riesgo de conversión del negocio ahora mismo. Con PayPal Business en modo checkout de invitado, la mayoría de compradores no necesitan cuenta PayPal (pueden pagar con tarjeta), pero:

- El branding del botón sigue diciendo "PayPal" primero, lo que genera fricción en compradores que no confían en PayPal o no lo reconocen como "pago con tarjeta".
- No hay Apple Pay / Google Pay / Shop Pay disponibles — estos suelen subir conversión mobile 10-20% en dropshipping porque eliminan el paso de tipear datos de tarjeta.
- **Acción de bajo costo:** verificar en el panel de PayPal Business si está habilitado "PayPal advanced checkout" o similar, que a veces permite mostrar el formulario de tarjeta directo sin salir a PayPal — reduce la fricción sin agregar un segundo procesador.
- Esto no se puede resolver solo con Cowork — requiere revisar configuración de cuenta PayPal, que es acceso de Brey.

---

## Bloque 5 — Plan de atracción de tráfico

### 1. SEO on-page — auditoría básica

Con el catálogo ya revisado en el Bloque 2, quedan pendientes específicos de SEO:
- **Meta descriptions:** Shopify genera un fallback automático desde la descripción del producto si no se define una manualmente — con las descripciones ya limpiadas de contenido de scraping, el fallback debería ser razonable, pero vale revisar los 6 productos que se reescribieron en el Bloque 2 y confirmar que las primeras ~155 caracteres de la nueva descripción funcionan bien como meta description.
- **Alt text de imágenes:** cuidado explícito de no exponer el proveedor de dropshipping — revisar que ningún alt text generado automáticamente por Shopify incluya nombres de archivo de AutoDS/AliExpress (esto pasa cuando el alt queda vacío y Shopify usa el nombre del archivo original como fallback). Es un chequeo rápido vía Admin, producto por producto.
- **Títulos de producto:** varios títulos son literalmente el título del listing de AliExpress/AutoDS (largos, llenos de keywords tipo "Stainless Straight Curved Thinning Shears Trimmer Kits") — funcionan para SEO long-tail pero no para marca. No es urgente cambiarlos (son buenos para búsqueda), pero si se quiere una tienda con más identidad de marca a futuro, es una tarea de copywriting, no de código.

### 2. Redes sociales y Magazine — bajo costo, un solo operador

- **Reutilizar el Magazine ya existente:** la tienda ya tiene la sección Magazine con historias editoriales — cada historia nueva es contenido reciclable para Instagram/TikTok sin producción adicional (recortar el texto + la imagen ya tratada con el pipeline Omni).
- **AutoDS Product Finding Hub (ya comprado):** usar Trending Products para detectar qué SKUs del nicho pet wellness están teniendo tracción antes de decidir qué destacar en Home/Magazine — no para expandir catálogo fuera del nicho, sino para priorizar cuáles de los 25 productos actuales promocionar primero. TikTok Analytics del mismo addon sirve para ver qué formato de video funciona en nicho mascotas sin gastar en pauta paga todavía.
- **Cadencia realista para operador único:** 2-3 publicaciones por semana reciclando contenido del Magazine es sostenible; more no lo es sin ayuda. Priorizar calidad de las fotos de producto (Bloque 3 de este ticket) antes que frecuencia de posteo — con fotos de AutoDS sin tratar, cualquier tráfico social que llegue al sitio choca contra el catálogo sin curar.
- **Cuenta @nimapets ya existe** (hallazgo previo, decisión #50 del ESTADO) — sigue sin confirmarse si es propia. Resolver esto es prerequisito antes de invertir tiempo en contenido para Instagram con ese handle.

### 3. Prioridad sugerida (impacto/costo)

1. Confirmar/corregir los 2 precios atípicos (Critter Nation, Elevated Dog Bed) — gratis, urgente.
2. Terminar el tratamiento de imágenes de producto (Bloque 3 de este ticket, guía ya entregada) — impacta directo en conversión y en si vale la pena mandar tráfico social.
3. Confirmar el umbral real de envío gratis y activarlo como descuento automático — gratis, sube AOV.
4. Confirmar cuenta de Instagram y arrancar cadencia de 2-3 posts/semana reciclando Magazine — gratis, requiere tiempo de Brey.
5. Revisar advanced checkout de PayPal para reducir fricción — gratis, requiere acceso de Brey a su cuenta PayPal.
6. Bundles manuales para los 2-3 productos con mejor rotación — bajo esfuerzo, sube AOV.

---

*No se tocó ninguna configuración de Shopify (descuentos, checkout, apps) en la elaboración de este plan — es un documento de recomendación para que Brey decida qué ejecutar y en qué orden.*
