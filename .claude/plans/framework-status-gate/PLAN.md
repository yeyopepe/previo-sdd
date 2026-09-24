# Framework status gate: script único de verificación + capacidad de instalar desde `pv-update`

## Index

- [Objective](#objective)
- [Context: current state](#context-current-state)
- [Design](#design)
  - [1. `check-framework-status.py` — script de verificación, propiedad de `pv-update`](#1-check-framework-statuspy--script-de-verificación-propiedad-de-pv-update)
  - [2. Migración de las 9 skills públicas al script único](#2-migración-de-las-9-skills-públicas-al-script-único)
  - [3. Conteo exacto de skills instaladas](#3-conteo-exacto-de-skills-instaladas)
  - [4. `pv-update install` — nueva capacidad de instalación/actualización](#4-pv-update-install--nueva-capacidad-de-instalaciónactualización)
  - [5. Ejemplos de prompts `/pv-update`](#5-ejemplos-de-prompts-pv-update)
- [Fuera de alcance](#fuera-de-alcance)
- [Tareas](./TASKS.md)
- [Reviews](#reviews)

## Objective

Hoy, nueve skills públicas del framework (`pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-status`,
`pv-todo`, `pv-version`, `pv-review-architecture`, `pv-review-doc-tech`) repiten, palabra
por palabra o con una redacción equivalente, el mismo bloque de prosa en su paso 0 para
comprobar que `.claude/pv-context.json` existe y que la versión instalada del framework
está verificada (`frameworkStatus.lastVerifiedVersion` / `blocked`). Esa verificación:

1. Debe pasar a apoyarse en un **script propio de `pv-update`**, en vez de en una
   comparación hecha "a mano" por el modelo leyendo dos ficheros. Si el script no existe
   en su ubicación esperada, se informa al usuario de que el framework no parece estar
   bien instalado y debe instalar la última versión — ninguna skill `pv-*` puede
   continuar su trabajo sin pasar antes por este paso.
2. Debe ampliarse para contar cuántas skills `pv-*` hay instaladas en el proyecto y
   compararlo contra el número exacto que la versión actual del framework declara. Un
   conteo distinto informa al usuario de que Previo no parece estar bien instalado, o que
   puede haber copiado skills sueltas del framework fuera de su uso previsto, y debe
   instalar la última versión. Igual que el punto 1, ninguna skill `pv-*` puede continuar
   sin pasar por esta comprobación.

Como consecuencia directa de que el punto 1 y 2 siempre reenvían al usuario a
`pv-update`, esta revisión detectó que `pv-update` en sí mismo **no puede hoy instalar ni
actualizar nada** — solo audita/repara la configuración ya presente en disco. Se añade
por tanto una tercera pieza: una capacidad explícita de `pv-update` (`/pv-update install`)
para instalar la versión actual o una superior (nunca una inferior) reutilizando
`install.sh`/`install.ps1`, que es el único lugar del repo con lógica de descarga desde
GitHub Releases.

## Context: current state

- Las 9 skills públicas (`pv-do/SKILL.md`, `pv-fix/SKILL.md`, `pv-how/SKILL.md`,
  `pv-new/SKILL.md`, `pv-status/SKILL.md`, `pv-todo/SKILL.md`, `pv-version/SKILL.md`,
  `pv-review-architecture/SKILL.md`, `pv-review-doc-tech/SKILL.md`) tienen en su paso 0 un
  párrafo con esta misma comprobación — idéntico palabra por palabra en las primeras 7,
  con una redacción más corta pero funcionalmente equivalente en las dos últimas ("Check
  the framework version the same way every other `pv-*` skill does..."): leer
  `metadata.version` del frontmatter de `pv-init/SKILL.md`, compararlo con
  `framework.frameworkStatus.lastVerifiedVersion` de `pv-context.json`, y parar si no
  coincide, si `frameworkStatus` falta, o si `blocked` es `true`.
- `pv-update/scripts/audit-context.py` ya implementa (Check A, líneas ~1102-1125) esa
  misma comparación de versión, más un chequeo de mayoría de versión entre skills
  (`skill-version-mismatch:*`, líneas ~1066-1100) — pero **no** un conteo exacto contra un
  número esperado; solo detecta que una skill se desvía de la mayoría de las demás, no que
  falten o sobren skills completas.
- `pv-update/scripts/mark-verified.py` ya escribe `frameworkStatus` (`--clear` / `--block`
  / `--confirm-downgrade`) tras una auditoría.
- `install.sh` / `install.ps1` (raíz del repo) ya soportan instalar la última versión o un
  tag concreto (positional arg / `$env:PREVIO_VERSION`), consultando la API de GitHub
  Releases (`/releases/latest` o `/releases/tags/<tag>`), y ya distinguen primera
  instalación vs. actualización. Es la única lógica de descarga existente en el repo.
- `tools/set-skill-versions.py` es el script que `dev-generate-version` usa para escribir
  `metadata.version` en todos los `pv-*/SKILL.md` al cortar una release — es el punto
  natural para mantener también sincronizado cualquier valor derivado del número de
  skills, si se decide declararlo en vez de derivarlo en tiempo de ejecución.
- Hoy existen exactamente **23 carpetas** bajo `.claude/skills/pv-*/`, todas en
  `0.9.8b6` y todas con `SKILL.md` (incluye `pv-review-architecture` y
  `pv-review-doc-tech`, ver arriba).

## Design

### 1. `check-framework-status.py` — script de verificación, propiedad de `pv-update`

Nuevo script en `pv-update/scripts/check-framework-status.py`. Es deliberadamente
**distinto** de `audit-context.py`: mientras `audit-context.py` es el auditor completo y
lento (markers, `.metadata.json`, namespace, hooks...) que solo corre bajo demanda
(`/pv-update`), este nuevo script es el subconjunto barato que **cada una de las 9 skills
públicas ejecuta en cada invocación propia**, así que debe ser rápido y no debe
duplicar los chequeos caros del auditor completo.

**Contrato:**

```
python .claude/skills/pv-update/scripts/check-framework-status.py
```

Sin argumentos. Imprime un único JSON por stdout, nunca lanza excepción sin capturar
(los fallos esperables — JSON roto, framework no inicializado — se reportan como datos,
no como traceback). Forma:

```json
{
  "ok": true,
  "problem": null,
  "message": null
}
```

o, en caso de fallo:

```json
{
  "ok": false,
  "problem": "context-missing | context-invalid-json | blocked | version-mismatch | skill-count-mismatch",
  "message": "texto explicativo listo para mostrar al usuario",
  "expected": "...",
  "actual": "..."
}
```

Comprobaciones, en este orden (para en la primera que falle — no acumula varios
problemas como sí hace `audit-context.py`, porque el propósito aquí es un gate binario
rápido, no un informe):

1. **`context-missing`** — `.claude/pv-context.json` no existe. Mensaje: el framework no
   está inicializado, ejecuta `pv-init`.
2. **`context-invalid-json`** — existe pero no parsea. Mensaje: la configuración está
   rota, ejecuta `/pv-update`.
3. **`blocked`** — `framework.frameworkStatus.blocked` es `true`. Mensaje incluye
   `blockedReason` si está presente. **Va antes que `version-mismatch`** a propósito:
   `mark-verified.py --block` (única forma en que `blocked` llega a `true`) deja
   `lastVerifiedVersion` intacto mientras bloquea, así que siempre que `blocked` es
   `true` la versión real ya es distinta de `lastVerifiedVersion` — si `version-mismatch`
   fuera antes, `blocked` nunca llegaría a evaluarse, porque el script para en el primer
   fallo. Comprobar `blocked` primero da al usuario el mensaje específico (con
   `blockedReason`) en vez del genérico de mismatch.
4. **`version-mismatch`** — mismo Check A que ya hace `audit-context.py` (leer
   `metadata.version` de `pv-init/SKILL.md`, comparar con
   `framework.frameworkStatus.lastVerifiedVersion`; ausencia de `frameworkStatus`
   cuenta como mismatch). Reutiliza la misma lógica de lectura de frontmatter que ya
   existe en `audit-context.py`/`mark-verified.py` (duplicada aquí a propósito, mismo
   patrón que ya siguen esos dos scripts — cada script `pv-*` es autocontenido).
5. **`skill-count-mismatch`** — ver sección 3 más abajo.

**Cuando el script no existe en su ubicación esperada** (`.claude/skills/pv-update/scripts/check-framework-status.py`):
esto es justo el caso "el framework no parece bien instalado" que pide el punto 1 del
objetivo — no es un problema que el script mismo pueda reportar (no puede ejecutarse si
no existe). La skill que lo invoca (paso 0 de las 9 skills públicas) debe comprobar la
existencia del fichero *antes* de intentar ejecutarlo y, si falta, mostrar directamente
el mensaje de instalación sin más rodeo (ver sección 2).

### 2. Migración de las 9 skills públicas al script único

El párrafo duplicado (o su equivalente funcional) del paso 0 en `pv-do`, `pv-fix`,
`pv-how`, `pv-new`, `pv-status`, `pv-todo`, `pv-version`, `pv-review-architecture`,
`pv-review-doc-tech` se sustituye, en las 9 skills, por el mismo texto (evitando volver a
duplicar prosa distinta en cada una):

> Antes de continuar, comprobar que `.claude/skills/pv-update/scripts/check-framework-status.py`
> existe. Si no existe, informar al usuario de que el framework no parece estar bien
> instalado y que debe instalar la última versión (ver [sección 5](#5-ejemplos-de-prompts-pv-update)
> para el prompt exacto) — parar ahí, sin continuar el trabajo de esta skill.
>
> Si existe, ejecutarlo (`python .claude/skills/pv-update/scripts/check-framework-status.py`)
> y leer su JSON. Si `ok` es `false`, mostrar `message` al usuario y parar — ninguna skill
> `pv-*` puede continuar su trabajo sin que este paso pase con `ok: true`.

Esto **reemplaza por completo** el párrafo equivalente en las 9 skills — tanto la forma
larga ("Additionally, before continuing, check that the framework's installed version is
verified: read `metadata.version`...") de las 7 primeras, como la forma corta ("Check the
framework version the same way every other `pv-*` skill does...") de
`pv-review-architecture`/`pv-review-doc-tech` — no coexisten varias formas de comprobar lo
mismo.

La comprobación de existencia de `.claude/pv-context.json` que cada una de las 9 skills
ya hace *antes* de este párrafo (p. ej. "If `.claude/pv-context.json` doesn't exist...")
se mantiene sin cambios — sigue siendo el primer chequeo, específico de "el framework no
se ha inicializado nunca en este proyecto" vs. "el framework está instalado pero algo no
cuadra", que es lo que cubre el nuevo script.

### 3. Conteo exacto de skills instaladas

El número exacto de skills `pv-*` que la versión actual del framework instala se declara
como una **constante hardcodeada dentro de `check-framework-status.py`**
(`EXPECTED_SKILL_COUNT = 22`), no en el frontmatter de ningún `SKILL.md` ni en un asset
aparte — un único número, en el único script que lo necesita en tiempo de ejecución en el
proyecto consumidor.

El script cuenta `len(list((root / ".claude/skills").glob("pv-*")))` (carpetas, no
ficheros — mismo patrón `glob("pv-*/SKILL.md")` que ya usa `audit-context.py`, pero
contando directorios) y lo compara contra `EXPECTED_SKILL_COUNT`. Si no coincide, emite
`skill-count-mismatch` con `expected`/`actual` y un mensaje explicando las dos causas
posibles (instalación incompleta/corrupta, o skills sueltas copiadas de Previo sin
soporte fuera del framework) y la recomendación de instalar la última versión.

**Mantenimiento de la constante**: `tools/set-skill-versions.py` (usado por
`dev-generate-version` en cada corte de release) se amplía para, además de reescribir
`metadata.version` en cada `SKILL.md`, recalcular
`len(glob("pv-*/SKILL.md"))` sobre el propio repo en ese momento y reescribir
`EXPECTED_SKILL_COUNT` en `pv-update/scripts/check-framework-status.py` para que
coincida — así el número nunca se declara a mano ni puede desincronizarse de las skills
que la release realmente contiene.

### 4. `pv-update install` — nueva capacidad de instalación/actualización

`pv-update` gana un segundo modo de invocación, explícito y separado del audit-only por
defecto (que sigue sin red y sin tocar nada fuera de `pv-context.json`):

**Nuevo asset**: `pv-update/scripts/install-framework.py`, wrapper que detecta el
sistema operativo (`platform.system()`) e invoca el script que corresponda a esa
plataforma — `install.ps1` (vía `powershell.exe -File`) en Windows, `install.sh` (vía
`sh`) en cualquier otro caso (Linux, macOS) — nunca ambos ni una elección basada en qué
binarios estén disponibles en el `PATH`, solo en el SO detectado. La lógica de descarga
real (tarball, sincronizado de `pv-*/`, `pv.py`, changelog) no se reimplementa aquí, se
delega íntegramente en esos dos scripts existentes, exactamente como pide el objetivo
del usuario.

**`owner/repo` de GitHub**: hoy `yeyopepe/previo-sdd` solo vive hardcodeado, por
duplicado, como `REPO=` en `install.sh` e `install.ps1` — `pv-context.json`/`schema.json`
no lo guarda en ningún campo. Para las llamadas propias a la API de Releases (ver más
abajo: resolver última oficial + pre-release más reciente antes de invocar el script de
plataforma), `install-framework.py` declara su **propia constante `REPO = "yeyopepe/previo-sdd"`**
— tercera copia hardcodeada, mismo patrón ya seguido en este repo (cada script `pv-*` es
autocontenido; `check-framework-status.py` hace lo mismo con `EXPECTED_SKILL_COUNT`) — no
se introduce un nuevo origen de verdad ni se intenta leer el valor de `install.sh`/`.ps1`
en tiempo de ejecución.

**Contrato:**

```
python .claude/skills/pv-update/scripts/install-framework.py [--version <tag>]
```

- **Antes de decidir nada**, el script consulta GitHub Releases para informar al usuario,
  independientemente de si luego instala algo: `GET /repos/{repo}/releases/latest`
  (la última release **oficial** — GitHub excluye pre-releases de este endpoint por
  diseño) y `GET /repos/{repo}/releases?per_page=1` (**la última release publicada en
  el repo, sea oficial o pre-release** — GitHub devuelve las releases siempre ordenadas
  de más a menos reciente independientemente de su tipo, así que este segundo endpoint
  nunca filtra por `prerelease`, a diferencia del primero). Si el `tag_name` de este
  segundo resultado difiere del de `/releases/latest` **y** su campo `prerelease` es
  `true`, eso significa que existe una pre-release más nueva que la última oficial, y se
  informa de ella. Ambos datos —versión oficial más reciente, y esa pre-release más
  reciente cuando existe— se muestran siempre al usuario antes de instalar nada, aunque
  el usuario haya pedido explícitamente una versión concreta: es información, no una
  pregunta a responder.
- La pre-release se informa **sin recomendarla** — mensaje neutro tipo "hay una
  pre-release `X.Y.Zb1` disponible, pero no se recomienda para uso normal por su
  estabilidad" — nunca se instala por defecto ni se ofrece como opción destacada frente
  a la oficial; el usuario solo la obtiene si la pide explícitamente por `--version`.
- Sin `--version`: instala la última release **oficial** (`install.sh`/`.ps1` sin
  argumento de tag ya resuelven exactamente esto — `/releases/latest` excluye
  pre-releases). Nunca instala una pre-release por defecto, ni aunque sea más reciente
  que la oficial.
- Con `--version <tag>`: antes de invocar el script de instalación, resuelve la versión
  actual instalada (mismo `read_skill_version` sobre `pv-init/SKILL.md`) y la compara con
  `<tag>` (parseo semver ya existente en `audit-context.py`, `parse_version`). **Si
  `<tag>` no matchea el formato `X.Y.Z[sufijo]` que `parse_version` espera** (devuelve
  `None` — typo, nombre de rama, cualquier string que no sea una versión del framework),
  **mismo rechazo duro que el caso de downgrade**: el script termina con error sin
  invocar `install.sh`/`.ps1`, explicando que `<tag>` no tiene forma de versión válida y
  que por tanto no se puede verificar que sea igual o superior a la instalada — nunca se
  delega la comparación al script de plataforma ni se asume que es válido solo porque
  GitHub podría resolverlo como tag. **Si `<tag>` sí parsea pero es inferior a la
  instalada, rechazo duro**: el script termina con error,
  mensaje explicando que `pv-update install` nunca hace downgrades (y que instalar una
  versión inferior a mano requiere ejecutar `install.sh`/`install.ps1` directamente,
  fuera de este flujo asistido) — no hay flag de escape para forzarlo. **Esto es fricción
  deliberada contra un downgrade accidental dentro del flujo asistido (p. ej. un
  `--version` mal tecleado), no una prohibición real de hacer downgrade**: un downgrade
  intencional sigue siendo alcanzable ejecutando `install.sh`/`install.ps1` a mano, y ese
  camino ya termina en el mecanismo existente de `audit-context.py`
  (`version-check-downgrade` + `mark-verified.py --confirm-downgrade`, ver Context) que
  lo detecta y lo confirma sin bloqueo permanente — este plan no cambia ni sustituye ese
  mecanismo, solo evita que se dispare por accidente desde el flujo asistido. Si `<tag>`
  resulta ser una pre-release (su release en GitHub tiene `prerelease: true`), el script
  procede igualmente (el usuario la pidió explícitamente) pero antes emite el mismo aviso
  de riesgo no vinculante del punto anterior.
- Igual o superior a la instalada (incluida la reinstalación de la misma versión):
  procede, invocando el script de plataforma correspondiente con el tag resuelto.
- Al terminar con éxito, no hace el `mark-verified.py --clear` por sí mismo — el flujo
  normal de `pv-update` (auditoría) es quien lo hace, y el modo `install` debe indicarle
  al usuario que ejecute `/pv-update` (modo audit) a continuación para verificar/reparar
  la configuración tras la actualización — mismo mensaje que ya imprime
  `install.sh`/`.ps1` al terminar ("You're updating from a previous version: run
  /pv-update").

**Nueva sección en `pv-update/SKILL.md`** (después del flujo de auditoría existente,
como un modo alternativo de entrada, no como parte de `workflow.audit.md`):

- Trigger: el usuario pide explícitamente instalar/actualizar el framework (ver
  ejemplos en la sección 5), o el propio audit, al reportar `version-check-outdated`,
  puede sugerir (no ejecutar automáticamente) invocar este modo.
- Determina si el usuario quiere la última versión o una concreta (pregunta si no está
  claro por el prompt).
- Ejecuta `install-framework.py` con el `--version` resuelto (u omitido para "latest").
  Antes de instalar nada, el script ya habrá impreso la última versión oficial y, si
  existe, la pre-release más reciente — la skill muestra siempre ambos datos al usuario
  (con el aviso de riesgo no vinculante sobre la pre-release), incluso cuando el usuario
  pidió una versión concreta y no pregunta por esto explícitamente.
- Si el script rechaza por downgrade, muestra el motivo tal cual lo devuelve el script,
  sin intentar reinterpretarlo ni ofrecer forzarlo.
- Al terminar con éxito, recuerda al usuario ejecutar `/pv-update` (modo audit) para
  verificar/reparar la configuración.

**Nuevo diagrama** `workflow.install.md` (mismo patrón de los demás `workflow.*.md`:
fuente de verdad del flujo, con nodos `[Text]` / `[INFO: ...]` / `[ASK: ...]` /
`{decisión}`), independiente de `workflow.audit.md` — cubre: consultar y mostrar última
versión oficial + pre-release más reciente (si existe) → resolver versión objetivo →
comparar con la instalada → si es inferior, informar y terminar → si es una pre-release
pedida explícitamente, avisar del riesgo sin bloquear → invocar `install-framework.py` →
informar resultado y recordar `/pv-update`.

### 5. Ejemplos de prompts `/pv-update`

Para que quede documentado qué frase del usuario dispara cada comportamiento (y para
usar en `pv-update/SKILL.md` como guía de qué reconocer), estos son los casos:

| Prompt del usuario | Comportamiento disparado |
|---|---|
| `/pv-update` (sin argumentos) | Modo audit por defecto: ejecuta `audit-context.py`, repara lo que puede, reporta. Sin red, sin instalar nada. |
| "check the framework" / "revisa la configuración de Previo" / "¿está todo bien configurado?" | Modo audit (mismo que el anterior — invocación por lenguaje natural, no solo por el slash command). |
| `/pv-update install` / "actualiza Previo a la última versión" / "instala la última versión del framework" | Modo install, sin `--version`: resuelve `latest` vía `install.sh`/`.ps1`, instala si es ≥ la actual. |
| `/pv-update install 1.0.2` / "instala la versión 1.0.2 de Previo" | Modo install con `--version 1.0.2`: instala si `1.0.2` ≥ la instalada; si no, rechazo duro. |
| `/pv-update install 0.9.5` (siendo `0.9.8b6` la instalada) | Modo install, rechazo duro: informa que `0.9.5` es inferior a la instalada y que `pv-update install` no hace downgrades — no instala nada. |
| Otra skill `pv-*` detecta en su paso 0 que `check-framework-status.py` no existe | Fallback: la skill informa directamente (sin invocar `pv-update`, porque no hay script que ejecutar) de que el framework no parece bien instalado y sugiere `/pv-update install` para reinstalar la última versión. |
| Otra skill `pv-*` detecta `version-mismatch` / `blocked` / `skill-count-mismatch` vía `check-framework-status.py` | La skill muestra el `message` del script y redirige a `/pv-update` (modo audit) — mismo mensaje para los tres casos, tal como se confirmó en el diseño. |

## Fuera de alcance

- Cualquier mecanismo de downgrade asistido (ver sección 4 — rechazo duro sin excepción,
  confirmado explícitamente en el diseño).
- Cambiar qué comprueba `audit-context.py` más allá de lo ya descrito — el nuevo script
  de la sección 1 es un subconjunto rápido, no un reemplazo del auditor completo.
- Instrumentar el conteo de skills o el gate de versión en skills internas
  (`pv-internal-*`) ni en `pv-init`/`pv-update` mismas — por diseño, ellas no pasan por
  este paso 0 (son las que bootstrapean o reparan el propio framework). `pv-review-*` **sí**
  entra en el alcance de la migración (ver sección 2) — ya tienen hoy una variante de este
  mismo chequeo, así que no están exentas.

## Reviews

- **2026-09-24** — Análisis crítico general: 7 hallazgos, todos resueltos e integrados
  (alcance ampliado de 7 a 9 skills en Objective/Context/Design/Fuera de alcance; conteo
  de carpetas corregido a 23; orden de comprobaciones `blocked`/`version-mismatch`
  corregido en Design §1; rechazo de downgrade en Design §4 reescrito; índice enlazado a
  `TASKS.md`; tarea añadida en TASKS §6 para `pv-design.en.md`/`.es.md`).
- **2026-09-24** — Análisis crítico SKILL.md vs. workflow.*.md: 3 hallazgos, todos
  resueltos e integrados (TASKS §5 ampliada con las tareas de sincronización de los 6
  `workflow.*.md` afectados — 5 skills que ya tenían el nodo del chequeo más la
  corrección del gap preexistente en `pv-version`, y anotación explícita en las 3 skills
  sin diagrama propio).

## Critical analysis — 2026-09-24

### Structure

No structural deviations. `PLAN.md` has all five required sections in order (Title,
Index, Objective, Design/Fuera de alcance content, Reviews last), the index links to
every own heading plus `TASKS.md`, and `TASKS.md` exists with a concrete, ordered,
checkable breakdown that covers every element the analysis raises (scripts, workflow
files, `SKILL.md` changes, both doc languages, manual verification).

### Design §4 / TASKS §6 — pv-update's documentation entry

| Finding | Explanation | Proposed improvement |
|---|---|---|
| `pv-update` has no existing "Assets and scripts" section to extend | TASKS §6's first task said to update "the 'Assets and scripts' sections of `pv-update`" for the two new scripts, as if such a section already exists (matching the pattern every other skill has, e.g. `pv-todo` at `pv-design.en.md:141`, `pv-version` at `:147`). It doesn't: `pv-update` has no dedicated skill-entry bullet anywhere in `pv-design.en.md` at all — grepping the file for `pv-update` only turns up passing mentions inside *other* skills' entries (lines 458, 490, 496, 500, 506, 533, 665), never a `- **pv-update** — ...` bullet of its own, the way every other public skill has. | Rewrote TASKS §6's first task: create `pv-update`'s full skill entry from scratch (summary + `*Uses:*` + "Assets and scripts"), alphabetically between `pv-todo` and `pv-version`, listing all five assets it will have after this plan — the three already-existing and undocumented (`workflow.audit.md`, `audit-context.py`, `mark-verified.py`) plus the two new ones (`check-framework-status.py`, `install-framework.py`) and `workflow.install.md` — in both `pv-design.en.md` and `pv-design.es.md`. |

### Design §4 — `install-framework.py` version-comparison contract

| Finding | Explanation | Proposed improvement |
|---|---|---|
| Tag-vs-installed-version comparison never states the exact strings compared | Design §4 says `--version <tag>` is compared against the installed version via `parse_version` (reused from `audit-context.py`). `parse_version`'s regex (`audit-context.py:139`) requires the full `X.Y.Z[suffix]` shape and returns `None` on anything else (`audit-context.py:142-147`), silently — no exception, no error message. Section 4's rejection-message prose only covered the case where the comparison *succeeds* and finds a genuine downgrade — the case where it can't parse `<tag>` at all wasn't mentioned as a distinct outcome. | Design §4 rewritten: an unparseable `<tag>` (`parse_version` returns `None`) now gets the same hard rejection as a genuine downgrade — never silently delegated to `install.sh`/`.ps1` for GitHub to resolve or reject. TASKS §3's `install-framework.py` task updated to state this explicitly. |

### Design §4 — pre-release detection window

| Finding | Explanation | Proposed improvement |
|---|---|---|
| "Most recent release of any kind" isn't necessarily one release ahead of `/releases/latest` | Design §4's Spanish prose ("la release más reciente de cualquier tipo") could be misread by an implementer as "the most recent pre-release," when it actually means "the most recent release, pre-release or not" — `/releases?per_page=1` never filters by `prerelease`, unlike `/releases/latest`. Minor wording ambiguity, not a logic bug, but worth tightening since `install-framework.py` doesn't exist yet and whoever writes it only has this prose to go on. | Design §4 reworded: now states explicitly that `/releases?per_page=1` returns the last published release regardless of type (GitHub orders all releases newest-first independent of `prerelease`/draft status, unlike `/releases/latest` which excludes pre-releases by design), and that the pre-release notice only fires when that result's `tag_name` differs from `/releases/latest`'s **and** its `prerelease` field is `true`. TASKS §3's wording was already unambiguous, no change needed there. |

## Detalle de implementación

- [ ] `.claude/pv-doc/pv-design/pv-design.en.md`
- [ ] `.claude/pv-doc/pv-design/pv-design.es.md`
- [ ] `.claude/skills/pv-update/scripts/install-framework.py`

### Everything else (Objective, Context, Design §1-§3, §5, Fuera de alcance, TASKS §1-§5, §7)

No findings. Every file/function/line reference checked against the repo (23 `pv-*`
folders, `audit-context.py`'s `parse_version`/`read_skill_version`/Check A/Check B,
`mark-verified.py`'s three modes, `install.sh`/`install.ps1`'s tag resolution and
`REPO=` constant, the 9 skills' current step-0 prose, the 6 `workflow.*.md` files'
`S0Check`/`S0Ok` nodes including the confirmed pre-existing gap in `pv-version`, and
`pv-design.en.md:527`'s "Reading rule") matches what the plan claims.
