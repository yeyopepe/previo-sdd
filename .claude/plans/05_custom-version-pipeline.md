# `custom-version-pipeline.md`: pasos de usuario en el flujo de `pv-version`

## Context

`pv-version` orquesta la preparación de una release con una secuencia **fija** (ver
`workflow.version.md`): guardrail de `implemented/` → resolver `XXXX` → crear
`versions/XXXX/` → compilar el entregable → copiar docs → `pv-internal-changelog` →
resumen.

El único punto donde hoy el proyecto puede inyectar algo propio es el paso 4
(`{workFolder}/stuff/how-to-compile-version.md`), y solo cubre **cómo compilar el
entregable** (comandos + artefactos a `files/`). No hay forma de que el usuario añada
pasos al *flujo* de la release: cosas como "antes de compilar, bump de versión en
`package.json`", "después de copiar docs, generar un PDF de notas", "al final, subir el
zip a un bucket", "validar que el working tree está limpio antes de empezar".

Objetivo: **mínimo cambio** — un fichero nuevo `{workFolder}/stuff/custom-version-pipeline.md`
que `pv-version` lee (si existe) y cuyos pasos ejecuta en puntos de anclaje bien
definidos del flujo. Sin tocar `workflow.version.md`'s secuencia troncal, sin scripts
nuevos, sin schema nuevo en `pv-context.json`.

## Piezas que ya existen (contexto)

- `{workFolder}/stuff/` es una subcarpeta fija que crea `pv-init`'s
  `scaffold-project.py` (con `.gitkeep`). Descrita en `schema.json` como *"holds
  pv-version's own project-specific files, starting with how-to-compile-version.md"* —
  o sea, el sitio natural para un segundo fichero de este tipo.
- `pv-version/SKILL.md` ya trata `stuff/*` como texto en `interaction.language` (no hay
  campo de idioma dedicado para `stuff/`). Aquí es `es`.
- `how-to-compile-version.template.md` ya soporta procesos multi-paso / multi-artefacto:
  el patrón "Step N: {name}" con comando + fichero resultante por paso. El nuevo fichero
  reutiliza esa forma.
- El flujo troncal está congelado en dos diagramas: `workflow.version.md` (ejecución) y
  `version-flow-diagram.template.md` (cara al usuario). Ambos habría que tocarlos si los
  puntos de anclaje se representan; ver §4.

## Decisiones de alcance (pendientes de validar contigo)

Marco lo que propongo; lo afinamos en el análisis posterior.

1. **Puntos de anclaje (hooks).** Propuesta de conjunto mínimo y cerrado, alineado con
   los nodos de `workflow.version.md`:
   - `before-all` — nada más pasar el guardrail de `implemented/`, antes de crear
     `versions/XXXX/`. Uso típico: validaciones de precondición (working tree limpio,
     rama correcta).
   - `before-compile` — tras crear la carpeta, justo antes del paso 4. Uso típico:
     bump de versión, generación de assets que el build necesita.
   - `after-compile` — tras copiar artefactos a `files/`, antes de copiar docs. Uso
     típico: firmar/empaquetar, checksums.
   - `after-docs` — tras `copy-docs.py`, antes de `pv-internal-changelog`. Uso típico:
     material derivado de la doc.
   - `after-all` — tras el resumen final. Uso típico: publicar/subir el contenido de
     `versions/XXXX/`.
   Un fichero puede definir 0..N pasos por hook; hooks sin pasos se omiten sin ruido.

2. **Qué es un "paso".** Igual que `how-to-compile-version.md`: prosa + bloque de
   comando(s) a ejecutar desde la raíz del repo, con nota de qué produce / cómo
   verificar que fue bien. `pv-version` los ejecuta en orden; **si uno falla, para y lo
   explica** (mismo criterio que el paso 4 actual), sin inventar alternativa.

3. **Variables de contexto disponibles para los pasos.** Al menos `{XXXX}` y las rutas
   `{workFolder}/versions/{XXXX}/` y sus `files/` y `docs/`. El fichero las referencia
   textualmente; `pv-version` sustituye al leerlo. (A decidir: si se permite algo más,
   p.ej. la rama actual.)

4. **Fichero ausente = comportamiento actual, sin cambios.** No se crea por defecto en
   `scaffold-project.py` (a diferencia de que `how-to-compile-version.md` tampoco se
   crea hasta la primera `pv-version`). Se documenta cómo crearlo, con plantilla.

