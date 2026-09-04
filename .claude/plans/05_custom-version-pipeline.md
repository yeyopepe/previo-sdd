# `custom-version-pipeline.md`: 3 puntos de extensión en el flujo de `pv-version`

## Context

`pv-version` orquesta la preparación de una release con una secuencia **fija** (ver
`workflow.version.md`): guardrail de `implemented/` → resolver `XXXX` → crear
`versions/XXXX/` → compilar el entregable → copiar docs → `pv-internal-changelog` →
resumen.

El único punto donde hoy el proyecto puede inyectar algo propio es el paso 4
(`{workFolder}/stuff/how-to-compile-version.md`), y solo cubre **cómo compilar el
entregable** (comandos + artefactos a `files/`). No hay forma de que el usuario añada
pasos al *flujo* de la release: "validar que el working tree está limpio antes de
empezar", "firmar/empaquetar el entregable recién compilado", "al final, subir el zip a
un bucket o generar release notes en PDF".

Objetivo: **mínimo cambio** — un fichero nuevo `{workFolder}/stuff/custom-version-pipeline.md`
que `pv-version` lee (si existe) y cuyos pasos ejecuta en **3 puntos de anclaje** bien
definidos del flujo. Sin tocar la secuencia troncal de `workflow.version.md`, sin
scripts nuevos, sin schema nuevo en `pv-context.json`.

## Piezas que ya existen (contexto)

- `{workFolder}/stuff/` es una subcarpeta fija que crea `pv-init`'s
  `scaffold-project.py` (con `.gitkeep`). Descrita en `schema.json` como *"holds
  pv-version's own project-specific files, starting with how-to-compile-version.md"* —
  el sitio natural para un segundo fichero de este tipo.
- `pv-version/SKILL.md` ya trata `stuff/*` como texto en `interaction.language` (no hay
  campo de idioma dedicado para `stuff/`). Aquí es `es`.
- `how-to-compile-version.template.md` ya soporta procesos multi-paso / multi-artefacto:
  el patrón `## Command(s) to run` / `## Generated file(s)` / `## Notes`, y su variante
  "Step N: {name}" cuando hay varios pasos independientes. El nuevo fichero **reutiliza
  ese mismo vocabulario** para no introducir un tercer dialecto.
- El flujo troncal está en dos diagramas: `workflow.version.md` (ejecución, source of
  truth) y `version-flow-diagram.template.md` (cara al usuario). Ambos se tocan (ver §3
  y §4), pero de forma ligera.

## Alcance: 3 hooks, no 5

La idea es marcar **un par de puntos clave** del flujo y poder customizarlos: uno antes
de empezar, uno por el medio con sentido, y uno al final del todo.

| Hook | Punto exacto en el flujo | Ve `{XXXX}` | Uso típico |
|---|---|---|---|
| **Antes de empezar** | tras el guardrail de `implemented/` (0.5), **antes** de resolver `XXXX` (1) y de crear `versions/XXXX/` (2) | **No** | precondiciones: working tree limpio, rama correcta, "¿de verdad quiero versionar ahora?" |
| **Por el medio** | dentro del paso 4, **tras** `copy-build-artifacts.py` (artefactos ya en `files/`), **antes** de `copy-docs.py` (5) | Sí | firmar/empaquetar el entregable, checksums, material derivado del build |
| **Al final** | tras `pv-internal-changelog` (6), **antes** del resumen (7) | Sí | publicar/subir `versions/{XXXX}/`, generar release notes PDF a partir de `changelog.md` |

Decisiones que esto fija (antes eran preguntas abiertas):

1. **Un "bump de versión antes de compilar" no necesita hook.** Si el build requiere un
   paso previo (bump en `package.json`, generar un asset), va como un "Step 1" dentro de
   `how-to-compile-version.md` y el build real pasa a ser "Step 2". Por eso no hay hook
   `before-compile`.
2. **No hay hook entre docs y changelog** (`after-docs`): no tiene un caso de uso que no
   encaje igual de bien en "Al final".
3. **"Antes de empezar" se ejecuta antes de resolver `XXXX`**, así que sus pasos **no
   pueden referenciar `{XXXX}`**. Su trabajo (working tree, rama) no lo necesita. Los
   otros dos hooks van después y sí tienen `{XXXX}` y las rutas de `versions/{XXXX}/`.
4. **"Al final" va antes del resumen** (no después), para que el paso 7 pueda mencionar
   lo que produjo el hook ("subido a X", "release notes en `notes.pdf`").
5. **Fichero ausente = comportamiento actual, sin cambios.** No se crea por defecto en
   `scaffold-project.py` (igual que `how-to-compile-version.md` tampoco se crea hasta la
   primera `pv-version`). Se documenta cómo crearlo, con plantilla.
