# Nima × OMNI — Nota oficial de integración

**Estado:** propuesta operativa aprobada para continuidad.  
**OMNI fuente de verdad:** `francoisbowman-cloud/image-toolkit` en `main`.  
**Nima fuente de verdad:** este repositorio en `main`.

## Objetivo

Nima debe utilizar OMNI como infraestructura compartida de producción visual, auditoría y gobernanza cuando la tarea encaje en sus capacidades, evitando duplicar lógica visual dentro del theme o de Nima Catalog AI.

## Principio de integración

Nima conserva Shopify, catálogo, reglas comerciales, theme y lógica propia del negocio. OMNI aporta capacidades reutilizables de procesamiento visual, análisis, planificación, quality gates, trazabilidad y profesionalización web.

Arquitectura objetivo:

`Nima / supplier / AutoDS → OMNI API / capabilities → resultado + evidencia + estado → Nima / Shopify`

La integración debe ser incremental y reversible.

## Primeros flujos recomendados

### 1. Supplier Image → OMNI → Shopify-ready Asset

Para imágenes nuevas provenientes de proveedor, feed o AutoDS:

1. Nima entrega la imagen original a OMNI.
2. OMNI ejecuta Image Refinement de manera conservadora.
3. Normaliza técnicamente fondo, encuadre, formato y derivados cuando corresponda.
4. Protege la identidad real del producto y contenido legítimo.
5. Devuelve manifiesto, evidencia y estado `PASS / REVIEW / FAIL`.
6. Solo un resultado admitido por la política de Nima puede continuar hacia Shopify.

OMNI no debe inventar producto, cambiar geometría, color, materiales, accesorios o texto legítimo del producto.

### 2. Batch de catálogo

Para lotes de imágenes, reutilizar batch processing de OMNI con retry/resume/cancelación. Evitar crear un segundo motor genérico de batch visual dentro de Nima si OMNI ya cubre el caso.

Nima Catalog AI puede conservar lógica específica de catálogo/producto, mientras OMNI actúa como motor visual compartido cuando corresponda.

### 3. Auditoría y evolución del theme

Para Home, Collection, PDP, Search, Cart y navegación:

`OBSERVE → INTENT → KNOWLEDGE → PLAN → PREVIEW → PROVE`

OMNI puede analizar la implementación real, definir Visual Intent, consultar Professional Intelligence/OVKB, generar un CompositionChangeSet selector-aware y producir evidencia BEFORE/AFTER Desktop/Mobile cuando exista un runtime Shopify fiel.

Si el runtime Shopify necesario no está disponible, OMNI debe informar `SHOPIFY_RUNTIME_REQUIRED` o limitación equivalente; no inventar renders.

No ejecutar Apply sin aprobación visual explícita y autorización de escritura.

## Reglas de frontera

- `main` de Nima sigue siendo la única fuente de verdad del proyecto Nima.
- `main` de OMNI sigue siendo la única fuente de verdad de OMNI.
- Nima no debe copiar motores generales de OMNI salvo una razón arquitectónica documentada.
- OMNI no sustituye Shopify, AutoDS ni las reglas comerciales de Nima.
- Un `preview` no equivale a aprobación, deploy ni publicación.
- Los resultados `REVIEW` o `FAIL` no deben publicarse como si fueran aprobados.
- Toda integración con servicios externos de pago debe quedar explícita; priorizar las capacidades propias/deterministas de OMNI cuando sean suficientes.

## Prioridad de implementación

1. Integración manual por API para imágenes de proveedor.
2. Batch automatizado para importaciones de catálogo.
3. Trigger al ingresar nuevas imágenes/productos cuando el flujo esté validado.
4. Integración formal de Render Gate y propuesta visual del theme.
5. Orquestación más autónoma solo después de evidencia estable en producción.

## Instrucción para futuros chats/agentes

Cuando trabajes en Nima y una tarea implique procesamiento de imágenes, consistencia visual, auditoría del theme, propuestas de diseño, quality gates, renders de revisión o una capacidad que OMNI ya provea:

1. inspecciona primero el estado actual de OMNI desde `francoisbowman-cloud/image-toolkit@main`;
2. reutiliza OMNI en lugar de duplicar la capacidad dentro de Nima;
3. respeta las fronteras Shopify/runtime, aprobación y publicación;
4. si aparece una necesidad reutilizable para varios proyectos, evalúala primero como evolución de OMNI y no como parche exclusivo de Nima.

Esta nota expresa intención de arquitectura. No autoriza por sí sola despliegues, publicación automática ni uso de proveedores externos de pago.
