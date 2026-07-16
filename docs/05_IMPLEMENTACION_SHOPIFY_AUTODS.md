# Implementación Shopify + AutoDS

## 1. Arquitectura recomendada

- Shopify como catálogo, checkout, cuentas y pedidos.
- AutoDS para importación, stock, pricing y fulfillment.
- OVL como capa externa o middleware.
- Metafields de Shopify para almacenar esencia y perfil visual.
- Theme app extension para renderizar módulos OVL.
- Headless opcional en una fase posterior.

## 2. Metafields sugeridos

Namespace: `ovl`

- `ovl.dominant_emotion`
- `ovl.functional_benefit`
- `ovl.emotional_benefit`
- `ovl.visual_profile`
- `ovl.story_id`
- `ovl.risk_level`
- `ovl.content_status`
- `ovl.review_status`
- `ovl.editorial_priority`

## 3. Flujo operativo

1. AutoDS importa candidato.
2. Se crea producto como borrador.
3. OVL analiza.
4. Se genera propuesta.
5. Revisión humana.
6. Se cargan assets aprobados.
7. Se asigna plantilla.
8. Se publica.
9. Se monitoriza rendimiento.

## 4. Plantillas Shopify

- `product.utility`
- `product.hybrid`
- `product.editorial`
- `collection.utility`
- `page.magazine`
- `article.ovl`
- `landing.problem`
- `landing.campaign`

## 5. Automatizaciones

- Clasificación inicial.
- Etiquetado.
- Detección de imágenes pobres.
- Generación de borrador de copy.
- Sugerencia de perfil OVL.
- Creación de bloques.
- Adaptación a redes.
- Monitor de stock.
- Alerta de cambio de proveedor.
- Detección de claim riesgoso.

## 6. Revisión humana

No automatizar totalmente:

- Selección final.
- Verificación de materiales.
- Verificación de talla.
- Claims de salud.
- Uso seguro.
- Calidad de imagen.
- Política de devoluciones.
- Servicio al cliente.

## 7. Integraciones futuras

- Klaviyo.
- Meta.
- Pinterest.
- Google Merchant Center.
- Analytics.
- Search Console.
- Motor de recomendación.
- Personalización.
- DAM.
- PIM.
