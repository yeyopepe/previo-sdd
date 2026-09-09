# `high-priority-hooks.md`: hooks a crear + nomenclatura — análisis técnico de implementación

Alcance: **lo que ya existe y lo que vamos a crear**. Es decir, los 5 hooks del commit
`8194c30` (4 de ellos se **renombran** para cumplir el catálogo, con migración en
`pv-update`) y los **4 hooks nuevos** (H1–H4) con su análisis técnico de implementación y
la convención de nombres que se aplica a todos los hooks. Las propuestas de hooks aún sin
decidir están en [`07_future-hooks.md`](07_future-hooks.md).

## Los 4 hooks

| ID  | Skill        | Hook                        | Momento en el flujo                                                        |
|-----|--------------|-----------------------------|---------------------------------------------------------------------------|
| H1  | `pv-how`     | `how/10-before-analysis`    | Inicio del paso 3 (analizar), antes de escribir `plan.md`                 |
| H2  | `pv-how`     | `how/20-after-plan`         | Tras el paso 3.1 (riesgo escrito), antes del paso 3.2 (preguntar si implementar) |
| H3  | `pv-new`     | `new/20-after-entry`        | Fin del paso 5, tras validar la doc y antes de ceder el turno a `pv-how`  |
| H4  | `pv-version` | `version/05-before-guardrail` | Inicio, antes del paso 0.5 (guardrail `implemented/` vacío) y de resolver `{XXXX}` |

Los nombres siguen el **catálogo de partículas** de la sección siguiente. Los 5 hooks ya
existentes del commit `8194c30` se revisan contra ese catálogo en "Los 5 hooks ya
existentes: renombrado" — 4 se renombran, 1 se queda.

## Catálogo de partículas para nombrar hooks

Un nombre de hook es siempre `<NN>-<temporal>-<objeto>`:

- **`<NN>`** — dos dígitos, orden numérico = orden de ejecución dentro del skill. Ver
  "Convención de numeración `NN`" más abajo.
- **`<temporal>`** — **una** de estas dos partículas, siempre:

  | Partícula  | Significado                                                        |
  |------------|------------------------------------------------------------------|
  | `before-`  | El hook corre **justo antes** de que el skill haga `<objeto>`.   |
  | `after-`   | El hook corre **justo después** de que el skill haya hecho `<objeto>`. |

  Se descarta `pre-`/`post-` (los usa hoy `pv-version` por historia) en favor de
  `before-`/`after-`: más legible, ya es lo que usa `pv-do`, y evita tener dos vocabularios.

- **`<objeto>`** — **un** sustantivo, en singular, que nombra el hito del flujo del skill
  al que el hook se ancla. Debe ser un término que el propio `SKILL.md`/`workflow.*.md`
  ya use para ese paso, no uno inventado. Los que usan los 4 hooks de este documento:

  | `<objeto>`  | Hito que nombra                                                              | Hooks       |
  |-------------|---------------------------------------------------------------------------- |-------------|
  | `analysis`  | El análisis técnico previo a escribir `plan.md`                             | H1          |
  | `plan`      | El fichero `plan.md` (escrito y con el riesgo ya calculado)                 | H2          |
  | `entry`     | La carpeta de change/fix bajo `inProgress/`, documentada y con sus `design_*` | H3        |
  | `guardrail` | Una comprobación bloqueante del skill (aquí: `implemented/` vacío)          | H4          |
  | `implementation` | El bucle de implementación de código (sección (b) del plan)            | `do/10` (renombrado) |
  | `version`   | Resolver el código de versión `{XXXX}` (paso 1 de `pv-version`)             | `version/10` (renombrado) |
  | `build`     | La generación / copia de los artefactos del entregable                     | `version/20` (renombrado) |
  | `changelog` | La redacción del changelog funcional                                       | `version/30` (renombrado) |

  Reglas para el `<objeto>`:
  - **Singular** siempre (`after-task`, no `after-tasks`), aunque el hook corra N veces.
  - Sin verbo (`after-build`, no `after-building` ni `after-build-done`).
  - Un guion interno solo si el hito no tiene nombre de una palabra (`docs-copy`); evítalo
    si puedes.
  - Si dudas entre dos, elige el que aparezca **literalmente** en el `SKILL.md` de ese
    paso.
  - Antes de inventar un `<objeto>` nuevo, mira si ya está en el vocabulario pre-acordado
    de [`07_future-hooks.md`](07_future-hooks.md) ("Vocabulario de `<objeto>`").

