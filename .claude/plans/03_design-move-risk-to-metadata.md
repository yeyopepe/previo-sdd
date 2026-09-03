# Diseño: mover `risk` del header de `plan.md` a `.metadata.json`

**Fecha:** 2026-09-03
**Estado:** borrador para revisar — **no implementado**
**Depende de:** [`design-metadata-json-flags.md`](design-metadata-json-flags.md) — este plan **asume** que ya existe `{workFolder}/changes/{state}/{xxxx}/.metadata.json`, su `metadata.schema.json`, y el script `set-metadata.py` en `pv-internal-workflow`. Es el "change 2": no tiene sentido abordarlo hasta que el sistema de flags (change 1) esté implementado.
**Disparador:** el valor de riesgo (mediana de los 9 factores de `pv-internal-tech-risks`) hoy se escribe como campo `**Risk**` en el header de `plan.md`. En realidad es un **dato de estado** puntual, no parte del diseño técnico — y `pv-status` lo tiene que parsear con regex de un `.md`. Moverlo a `.metadata.json.risk` lo deja en un solo sitio, parseable sin ambigüedad, junto al resto de estado mutable del cambio.

---

## 1. Alcance

Un único cambio de dato: `risk` deja de vivir en `plan.md` y pasa a `.metadata.json`.

- **NO** se toca la sección opcional `## (f) Risk analysis` de `plan.md` (los 9 factores en prosa, solo si el usuario los pidió). Eso es *análisis*, se queda donde está.
- **NO** cambia quién calcula el riesgo (`pv-internal-tech-risks`) ni cuándo (`pv-how` paso 3.1, tras escribir `plan.md`).
- **SÍ** cambia dónde lo escribe `pv-how`, cómo lo leen los 2 parsers de `pv-status`, la plantilla `PLAN.template.md`, la convención de marcadores, y el marker-check + una migración one-shot en `pv-update`.

---

## 2. Campo en `.metadata.json`

```json
{
  "flags": [],
  "flagsLastModified": "2026-09-03",
  "risk": 5
}
```

- **`risk`** (entero 0-10 | `null`): la mediana de los 9 factores. `null` o campo ausente = todavía no evaluado — equivale al `?` que hoy muestra `pv-status` cuando `plan.md` no tiene el campo (`fast` entries, o cambios aún sin `pv-how`).
- Ya está contemplado en el `metadata.schema.json` del change 1:
  ```json
  "risk": { "type": ["integer", "null"], "minimum": 0, "maximum": 10 }
  ```
- `set-metadata.py` ya expone `--set-risk <0-10>` (definido en el change 1 para no dispersar la lógica de read-modify-write de `.metadata.json`).

---

## 3. Pipeline actual de `risk` (lo que hay que cambiar)

1. **`pv-how` paso 3** escribe `plan.md` **sin** el campo `**Risk**` (explícito en su `SKILL.md`: "don't write the header's `**Risk**` field yet ... it's added in step 3.1").
2. **`pv-how` paso 3.1** invoca `pv-internal-tech-risks` (no escribe nada, solo devuelve los 9 factores + mediana) y **edita el header de `plan.md`** añadiendo, bajo `**Creation date**`, el campo `**Risk**: {median}/10 — {meaning}` (el `{meaning}` sale de la tabla de la plantilla).
3. **`pv-how` paso 3.1** tiene un check duro: no dar `plan.md` por terminado, ni pasar al paso 3.2, sin confirmar que el header ya tiene `**Risk**` con valor real (nunca placeholder).
4. **`PLAN.template.md`** línea 2: `- **[[[Risk]]]**: [median 0-10 returned by pv-internal-tech-risks] — [description...]` → el `[[[Risk]]]` lo marca como **marcador estructural obligatorio**.
5. **`pv-status`** lo parsea en **2 ficheros**:
   - `collect_status.py`: `parse_risk(plan_path)` + `RISK_RE` (`re.compile(r"\*\*Risk\*\*\s*[:—-]\s*(\d{1,2})\s*/\s*10")`).
   - `filter_status.py`: `extract_risk(text)` + su propio `RISK_RE` (misma regex, ~línea 89).
   - `render_status.py`: `format_risk(entry)` **solo consume `entry["risk"]`** del dict que arma `collect_status.py` — no parsea `plan.md` directamente.
