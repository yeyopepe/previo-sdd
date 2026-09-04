# Diseño: mover `risk` del header de `plan.md` a `.metadata.json`

**Fecha:** 2026-09-03 · **revisado contra el repo:** 2026-09-04 · **implementado:** 2026-09-04
**Estado:** ✅ **implementado** — código + docs (es/en) + pruebas. Diferencias con el plan durante la implementación:
- La migración one-shot de `pv-update` se implementó como un **check nuevo en `audit-context.py`** (`check_risk_in_plan_headers` → problema `risk-in-plan-header:*`) + su fix en el bucle del paso 3 de `pv-update/SKILL.md`, en vez de un pase proactivo suelto. Encaja mejor con el diseño "todo lo auditable es un `problems`" y sale gratis la idempotencia (el check solo dispara si falta `risk` en `.metadata.json`). `audit-context.py` **sí se tocó** para esto (el plan decía que no) — pero solo para *añadir* el detector de migración, no para la validación de `risk` (esa ya estaba).
- `PLAN.template.md`: la tabla de "Meaning" se movió a una sub-sección `### Risk median meaning` dentro de `(f)`, con nota de que el valor vive en `.metadata.json`.
- Traducción: se editaron los fragmentos cambiados directamente en cada `.en.md` (no regeneración completa con `en-translate`) para no arrastrar diffs masivos ni divergir del inglés ya asentado.

> **Correcciones de la revisión 2026-09-04** (el borrador original tenía 4 desajustes con el repo):
> 1. `audit-context.py` **ya valida `risk`** (change 1): `METADATA_ALLOWED_KEYS` lo incluye + rango 0-10. No se toca — §4.5, §7.8, §8.
> 2. `pv-status/scripts` **sí tiene import cruzado**: `filter_status.py` importa `read_flags`/`parse_todo_description` de `collect_status.py`. `read_risk` se define **una vez** en `collect_status.py` y se importa, no se duplica — §1, §4.4, §7.7.
> 3. `filter_status.py`'s render usa `if entry["risk"]` (truthiness) → con `int`, `risk == 0` se pintaría `?`. Cambiar a `is not None` en `render_report` (L402) y `render_terminal` (L472) — §4.4, §7.6.
> 4. El marker-check de `pv-update` **no tiene lista hardcodeada** (lee `[[[...]]]` de la plantilla en caliente): quitar `[[[Risk]]]` de `PLAN.template.md` basta. Solo hay prosa desactualizada en `pv-update/SKILL.md` ~L44 **y** ~L91 — §4.5, §7.8, §8.
**Depende de:** el "change 1" (`.metadata.json` + sistema de `flags`), que **ya está implementado y commiteado** (`4ff6ac8` "Added: .metadata.json definition", `8d4efee` "Added: Flags to changes"). En el repo ya existen:
- `{workFolder}/changes/{state}/{xxxx}/.metadata.json` (dotfile por cambio, creado en el primer write, nunca borrado).
- `.claude/skills/pv-internal-workflow/metadata.schema.json` — con el campo `risk` **ya declarado** (`"type": ["integer","null"], "minimum": 0, "maximum": 10`) y descrito como *"This plan (flags) never writes it; set-metadata.py preserves it untouched"*.
- `.claude/skills/pv-internal-workflow/scripts/set-metadata.py` — hoy solo maneja `flags` (`--add-flag` / `--remove-flag` / `--toggle-flag`). Su docstring dice literalmente *"the risk plan (change 2) will add `--set-risk` here"*. **Este plan es quien lo añade.**
- `read_metadata(entry_dir)` en `collect_status.py`, que lee `.metadata.json` y devuelve `{}` ante fichero ausente o malformado.
- `read_flags(entry_dir)` **definida solo en `collect_status.py`**; `filter_status.py` **la importa** (`from collect_status import parse_todo_description, read_flags`, línea ~82). O sea: `pv-status/scripts` **sí** tiene un import cruzado establecido (`filter_status.py` → `collect_status.py`), y `read_metadata` / `read_flags` viven en un único sitio. `read_risk` sigue el mismo patrón: se define en `collect_status.py` y `filter_status.py` la añade a ese import — **no** se duplica.
- **`audit-context.py` (change 1) ya valida `risk`**: `METADATA_ALLOWED_KEYS = {"flags", "flagsLastModified", "risk"}` (línea ~180) y una comprobación de rango (entero 0-10, excluyendo `bool`) que emite `metadata-risk-invalid:*` (líneas ~249-255). El schema ya lo declaraba y la auditoría genérica de `.metadata.json` ya lo cubre — este plan **no toca `audit-context.py`**.

