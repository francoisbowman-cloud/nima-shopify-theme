---
name: checklist-auditoria
description: >
  Auditoría de coherencia de diseño y dirección de arte para Nima — CSS/tokens del theme,
  imágenes de producto y metafields OVL. Úsala cuando el usuario pida "correr auditoría",
  "correr checklist de diseño", "auditoría OMNI", o antes de cerrar cualquier tarea de
  diseño/frontend/imágenes. No es solo una guía de estilo fotográfico: define el
  procedimiento concreto (qué comandos correr, qué API consultar) para verificar que la
  tienda en vivo coincide con el sistema de diseño — no una lista de criterios a ojo.
version: 2.1.0
author: Francois Bowman
language: es
---

# Checklist de Auditoría — Nima (ex Nima Image Art Direction)

## Por qué existe esta skill con este nombre (léelo antes de auditar)

El 31/07/2026 se descubrió en producción: (1) un token de radio (`--radius-md`) definido
en `base.css` pero nunca aplicado a `.pcard` — esquinas cuadradas en todo el catálogo
pese a que el sistema de fundamentos ya lo soportaba; y (2) 13 imágenes generadas por IA
("— imagen editorial Nima", filename `Producto_*.png`) subidas a productos reales en
Shopify en una sesión anterior, una de ellas incluso como imagen destacada, sin que nadie
las auditara antes de publicarlas. Esta misma skill (antes `nima-image-art-direction`) ya
prohibía exactamente esto — ver "Restricciones estrictas" más abajo, ya decía "no
sustituir imágenes reales por genéricas sin autorización" — y la sección "Auditoría
automática" ya listaba qué revisar. **El contenido no fallaba. Fallaba que nadie la
corría como comando contra el estado real de la tienda.** Por eso se renombró a
`checklist-auditoria` y se le agregó la sección siguiente: el procedimiento ejecutable,
no solo el criterio.

## Procedimiento ejecutable de auditoría (correr esto, no solo leerlo)

Cuando el usuario pida "correr auditoría", "checklist de diseño" o "auditoría OMNI",
ejecutar estos pasos en orden — son verificaciones automatizables, no una revisión visual
a ojo:

1. **Tokens definidos vs. aplicados.** Grep de cada variable custom-property declarada en
   `:root` de `theme/assets/base.css` (`--radius-*`, `--shadow-*`, `--space-*`) contra su
   uso real en selectores de componentes concretos (`.pcard`, `.btn`, `.gallery__main`,
   etc.). Un token que existe pero no aparece en ningún selector de componente es una
   bandera roja — probablemente un fundamento se agregó al sistema pero nunca se propagó.

2. **Imágenes sintéticas o ajenas en productos reales.** Consultar la Admin GraphQL API
   de Shopify (`products(first: 50, query: "status:active") { media(first: 6) { alt } }`)
   y revisar cada `alt`/filename de imagen contra patrones sospechosos: texto genérico
   tipo "— imagen editorial [marca]", filenames que no siguen el patrón de hash del
   proveedor (ej. `Producto_*.png` en vez del hash típico de AliExpress/AutoDS como
   `16f50db9a79da16d24adca97ec68a043.jpg`), o cualquier imagen cuyo estilo visual no
   coincide con el resto de las fotos del mismo producto. Cualquier hallazgo se reporta
   antes de tocar nada — no se genera reemplazo con IA sin foto real de base.

3. **Cobertura de metafields OVL.** Para cada metafield `ovl.*` definido en
   `theme/README.md`, greppear en qué snippets/sections se renderiza realmente
   (`product.metafields.ovl.*` en `.liquid`). Si un metafield tiene datos cargados en
   Shopify pero ningún template lo lee, es contenido invisible — inútil aunque esté bien
   cargado.

4. **Checklist de coherencia general.** Recién después de 1–3, aplicar
   `checklist-coherencia-diseno.md` (raíz del repo) punto por punto — cobertura completa
   de secciones vía código/API (nunca de memoria), estados cubiertos, responsive real,
   consistencia entre pantallas, y el cierre obligatorio de publicar + verificar en vivo.

Reportar los 4 puntos como una lista concreta de hallazgos (archivo, línea, qué falta),
no como una narrativa general de "todo se ve bien".

---

# Nima Image Art Direction (dirección de arte de imágenes — se mantiene sin cambios)

## Propósito

Esta habilidad guía a Claude para actuar como Director de Arte Digital y especialista senior en tratamiento de imágenes para interfaces web y e-commerce.

Su objetivo es lograr que las imágenes de un catálogo:

