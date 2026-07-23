# Continuidad — Nima (ex-PetDrop, RFC-007, Atlas Commerce)
Pegar como primer mensaje en la sesión nueva de Code, junto con
`ESTADO-tienda-mascotas.md` (ya actualizado en el repo, no hace falta
adjuntarlo aparte si la sesión abre con acceso a la carpeta).

## Estado al cierre de esta sesión (23 de julio de 2026)

Repo: `C:\Users\user\Claude\Projects\OVL_PetDrop`, sincronizado con
`github.com/francoisbowman-cloud/nima-shopify-theme` (privado), rama
`main`, working tree limpio. Último commit: `e250563`.

### Lo más importante para entender antes de tocar nada
**El theme publicado (MAIN) en Shopify puede divergir del código de este
repo.** Ya pasó una vez: Design reemplazó el MAIN por un theme nuevo
("Nima — Dirección B") sin avisar, y este repo seguía trackeando el
theme viejo (`PetDrop_OVL`), que ya no existía. Antes de auditar o
tocar cualquier archivo de `theme/`, verificar contra la API real cuál
es el theme `MAIN` actual y confirmar que coincide con lo que dice
`ESTADO-tienda-mascotas.md`. El procedimiento exacto (queries GraphQL
de solo lectura, cómo resincronizar, cómo aplicar fixes sin romper el
theme publicado) está documentado en `CLAUDE.md`, sección "⚠️ El theme
publicado puede divergir del repo".

### Completado en esta sesión
1. **Repo movido a GitHub** (privado) + `gh` CLI instalado y
   autenticado en la máquina de Brey, para que ChatGPT/Codex Cloud
   pueda trabajar sobre el código y entregar PRs.
2. **`AGENTS.md` creado** — equivalente de `CLAUDE.md` para Codex
   Cloud, con el protocolo v2 completo embebido (Codex no puede leer
   archivos fuera de este repo).
3. **Corrección ortográfica "Atlas Comerce" → "Atlas Commerce"**
   aplicada en todo el repo y a nivel sistema (archivo renombrado a
   `ESTADO-atlas-commerce.md` en el Project Atlas E-Commerce,
   referencias corregidas en `ESTADO-aromia.md`, protocolo actualizado
   a v2). Pendiente solo el renombrado del Project de claude.ai en la
   UI (acción manual, no de código).
4. **Detectado y resincronizado: el theme publicado ya no era
   `PetDrop_OVL`.** Design lo había reemplazado por "Nima — Dirección
   B" (ID `198916800593`), con paleta cálida propia, páginas nuevas
   (Sobre Nima, Contacto) y una sección de teaser de Magazine. Se leyó
   el theme real vía Admin GraphQL API (`theme.files`) y se
   sobreescribió `theme/` en el repo para reflejar la realidad.
5. **Auditoría técnica completa de "Nima — Dirección B"**, en orden de
   prioridad (rompe-compra → responsive → navegación → consistencia
   visual → limpieza). Bugs reales encontrados y corregidos:
   - Selector de color roto en productos con Color + otra opción (Dog
     Leash 17 variantes, Portable Pet Grooming Hammock 9 variantes) —
     mostraba círculos duplicados sin indicar talla.
   - Galería de producto sin forma de volver a la imagen principal.
   - Formulario de contacto en inglés mostraba las claves de
     traducción sin resolver (faltaba el bloque `contact` en
     `en.json`).
   - Logo del header con `height="auto"` inválido (regresión) + 3
     imágenes nuevas sin `width`/`height`.
   - Grid del blog no colapsaba a 1 columna en mobile (un `style`
     inline pisaba el breakpoint responsive).
   - Swatches/pills sin estado visual para "sin stock".
   - Consolidado el CSS duplicado de tarjetas (Catálogo/Búsqueda/
     Colecciones ahora usan el mismo patrón).
   - Colores hardcodeados que coincidían con la paleta (footer,
     botones, paneles oscuros) migrados a variables de tema — antes
     no seguían el color elegido en el Customizer.
   - Limpieza: metadata del theme desactualizada, copy con datos
     incorrectos.
   - `shopify theme check`: 0 errores (antes 7), 2 warnings ya
     conocidos (fuentes deprecated, sin urgencia).
6. **Los fixes se subieron a un theme duplicado sin publicar**
   ("Nima — Dirección B (Auditoría Code)", ID `198934265937`) — Shopify
   bloquea escritura por API sobre el theme MAIN. Todo documentado en
   `CHANGELOG.md` (tanda 9) y `ESTADO-tienda-mascotas.md` (decisiones
   #31-33, sección 9 con la checklist de qué revisar).

### Pendiente exacto al momento de migrar
1. **Brey debe previsualizar el duplicado `198934265937` en Shopify y
   publicarlo manualmente** si aprueba los cambios (Online Store →
   Themes → ese theme → Publicar). Checklist de qué mirar:
   `ESTADO-tienda-mascotas.md`, sección 9.
2. Conectar Codex Cloud (ChatGPT) al repo de GitHub — primer uso, sin
   hacer todavía.
3. Confirmar si existen las "adendas v3-v5" del protocolo
   (`PROTOCOLO-adendas-completas.md`) mencionadas en un mensaje de
   Chat — no se encontraron en ninguna carpeta de proyecto verificada.
   Si no existen, aclarar de dónde salió la referencia.
4. Verificar en el checkout real que el nombre visible al cliente sea
   "Nima" (no "Atlas Commerce" ni "PetDrop").
5. Confirmar si Brey corrigió la configuración de moneda en AutoDS
   (causa raíz de un bug de precios DOP→USD que se repitió más de una
   vez en el catálogo).
6. Quitar la contraseña de la tienda para abrirla al público —
   decisión de timing de Brey, no técnica.
7. Renombrar el Project de claude.ai "Atlas-Comerce-Lab" en la UI
   (única parte manual que falta de la corrección ortográfica).

## Reglas de esta sesión, ya en memoria (no hace falta repetirlas)
- **Verificar contra el repo/API real antes de reportar algo como
  pendiente o roto** — no asumir desde memoria de sesión ni desde una
  copia vieja de un documento (regla del protocolo v2, sección 8).
- **Nunca escribir directo sobre el theme MAIN/publicado vía API** —
  Shopify lo bloquea. Flujo seguro: duplicar → aplicar fixes en el
  duplicado → Brey revisa y publica manualmente.
- `shopify theme pull`/`push` no son viables en este entorno (requieren
  login OAuth interactivo) — todo lo que Code hace contra Shopify es
  vía Admin GraphQL API (lectura y, en duplicados, escritura).
- Autoridad exclusiva de `git commit`/`push` es de Code, sin excepción.
- Numeración de decisiones nuevas en `ESTADO`: la asigna quien commitea
  (Code), nunca quien la propone — evita colisiones entre sesiones que
  no se vieron entre sí.
- Español neutro, sin coloquialismos. Brey es principiante en
  programación — explicar conceptos técnicos con contexto, sin asumir
  jerga previa.