**Disparador:** el valor de riesgo (mediana de los 9 factores de `pv-internal-tech-risks`) hoy se escribe como campo `**Risk**` en el header de `plan.md`. En realidad es un **dato de estado** puntual, no parte del diseño técnico — y `pv-status` lo tiene que parsear con regex de un `.md`. Moverlo a `.metadata.json.risk` lo deja en un solo sitio, parseable sin ambigüedad, junto al resto de estado mutable del cambio (`flags`), reusando el fichero, el schema y el script que el change 1 ya introdujo.

---

## 1. Alcance

Un único cambio de dato: `risk` deja de vivir en `plan.md` y pasa a `.metadata.json`.

- **NO** se toca la sección opcional `## (f) Risk analysis` de `plan.md` (los 9 factores en prosa, solo si el usuario los pidió). Eso es *análisis*, se queda donde está.
- **NO** cambia quién calcula el riesgo (`pv-internal-tech-risks`) ni cuándo (`pv-how` paso 3.1, tras escribir `plan.md`).
- **SÍ** cambia:
  - dónde lo escribe `pv-how` (`.metadata.json` vía `set-metadata.py --set-risk`, no el header de `plan.md`),
  - cómo lo leen los 2 parsers de `pv-status` (`collect_status.py`, `filter_status.py`) — de `.metadata.json`, no de `plan.md`,
  - la plantilla `PLAN.template.md` (fuera el marcador `[[[Risk]]]` del header),
  - la convención de marcadores (`pv-design.*.md`),
  - el marker-check de `pv-update` (fuera `**Risk**` de los labels obligatorios — aparece en `SKILL.md` líneas ~44 **y** ~91, ambas descriptivas) + una **migración one-shot** `plan.md` → `.metadata.json`,
  - `set-metadata.py` gana el subcomando `--set-risk`,
  - `metadata.schema.json` — actualizar la descripción de `risk` (ya no es "never written"),
  - `pv-how/SKILL.md` — bloque "Language" (línea ~16) + pasos 3 / 3.1 / check (líneas ~106-121),
  - **NO** se toca `pv-update/scripts/audit-context.py`: la validación de `.metadata.json.risk` contra el schema (rango 0-10, `metadata-risk-invalid:*`) **ya está implementada por el change 1** (`METADATA_ALLOWED_KEYS` incluye `"risk"`, hay comprobación de rango). Solo se verifica que sigue ahí.

---

## 2. Campo en `.metadata.json`

```json
{
  "flags": [],
  "flagsLastModified": "2026-09-03",
  "risk": 5
}
```

- **`risk`** (entero 0-10 | ausente): la mediana de los 9 factores. **Campo ausente = todavía no evaluado** — equivale al `?` que hoy muestra `pv-status` cuando `plan.md` no tiene el campo (`fast` entries, o cambios aún sin `pv-how`).
  - **No se soporta "volver a no evaluado".** Una vez `pv-how` escribe el valor, siempre hay un entero. `--set-risk` solo acepta `0`-`10`; no hay `--clear-risk` ni `--set-risk null`. El schema mantiene `null` como valor válido por robustez de lectura (un fichero editado a mano), pero ningún camino del framework lo escribe.
- **Ya declarado** en `metadata.schema.json` (change 1):
  ```json
  "risk": { "type": ["integer", "null"], "minimum": 0, "maximum": 10 }
  ```
  Este plan **actualiza su `description`**: quitar *"This plan (flags) never writes it"*, poner algo como *"Median of pv-internal-tech-risks' 9 factors, written by pv-how (step 3.1) via set-metadata.py --set-risk. Absent = not yet assessed."*.
- **`flagsLastModified` NO se toca** al escribir `risk`. Es, por definición del schema, el timestamp de la última mutación de `flags` (*"any add or remove"* de flags). `risk` no lleva su propio `riskLastModified` — nadie lo necesita.
- El `{meaning}` textual ("Moderate risk", etc.) **no se persiste** — es derivable de la mediana vía la tabla de `PLAN.template.md`. Quien lo quiera mostrar (p.ej. `pv-status` en chat) lo deriva de `risk` con esa misma tabla.

---

## 3. Pipeline actual de `risk` (lo que hay que cambiar)