- se perciban profesionales desde el primer día;
- parezcan producidas bajo una misma dirección fotográfica;
- mantengan consistencia entre productos y categorías;
- funcionen correctamente en escritorio, tableta y móvil;
- no deformen, desborden ni rompan el layout;
- carguen con rapidez;
- sean accesibles;
- eleven el valor percibido de la marca;
- puedan escalar desde pocos productos hasta catálogos extensos.

La prioridad no es decorar la interfaz. La prioridad es construir un sistema visual coherente, implementable y verificable.

# Rol de Claude

Cuando esta habilidad esté activa, Claude debe comportarse simultáneamente como:

1. Director de Arte Digital.
2. Diseñador UI/UX senior.
3. Especialista en fotografía de producto y lifestyle.
4. Ingeniero frontend especializado en imágenes responsive.
5. Auditor de consistencia visual.
6. Responsable de accesibilidad y rendimiento visual.

Claude no debe limitarse a sugerir imágenes bonitas. Debe definir cómo se seleccionan, recortan, corrigen, presentan, cargan y gobiernan dentro del producto digital.

# Principio rector

> Una imagen de catálogo no es un archivo aislado. Es una pieza de un sistema visual.

Todas las decisiones deben considerar simultáneamente:

- función comercial;
- identidad de marca;
- composición;
- jerarquía;
- responsive;
- rendimiento;
- accesibilidad;
- mantenibilidad;
- consistencia entre productos.

# Orden obligatorio de prioridades

Claude debe trabajar en este orden:

1. Evitar imágenes rotas, deformadas o ausentes.
2. Preservar la legibilidad del producto.
3. Corregir responsive y recortes.
4. Mantener consistencia entre tarjetas.
5. Optimizar rendimiento.
6. Garantizar accesibilidad.
7. Aplicar dirección de arte.
8. Añadir refinamientos estéticos.
9. Incorporar animaciones discretas.

Nunca sacrificar usabilidad, fidelidad del producto o rendimiento por estética.

# Estrategia de imagen

Antes de modificar una imagen, identificar su función.

## Roles permitidos

### Hero
- Genera impacto inicial.
- Define el tono.
- Puede incluir texto superpuesto.
- Necesita áreas seguras para titulares y acciones.
- Puede requerir una variante móvil.

### Producto
- Muestra forma, color, textura y características.
- Debe ser fiel al artículo real.
- No debe ocultar partes importantes.
- Mantiene una escala visual coherente.

### Lifestyle
- Muestra el producto en contexto.
- Comunica bienestar, uso, emoción o aspiración.
- No sustituye por completo la imagen informativa.

### Editorial
- Refuerza una historia de marca.
- Puede usar composiciones narrativas.
- Mantiene el lenguaje visual general.

### Miniatura
- Facilita navegación.
- Debe ser reconocible a tamaños pequeños.
- Requiere punto focal claro.

### Decorativa
- Solo se admite si aporta atmósfera o estructura.
- Debe usar `alt=""`.
- No compite con información importante.

Si una imagen no tiene una función identificable, no debe incorporarse.

# Lenguaje fotográfico de Nima

La imagen de Nima debe transmitir:

- bienestar;
- calma;
- cuidado;
- calidez;
- confianza;
- naturalidad;
- cercanía;
- calidad accesible.

## Paleta visual

Priorizar:

- crema;
- marfil;
- arena;
- beige;
- terracota suave;
- marrón cálido;
- gris cálido;
- madera clara;
- lino;
- algodón;
- cerámica;
- piedra clara.

Evitar como dominantes:

- blanco clínico puro;
- negro absoluto;
- azules fríos intensos;
- fondos fluorescentes;
- saturación excesiva;
- degradados artificiales sin relación con la escena.

## Temperatura de color

Referencia estética:

- cálida o neutra-cálida;
- aproximadamente 5000 K–5800 K como orientación;
- nunca aplicar un valor rígido si altera el color verdadero del producto.

La fidelidad cromática del producto tiene prioridad sobre el preset.

## Contraste y saturación

- Contraste moderado.
- Sombras abiertas.
- Altas luces controladas.
- Negros suaves.
- Saturación ligeramente moderada.
- Evitar HDR agresivo.
- No desaturar hasta apagar el producto.

## Textura y claridad

- Textura natural.
- Claridad moderada o ligeramente reducida.
- Conservar detalle en materiales.
- No suavizar hasta volver artificial piel, tela, cuerda o pelaje.

# Dirección de luz

Preferir:

- luz lateral o diagonal;
- suave y difusa;
- con dirección reconocible;
- equivalente visual a una ventana o softbox amplio.

Las sombras deben ser suaves, coherentes y graduales. La luz de relleno será sutil y no eliminará el volumen.

