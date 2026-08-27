# Plan: script `resolve-path.py` para resolver rutas de `pv-context.json`

## Objetivo

Que ninguna skill de flujo (`pv-new`, `pv-fix`, `pv-how`, `pv-do`, `pv-internal-*`) tenga que
conocer la estructura interna de `pv-context.json` para obtener una ruta absoluta. Solo
`pv-init` y `pv-update` conocen el schema; el resto pide rutas por **clave lógica** a un
script propiedad de `pv-init`.

## Origen

`pv-how` (vía `pv-internal-tech-analysis`) resolvió `framework.docs.tech.architectureDocDir`
desde la raíz del repo en vez de desde `workFolder`, no encontró la carpeta, la localizó
explorando, y reportó "rutas de `framework.docs.*` mal configuradas en `pv-context.json`" —
un falso positivo. La regla de resolución (base = `workFolder` para `docs.*`, base = repo
root solo para `sourcecodeDir`) está en el schema (texto) y en `audit-context.py` (código),
pero ninguna skill de flujo la tiene explícita, así que el modelo la adivina.

## Decisiones tomadas (con el usuario)

- Interfaz por **claves lógicas fijas** (`--what architectureDocDir`), no dotted-path.
- Cualquier fallo de resolución → exit ≠ 0 con mensaje claro → la skill llamante **para** y
  remite al usuario a `/pv-update` (que repara). No hay "salida limpia si no está
  configurado": en la práctica los tres doc dirs siempre existen (los crea `pv-init`), así
  que ausencia = estado roto. (La obligatoriedad de los doc dirs se aborda en el otro plan,
  `docs-obligatoria-limpieza.md`; este plan solo crea la herramienta.)
- El script es propiedad de `pv-init` (dueño del schema), en
  `.claude/skills/pv-init/scripts/resolve-path.py`.

---

## Parte A — Crear el script

### A1. `.claude/skills/pv-init/scripts/resolve-path.py`

**Invocación:**

```
python .claude/skills/pv-init/scripts/resolve-path.py --what <clave>
```

**Claves lógicas soportadas** (mapeo campo → base, embebido en el script):

| Clave                | Campo en `pv-context.json`                        | Base de resolución |
|----------------------|--------------------------------------------------|--------------------|
| `workFolder`         | `framework.workFolder` (default `/previo-sdd`)    | repo root          |
| `sourcecodeDir`      | `framework.sourcecodeDir` (default `/src`)        | repo root          |
| `changesDir`         | *(derivado)* `{workFolder}/changes`              | repo root          |
| `versionsDir`        | *(derivado)* `{workFolder}/versions`            | repo root          |
| `stuffDir`           | *(derivado)* `{workFolder}/stuff`               | repo root          |
| `architectureDocDir` | `framework.docs.tech.architectureDocDir`          | **`workFolder`**   |
| `styleBibleDocDir`   | `framework.docs.tech.styleBibleDocDir`            | **`workFolder`**   |
| `featuresDocPathDir` | `framework.docs.functional.featuresDocPathDir`    | **`workFolder`**   |

**Salida en éxito:** exit 0. Imprime **solo la ruta absoluta resuelta** en stdout
(POSIX slashes, sin barra final, nada más) para que la skill la capture directa.

**Salida en error:** exit ≠ 0. Diagnóstico a stderr en formato fijo, con exit code por
categoría:

| Exit | Causa                                                                     | Qué debe hacer la skill llamante                                                                 |
|------|-------------------------------------------------------------------------- |------------------------------------------------------------------------------------------------- |
| `2`  | `.claude/pv-context.json` no existe / no es JSON válido / falta `framework` | Parar. "El framework no está inicializado o `pv-context.json` está corrupto. Ejecuta `/pv-init`." |
| `3`  | Clave configurable ausente en `pv-context.json` (p.ej. no hay `docs.tech.architectureDocDir`) | Parar. "Falta configuración de documentación en `pv-context.json`. Ejecuta `/pv-update`."        |
| `4`  | Clave configurada pero la carpeta **no existe** en disco                  | Parar. Igual que exit 3 → `/pv-update`.                                                          |
| `5`  | Clave lógica desconocida (bug de la skill que llama)                      | Parar, reportar el bug, sugerir `/pv-update`.                                                    |

