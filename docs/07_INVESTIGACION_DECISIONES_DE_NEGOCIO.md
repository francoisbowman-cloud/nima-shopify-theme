# 07 — Investigación de decisiones de negocio pendientes

Documento preparado por Code (sesión del 17 de julio de 2026, RFC-007) para que Brey
decida y ejecute con la menor fricción posible. Ninguna de las acciones de este
documento fue ejecutada — Code no tiene acceso de login al admin de Shopify ni a
AutoDS; todo lo de abajo es investigación y recomendación, lista para copiar/pegar
o para guiar una revisión manual.

Nota metodológica: para las secciones 1 y 2 sí tuve acceso de **solo lectura** a la
tienda `petdrop-9236.myshopify.com` a través del conector de Shopify ya autorizado en
esta sesión (confirmé primero con `get-shop-info` que apuntaba a PetDrop y no a
Flexta/My Store 3/Mi tienda/Mi tienda 5, antes de consultar nada). No hice ninguna
escritura — ni creación, ni edición, ni cambio de estado de productos.

---

## 0. Lista final de acciones manuales (en orden)

Todo lo técnico que yo podía hacer ya está hecho y commiteado. Esto es lo que queda
para vos — con login manual (Shopify admin y/o AutoDS) o desde tu terminal. Están en
el orden en que tiene más sentido hacerlas. Cada paso incluye qué es y por qué hace
falta, sin dar por sentado que ya conocés la jerga.

1. **Revisar en AutoDS las 4 imágenes faltantes** (ver sección 1 abajo) y decidir
   qué hacer con cada producto. AutoDS es el panel donde administrás los productos
   que se importan automáticamente desde proveedores — ahí vas a poder ver si el
   proveedor original tiene fotos o no.
2. **Revisar en AutoDS el desfase de 15 vs 13 productos** (sección 2) usando la
   lista de 13 que te dejo, para encontrar cuáles 2 nunca llegaron a Shopify.
3. ~~**Decidir moneda: DOP o USD**~~ — **Hecho (17/07/2026).** Brey cambió la moneda
   de la tienda a USD desde el admin de Shopify, siguiendo la recomendación de abajo.
   Confirmado por API.
4. **Configurar el mercado "Estados Unidos"** (sección 4): **Configuración →
   Mercados** en el admin de Shopify. "Mercado" es el término que usa Shopify para
   una región de venta (moneda, idioma, métodos de pago propios de esa región). Con
   uno solo (EE.UU.) alcanza por ahora.
5. **Agregar un método de pago** (sección 4): como Shopify Payments no está
   disponible para comercios en RD, hay que agregar un proveedor externo desde
   **Configuración → Pagos**. Te recomiendo empezar con PayPal (buscalo en la lista
   de proveedores de terceros que ofrece Shopify ahí mismo).
6. **Pegar las políticas de envío y devolución** (sección 4): **Configuración →
   Políticas**, dos campos de texto donde pegás los borradores en inglés que te dejé
   ya redactados.
7. **Correr el push del theme a Shopify** (todo el código ya está commiteado en este
   repo). Desde una terminal, parado en la carpeta `theme/` del repo, corré:
   ```
   shopify theme push --store=petdrop-9236.myshopify.com --theme=198713933905
   ```
   Esto sube los archivos del theme (Liquid/CSS/JS) al borrador `PetDrop_OVL` en
   Shopify. La CLI te va a pedir loguearte con tu cuenta de Shopify la primera vez
   (se abre el navegador) — es normal, solo tenés que aceptar.
8. **Confirmar visualmente** que todo se ve bien en el preview:
   `petdrop-9236.myshopify.com?preview_theme_id=198713933905` — revisá home,
   producto, Magazine y carrito.

---

## 1. Imágenes faltantes en 4 productos

Confirmado por API (no es un problema de theme ni de caché del navegador): los 4
productos tienen **cero imágenes** cargadas en la biblioteca de medios de Shopify
(`images: []`, `featuredMedia: null`). No es que el theme no las muestre — Shopify
no tiene ningún archivo de imagen asociado a estas fichas.

| Producto | Handle | Estado |
|---|---|---|
| Premium Cat Litter Mat... | `premium-cat-litter-mat-...` | Draft, sin imagen |
| Dog Birthday Hat, Blue Birthday Boy Bandana... | `dog-birthday-hat-...` | Draft, sin imagen |
| Dog Car Seat Cover... | `dog-car-seat-cover-...` | Draft, sin imagen |
| Dog Water Bottle, Leak Proof Portable... | `dog-water-bottle-...` | Draft, sin imagen |