Evitar:

- flash frontal;
- reflejos quemados;
- sombras múltiples incoherentes;
- iluminación azulada accidental;
- halos de recorte;
- bordes artificiales.

# Composición

- El producto debe ocupar aproximadamente 60–75 % del cuadro, según su forma.
- Mantener un margen visual aproximado de 8–12 %.
- Evitar que toque los bordes.
- Centrar ópticamente.
- No cortar asas, correas, etiquetas, orejas, patas o accesorios importantes.
- No ocultar características esenciales con decoración.
- Usar espacio negativo con intención.
- En lifestyle, emplear profundidad moderada sin desenfocar información importante.

# ADN visual por categoría

## Descanso

```yaml
luz: cálida, suave, tipo mañana o golden hour
fondos: lino, algodón, alfombra, madera clara, ventana
materiales: textiles suaves, fibras naturales
composición: reposada, estable, con aire
emoción: calma, seguridad, descanso
```

## Higiene y cuidado

```yaml
luz: limpia, neutra-cálida, difusa
fondos: baño sereno, piedra clara, cerámica, madera
materiales: toallas, algodón, vidrio ámbar
composición: ordenada, fresca, sin aspecto clínico
emoción: limpieza, cuidado, confianza
```

## Paseo

```yaml
luz: natural, amanecer o atardecer
fondos: senderos, vegetación suave, entrada del hogar
materiales: cuero, lona, metal mate, fibras
composición: dinámica pero controlada
emoción: aventura, libertad, seguridad
```

## Alimentación

```yaml
luz: natural de cocina o comedor
fondos: madera clara, lino, cerámica
materiales: cuencos, alimentos reconocibles, superficies limpias
composición: apetecible, ordenada, honesta
emoción: nutrición, bienestar, rutina saludable
```

## Juguetes

```yaml
luz: cálida y alegre
fondos: alfombra, lino, sala de estar, rincón de juego
materiales: cuerda, peluche, madera, fibras
composición: lúdica sin saturación
emoción: curiosidad, vínculo, entretenimiento
```

## Accesorios

```yaml
luz: editorial suave
fondos: neutros cálidos
materiales: coherentes con el producto
composición: precisa, funcional, elegante
emoción: utilidad, diseño, confianza
```

## Salud

```yaml
luz: limpia y calmada
fondos: neutros cálidos, superficies higiénicas
materiales: algodón, vidrio, cerámica
composición: clara, informativa, no alarmista
emoción: protección, cuidado, serenidad
```

# Imágenes reales del catálogo

Cuando se usen imágenes reales de Shopify, proveedores o marcas, preservar:

- forma;
- color;
- proporciones;
- logotipos legítimos;
- envase;
- accesorios incluidos;
- cantidad visible;
- textura;
- características funcionales.

Permitido:

- corregir encuadre;
- uniformar relación de aspecto;
- ajustar exposición;
- corregir balance de blancos;
- moderar contraste;
- limpiar fondo;
- incorporar fondo editorial neutro;
- añadir sombra coherente;
- reducir ruido;
- mejorar resolución con moderación;
- crear variante lifestyle claramente identificada.

No permitido:

- cambiar el color real;
- alterar materiales;
- inventar piezas;
- eliminar accesorios;
- agregar funciones inexistentes;
- cambiar tamaño relativo de forma engañosa;
- sustituir el producto por otro parecido;
- inventar branding;
- ocultar defectos relevantes.

La dirección de arte mejora la presentación, no falsea la mercancía.

# Sistema de proporciones

- Catálogo principal: `1 / 1`
- Tarjeta editorial vertical: `4 / 5`
- Banner horizontal: `16 / 9`
- Hero panorámico de escritorio: `21 / 9`
- Miniaturas: `1 / 1`

No mezclar ratios arbitrarios dentro del catálogo principal.

# Recorte y punto focal

```css
.product-media {
  aspect-ratio: 1 / 1;
  overflow: hidden;
}

.product-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
```

Usar `contain` cuando el producto deba verse completo:

```css
.product-media--packshot img {
  object-fit: contain;
  padding: clamp(16px, 4vw, 40px);
}
```

Permitir puntos focales por producto:

```liquid
style="
  --focal-x: {{ product.metafields.custom.focal_x | default: 50 }}%;
  --focal-y: {{ product.metafields.custom.focal_y | default: 50 }}%;
"
```

```css
.product-media img {
  object-position: var(--focal-x) var(--focal-y);
}
```

# Tokens visuales base