6. **`pv-update`** marker-check (`marker-missing:*`, `SKILL.md` ~línea 44): `**Risk**` está entre los labels obligatorios que compara contra `PLAN.template.md`.
7. Sección opcional `## (f) Risk analysis` de `plan.md`: los 9 factores en prosa, solo si el usuario los pidió. **Independiente del header.**

---

## 4. Pipeline propuesto

1. **`pv-how` paso 3**: igual — `plan.md` sin nada de riesgo en el header. (De hecho más simple: ya no hay un "campo que se añade después".)
2. **`pv-how` paso 3.1**: tras `pv-internal-tech-risks`, en vez de editar `plan.md`, invoca:
   ```
   python .claude/skills/pv-internal-workflow/scripts/set-metadata.py --xxxx {xxxx} --set-risk {median}
   ```
   (con `--work-folder` si aplica). Esto **crea `.metadata.json`** si aún no existe. `pv-how` no escribe JSON a mano — coherente con que las skills deleguen las mutaciones de ficheros del framework en scripts (mismo criterio que `move-change.py`, `delete-todo.py`).
   - El `{meaning}` textual ("Moderate risk", etc.) **deja de persistirse** — era derivable de la mediana vía la tabla de la plantilla. Quien lo quiera mostrar (p.ej. `pv-status` en chat) lo deriva de `risk` con esa misma tabla. Alternativa: guardarlo también como `riskMeaning` en `.metadata.json` — no recomendado, es redundante.
3. **`pv-how` check**: "no terminar el `plan.md` / no pasar al paso 3.2 sin `.metadata.json.risk` con valor entero real (0-10, no `null`)".
4. **`PLAN.template.md`**: quitar la línea `- **[[[Risk]]]**: ...` del header. El header queda solo con `- **[[[Creation date]]]**: ...`. Ajustar cualquier texto de la plantilla que numere/menciona ese campo, y su sección de notas de autoría.
5. **`pv-status`**:
   - Nueva función compartida `read_risk(entry_dir) -> int | None` (o reutilizar el `read_metadata()` que el change 1 ya introduce para `flags`) que lee `.metadata.json.risk`.
   - `collect_status.py`: `parse_risk()` pasa a delegar en `read_risk(entry_dir)`. Firma `parse_risk(entry_dir)` en vez de `parse_risk(plan_path)`. **Eliminar `RISK_RE`** de este fichero.
   - `filter_status.py`: `extract_risk()` → `read_risk(entry_dir)`. **Eliminar `RISK_RE`** de este fichero.
   - `render_status.py`: **sin cambios** — `format_risk(entry)` sigue leyendo `entry["risk"]`, que `collect_status.py` ahora rellena desde `.metadata.json`. Es el punto que hace este refactor viable: el render no toca la fuente.
   - Plantillas `STATUS.template.md` / `STATUS.filtered.template.md`: la columna `Risk` **no cambia** (el dato llega ya resuelto en el dict). Si se quiere mostrar el "meaning" textual, se deriva de la mediana.
6. **`pv-update`**:
   - **Quitar `**Risk**`** de la lista de labels obligatorios del marker-check de `plan.md`. Si no, todo `plan.md` nuevo (ya sin el campo) daría `marker-missing:**Risk**`.
   - **Migración one-shot**: por cada carpeta bajo `changes/inProgress/*` y `changes/implemented/*` con `plan.md` que tenga el campo `**Risk**`:
     1. parsear su valor (misma regex que hoy),
     2. `set-metadata.py --xxxx {xxxx} --set-risk {N}` (o escribir `.metadata.json` directamente desde `pv-update`, ya que es una operación de reparación),
     3. eliminar la línea `- **Risk**: ...` del header de `plan.md`.
   - `changes/closed/*`: historia congelada, **no se migra** — se deja el `**Risk**` muerto en esos `plan.md` (nadie los parsea; `filter_status.py` sí puede listar `closed`, pero el `risk` de un cambio ya cerrado no aporta). *Decisión abierta §7.1.*
   - Añadir la validación de `.metadata.json.risk` contra el schema (rango 0-10) — probablemente ya cubierto por la auditoría de schema que introduce el change 1.
