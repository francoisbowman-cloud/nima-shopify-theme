# Nima — Production Readiness Gate

Estado consolidado de storefront: `main`

PR de lanzamiento: `#4 — Nima production readiness launch` — **MERGED**

Merge commit: `d7c118872f089b4182aff6e1b065e990d88b27a9`

Último commit de hardening comercial posterior al merge: `fb35af45a53942b57ba5460cb3a66b54c56f8449`

## Objetivo

Mover Nima desde una tienda técnicamente funcional hacia una experiencia lista para recibir tráfico y aprender de ventas reales, sin degradar su identidad editorial ni introducir dependencias pagas innecesarias.

## Cerrado en código

### EN/ES
- Announcement bar usa locale keys.
- Copy operativo de colección, PDP, búsqueda, contacto y password cubierto por locales EN/ES.
- Nuevos bloques de lanzamiento tienen copy EN/ES nativo.
- Se eliminó del theme la promesa no verificada `Free shipping from $50` / `Envío gratis desde $50`.
- Se eliminó la afirmación no verificada de devoluciones garantizadas en 30 días. La PDP remite ahora a la política real de devoluciones.

### Home — commerce bridge
- Nueva sección `editorial-shop-window` inmediatamente después del hero.
- Fallback automático a `collections['all']`; no requiere configuración manual para mostrar producto.
- Usa `product-card` existente y conserva la dirección editorial.
- Desktop, tablet y mobile contemplados en `launch.css`.

### PDP — cross-sell sin apps
- Nueva sección `product-routine-cross-sell` al final de la ficha.
- Prioriza la primera colección del producto y excluye el SKU actual.
- Fallback real a `collections['all']` si la primera colección no aporta productos alternativos.
- Máximo configurable 2–4 productos.
- Sin AJAX, sin app, sin coste adicional.

### Dirección visual de lanzamiento
- `launch.css` es una capa aditiva y reversible.
- Refuerza jerarquía editorial, espacios, tipografía y composición sin convertir Nima en un e-commerce genérico.
- Product media de los nuevos módulos se presenta sobre blanco, compatible con la política commerce-primary de Catalog AI v0.3.1.

### Contratos de lanzamiento
- `tests/test_launch_theme_contract.py` comprueba referencias section/template, paridad EN/ES, translation keys, orden de carga CSS, jerarquía Home/PDP y fallbacks del catálogo.
- `.github/workflows/theme-validation.yml` define Theme Check + validación JSON.
- `.github/workflows/launch-contract.yml` define ejecución de los contratos de lanzamiento.

## Estado de CI

Los workflows están definidos, pero GitHub no inició ejecuciones ni en la rama, ni en PR, ni después del merge a `main`. La integración disponible tampoco tiene permiso suficiente para administrar Actions (`403`). Por tanto:

- **NO** se reclama que Theme Check haya corrido sobre el storefront de lanzamiento.
- **NO** se reclama que los contratos pytest hayan corrido en GitHub.
- Los checks quedan reproducibles para el primer entorno con Actions/CLI disponible.

## Evidencia comercial revisada

### Mercado y pago

Estado histórico verificado del proyecto:
- mercado objetivo/activo: Estados Unidos;
- moneda: USD;
- PayPal Business configurado como procesador principal;
- dominio `nimapets.com` conectado a Shopify en la configuración histórica documentada.

Estos puntos necesitan un smoke test actual antes de tráfico, pero ya no son decisiones abiertas de arquitectura.

### Shipping

La evidencia histórica del proyecto registra una tarifa `Free Shipping` de `$0.00 USD` en los perfiles de envío a Estados Unidos. Como el theme había evolucionado a una promesa de `Free shipping from $50` sin evidencia equivalente, el copy se hizo deliberadamente conservador:

- EN: `Shipping within the United States · Secure checkout`
- ES: `Envíos dentro de Estados Unidos · Checkout seguro`

El checkout real sigue siendo la autoridad final sobre precio y disponibilidad de envío.

### Precios premium

El catálogo aprobado del 3 de agosto muestra:

- Original Elevated Dog Bed: venta `$165.01`, coste `$133.13` — margen bruto sobre coste aproximado de 23.9%.
- Critter Nation Double Unit: venta `$404.82`, coste `$326.98` — margen bruto sobre coste aproximado de 23.8%.

Conclusión: ambos precios atípicos son internamente coherentes con sus costes y no presentan la firma del bug histórico DOP→USD. Aun así, el precio vivo de Shopify debe comprobarse en el smoke test previo a tráfico.

## Catalog AI v0.3.1 — estado separado

Rama: `fix/nima-catalog-ai-v031-production-image-readiness`

- Política `commerce-primary = #FFFFFF` implementada.
- Lifestyle/in-use permanece contextual/editorial.
- Halo dominante reducido y causa raíz aislada.
- Edge matte residual implementado en rama, pero NO declarado validado todavía sobre el feeding-mat real porque el source local de `nima-catalog-images/` no está disponible en este entorno.
- Este caso no bloquea el storefront si las imágenes prioritarias elegidas para lanzamiento ya están limpias; sí bloquea declarar Catalog AI v0.3.1 completamente cerrado.

## Gates externos restantes antes de publicar/acelerar tráfico

1. Ejecutar `theme check theme --fail-level error` sobre el `main` actual.
2. Ejecutar `pytest -q tests/test_launch_theme_contract.py`.
3. Renderizar el `main` actual en un preview Shopify real y revisar Home/Collection/PDP en desktop y mobile.
4. Confirmar que EN y ES no muestran claves crudas y que announcement bar cambia correctamente.
5. Confirmar en checkout que Estados Unidos es shippable y que el precio de envío coincide con la configuración real.
6. Confirmar PayPal Business y guest/card checkout en producción.
7. Completar una compra controlada de punta a punta con un SKU normal y dirección válida de EE.UU.
8. Confirmar que el pedido aparece en Shopify Admin y sincroniza con AutoDS.
9. Confirmar email/order-status y cancelar/reembolsar el pedido de prueba si no debe cumplirse.
10. Confirmar que Shopify Analytics observa sesión, add-to-cart, checkout y purchase; registrar baseline.
11. Publicar el theme validado y repetir smoke test en el dominio live.
12. Validar por separado el residual edge matte de Catalog AI con el feeding mat real cuando el asset esté disponible.

## Gate de salida a ventas

Nima puede pasar a tráfico real cuando:

- el theme actual pasa validación técnica y visual en Shopify;
- checkout real funciona en EE.UU.;
- shipping/políticas mostradas coinciden con la realidad;
- PayPal procesa la compra controlada;
- AutoDS recibe/sincroniza correctamente el pedido;
- Shopify Analytics registra el funnel mínimo;
- las imágenes principales elegidas para lanzamiento representan fielmente el producto.

A partir de ese punto, la prioridad cambia de construcción a:

`tráfico → conversión → analítica → aprendizaje → optimización → escalado`.

## Restricciones de lanzamiento

- No instalar tracking duplicado antes de verificar Shopify Analytics nativo.
- No añadir apps de pago por defecto sin una necesidad observada.
- No consumir generación de imagen sólo para validar layout.
- No sacrificar identidad editorial por patrones genéricos de marketplace.
- No incrementar pauta si checkout, shipping o fulfillment fallan.