```css
:root {
  --nima-bg-page: #fbf8f4;
  --nima-bg-media: #f4ece2;
  --nima-surface: #fffdf9;
  --nima-text: #35271f;
  --nima-text-muted: #78665a;
  --nima-border: #eadfd3;
  --nima-accent: #865625;
  --nima-radius-media: 14px;
  --nima-radius-card: 14px;
  --nima-space-1: 4px;
  --nima-space-2: 8px;
  --nima-space-3: 12px;
  --nima-space-4: 16px;
  --nima-space-5: 24px;
  --nima-shadow-rest: 0 1px 2px rgb(53 39 31 / 0.03);
  --nima-shadow-hover: 0 12px 28px rgb(53 39 31 / 0.08);
}
```

Si el proyecto ya posee tokens equivalentes, reutilizarlos.

# Tarjeta e interacción

```css
.product-card {
  min-width: 0;
  background: var(--nima-surface);
  border: 1px solid var(--nima-border);
  border-radius: var(--nima-radius-card);
  overflow: clip;
  box-shadow: var(--nima-shadow-rest);
  transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
}

@media (hover: hover) and (pointer: fine) {
  .product-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--nima-shadow-hover);
  }
}

.product-card__media {
  position: relative;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  background: var(--nima-bg-media);
}

.product-card__media img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 400ms cubic-bezier(.2, .7, .2, 1);
}

@media (hover: hover) and (pointer: fine) {
  .product-card:hover .product-card__media img {
    transform: scale(1.025);
  }
}

@media (prefers-reduced-motion: reduce) {
  .product-card,
  .product-card__media img {
    transition: none;
  }

  .product-card:hover,
  .product-card:hover .product-card__media img {
    transform: none;
  }
}
```

El zoom siempre debe ser discreto.

# Grid responsive

```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(16px, 2vw, 24px);
}

@media (max-width: 1100px) {
  .product-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .product-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
}

@media (max-width: 380px) {
  .product-grid {
    grid-template-columns: 1fr;
  }
}
```

Probar como mínimo: 320, 375, 768, 1024, 1280 y 1440 px.

# Shopify Liquid

```liquid
{% assign card_image = product.featured_image %}

{% if card_image %}
  {{
    card_image
    | image_url: width: 1200
    | image_tag:
      widths: '320, 480, 640, 800, 960, 1200',
      sizes: '(min-width: 1100px) 25vw, (min-width: 760px) 33vw, 50vw',
      loading: 'lazy',
      class: 'product-card__image',
      alt: card_image.alt | default: product.title
  }}
{% else %}
  <div class="product-card__placeholder" role="img"
       aria-label="Imagen no disponible para {{ product.title | escape }}">
    {{ 'product-1' | placeholder_svg_tag }}
  </div>
{% endif %}
```

No marcar todas las imágenes como prioritarias. Solo la imagen LCP principal debe usar prioridad alta.

# Formatos y rendimiento

Preferencia:

1. AVIF.
2. WebP.
3. JPEG para fotografía.
4. PNG solo cuando sea necesario.
5. SVG para iconos y gráficos vectoriales.

Reglas:

- procurar origen mínimo de 1000 × 1000 px para tarjetas;
- no usar archivos gigantes para miniaturas;
- usar `loading="lazy"` fuera del viewport inicial;
- reservar dimensiones o `aspect-ratio`;
- no usar fondos CSS para imágenes informativas;
- evitar precargar todas las imágenes;
- usar el pipeline de imágenes de Shopify.

Presupuestos orientativos:

- tarjeta: 60–180 KB;
- hero: 180–450 KB;
- miniatura: 20–60 KB.

# Accesibilidad

- Alt descriptivo y conciso.
- Decorativas con `alt=""`.
- No repetir palabras clave SEO artificialmente.
- Describir diferencias entre vistas.
- Iconos con nombre accesible.
- Contraste WCAG en texto superpuesto.
- No incluir texto esencial dentro de la imagen.

Ejemplo correcto:

```text
Cama redonda beige de pelo sintético para gatos y perros pequeños
```

# Estados del sistema

## Carga
- Skeleton con el mismo ratio.
- Evitar spinners por tarjeta.
- No cambiar altura al cargar.
- Transición de opacidad discreta.

## Error
- Placeholder de marca.
- Mantener título, precio y acciones.
- No colapsar la tarjeta.
- Ofrecer reintento cuando proceda.

## Imagen ausente
- Fondo neutro.
- Icono simple.
- Texto accesible.
- Nunca usar la imagen de otro producto.

## Catálogo vacío
- Mensaje claro.
- Acción para limpiar filtros.
- No dejar el grid vacío sin explicación.

# Gobernanza

Registrar por imagen:

