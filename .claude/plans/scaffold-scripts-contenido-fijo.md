# Mover la creación de ficheros con contenido fijo de las skills a scripts

## Contexto

El framework `pv-*` ya sigue el patrón "el script hace lo mecánico y determinista, la skill
razona". Casi todo lo que era emitir una plantilla estática ya está en scripts Python
(`scaffold-project.py`, `rebuild-index.py`, `init-version-folder.py`, `move-change.py`,
`resolve-path.py`, `render_status.py`…), y la frase *"deterministically and for free in tokens"*
aparece ~10 veces en los `SKILL.md`. `pv-status` es el modelo al que converge todo: el modelo
emite **0 tokens** de contenido de informe, solo repite el stdout del script.

Aun así quedan puntos donde una **skill** todavía hace que el modelo escriba a mano contenido
puramente fijo: frontmatter, labels forzados a inglés literal, headings, esqueletos de sección,
párrafos-plantilla, tablas que nunca cambian. El modelo gasta tokens de salida (y de entrada,
al leer el `*.template.md`) reproduciendo texto que un script escribiría sin coste.

**Objetivo**: que en la fase inicial de cada flujo un script cree el documento base
(estructura fija + valores triviales ya rellenados + huecos marcados) y la skill trabaje
**editando** ese documento en vez de generarlo entero. Mismo contrato que `scaffold-project.py`.

Alcance confirmado con el usuario: **los 6 puntos**. El punto 6 (semillas `00-glossary.md` /
`00-namespace.md`) lo **absorbe este plan**; en `pv-internal-doc-technical-optimizacion_impl-2-6-7-13-14-15.md`
§13/§15 se sustituyen las líneas que hoy dicen "semilla en `scaffold-project.py`" por una
referencia a este plan.

---

## Inventario — dónde el modelo aún emite contenido fijo

### Ya resuelto (patrón a replicar)

| Punto | Script | Contenido fijo sin coste de tokens |
|---|---|---|
| scaffolding de `pv-init` | `pv-init/scripts/scaffold-project.py` | subcarpetas de `workFolder` + `.gitkeep`, `001-overview.md` (constante `OVERVIEW_TEMPLATE`), copia `pv.py`, delega `INDEX.md` a `rebuild-index.py` |
| numeración de cambios | `pv-internal-workflow/scripts/next-change-number.py` | `xxxx` |
| mover carpetas | `move-change.py` | inProgress→implemented→closed |
| índices de docs | `pv-internal-doc-files/scripts/rebuild-index.py` | **única fuente de `INDEX.md`**, nunca a mano |
| carpeta de versión | `pv-version/scripts/init-version-folder.py` | `versions/{XXXX}/{files,docs}/` |
| resolución de rutas | `pv-init/scripts/resolve-path.py` | ninguna skill parsea `pv-context.json` |
| informes de estado | `pv-status/scripts/render_status.py` etc. | el modelo repite stdout, 0 tokens propios |

### Pendiente — la skill hace que el modelo teclee la plantilla

Ranking por tokens fijos de salida × frecuencia (confirmado por exploración del repo):