1. **`pv-how` paso 3** (`SKILL.md` línea ~106) escribe `plan.md` **sin** el campo `**Risk**` (explícito: *"Don't write the header's `**Risk**` field yet in this save ... it's added in step 3.1"*).
2. **`pv-how` paso 3.1** (`SKILL.md` líneas ~113-117) invoca `pv-internal-tech-risks` (no escribe nada, solo devuelve los 9 factores + mediana) y **edita el header de `plan.md`** añadiendo, bajo **Creation date**, el campo `**Risk**: {median}/10 — {meaning}` (el `{meaning}` sale de la tabla de la plantilla).
3. **`pv-how` check** (`SKILL.md` línea ~119): no dar `plan.md` por terminado, ni pasar al paso 3.2, sin confirmar que el header ya tiene `**Risk**` con valor real (nunca placeholder).
4. **`pv-how/SKILL.md` bloque "Language"** (línea ~16): lista `**Risk**` como uno de los dos campos de header fijos en inglés (junto a **Creation date**) y menciona que `filter_status.py` lo parsea literalmente (`extract_risk`) para el status report — *"translating them makes the entry's planned date and risk show up as missing there, silently"*.
5. **`PLAN.template.md`**: el header lleva `- **[[[Risk]]]**: [median 0-10 returned by pv-internal-tech-risks] — [description...]` → el `[[[Risk]]]` lo marca como **marcador estructural obligatorio**. Debajo, la tabla de "Meaning" por rango de mediana.
6. **`pv-status`** lo parsea en **2 ficheros** (cada uno con su propia `RISK_RE`, aunque hay import cruzado para otras funciones):
   - `collect_status.py`: `parse_risk(plan_path) -> int | None` (línea 130-143) + `RISK_RE` (línea 55: `re.compile(r"\*\*Risk\*\*\s*[:—-]\s*(\d{1,2})\s*/\s*10")`). Se llama en `build_entry` (línea 223): `risk = parse_risk(plan_path) if has_plan else None`. El docstring del módulo (líneas 26-30) describe `risk` como *"parsed from plan.md's '**Risk**' header field"*.
   - `filter_status.py`: `extract_risk(text) -> str | None` (línea 193-195) + su propio `RISK_RE` (línea 89, misma regex). Se llama en `build_entry` (línea 240): `risk = extract_risk(plan_text) if plan_text else None`. **Ojo: devuelve `str`, no `int`** — inconsistencia de tipos preexistente. Ya importa de `collect_status` (línea 82: `parse_todo_description, read_flags`), así que `read_risk` cabe en ese import. El render de este script (`render_report` L402, `render_terminal` L472) usa `if entry["risk"]` (truthiness) — con `int` habría que pasar a `is not None` para no romper `risk == 0`.
   - `render_status.py`: `format_risk(entry)` (línea 133-135) **solo consume `entry["risk"]`** del dict, y ya usa `risk is not None` — no parsea `plan.md` ni asume tipo.
7. **`pv-update`** — el marker-check **no tiene lista de labels hardcodeada**: `audit-context.py`'s `check_marked_documents` lee los `[[[...]]]` de `PLAN.template.md` fresco en cada ejecución (`MARKED_TEMPLATES`). Lo único que cita `**Risk**` explícitamente es la **prosa de `pv-update/SKILL.md`** (~L44 y ~L91), como ejemplo.
8. **`pv-update/scripts/audit-context.py`**: **ya valida `risk`** (change 1): `METADATA_ALLOWED_KEYS = {"flags", "flagsLastModified", "risk"}` (L180), rango 0-10 excluyendo `bool` (L249-255), `metadata-risk-invalid:*`.
9. Sección opcional `## (f) Risk analysis` de `plan.md`: los 9 factores en prosa, solo si el usuario los pidió. **Independiente del header.**

---

## 4. Pipeline propuesto

### 4.1 `set-metadata.py` — añadir `--set-risk`

Nuevo argumento `--set-risk N` (entero 0-10). Cambios en el script:

- **Argparse**: `parser.add_argument("--set-risk", type=int, metavar="N", help="Set the change's risk median (0-10), from pv-internal-tech-risks.")`. Validar `0 <= N <= 10` con `parser.error` si no.
- **Relajar el guard "nothing to do"** (línea ~277): hoy exige al menos una op de flags. Pasa a: al menos una op de flags **o** `--set-risk`.
- **Read-modify-write** dentro del `_FileLock` (ya existente): tras resolver `entry_dir` (que ya rechaza `todo/` para cualquier operación — §7.4 resuelto "gratis"), si `--set-risk` está presente:
  - `data["risk"] = args.set_risk`
  - **no** tocar `flags` ni `flagsLastModified`
  - `changed_risk = (old_risk != args.set_risk)`; escribir el fichero si `changed_risk` o si hubo cambio de flags o si el fichero no existía.
- **Confirmación de salida** (líneas ~324-334): hoy asume operación de flags. Añadir una rama: si se tocó `risk`, incluir `risk N` (o `risk N->M`) en la línea de confirmación. Si **solo** se tocó risk, no imprimir nada de flags.
- **`--print`**: sin cambios (reserializa el `.metadata.json` resultante).
- `VALID_FLAGS` y toda la lógica de flags: intactas.

Uso desde `pv-how`:
```
python .claude/skills/pv-internal-workflow/scripts/set-metadata.py --xxxx {xxxx} --set-risk {median}
```
(con `--work-folder` si aplica; `--state inProgress` si se quiere evitar la búsqueda). **Crea `.metadata.json`** si aún no existe.