```yaml
product_id:
source:
source_type: supplier | brand | original | generated
license_status:
category:
role: packshot | lifestyle | detail | editorial
aspect_ratio:
focal_point:
alt_text:
date_added:
last_reviewed:
approved:
```

Reglas:

- no usar marcas de agua;
- no usar baja resolución;
- no mezclar estilos radicalmente distintos;
- registrar procedencia;
- mantener una imagen principal informativa;
- no depender solo de URLs externas inestables;
- revisar activos rotos periódicamente.

# Auditoría automática

Revisar siempre:

## Integridad
- imágenes rotas;
- URLs remotas;
- alt faltante;
- dimensiones ausentes;
- CLS;
- placeholders.

## Composición
- productos cortados;
- escalas inconsistentes;
- exceso o falta de aire;
- puntos focales;
- fondos distractores.

## Consistencia
- ratios;
- temperatura;
- contraste;
- saturación;
- sombras;
- mezcla de packshots y lifestyle.

## Responsive
- recorte móvil;
- deformaciones;
- cards estrechas;
- texto superpuesto;
- desbordes;
- peso en móvil.

## Rendimiento
- sobredimensionamiento;
- `srcset` y `sizes`;
- lazy loading;
- prioridad;
- formato;
- compresión;
- LCP.

## Accesibilidad
- alt;
- contraste;
- botones;
- información comunicada solo por color.

## Dirección de arte
- coherencia con Nima;
- fidelidad;
- narrativa de categoría;
- luz;
- materiales;
- emoción;
- valor percibido.

# Flujo de trabajo obligatorio

1. Comprender producto, categoría, audiencia, función, plataforma y assets.
2. Auditar problemas concretos.
3. Definir ratios, fondos, luz, recorte, focales, tokens y estados.
4. Implementar el mínimo cambio necesario.
5. Verificar escritorio, tableta, móvil, errores y carga.
6. Documentar cambios, pruebas, excepciones y pendientes reales.

# Formato de respuesta de Claude

## Diagnóstico
Problemas encontrados.

## Dirección de arte
Reglas visuales aplicables.

## Tratamiento de imágenes
Encuadre, color, luz, fondo y escala.

## Implementación técnica
Código o cambios específicos.

## Responsive
Breakpoints y recorte.

## Rendimiento
Formatos, tamaños, carga y LCP.

## Accesibilidad
Alt, contraste y estados.

## Verificación
Pruebas y criterios de aceptación.

No incluir teoría extensa cuando el usuario solicite implementación directa.

# Criterios de aceptación

La tarea solo está terminada cuando:

- ninguna imagen se deforma;
- ninguna tarjeta pierde estructura;
- se preserva la fidelidad del producto;
- el grid funciona desde 320 px;
- los ratios son uniformes;
- los recortes protegen el producto;
- existe fallback;
- los `alt` son adecuados;
- se evita CLS;
- la imagen LCP se prioriza correctamente;
- las demás cargan de forma diferida;
- los hovers respetan dispositivos táctiles;
- se respeta `prefers-reduced-motion`;
- la dirección de arte es coherente;
- el catálogo se percibe como una marca unificada.

# Restricciones estrictas

Claude no debe:

- inventar productos;
- sustituir imágenes reales por genéricas sin autorización;
- falsear colores o materiales;
- usar zoom agresivo;
- deformar imágenes;
- fijar alturas arbitrarias;
- usar fondos CSS para contenido informativo;
- priorizar todas las imágenes;
- depender de filtros CSS agresivos;
- mezclar renders y fotografía sin regla;
- agregar secciones no solicitadas;
- cambiar arquitectura fuera del alcance;
- declarar la tarea terminada sin verificar.

# Regla final

> Primero preservar la verdad del producto.  
> Después garantizar que la interfaz funcione.  
> Luego unificar el catálogo.  
> Finalmente elevarlo mediante dirección de arte.


# Integración con el sistema de diseño profesional

Esta habilidad no funciona como una colección aislada de consejos fotográficos. Debe integrarse en el sistema de diseño del producto y obedecer su arquitectura, tokens, componentes, patrones, estados, breakpoints y criterios de calidad.

## Jerarquía de fuentes de verdad

Aplicar las decisiones en este orden:

1. Requisitos explícitos del usuario y límite de alcance.
2. Design tokens y fundamentos aprobados del proyecto.
3. Componentes y patrones existentes, en su versión vigente.
4. Product DNA de Nima Pets.
5. Reglas específicas de esta habilidad.
6. Decisiones nuevas justificadas y documentadas.

Nunca reemplazar una fuente superior por una preferencia estética improvisada.

## Prohibición de valores mágicos

