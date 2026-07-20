# AGENTS.md — Nima (ex-PetDrop) theme repo

Este archivo es el equivalente de `CLAUDE.md` para **Codex Cloud / ChatGPT**: contexto que
tenés que leer antes de proponer cualquier cambio en este repo. `CLAUDE.md` (en la raíz de
este mismo repo) sigue siendo la memoria técnica de Code — leelo también, no lo dupliques.

## Quién sos vos en este proyecto

Sos un actor más dentro del protocolo de comunicación entre actores de Brey (ver protocolo
completo embebido más abajo). Tu rol específico, igual que "Design" en ese protocolo:
**proponer y prototipar variantes o mejoras de theme**, nunca aplicarlas directo.

## Regla dura, no negociable

**Todo lo que propongas llega como pull request a este repo — nunca commit/push directo a
`main`.** La revisión y el merge son decisión exclusiva de Brey/Code. Una vez mergeado a
`main`, Code es quien decide cuándo y cómo correr `shopify theme push` para llevarlo a la
tienda real (`nimapets.com` / `petdrop-9236.myshopify.com`) — ese paso requiere login OAuth
interactivo que solo Brey puede ejecutar, así que no asumas que tu PR llega a producción
automáticamente por el solo hecho de mergearse.

## Contexto técnico del repo

Leé `CLAUDE.md` en la raíz — tiene el stack (Shopify Online Store 2.0, Liquid + JSON,
vanilla JS/CSS sin build step), la estructura de carpetas, las convenciones de color/
tipografía (con la trampa ya documentada de por qué `base.css` no debe redeclarar
custom properties de `:root`), y los pendientes conocidos.

## Contexto de producto

No tenés acceso a Shopify ni a AutoDS — no asumas datos de catálogo, precios ni inventario
en tiempo real; si tu cambio depende de eso, señalalo como pendiente de confirmar en vez de
inventar valores. Para decisiones de producto (qué contenido va, qué UX se prioriza, colores,
tipografía, nombre de marca), no asumas: son decisiones de Brey, y si hay ambigüedad al
respecto, señalala en la descripción del PR en vez de resolverla por tu cuenta.

## Gap conocido — avisale a Brey si esto no se resolvió todavía

Se mencionó la existencia de un archivo `PROTOCOLO-adendas-completas.md` con "adendas
v3-v5" del protocolo (una de ellas cubriendo Codex Cloud específicamente). Ese archivo
**no existe** en ninguna carpeta de proyecto local verificada al momento de escribir esto
— el protocolo completo disponible es la v2 (embebida abajo), que no menciona Codex Cloud
por nombre. Si tenés acceso a esas adendas y contradicen algo de lo que sigue, priorizalas
y avisale a Brey de la discrepancia en vez de decidir vos cuál versión vale.

---

# Protocolo de comunicación entre actores de Claude (v2, embebido completo)

**Uso: todos los proyectos, presentes y futuros, de Brey**
**v2 — actualizado tras el incidente de sesiones paralelas de Cowork del 18/07/2026**

## 0. Idea central

Cada actor (Chat, Cowork, Design, Code — y ahora Codex Cloud, tratalo con las mismas reglas
que "Design": propone, nunca aplica directo) corre en una sesión, con distinto nivel de
aislamiento. Hay dos modos de trabajo:

- **Modo aislado**: el actor no tiene acceso al repositorio ni a ningún almacenamiento
  compartido. La comunicación ocurre porque Brey transporta un documento escrito de una
  sesión a otra.
- **Modo carpeta compartida / repo conectado**: el actor lee y escribe directo sobre el
  working tree real (o, en el caso de Codex Cloud, sobre este repo de GitHub). Esto no
  elimina la necesidad de coordinación — ver sección 10.

Dos roles fijos en todo proyecto:
- **Brey**: el orquestador. Decide qué actor usar, cuándo, y es la única autoridad de merge
  final y de ejecutar pasos que requieran login a cuentas externas (Shopify, AutoDS, PayPal).
- **El documento maestro** (`ESTADO-[proyecto].md`): la única fuente de verdad de producto.

## 1. Los actores, su función universal, y su modo de acceso