### 4.2 `pv-how`

1. **Paso 3** (`SKILL.md` L106 + `workflow.how.md`): igual — `plan.md` sin nada de riesgo en el header. De hecho más simple: ya no hay un "campo del header que se añade después". Reescribir la coletilla *"**Don't write the header's `**Risk**` field yet in this save** (not even with a placeholder ...) — it's added in step 3.1..."* → algo como *"The risk value isn't part of `plan.md` at all; step 3.1 writes it to `.metadata.json`."*.
   - **`workflow.how.md`** (diagrama Mermaid): el nodo `S3WritePlan[Write plan.md sections a-e, without Risk field yet]` → *"Write plan.md sections a-e"* (ya no hay "Risk field" que posponer). El nodo `S31Write[Add Risk field to plan.md header]` → *"Write risk to .metadata.json via set-metadata.py --set-risk"*. `S31Risk`, `S31Detail`, `S31AddSection` (sección f) no cambian.
2. **Paso 3.1** (`SKILL.md` ~L113-117): tras `pv-internal-tech-risks`, **en vez de editar `plan.md`**, invocar `set-metadata.py --set-risk {median}`. `pv-how` no escribe JSON a mano — coherente con que las skills deleguen las mutaciones de ficheros del framework en scripts (mismo criterio que `move-change.py`, `delete-todo.py`). El `{meaning}` textual **no se persiste**; si el usuario lo pide en chat, se deriva de la mediana con la tabla de la plantilla.
3. **Check** (`SKILL.md` ~L119): *"no terminar el `plan.md` / no pasar al paso 3.2 sin haber confirmado que `.metadata.json.risk` tiene un entero 0-10 real (p.ej. releyendo el fichero, o con `--print`)"*.
4. **Bloque "Language"** (`SKILL.md` L16). Texto actual: *"that's the two header fields (**Creation date**, **Risk**) and the three always-present section headings ..."* y más abajo *"`pv-status`'s `filter_status.py` parses **Creation date** and **Risk** literally (`extract_date`/`extract_risk`, reused from `description.md`'s parsing) ... translating them makes the entry's planned date and risk show up as missing there, silently"*. Cambios:
   - *"the two header fields (**Creation date**, **Risk**)"* → *"the header field (**Creation date**)"* — solo queda uno marcado con `[[[...]]]` en la plantilla.
   - *"parses **Creation date** and **Risk** literally (`extract_date`/`extract_risk`...)"* → *"parses **Creation date** literally (`extract_date`...)"*; quitar la coletilla sobre "risk show up as missing" (risk ya no sale de `plan.md`).

### 4.3 `PLAN.template.md`

- Quitar la línea `- **[[[Risk]]]**: ...` del header. El header queda solo con `- **[[[Creation date]]]**: ...`.
- La **tabla de "Meaning" por rango de mediana**: se **mantiene** en la plantilla (es la fuente canónica que `pv-how` usa para el chat y que `pv-status` puede usar para derivar el meaning). Reetiquetarla si su título la ata al "campo del header" (p.ej. *"Risk median meaning (written to `.metadata.json.risk` by pv-how)"*).
- Ajustar cualquier texto de la plantilla que numere/menciona el campo del header, y su sección de notas de autoría.

### 4.4 `pv-status`

- **`read_risk(entry_dir) -> int | None`**: función nueva **en `collect_status.py`**, y `filter_status.py` la **importa** — mismo patrón que `read_flags` hoy (`filter_status.py` línea ~82: `from collect_status import parse_todo_description, read_flags` → pasa a `... read_flags, read_risk`). **No se duplica.** Implementación:
  ```python
  def read_risk(entry_dir: Path) -> int | None:
      raw = read_metadata(entry_dir).get("risk")
      # bool es subclase de int en Python: excluirlo explícitamente.
      if isinstance(raw, bool) or not isinstance(raw, int):
          return None
      return raw if 0 <= raw <= 10 else None
  ```
  (apoyada en el `read_metadata` que ya vive en `collect_status.py`).
- **`collect_status.py`**:
  - `build_entry` (L223): `risk = parse_risk(plan_path) if has_plan else None` → `risk = read_risk(entry_dir)` (ya no depende de `has_plan`).
  - **Eliminar** `parse_risk()` (L130-143) y `RISK_RE` (L55).
  - Actualizar el docstring del módulo (líneas ~26-30: *"risk: integer 0-10 parsed from plan.md's '**Risk**' header field ..."*) → *"risk: integer 0-10 read from .metadata.json's 'risk' field (written by pv-how via set-metadata.py). Null if absent"*.