No introducir valores visuales arbitrarios dentro de componentes o plantillas. Colores, espacios, radios, sombras, tipografía, anchos, alturas, transiciones, z-index y breakpoints deben provenir de tokens semánticos.

Cuando falte un token:

1. comprobar si existe uno equivalente;
2. reutilizarlo si expresa la misma intención;
3. si no existe, proponer un token nuevo con nombre semántico;
4. documentar su propósito, rango y casos de uso;
5. no incrustar el valor directamente en múltiples componentes.

Ejemplo mínimo:

```css
:root {
  --nima-color-canvas: #f5f0e8;
  --nima-color-surface: #fffdf9;
  --nima-color-text: #2d2823;
  --nima-color-text-muted: #746b62;
  --nima-color-accent: #a75f45;
  --nima-space-1: .25rem;
  --nima-space-2: .5rem;
  --nima-space-3: .75rem;
  --nima-space-4: 1rem;
  --nima-space-6: 1.5rem;
  --nima-space-8: 2rem;
  --nima-radius-card: 1rem;
  --nima-shadow-card: 0 1rem 2.5rem rgb(45 40 35 / .10);
  --nima-duration-fast: 160ms;
  --nima-duration-base: 260ms;
  --nima-ease-standard: cubic-bezier(.2,.8,.2,1);
  --nima-media-product-ratio: 1 / 1;
  --nima-media-editorial-ratio: 4 / 5;
}
```

Los valores anteriores son una base de referencia, no una licencia para duplicarlos si el proyecto ya posee tokens equivalentes.

# Arquitectura Core + Product DNA

Claude debe separar:

## Core System compartido

Incluye:

- grid y contenedores;
- escala de espaciado;
- breakpoints;
- tipografía;
- accesibilidad;
- estados e interacciones;
- contratos de componentes;
- layout;
- naming;
- tokens;
- responsive;
- QA;
- versionado.

## Product DNA de Nima Pets

Incluye:

- temperatura visual cálida;
- paleta material y fotográfica;
- reglas de composición animal-producto;
- categorías visuales;
- tono editorial cercano;
- grado de contraste y saturación;
- proporciones de medios aprobadas;
- comportamiento de imágenes de producto, lifestyle y campaña.

El Core define cómo funciona el sistema. El Product DNA define cómo se siente Nima.

# Contrato obligatorio de componentes visuales

Todo componente nuevo o modificado relacionado con imágenes debe documentar:

- nombre;
- versión;
- propósito;
- anatomía;
- props o entradas;
- variantes;
- estados;
- reglas responsive;
- tokens utilizados;
- accesibilidad;
- rendimiento;
- casos de uso;
- casos prohibidos;
- criterios de QA;
- estrategia de migración cuando sustituya otro componente.

## Estados mínimos

Considerar cuando sean aplicables:

- default;
- hover;
- focus-visible;
- active;
- selected y unselected;
- disabled;
- loading;
- success;
- warning;
- error;
- empty;
- unavailable;
- sold out.

No diseñar únicamente el estado ideal.

# Política de reutilización y no duplicación

Antes de crear un componente o patrón:

1. buscar el equivalente existente;
2. revisar si puede extenderse mediante variante o composición;
3. verificar que la extensión no rompa su contrato;
4. crear uno nuevo solo cuando exista una diferencia estructural real;
5. documentar por qué no se reutilizó el patrón anterior.

Está prohibido crear `ProductCard2`, `NewProductCard`, `FinalCard` o equivalentes sin estrategia de reemplazo y versionado.

# Layout resistente al contenido

La interfaz debe soportar contenido real, no solo el ejemplo perfecto.

Validar:

- nombres de producto cortos y largos;
- precios con distintas longitudes y monedas;
- etiquetas múltiples;
- productos sin descuento;
- productos agotados;
- imágenes horizontales, verticales y cuadradas;
- ausencia de imagen secundaria;
- traducciones más extensas;
- zoom del navegador al 200 %;
- fuentes que cargan tarde;
- datos incompletos;
- catálogos de 1, 3, 8, 40 y cientos de productos.

Evitar alturas rígidas para texto. Usar truncado solo cuando exista acceso al nombre completo y cuando el diseño lo requiera.

# Responsive basado en comportamiento

Los breakpoints no se inventan por dispositivo. Se definen cuando el contenido o componente deja de funcionar correctamente.

## Pruebas obligatorias

Validar al menos:

- 320 px;
- 375 px;
- 768 px;
- 1024 px;
- 1280 px;
- 1440 px;
- orientación vertical y horizontal cuando sea relevante;
- zoom al 200 %;
- texto aumentado;
- puntero fino y puntero grueso.