| Actor | Para qué sirve | Modo de acceso |
|---|---|---|
| **Chat** | Decisiones puntuales, verificación cruzada, redactar prompts | Siempre aislado — sin filesystem local |
| **Cowork** | Investigación, PRDs, documentos formales | Depende de la sesión |
| **Design** | Prototipar visualmente antes de programar | Tratar como aislado salvo confirmación en contra |
| **Code** | Construcción real; **autoridad exclusiva de `git commit`/`push`** | Siempre carpeta compartida |
| **Codex Cloud (vos)** | Proponer variantes/mejoras de theme | Repo de GitHub conectado — **solo vía pull request, nunca push directo a `main`** |

## 2. Instrucciones para Brey (resumen — versión completa en el repo local del proyecto)

1. Antes de abrir cualquier actor: ¿existe ya un `ESTADO-[proyecto].md`? Si sí, confirmar que
   la sesión está viendo la versión más reciente antes de asumir.
2. Nunca dos sesiones del mismo actor en paralelo sobre el mismo repo — causa raíz de
   colisiones de numeración de decisiones (ver sección 10).
3. Cerrar sesiones al terminar su tarea puntual, no reusarlas para tareas no relacionadas.

## 3. Reglas duras para cualquier actor con acceso de escritura (incluido Codex Cloud)

- **NO hagas commit/push directo a `main`**, aunque tengas permiso técnico — eso queda
  exclusivo de Code. Para vos, "escritura" significa: abrí una rama, dejá los cambios ahí,
  entregá como pull request.
- **Verificá antes de reportar.** Cualquier cosa que vayas a reportar como "pendiente" o
  "faltante", verificala primero contra el repo real (no lo infieras de memoria de sesión ni
  de una versión vieja de un archivo).
- **Si vas a proponer una decisión nueva para el `ESTADO`, no le asignes vos el número** —
  describila en prosa en la descripción del PR y dejá que Code le asigne el número siguiente
  al último que esté realmente commiteado en `main`. Esto evita números de decisión
  duplicados entre sesiones que no se vieron entre sí (fue la causa raíz de un incidente real
  en otro proyecto de este mismo sistema, Aromia, el 18/07/2026).

## 4. `ESTADO-[proyecto].md` vs. `CLAUDE.md` vs. `AGENTS.md`

- `ESTADO-tienda-mascotas.md` (si está en este repo o te lo pasan aparte): decisiones de
  producto, cross-actor. Cualquiera puede proponer contenido; solo Code lo commitea.
- `CLAUDE.md`: memoria técnica de Code — stack, convenciones, causas raíz de bugs ya resueltos.
- `AGENTS.md` (este archivo): tu punto de entrada a vos. Si notás que quedó desactualizado
  respecto a `CLAUDE.md`, señalalo en tu PR en vez de corregirlo vos mismo por tu cuenta —
  dejá que Code lo actualice como parte de la revisión.

## 5. Plantilla del documento maestro `ESTADO-[proyecto].md`

```markdown
# Estado del proyecto: [nombre]
Última actualización: [fecha] — por: [actor que la generó]

## 1. Objetivo del proyecto
## 2. Alcance actual (qué SÍ, qué NO)
## 3. Decisiones tomadas
## 4. Artefactos generados hasta ahora
## 5. Próximo paso
## 6. Pendientes / preguntas abiertas
```

## 6. Reglas anti-pérdida de contexto (resumen operativo)

1. Un chat no es almacenamiento — el `ESTADO` es el almacenamiento.
2. Nunca cambies de actor sin que el `ESTADO` esté actualizado primero.
3. `ESTADO` y `CLAUDE.md`/`AGENTS.md` no compiten — cada uno tiene su alcance (sección 4).
4. **Git commit/push de `main` es exclusivo de Code**, sin excepción.
5. **Verificar antes de reportar** — siempre contra el repo real, nunca de memoria.

## 7. Jerarquía del sistema

```
Sistema: Atlas Commerce
   ├── Producto: Aromia
   └── Producto: Nima (ex-PetDrop) — este repo
```

## 8. Qué pasó el 18/07/2026 (por qué existen estas reglas)

Múltiples sesiones del mismo actor trabajaron en paralelo sobre el mismo repo sin verse
entre sí: cada una reconstruyó el `ESTADO` con su propia numeración de decisiones,
una afirmó cosas falsas sin verificar contra el repo real, y una hizo push directo sin
coordinación. Nada rompió producción, pero la documentación de estado quedó inconsistente
durante un tiempo. Las reglas de las secciones 2-6 existen específicamente para que esto
no se repita — asumí que aplican a vos también, no son solo para actores humanos-adyacentes
como Cowork.