- `workFolder` / `sourcecodeDir` / `changesDir` / `versionsDir` / `stuffDir`: tienen valor
  siempre (default en schema o derivado), así que **nunca** dan exit 3; sí pueden dar exit 4
  si la carpeta resultante no existe.
- `architectureDocDir` / `styleBibleDocDir` / `featuresDocPathDir`: exit 3 si el campo falta,
  exit 4 si el campo está pero la carpeta no.

**Formato del mensaje de error (stderr):**

```
resolve-path: <categoría> — <detalle>
  what: architectureDocDir
  field: framework.docs.tech.architectureDocDir
  fix: run /pv-update
```

**Flags auxiliares:**

- `--json` — en vez de la ruta a pelo, imprime
  `{"what":..., "field":..., "path":..., "exists":true}`. Para depuración / uso desde otros
  scripts. El modo por defecto (ruta a pelo) es el que usan las skills.
- `--allow-missing` — convierte exit 4 en exit 0 e imprime la ruta igualmente. La usan
  `pv-init` (al hacer scaffold, la carpeta aún no existe) y potencialmente `audit-context.py`.
  Las skills de flujo **no** la pasan.

**Detalles de implementación:**

- `repo_root()`: `Path(__file__).resolve().parents[3]` (el script vive en
  `.claude/skills/pv-init/scripts/`). Verificar el nivel exacto de `parents[]` contra la
  ubicación real — `audit-context.py` usa `parents[4]` porque está un nivel más profundo
  (`pv-update/scripts/` vs. lo mismo… ambos están a la misma profundidad: `.claude/skills/
  <skill>/scripts/<file>` → `parents[4]` = repo root). **Usar `parents[4]`, igual que
  `audit-context.py`.**
- Reutilizar (copiar, no importar) `strip_leading_slash` y `resolve_under` de
  `audit-context.py`. El framework no tiene módulo compartido y los scripts son
  self-contained. Documentar en un comentario de cabecera: *"resolution logic kept in sync
  with `pv-update/scripts/audit-context.py`'s `check_docs_dir` — change both together."*
- `sys.stdout.reconfigure(encoding="utf-8")` como el resto de scripts del framework.
- Solo stdlib: `json`, `sys`, `argparse`, `pathlib`.
- No acepta `--context-path`: siempre `{repo_root}/.claude/pv-context.json`.

### A2. Probar el script (en conversación, sin fichero de test)

- `--what workFolder` en este repo → documentar salida real (el repo se llama `previo-sdd`
  y `workFolder` es `/previo-sdd` → esperado `{repo}/previo-sdd`).
- `--what sourcecodeDir` → `{repo}/src` (o exit 4 si no existe — documentar).
- `--what changesDir` → `{repo}/previo-sdd/changes`.
- `--what architectureDocDir` → resolver bajo `{workFolder}/...`; documentar si da ruta o
  exit 4 en este repo.
- `--what featuresDocPathDir`, `--what styleBibleDocDir` → idem.
- `--what foo` → exit 5.
- `--json --what workFolder` → objeto JSON.
- Caso exit 2: validar por lectura de código + un test aislado en el scratchpad que importe
  las funciones del script con un JSON roto (no tocar el `pv-context.json` real).

---

## Parte B — Documentar en `pv-design.*`

### B1. Nueva subsección "Resolving paths" en `pv-design.es.md` y `pv-design.en.md`

Insertar dentro de "The `pv-context.json` file", tras la subsección "Documentation" y antes
de "## The `pv.py` launcher". Texto (EN; traducir para ES):