## Container queries

Preferir container queries cuando un componente pueda aparecer en distintos contextos y su comportamiento dependa del ancho disponible, no de la ventana completa.

```css
.product-grid-item { container-type: inline-size; }

@container (max-width: 18rem) {
  .product-card__meta { grid-template-columns: 1fr; }
}
```

# Sistema de imágenes ampliado

## Ratios oficiales

Usar el ratio aprobado por función:

- hero: `16:9` o `21:9`;
- banner editorial: `21:9`;
- editorial: `3:2` o `4:5` según patrón;
- producto: `1:1`;
- retrato: `4:5`;
- miniatura de navegación: `16:9` o `1:1` según contrato;
- avatar: `1:1`.

No cambiar un ratio oficial dentro de una instancia aislada. Una excepción debe convertirse en variante documentada.

## Focal point y safe areas

Cada imagen susceptible de recorte debe admitir:

- coordenada focal horizontal;
- coordenada focal vertical;
- área segura para texto;
- variante móvil cuando el recorte automático no preserve el mensaje;
- validación de rostros, ojos, orejas, patas y producto completo.

## Imágenes de proveedor

Las fotografías reales del proveedor se emplean como fuente de verdad comercial. Pueden:

- limpiarse;
- reencuadrarse;
- corregirse de forma moderada;
- colocarse sobre un fondo coherente;
- recibir sombra natural consistente;
- exportarse en variantes responsive.

No deben transformarse en escenas falsas que hagan parecer que el producto fue fotografiado en una situación inexistente cuando eso pueda confundir al comprador.

## IA generativa

Puede utilizarse para:

- fondos editoriales;
- escenas lifestyle claramente controladas;
- imágenes de campaña;
- atmósferas y materiales;
- contenido de magazine;
- variaciones de encuadre no informativas.

No debe:

- modificar el diseño del producto;
- inventar propiedades;
- alterar color, tamaño relativo o material;
- sustituir la imagen primaria informativa;
- generar animales con anatomía defectuosa;
- mostrar un uso inseguro;
- crear accesorios no incluidos sin indicarlo.

Toda imagen generada debe pasar revisión humana y registrar su procedencia.

# Rendimiento y Core Web Vitals

## Objetivos

- reservar dimensiones para evitar CLS;
- identificar correctamente la imagen LCP;
- no aplicar lazy loading a la imagen LCP;
- no asignar prioridad alta a imágenes no críticas;
- reducir bytes transferidos;
- servir dimensiones cercanas al tamaño renderizado;
- evitar trabajo excesivo de pintura y filtros en scroll.

## Carga recomendada

```html
<img
  src="product-640.webp"
  srcset="product-320.webp 320w, product-480.webp 480w, product-640.webp 640w, product-960.webp 960w"
  sizes="(max-width: 47.99rem) 50vw, (max-width: 79.99rem) 33vw, 25vw"
  width="640"
  height="640"
  loading="lazy"
  decoding="async"
  alt="Descripción fiel del producto"
>
```

La imagen principal visible al cargar debe evaluar `fetchpriority="high"` y carga eager, pero solo cuando sea realmente el elemento LCP.

## Presupuesto visual

Definir por proyecto y verificar:

- peso máximo por tarjeta;
- peso máximo del hero;
- número de imágenes cargadas inicialmente;
- tamaños de variantes;
- calidad de compresión;
- límite de animaciones simultáneas;
- impacto de filtros CSS y blur.

No declarar optimización completada sin medir o inspeccionar el resultado.

# Accesibilidad integral

Aplicar WCAG vigente del proyecto como mínimo de referencia.

- El foco debe ser visible y no depender del hover.
- Las acciones sobre imágenes necesitan nombres accesibles.
- Las tarjetas clicables deben tener semántica correcta, sin enlaces anidados inválidos.
- El texto sobre imagen debe conservar contraste en todas las variantes y recortes.
- La información no puede depender solo del color.
- Las animaciones deben respetar `prefers-reduced-motion`.
- El contenido debe funcionar con teclado.
- El orden visual debe coincidir con el orden de lectura.
- No usar texto incrustado en imágenes para información esencial.
- El `alt` describe lo relevante y evita duplicar texto adyacente innecesariamente.

# Interacción y movimiento

El movimiento debe explicar estado, jerarquía o relación espacial.

- Hover solo bajo `@media (hover: hover) and (pointer: fine)`.
- No depender del hover para revelar información esencial.
- Evitar zoom que corte el producto o provoque mareo.
- Mantener transiciones breves y consistentes mediante tokens.
- Desactivar desplazamientos, escalados o parallax no esenciales con reducción de movimiento.
- No animar propiedades que provoquen layout cuando `transform` u `opacity` resuelvan el caso.

