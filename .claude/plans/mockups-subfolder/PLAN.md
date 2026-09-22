# Mover cada archivo de mockup a una subcarpeta `mockups/`

## Índice

- [Objetivo del plan](#objetivo-del-plan)
- [Estado verificado del repo](#estado-verificado-del-repo)
  - [Archivos con lógica real que depende del layout plano](#archivos-con-lógica-real-que-depende-del-layout-plano)
  - [Archivos donde cada mención es solo prosa/ruta (sin cambio de comportamiento)](#archivos-donde-cada-mención-es-solo-prosaruta-sin-cambio-de-comportamiento)
- [Decisiones de diseño](#decisiones-de-diseño)
- [Enfoque](#enfoque)
  - [1. Establecer la convención (D1)](#1-establecer-la-convención-d1)
  - [2. Puntos de escritura](#2-puntos-de-escritura)
  - [3. Puntos de lectura/descubrimiento](#3-puntos-de-lecturadescubrimiento)
  - [4. `pv-update`: migración activa de entries legacy (D5, D6)](#4-pv-update-migración-activa-de-entries-legacy-d5-d6)
  - [5. `pv-status/scripts/filter_status.py`: `extra_files` sigue siendo preciso, y se añade `mockups_count`](#5-pv-statusscriptsfilter_statuspy-extra_files-sigue-siendo-preciso-y-se-añade-mockups_count)
- [Archivos críticos](#archivos-críticos)
- [Plan de implementación](#plan-de-implementación)
  - [Paso 1 — Convención base en las skills de mockup (D1)](#paso-1--convención-base-en-las-skills-de-mockup-d1)
  - [Paso 2 — Puntos de escritura nuevos (pv-new, pv-fix)](#paso-2--puntos-de-escritura-nuevos-pv-new-pv-fix)
  - [Paso 3 — Puntos de lectura/descubrimiento (pv-how)](#paso-3--puntos-de-lecturadescubrimiento-pv-how)
  - [Paso 4 — `extend-entry.md`: migración incidental de entries legacy (D4, D6)](#paso-4--extend-entrymd-migración-incidental-de-entries-legacy-d4-d6)
  - [Paso 5 — `pv-todo`: D2 (eliminar creación), D3 (copia D.4 consciente de subcarpetas), D6 (nombre nuevo en el listado/copia)](#paso-5--pv-todo-d2-eliminar-creación-d3-copia-d4-consciente-de-subcarpetas-d6-nombre-nuevo-en-el-listadocopia)
  - [Paso 6 — `pv-status`: separar `extra_files` de `mockups_count`](#paso-6--pv-status-separar-extra_files-de-mockups_count)
  - [Paso 7 — `pv-update`: migración activa de entries legacy (D5, D6)](#paso-7--pv-update-migración-activa-de-entries-legacy-d5-d6)
  - [Paso 8 — Pase de consistencia final](#paso-8--pase-de-consistencia-final)
- [Reviews](#reviews)
  - [2026-09-22 (pasadas 1-3, previas a la formalización de esta sección)](#2026-09-22-pasadas-1-3-previas-a-la-formalización-de-esta-sección)
  - [2026-09-22 (pasada 4)](#2026-09-22-pasada-4)
  - [2026-09-22 (pasada 5)](#2026-09-22-pasada-5)
  - [2026-09-22 (pasada 6)](#2026-09-22-pasada-6)
  - [2026-09-22 (pasada 7)](#2026-09-22-pasada-7)

## Objetivo del plan

Hoy, cada mockup visual que `pv-new`/`pv-fix` generan para un cambio/fix (`design_*.html`,
`design_*.txt`) vive suelto, directamente dentro de la carpeta propia de la entry
(`{changesDir}/inProgress/{xxxx}/`), junto a `description.md`, `plan.md`, `history.md` — y junto a
`design_navigation_*.md`/`design_data_*.md`, que **no** son mockups (no los genera la skill de
mockups configurada en `framework.skills.mockups`; `pv-new`/`pv-fix` los escriben directamente como
documentos funcionales de navegación/datos) y **quedan fuera del alcance de este plan**: se quedan
donde están, sueltos en la raíz de la entry, sin ningún cambio.

Este plan mueve solo `design_*.html`/`design_*.txt` (lo que de verdad gestiona la skill de mockups)
a una subcarpeta dedicada `{changesDir}/inProgress/{xxxx}/mockups/`, con dos objetivos concretos:

1. **Desacoplar al resto del framework de la extensión/tecnología del mockup.** `pv-how`,
   `pv-status`, `pv-todo`, etc. dejan de necesitar enumerar los patrones `design_*.html`/
   `design_*.txt` por nombre — solo necesitan saber "esta entry tiene una carpeta `mockups/`" y
   delegar su contenido a la skill de mockups configurada (`framework.skills.mockups`).
   `design_navigation_*.md`/`design_data_*.md` siguen necesitando su propio glob por nombre, igual
   que hoy — no son responsabilidad de la skill de mockups y este plan no cambia eso.
2. **Ser prerrequisito bloqueante para el plan [`interactive-mockups`](../interactive-mockups/PLAN.md)**,
   cuyo contrato `ensure-closed`/`describe` ya asume ese desacoplamiento para los mockups HTML/ASCII
   — el layout plano de hoy obliga a `pv-how` a enumerar el patrón `design_*.html`/`design_*.txt`
   por nombre además de los otros dos (ver el hallazgo "Critical analysis (2026-09-22)" de ese plan
   sobre el paso 1.1 de `pv-how`). **Este plan debe aterrizar antes de que empiece la
   implementación de `interactive-mockups`.**

Nota: las skills de mockup (`pv-internal-mockups-html`/`pv-internal-mockups-ascii`) ya eran
agnósticas de la subcarpeta desde el principio — "carpeta de destino" siempre fue un parámetro de
entrada que provee quien llama, nunca algo que resuelven por sí mismas. Lo que cambia es que el
*resto* del framework empieza a pasarles `mockups/` como ese destino, en vez de la raíz de la
entry.

**Fuera de alcance**: este plan no toca el framework de anotaciones, `ensure-closed`, `describe`,
ni ninguna parte del contrato de `interactive-mockups` — eso es trabajo del otro plan, construido
encima de este.

**Añadido al alcance (D6)**: aunque `design_navigation_*.md`/`design_data_*.md` no se mueven a
`mockups/` (no son mockups, no los gestiona `framework.skills.mockups`), el prefijo `design_` que
llevan hoy induce a pensar que sí lo son. Este plan también los renombra a `navigation_*.md`/
`data_*.md` — mismo tipo de cambio (naming/descubrimiento), mismos archivos ya en juego (`pv-new`,
`pv-fix`, `extend-entry.md`, `pv-how`, `pv-todo`), y por eso viaja en este plan en vez de en uno
aparte. Ver D6 en "Decisiones de diseño".

## Estado verificado del repo

Investigación en dos pasadas contra el repo real (no contra suposiciones): una primera pasada
(`Explore`) hizo grep de `design_*.html` / `design_navigation_*.md` / `design_data_*.md` /
`design_*.txt` en cada skill `pv-*`, clasificando cada hit como prosa pura o lógica real que asume
el layout plano; una segunda pasada auditó cada cita línea por línea contra los archivos actuales,
y una tercera cazó específicamente bugs de lógica, huecos y casos límite que la primera pasada no
cubría (ver "Historial de revisión" al final). Lo que sigue ya incorpora las correcciones y
decisiones de las tres pasadas.

### Archivos con lógica real que depende del layout plano

1. **`pv-status/scripts/filter_status.py`** — `count_extra_files()` (L196-201) calcula
   `entry_dir.iterdir()` de forma no recursiva, filtrado por `p.is_file()`, contra
   `TERMINAL_FRAMEWORK_FILES = {"description.md", "plan.md", "history.md"}` (línea 151) — todo lo
   demás directamente dentro de la carpeta de la entry cuenta como "extra" y se muestra en la
   tarjeta de detalle del modo `--terminal` (`extra files: N`). Una subcarpeta `mockups/` es un
   directorio, no un archivo — `iterdir()` no descenderá en ella y `p.is_file()` la filtra por
   completo. Sin fix, este conteo cae silenciosamente a 0 para cada entry con mockups.
2. **`pv-how/SKILL.md`** (paso 1.1, ~L80) y **`pv-how/workflow.how.md`** (nodo `S11Validate`,
   ~L27) — instruyen leer `description.md` y los archivos `design_*` "en busca de
   inconsistencias" sin especificar ruta; hoy eso implícitamente es la raíz de la entry.
3. **`pv-how/SKILL.md`** paso 3, punto 2 (~L124) — abre `design_*.html` "como referencia visual";
   mismo problema de ruta implícita.
4. **`pv-new/extend-entry.md`** (paso 1, L5) — dice explícitamente "comprobar si ya existen
   archivos `design_*.html`, `design_navigation_*.md` o `design_data_*.md` **en esa misma
   carpeta**" (la misma que `description.md`).
5. **`pv-new/todo-mode.md`** (L6) — lee "sus archivos `design_*.html` en esa misma carpeta" al
   promocionar una idea ya anotada bajo `{changesDir}/todo/{code}/` a `inProgress/`.
6. **`pv-todo/SKILL.md`** — dos puntos distintos, ambos con lógica real:
   - **L93** (paso D.2, listado de confirmación): al convertir una entry `inProgress/{xxxx}/` de
     vuelta a idea `todo/`, lista "los archivos que contiene la carpeta... cualquier `design_*`,
     `design_data_*`, etc." antes de confirmar con el usuario.
   - **Paso D.4, L101-108** (la copia real, **distinta** del listado anterior): copia "cada
     archivo" de la entry hacia `todo/{code}/`, fraseado enteramente en términos de archivos
     individuales — sin mención de subcarpetas. Una `mockups/` no se copiaría como tal con una
     lectura literal de este paso.
   - **Paso 3, L71** (creación directa de mockups en una idea `todo/` nueva, *no* proveniente de
     una democión): "si la idea tiene un componente visual claro... puedes crear algunos
     `design_*.html`, igual que hace `pv-new`... en esa misma carpeta". Este es un tercer punto de
     escritura independiente de D.4, y no encaja con la intención de este plan (ver decisión más
     abajo).

### Archivos donde cada mención es solo prosa/ruta (sin cambio de comportamiento)

- `pv-new/SKILL.md` paso 3 (L102-118): crea `design_navigation_*.md`/`design_data_*.md`
  "directamente en `{changesDir}/inProgress/{xxxx}/`" (L106); invoca la skill de mockups con la
  carpeta de destino (L103); el mensaje de confirmación al usuario (L115) construye estas rutas.
- `pv-fix/SKILL.md` (pasos 4/4.1/5, L100-108) — mismo patrón que `pv-new`.
- `pv-new/workflow.new.md` / `pv-fix/workflow.fix.md` — nodos Mermaid que nombran los mismos
  patrones como lo que se crea; etiquetas que reflejan la prosa de arriba, sin lógica de glob
  propia.
- `pv-internal-tech-mermaid/SKILL.md` (L15) — frase comparativa que delimita el rol de esta skill
  frente a las de mockup/navegación. Sin lógica.
- `pv-internal-mockups-html/SKILL.md` y `pv-internal-mockups-ascii/SKILL.md` (L25-29 en ambas) —
  ya agnósticas de la subcarpeta; solo el texto ilustrativo por defecto ("normalmente
  `{changesDir}/inProgress/{xxxx}/`") pide actualizarse.
- `pv-internal-doc-style/SKILL.md` (L26, L61), `pv-do/SKILL.md` (L119, L121), `pv-init/SKILL.md`
  (L82, L185) — todas consumen "contexto ya reunido" que `pv-do`/`pv-init` ensamblan; ninguna hace
  descubrimiento de directorio propio ni fija un patrón de nombre de fichero — las rutas que citan
  se propagan automáticamente en cuanto se actualicen los llamadores de arriba. `pv-internal-doc-
  features/SKILL.md` **no** entra en este grupo (ver Reviews, pasada 7): fija por nombre el patrón
  `design_navigation_*.md`, que D6 retira — movido a "Archivos críticos" y a la sección 3 de
  "Enfoque"/Paso 3 de "Plan de implementación", como punto de lectura más.
- `pv-init/schema.json` — dos menciones dentro de `description` de JSON Schema
  (`framework.changes.language`, `framework.skills.mockups`); ninguna asume un layout plano.
- `pv-new/hooks/20-after-entry.template.md` (L3) — describe cuándo corre un hook de proyecto
  "tras validar el paso 4 los `design_*`"; prosa, sin lógica de directorio.

## Decisiones de diseño

**D1 — Convención base.** Todo archivo de mockup vive bajo `{carpeta de destino}/mockups/`, nunca
suelto en la raíz de la entry. Quien invoca la skill de mockups es responsable de pasar
`{changesDir}/inProgress/{xxxx}/mockups/` (no la raíz) como "carpeta de destino" — la skill de
mockups no crea ni asume el nombre de la subcarpeta, simplemente escribe donde se le indique,
igual que hoy.

**D2 — `pv-todo` deja de poder crear mockups.** Se elimina la capacidad del paso 3 (L71) de crear
`design_*.html` al anotar una idea nueva — anotar una idea vuelve a ser texto puro, sin excepción
para ideas con componente visual. Consecuencia: una idea `todo/{code}/` solo puede llegar a tener
una subcarpeta `mockups/` como resultado de **degradar** una entry `inProgress/` que ya tenía
mockups (el flujo D.1-D.4), nunca por creación directa. Esto simplifica todo lo demás: solo hay
una vía de entrada de mockups a `todo/`, no dos.

**D3 — La copia D.4 preserva `mockups/` como subárbol y marca su antigüedad.** Al degradar una
entry a idea, `mockups/` (si existe) se copia como subcarpeta completa a
`{changesDir}/todo/{code}/mockups/`, preservando su estructura, junto al resto de archivos sueltos
que D.4 ya copiaba. Además, se escribe en esa carpeta destino un fichero `mockups/important.md`
con un texto fijo indicando que esos mockups fueron generados en el pasado (con la fecha de la
conversión) y deben tomarse solo como material de referencia/ejemplo, no como el diseño vigente —
esto evita que, si la idea se vuelve a promocionar más adelante, alguien confunda un mockup
congelado con el diseño actual.

**D4 — `extend-entry.md` migra entries legacy al extenderlas.** Si el paso 1 (actualizado para
mirar solo en `mockups/`) encuentra en su lugar archivos `design_*` sueltos en la raíz de una
entry sin `mockups/` (una entry anterior a esta convención), migra primero: crea `mockups/` y
mueve esos archivos dentro, antes de continuar con el resto del paso. Esto evita que los pasos 4-6
creen una `mockups/` nueva al lado de archivos legacy intactos, partiendo los mockups de una misma
entry entre dos ubicaciones — y de paso evita que la acción `edit` de las skills de mockup (que
resuelven solo por nombre exacto de archivo en la carpeta de destino, sin verificación de
existencia propia — ver `pv-internal-mockups-html/SKILL.md` L23-29/L57-64) produzca un duplicado
silencioso en vez de una edición real.

**D5 — Entries legacy no extendidas se migran vía `pv-update`, no vía fallback en `pv-how`.**
Decisión explícita: `pv-how` (y cualquier otro punto de lectura/descubrimiento) **nunca** mira la
raíz de una entry buscando mockups, ni siquiera como fallback — solo `mockups/`. La
responsabilidad de que ninguna entry se quede en estado legacy recae en `pv-update`
(`.claude/skills/pv-update/`), que ya sigue el patrón adecuado para esto: un script de auditoría
de solo lectura (`scripts/audit-context.py`) que reporta problemas, seguido de un bucle de fixes
deterministas auto-aplicados (paso 3 de `pv-update/SKILL.md`), sin pedir confirmación al usuario
salvo los cuatro casos ya documentados como excepción (este no es uno de ellos). Se acepta
explícitamente la ventana de exposición entre la publicación de esta migración y la primera
ejecución de `pv-update` en cada proyecto: durante esa ventana, una entry legacy que nadie ha
extendido todavía es invisible para `pv-how`.

**D6 — `design_navigation_*.md`/`design_data_*.md` pierden el prefijo `design_` (no son mockups).**
No los genera la skill de mockups (`framework.skills.mockups`); `pv-new`/`pv-fix`/`extend-entry.md`
los escriben directamente como documentos funcionales de navegación y datos, no como mockups
visuales. El prefijo `design_` que comparten hoy con `design_*.html`/`design_*.txt` es engañoso —
sugiere que son mockups y que deberían vivir en `mockups/`, cuando en realidad se quedan sueltos en
la raíz de la entry (ver "Añadido al alcance" arriba). Se renombran a `navigation_<description>.md`
y `data_<description>.md` respectivamente, sin cambio de contenido, formato ni ubicación — solo el
nombre del archivo. Entries legacy con el nombre viejo (`inProgress/`/`implemented/`, igual que D5;
`closed/` queda fuera, historia congelada) se migran vía `pv-update`, mismo mecanismo que D5: un
check determinista más en `audit-context.py`, hermano de `check_legacy_loose_mockups`, que detecta
y renombra sin pedir confirmación. Sin fallback al nombre viejo en ningún punto de lectura —mismo
criterio que D5— la garantía de que ninguna entry se quede con el nombre legacy la da `pv-update`.

## Enfoque

### 1. Establecer la convención (D1)

Añadir una regla breve y explícita cerca del inicio de `pv-internal-mockups-html/SKILL.md` y
`pv-internal-mockups-ascii/SKILL.md` (sección "Expected input from the caller" de ambas): todo
archivo de mockup vive bajo `{carpeta de destino}/mockups/`, nunca suelto en la raíz de la entry.
Actualizar también la línea ilustrativa "normalmente `{changesDir}/inProgress/{xxxx}/`" a
"normalmente `{changesDir}/inProgress/{xxxx}/mockups/`" — sin cambio de comportamiento real, ya
que el destino siempre viene del argumento que provee quien llama.

### 2. Puntos de escritura

- `pv-new/SKILL.md` paso 3 (L102-118): pasar `{changesDir}/inProgress/{xxxx}/mockups/` como
  carpeta de destino al invocar la skill de mockups (solo `design_*.html`). El
  `design_navigation_*.md` que este mismo paso escribe (L106) **no** se mueve a `mockups/` — sigue
  directamente en la raíz de la entry, pero renombrado a `navigation_<description>.md` (D6).
- `pv-new/SKILL.md` paso 3.1: el `design_data_*.md` que escribe se renombra a
  `data_<description>.md` (D6) — sigue en la raíz de la entry, sin subcarpeta.
- `pv-new/SKILL.md` paso 4 (mensaje de validación, L115): rutas mostradas al usuario reflejan
  `mockups/` para el mockup HTML/ASCII y los nuevos nombres `navigation_*.md`/`data_*.md` para
  navegación/datos.
- `pv-fix/SKILL.md` pasos 4/4.1/5 (L100-108): los mismos cambios, reflejados (mockup a `mockups/`,
  `design_data_*.md` → `data_*.md` renombrado en la raíz, mensaje de validación actualizado).
- `pv-new/extend-entry.md` paso 1 (L5): comprobar existencia del mockup bajo `mockups/`, no en la
  raíz; comprobar `navigation_*.md`/`data_*.md` (nombre nuevo) en la raíz de la entry, no
  `design_navigation_*.md`/`design_data_*.md`. Si encuentra el mockup suelto en la raíz sin
  `mockups/` (entry legacy), **migrarlo primero** — crear `mockups/` y moverlo dentro antes de
  continuar (D4). Si encuentra `design_navigation_*.md`/`design_data_*.md` con el nombre viejo
  (entry legacy, D6), renombrarlos a `navigation_*.md`/`data_*.md` antes de continuar — mismo
  principio de migración incidental que D4, aplicado al rename.
- `pv-new/extend-entry.md` pasos 4/5/6/8: carpeta de destino `mockups/` para `create`/`edit` del
  mockup; `navigation_<description>.md`/`data_<description>.md` (nombre nuevo, D6) para crear/editar
  navegación/datos, en la raíz de la entry. Rutas presentadas al usuario (paso 6) y en el mensaje
  final (paso 8) reflejan ambos cambios.
- `pv-new/todo-mode.md`, tres puntos distintos (no solo L6): paso 2 ("y, si las hay, sus archivos
  `design_*.html` en esa misma carpeta" → pasa a "y, si existe, el contenido de su carpeta
  `mockups/`"), paso 4 ("Si había `design_*.html` en la idea de `todo/`, tenlos en cuenta..." →
  "Si había contenido en `mockups/` de la idea, tenlo en cuenta...") y paso 5 ("borra...
  `description.md` y cualquier `design_*.html` que tuviera" → "borra... `description.md` y su
  carpeta `mockups/` si existe"). Los tres leen/actúan sobre lo que haya dentro de `mockups/` como
  carpeta opaca, sin asumir el nombre `design_*.html` — esa carpeta ahora solo puede existir por
  democión (D2); ver también punto 3, D.4.
- **`pv-todo/SKILL.md` paso 3 (L71): eliminar la capacidad de crear `design_*.html` al anotar una
  idea nueva** (D2) — anotar una idea vuelve a ser texto puro, sin excepción visual.
- Diagramas: `pv-new/workflow.new.md`, `pv-fix/workflow.fix.md` — actualizar etiquetas de nodo
  donde la ruta esté deletreada explícitamente (su regla de "el diagrama manda" implica que un
  cambio de prosa que altere secuencia/ramificación debe reflejarse aquí también; un cambio puro
  de cadena de ruta no requiere tocar el diagrama salvo que el propio diagrama la deletree).

### 3. Puntos de lectura/descubrimiento

- `pv-how/SKILL.md` paso 1.1 y `pv-how/workflow.how.md` nodo `S11Validate`: leer `description.md`,
  todo lo que haya bajo `mockups/` de la entry (mockup HTML/ASCII), y `navigation_*.md`/`data_*.md`
  (nombre nuevo, D6) sueltos en la raíz de la entry — dos ubicaciones distintas, no una sola.
  **Sin fallback al layout/nombre legacy** (D5 para `mockups/`, D6 para el rename) — la garantía de
  que ninguna entry se quede legacy la da `pv-update` (punto 4) y la migración incidental de
  `extend-entry.md` (punto 2, D4/D6).
- `pv-how/SKILL.md` paso 3, punto 2 (mockup `design_*.html` como referencia visual): leer desde
  `mockups/`.
- `pv-how/SKILL.md` paso 3, punto 3 (L125, `design_data_*.md` como fuente de verdad para el
  diseño técnico de datos): leer `data_*.md` (nombre nuevo, D6) de la raíz de la entry, no de
  `mockups/` — se había quedado fuera de la migración original y, tras D6, tampoco va a
  `mockups/` porque no es un mockup.
- `pv-internal-doc-features/SKILL.md` (D6; hallazgo de Reviews, pasada 7) — dos menciones, ambas
  fijan por nombre el patrón retirado: L26 ("Content checklist", carga de diagramas funcionales a
  arrastrar a la documentación de features) y L66 (parámetro `context` de la acción `upsert`).
  Ambas pasan de `design_navigation_*.md` a `navigation_*.md` (nombre nuevo, D6), sueltos en la
  raíz de la entry — sin cambio de ubicación ni de lógica, solo el patrón de nombre que cita el
  texto. Invocada por `pv-do` tras implementar, no por el propio flujo de escritura/lectura de
  `pv-new`/`pv-fix`/`pv-how` — mismo rol de "lector", por eso vive en este punto y no en "Puntos de
  escritura".
- `pv-todo/SKILL.md` paso D.2 (L93, listado de confirmación): enumerar explícitamente el contenido
  de `mockups/` (mockup HTML/ASCII) por un lado, y los `navigation_*.md`/`data_*.md` (nombre
  nuevo, D6) sueltos en la raíz por otro — no un solo glob de `design_*`.
- `pv-todo/SKILL.md` paso D.4 (L101-108, la copia real — distinta del listado anterior): copiar
  `mockups/` (si existe) como subcarpeta completa hacia `{changesDir}/todo/{code}/mockups/`,
  preservando su estructura, junto al resto de archivos sueltos que ya copiaba (incluidos
  `navigation_*.md`/`data_*.md`, que siguen siendo archivos sueltos, solo que con nombre nuevo).
  Escribir además `mockups/important.md` con el texto fijo de "material histórico, solo
  referencia" (D3) — nota: ese aviso aplica solo al mockup visual; `navigation_*.md`/`data_*.md`
  copiados no necesitan el mismo aviso porque no son "diseño vigente" en el mismo sentido (son
  datos/flujo funcionales, no un mockup congelado que pueda confundirse con el actual).

### 4. `pv-update`: migración activa de entries legacy (D5, D6)

Dos problemas nuevos e independientes en el catálogo de `audit-context.py`, uno por decisión:

- **`legacy-loose-mockups:<xxxx>` (D5)** — detectado recorriendo `{changesDir}/inProgress/*` en
  busca de archivos `design_*.html` / `design_*.txt` sueltos directamente en la raíz de una entry
  cuya subcarpeta `mockups/` no existe. **No incluye** `design_navigation_*.md`/`design_data_*.md`
  ni sus nombres nuevos (`navigation_*.md`/`data_*.md`) — esos nunca van a `mockups/`, los cubre el
  check siguiente. Fix determinista y automático en el paso 3 de `pv-update/SKILL.md` (no uno de
  los cuatro casos que requieren confirmación del usuario): crear `mockups/` y mover esos archivos
  dentro. Reportar en el paso 4 de `pv-update` bajo una nueva área ("mockups"), junto al resto del
  informe.
- **`legacy-design-prefix:<xxxx>` (D6)** — detectado recorriendo `{changesDir}/inProgress/*` en
  busca de `design_navigation_*.md`/`design_data_*.md` (nombre viejo) sueltos en la raíz de una
  entry. Fix determinista y automático en el mismo paso 3: renombrar cada uno a
  `navigation_*.md`/`data_*.md` respectivamente, preservando el resto del nombre y su ubicación (no
  se mueven, solo se renombran). Reportar en el paso 4 bajo una nueva área ("design-prefix"), junto
  al resto del informe.

### 5. `pv-status/scripts/filter_status.py`: `extra_files` sigue siendo preciso, y se añade `mockups_count`

`count_extra_files(entry_dir)` (L196-201) debe seguir contando archivos "extra" (cualquier cosa
que no sea `description.md`/`plan.md`/`history.md`) después de la migración. Un `rglob`
recursivo sin más lo resolvería, pero mezclaría los mockups dentro del mismo número genérico —
hoy la tarjeta de detalle en modo `--terminal` (`render_terminal`, L478: `f"extra files:
{extra_files}"`) es la única vista que expone este dato al usuario, y perder la distinción "esto
son mockups" dentro de un conteo genérico es una regresión de información, no solo un detalle de
implementación.

Nota (D6): `navigation_*.md`/`data_*.md` (nombre nuevo) siguen contando como `extra_files`, igual
que `design_navigation_*.md`/`design_data_*.md` contaban hoy — el rename no cambia su ubicación
(siguen sueltos en la raíz) ni su naturaleza de "extra". Ningún cambio adicional en esta sección
por causa de D6.

**Decisión**: separar en dos campos.
- `extra_files` sigue contando archivos sueltos directamente en la raíz de la entry (no
  recursivo, mismo comportamiento que hoy) que no sean `description.md`/`plan.md`/`history.md` ni
  el propio directorio `mockups/` — tras esta migración, en el camino feliz este número debería
  ser 0 salvo casos excepcionales (p. ej. una entry legacy aún no migrada por `pv-update`, ver
  punto 4).
- Nuevo campo `mockups_count`: número de archivos dentro de `entry_dir / "mockups"` (si existe;
  `None` si no existe, igual que `risk` cuando no hay `.metadata.json`) — no recursivo dentro de
  `mockups/` tampoco, es una carpeta plana por convención (D1).

Cambios concretos en `build_entry()` (L204-259) y `render_terminal()` (~L448-484):
- Añadir `count_mockups_files(entry_dir)`, análoga a `count_extra_files` pero apuntando a
  `entry_dir / "mockups"` y devolviendo `None` si esa subcarpeta no existe.
- En `count_extra_files`, excluir explícitamente el nombre `"mockups"` del recuento (sigue siendo
  `iterdir()` + `is_file()`, sin necesidad de `rglob` — un directorio ya lo descarta `is_file()`
  hoy; el cambio real es solo conceptual: el docstring deja de decir "e.g. design_*.html mockups"
  como ejemplo de qué cuenta, porque los mockups ya no viven ahí en el camino feliz).
- En `build_entry()`, calcular `mockups_count = None if state == "todo" else
  count_mockups_files(entry_dir)` y añadirlo al dict devuelto.
- En `render_terminal()`, tras la línea `extra files: {extra_files}` (L478), añadir una línea
  `mockups: {mockups_count}` **solo si `mockups_count` no es `None`** (mismo patrón condicional
  que `Related: ...` en L480-481, que solo se muestra si `related_ids` no está vacío) — una entry
  sin mockups no debe mostrar una línea "mockups: 0" ruidosa.

Actualizar el docstring (~L30-36) para documentar `mockups_count` junto a `extra_files`, y el
comentario de `TERMINAL_FRAMEWORK_FILES` (L147-151) para aclarar que `mockups/` se excluye del
conteo de "extra" porque se cuenta y muestra por separado.

## Archivos críticos

- `D:\repos\previo-sdd\.claude\skills\pv-status\scripts\filter_status.py` — `count_extra_files`
  excluye `mockups/`, nueva `count_mockups_files`, `build_entry`/`render_terminal` exponen
  `mockups_count` (cambio de lógica real, punto 5). Sin cambio por D6 (nota en el punto 5).
- `D:\repos\previo-sdd\.claude\skills\pv-update\scripts\audit-context.py` — dos problemas nuevos:
  `legacy-loose-mockups:<xxxx>` (D5, detección de mockups sueltos) y `legacy-design-prefix:<xxxx>`
  (D6, detección de `design_navigation_*.md`/`design_data_*.md` con nombre viejo) — ambos cambio de
  lógica real, punto 4.
- `D:\repos\previo-sdd\.claude\skills\pv-update\SKILL.md` — dos fixes deterministas nuevos en el
  paso 3 (D5, D6), dos áreas nuevas en el informe del paso 4 ("mockups", "design-prefix").
- `D:\repos\previo-sdd\.claude\skills\pv-how\SKILL.md` — paso 1.1 (dos ubicaciones: `mockups/` +
  `navigation_*.md`/`data_*.md` en la raíz), paso 3 punto 2 (`mockups/`), paso 3 punto 3 (L125,
  `data_*.md` en la raíz, nombre nuevo D6).
- `D:\repos\previo-sdd\.claude\skills\pv-how\workflow.how.md` — nodo `S11Validate`.
- `D:\repos\previo-sdd\.claude\skills\pv-internal-doc-features\SKILL.md` — L26 (checklist de
  diagramas funcionales a arrastrar) y L66 (parámetro `context` de `upsert`): ambas
  `design_navigation_*.md` → `navigation_*.md` (nombre nuevo, D6), sin cambio de carpeta (hallazgo
  de Reviews, pasada 7).
- `D:\repos\previo-sdd\.claude\skills\pv-new\SKILL.md` — pasos 3 (mockup a `mockups/`,
  `design_navigation_*.md` → `navigation_*.md` en la raíz), 3.1 (`design_data_*.md` →
  `data_*.md` en la raíz), 4 (mensaje de validación).
- `D:\repos\previo-sdd\.claude\skills\pv-new\extend-entry.md` — pasos 1 (con migración legacy de
  D4 y D6), 4, 5, 6, 8.
- `D:\repos\previo-sdd\.claude\skills\pv-new\todo-mode.md` — pasos 2, 4, 5 (lectura, uso al
  construir la propuesta visual y borrado de `mockups/`, no solo L6).
- `D:\repos\previo-sdd\.claude\skills\pv-new\workflow.new.md`.
- `D:\repos\previo-sdd\.claude\skills\pv-fix\SKILL.md` — pasos 4 (mockup a `mockups/`), 4.1
  (`design_data_*.md` → `data_*.md` en la raíz), 5 (mensaje de validación).
- `D:\repos\previo-sdd\.claude\skills\pv-fix\workflow.fix.md`.
- `D:\repos\previo-sdd\.claude\skills\pv-todo\SKILL.md` — L93 (listado D.2, dos ubicaciones), paso
  D.4 L101-108 (copia real + `important.md` solo para el mockup), paso 3/L71 (eliminar creación de
  mockups, D2).
- `D:\repos\previo-sdd\.claude\skills\pv-internal-mockups-html\SKILL.md` — regla D1 + texto de
  ejemplo.
- `D:\repos\previo-sdd\.claude\skills\pv-internal-mockups-ascii\SKILL.md` — regla D1 + texto de
  ejemplo.
- (referencia, sin cambio esperado — verificado prosa-only, las rutas se propagan automáticamente
  desde los llamadores de arriba) `pv-internal-doc-style/SKILL.md`,
  `pv-do/SKILL.md`, `pv-init/SKILL.md`, `pv-init/schema.json`,
  `pv-internal-tech-mermaid/SKILL.md`, `pv-new/hooks/20-after-entry.template.md`,
  `pv-init/workflow.init.md` (L49, etiqueta de nodo Mermaid nombrando la clave de configuración
  `framework.skills.mockups`, sin lógica de ruta).

## Plan de implementación

Orden pensado para que cada paso sea verificable de forma aislada antes de depender de él el
siguiente, y para que un fallo a mitad de camino deje el repo en un estado consistente (nunca
"algunos escritores ya apuntan a `mockups/` pero ningún lector lo espera todavía", ni viceversa).

### Paso 1 — Convención base en las skills de mockup (D1)

Editar `pv-internal-mockups-html/SKILL.md` y `pv-internal-mockups-ascii/SKILL.md`:
- Añadir la regla "todo archivo de mockup vive bajo `{carpeta de destino}/mockups/`, nunca suelto
  en la raíz de la entry" en la sección "Expected input from the caller".
- Cambiar el texto ilustrativo "normalmente `{changesDir}/inProgress/{xxxx}/`" por "normalmente
  `{changesDir}/inProgress/{xxxx}/mockups/`".

Sin riesgo: ninguna llamada real cambia todavía (los callers siguen pasando la raíz hasta el paso
2), es solo documentación/contrato de la skill. Verificable con una lectura del diff.

### Paso 2 — Puntos de escritura nuevos (pv-new, pv-fix)

Editar en este orden (cada uno es independiente, pero agrupar el commit por skill facilita
revertir si algo falla):

1. `pv-new/SKILL.md` pasos 3, 3.1, 4 — carpeta de destino `mockups/` para el mockup HTML/ASCII;
   `design_navigation_*.md`/`design_data_*.md` renombrados a `navigation_*.md`/`data_*.md` (D6),
   ambos sin moverse de la raíz de la entry; rutas del mensaje de validación reflejando ambos
   cambios.
2. `pv-fix/SKILL.md` pasos 4, 4.1, 5 — mismos cambios, mirror de `pv-new`.
3. `pv-new/workflow.new.md`, `pv-fix/workflow.fix.md` — actualizar solo las etiquetas de nodo que
   deletreen la ruta o el nombre de archivo explícitamente (revisar caso por caso antes de tocar,
   para no editar diagramas que no lo necesitan).

**Verificación de este paso**: correr `pv-new` end-to-end sobre un cambio visual desechable;
confirmar que `design_*.html` aterriza en `{changesDir}/inProgress/{xxxx}/mockups/` y que
`navigation_*.md`/`data_*.md` (nombre nuevo, sin prefijo `design_`) aterrizan sueltos en
`{changesDir}/inProgress/{xxxx}/`, no en `mockups/`. Repetir con `pv-fix` sobre un fix no trivial.

En este punto del despliegue, las entries **nuevas** ya usan `mockups/`, pero `pv-how`/`pv-status`
todavía no lo saben — es una ventana esperada dentro de esta implementación (no del despliegue a
producción; los pasos siguen aplicándose en la misma sesión de trabajo antes de dar el plan por
cerrado).

### Paso 3 — Puntos de lectura/descubrimiento (pv-how, pv-internal-doc-features)

Editar `pv-how/SKILL.md` (paso 1.1, paso 3 punto 2, paso 3 punto 3) y `pv-how/workflow.how.md`
(nodo `S11Validate`): el mockup se lee desde `mockups/`, sin fallback a la raíz (D5);
`navigation_*.md`/`data_*.md` se leen sueltos en la raíz de la entry, con el nombre nuevo sin
prefijo `design_`, sin fallback al nombre viejo (D6).

Editar además `pv-internal-doc-features/SKILL.md` (L26, checklist de diagramas funcionales a
arrastrar a la documentación de features; L66, parámetro `context` de la acción `upsert`):
`design_navigation_*.md` → `navigation_*.md` (nombre nuevo, D6) en ambas menciones, sin cambio de
ubicación (siguen sueltos en la raíz de la entry, este archivo nunca tocó `mockups/`). Hallazgo de
Reviews, pasada 7 — vive aquí y no en el Paso 2 porque esta skill es consumidora (la invoca
`pv-do` tras implementar), no productora.

**Verificación**: correr `pv-how` sobre la entry creada en el paso 2; confirmar que la
comprobación de consistencia del paso 1.1 lee tanto `mockups/` como `navigation_*.md`/`data_*.md`
de la raíz, que la referencia visual del paso 3 punto 2 lee `mockups/`, y que la lectura de
`data_*.md` del paso 3 punto 3 lee de la raíz (nombre nuevo). Sobre una entry legacy preexistente
en el repo (si hay alguna con mockups sueltos en la raíz, o con `design_navigation_*.md`/
`design_data_*.md` sin renombrar), confirmar que `pv-how` **no** los encuentra en ninguno de los
dos casos — comportamiento esperado según D5/D6, no un bug. Sobre `pv-internal-doc-features`:
completar `pv-how` → `pv-do` end-to-end sobre esa misma entry y confirmar que, al documentar la
feature, la skill busca/menciona `navigation_*.md` (nombre nuevo) y no `design_navigation_*.md`.

### Paso 4 — `extend-entry.md`: migración incidental de entries legacy (D4, D6)

Editar `pv-new/extend-entry.md`:
- Paso 1: comprobar el mockup bajo `mockups/`; si hay archivos legacy sueltos en la raíz y
  `mockups/` no existe, crearla y moverlos dentro antes de continuar (D4). Comprobar
  `navigation_*.md`/`data_*.md` (nombre nuevo) sueltos en la raíz; si en su lugar hay
  `design_navigation_*.md`/`design_data_*.md` (nombre viejo), renombrarlos antes de continuar (D6).
- Pasos 4, 5, 6, 8: carpeta de destino `mockups/` para el mockup, nombre `navigation_*.md`/
  `data_*.md` para navegación/datos en la raíz; rutas mostradas al usuario coherentes con ambos.

**Verificación**: cuatro casos (dos de D4, dos de D6, pueden combinarse en las mismas entries de
prueba).
1. Sobre la entry del paso 2 (ya en `mockups/`, ya con nombre nuevo): extenderla con un ajuste
   visual nuevo; confirmar que el paso 1 detecta los archivos existentes bajo `mockups/` y
   `navigation_*.md`/`data_*.md` en la raíz (sin falso "nada existe aún").
2. Sobre una entry legacy de mockup (crear una de prueba con `design_*.html` suelto en la raíz y
   sin `mockups/`, simulando el estado pre-D1): extenderla; confirmar que el paso 1 migra el
   archivo a `mockups/` antes de aplicar el resto de la extensión, y que no queda suelto en la raíz
   al terminar.
3. Sobre una entry legacy de nombre (crear una de prueba con `design_navigation_*.md` o
   `design_data_*.md` sueltos en la raíz, simulando el estado pre-D6): extenderla; confirmar que el
   paso 1 los renombra a `navigation_*.md`/`data_*.md` antes de aplicar el resto de la extensión, y
   que no queda ningún archivo con el nombre viejo al terminar.

### Paso 5 — `pv-todo`: D2 (eliminar creación), D3 (copia D.4 consciente de subcarpetas), D6 (nombre nuevo en el listado/copia)

Editar `pv-todo/SKILL.md`:
- Paso 3 (L71): eliminar el párrafo que permite crear `design_*.html` al anotar una idea nueva.
- Paso D.2 (L93): enumerar el contenido de `mockups/` y los `navigation_*.md`/`data_*.md` (nombre
  nuevo) sueltos en la raíz, en el listado de confirmación.
- Paso D.4 (L101-108): copiar `mockups/` como subárbol completo (no archivo por archivo) hacia
  `{changesDir}/todo/{code}/mockups/`; añadir `mockups/important.md` con el texto fijo de
  advertencia (mockups históricos, fecha de conversión, solo referencia). Copiar
  `navigation_*.md`/`data_*.md` sueltos igual que el resto de archivos sueltos que ya copiaba, sin
  `important.md` (no son mockups congelados, ver nota en "Enfoque" punto 3).

Editar `pv-new/todo-mode.md` en sus tres puntos reales (pasos 2, 4 y 5, no solo L6): cada mención de
`design_*.html` pasa a hablar del contenido de la carpeta `mockups/` de la idea, tratándola como
carpeta opaca — leerla (paso 2), tenerla en cuenta al construir la propuesta visual (paso 4) y
borrarla junto a `description.md` al completar la promoción (paso 5).

**Verificación**: sobre la entry con mockups del paso 2, degradarla a idea `todo/` (`/pv-todo
change <xxxx>`); confirmar que el listado de confirmación menciona `mockups/`, que la subcarpeta
se copia completa (no se aplana) a `todo/{code}/mockups/`, y que aparece `mockups/important.md`
con la fecha de hoy. Por separado, intentar anotar una idea nueva con un componente visual y
confirmar que `pv-todo` ya no ofrece ni crea ningún `design_*.html` — solo el texto en
`description.md`.

### Paso 6 — `pv-status`: separar `extra_files` de `mockups_count`

Editar `pv-status/scripts/filter_status.py`:
1. Excluir `"mockups"` del recuento de `count_extra_files` (sigue siendo `iterdir()` +
   `is_file()`, no recursivo — solo se añade la exclusión explícita del nombre).
2. Añadir `count_mockups_files(entry_dir)`: cuenta los archivos dentro de `entry_dir / "mockups"`
   si existe, `None` si no.
3. En `build_entry()` (L204-259), calcular y devolver `mockups_count`.
4. En `render_terminal()` (~L448-484), añadir la línea `mockups: {mockups_count}` tras `extra
   files: {extra_files}`, solo cuando `mockups_count` no es `None` (mismo patrón condicional que
   la línea `Related:`).
5. Actualizar el docstring (~L30-36) y el comentario de `TERMINAL_FRAMEWORK_FILES` (L147-151).

**Verificación**: correr `pv.py`/`pv-status` en modo `--terminal` sobre la entry con mockups del
paso 2; confirmar que aparece una línea `mockups: N` con el conteo real de archivos dentro de
`mockups/`, y que `extra files: 0` ya no incluye esos archivos en su número. Sobre una entry sin
mockups, confirmar que la línea `mockups:` no aparece en absoluto.

### Paso 7 — `pv-update`: migración activa de entries legacy (D5, D6)

Este paso va último a propósito: solo tiene sentido una vez el resto del framework ya conoce y
depende de `mockups/` y del nombre nuevo (pasos 1-6), porque es la red de seguridad para todo lo
que quedó legacy antes de esta migración. Recorre `inProgress/` **e `implemented/`** — no
`closed/`, historia congelada (mismo criterio ya fijado en Reviews, pasada 4, para D5; se aplica
igual a D6).

En `pv-update/scripts/audit-context.py`, seguir el mismo patrón que `check_risk_in_plan_headers`
(función dedicada, recorre `inProgress/` e `implemented/`, usa el helper `add(problems, id,
severity, field, message, expected=, actual=)`):

```python
def check_legacy_loose_mockups(root: Path, work_folder: str, problems: list) -> None:
    """Detects design_*.html / design_*.txt files sitting loose in an
    inProgress/{xxxx}/ or implemented/{xxxx}/ entry's own root, predating the
    mockups/ subfolder convention. Fires only when the entry has no mockups/
    subfolder yet -- once mockups/ exists (however it got there), the entry
    is considered migrated regardless of what's still loose in its root.
    Fixed by pv-update: create mockups/ and move every matching loose file
    into it. closed/ is intentionally excluded -- frozen history."""
    wf_path = resolve_under(root, work_folder)
    changes_dir = wf_path / "changes"
    patterns = ("design_*.html", "design_*.txt")
    for state in ("inProgress", "implemented"):
        entries_dir = changes_dir / state
        if not entries_dir.is_dir():
            continue
        for entry_dir in sorted(p for p in entries_dir.iterdir() if p.is_dir()):
            if (entry_dir / "mockups").exists():
                continue
            loose = sorted(
                f.name for pat in patterns for f in entry_dir.glob(pat)
            )
            if not loose:
                continue
            rel = entry_dir.relative_to(root).as_posix()
            add(problems, f"legacy-loose-mockups:{entry_dir.name}", "optional", rel,
                f"'{rel}' has mockup file(s) loose in its own root "
                f"({', '.join(loose)}) predating the mockups/ subfolder "
                f"convention. Migrate: create '{rel}/mockups/' and move "
                f"every one of those files into it.",
                expected="mockup files under mockups/",
                actual=f"loose in entry root: {', '.join(loose)}")


def check_legacy_design_prefix(root: Path, work_folder: str, problems: list) -> None:
    """Detects design_navigation_*.md / design_data_*.md files still
    carrying the retired design_ prefix, in inProgress/{xxxx}/ or
    implemented/{xxxx}/ (closed/ excluded -- frozen history). These aren't
    mockups and never move to mockups/ -- only their name changes. Fixed by
    pv-update: rename each to navigation_*.md / data_*.md in place."""
    wf_path = resolve_under(root, work_folder)
    changes_dir = wf_path / "changes"
    patterns = ("design_navigation_*.md", "design_data_*.md")
    for state in ("inProgress", "implemented"):
        entries_dir = changes_dir / state
        if not entries_dir.is_dir():
            continue
        for entry_dir in sorted(p for p in entries_dir.iterdir() if p.is_dir()):
            stale = sorted(
                f.name for pat in patterns for f in entry_dir.glob(pat)
            )
            if not stale:
                continue
            rel = entry_dir.relative_to(root).as_posix()
            add(problems, f"legacy-design-prefix:{entry_dir.name}", "optional", rel,
                f"'{rel}' has file(s) with the retired 'design_' prefix "
                f"({', '.join(stale)}). Migrate: rename each to drop the "
                f"'design_navigation_'/'design_data_' prefix in favor of "
                f"'navigation_'/'data_', in place.",
                expected="navigation_*.md / data_*.md (no design_ prefix)",
                actual=f"stale name in entry root: {', '.join(stale)}")
```

Registrar las llamadas a `check_legacy_loose_mockups(root, work_folder, problems)` y
`check_legacy_design_prefix(root, work_folder, problems)` junto al resto de checks que recorren
`changes/` (cerca de `check_risk_in_plan_headers`/`check_metadata_files`).

En `pv-update/SKILL.md`:
- Añadir `legacy-loose-mockups:*` y `legacy-design-prefix:*` a la lista de problemas cubiertos por
  el paso 2 (junto a `risk-in-plan-header:*`, con una línea de descripción igual de concisa cada
  uno).
- Añadir los dos fixes deterministas al paso 3: "crear `mockups/` y mover dentro cada archivo
  listado en `actual`, preservando su nombre" (D5); "renombrar cada archivo listado en `actual`
  quitando el prefijo `design_`, sin moverlo de sitio" (D6).
- Añadir "mockups" y "design-prefix" como dos áreas nuevas del informe del paso 4, listando cada
  `<xxxx>` migrada en cada una.

**Verificación**: dos casos independientes.
1. Crear una entry de prueba con `design_*.html` suelto en la raíz y sin `mockups/`; correr
   `pv-update`; confirmar que detecta `legacy-loose-mockups:<xxxx>`, mueve el archivo a `mockups/`
   sin pedir confirmación, y lo reporta en el paso 4 bajo el área "mockups". Confirmar que, sobre
   esa misma entry, `pv-how` no encontraba el mockup **antes** de correr `pv-update` (paso 3) y sí
   lo encuentra **después**. Repetir sobre una entry de prueba en `implemented/`, confirmando que
   el barrido también la alcanza.
2. Crear una entry de prueba con `design_navigation_*.md`/`design_data_*.md` sueltos en la raíz
   (nombre viejo); correr `pv-update`; confirmar que detecta `legacy-design-prefix:<xxxx>`,
   renombra los archivos sin pedir confirmación (sin moverlos), y lo reporta en el paso 4 bajo el
   área "design-prefix". Confirmar que `pv-how` no encontraba esos archivos con el nombre viejo
   **antes** de correr `pv-update` y sí los encuentra con el nombre nuevo **después**.

### Paso 8 — Pase de consistencia final

Antes de dar el plan por implementado:
1. Grep de `design_*.html`, `design_*.txt` en todo `.claude/skills/**` para confirmar que ninguna
   mención restante asume la raíz de la entry como ubicación del mockup (los archivos de
   "referencia, sin cambio esperado" deben seguir siendo solo prosa que no fija una ruta). Grep por
   separado de `design_navigation_` y `design_data_` (nombre viejo, con prefijo) para confirmar que
   no queda ninguna mención activa del nombre retirado — solo puede aparecer, si acaso, en el
   propio catálogo de `pv-update` (los patrones que detecta) o en este plan.
2. Ejecutar la lista completa de "Verificación" de cada paso anterior una vez más, de corrido,
   sobre un único cambio/fix desechable de principio a fin: `pv-new` → extender → `pv-how` →
   `pv-status` → degradar a `todo` → `pv-update` sobre dos entries legacy aparte (una de mockup
   suelto para D5, una de nombre viejo para D6). Esto cubre el camino feliz completo más ambos
   caminos legacy en una sola pasada.
3. Confirmar que no queda ningún archivo modificado que no esté en la lista de "Archivos críticos"
   de este plan (`git status` contra esa lista).

## Reviews

### 2026-09-22 (pasadas 1-3, previas a la formalización de esta sección)

Tres pasadas de análisis crítico verificaron este plan contra el repo real antes de escribir la
versión final de arriba:

1. **Verificación de citas** — cada número de línea y fragmento textual citado en la primera
   versión del plan se comprobó abriendo los archivos reales. Resultado: casi exhaustivo, solo
   tres correcciones menores (dos archivos ausentes de la lista — `pv-init/SKILL.md`,
   `pv-new/hooks/20-after-entry.template.md`, ambos prosa-only — y una cita de línea incorrecta en
   `pv-internal-doc-features/SKILL.md`, L66 → L26). Ya incorporadas arriba.
2. **Lógica y huecos** — pasada distinta, buscando bugs, inconsistencias entre secciones,
   huecos implícitos y casos límite (no citas). Encontró seis problemas reales: la copia D.4 de
   `pv-todo` no reconocía subcarpetas; el paso de creación de mockups en `pv-todo` (L71) no estaba
   cubierto; la ruta `todo/{code}/mockups/` nunca se deletreaba explícita; el fallback legacy de
   `pv-how` (decidido en un borrador anterior) nunca se tradujo en instrucción concreta;
   `extend-entry.md` podía partir los mockups de una entry legacy entre dos ubicaciones; y la
   acción `edit` de las skills de mockup podía producir un duplicado silencioso como consecuencia
   de lo anterior. Las decisiones D2-D5 de este documento son la resolución de esos seis hallazgos
   — en el proceso, la decisión original de "tolerar mockups legacy en la raíz como fallback" se
   descartó por completo en favor de D5 (migración activa vía `pv-update`), y la capacidad de
   `pv-todo` de crear mockups se eliminó en vez de migrarse (D2), simplificando el resto.
3. **Consistencia del documento** — el plan se reestructuró para incorporar todas las decisiones
   directamente en las secciones correspondientes, en vez de arrastrar el historial cronológico de
   "esto se dijo aquí, se corrigió allá" en tablas de hallazgos separadas.

Sin hallazgos vivos de estas tres pasadas: todo lo detectado quedó resuelto e incorporado al cuerpo
del plan (decisiones D1-D5 y las secciones de "Enfoque"/"Plan de implementación").

### 2026-09-22 (pasada 4)

Verificación independiente contra el repo real (no contra lo que el plan afirma): se releyeron
`filter_status.py`, `collect_status.py`, `pv-how/SKILL.md` + `workflow.how.md`, `pv-new/SKILL.md` +
`extend-entry.md` + `todo-mode.md` + `workflow.new.md`, `pv-fix/SKILL.md` + `workflow.fix.md`,
`pv-todo/SKILL.md`, `pv-update/SKILL.md` + `audit-context.py`, `pv-internal-mockups-html/SKILL.md`,
`pv-internal-mockups-ascii/SKILL.md`, y cada archivo listado como "prosa-only" (`pv-do/SKILL.md`,
`pv-internal-doc-features/SKILL.md`, `pv-internal-doc-style/SKILL.md`, `pv-init/SKILL.md`,
`pv-init/schema.json`, `pv-internal-tech-mermaid/SKILL.md`, `pv-new/hooks/20-after-entry.template.md`).
Todas las citas de línea y las clasificaciones prosa-vs-lógica del plan se confirmaron exactas
contra el estado actual de esos archivos. También se inspeccionó el estado real de
`{workFolder}/changes/` (`sandbox-test1/previo-sdd/changes/`, el `workFolder` configurado en
`.claude/pv-context.json`), que contiene datos legacy reales, no hipotéticos.

(Un candidato a hallazgo — que el paso 8 debería reutilizar entries legacy ya existentes en
`sandbox-test1/` en vez de crear una nueva de prueba — se descartó tras discutirlo: `sandbox-test1/`
es terreno de pruebas libre, no trabajo en curso real, y el usuario prefiere crear entries nuevas
para cada verificación. El paso 8 ya lo hace así; no había problema que corregir.)

| Finding | Explanation | Proposed improvement |
|---|---|---|
| El barrido de migración de `pv-update` (paso 7, D5) solo cubre `inProgress/`, dejando `implemented/` con mockups legacy huérfanos para siempre | `check_legacy_loose_mockups` recorría explícitamente solo `changes_dir / "inProgress"`. El repo real (workFolder actual: `sandbox-test1/previo-sdd/`) ya tiene mockups sueltos en la raíz, sin `mockups/`, en `changes/implemented/00210/`. `closed/` queda fuera a propósito (historia congelada), pero `implemented/` sí debía migrarse igual que `inProgress/`. | Resuelto: Paso 7 reescrito, `check_legacy_loose_mockups` (y su hermano `check_legacy_design_prefix`, añadido en la pasada 6 por D6) recorren ahora `inProgress/` e `implemented/`. `closed/` sigue excluido. |

### 2026-09-22 (pasada 5)

Verificación independiente contra el repo real, complementaria a la pasada anterior: se releyeron de
nuevo `pv-todo/SKILL.md` completo, `pv-new/todo-mode.md` completo, `pv-how/SKILL.md` (paso 3 punto
3, no solo punto 2), `pv-init/workflow.init.md`, y se hizo un grep exhaustivo de `design_*`/`mockups`
en todo `.claude/skills/**` para confirmar que la lista de "Archivos críticos" y "reference, sin
cambio esperado" del plan no deja ningún archivo real fuera.

**Structure**

| Finding | Explanation | Proposed improvement |
|---|---|---|
| Faltaba la sección "Índice" exigida | El documento no tenía ninguna tabla de contenidos enlazando a sus propios encabezados. | Resuelto: sección `## Índice` generada tras el título, con un enlace por cada encabezado del documento (incluida esta sección `Reviews`). |
| "Plan de implementación" no era la última sección | Tras `## Plan de implementación` el documento seguía con `## Historial de revisión` y los `## Análisis crítico`. Regla de la skill actualizada entre tanto: ahora exige una sección `Reviews` al final (histórico por fecha, hallazgos vivos únicamente, resueltos se retiran) — no que "Plan de implementación" sea la última sección a secas. | Resuelto: "Historial de revisión" + los "Análisis crítico" fusionados en esta sección `## Reviews`, una entrada por fecha, como última sección del documento. |
| El heading "Objetivo" no coincide con el texto exigido "Objetivo del plan" | La sección se llamaba solo `## Objetivo`; la convención del skill pide `## Objetivo del plan` (o "Goal"/"Plan objective" en inglés) como texto exacto, no una paráfrasis. El contenido cumple la intención, pero el heading literal no coincidía. | Resuelto: renombrado a `## Objetivo del plan` (sin cambio de contenido). |

**Enfoque / Plan de implementación**

| Finding | Explanation | Proposed improvement |
|---|---|---|
| `pv-new/todo-mode.md` tiene tres puntos de lectura de `design_*.html`, no uno solo, y el plan solo revisa L6 | El plan (sección "Puntos de escritura", punto de `todo-mode.md`, y Paso 5 de "Plan de implementación") decía textualmente que `todo-mode.md` "sigue leyendo `design_*.html` desde `mockups/` de la idea... sin cambio adicional respecto al plan original" y limitaba cualquier ajuste a "si al escribir el punto anterior se detecta que el texto de L6 necesita ajuste de redacción". Pero el archivo real tiene tres menciones activas, no una: paso 2, paso 4 y paso 5. Tras D2/D3, una idea en `todo/` solo puede tener mockups bajo `mockups/` (llegados por democión D.4) — las tres menciones leen/usan/borran esa carpeta como contenido opaco, sin asumir el nombre `design_*.html`. | Resuelto: "Enfoque" punto 2 y "Plan de implementación" Paso 5 reescritos para cubrir los tres puntos (pasos 2, 4, 5 de `todo-mode.md`), cada uno hablando del contenido/carpeta `mockups/` en vez de `design_*.html`. `todo-mode.md` añadido explícitamente a "Archivos críticos". |
| `pv-how/SKILL.md` tiene una tercera mención de `design_data_*.md` (paso 3, punto 3) que el plan no cita en sus "Puntos de lectura/descubrimiento" | El plan solo mencionaba "paso 1.1" y "paso 3, punto 2" de `pv-how/SKILL.md` como puntos de lectura a migrar a `mockups/`. El archivo real tiene un tercer punto con la misma lógica de ruta implícita: paso 3, punto 3 (L125), que trata `design_data_*.md` como fuente de verdad para el diseño técnico de datos. Sin cubrirlo, tras la migración `pv-how` dejaría de encontrar los datos funcionales. | Resuelto: "Enfoque" punto 3, "Plan de implementación" Paso 3 y "Archivos críticos" actualizados para incluir el paso 3 punto 3 de `pv-how/SKILL.md`. |
| `pv-init/workflow.init.md` no está en la lista de "prosa-only, sin cambio esperado" | El grep de `design_*`/`mockups` en todo `.claude/skills/**` encontró una mención no listada en ningún sitio del plan: `pv-init/workflow.init.md` L49, etiqueta de nodo Mermaid sobre el nombre de la clave de configuración `framework.skills.mockups`, sin lógica de ruta. Inofensivo, pero al no estar citado el grep final del Paso 8 no podía distinguir "revisado y es prosa" de "olvidado". | Resuelto: añadido a la lista de "Archivos críticos" (referencia, sin cambio esperado). |

#### Detalle de implementación

- [x] `.claude/plans/mockups-subfolder/PLAN.md` — Índice, heading "Objetivo del plan", sección
  `Reviews` consolidada (este documento, ya aplicado).
- [ ] `.claude/skills/pv-new/todo-mode.md` — pasos 2, 4, 5 (contenido de `mockups/`, no
  `design_*.html`).
- [ ] `.claude/skills/pv-how/SKILL.md` — paso 3, punto 3 (además de paso 1.1 y paso 3 punto 2 ya
  cubiertos).
- [ ] `.claude/skills/pv-init/workflow.init.md` — sin cambio de comportamiento, solo confirmar en
  el grep final del Paso 8 que sigue siendo prosa-only.

### 2026-09-22 (pasada 6)

A petición del usuario: `design_data_*.md` (y por la misma razón, `design_navigation_*.md`) no son
mockups y no los gestiona `framework.skills.mockups` — nunca debieron moverse a `mockups/`. El plan
se revisó para excluirlos del movimiento a subcarpeta (corrigiendo una decisión de D1 que sí los
incluía) y, además, se añadió D6: pierden el prefijo `design_` (→ `navigation_*.md`/`data_*.md`),
quedándose sueltos en la raíz de la entry, sin cambiar de ubicación. El usuario confirmó que el
rename va en este mismo plan (mismos archivos ya en juego) y que las entries legacy con el nombre
viejo se migran vía `pv-update`, mismo mecanismo que D5.

Verificado contra el repo: las skills `pv-internal-mockups-html`/`pv-internal-mockups-ascii` nunca
mencionan `design_data_*.md`/`design_navigation_*.md` — confirma que no son su responsabilidad.
Hay entries legacy reales con `design_navigation_*.md` en `sandbox-test1/` (`inProgress/00196/`,
`implemented/00210/`, y `closed/00212/`+`closed/00214/` — estas dos últimas fuera del barrido de
`pv-update`, historia congelada, igual que el resto del plan trata `closed/`).

| Finding | Explanation | Proposed improvement |
|---|---|---|
| D1 (versión previa) movía `design_navigation_*.md`/`design_data_*.md` a `mockups/` sin que la skill de mockups los gestione | El "Objetivo del plan" y D1 originales trataban los cuatro tipos de archivo (`design_*.html`, `design_*.txt`, `design_navigation_*.md`, `design_data_*.md`) como "mockups" a mover a `mockups/`. Verificado contra `pv-internal-mockups-html/SKILL.md`/`pv-internal-mockups-ascii/SKILL.md`: ninguna menciona `design_navigation_*`/`design_data_*` — los escriben directamente `pv-new`/`pv-fix`/`extend-entry.md`, no son mockups visuales. | Resuelto: "Objetivo del plan", "Fuera de alcance", D1 (implícitamente, vía D6) y todas las secciones de "Enfoque"/"Plan de implementación"/"Archivos críticos" corregidas — `design_navigation_*.md`/`design_data_*.md` ya no se mueven a `mockups/`, se quedan sueltos en la raíz. |
| Prefijo `design_` engañoso en archivos que no son mockups | Aun quedándose fuera de `mockups/`, `design_navigation_*.md`/`design_data_*.md` seguían llamándose como si fueran mockups, lo que induce a error (¿por qué un archivo "design_" no vive en `mockups/`?). | Resuelto: D6 añadida — renombrados a `navigation_*.md`/`data_*.md`, sin prefijo `design_`, sin cambio de ubicación. Migración legacy vía `pv-update` (`legacy-design-prefix:<xxxx>`, mismo mecanismo que D5). Todas las secciones del plan actualizadas para reflejar el nombre nuevo en los puntos de escritura (`pv-new`/`pv-fix`/`extend-entry.md`), lectura (`pv-how`/`pv-todo`), y migración (`pv-update`). |

#### Detalle de implementación (pasada 6)

- [x] `.claude/plans/mockups-subfolder/PLAN.md` — exclusión de `design_navigation_*.md`/
  `design_data_*.md` de `mockups/`, D6 (rename), pseudocódigo `check_legacy_design_prefix`, todas
  las secciones actualizadas (este documento, ya aplicado).
- [ ] `.claude/skills/pv-new/SKILL.md` — pasos 3 (`design_navigation_*.md` → `navigation_*.md`),
  3.1 (`design_data_*.md` → `data_*.md`), 4 (mensaje de validación).
- [ ] `.claude/skills/pv-fix/SKILL.md` — pasos 4.1 (`design_data_*.md` → `data_*.md`), 5 (mensaje
  de validación).
- [ ] `.claude/skills/pv-new/extend-entry.md` — paso 1 (comprobación + migración legacy D6),
  pasos 4/5/6/8 (nombre nuevo).
- [ ] `.claude/skills/pv-how/SKILL.md` — paso 1.1 (dos ubicaciones), paso 3 punto 3 (`data_*.md` en
  la raíz, no `mockups/`).
- [ ] `.claude/skills/pv-todo/SKILL.md` — paso D.2 (listado con nombre nuevo), paso D.4 (copia sin
  `important.md` para `navigation_*.md`/`data_*.md`).
- [ ] `.claude/skills/pv-update/scripts/audit-context.py` — nueva función `check_legacy_design_prefix`
  (hermana de `check_legacy_loose_mockups`, que a su vez se corrige para no incluir
  `design_navigation_*`/`design_data_*` en sus patrones).
- [ ] `.claude/skills/pv-update/SKILL.md` — nueva área "design-prefix" en el informe, nuevo fix
  determinista en el paso 3.

### 2026-09-22 (pasada 7)

Verificación independiente contra el repo real (no contra las citas del propio plan), incluyendo
una segunda pasada de un subagente que releyó cada archivo citado desde cero, sin partir de los
números de línea del plan. Confirmado exacto contra el repo: `filter_status.py`
(`count_extra_files`, `TERMINAL_FRAMEWORK_FILES`, `build_entry`, `render_terminal` y su patrón
condicional `Related:`), `pv-how/SKILL.md` (paso 1.1, paso 3 puntos 2 y 3) + `workflow.how.md`
(`S11Validate`), `pv-new/extend-entry.md` paso 1, `pv-new/todo-mode.md` (los tres puntos: pasos 2,
4, 5), `pv-todo/SKILL.md` (paso 3/L71, D.2/L93, D.4/L101-108), `pv-internal-mockups-html`/
`-ascii` ("Expected input from the caller"), `pv-update/scripts/audit-context.py`
(`check_risk_in_plan_headers` como patrón a espejar, `add()`, `resolve_under()` — sin colisión de
nombre con las dos funciones nuevas propuestas), `pv-update/SKILL.md` (pasos 2/3/4), `pv-new/
SKILL.md` y `pv-fix/SKILL.md` (destino de carpeta actual = raíz de la entry, confirmando que el
cambio a `mockups/` es real). También confirmadas contra `sandbox-test1/previo-sdd/changes/` las
cuatro entries legacy citadas (`inProgress/00196`, `implemented/00210`, `closed/00212`,
`closed/00214`) con sus ficheros exactos, y las "cuatro excepciones" de `pv-update/SKILL.md`
(`context-invalid-json`, `version-check-downgrade`, `namespace-anchor-broken:*`,
`stuff-pipeline-legacy-location`) — confirmando que D5 razona correctamente que una migración
determinista de mockups sueltos no encaja en ninguna de ellas.

| Finding | Explanation | Proposed improvement |
|---|---|---|
| `pv-internal-doc-features/SKILL.md` tiene dos menciones activas y vigentes de `design_navigation_*.md` (L26 y L66), ninguna de las dos en "Archivos críticos" ni correctamente resuelta como prosa-only | El archivo está clasificado en la sección "Archivos donde cada mención es solo prosa/ruta" (L132) citando solo L26, y el Reviews de la pasada 1 (L630) dice explícitamente que una cita inicial de L66 se "corrigió" a L26 — tratándola como un error de número de línea, no como una segunda mención real. Verificado contra el archivo actual: **ambas líneas existen y ambas son menciones reales y distintas** — L26 (`## Content checklist`): "...o la carpeta de la entry tiene uno o más `design_navigation_*.md`, y representa un flujo..."; L66 (parámetro `context` de la acción `upsert`): "...o la carpeta de la entry tiene ficheros `design_navigation_*.md`)...". La pasada 1 nunca debió "corregir" L66 a L26 — son dos citas independientes, ambas vigentes hoy. Más grave: a diferencia de `pv-internal-doc-style/SKILL.md` (L26/L61, que citan `design_*.html`/`.txt` como *mockups a los que apuntar*, sin fijar su nombre — ver Enfoque punto 1, esos siguen llamándose `design_*.html` tras este plan, solo cambian de carpeta), estas dos líneas de `pv-internal-doc-features/SKILL.md` **fijan el patrón de nombre `design_navigation_*.md` de forma literal**, el mismo patrón que D6 retira por completo (renombrado a `navigation_*.md`). Tras D6, sin editar este archivo, `pv-internal-doc-features` seguiría buscando/mencionando un patrón de fichero que ya no existirá en ninguna entry nueva — quedaría desalineado del resto del framework, con el mismo tipo de riesgo funcional (aunque menor, al ser solo texto descriptivo hacia el LLM que ejecuta la skill, no lógica de glob determinista en código) que D6 ya reconoce para `pv-how`/`pv-todo`/`pv-new`/`extend-entry.md`. Esta clasificación fue hecha en la pasada 1 (antes de que D6 existiera, añadida recién en la pasada 6) y nunca se revisó contra el impacto de D6 en pasadas posteriores — un hueco de cobertura, no un error de cita menor. | **Resuelto:** `pv-internal-doc-features/SKILL.md` sacado del grupo "prosa-only" (L133-136) y movido a "Archivos críticos" (nuevo bullet, junto a `pv-how/workflow.how.md`). Añadido como punto nuevo en "Enfoque" sección 3 ("Puntos de lectura/descubrimiento") y en el Paso 3 de "Plan de implementación" (renombrado "Paso 3 — Puntos de lectura/descubrimiento (pv-how, pv-internal-doc-features)"), junto a su verificación end-to-end (`pv-how` → `pv-do`). Ambas líneas (L26, L66) pasan de `design_navigation_*.md` a `navigation_*.md`, sin cambio de ubicación. |