5. **`pv-version` no lo autogenera preguntando.** A diferencia de
   `how-to-compile-version.md` (que `pv-version` rellena preguntándote la primera vez),
   este fichero es 100% opt-in manual: si no existe, `pv-version` no pregunta nada.
   (A decidir: ¿o sí conviene un aviso una-sola-vez tipo "puedes añadir pasos custom con
   stuff/custom-version-pipeline.md"?)

## Cambios propuestos (mínimos)

### 1. Nueva plantilla `.claude/skills/pv-version/custom-version-pipeline.template.md`

Documento de referencia + esqueleto, en el mismo tono que
`how-to-compile-version.template.md`:
- Cabecera explicando qué es (fichero propio del proyecto, no de `pv-context.json`;
  opcional; leído y ejecutado por `pv-version` si existe).
- Sección por hook (`## before-all`, `## before-compile`, `## after-compile`,
  `## after-docs`, `## after-all`), cada una con 0..N `### Step N: {name}` y, dentro,
  "Command(s) to run" / "Produces / how to verify" / "Notes".
- Lista de variables sustituibles (`{XXXX}`, rutas).
- Nota de que un hook sin pasos se omite y de que un fallo detiene la release.

### 2. `.claude/skills/pv-version/SKILL.md`

- **Nuevo paso 0.6 (o sub-pasos en los existentes): "Cargar pipeline personalizado".**
  Tras el guardrail (0.5) y antes de resolver `XXXX` (1): buscar
  `{workFolder}/stuff/custom-version-pipeline.md`. Si no existe, seguir igual. Si existe,
  leerlo, parsear los pasos por hook y sustituir variables (con `{XXXX}` resuelto: por
  eso se lee aquí pero los hooks `before-*` que dependen de `XXXX` se ejecutan **después**
  del paso 1 — a afinar en análisis).
- **Insertar la ejecución de cada hook** en su punto:
  - `before-all` → nuevo, entre 1 y 2 (o entre 0.5 y 1 si no usa `{XXXX}`).
  - `before-compile` → entre 3 y 4.
  - `after-compile` → dentro de 4, tras `copy-build-artifacts.py`.
  - `after-docs` → entre 5 y 6.
  - `after-all` → tras 7.
  Cada bloque: "si el pipeline define pasos para este hook, ejecútalos en orden; si uno
  falla, para y explícalo".
- **Actualizar el párrafo de `stuff/`** al principio del `SKILL.md` para nombrar el
  segundo fichero (`how-to-compile-version.md` + `custom-version-pipeline.md`).
- **Actualizar el paso 7 (resumen)** para mencionar, si hubo pipeline, qué hooks se
  ejecutaron.

### 3. `.claude/skills/pv-version/workflow.version.md`

Añadir los nodos de hook al diagrama de ejecución (cada uno un `{decisión}` "¿pipeline
define pasos para este hook?" → `[Ejecutar pasos del hook X]` / seguir). Es el source of
truth de la secuencia; si no se toca, el diagrama y el `SKILL.md` divergen (y el propio
`SKILL.md` dice que en ese caso gana el diagrama).

### 4. `.claude/skills/pv-version/version-flow-diagram.template.md`

Diagrama cara al usuario: añadir un nodo genérico "Pasos personalizados del proyecto
(stuff/custom-version-pipeline.md)" o cinco puntos de extensión marcados, sin detalle de
parámetros. A decidir en análisis cuánto detalle merece aquí.

### 5. `.claude/skills/pv-init/schema.json` — **solo si hace falta**

Propuesta: **no tocarlo**. El fichero vive en `stuff/` por convención (como
`how-to-compile-version.md`, que tampoco está en el schema salvo la mención en prosa de
`workFolder`). Si acaso, ampliar esa frase en prosa para nombrar el segundo fichero.

## Fuera de alcance

- Scripts nuevos (`.py`) para parsear/ejecutar el pipeline: los pasos son comandos que
  `pv-version` lanza como ya lanza los de `how-to-compile-version.md`.
- Hooks en otras skills (`pv-do`, `pv-new`, etc.).
- Campo nuevo en `pv-context.json` / `scaffold-project.py` creando el fichero por
  defecto.
- Idioma dedicado para `stuff/*` (sigue `interaction.language`).
- Paralelismo, condicionales o dependencias entre pasos: orden secuencial, fallo = stop.

## Preguntas abiertas para el análisis

1. ¿El conjunto de 5 hooks es el correcto, o sobra/falta alguno? (p.ej. ¿un hook
   `before-changelog` separado de `after-docs`? ¿uno tras `pv-internal-changelog` y
   antes del resumen?)
2. ¿`before-all` se ejecuta antes o después de resolver `XXXX`? Afecta a si puede usar
   `{XXXX}` como variable.
3. ¿`pv-version` avisa una vez de que este fichero existe como opción, o silencio total
   si no está?
4. ¿Qué variables se exponen a los pasos, más allá de `{XXXX}` y las rutas de
   `versions/{XXXX}/`?
5. ¿Cuánto detalle de los puntos de extensión va en el diagrama cara al usuario?
6. Formato exacto del fichero: ¿headings Markdown por hook (como
   `how-to-compile-version.md`) o algo más estructurado? Markdown encaja con el resto de
   `stuff/` y con cómo `pv-version` ya "lee y sigue" ese tipo de fichero.
