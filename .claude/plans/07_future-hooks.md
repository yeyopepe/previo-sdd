# `future-hooks.md`: propuestas de hooks para revisar más adelante

## Context

El framework `pv-*` tiene un mecanismo de **hooks de proyecto**: puntos de inserción donde
un skill instalado ejecuta pasos *definidos por el proyecto consumidor*, sin tocar el
`SKILL.md`. Catálogo completo y actualizado en `pv-design.en.md`/`.es.md`, sección
"Project hooks"/"Hooks de proyecto". Hoy existen en:

| Skill        | Hooks actuales                                                              | Fichero seed en el proyecto                          |
|--------------|------------------------------------------------------------------------------|-----------------------------------------------------|
| `pv-how`     | `how/10-before-analysis`, `how/20-after-plan`                                | `{workFolder}/stuff/hooks/how/*.md`                  |
| `pv-new`     | `new/20-after-entry`                                                          | `{workFolder}/stuff/hooks/new/*.md`                  |
| `pv-fix`     | `fix/10-before-entry` (vía rápida; reutiliza además los dos hooks de `pv-do`) | `{workFolder}/stuff/hooks/fix/*.md`                  |
| `pv-do`      | `do/10-before-implementation`, `do/20-after-implementation`                  | `{workFolder}/stuff/hooks/do/*.md`                   |
| `pv-version` | `version/05-before-guardrail`, `version/10-before-version`, `version/20-after-build`, `version/30-after-changelog` | `{workFolder}/stuff/hooks/version/*.md` |

Contrato compartido de un hook (ya establecido, se respeta en todo lo que sigue):

- Seed LITERAL copiado por `pv-init`/`pv-update` a `{workFolder}/stuff/hooks/<skill>/NN-slug.md`;
  **se crea solo si no existe, nunca se sobrescribe** → los pasos que añade el equipo
  sobreviven a una actualización del framework.
- El fichero declara bloques `### Step N: {name}` con **Command(s) to run** /
  **Generated file(s)** / **Notes**. Sin bloques `### Step` → hook omitido en silencio.
- Sustituibles solo las variables que el skill garantiza que existen en ese punto del
  flujo (p. ej. `{workFolder}` siempre; `{xxxx}` solo si la entrada ya está resuelta).
- Si un paso falla o no aparece su salida esperada, **el skill se detiene y lo explica**;
  no improvisa ni continúa.
- El diagrama `workflow.<skill>.md` marca los nodos de hook en naranja y es la fuente de
  verdad de dónde se insertan.

**Objetivo de este plan:** aparcar propuestas de hooks para una revisión más adelante.
Nada de aquí está decidido ni planificado — es un banco de ideas. La convención de nombres
(`<NN>-<before|after>-<objeto>`) y el catálogo de hooks ya implementados están documentados
en `pv-design.en.md`/`.es.md`, sección "Project hooks"/"Hooks de proyecto".

Cuando una de estas propuestas se apruebe, se implementa y se borra de aquí.

## Principios para decidir si un punto merece un hook

1. **Hay una acción de proyecto real y repetible** que hoy el usuario tiene que recordar
   hacer a mano alrededor de ese momento (lint, generar tipos, actualizar un índice,
   notificar, sellar un artefacto…).
2. **El momento es determinista y nombrable** dentro del flujo del skill (antes de X,
   después de Y), no "en algún punto".
3. **Las variables que necesita el hook existen y son estables** en ese punto.
4. **No sustituye a los dos puntos de personalización que ya existen** (`how-to-compile.md`
   para construir el entregable; los hooks ya definidos). Si encaja en uno de esos, no es
   un hook nuevo.