> #### Resolving paths
>
> No skill parses `pv-context.json`'s path fields on its own. The resolution rules (which
> field, which base folder, leading-`/` stripping) live in one place:
> [`.claude/skills/pv-init/scripts/resolve-path.py`](skills/pv-init/scripts/resolve-path.py),
> owned by `pv-init` (the schema's owner). Any skill needing an absolute path calls it by
> logical key:
>
> ```
> python .claude/skills/pv-init/scripts/resolve-path.py --what architectureDocDir
> ```
>
> Keys: `workFolder`, `sourcecodeDir`, `changesDir`, `versionsDir`, `stuffDir`,
> `architectureDocDir`, `styleBibleDocDir`, `featuresDocPathDir`. On success it prints the
> absolute path and exits 0. On any failure — file missing/corrupt (exit 2), field not
> configured (exit 3), folder missing on disk (exit 4), unknown key (exit 5) — it prints a
> diagnostic and **the calling skill must stop and tell the user to run `/pv-update`**. Only
> `pv-init` and `pv-update` know the JSON's internal shape; every other skill goes through
> this script.
>
> `resolve-path.py` and `pv-update`'s `audit-context.py` share the same resolution logic
> (copied, not imported — framework scripts are self-contained); changing one means changing
> the other.

### B2. Punteros cruzados

En las descripciones de `workFolder`, `sourcecodeDir` y los tres `docs.*` de esa misma
sección, añadir *"(resolved via `resolve-path.py` — see 'Resolving paths' below)"*.

---

## Parte C — Migrar las skills a `resolve-path.py`

Patrón por skill: sustituir "leer `pv-context.json` y componer la ruta" por "llamar a
`resolve-path.py --what <key>`; si sale exit ≠ 0, parar y remitir a `/pv-update`".
(La eliminación del lenguaje "opcional / si no está configurado" se detalla en el otro plan;
aquí solo el cambio mecánico de cómo se obtiene la ruta.)

### C1. `pv-internal-tech-analysis` — `SKILL.md`

- **Revertir** el párrafo largo "Path resolution" que se añadió al paso 1 (con el ejemplo
  `design/docs/architecture`). Sustituir por: *"To get the absolute path of
  `architectureDocDir` / `styleBibleDocDir`, call `resolve-path.py --what <key>` (see
  pv-design's 'Resolving paths'). If it exits non-zero, stop this analysis and tell the
  caller the framework config is broken and the user must run `/pv-update` — do not try to
  locate the docs yourself, and never report this as a doc-vs-code inconsistency."*
- Paso 0: quitar *"treat all of `docs.tech` as unconfigured and go straight to step 2"* — con
  el otro plan `docs.tech` siempre existe; un fallo del script es error, no ausencia.
- Paso 1: quitar *"configured **and** really exists as a folder in the repo"* y *"Skip the
  ones not configured, or configured but whose folder doesn't exist yet"*. Reemplazar por el
  flujo de error vía script.
- Paso 4: **conservar** el párrafo "Scope: this is strictly about doc content vs code, never
  `pv-context.json`" ya añadido (sigue vigente).
- **Modo bootstrap**: `pv-init` invoca a este skill en su paso 5.5 con `docs.tech` recién
  scaffolded (sin `INDEX.md` real) → `resolve-path.py` daría exit 4. Añadir al "Expected
  input from the caller" un parámetro opcional `bootstrap: true` que hace que el skill **no**
  invoque `resolve-path.py` para `docs.tech` y vaya directo a explorar `sourcecodeDir`.
  `pv-init` lo pasa; nadie más.

### C2. `pv-how` — `SKILL.md`

- Línea ~36: *"`docs.tech.*` … and `sourcecodeDir` are optional and used as context in step
  3; if not configured, proceed without them"* → *"resolved via `resolve-path.py` in step 3
  (through `pv-internal-tech-analysis`); a resolution failure there means the user must run
  `/pv-update`."*
- **Conservar** el párrafo del paso 3 punto 5 sobre no decir que `pv-context.json` está mal
  configurado (ya añadido).
- (El "if `docs.tech.architectureDocDir` is configured and…" de las secciones (c)/(d) se
  trata en el otro plan.)

### C3. `pv-do` — `SKILL.md`

- Paso 2.1: donde hoy lee `docs.tech.architectureDocDir` / `styleBibleDocDir` /
  `docs.functional.featuresDocPathDir` de `pv-context.json`, pasar a `resolve-path.py --what
  <key>` para cada uno. Si alguno falla → parar antes de tocar documentación y remitir a
  `/pv-update`.
- Revisar el paso 2.1 completo en implementación (varias líneas truncadas en el grep).

### C4. `pv-fix` — `SKILL.md`

- Donde menciona *"it reads the configured `framework.docs.tech` documentation first"* →
  *"it resolves `docs.tech` via `resolve-path.py`"*.
- Revisar líneas 33, 55, 63-65, 87, 91, 114 en implementación.

### C5. `pv-new` — `SKILL.md`

- Revisar si lee `docs.*` / `sourcecodeDir` / `workFolder` directamente (línea ~30 truncada
  y contexto). Migrar a `resolve-path.py`.

### C6. `pv-internal-doc-features` — `SKILL.md`

- Línea ~46: *"If `docs.functional.featuresDocPathDir` isn't configured in
  `.claude/pv-context.json`, say so and stop"* → *"resolve via
  `resolve-path.py --what featuresDocPathDir`; if it fails, stop and report to the caller
  that the user must run `/pv-update`."*

### C7. `pv-internal-doc-files` — `SKILL.md`

- Recibe `folder` como parámetro del caller (no lee `pv-context.json`). Verificar que los
  callers (`pv-internal-doc-features`, `pv-do`) le pasan ahora la ruta ya resuelta por
  `resolve-path.py`. Probablemente sin cambios en este fichero.

### C8. `pv-init` — `SKILL.md`

- Paso 5.5 (invocación de `pv-internal-tech-analysis`): pasar `bootstrap: true` (ver C1).
- Donde `pv-init` compone rutas de doc dirs para el scaffold, puede seguir haciéndolo él
  mismo (es el dueño del schema) o usar `resolve-path.py --allow-missing` para consistencia.
  Decidir en implementación; preferible `--allow-missing` para tener un único punto de
  resolución.

---

## Parte D — Scripts satélite

### D1. `audit-context.py` (`pv-update`)

- `check_docs_dir` (líneas ~225-238) ya resuelve bajo `workFolder` — **es la referencia
  canónica**. Añadir comentario: *"keep in sync with
  `pv-init/scripts/resolve-path.py`"*.
- No migrar a subprocess de `resolve-path.py` (self-contained; el riesgo de acoplar scripts
  de dos skills no compensa). Sync manual documentado.
- (El nuevo problema `docs-dir-unconfigured:*` se añade en el otro plan.)

### D2. `copy-docs.py` (`pv-version`)

- Ya resuelve rutas de forma determinista (líneas 107-109) con su propio `skipped`.
  **No migrar** a `resolve-path.py` — es un script determinista, no un modelo que adivina;
  el problema original no aplica. Solo actualizar el docstring para reflejar que los tres
  dirs siempre existen (ver el otro plan para el cambio de `skipped` → error).

### D3. `scaffold-project.py` (`pv-init`)

- Ya recibe rutas resueltas del caller. Verificar que funciona cuando se le pide recrear
  **solo un** doc dir (invocación desde `pv-update`), no el scaffold completo. Puede
  necesitar un flag `--only <path>`. Leer en implementación. (Uso desde `pv-update` se
  detalla en el otro plan.)

---

## Parte E — Verificación

### E1. Tests deterministas (comandos, en conversación)

- `resolve-path.py` para las 8 claves en este repo → documentar salida real de cada una.
- `resolve-path.py --what <clave-mala>` → exit 5.
- `resolve-path.py --json --what workFolder` → objeto JSON válido.
- Test aislado en scratchpad: importar funciones del script con un `pv-context.json` roto →
  exit 2.

### E2. Revisión de consistencia cruzada

- `grep -rn "pv-context.json" .claude/skills/**/SKILL.md` → tras los cambios, solo
  `pv-init`, `pv-update` y menciones tipo "run `/pv-init` / `/pv-update`". Ninguna skill de
  flujo debe describir cómo leer una ruta del JSON.
- Verificar que ninguna skill migrada quedó con instrucción contradictoria (leer el JSON
  *y* llamar al script).

### E3. Flujo end-to-end

- `pv-how` sobre una entrada real de este repo → confirmar que ya no emite el falso positivo
  y que el resto del flujo es idéntico.

---

## Puntos abiertos a confirmar durante la implementación

1. `pv-init` al hacer scaffold: ¿usa `resolve-path.py --allow-missing` o compone las rutas
   él mismo? (Plan recomienda `--allow-missing`.)
2. `scaffold-project.py`: ¿necesita flag `--only <path>` para recreación puntual desde
   `pv-update`?
3. Nivel de `parents[]` en `repo_root()` — confirmar `parents[4]` con la ruta real.

---

## Dependencia con el otro plan

`docs-obligatoria-limpieza.md` declara los tres doc dirs obligatorios de facto y da a
`pv-update` el mecanismo para recrear uno ausente. Este plan asume ese modelo (exit 3 = ir a
`/pv-update`). **Implementar primero las partes A, B y C10/C11 de `docs-obligatoria-limpieza.md`**
(schema + `pv-update` sabe recrear un doc dir) antes de la Parte C de este plan, para que
"exit 3 → `/pv-update`" tenga sentido.