- **`filter_status.py`**:
  - `build_entry` (L240): `risk = extract_risk(plan_text) if plan_text else None` → `risk = read_risk(entry_dir)`.
  - **Eliminar** `extract_risk()` (L193-195) y `RISK_RE` (L89).
  - Añadir `read_risk` al import de `collect_status` (L82).
  - Actualizar el docstring del módulo (líneas ~21-25: *"risk: plan.md's '**Risk**' header field (written by pv-how...)"*) → *"risk: .metadata.json's 'risk' field (written by pv-how via set-metadata.py); None if absent"*.
  - **Tipo unificado a `int | None`**: hoy `extract_risk` devolvía `str`. Esto obliga a tocar `filter_status.py`'s propio render, que hoy usa **truthiness**, no `is not None`:
    - `render_report` (L402): `risk=f"{entry['risk']}/10" if entry["risk"] else "?"` → `... if entry["risk"] is not None else "?"`.
    - `render_terminal` (L472): `risk = f"{entry['risk']}/10" if entry["risk"] else "?"` → `... if entry["risk"] is not None else "?"`.
    - Motivo: con `int`, un `risk` **`0`** (riesgo nulo, valor legítimo del schema) es *falsy* y se pintaría como `?`. Con el `str` de hoy nunca llegaba un `"0"`, así que el bug está latente; al cambiar a `int` hay que cerrarlo. `collect_status.py` no tiene este problema (nunca formatea risk; lo hace `render_status.py`, que ya usa `is not None`).
- **`render_status.py`**: **sin cambios** — `format_risk(entry)` (L133-135) ya usa `risk is not None`, y sigue leyendo `entry["risk"]`, que ambos builders ahora rellenan desde `.metadata.json` como `int | None`. Es el punto que hace este refactor viable: el render de `render_status.py` no toca la fuente ni asume tipo.
- **Plantillas** `STATUS.template.md` / `STATUS.filtered.template.md`: la columna `Risk` **no cambia** (el dato llega ya resuelto en el dict). Si se quiere mostrar el "meaning" textual, se deriva de la mediana con la tabla de `PLAN.template.md`.

### 4.5 `pv-update`

- **Marker-check** — el motor real vive en `audit-context.py`: **no hay lista hardcodeada de labels**, `extract_markers()` lee los `[[[...]]]` frescos de `PLAN.template.md` en cada ejecución (`MARKED_TEMPLATES`). Así que quitando `[[[Risk]]]` de la plantilla (§4.3) el marker-check deja de exigirlo **automáticamente** — `audit-context.py` no se toca. Lo que sí hay que editar es la **prosa de `pv-update/SKILL.md` que cita `**Risk**` como ejemplo de marcador obligatorio**, en **dos** sitios:
  - **~L44** (descripción de `marker-missing:*`): `**Name**`, `**Creation date**`, `**Risk**`… → quitar `**Risk**` de esa enumeración de ejemplo.
  - **~L91** (cómo se repara `marker-missing:*`): mismo retoque si nombra `**Risk**`.
  Ninguna de las dos es funcional (el chequeo se rige por la plantilla), pero dejarlas desactualizadas induce a error.
- **Migración one-shot** (parte de la auditoría normal de `/pv-update`, **corre sola**, sin modo aparte ni pregunta — como el resto de reparaciones; es idempotente: solo actúa donde hay `**Risk**` en `plan.md` y falta `risk` en `.metadata.json`):
  - **`changes/inProgress/*` y `changes/implemented/*`** con `plan.md` que tenga `**Risk**` en el header:
    1. parsear el valor con la **misma regex de hoy** (`\*\*Risk\*\*\s*[:—-]\s*(\d{1,2})\s*/\s*10`),
    2. **escribir `.metadata.json` directamente desde `pv-update`** (read-modify-write del dotfile: fusionar `{"risk": N}` preservando `flags` / `flagsLastModified`; crear el fichero si no existe). Es una operación de reparación puntual y `pv-update` ya toca ficheros del framework al auditar — no merece el coste de invocar `set-metadata.py` por carpeta.
    3. eliminar la línea `- **Risk**: ...` del header de `plan.md` (dejar `- **Creation date**: ...`).
  - **`changes/closed/*`** (decisión §7.1 → **migrar, solo lectura**): por cada `plan.md` de `closed` con `**Risk**`:
    1. parsear el valor (misma regex),
    2. escribir `.metadata.json` con `{"risk": N}` (mismo read-modify-write),
    3. **NO tocar el `plan.md` de `closed`** — historia congelada; el `**Risk**` muerto se queda ahí, pero `filter_status.py <closed>` seguirá mostrando el número (ahora desde `.metadata.json`).
- **`audit-context.py`**: **ya cubre `risk`**, no se toca. `METADATA_ALLOWED_KEYS` incluye `"risk"` y `check_metadata_files()` valida rango 0-10 (excluyendo `bool`) emitiendo `metadata-risk-invalid:*`. Tras la migración, un `.metadata.json` con `{"risk": 6}` es válido para la auditoría sin cambio alguno. Solo se comprueba en las pruebas que sigue siendo así.