### Los 5 hooks ya existentes: renombrado

Revisión contra el catálogo. **4 se renombran, 1 se queda.** Los renombrados van en la
misma tanda que H1–H4, con migración en `pv-update` (ver "Cómo se implementa un hook
nuevo" → paso 6).

| Hook actual                | Momento real                                                        | ¿Cumple? | Nuevo nombre                     |
|----------------------------|------------------------------------------------------------------- |----------|----------------------------------|
| `do/10-before-start`       | inicio del paso 2, antes de tocar código (antes del bucle de impl.) | `before-` ok; `start` ✗ | **`do/10-before-implementation`** |
| `do/20-before-finish`      | fin del 2.1 (código + docs hechos), antes de mover a `implemented/` | `before-` ok; `finish` ✗ pero… | **se queda** `do/20-before-finish` |
| `version/10-pre-release`   | antes del paso 1, antes de resolver `{XXXX}`                        | `pre-` ✗ | **`version/10-before-version`**   |
| `version/20-post-build`    | tras copiar artefactos a `files/`, antes de zipear docs            | `post-` ✗ | **`version/20-after-build`**      |
| `version/30-post-changelog`| tras redactar el changelog, antes del resumen                      | `post-` ✗ | **`version/30-after-changelog`**  |

Notas:
- **`do/20-before-finish` se queda** por decisión explícita. `finish` no está en el
  vocabulario, pero renombrarlo (`before-move` / `after-documentation`) no aporta claridad
  suficiente para justificar el cambio. Queda como excepción única y documentada.
- **`version/10-before-version`**: el `<objeto>` es `version` — el hito es "resolver el
  código de versión `{XXXX}`" (paso 1 de `pv-version`). No confundir con H4
  (`version/05-before-guardrail`), que corre aún antes, antes del guardrail de
  `implemented/` vacío. Con ambos: `05-before-guardrail` → guardrail → `10-before-version`
  → se resuelve `{XXXX}`.
- El `<objeto>` `version` se añade al vocabulario (tabla de arriba y la de
  `07_future-hooks.md`).

### Documentar el catálogo en la doc técnica

Al implementar esta tanda, el catálogo (partículas `before`/`after`, tabla de `<objeto>`s,
reglas, convención de `NN` de más abajo, y la excepción `do/20-before-finish`) debe quedar
recogido en **`pv-design.en.md`**, en una sección nueva **"Project hooks"** (o ampliando
"Workflow diagrams"). A partir de ahí, cada `<NN>-<slug>.template.md` solo describe su
punto concreto y enlaza a esa sección en vez de repetir el preámbulo. En el mismo pase se
actualizan las menciones a los nombres viejos de hook por todo `pv-design.en.md` (ver
paso 4). Es requisito de cierre de la tanda, no un extra.

### Documentar los hooks en la guía de usuario

La guía de usuario (`.claude/pv-doc/pv-guide.en.md` y `pv-guide.es.md`), apartado
**"4. Pasos personalizados en el pipeline de versión (hooks)"**, hoy solo habla de
`pv-version` ("tres puntos fijos", `hooks/version/*.md`). Al implementar esta tanda ese
apartado debe:

- Generalizarse: ya no son solo los del pipeline de versión — hay hooks en `pv-how`,
  `pv-new`, `pv-do` y `pv-version`, cada uno con su subcarpeta bajo
  `{workFolder}/stuff/hooks/`. Ajustar el título y el texto ("tres puntos fijos" ya no
  vale).
- Incluir una **lista de los hooks disponibles** — un ítem por hook, con: skill dueño,
  slug (`<subdir>/<NN>-<temporal>-<objeto>`), y una frase de en qué punto del flujo corre
  y para qué sirve. Es la tabla "Los 4 hooks" + "Los 5 hooks ya existentes" de este
  documento, reescrita para usuario final (sin la parte de renombrado ni la mecánica de
  implementación). Con los nombres **nuevos** ya (`10-before-implementation`,
  `10-before-version`, `20-after-build`, `30-after-changelog`, más H1–H4).
- Mantener el enlace a que se consultan los hooks realmente definidos en
  `{workFolder}/stuff/hooks/` y que se editan pidiéndoselo a Claude en lenguaje natural.

Se hace en el mismo pase de doc que la sección técnica, en ambos idiomas. Es requisito de
cierre de la tanda.

### H1 — `pv-how` : `how/10-before-analysis`

- **Momento exacto:** al principio del paso 3 (`## 3. Analyze and write plan.md`), antes
  del sub-paso 5 que invoca `pv-internal-tech-analysis`. En re-análisis (paso 2 elige
  "re-analizar") también se ejecuta; si el usuario elige "implementar lo que ya hay"
  (salta a 3.1), **no** se ejecuta — este hook alimenta el análisis, y no hay análisis.
- **Para qué:** cargar contexto que el análisis debería tener siempre y que hoy depende de
  que el usuario lo pegue — refrescar tipos/OpenAPI generados, `db schema dump`,
  regenerar un índice de módulos, traer doc de una dependencia externa a un fichero local
  que `pv-internal-tech-analysis` pueda leer como parte de `sourcecodeDir`/docs.
- **Variables:** `{workFolder}`, `{xxxx}` (la entrada existe en `inProgress/{xxxx}/` desde
  el paso 1).
- **Semántica de fallo:** "para y explica" (contrato actual). Si el dump falla, planificar
  a ciegas es peor que parar. No necesita variante blanda.

### H2 — `pv-how` : `how/20-after-plan`

- **Momento exacto:** después del paso 3.1 (mediana de riesgo ya escrita en
  `.metadata.json` y verificada) y antes del paso 3.2 (`## 3.2 Ask whether to implement`).
  Punto elegido a propósito **después** de 3.1: así el hook puede leer la mediana de riesgo
  ya persistida y publicarla donde el equipo la consuma.
- **Para qué:** validaciones sobre el propio plan y export — linter de formato de
  `plan.md`, comprobar que las rutas citadas en secciones (c)/(d) existen, crear el ticket
  de implementación en un tracker con el resumen del plan y la mediana de riesgo.
- **Variables:** `{workFolder}`, `{xxxx}`. La ruta a `plan.md` es derivable
  (`{workFolder}/changes/inProgress/{xxxx}/plan.md`) — **no** se añade variable nueva
  (ver "Convención de variables" abajo); el paso del hook la compone con las dos que hay.
- **Semántica de fallo:** "para y explica". Un `plan.md` que no pasa el linter del equipo
  o cita rutas inexistentes es un plan que no debería llegar a `pv-do`.

### H3 — `pv-new` : `new/20-after-entry`

- **Momento exacto:** dentro del paso 5 (`5. State the next step`), después de que el
  paso 4 haya validado con el usuario los `design_*` y antes de que el skill diga
  "invoca `pv-how`" / encadene `pv-how`. Es el único punto de salida de `pv-new` hoy no
  personalizable.
- **Para qué:** dar de alta la entrada donde el equipo la sigue — issue en el tracker,
  post en un canal, fila en un índice `CHANGES.md`, etiqueta en un tablero.
- **Variables:** `{workFolder}`, `{xxxx}`. La carpeta de la entrada es derivable igual que
  en H2.
- **Semántica de fallo:** "para y explica". Es coherente con el resto del contrato y H3 no
  está en un bucle, así que un fallo aquí no deja nada a medias (la entrada ya está
  documentada en disco; solo falta el alta externa).
- **Simetría:** con `do/20-before-finish` (ya existe) y con P2 de `07_future-hooks.md`
  (`pv-fix : fix/20-after-entry`, propuesta). Al implementar H3 conviene dejar el slug y la
  estructura de forma que P2, si se aprueba, sea copy-paste con otro `owner`.
- **Nota `todo` mode:** `pv-new todo <code>` borra la idea de `todo/` al terminar. El hook
  va **después** de ese borrado (fin del paso 5), con la entrada ya en `inProgress/`.

### H4 — `pv-version` : `version/05-before-guardrail`

- **Momento exacto:** nuevo sub-paso `## 0.4. Hook: 05-before-guardrail`, entre el 0.2
  (invocación informativa) y el 0.5 (guardrail `implemented/` vacío). Antes de resolver
  `{XXXX}` (paso 1) y antes de crear `versions/{XXXX}/` (paso 2).
- **Para qué:** abortar barato — árbol git limpio, rama correcta, CI en verde, no existe
  ya un tag con el nombre previsto. Hoy el único guardrail automático es `implemented/`
  vacío.
- **Variables:** solo `{workFolder}` (igual que `10-before-version`; `{XXXX}` y
  `versions/{XXXX}/` no existen aún). Un paso que necesite la rama corre su propio
  `git rev-parse --abbrev-ref HEAD`.
- **Semántica de fallo:** "para y explica" — es exactamente su función.
- **Relación con `10-before-version`** (antes `10-pre-release`): corre en el paso 0.7,
  **después** de 0.6 (cargar hooks) pero **antes** de resolver `{XXXX}` (headers actuales
  del SKILL: 0.6 → 0.7 → 1). Revisar en implementación si H4 y `10-before-version` no
  acaban siendo el mismo punto: si `10-before-version` ya corre antes de `{XXXX}`, quizá H4
  sobra y basta documentar mejor que `10-before-version` sirve también de guardrail.
  **Decisión a tomar al implementar, mirando `workflow.version.md`.** Si se mantienen
  separados: H4 corre antes del guardrail (puede abortar antes incluso de comprobar
  `implemented/`), `10-before-version` corre después del guardrail y antes de `{XXXX}` — y
  el nombre encaja: el `<objeto>` es exactamente "resolver la versión".

## Cómo se implementa un hook nuevo (mecánica, ya establecida por el commit `8194c30`)

Cada hook **nuevo** toca los sitios 1–5. El renombrado de los 4 existentes añade el
sitio 6 (migración) y toca también 1, 3, 4 y 5 (los nombres viejos aparecen ahí). Para
H1/H2 (mismo skill) varios pasos se hacen una sola vez.

### 1. Fichero seed `.template.md` en el skill dueño

`.claude/skills/<skill>/hooks/<NN>-<slug>.template.md`. Copiar la estructura de
`.claude/skills/pv-do/hooks/20-before-finish.template.md` (el que no se renombra):

- Título `# <subdir>/<NN> — <slug>`.
- Párrafo 1: qué ejecuta el skill y en qué punto exacto del flujo; que es seed LITERAL
  copiado por `pv-init`/`pv-update`, creado solo si ausente, nunca sobrescrito.
- Párrafo 2: qué variables son sustituibles aquí (ver tabla de cada hook arriba); que sin
  bloques `### Step` el hook se omite en silencio; que un fallo detiene el skill.
- Comentario HTML con la plantilla `### Step N: {name}` (Command(s) to run / Generated
  file(s) / Notes).

Ficheros a crear:
- `pv-how/hooks/10-before-analysis.template.md`
- `pv-how/hooks/20-after-plan.template.md`
- `pv-new/hooks/20-after-entry.template.md`
- `pv-version/hooks/05-before-guardrail.template.md`

Ficheros a **renombrar** (git mv del `.template.md`, mismo contenido salvo el título
`# <subdir>/<NN> — <slug>` de la línea 1):
- `pv-do/hooks/10-before-start.template.md` → `10-before-implementation.template.md`
- `pv-version/hooks/10-pre-release.template.md` → `10-before-version.template.md`
- `pv-version/hooks/20-post-build.template.md` → `20-after-build.template.md`
- `pv-version/hooks/30-post-changelog.template.md` → `30-after-changelog.template.md`

(`pv-do/hooks/20-before-finish.template.md` no se toca.)

### 2. `scaffold-project.py` (`pv-init`) — `HOOK_SETS`

`.claude/skills/pv-init/scripts/scaffold-project.py`, dict `HOOK_SETS` (~línea 196):

```python
HOOK_SETS = {
    "version": ("pv-version", (
        "05-before-guardrail.md",   # + nuevo, PRIMERO (orden = orden de ejecución)
        "10-before-version.md",     # renombrado desde 10-pre-release
        "20-after-build.md",        # renombrado desde 20-post-build
        "30-after-changelog.md",    # renombrado desde 30-post-changelog
    )),
    "do": ("pv-do", (
        "10-before-implementation.md",  # renombrado desde 10-before-start
        "20-before-finish.md",          # SIN cambio
    )),
    "how": ("pv-how", (              # + subdir nuevo
        "10-before-analysis.md",
        "20-after-plan.md",
    )),
    "new": ("pv-new", (             # + subdir nuevo
        "20-after-entry.md",
    )),
}
```

`ensure_hook_set` ya resuelve `<name>.md` → `<name>.template.md` bajo
`.claude/skills/<skill_dir>/hooks/` y crea el subdir. Con los `.template.md` ya renombrados
(paso 1) no hace falta lógica nueva aquí para el rename — un proyecto nuevo se scaffoldea
directamente con los nombres nuevos. El bloque `DOC` de la cabecera menciona "pv-version's
three / pv-do's two" — actualizar ese texto.

### 3. `audit-context.py` (`pv-update`) — `HOOK_SETS` + `WORKFOLDER_STRUCTURE`

`.claude/skills/pv-update/scripts/audit-context.py`:

- Dict `HOOK_SETS` (~línea 282): el valor es `(owner, {NN: "<NN>-<slug>.md"})` — mapa por
  id. Deja los canónicos ya con los nombres nuevos:
  ```python
  "version": ("pv-version", {
      "05": "05-before-guardrail.md",
      "10": "10-before-version.md",
      "20": "20-after-build.md",
      "30": "30-after-changelog.md",
  }),
  "do":  ("pv-do",  {"10": "10-before-implementation.md", "20": "20-before-finish.md"}),
  "how": ("pv-how", {"10": "10-before-analysis.md", "20": "20-after-plan.md"}),
  "new": ("pv-new", {"20": "20-after-entry.md"}),
  ```
- `check_version_hooks_seed` itera `HOOK_SETS` y llama `_check_one_hook_set` por subdir:
  emite `stuff-<subdir>-hook-missing:<NN>` (reseed) y `stuff-<subdir>-hook-badslug:<file>`
  (normaliza el nombre). **Aquí es donde ocurre la migración de los renombrados** (ver
  paso 6): en un proyecto viejo, `stuff/hooks/do/10-before-start.md` tiene el `<NN>` `10`
  correcto pero el slug viejo → `_check_one_hook_set` lo detecta como `badslug` y
  `pv-update` lo renombra a `10-before-implementation.md` conservando el contenido. Hay que
  confirmar que el `badslug` actual **mueve el fichero** (no solo avisa) y que conserva los
  `### Step`; si solo avisa, ampliar esa rama. Igual para los 3 de `version`.
- Comprobar si `check_version_hooks_seed` monta a mano el listado de subdirs esperados en
  `stuff/hooks/` (para avisar de subdirs desconocidos): si es así, añadir `how` y `new`.
- Si hay un set de rutas "estructura esperada de `stuff/`" (`stuff/hooks` aparece
  suelto ~línea 80), añadir `stuff/hooks/how` y `stuff/hooks/new` si el audit lista
  subdirs concretos (verificar; puede que solo mire `stuff/hooks` a secas y no haga falta).
- El texto del docstring que dice "(see HOOK_SETS: version, do)" → "version, do, how, new".

### 4. `SKILL.md` del skill dueño — tabla de hooks + paso(s) de ejecución

Patrón de `pv-do/SKILL.md` §1.5 (tabla `<NN> | file | runs`) + §2.0/§2.2 (bloques
"Hook: `<slug>`") y de `pv-version/SKILL.md` §0.6 + §0.7/§4.1/§6.1.

- **`pv-how/SKILL.md`:**
  - Nuevo `## 0.6 Load the project's hooks` (copiar de `pv-do` §1.5, adaptar tabla:
    `10 | 10-before-analysis.md | step 3, before pv-internal-tech-analysis` /
    `20 | 20-after-plan.md | after step 3.1, before step 3.2`). Ponerlo tras el paso 1
    (entrada ya identificada, `{xxxx}` disponible).
  - Nuevo bloque `### Hook: 10-before-analysis` al principio del paso 3.
  - Nuevo bloque `### Hook: 20-after-plan` entre 3.1 y 3.2.
  - Actualizar el párrafo "**This skill is installed framework...**" (hoy dice que `pv-how`
    no tiene punto de personalización) para nombrar `{workFolder}/stuff/hooks/how/*.md`.
  - Actualizar la frase "**Before any other step**, read `workflow.how.md`... including the
    N hook insertion points" (copiar el patrón de `pv-do`/`pv-version`).
- **`pv-new/SKILL.md`:**
  - Nuevo `## Load the project's hooks` antes de `## Steps` (o como sub-paso 0.3), tabla
    de una fila: `20 | 20-after-entry.md | end of step 5, before handing off to pv-how`.
  - Nuevo bloque de ejecución dentro del paso 5.
  - Actualizar el párrafo de "installed framework, not editable" si lo tiene (verificar;
    `pv-new/SKILL.md` puede no llevarlo aún).
- **`pv-version/SKILL.md`:**
  - §0.6 tabla: añadir fila `05 | 05-before-guardrail.md | before step 0.5` y **renombrar**
    las tres existentes (`10-before-version.md`, `20-after-build.md`, `30-after-changelog.md`).
  - Nuevo `## 0.4. Hook: 05-before-guardrail` (copiar de §0.7), antes de §0.5. Solo
    `{workFolder}` sustituible.
  - Renombrar los headers `## 0.7. Hook: 10-pre-release` → `10-before-version`,
    `### 4.1. Hook: 20-post-build` → `20-after-build`, `### 6.1. Hook: 30-post-changelog`
    → `30-after-changelog`, y las menciones en el cuerpo.
  - En §0.6 "Three points are defined" → "Four".
- **`pv-do/SKILL.md`:**
  - §1.5 tabla: renombrar la fila `10` a `10-before-implementation.md` (la `20` no cambia).
  - Renombrar el header `### 2.0. Hook: 10-before-start` → `10-before-implementation` y las
    menciones (`§top`, "the two hooks", etc.). `20-before-finish` intacto.
- **`pv-design.en.md`:** actualizar las menciones a los nombres viejos de hook (líneas de
  "Customization points" de `pv-do` y `pv-version`, la sección "Workflow diagrams" → "Hook
  nodes", la de `check_version_hooks_seed` en "structural markers", y el árbol de "Full
  folder and file structure") — se hace de una vez con la sección nueva "Project hooks"
  (ver "Documentar el catálogo…").

### 5. `workflow.<skill>.md` — nodos naranja en el diagrama

`pv-design.en.md` "Workflow diagrams" define la notación; los nodos de hook van con
`classDef hook fill:#d9770e,color:#fff` (ver `workflow.do.md` líneas 46-47) y el nodo es
un rombo `{... defines steps?}` → `[Run ... steps in order ...]`.

- `pv-how/workflow.how.md`: dos parejas de nodos (check + run) — una al entrar en el nodo
  "Analyze and write plan.md", otra entre "Assess risk" y "Ask whether to implement".
- `pv-new/workflow.new.md`: una pareja dentro del nodo del paso 5.
- `pv-version/workflow.version.md`: una pareja para `05-before-guardrail` antes del nodo
  del guardrail `implemented/`, y renombrar los nodos de los 3 hooks existentes
  (`10-before-version`, `20-after-build`, `30-after-changelog`).
  **Verificar primero** dónde cae hoy el nodo de `10-pre-release`/`10-before-version` (ver
  decisión en H4).
- `pv-do/workflow.do.md`: renombrar el nodo `10-before-start` → `10-before-implementation`
  (líneas 25-26 del diagrama actual).
- Actualizar la leyenda "Orange nodes — the project's own hook insertion points" si
  enumera los skills.

### 6. Migración de los 4 hooks renombrados en proyectos ya inicializados

El mecanismo **ya existe**: `pv-update`'s `stuff-<subdir>-hook-badslug:<file>` (ver
`audit-context.py` `_check_one_hook_set` + `pv-update/SKILL.md` "fix loop"). Al cambiar los
nombres canónicos en `HOOK_SETS` (paso 3), en cualquier proyecto viejo:

1. `10-before-start.md` tiene el `<NN>` `10` correcto pero ya no coincide con el canónico
   `10-before-implementation.md` → se emite `stuff-do-hook-badslug:10-before-start.md`.
2. `pv-update` lo renombra con `git mv` (o move) al nombre canónico, **contenido intacto**
   → los `### Step` que el equipo hubiera añadido se conservan.
3. Igual para los 3 de `version`.

Qué hay que verificar / ajustar al implementar:
- Que el fix de `badslug` en el flujo de `pv-update` **mueve de verdad** el fichero (no
  solo avisa). Según `SKILL.md` línea ~85 sí (`git mv`, "Contents don't change") — confirmar
  en el código real del fix loop.
- El **texto** del problema (`audit-context.py` línea ~328: "has the right id ... but not
  the canonical name") sirve, pero conviene añadir una frase para el caso
  framework-driven: "el framework renombró este punto de inserción en la versión X".
- El `.template.md` viejo bajo `.claude/skills/<skill>/hooks/` ya no existe (renombrado en
  paso 1), así que `stuff-<subdir>-hook-missing` **no** se dispara para el nombre viejo, y
  el nuevo se reseedearía solo si faltara — pero como `badslug` renombra el que hay, no
  llega a faltar. Verificar que el orden en el fix loop es badslug-antes-que-missing, o que
  ambos convergen.
- Entrada en el changelog del framework: "hooks renombrados: `before-start`→
  `before-implementation`, `pre-release`→`before-version`, `post-build`→`after-build`,
  `post-changelog`→`after-changelog`; `pv-update` los migra automáticamente".

## Convención de variables (fijar ahora, antes de la primera tanda)

Los 4 hooks de alta prioridad se cubren **solo con `{workFolder}` y `{xxxx}`** (`{XXXX}`
para `version`, que ya existe). No hace falta ninguna variable nueva:

- Rutas como `plan.md`, `description.md`, la carpeta de la entrada → el paso del hook las
  compone: `{workFolder}/changes/inProgress/{xxxx}/plan.md`. Documentarlo en cada
  `.template.md` con un ejemplo, para que el equipo no espere una variable dedicada.
- Cualquier otro dato (rama, timestamp, lista de ficheros tocados) → el paso corre su
  propio comando. Esto ya es el contrato actual; no se toca.
- La variable `{changedFiles}` que pedían P1/P3 en `07_future-hooks.md` **no** se
  introduce con esta tanda — es una decisión abierta que solo afecta a propuestas no
  incluidas aquí.

## Convención de numeración `NN` (fijar ahora)

Complementa el catálogo de partículas de arriba (el `<NN>` del nombre `<NN>-<temporal>-<objeto>`).

- `NN` de dos dígitos, orden numérico = orden de ejecución dentro del skill.
- Múltiplos de `10` para los puntos "principales" (`10`, `20`, `30`, `40`… — ya en uso
  en `version`).
- Hueco por debajo (`00`–`09`) y entre medias (`11`–`19`, `21`–`29`…) reservado para
  intercalar puntos futuros sin renumerar. H4 estrena el `05`.
- El `<NN>` **no** codifica `before`/`after` — eso lo dice la partícula temporal. Un
  `before-` y un `after-` del mismo hito llevan `NN` distintos si el skill hace algo entre
  medias (`10-before-analysis` … análisis … no hay `after-analysis` porque el siguiente
  hito ya es `20-after-plan`).
- Esta convención se documenta en `pv-design.en.md` junto con el catálogo de partículas
  — ver "Documentar el catálogo en la doc técnica" más arriba.

## Orden de implementación sugerido

1. **H3 (`pv-new`)** — el más aislado: subdir nuevo, un solo punto, sin bucle, sin
   interacción con `{XXXX}` ni con el riesgo. Sirve de plantilla para validar que la
   mecánica de "subdir nuevo" funciona end-to-end (scaffold + audit + SKILL + workflow).
2. **H1 + H2 (`pv-how`)** — juntos: comparten subdir, tabla de §0.6 y párrafos de cabecera.
   H1 es trivial; H2 aporta el detalle de "leer la mediana de riesgo ya persistida".
3. **H4 (`pv-version`)** — último, porque arrastra la decisión de si se solapa con
   `10-before-version`; conviene resolverla con `workflow.version.md` delante y sin
   bloquear las otras tres.
4. **Renombrado de los 4 existentes + migración (paso 6)** — puede ir en cualquier momento
   de la tanda, pero conviene **junto con H4** (comparten `pv-version/SKILL.md` §0.6,
   `workflow.version.md` y `pv-design.en.md`), para tocar cada fichero una sola vez.

Tras cada cambio: `pv-update` en un proyecto de prueba **inicializado con la versión
anterior** (p. ej. `sandbox-test1/`) debe: (a) reseedear los `.template.md` nuevos sin
tocar los que el proyecto ya tenga con contenido; (b) renombrar los 4 hooks viejos vía
`badslug` conservando sus `### Step`; (c) no emitir `hook-missing`/`badslug` falsos tras
eso. Y `pv-init` en un repo limpio debe crear los subdirs `how/`, `new/` y los 5 ficheros
de `version`/`do` ya con los nombres nuevos.

## Fuera de alcance de este documento

Este documento cubre **solo** los 5 hooks que ya existen (4 renombrados, 1 igual) y los
4 que se van a crear ya (H1–H4). Todo lo demás vive en
[`07_future-hooks.md`](07_future-hooks.md):

- Propuestas de hooks aún sin decidir (P1–P8 y cualquiera nueva).
- El vocabulario completo de `<objeto>` para esas propuestas.
- Semántica de fallo "best-effort", política de reanudación de hooks en bucle, y paso de
  la lista de ficheros al hook (`{changedFiles}`) — decisiones abiertas que solo afectan a
  propuestas no incluidas aquí.