5. **El coste de parar el flujo por un fallo del hook es aceptable** (o el hook es
   explícitamente "best-effort" y así se documenta — decisión pendiente, ver "Cuestiones
   abiertas").

## Vocabulario de `<objeto>` (pre-acordado, para nombrar estas propuestas si se aprueban)

El nombre de un hook es `<NN>-<before|after>-<objeto>` (catálogo completo en
`pv-design.en.md`/`.es.md`, sección "Project hooks"/"Hooks de proyecto"). Ya están en uso:
`analysis`, `plan`, `entry`, `guardrail`, `implementation`, `version`, `build`, `changelog`.
Estos otros están **pre-acordados** para los puntos que aún no tienen hook, para no
reinventarlos en cada propuesta:

| `<objeto>`       | Hito que nombra                                                    | Skill         |
|------------------|------------------------------------------------------------------ |---------------|
| `task`           | Una tarea concreta de la sección (b) del plan                      | `pv-do`       |
| `docs-copy`      | La copia de la doc técnica congelada a `versions/{XXXX}/`          | `pv-version`  |
| `scaffold`       | El scaffold de carpetas + `pv-context.json`                        | `pv-init`     |
| `repair`         | La reparación de config que hace `pv-update`                       | `pv-update`   |
| `note`           | El guardado/expansión de una idea en `todo/`                       | `pv-todo`     |
| `report`         | El informe de estado                                               | `pv-status`   |

(`entry` ya lo usa `pv-new` para `new/20-after-entry` y `pv-fix` para `fix/10-before-entry`;
P2 lo reutilizaría de nuevo para `fix/20-after-entry` — mismo hito, otro punto del flujo.)

## Propuestas

Ninguna está decidida. "Utilidad aparente media/baja" es solo una intuición, no un
compromiso. Los slugs son tentativos pero ya siguen el catálogo de nombres documentado en
`pv-design.en.md`/`.es.md`.

### Utilidad aparente media

#### P2 — `pv-fix` : `fix/20-after-entry` (después de documentar un fix no trivial en `inProgress/`)

- **Momento:** el fix no era trivial, `pv-fix` lo ha documentado en `inProgress/` y va a
  encadenar `pv-how`.
- **Para qué:** igual que H3 (`pv-new : new/20-after-entry`, ya planificado) pero para
  bugs — alta en el tracker como `bug`, aviso al responsable del área afectada. Si se
  aprueba, copia de H3 cambiando el `owner`.
- **Variables:** `{workFolder}`, `{xxxx}`.

#### P3 — `pv-do` : `do/15-after-task` (tras marcar cada checkbox de la sección `b` del plan)

- **Momento:** dentro del bucle de implementación, cada vez que `pv-do` completa una tarea
  del plan y marca su caja.
- **Para qué:** feedback incremental — correr los tests del módulo tocado por esa tarea,
  `typecheck` rápido, commit por tarea. Hoy `pv-do` solo tiene hook al principio y al
  final; en cambios largos eso es tarde para detectar una rotura.
- **Variables:** `{workFolder}`, `{xxxx}`, identificador/orden de la tarea recién marcada,
  idealmente la lista de ficheros que tocó.
- **Riesgo alto de parar:** si este hook detiene el flujo en cada tarea, un fallo a mitad
  deja el cambio a medio implementar. Necesita política clara de reanudación (ver
  "Cuestiones abiertas") — por eso no está entre los ya planificados pese a ser muy útil.

#### P4 — `pv-version` : `version/40-after-docs-copy` (después de copiar la doc técnica al `versions/{XXXX}/`)

- **Momento:** `pv-version` ya ha copiado la documentación técnica actual a
  `{workFolder}/versions/{XXXX}/` y aún no ha (o acaba de) generar el changelog.
- **Para qué:** post-procesar la doc congelada — convertir a PDF/HTML, sellar con la
  versión y la fecha, quitar secciones internas, subir a un sitio de docs.
- **Variables:** `{workFolder}`, `{XXXX}`, ruta a `versions/{XXXX}/`.
- **Nota:** revisar solape con `20-after-build` y `30-after-changelog`; puede que baste con
  reordenar/renombrar los tres existentes en lugar de añadir un cuarto.

### Utilidad aparente baja / a debatir

#### P5 — `pv-update` : `update/90-after-repair` (después de que `pv-update` repara la config)

- **Para qué:** re-validar el proyecto tras la reparación (re-generar `pv.py`, correr un
  smoke test del framework, avisar si algo quedó `blocked`).
- **Contra:** `pv-update` es exactamente el skill que gestiona los seeds de hooks; un hook
  suyo que dependa de un seed que él mismo acaba de crear/migrar es frágil. Definir bien el
  orden o descartarlo.

#### P6 — `pv-init` : `init/90-after-scaffold` (tras generar `pv-context.json` y el scaffold)

- **Para qué:** enganchar el framework al resto del repo — añadir entradas a `.gitignore`,
  crear un `Makefile`/`npm script` de conveniencia, un primer commit del scaffold.
- **Contra:** en `pv-init` el seed del propio hook se acaba de crear; solo tiene sentido
  como "one-shot" y el usuario podría hacerlo a mano igual de bien.

#### P7 — `pv-todo` : `todo/20-after-note` (tras guardar/expandir una idea en `todo/`)

- **Para qué:** volcar la idea a un backlog externo.
- **Contra:** `pv-todo` es deliberadamente "fuera del workflow"; añadirle integración va
  contra su propósito. Probablemente **no** se implementa; queda listado para cerrar el
  debate.

#### P8 — `pv-status` : hook de salida para publicar el informe

- **Slug tentativo:** `status/20-after-report`.
- **Para qué:** que `/pv-status` además de responder en el chat deje el informe en un
  fichero/dashboard del equipo.
- **Contra:** ya hay un flag ("escribe el informe si el usuario lo pide"); un hook fijo
  duplica esa decisión.

## Tabla de propuestas

| ID | Skill        | Slug tentativo               | Utilidad aparente | Depende de cuestión abierta |
|----|--------------|------------------------------|-------------------|-----------------------------|
| P2 | `pv-fix`     | `fix/20-after-entry`         | Media             | —                           |
| P3 | `pv-do`      | `do/15-after-task`           | Media             | política de reanudación     |
| P4 | `pv-version` | `version/40-after-docs-copy` | Media             | solape con 20/30            |
| P5 | `pv-update`  | `update/90-after-repair`     | Baja              | orden seed/hook             |
| P6 | `pv-init`    | `init/90-after-scaffold`     | Baja              | —                           |
| P7 | `pv-todo`    | `todo/20-after-note`         | ¿Descartar?       | propósito del skill         |
| P8 | `pv-status`  | `status/20-after-report`     | Baja              | duplica flag existente      |

## Cuestiones abiertas (a resolver si alguna propuesta se aprueba)

Las de nombres y numeración (catálogo de partículas + convención de `NN`), y el "cómo" de
dar de alta un hook nuevo (`HOOK_SETS` de `scaffold-project.py`/`audit-context.py`, checks
de auditoría), **ya están resueltas y aplicadas** — ver el catálogo completo en
`pv-design.en.md`/`.es.md`, sección "Project hooks"/"Hooks de proyecto". `fix/10-before-entry`
(antes P1) ya se implementó con semántica de fallo dura ("para y explica"), sin necesitar
la variante blanda ni paso de ficheros al hook. Lo que sigue solo afecta a P3:

1. **Hooks a mitad de bucle (P3): política de reanudación.** Si el hook falla en la tarea
   4 de 9, ¿`pv-do` se reanuda desde la 4 al reinvocarlo? ¿Marca la entrada como
   `blocked`? Hay que definirlo antes de exponer cualquier hook dentro de un bucle.
2. **Semántica de fallo "best-effort" (avisan y siguen).** Hoy el contrato de todo hook es
   "para y explica". P3, por correr a mitad de bucle, podría necesitar la variante blanda.
   Si se añade, el fichero seed necesita un campo explícito
   (`**On failure:** stop | warn-and-continue`) y el diagrama otra forma de nodo.
3. **Paso de ficheros al hook (P3).** Necesita "los ficheros que tocó esta tarea". Hoy solo
   se sustituyen `{workFolder}` y `{xxxx}`. Hace falta una convención: ¿el skill escribe un
   `changed-files.txt` en la carpeta de la entrada y el hook lo lee? ¿Se añade una variable
   `{changedFiles}`?
