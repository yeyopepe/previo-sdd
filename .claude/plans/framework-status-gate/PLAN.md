# Framework status gate: script único de verificación + capacidad de instalar desde `pv-update`

## Index

- [Objective](#objective)
- [Context: current state](#context-current-state)
- [Design](#design)
  - [1. `check-framework-status.py` — script de verificación, propiedad de `pv-update`](#1-check-framework-statuspy--script-de-verificación-propiedad-de-pv-update)
  - [2. Migración de las 7 skills públicas al script único](#2-migración-de-las-7-skills-públicas-al-script-único)
  - [3. Conteo exacto de skills instaladas](#3-conteo-exacto-de-skills-instaladas)
  - [4. `pv-update install` — nueva capacidad de instalación/actualización](#4-pv-update-install--nueva-capacidad-de-instalaciónactualización)
  - [5. Ejemplos de prompts `/pv-update`](#5-ejemplos-de-prompts-pv-update)
- [Fuera de alcance](#fuera-de-alcance)
- [Reviews](#reviews)

## Objective

Hoy, siete skills públicas del framework (`pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-status`,
`pv-todo`, `pv-version`) repiten, palabra por palabra, el mismo bloque de prosa en su
paso 0 para comprobar que `.claude/pv-context.json` existe y que la versión instalada del
framework está verificada (`frameworkStatus.lastVerifiedVersion` / `blocked`). Esa
verificación:

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

- Las 7 skills públicas (`pv-do/SKILL.md`, `pv-fix/SKILL.md`, `pv-how/SKILL.md`,
  `pv-new/SKILL.md`, `pv-status/SKILL.md`, `pv-todo/SKILL.md`, `pv-version/SKILL.md`)
  tienen en su paso 0 un párrafo idéntico: leer `metadata.version` del frontmatter de
  `pv-init/SKILL.md`, compararlo con `framework.frameworkStatus.lastVerifiedVersion` de
  `pv-context.json`, y parar si no coincide, si `frameworkStatus` falta, o si
  `blocked` es `true`.
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
- Hoy existen exactamente **22 carpetas** bajo `.claude/skills/pv-*/`, todas en
  `0.9.8b6`.

## Design

### 1. `check-framework-status.py` — script de verificación, propiedad de `pv-update`

Nuevo script en `pv-update/scripts/check-framework-status.py`. Es deliberadamente
**distinto** de `audit-context.py`: mientras `audit-context.py` es el auditor completo y
lento (markers, `.metadata.json`, namespace, hooks...) que solo corre bajo demanda
(`/pv-update`), este nuevo script es el subconjunto barato que **cada una de las 7 skills
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
  "problem": "context-missing | context-invalid-json | version-mismatch | blocked | skill-count-mismatch",
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
3. **`version-mismatch`** — mismo Check A que ya hace `audit-context.py` (leer
   `metadata.version` de `pv-init/SKILL.md`, comparar con
   `framework.frameworkStatus.lastVerifiedVersion`; ausencia de `frameworkStatus`
   cuenta como mismatch). Reutiliza la misma lógica de lectura de frontmatter que ya
   existe en `audit-context.py`/`mark-verified.py` (duplicada aquí a propósito, mismo
   patrón que ya siguen esos dos scripts — cada script `pv-*` es autocontenido).
4. **`blocked`** — `framework.frameworkStatus.blocked` es `true`. Mensaje incluye
   `blockedReason` si está presente.
5. **`skill-count-mismatch`** — ver sección 3 más abajo.

**Cuando el script no existe en su ubicación esperada** (`.claude/skills/pv-update/scripts/check-framework-status.py`):
esto es justo el caso "el framework no parece bien instalado" que pide el punto 1 del
objetivo — no es un problema que el script mismo pueda reportar (no puede ejecutarse si
no existe). La skill que lo invoca (paso 0 de las 7 skills públicas) debe comprobar la
existencia del fichero *antes* de intentar ejecutarlo y, si falta, mostrar directamente
el mensaje de instalación sin más rodeo (ver sección 2).

### 2. Migración de las 7 skills públicas al script único

El párrafo duplicado del paso 0 en `pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-status`,
`pv-todo`, `pv-version` se sustituye, en las 7 skills, por el mismo texto (evitando
volver a duplicar prosa distinta en cada una):

> Antes de continuar, comprobar que `.claude/skills/pv-update/scripts/check-framework-status.py`
> existe. Si no existe, informar al usuario de que el framework no parece estar bien
> instalado y que debe instalar la última versión (ver [sección 5](#5-ejemplos-de-prompts-pv-update)
> para el prompt exacto) — parar ahí, sin continuar el trabajo de esta skill.
>
> Si existe, ejecutarlo (`python .claude/skills/pv-update/scripts/check-framework-status.py`)
> y leer su JSON. Si `ok` es `false`, mostrar `message` al usuario y parar — ninguna skill
> `pv-*` puede continuar su trabajo sin que este paso pase con `ok: true`.

Esto **reemplaza por completo** el párrafo "Additionally, before continuing, check that
the framework's installed version is verified: read `metadata.version`..." en las 7
skills — no coexisten las dos formas de comprobar lo mismo.

La comprobación de existencia de `.claude/pv-context.json` que cada una de las 7 skills
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
  diseño) y `GET /repos/{repo}/releases?per_page=1` (la release más reciente de
  cualquier tipo; si su `tag_name` difiere del de `/releases/latest` y su campo
  `prerelease` es `true`, hay una pre-release más nueva que la última oficial
  disponible). Ambos datos —versión oficial más reciente, y pre-release más reciente si
  existe una posterior a esa— se muestran siempre al usuario antes de instalar nada,
  aunque el usuario haya pedido explícitamente una versión concreta: es información,
  no una pregunta a responder.
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
  `<tag>` es inferior a la instalada, rechazo duro**: el script termina con error,
  mensaje explicando que `pv-update install` nunca hace downgrades (y que instalar una
  versión inferior a mano requiere ejecutar `install.sh`/`install.ps1` directamente,
  fuera de este flujo asistido) — no hay flag de escape para forzarlo. Si `<tag>` resulta
  ser una pre-release (su release en GitHub tiene `prerelease: true`), el script procede
  igualmente (el usuario la pidió explícitamente) pero antes emite el mismo aviso de
  riesgo no vinculante del punto anterior.
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
  (`pv-internal-*`, `pv-review-*`) ni en `pv-init`/`pv-update` mismas — por diseño, ellas
  no pasan por este paso 0 (son las que bootstrapean o reparan el propio framework).

## Reviews