7. **`pv-design.*.md`** ("Marker convention in templates", ambos idiomas): quitar `**Risk**` de la lista de ejemplos de marcadores de `PLAN.template.md`; si hay una tabla de "qué marca cada plantilla", actualizarla.
8. **`pv-how/SKILL.md`**: reescribir los pasos 3, 3.1 y el check (líneas ~106-121 hoy) para reflejar que el valor va a `.metadata.json` vía `set-metadata.py`, no al header. Es el fichero con más texto que cambiar — documenta el pipeline con mucho detalle, incluida la interacción con la convención de marcadores y con `filter_status.py`.

---

## 5. Retrocompatibilidad

- **Carpetas existentes con `**Risk**` en `plan.md`**: hasta que `pv-update` corra la migración, `pv-status` mostraría `risk: ?` para esos cambios (los parsers nuevos no miran `plan.md`). Estado transitorio aceptable, **pero hay que documentarlo** y probablemente hacer que `pv-update` lo corra automáticamente al detectar `plan.md` con `**Risk**` y sin `.metadata.json.risk`.
- **`fast` entries**: nunca tuvieron `plan.md` → nunca tuvieron `risk` → siguen mostrando `?`. Sin cambio.
- **Proyectos en versión anterior del framework**: al actualizar, `pv-update` corre la migración.
- **`changes/closed/*`**: ver §4.6 — se dejan como están.

---

## 6. Orden de implementación

1. `/pv-new` + `/pv-how` para documentar este change (tras el change 1).
2. `pv-status`: `read_risk()` compartido → `collect_status.py` (delegar `parse_risk`, borrar `RISK_RE`) → `filter_status.py` (delegar `extract_risk`, borrar `RISK_RE`). Verificar `render_status.py` intacto.
3. `pv-how`: reescribir pasos 3 / 3.1 / check en `workflow.how.md` y `SKILL.md`; invocar `set-metadata.py --set-risk`.
4. `PLAN.template.md`: quitar `[[[Risk]]]`.
5. `pv-design.es.md` + `pv-design.en.md`: "Marker convention" sin `**Risk**`.
6. `pv-update`: quitar `**Risk**` del marker-check; añadir la migración one-shot `plan.md` → `.metadata.json`.
7. **Documentación en español** (§8): actualizar todos los ficheros del checklist.
8. **Traducción a inglés** (§9): regenerar cada `.en.md` desde su `.es.md` con `en-translate` (traduce *hacia* inglés) (y editar los `SKILL.md` / plantillas directamente en inglés).
9. Pruebas:
   - regenerar un `plan.md` con `/pv-how` sobre un fixture y verificar que `.metadata.json.risk` queda escrito y `plan.md` no tiene `**Risk**`.
   - `pv-status` (chat y `--terminal`) sigue mostrando el riesgo, ahora desde `.metadata.json`.
   - `pv-update` sobre un fixture con `plan.md` de formato viejo (`**Risk**: 6/10 — ...`): migra el valor, limpia el header, no reporta `marker-missing`.
   - un `fast` entry sigue mostrando `Risk: ?`.

---

## 7. Decisiones abiertas

**7.1 — `changes/closed/*`: ¿migrar o dejar el `**Risk**` muerto?** Propuesta: dejarlo (historia congelada, nadie parsea `closed` para riesgo). Contra: `filter_status.py <closed>` mostraría `Risk: ?` para cambios cerrados que antes mostraban un número. Si molesta, migrar también `closed` en la one-shot (solo lectura del valor + escritura de `.metadata.json`, sin tocar el `plan.md` de `closed`).

**7.2 — ¿Persistir el "meaning" textual (`riskMeaning`) o derivarlo siempre de la mediana?** Propuesta: derivarlo (tabla en la plantilla / en un helper de `pv-status`), no persistirlo — es redundante con `risk`.

