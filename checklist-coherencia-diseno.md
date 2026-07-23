# Checklist de Coherencia de Diseño

Documento de referencia corto para usar en cualquier proyecto (Nima, Aromia, futuros) antes de dar por cerrada una tarea de diseño/frontend. No reemplaza el skill `frontend-design`; es el paso de verificación final.

---

## 1. Cobertura completa (no auditar de memoria)

Antes de revisar nada, generar la lista **completa** de secciones/páginas/componentes que existen realmente en el proyecto (vía API/código, no de memoria). Auditar contra esa lista, no contra "lo que me acuerdo que existe".

> Por qué: en Nima, una sección quedó fuera de una auditoría completa simplemente porque no estaba en la lista mental de "lo que hay que revisar".

---

## 2. Checklist de diseño (lo mínimo, no las 40 categorías)

- [ ] **Tokens**: cero colores/tipografías/espaciados hardcodeados — todo referencia las variables del sistema (settings del theme, design tokens, variables CSS)
- [ ] **Contraste texto-sobre-imagen**: toda sección con foto de fondo usa tratamiento para texto claro (o scrim suficiente) — nunca texto por defecto sin verificar
- [ ] **Estados cubiertos**: hover, disabled, sold-out/vacío, error — al menos los que apliquen al componente
- [ ] **Responsive real**: probado en mobile real, no asumido desde desktop
- [ ] **Consistencia entre pantallas**: mismo componente (tarjeta, botón, badge) no debería verse distinto en dos páginas sin razón

---

## 3. Assets/imágenes (si el proyecto depende de fuentes externas — proveedores, stock, etc.)

Si las imágenes vienen de fuera del proyecto (proveedor, banco de imágenes), definir un pipeline fijo antes de subirlas:

1. Tratamiento de fondo unificado (quitar fondo / fondo consistente)
2. Misma relación de aspecto que el resto del catálogo/sección
3. Mismo criterio de recorte/composición

> Por qué: fotos crudas de proveedores distintos rompen la coherencia visual aunque el código esté perfecto — es un problema de datos, no de CSS.

---

## 4. Cierre: publicar y verificar en vivo, siempre

Ninguna tarea de diseño se marca como terminada sin:

1. Publicar el cambio (o confirmar que ya está en el entorno que corresponde)
2. Abrir el sitio real en incógnito (no el editor/preview)
3. Confirmar visualmente que el cambio se ve
4. Recién ahí, cerrar la tarea

> Por qué: un cambio correcto guardado en un borrador sin publicar es indistinguible, para el usuario final, de que no se hizo nada.

---

## Notas para adaptar a un proyecto específico

- Reemplazar "settings del theme" por el sistema de tokens real del proyecto (Shopify theme settings, Tailwind config, CSS variables, etc.)
- Si el proyecto no depende de proveedores externos de imágenes, el punto 3 puede omitirse
- Este documento no define identidad visual, tono, o principios de marca — eso vive en la documentación propia de cada proyecto