| # | Ubicación | Contenido fijo que el modelo emite hoy | Tokens salida / vez | Frecuencia |
|---|---|---|---|---|
| **1** | `pv-how` §3.6 — `plan.md` desde `PLAN.template.md` | esqueleto `(a)`–`(f)` (2 labels + 3-6 headings inglés literal) **+**, si el usuario pide detalle de riesgo, la sección `(f)`: **tabla fija de 9 factores + tabla-leyenda fija de 8 filas Value/Meaning** (líneas 37-59 del template, copiadas verbatim) | ~40 esqueleto · **~250 la sección (f)** | cada `pv-how`; la (f) solo si piden detalle |
| **2** | `pv-internal-workflow` `action=create` — `history.md` desde `history.template.md` | cabecera `# Prompt history — {xxxx}` **+ blurb explicativo fijo de 2 párrafos** ("Historical information about the analysis process… Exclusive use of `pv-new` and `pv-fix`…") **+** `## {date} — initial session`. Lo único variable: el `promptOriginal` pegado | **~70** | cada `pv-new` / `pv-fix` (no trivial) / `pv-fix` fast |
| **3** | `pv-internal-workflow` `action=create` — `description.md` desde `description.template.md` | 4 labels forzados a inglés (`**Name**`, `**Code**`, `**Type**`, `**Creation date**`) + 2 headings (`## Full description`, `## Technical notes`) + comentarios-guía `<...>`. `Code`/`Type`/`Creation date` son valores triviales | ~30 | cada entrada |
| **4** | `pv-internal-changelog` §4 — `changelog.md` desde `changelog.template.md` | `# Version {XXXX} — {date}` + línea de conteos `New: N · Changed: N · Removed: N · Fixes: N` + hasta 4 headings `## New/Changed/Removed/Fixes` | ~20 | cada `pv-version` |
| **5** | `pv-todo` §3 — `description.md` desde `pv-todo/description.template.md` | `# Idea: {code}` + 4 headings (`## Idea`, `## Code`, `## Creation date`, `## Notes`), sin bold/sin `:` (regex de `list_todo.py`). `Code`/`Creation date` triviales | ~15 | cada idea `pv-todo` |
| **6** | semillas `00-glossary.md` / `00-namespace.md` (previstas en `_impl-2-6-7-13-14-15.md` §13/§15) | cabecera + convención de notación / convención de orden de segmentos + ejemplo comentado | ~480-520 | 1ª vez por repo |
| — | `pv-version` §3 — `how-to-compile-version.md` | 3 headings (`## Command(s) to run`, `## Generated file(s)`, `## Notes`) + párrafo de cabecera. Cuerpo = comandos del proyecto (razonado) | ~20 (headings) | 1ª vez por repo |
| — | `pv-do` §2.1 caso legacy — `FEATURES.md` desde `pv-do/FEATURES.template.md` | `# Features` + `## [area]` + `### [feature]` + `- **Available in**:` + `- **Code**:` | ~15 | por entrada, solo proyectos sin migrar |

Nota: `pv-do` §2.1 (caso carpeta) **no** es contenido fijo — el cuerpo lo redactan
`pv-internal-doc-technical` / `-style` / `-features` y es razonamiento sobre el proyecto; el
`# NNN — title` + `**Area**:` ya lo escribe `pv-internal-doc-files`. Se deja fuera.

---

## Estimación de ahorro de tokens

**Metodología**: contar solo el texto **fijo** (independiente del proyecto) que hoy el modelo
emite como *output*. ≈ 1 token ≈ 4 chars para inglés técnico con markdown; tablas y `<...>`
tokenizan peor (~3,5 chars/token). El framework rehúsa cifras sin medir (regla 8 del doc de
ideas) — esto es una estimación de orden de magnitud, no un dato medido.

### Ahorro de salida por invocación

| Punto | Tokens de salida fijos ahorrados / invocación |
|---|---|
| 1. `pv-how` `plan.md` esqueleto | **~40** siempre |
| 1. `pv-how` `plan.md` sección (f) tablas de riesgo | **~250** cuando el usuario pide detalle de riesgo — *el mayor bloque estático fijo que emite una skill de flujo* |
| 2. `pv-internal-workflow` `history.md` preámbulo | **~70** por entrada |
| 3. `pv-internal-workflow` `description.md` esqueleto | **~30** por entrada |
| 4. `pv-internal-changelog` `changelog.md` cabecera | **~20** por versión |
| 5. `pv-todo` `description.md` esqueleto | **~15** por idea |
| 6. semillas glosario/namespace | **~500** una vez por repo |

### Ahorro por flujo típico

- **`pv-new` / `pv-fix`** (puntos 2+3): **~100 tokens de salida** por entrada. Flujo más
  frecuente del framework → el ahorro **acumulado** real vive aquí.
- **`pv-how`** (punto 1): **~40 tokens siempre**, **~290 si se pide detalle de riesgo**.
- **`pv-version`** (punto 4): ~20 por versión.
- **`pv-todo`** (punto 5): ~15 por idea.
- **`pv-init`** (punto 6): ~500 una vez por proyecto.

### Ahorro secundario (igual de importante que el de salida)

1. **Entrada**: hoy la skill además **lee** el `*.template.md` (mismo texto otra vez como
   input). Si la plantilla pasa a ser constante Python en el script, la skill ya **no lee el
   `*.template.md` en absoluto** → se ahorra ~la misma cantidad de tokens de **entrada** por
   invocación (~350 en `pv-how` con `PLAN.template.md` de 60 líneas, ~230 en `create` sumando
   los dos templates, etc.).
2. **Coste de salida vs. entrada**: los tokens de salida cuestan ~4-5× y se generan más
   despacio → el ahorro **percibido** (latencia) es mayor que el número bruto.