6. **`pv-version` no lo autogenera ni avisa.** 100% opt-in manual: si no existe,
   `pv-version` no pregunta ni menciona nada. Silencio total (un aviso "una sola vez"
   necesitaría estado persistente, y eso contradice "sin schema nuevo").
7. **Qué es un "paso".** Prosa + bloque de comando(s) desde la raíz del repo, con nota
   de qué produce / cómo verificar. `pv-version` los ejecuta en orden; **si uno falla,
   para y lo explica** (mismo criterio que el paso 4 actual), sin inventar alternativa.
8. **Variables sustituibles.** `{workFolder}` siempre; `{XXXX}`,
   `{workFolder}/versions/{XXXX}/`, `.../files/`, `.../docs/` solo en "Por el medio" y
   "Al final". Nada más: si un paso necesita la rama actual, que ejecute
   `git rev-parse --abbrev-ref HEAD` en su propio bloque de comando.
9. **Sección sin pasos = se omite sin ruido.** Un fichero puede definir 0..N pasos por
   sección.

## Estructura del fichero: 3 secciones fijas

Headings `##`, una por hook, en el orden del flujo. Dentro de cada una, 0..N
`### Step N: {name}` con los mismos tres campos que `how-to-compile-version.md`.

```markdown
# Custom steps for this project's release pipeline

`pv-version`'s own file (not part of `.claude/pv-context.json`): optional
project-specific steps that `pv-version` runs at three fixed points of the
release flow. If this file doesn't exist, `pv-version` behaves exactly as
without it. A section with no steps is skipped silently. If any step fails,
`pv-version` stops and explains — it doesn't improvise an alternative.

Substitutable variables: `{workFolder}` everywhere; `{XXXX}`,
`{workFolder}/versions/{XXXX}/`, `.../files/`, `.../docs/` only in "In the
middle" and "At the end". "Before starting" runs before `XXXX` is resolved,
so `{XXXX}` is not available there.

## Before starting

Runs after the `implemented/` guardrail passes, before resolving `XXXX` and
creating `versions/XXXX/`. Typical use: precondition checks (clean working
tree, correct branch).

### Step 1: {name}

**Command(s) to run**
[commands from the repo root]

**Generated file(s)**
[what it produces, or "none — check only"]

**Notes**
[optional]

## In the middle

Runs after the deliverable's artifacts are copied to
`{workFolder}/versions/{XXXX}/files/`, before the technical docs are zipped.
Typical use: sign/package the deliverable, checksums.

### Step 1: {name}
...

## At the end

Runs after the changelog is drafted, before the final summary. Typical use:
publish/upload `{workFolder}/versions/{XXXX}/`, generate derived release
material.

### Step 1: {name}
...
```

Nombres de sección traducidos a `interaction.language` (aquí `es`: "Antes de empezar" /
"Por el medio" / "Al final"), igual que el resto de `stuff/`.

## Cambios propuestos (mínimos)

### 1. Nueva plantilla `.claude/skills/pv-version/custom-version-pipeline.template.md`

El esqueleto de §"Estructura del fichero", en el mismo tono que
`how-to-compile-version.template.md`:
- Cabecera: qué es (fichero propio del proyecto, no de `pv-context.json`; opcional;
  leído y ejecutado por `pv-version` si existe; ausente = sin cambios).
- Las 3 secciones (`## Before starting`, `## In the middle`, `## At the end`), cada una
  con su párrafo de "cuándo corre / uso típico" y 0..N `### Step N: {name}` con
  `**Command(s) to run**` / `**Generated file(s)**` / `**Notes**`.
- Lista de variables sustituibles y la restricción de `{XXXX}` en "Before starting".
- Nota de que una sección sin pasos se omite y de que un fallo detiene la release.

### 2. `.claude/skills/pv-version/SKILL.md`

- **Nuevo paso 0.6: "Cargar pipeline personalizado".** Tras el guardrail (0.5): buscar
  `{workFolder}/stuff/custom-version-pipeline.md`. Si no existe, seguir igual sin decir
  nada. Si existe, **leerlo y parsear los pasos por sección**, pero **sin sustituir
  `{XXXX}` todavía** (aún no está resuelto). La sustitución de variables se hace en cada
  anclaje, en el momento de ejecutar.
- **Insertar la ejecución de cada hook** en su punto, cada bloque con la forma "si el
  pipeline define pasos para esta sección, ejecútalos en orden; si uno falla, para y
  explícalo":
  - **"Before starting"** → nuevo bloque entre 0.6 y 1. Solo `{workFolder}` sustituido.
  - **"In the middle"** → dentro del paso 4, tras `copy-build-artifacts.py`. `{XXXX}` y
    rutas de `versions/{XXXX}/` ya disponibles.
  - **"At the end"** → nuevo bloque entre 6 y 7. `{XXXX}` y rutas disponibles.