### 4.6 `pv-design.es.md` + `pv-design.en.md`

- **"Convención de marcadores en plantillas"** (`pv-design.es.md` L444-468): **el ejemplo NO cita `**Risk**`** — usa `[[[Creation date]]]` / `[[[Full description]]]` / `[[[(a) Functional notes]]]`. No hay lista de marcadores por plantilla que mantener aquí (el texto es explícito: *"la plantilla es la única fuente de verdad"*). **Nada que tocar en esta sección** más allá de una relectura de confirmación.
- **`metadata.schema.json` en la sección de responsabilidades de scripts** (`pv-design.es.md` L212): hoy dice de `risk` *"declarado pero no escrito por este flujo — hueco para un plan posterior"*. Actualizar → *"escrito por `pv-how` (paso 3.1) vía `set-metadata.py --set-risk`; ausente = aún no evaluado"*.
- **Responsabilidades de `pv-how`** (`pv-design.es.md` L103): *"escribe la mediana devuelta en la cabecera del plan"* → *"escribe la mediana en `.metadata.json` vía `set-metadata.py --set-risk`"*.
- **`pv-status` scripts** (L122, ficha de `filter_status.py`): la línea 1 de ficha `flags · code · [type] · (status) · Risk` **no cambia**; solo cambia el origen del dato (de `plan.md` a `.metadata.json`). Revisar si el texto lo detalla.
- Si hay bloque de responsabilidades de `pv-update`, añadir la migración one-shot `plan.md` → `.metadata.json` para `risk`.

---

## 5. Retrocompatibilidad

- **Carpetas existentes con `**Risk**` en `plan.md`** (`inProgress` / `implemented`): hasta que `pv-update` corra la migración, `pv-status` mostraría `Risk: ?` para esos cambios (los parsers nuevos no miran `plan.md`). Estado transitorio aceptable; se documenta y **`pv-update` lo repara solo** en su siguiente ejecución (detecta `plan.md` con `**Risk**` y sin `.metadata.json.risk`).
- **`changes/closed/*`**: migración solo-lectura (§4.5) — `filter_status.py <closed>` sigue mostrando el número. El `**Risk**` del `plan.md` de `closed` se deja muerto.
- **`fast` entries**: nunca tuvieron `plan.md` → nunca tuvieron `risk` → siguen mostrando `?`. Sin cambio.
- **Proyectos en versión anterior del framework**: al actualizar, `pv-update` corre la migración (los tres estados).

---

## 6. Orden de implementación

1. `/pv-new` + `/pv-how` para documentar este change.
2. **`set-metadata.py`**: añadir `--set-risk` (§4.1). Probar: `--set-risk 5` crea/actualiza el fichero, no toca `flags`/`flagsLastModified`; `--set-risk 11` y `--set-risk -1` fallan; `--set-risk` sobre `todo/` falla (heredado); `--print` refleja `risk`.
3. **`metadata.schema.json`**: actualizar la `description` de `risk`.
4. **`pv-status`**: `read_risk()` en `collect_status.py` → `collect_status.py` (delegar en `build_entry`, borrar `parse_risk` + `RISK_RE`, docstring) → `filter_status.py` (añadir `read_risk` al import de `collect_status`, delegar en `build_entry`, borrar `extract_risk` + `RISK_RE`, docstring, **cambiar `if entry["risk"]` → `if entry["risk"] is not None` en `render_report` L402 y `render_terminal` L472**). Verificar `render_status.py` intacto y las plantillas `STATUS*`.
5. **`pv-how`**: `SKILL.md` — reescribir bloque "Language" (L16) + pasos 3 (L106) / 3.1 (L113-121) / check (L119); `workflow.how.md` — nodos `S3WritePlan` y `S31Write` del diagrama Mermaid (§4.2 punto 1). El paso 3.1 pasa a invocar `set-metadata.py --set-risk` en vez de editar el header.
6. **`PLAN.template.md`**: quitar `[[[Risk]]]` del header; conservar/reetiquetar la tabla de "Meaning".
7. **`pv-design.es.md` + `pv-design.en.md`**: "Marker convention" sin `**Risk**`; responsabilidades.
8. **`pv-update/SKILL.md`**: quitar `**Risk**` de la prosa de ejemplo del marker-check (~L44 y ~L91); añadir la migración one-shot (`inProgress` + `implemented` limpian header; `closed` solo lee). **`audit-context.py` NO se toca** (ya valida `risk`); el marker-check tampoco (se rige por la plantilla, ya sin `[[[Risk]]]`).
9. **Documentación en español** (§8): actualizar todos los ficheros del checklist.
10. **Traducción a inglés** (§9): regenerar cada `.en.md` desde su `.es.md` con `en-translate` (y editar `SKILL.md` / plantillas directamente en inglés).
11. Pruebas:
    - regenerar un `plan.md` con `/pv-how` sobre un fixture → `.metadata.json.risk` escrito, `plan.md` sin `**Risk**`.
    - `pv-status` (chat y `--terminal`) sigue mostrando el riesgo, ahora desde `.metadata.json`.
    - `pv-update` sobre un fixture con `plan.md` viejo (`**Risk**: 6/10 — ...`) en `inProgress`: migra el valor, limpia el header, no reporta `marker-missing`.
    - `pv-update` sobre un fixture `closed/` con `**Risk**`: escribe `.metadata.json.risk`, deja el `plan.md` intacto; `filter_status.py closed` muestra el número.
    - un `fast` entry sigue mostrando `Risk: ?`.