3. **Drift de formato eliminado**: hoy el modelo puede parafrasear sin querer un heading fijo
   (`## Full description` → `## Description`, o traducir un label `[[[...]]]`) y romper el
   parser de `filter_status.py` / `list_todo.py` / `extract_description` silenciosamente. Un
   script lo escribe siempre byte a byte igual — desaparece una clase entera de bugs.

### Total realista por tarea completa `pv-fix` → `pv-how` → `pv-do`

- **~150-400 tokens de salida** + **~600 de entrada** ahorrados (~750-1.000 tokens/tarea; el
  rango alto si en `pv-how` se pide el detalle de riesgo).
- Más el ~500 puntual de `pv-init` por proyecto.

**Conclusión**: el ahorro por invocación individual es modesto (~15-290 tokens de salida), pero
(a) se concentra en los dos flujos más repetidos (`pv-new`/`pv-fix` y `pv-how`), (b) duplica su
valor al eliminar también la lectura del `*.template.md`, (c) elimina bugs de drift de formato,
y (d) completa un patrón que el framework **ya aplica** en la práctica totalidad de sus pasos
mecánicos. Coste de implementación bajo: scripts pequeños, deterministas, sin dependencias, con
un contrato ya probado (`scaffold-project.py`).

---

## Enfoque recomendado

Para cada punto pendiente, crear un script `scaffold-*.py` en `scripts/` de la skill **dueña
del formato** (no un script compartido — añadiría acoplamiento entre skills sin ganancia),
siguiendo el patrón exacto de `scaffold-project.py`:

- **Contrato de entrada**: recibe por argumentos solo lo que la skill ya tiene resuelto sin
  razonar (`--xxxx`, `--type`, `--date`, `--code`, `--name`, `--xxxx` de versión…); lee de
  `.claude/pv-context.json` lo demás (`workFolder`, `numberWidth`, `changes.language`).
- **Escribe** el fichero con: estructura fija + valores triviales ya rellenados (`Code`,
  `Creation date`, `Type`) + los huecos que la skill sí debe razonar marcados con un
  placeholder inequívoco (mantener los `<...>` actuales, que ya son la convención).
- **Idempotente y contenido**: si el fichero ya existe, no lo toca y lo reporta `skipped`
  (igual que `scaffold-project.py`); `resolve_inside_repo` para contención dentro del repo.
- **Salida**: un único JSON en stdout, p. ej. `{path, status, fieldsToFill: [...]}`.
- La **plantilla** deja de vivir en un `*.template.md` leído por el modelo y pasa a ser una
  constante Python en el script (como `OVERVIEW_TEMPLATE`). El `*.template.md` se **elimina**;
  si su prosa-guía tiene valor documental para humanos, se reduce a eso y se marca como no
  leído por ninguna skill.
- El `SKILL.md` cambia de *"crea el fichero siguiendo la plantilla X"* a *"ejecuta
  `scaffold-X.py`; luego rellena los campos que reporta en `fieldsToFill`"*.

### Marker convention

Se mantiene la convención `[[[...]]]` de `pv-design.en.md` (labels/headings fijos en inglés
siempre). El script escribe esos ya sin corchetes y en inglés — de hecho **mejor** que el
modelo, que hoy tiene que acordarse de no traducirlos. `pv-update`'s `marker-missing:*` check
sigue teniendo sentido para ficheros anteriores al cambio.

### Sección (f) de `plan.md` (el mayor bloque)

`scaffold-plan.py` incrusta la tabla-leyenda Value/Meaning (8 filas, 100% estática) como
constante. Cuando el usuario pide el detalle de riesgo, la skill solo añade la tabla de 9
factores **con los valores** que `pv-internal-tech-risks` devolvió — no la plantilla vacía.

---

## Ficheros a crear / modificar

