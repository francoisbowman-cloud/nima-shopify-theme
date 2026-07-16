# Especificación funcional y técnica de OVL

## 1. Definición

OVL es un motor de interpretación y dirección creativa. Su función es transformar información estructurada y no estructurada de producto en decisiones visuales, narrativas y comerciales.

## 2. Pipeline

### 2.1 Ingesta

Entradas:

- Título.
- Descripción.
- Imágenes.
- Precio.
- Variantes.
- Materiales.
- Dimensiones.
- Categoría.
- Proveedor.
- Reviews.
- Datos de uso.
- Restricciones.
- Público objetivo.

### 2.2 Normalización

- Limpieza de título.
- Eliminación de claims no verificables.
- Conversión de unidades.
- Homologación de atributos.
- Detección de duplicados.
- Clasificación de calidad de imagen.

### 2.3 Interpretación

OVL identifica:

- Job to be done.
- Problema principal.
- Beneficio funcional.
- Beneficio emocional.
- Riesgo percibido.
- Contexto de uso.
- Nivel de complejidad.
- Emoción dominante.
- Emociones secundarias.

### 2.4 Esencia OVL

Ejemplo:

```yaml
essence:
  functional: "transportar con seguridad"
  emotional: "tranquilidad"
  social: "cuidado responsable"
  dominant_emotion: "confianza"
  secondary_emotions:
    - "calma"
    - "protección"
```

### 2.5 Dirección visual

OVL genera:

- Paradigma visual.
- Paleta.
- Relación de blancos.
- Contraste.
- Tipo de luz.
- Composición.
- Encuadre.
- Escala.
- Movimiento.
- Materialidad.
- Tipografía.
- Iconografía.

### 2.6 Dirección editorial

OVL define:

- Promesa.
- Tono.
- Titular.
- Subtítulo.
- Bullets.
- Historia larga.
- Pruebas.
- FAQs.
- Microcopy.
- CTA.

### 2.7 Selección de formato

OVL decide entre:

- Ficha funcional.
- Producto híbrido.
- Storytelling largo.
- Landing por problema.
- Guía.
- Comparativa.
- Magazine.
- Carrusel.
- Reel.
- Email.

### 2.8 Generación

Salidas:

- Brief de imagen.
- Prompt de generación.
- Guion.
- Copy.
- Jerarquía.
- Secciones.
- Assets.
- Metadatos SEO.
- Adaptaciones por canal.

### 2.9 Revisión humana

Revisión obligatoria para:

- Claims.
- Salud y seguridad.
- Calidad visual.
- Fidelidad del producto.
- Tallas.
- Materiales.
- Precios.
- Información logística.

### 2.10 Publicación y aprendizaje

- Publicación.
- Seguimiento.
- Medición.
- Comparación.
- Ajuste del perfil OVL.

## 3. Perfiles visuales

Ejemplos:

### Calm

- Blanco dominante.
- Neutros cálidos.
- Luz natural.
- Encuadre estable.
- Mucho espacio negativo.
- Ritmo lento.

### Play

- Color vivo.
- Movimiento.
- Encuadres dinámicos.
- Tipografía energética.
- Microinteracciones.

### Care

- Cercanía.
- Piel, pelo, manos.
- Luz suave.
- Información clara.
- Prueba y confianza.

### Tech

- Precisión.
- Fondo blanco o oscuro controlado.
- Exploded views.
- Datos.
- Líneas limpias.
- Ritmo técnico.

### Travel

- Escala.
- Desplazamiento.
- Escenas reales.
- Seguridad.
- Modularidad.
- Checklists.

## 4. Lógica de decisión

Ejemplo simplificado:

```text
Si el riesgo percibido es alto:
  priorizar confianza, pruebas, especificaciones y devoluciones.

Si el producto es visualmente simple:
  añadir contexto de uso y narrativa.

Si el producto resuelve ansiedad:
  usar ritmo calmado, luz suave y lenguaje de tranquilidad.

Si la intención es rápida:
  mostrar CTA y variantes antes de la narrativa.

Si la intención es exploratoria:
  iniciar con emoción y contexto.
```

## 5. Gobernanza

OVL nunca debe:

- Inventar certificaciones.
- Alterar el producto.
- Ocultar limitaciones.
- Generar imágenes que induzcan a error.
- Sustituir información crítica por estética.
- Publicar sin revisión en categorías sensibles.

## 6. KPIs

- CTR.
- Conversión.
- Add-to-cart.
- Tiempo en página.
- Profundidad de scroll.
- Interacción con módulos editoriales.
- Valor promedio de pedido.
- Tasa de devolución.
- Repetición.
- NPS.
- Rendimiento por perfil OVL.