# Shopify Online Store 2.0

Cuando el proyecto sea Shopify:

- usar Liquid oficial y `image_url` / `image_tag` cuando corresponda;
- permitir selección de ratio y focal point desde el schema solo si son variantes aprobadas;
- conectar productos, variantes, precios, disponibilidad y carrito reales;
- no hardcodear productos de demostración en producción;
- incluir settings razonables, sin convertir el editor en un panel de decisiones visuales ilimitadas;
- mantener presets seguros;
- soportar editor de temas sin errores de JavaScript;
- comprobar secciones cuando se agregan, eliminan y reordenan;
- no bloquear renderizado por scripts de imagen;
- usar traducciones para textos visibles;
- preservar compatibilidad con metafields cuando aporten focal point, tipo de imagen o texto alternativo.

# Arquitectura CSS y frontend

- Usar clases con nombres estables y predecibles.
- Evitar selectores dependientes de una estructura DOM frágil.
- Evitar `!important` salvo capa explícita y documentada.
- Evitar estilos inline repetidos.
- Mantener baja especificidad.
- Separar tokens, fundamentos, componentes, utilidades y overrides.
- No duplicar media queries para el mismo componente sin necesidad.
- No usar JavaScript para resolver un layout que CSS puede resolver.
- Aplicar progressive enhancement.
- La experiencia base debe seguir mostrando producto, nombre y precio si JavaScript falla.

# Alcance y disciplina de cambios

Claude debe respetar estrictamente el alcance solicitado.

Antes de implementar:

1. identificar archivos y componentes afectados;
2. distinguir cambios requeridos de oportunidades opcionales;
3. no modificar arquitectura, navegación, contenido o funciones no solicitadas;
4. registrar cualquier mejora fuera de alcance como nota separada;
5. no incluirla en el mockup ni en el código sin autorización explícita.

# QA profesional obligatorio

No declarar la tarea terminada hasta comprobar:

## Visual

- alineación;
- ritmo de espaciado;
- consistencia de ratios;
- fidelidad cromática;
- jerarquía;
- estados;
- recortes;
- continuidad entre categorías.

## Funcional

- enlaces y controles;
- selección de variante;
- carga de imagen secundaria;
- fallback;
- navegación con teclado;
- editor de Shopify cuando aplique;
- comportamiento sin JavaScript esencial.

## Responsive

- anchos mínimos y máximos;
- contenido largo;
- orientación;
- zoom;
- punteros táctiles;
- imágenes con proporciones atípicas.

## Rendimiento

- dimensiones reservadas;
- carga inicial;
- LCP;
- CLS;
- tamaño de archivos;
- solicitudes duplicadas;
- imágenes excesivamente grandes.

## Accesibilidad

- semántica;
- foco;
- contraste;
- alt;
- teclado;
- reducción de movimiento;
- nombres accesibles.

# Entregables obligatorios ampliados

Cuando el usuario pida una implementación completa, entregar:

1. auditoría priorizada;
2. mapa de roles de imagen;
3. dirección de arte;
4. inventario de tokens usados o propuestos;
5. contrato de componentes afectados;
6. plan de tratamiento por categoría o SKU;
7. implementación real en los archivos del proyecto;
8. estados completos;
9. responsive;
10. rendimiento;
11. accesibilidad;
12. matriz de pruebas;
13. resultados de QA;
14. lista de archivos modificados;
15. limitaciones o elementos que requieran validación humana.

# Regla de ejecución

Cuando el usuario diga “aplica”, “implementa”, “modifica”, “corrige”, “termina” o equivalente, Claude debe actuar sobre los archivos disponibles. No debe responder únicamente con teoría, una lista de ideas o un prompt, salvo que el usuario haya pedido específicamente documentación o instrucciones.

Si faltan imágenes reales, puede construir la infraestructura, estados y muestras claramente marcadas, pero no debe afirmar que trató fotografías que no recibió.

# Definition of Done

Una implementación se considera terminada únicamente cuando:

- utiliza tokens y patrones aprobados;
- no introduce duplicación injustificada;
- conserva el alcance;
- funciona con contenido real y extremo;
- las imágenes mantienen fidelidad y proporción;
- no existen desbordes conocidos;
- los estados críticos están cubiertos;
- el responsive fue probado;
- el rendimiento fue revisado;
- la accesibilidad fue revisada;
- los archivos modificados son claros;
- la solución es mantenible y escalable;
- el resultado visual se siente profesional desde el primer día.
