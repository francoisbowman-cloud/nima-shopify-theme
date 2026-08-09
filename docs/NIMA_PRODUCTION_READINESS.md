# Nima — Production Readiness Gate

Branch de trabajo: `feat/nima-production-readiness-launch`
Base: `fix/theme-en-es-locale-audit` (derivada de `main` `6a48a20`)

## Objetivo

Mover Nima desde una tienda técnicamente funcional hacia una experiencia lista para recibir tráfico y aprender de ventas reales, sin degradar su identidad editorial ni introducir dependencias pagas innecesarias.

## Cerrado en código

### EN/ES
- Announcement bar usa locale keys.
- Copy operativo de colección, PDP, búsqueda, contacto y password cubierto por locales EN/ES.
- Nuevos bloques de lanzamiento tienen copy EN/ES nativo.

### Home — commerce bridge
- Nueva sección `editorial-shop-window` inmediatamente después del hero.
- Fallback automático a `collections['all']`; no requiere configuración manual para mostrar producto.
- Usa `product-card` existente y conserva la dirección editorial.
- Desktop, tablet y mobile contemplados en `launch.css`.

### PDP — cross-sell sin apps
- Nueva sección `product-routine-cross-sell` al final de la ficha.
- Prioriza la primera colección del producto y excluye el SKU actual.
- Fallback a catálogo general.
- Máximo configurable 2–4 productos.
- Sin AJAX, sin app, sin coste adicional.

### Dirección visual de lanzamiento
- `launch.css` es una capa aditiva y reversible.
- Refuerza jerarquía editorial, espacios, tipografía y composición sin convertir Nima en un e-commerce genérico.
- Product media de los nuevos módulos se presenta sobre blanco, compatible con la política commerce-primary de Catalog AI v0.3.1.

## Catalog AI v0.3.1 — estado separado

Rama: `fix/nima-catalog-ai-v031-production-image-readiness`

- Política `commerce-primary = #FFFFFF` implementada.
- Lifestyle/in-use permanece contextual/editorial.
- Halo dominante reducido y causa raíz aislada.
- Edge matte residual implementado en rama, pero NO declarado validado todavía sobre el feeding-mat real porque `nima-catalog-images/` no está trackeado en GitHub.
- No bloquear el resto de Production Readiness por este punto; sí exigir validación real antes de declarar Catalog AI v0.3.1 cerrado.

## Pendiente de validación técnica

Antes de merge a `main`:

1. Ejecutar `theme check` sobre `feat/nima-production-readiness-launch`.
2. Validar JSON/Liquid del theme completo.
3. Revisar visualmente Home desktop/mobile:
   - hero;
   - editorial shop window;
   - split;
   - Magazine teaser.
4. Revisar visualmente PDP desktop/mobile:
   - compra;
   - variantes;
   - OVL story;
   - routine cross-sell.
5. Confirmar que colección `all` devuelve productos activos en el storefront.
6. Confirmar que EN y ES renderizan correctamente los nuevos locale keys.

## Pendiente administrativo / negocio

No resoluble únicamente desde GitHub:

1. Confirmar que "Free shipping from $50" / "Envío gratis desde $50" sea política real antes de tráfico pagado.
2. Confirmar precios atípicos del catálogo (especialmente tickets premium) antes de campañas.
3. Revisar PayPal Business / guest-card checkout y reducir fricción si la cuenta lo permite.
4. Confirmar mercado y shipping activo para Estados Unidos.
5. Confirmar Instagram/handles oficiales antes de distribución de contenido.

## Gate de salida a ventas

Nima puede pasar a tráfico real cuando:

- theme branch pasa validación técnica y visual;
- locale branch está incorporada;
- imágenes principales prioritarias cumplen fondo blanco consistente;
- precios y shipping están confirmados;
- checkout permite completar una compra real de punta a punta;
- analítica mínima de sesiones, add-to-cart, checkout y compra está observable.

A partir de ese punto, la prioridad cambia de construcción a:

`tráfico → conversión → analítica → aprendizaje → optimización → escalado`.

## Restricciones

- No merge automático a `main` sin gate.
- No cambios directos en Shopify desde esta rama.
- No apps de pago nuevas por defecto.
- No llamadas de generación de imagen para validar estructura o layout.
- No sacrificar identidad editorial por patrones genéricos de marketplace.