| Acción | Fichero |
|---|---|
| **Nuevo** | `.claude/skills/pv-how/scripts/scaffold-plan.py` (punto 1 — incluye la leyenda (f)) |
| **Nuevo** | `.claude/skills/pv-internal-workflow/scripts/scaffold-entry.py` (puntos 2+3 — `description.md` + `history.md` en una pasada) |
| **Nuevo** | `.claude/skills/pv-internal-changelog/scripts/scaffold-changelog.py` (punto 4 — cabecera + headings de sección; la skill intercala entradas clasificadas) |
| **Nuevo** | `.claude/skills/pv-todo/scripts/scaffold-idea.py` (punto 5) |
| **Ampliar** | `pv-init/scripts/scaffold-project.py` — añadir semillas `00-glossary.md` y `00-namespace.md` (punto 6, con sus constantes-plantilla); también la semilla `FEATURES.md` del caso legacy si se decide cubrirlo |
| **Editar** | `pv-internal-workflow/SKILL.md` §create.2 — "ejecuta `scaffold-entry.py`, luego rellena **Full description** y pega `promptOriginal`" |
| **Editar** | `pv-how/SKILL.md` §3.6 y §3.1 — "ejecuta `scaffold-plan.py`; edita el campo **Risk** y, si se pide, añade la tabla de 9 factores con valores" |
| **Editar** | `pv-todo/SKILL.md` §3; `pv-internal-changelog/SKILL.md` §4 |
| **Eliminar** | `PLAN.template.md`, `pv-internal-workflow/description.template.md`, `history.template.md`, `changelog.template.md`, `pv-todo/description.template.md` → constantes en sus scripts |
| **Editar** | `pv-internal-doc-technical-optimizacion_impl-2-6-7-13-14-15.md` §13/§15/§17 — sustituir "semilla en `scaffold-project.py`" por "creado por `scaffold-project.py` según el plan de scaffolding (`scaffold-scripts-contenido-fijo.md`)"; §15.4 y §15.8 igual |
| **Versionar** | `/dev-generate-version` al final — todos los `pv-*/SKILL.md` tocados a una versión consistente |

---

## Verificación

1. **`scaffold-entry.py`**: ejecutar `pv-new` con una petición de prueba; `diff` de
   `inProgress/{xxxx}/description.md` y `history.md` contra una entrada creada a mano con las
   plantillas viejas → byte-idénticos salvo los huecos. Confirmar que
   `filter_status.py`'s `extract_description` sigue parseando `## Full description` y que el
   preámbulo de `history.md` está intacto.
2. **`scaffold-plan.py`**: `/pv-how` sobre esa entrada; confirmar que `plan.md` tiene el
   esqueleto correcto, que al pedir detalle de riesgo la tabla de 9 factores sale **con
   valores** y la leyenda de 8 filas intacta, y que `pv-do` lee `plan.md` sin fricción.
3. **`scaffold-changelog.py`**: `/pv-version` en un repo de prueba con entradas en `closed`;
   `diff` del `changelog.md` contra el formato viejo; conteos correctos.
4. **`scaffold-idea.py`**: `/pv-todo` con una idea; `diff` del `description.md`; confirmar que
   `list_todo.py`'s regex sigue casando los 4 headings.
5. **`scaffold-project.py` ampliado**: correr en `test/previo-sdd/` (fixture); verificar que
   `00-glossary.md` / `00-namespace.md` se crean solo si no existen (`status: skipped` en 2ª
   pasada) y que su contenido casa con lo que `_impl-2-6-7-13-14-15.md` espera.
6. **Regresión de tokens**: comparar el transcript de un `pv-fix` → `pv-how` → `pv-do`
   completo antes/después (el harness reporta tokens por turno) contra la estimación de arriba.
7. **`pv-update`**: `audit-context.py`'s `marker-missing:*` sigue funcionando sobre ficheros
   antiguos; ningún script tocado rompe `test/pv-test.py --testconfig` si `pv.py` lo consume.
8. **Coherencia con `_impl-2-6-7-13-14-15.md`**: `grep` de "semilla en `scaffold-project.py`"
   en `.claude/plans/` → 0 resultados tras la edición; las nuevas referencias apuntan a este
   plan.

---

## Notas / decisiones

- **Prioridad por ROI**: punto **1 (sección f)** > **2** > **3** > 4 > 5 > 6. Los puntos 1-3
  son ~el 80% del ahorro acumulado real.
- **`_impl-2-6-7-13-14-15.md`**: este plan y ese comparten el punto 6. Acordado: lo implementa
  **este** plan (creación de las semillas en `scaffold-project.py`); el otro plan solo lo
  referencia y aporta el *contenido* exacto de las semillas (cabecera, convenciones, ejemplos)
  desde sus §13.5 / §15.5. Ejecutarlos coordinados: primero este define el mecanismo, luego el
  otro rellena qué dicen las semillas.
- **Caso legacy `FEATURES.md`** y `how-to-compile-version.md`: ROI bajísimo (solo 1ª vez por
  repo, y el 2º es casi todo contenido razonado). Se pueden dejar como están o cubrir de paso
  al tocar `scaffold-project.py` — sin script nuevo.
- **No** convertir a script el contenido de `pv-do` §2.1 caso carpeta ni los informes de
  `pv-status` (ya resueltos / ya son razonamiento puro).