---

## 7. Decisiones (cerradas)

**7.1 — `changes/closed/*`: ¿migrar?** → **Sí, solo-lectura.** `pv-update` lee el `**Risk**` del `plan.md` de `closed` y escribe `.metadata.json`, **sin tocar el `plan.md`**. Así `filter_status.py <closed>` sigue mostrando el número en vez de `?`.

**7.2 — ¿Persistir `riskMeaning`?** → **No.** Se deriva siempre de la mediana con la tabla de `PLAN.template.md`. `.metadata.json` solo guarda el entero.

**7.3 — ¿La migración de `pv-update` corre sola?** → **Sí.** Forma parte de la auditoría normal de `/pv-update`, sin modo aparte ni pregunta. Idempotente.

**7.4 — ¿`set-metadata.py --set-risk` valida el estado?** → **Ya resuelto por el change 1.** `resolve_entry_dir` rechaza cualquier carpeta bajo `todo/` (o `--state todo`) para **toda** operación, sin importar si es de flags o de risk. No hay nada que añadir.

**7.5 — ¿Borrar `risk` (volver a "no evaluado")?** → **No soportado.** Una vez `pv-how` lo escribe, siempre hay un entero 0-10. `--set-risk` solo acepta `0`-`10`. El schema mantiene `null` como valor legible por robustez, pero ningún camino del framework lo escribe.