**7.3 — ¿La migración de `pv-update` corre sola o solo cuando el usuario invoca `/pv-update`?** Propuesta: forma parte de la auditoría normal de `/pv-update` (como el resto de reparaciones que hace sin preguntar), no un modo aparte.

**7.4 — ¿`set-metadata.py --set-risk` valida que el estado sea `inProgress`/`implemented`?** Un `todo` no debería tener `risk`. Propuesta: el script rechaza `--set-risk` si la carpeta resuelta está bajo `todo/`.

---

## 8. Documentación afectada

> Igual que en el plan de flags: se actualiza **cuando el change se implementa**. Cada doc `pv-*` con par `.es.md` / `.en.md` se edita en las dos versiones a la vez.

| Fichero | Qué cambia |
|---|---|
| `.claude/pv-doc/pv-design/pv-design.es.md` **+** `.en.md` | **Convención de marcadores en plantillas**: quitar `**Risk**` de la lista de etiquetas marcadas con `[[[...]]]` en `PLAN.template.md`. Si hay tabla "qué marca cada plantilla", actualizar la fila de `plan.md`. **Responsabilidades**: `pv-how` ya no escribe `risk` en `plan.md` sino en `.metadata.json` vía `set-metadata.py`; `pv-update` gana la migración one-shot `plan.md` → `.metadata.json` para `risk`. **`collect_status.py` / `filter_status.py`**: el riesgo se lee de `.metadata.json.risk`, no de `plan.md`. |
| `.claude/pv-doc/pv-guide.es.md` **+** `.en.md` | Donde menciona que `/pv-how` "escribe la mediana de riesgo en la cabecera del plan" (~línea 224-227 y la lista de "Tres cosas se quedan en inglés" ~línea 353, que cita `**Risk**` como etiqueta parseada en `plan.md`): actualizar a "lo escribe en `.metadata.json`". Quitar `**Risk**` de la lista de etiquetas `[[[...]]]` de `description.md`/`plan.md` si aparece. La descripción de `pv-status` (muestra el riesgo) no cambia — el dato sigue apareciendo, solo cambia su origen. |
| `.claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md` **+** `.en.md` | Revisar la "Ficha Detalle": la línea `Risk: N/10` sigue igual visualmente, pero si el texto explica que sale de `plan.md`'s `**Risk**` (`extract_risk`/`RISK_RE`), corregir a `.metadata.json.risk`. La tabla de "Dependencias Externas" no cambia (mismos scripts). |
| `README.es.md` **+** `README.md` | Solo si mencionan el campo `**Risk**` de `plan.md`. Probablemente nada. |
| `pv-how/SKILL.md` + `pv-how/workflow.how.md` + `pv-how/PLAN.template.md` | Reescritura de los pasos 3 / 3.1 / check (inglés — fuente canónica). `PLAN.template.md` sin `[[[Risk]]]`. |
| `pv-status/SKILL.md` | `collect_status.py` / `filter_status.py` leen `risk` de `.metadata.json`; `RISK_RE` eliminado. |
| `pv-update/SKILL.md` | `**Risk**` fuera del marker-check; nueva migración one-shot `plan.md` → `.metadata.json`. |
| `dev-changelog/SKILL.md` | Revisar si su lógica lee `**Risk**` de `plan.md` (no debería — trabaja sobre `description.md` de `closed/`). |

---

## 9. Traducción de la documentación a inglés

Paso final, **después** de §8. Igual que en el plan de flags:

- **Fuente editada = ES** → generar la `.en.md` con **`en-translate`** (la skill se nombra por el idioma destino: `en-translate` = hacia inglés): `pv-design.es.md`, `pv-guide.es.md`, `pv-design-onescript.es.md`, `README.es.md`.
- **Fuente canónica = inglés** (se edita directo en EN; si hiciera falta la ES, `es-translate`): los `SKILL.md`, `workflow.how.md`, `PLAN.template.md`. La documentación técnica (`architectureDocDir` / `styleBibleDocDir`) es siempre inglés y no tiene par ES.
- No cerrar la documentación hasta que cada par `.es.md` / `.en.md` sea equivalente (misma estructura, tablas, ejemplos).