**Qué revisar en AutoDS (pregunta exacta):** para cada uno de estos 4 SKUs, abrir la
ficha del proveedor de origen en AutoDS y confirmar si el proveedor **sí** tiene fotos
del producto que no se sincronizaron al importar (bug de sync — se podría reintentar
la importación de medios), o si el proveedor **nunca tuvo fotos propias** en su
listado (pasa seguido con proveedores de dropshipping de catálogo genérico).

**Recomendación:** un producto sin imagen no debería pasar de `Draft` a `Active`. Si
al revisar en AutoDS el proveedor no tiene fotos, hay dos caminos — cuál usar es
decisión de producto, no técnica:
- (a) conseguir/generar imágenes propias antes de publicar (foto de stock del tipo de
  producto, o un render genérico), o
- (b) dejar estos 4 archivados hasta conseguir imagen real.

---

## 2. Desfase de conteo AutoDS → Shopify

Confirmado por API: la tienda tiene **exactamente 13 productos en total** — 9 en
`Draft` y 4 en `Archived`. Ningún producto está `Active` en este momento.

Esto no coincide con el número que traía el registro previo ("11 productos
importados... revertidos de Active a Draft" en `CHANGELOG.md`) — el conteo real de
`Draft` hoy es 9, no 11. Y de los 15 que se dicen importados en AutoDS, en Shopify
solo existen 13 en cualquier estado (activo, draft o archivado): **faltan 2 por
completo**, ni siquiera como borrador.

Lista completa de los 13 productos que sí existen en Shopify (para cruzar contra tu
lista de 15 en AutoDS y encontrar cuáles 2 no llegaron):

**Draft (9):**
1. Anti-Splash Water Bowl for Dogs 1L...
2. Crate Water Bowl for Dogs & Cats No-Spill...
3. Dog Birthday Hat, Blue Birthday Boy Bandana...
4. Dog Car Seat Cover, Back Seat Cover for Dogs...
5. Dog Dental Bone Treats, Tiny/Small...
6. Dog Poop Bag Holder and Dispenser...
7. Dog Water Bottle, Leak Proof Portable...
8. Foam Soccer Balls Cat Toys - Pack of 12
9. Premium Cat Litter Mat...

**Archived (4):**
10. Dog Clothes Puppy Shirts "I Love My Mom"...
11. Prime Fresh and Saltwater Conditioner...
12. Reflective Service Dog in Training Patches...
13. Selenium - 200 Mcg...

**Qué revisar en AutoDS (pregunta exacta):** en el historial/log de la importación
de esos 15 productos, filtrar por errores o estados "failed"/"not pushed" — buscá
específicamente 2 SKUs que no aparezcan en la lista de 13 de arriba. Las causas
típicas en AutoDS son: producto marcado "unavailable" por el proveedor justo al
momento de sincronizar, error de mapeo de variante, o límite de plan alcanzado
durante el batch de importación.

**Nota honesta:** no puedo cerrar esta pregunta del todo sin ver la lista original
de 15 en AutoDS — lo que sí puedo confirmarte con certeza es el número real y la
lista real del lado de Shopify (arriba), que es distinto al que veníamos usando.

---

## 3. Moneda: DOP vs USD — recomendación

**✅ Resuelto (17/07/2026):** Brey cambió la moneda de la tienda a USD, siguiendo la
recomendación de abajo. Confirmado por API — `currencyCode` de la tienda es ahora `USD`.
Se deja el razonamiento completo como registro de por qué se tomó esta decisión.

**Estado antes del cambio:** la tienda estaba configurada en pesos dominicanos (DOP).

**Hallazgo clave (documentación pública de Shopify):** Shopify Payments **no está
disponible para comercios registrados en República Dominicana** — no figura en la
lista de países soportados. Esto es independiente de en qué moneda esté la tienda:
sea DOP o USD, el gateway principal no puede ser Shopify Payments nativo; hace falta
un proveedor de pago de terceros (ver sección 4).

**Recomendación: cambiar la moneda de la tienda de DOP a USD.** Razones:

1. **100% del mercado de envío es EE.UU.** — mostrarle a un comprador en EE.UU. un
   precio convertido de DOP a USD en pantalla (ej. "$47.32" en vez de un precio
   redondo como "$45.00") genera fricción y desconfianza en el checkout.
2. **Sincronización con AutoDS**: los productos de este catálogo vienen de
   proveedores que cotizan en USD. Mantener la tienda en DOP obliga a una conversión
   extra en cada sincronización de precio, con riesgo de error de redondeo y de
   desfase cuando cambia el tipo de cambio DOP/USD.
3. **Liquidación del gateway de pago**: los proveedores de terceros recomendados
   para RD (PayPal, Payoneer Checkout — ver sección 4) liquidan naturalmente en USD.
   Cobrar en DOP para terminar liquidando en USD agrega una capa de conversión de
   cambio que reduce margen sin necesidad.
4. **Cambio técnicamente simple y sin riesgo para el theme**: la moneda de la tienda
   se cambia en Configuración → General → Moneda de la tienda. Ningún precio está
   hardcodeado en el theme — todos pasan por el filtro `money` de Liquid, que se
   ajusta solo al formato de la moneda configurada.

**Contra a confirmar (no técnico):** si hay obligaciones contables/fiscales en
República Dominicana que requieran declarar en DOP, es una pregunta para un contador
local — no es una limitación de Shopify ni del theme.

Fuentes consultadas: [Shopify Help Center — Supported countries for Shopify Payments](https://help.shopify.com/en/manual/payments/shopify-payments/supported-countries),
[Shopify Help Center — Multi-currency](https://help.shopify.com/en/manual/payments/shopify-payments/store-currency/multi-currency).

---

## 4. Mercados, pagos y políticas — propuesta inicial

Configuración inicial razonable para una tienda dropshipping operada desde República
Dominicana con envíos exclusivamente a EE.UU. Todo lo de abajo es una propuesta —
podés pegarla directamente en el admin si estás de acuerdo, o pedirme que ajuste
algo antes.

### Mercados
- Activar **un solo mercado: Estados Unidos** (Configuración → Mercados). No hace
  falta abrir más mercados todavía — el 100% del catálogo/envío está pensado para
  EE.UU. Agregar mercados nuevos (ej. Canadá) es una decisión futura, no de esta etapa.

### Métodos de pago
Dado que Shopify Payments no está disponible para RD (sección 3):
- **Principal: PayPal** — es el método más reconocido y confiable para compradores
  en EE.UU., y opera sin problema para comercios registrados en RD. Se activa desde
  Configuración → Pagos → agregar PayPal.
- **Secundario: Payoneer Checkout** — alternativa con soporte específico para
  comercios dominicanos, permite además aceptar tarjeta directamente si un comprador
  no quiere usar PayPal.
- No recomiendo métodos locales dominicanos (ej. Banco Popular) — están pensados
  para compradores en RD, no aplican acá porque el mercado es 100% EE.UU.

### Política de envío (borrador en inglés, listo para pegar en Configuración → Políticas → Política de envío)

> **Shipping Policy**
>
> We currently ship to customers within the United States only.
>
> - **Free shipping** on all orders over $50.
> - Estimated delivery time: 3–7 business days from the date your order ships.
> - You'll receive a tracking number by email as soon as your order is on its way.
> - Orders are processed within 1–2 business days before shipping.
>
> If your order hasn't arrived within the estimated window, contact us and we'll
> look into it right away.

### Política de devoluciones (borrador en inglés, listo para pegar en Configuración → Políticas → Política de reembolso)

> **Return & Refund Policy**
>
> We want you to be happy with your purchase. If you're not fully satisfied, you can
> return most items within **30 days** of delivery for a refund or exchange.
>
> - Items must be unused, in their original packaging, and in the condition you
>   received them.
> - To start a return, contact us with your order number and we'll send you
>   instructions.
> - Refunds are issued to your original payment method once we receive and inspect
>   the returned item.
> - Return shipping costs are the customer's responsibility unless the item arrived
>   damaged or defective.
>
> Damaged or incorrect items: contact us within 7 days of delivery with a photo of
> the item, and we'll replace it or issue a full refund at no extra cost to you.

Este texto ya es consistente con lo que el theme comunica hoy ("Envío gratis desde
$50 · Devoluciones fáciles en 30 días" en `main-product.liquid`) — no haría falta
tocar el código del theme para que las políticas y el mensaje en la ficha de
producto coincidan.