**7.6 — Tipo de `risk` en los dicts de `pv-status`.** → **`int | None` en ambos scripts.** Se corrige la inconsistencia preexistente (`filter_status.py`'s `extract_risk` devolvía `str`). **Consecuencia:** `filter_status.py`'s render usa hoy `if entry["risk"]` (truthiness), que con `int` trataría `risk == 0` como `?`. Se cambia a `is not None` en `render_report` (L405) y `render_terminal` (L472). `collect_status.py`/`render_status.py` no se ven afectados (`render_status.py` ya usa `is not None`; `collect_status.py` no formatea).

**7.7 — ¿`read_risk` se duplica en los dos scripts de `pv-status`?** → **No.** `filter_status.py` ya importa de `collect_status.py` (`read_flags`, `parse_todo_description`). `read_risk` se define una vez en `collect_status.py` y se añade a ese import. La afirmación del borrador original de que `pv-status/scripts` no tiene imports cruzados era incorrecta.

**7.8 — ¿`audit-context.py` necesita cambios para `risk`?** → **No.** El change 1 ya lo dejó validando `risk` (`METADATA_ALLOWED_KEYS` lo incluye; `check_metadata_files` valida rango 0-10 excluyendo `bool`; emite `metadata-risk-invalid:*`). El marker-check tampoco: no hay lista de labels hardcodeada, lee `[[[...]]]` de `PLAN.template.md` en cada ejecución, así que quitar `[[[Risk]]]` de la plantilla basta.

---

## 8. Documentación afectada

> Se actualiza **cuando el change se implementa**. Cada doc `pv-*` con par `.es.md` / `.en.md` se edita en las dos versiones a la vez.

| Fichero | Qué cambia |
|---|---|
| `.claude/skills/pv-internal-workflow/scripts/set-metadata.py` | Nuevo `--set-risk N` (0-10); relajar el guard "nothing to do"; rama de risk en la confirmación de salida; docstring (quitar *"the risk plan will add"*, documentar `--set-risk`). |
| `.claude/skills/pv-internal-workflow/metadata.schema.json` | `description` de `risk`: quitar *"This plan (flags) never writes it"*, poner que lo escribe `pv-how` vía `set-metadata.py --set-risk`; "absent = not yet assessed". |
| `.claude/pv-doc/pv-design/pv-design.es.md` **+** `.en.md` | **Convención de marcadores** (L444-468): **no cita `**Risk**`**, nada que tocar (solo confirmar). **L103** (resp. `pv-how`): *"escribe la mediana devuelta en la cabecera del plan"* → *"...en `.metadata.json` vía `set-metadata.py --set-risk`"*. **L212** (resp. `metadata.schema.json`): `risk` *"declarado pero no escrito por este flujo"* → *"escrito por `pv-how` vía `set-metadata.py --set-risk`; ausente = aún no evaluado"*. **L122** (ficha `filter_status.py`): la línea 1 no cambia, solo el origen del dato. Añadir migración one-shot de `pv-update` si hay bloque de resp. para ella. |
| `.claude/pv-doc/pv-guide.es.md` **+** `.en.md` | **Un solo sitio**: L353, lista de "**Tres** cosas se quedan siempre en inglés" — cita `**Risk**` entre las *"etiquetas de campo markdown que los scripts parsean literalmente en `description.md` y `plan.md`"* (`**Type**`, `**Name**`, `**Creation date**`, `**Risk**`, `## Idea`...). Quitar `**Risk**` de esa enumeración (ya no se parsea de `plan.md`; `**Creation date**` sí sigue). El Paso 2 (L219-227) describe `pv-how` **sin mencionar el riesgo** — no hay nada que tocar ahí. La descripción de `pv-status` tampoco cambia. |
| `.claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md` **+** `.en.md` | **L476**: *"`Risk` (línea 1): `plan.md`'s campo `**Risk**`, formato `{valor}/10` — `?` si no hay `plan.md` o el campo no tiene ese formato"* → *"`.metadata.json`'s `risk`, formato `{valor}/10` — `?` si el campo está ausente"*. Los ejemplos visuales (L457/464/472/482/485) **no cambian**. **No cita `extract_risk`/`RISK_RE`.** Sí describe `set-metadata.py` como *"único escritor de `.metadata.json` (**flags**)"* y `.metadata.json` como *"estado mutable... `flags`"* en **L223, L268, L611, L622** — ampliar cada uno a *"`flags` + `risk`"* (o *"flags y el riesgo"*). `pv.py` **no** invoca `--set-risk` (solo `pv-how` lo hace) — dejar claro que `pv.py` sigue usando `set-metadata.py` solo para flags. |
| `README.es.md` **+** `README.md` | Solo si mencionan el campo `**Risk**` de `plan.md`. Probablemente nada. |
| `pv-how/SKILL.md` + `pv-how/workflow.how.md` + `pv-how/PLAN.template.md` | Bloque "Language" (L16, fuera `**Risk**` de "the two header fields" y de la frase *"`filter_status.py` parses **Creation date** and **Risk** literally (`extract_date`/`extract_risk`)"* → solo **Creation date**/`extract_date`) + pasos 3 / 3.1 / check (L106-121, inglés — fuente canónica): paso 3 ya no dice "don't write `**Risk**` yet"; paso 3.1 invoca `set-metadata.py --set-risk {median}` en vez de editar el header; el check reconfirma `.metadata.json.risk`. `PLAN.template.md` sin `[[[Risk]]]` (línea 2 fuera); conservar/reetiquetar la tabla de "Meaning" (sección f). |
| `pv-status/SKILL.md` | **Probablemente nada.** Solo menciona `Risk` como columna de la tabla de salida (L64), sin describir su origen ni citar `parse_risk`/`extract_risk`. Confirmar en la relectura. |
| `pv-update/SKILL.md` | Quitar `**Risk**` de la prosa de ejemplo de `marker-missing:*` (~L44 y ~L91) — no funcional pero desactualizado. Nueva migración one-shot `plan.md` → `.metadata.json` (los 3 estados; `closed` solo-lectura). |
| ~~`pv-update/scripts/audit-context.py`~~ | **Sin cambios.** El change 1 ya lo dejó validando `risk` (rango 0-10, `metadata-risk-invalid:*`). Solo se comprueba en pruebas. |
| `dev-changelog/SKILL.md` | Revisar si su lógica lee `**Risk**` de `plan.md` (no debería — trabaja sobre `description.md` de `closed/`). |

---

## 9. Traducción de la documentación a inglés

Paso final, **después** de §8. Igual que en el plan de flags:

- **Fuente editada = ES** → generar la `.en.md` con **`en-translate`**: `pv-design.es.md`, `pv-guide.es.md`, `pv-design-onescript.es.md`, `README.es.md`.
- **Fuente canónica = inglés** (se edita directo en EN; si hiciera falta la ES, `es-translate`): los `SKILL.md`, `workflow.how.md`, `PLAN.template.md`. La documentación técnica (`architectureDocDir` / `styleBibleDocDir`) es siempre inglés y no tiene par ES.
- No cerrar la documentación hasta que cada par `.es.md` / `.en.md` sea equivalente (misma estructura, tablas, ejemplos).
