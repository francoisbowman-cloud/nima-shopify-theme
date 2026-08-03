# Flujo de catálogo y tratamiento de imágenes

Este flujo convierte exportaciones de Shopify en propuestas revisables. No modifica Shopify, no reemplaza medios existentes y no inventa materiales, medidas ni promesas comerciales.

## 1. Títulos y descripciones

Exportar productos desde Shopify y ejecutar:

```bash
python tools/catalog_copy_generator.py products_export.csv --output build/catalog-copy-review.csv
```

El CSV resultante incluye título, cuerpo HTML y SEO propuestos, más uno de estos estados:

- `REVIEW_REQUIRED`: hay texto fuente suficiente, pero una persona debe verificarlo.
- `NEEDS_EVIDENCE`: falta descripción verificable; no se genera una nueva.
- `BLOCKED`: falta una imagen principal; el producto no debe publicarse como listo.

El generador elimina ruido evidente de proveedores, reorganiza únicamente frases ya presentes en la fuente y produce una sola propuesta por `Handle`. El archivo generado no debe importarse directamente: primero se revisa contra la ficha del proveedor y después se traslada a un CSV de importación de Shopify.

## 2. Imágenes con OMNI

Se puede preparar un piloto directamente desde la exportación de Shopify
(una imagen principal por producto, sin descargar ni modificar la fuente):

```bash
python tools/prepare_omni_batch.py products_export.csv \
  --primary-only --output build/omni-primary-batch.json
```

Para un lote basado en archivos ya descargados, usar una carpeta local:

```bash
python tools/prepare_omni_batch.py build/source-images --output build/omni-batch.json
```

Ejecutar OMNI desde el repositorio hermano `image-toolkit`:

```bash
IT_PRESETS_DIR="$PWD/omni-presets" \
  uv --project ../image-toolkit run image-toolkit refine-batch \
  build/omni-batch.json --output-dir build/omni-review
```

El preset `nima-product` hereda las reglas neutrales y de productos para mascotas de OMNI. Mantiene revisión obligatoria, crea derivados WebP 1:1 y prohíbe añadir animales o personas. Nunca reemplaza el medio original automáticamente.

Antes de subir cada resultado:

1. Comparar con el original y comprobar que el producto, accesorios y texto de empaque no cambiaron.
2. Rechazar cualquier resultado que elimine piezas reales, invente geometría o use una especie distinta.
3. Confirmar fondo crema coherente, producto completo, aire perimetral y mínimo 1600 × 1600 px.
4. Registrar producto, imagen fuente, resultado, fecha y responsable de aprobación.
5. Subir manualmente a Shopify y conservar el original hasta verificar catálogo y ficha de producto.

## 3. Orden de remediación

1. Productos sin imagen: conseguir una fuente real o despublicar temporalmente.
2. Imágenes con marcas de terceros, claims o collages de marketplace: reemplazar desde fuente autorizada; OMNI no debe borrar evidencia comercial para hacerla parecer propia.
3. Packshots válidos con fondo inconsistente: refinar con `nima-product`.
4. Lifestyle válido: mantener como imagen secundaria y auditar recorte 4:5.

## 4. Límites actuales

El repositorio del tema no contiene el catálogo ni las imágenes de Shopify. Por eso el flujo queda implementado y probado aquí, pero el tratamiento de las fichas requiere una exportación real de productos e imágenes o acceso autorizado al Admin API. Sin esa evidencia no se deben generar descripciones ni reconstruir productos desde capturas.