- **Actualizar el párrafo de `stuff/`** al principio del `SKILL.md` para nombrar el
  segundo fichero (`how-to-compile-version.md` + `custom-version-pipeline.md`), y la
  nota de idioma para incluirlo.
- **Actualizar el paso 7 (resumen)** para mencionar, si hubo pipeline, qué secciones se
  ejecutaron y qué produjeron (especialmente lo de "At the end").

### 3. `.claude/skills/pv-version/workflow.version.md`

Añadir 3 nodos al diagrama de ejecución, cada uno un `{decisión}` "¿el pipeline define
pasos para esta sección?" → `[Ejecutar pasos de la sección X]` / seguir:
- "Before starting" entre `S05Empty -->|Yes|` y `S1Resolve`.
- "In the middle" entre `S4Copy` y `S5Docs`.
- "At the end" entre `S6Changelog` y `S7Summary`.
Es el source of truth de la secuencia; si no se toca, diverge del `SKILL.md` (y el
propio `SKILL.md` dice que en ese caso gana el diagrama).

### 4. `.claude/skills/pv-version/version-flow-diagram.template.md`

Diagrama cara al usuario: **un único nodo genérico** "Pasos personalizados del proyecto
(stuff/custom-version-pipeline.md)" conectado como punto de extensión, sin detalle de
las 3 secciones ni de parámetros. Basta con señalar que el flujo es extensible.

### 5. `.claude/skills/pv-init/schema.json` — **no tocar**

El fichero vive en `stuff/` por convención (como `how-to-compile-version.md`, que
tampoco está en el schema salvo la mención en prosa de `workFolder`). Si acaso, ampliar
esa frase en prosa para nombrar el segundo fichero — opcional.

### 6. Guardrail: `pv-version` no se edita desde un proyecto consumidor

Problema observado: al pedir algo relacionado con el flujo de versión en un proyecto
consumidor, el modelo a veces propone **editar `pv-version/SKILL.md` o
`workflow.version.md`** en vez de usar los puntos de personalización. Eso rompe la
separación framework/proyecto y se pierde en el siguiente `pv-update`. Ahora que este
cambio añade el mecanismo (`custom-version-pipeline.md`) que hace innecesario editar la
skill, es el momento de poner la barrera explícita.

Añadir a `pv-version/SKILL.md`, cerca del inicio (junto al párrafo de `{workFolder}` /
`stuff/`), un párrafo del estilo:

> **Esta skill es framework instalado, no editable desde un proyecto consumidor.** Si el
> usuario pide cambiar *cómo* funciona el flujo de versión (añadir un paso, cambiar el
> orden, un check previo, publicar algo al terminar), la respuesta correcta **no** es
> editar este `SKILL.md`, `workflow.version.md`, ni ningún fichero bajo
> `.claude/skills/pv-*/`. Los puntos de personalización son dos, ambos en
> `{workFolder}/stuff/`: la compilación del entregable → `how-to-compile-version.md`;
> pasos propios del proyecto en 3 puntos del flujo (antes de empezar / por el medio / al
> final) → `custom-version-pipeline.md` (ver paso 0.6). Si lo que se pide no encaja en
> ninguno de los dos, decírselo al usuario y proponer abrir un cambio en el repo del
> framework — nunca un parche local a la skill.

Reforzar con la marca ya existente: la presencia de `framework.frameworkStatus` en
`pv-context.json` significa que estas skills se gestionan vía `pv-update`; editarlas a
mano las deja en estado inconsistente (ya lo comprueba el paso 0 comparando versiones).

## Fuera de alcance

- Scripts nuevos (`.py`) para parsear/ejecutar el pipeline: los pasos son comandos que
  `pv-version` lanza como ya lanza los de `how-to-compile-version.md`.
- Hooks en otras skills (`pv-do`, `pv-new`, etc.).
- Replicar el guardrail de §6 ("no editar la skill desde un proyecto consumidor") en las
  demás skills de orquestación (`pv-new`, `pv-fix`, `pv-do`, `pv-init`): el mismo fallo
  puede darse con cualquiera, pero es un cambio más ancho. Seguimiento aparte.
- Campo nuevo en `pv-context.json` / `scaffold-project.py` creando el fichero por
  defecto.
- Idioma dedicado para `stuff/*` (sigue `interaction.language`).
- Un cuarto hook "después del resumen": "Al final" ya corre antes del resumen para que
  este pueda reportar lo que produjo; subir/publicar encaja ahí.
- Paralelismo, condicionales o dependencias entre pasos: orden secuencial, fallo = stop.
- Hook `before-compile` (lo cubre `how-to-compile-version.md` con un "Step 1" previo) y
  hook `after-docs` (redundante con "Al final").
