# Diseño: `.metadata.json` por cambio — sistema de `flags`

**Fecha:** 2026-09-03
**Estado:** borrador para revisar — **no implementado**
**Disparador:** el usuario quiere des/marcar cambios con **flags** — un conjunto extensible de etiquetas de estado, de momento `priority` (⭐) y `workinprogress` (⚙️) — y que **todas las listas de cambios de `pv.py`** muestren los iconos de las flags que tenga cada cambio.
**Fuera de alcance (plan aparte):** mover el `risk` del header de `plan.md` a este mismo fichero → [`design-move-risk-to-metadata.md`](design-move-risk-to-metadata.md) ("change 2"). Este plan solo introduce `.metadata.json` + `flags`; el campo `risk` se añade después, reusando el fichero y el script que aquí se crean.
**Ideas descartadas:** guardar el código dentro del fichero (§2); un único booleano `priority` en vez del array `flags` (§3).
**Nota de alcance:** el grueso del plan es **aditivo** (fichero nuevo, script nuevo, prefijo de iconos que se antepone). La **única excepción** es la decisión 6.14 (§4.2.1): reordena los campos de la línea 1 de las fichas de `filter_status.py` y `render_status.py`, que ya existen hoy — es un cambio de formato visible para usuarios que no usan flags. Tratar como parte del scope explícito, no como detalle de implementación.

---

## 0. TL;DR de la recomendación

1. **Sí** a un fichero de estado mutable por cambio: `.metadata.json` en `{workFolder}/changes/{state}/{xxxx}/`, junto a `description.md` / `plan.md` / `history.md`. Dotfile: no ensucia el `ls` de la carpeta, que sigue mostrando solo los `.md` de documentación.
2. **`flags`: array de strings**, no un booleano por concepto. Valores válidos hoy: `"priority"` (⭐), `"workinprogress"` (⚙️). Añadir una flag futura = un valor al enum del schema + su icono/label en un mapa, sin tocar el shape ni la firma de los scripts. Un cambio puede tener 0, 1 o varias.
3. **Solo los cambios llevan flags, nunca los `todo`.** Un `todo` es una idea suelta fuera del flujo; no hay nada "en progreso" ni "priorizado dentro del flujo" que marcar. `set-metadata.py` rechaza cualquier operación sobre una carpeta bajo `todo/`, y `pv-update` reporta cualquier `.metadata.json` que aparezca ahí.
4. **No** duplicar el código dentro del fichero. El código ya es el nombre de la carpeta y está en `description.md`.
5. Esto **no es una feature de `pv.py`** — es un **contrato de datos del framework**. Toca `pv-internal-workflow` (crea/mueve carpetas + script de mutación + schema), `pv-status` (lee flags, pinta iconos, filtra), `pv-update` (audita). `pv.py` pone los botones de toggle y muestra los iconos, delegando toda escritura en el script nuevo.

---

## 1. Qué problema resuelve exactamente

Hoy el estado de un cambio es **solo su carpeta de workflow** (`inProgress` / `implemented` / `closed`; `todo` es aparte) + `subStatus` derivado (`described` vs `ready_to_implement`). No hay forma de decir *"de los 6 que tengo en `inProgress`, en estos 2 estoy metido ahora mismo"* ni *"estos 3 son los que más me urgen"*.

Las **flags** son **ortogonales al workflow**: un cambio en `inProgress` puede estar `workinprogress` (activo ahora) o no; puede llevar `priority` para subir en la cola. Es una capa de *foco personal* encima del ciclo de vida, y **multivalor**: `priority` y `workinprogress` son independientes y un cambio puede tener las dos.

| flag | icono | label (UI) | significado |
|---|---|---|---|
| `priority` | ⭐ | Priority | marcado como prioritario |
| `workinprogress` | ⚙️ | Work in progress | se está trabajando activamente en este cambio ahora mismo |

El conjunto es **abierto**: añadir una tercera flag (`blocked` 🚫, `review` 👀…) = un valor en el enum del schema + una entrada en el mapa icono/label. Nada más.

**`workinprogress` (la flag) ≠ `inProgress` (la carpeta):** la flag es "estoy tecleando en esto ahora"; la carpeta es "fase del ciclo de vida". Un cambio puede estar en `inProgress` sin la flag, y llevar `workinprogress` estando en `implemented` (retoques post-implementación — confirmado).

---

## 2. Por qué un fichero nuevo y no reutilizar `description.md`

| Opción | Problema |
|---|---|
| Campos en `description.md` | Es documentación *del cambio* (qué es, por qué), redactada una vez por `pv-new`/`pv-fix` y luego casi inmutable. Meterle flags que se togglean a diario mezcla dos ritmos de escritura y ensucia los diffs de documentación. Además la escribe el modelo en prosa; un toggle quiere JSON parseable sin ambigüedad. |
| Campo en `plan.md` | Puede no existir aún (un `inProgress/described` no tiene `plan.md`). Las flags tienen que poder existir antes que el plan. |
| Índice central (`{workFolder}/changes/_flags.json`) | Un único fichero que toda operación de workflow tendría que actualizar al mover/borrar carpetas → punto único de contención y corrupción, y se desincroniza si alguien mueve una carpeta a mano. |
| **`.metadata.json` por carpeta** | **Elegida.** Local a la carpeta, viaja con ella en el `git mv` de `move-change.py`, no colisiona con la documentación, JSON parseable. Dotfile → invisible en un `ls` normal, como `.gitignore`. |

---

## 3. Contenido de `.metadata.json`

Solo estado mutable — lo que cambia sin re-documentar el cambio:

```json
{
  "flags": ["priority", "workinprogress"],
  "flagsLastModified": "2026-09-03"
}
```

- **`flags`** (array de strings, sin duplicados): las etiquetas activas. Valores válidos: los del enum del schema (hoy `"priority"`, `"workinprogress"`). `[]`, campo ausente o fichero ausente = sin flags (§5). El orden en el array no es significativo; los consumidores lo normalizan al pintar (⭐ siempre antes que ⚙️).
- **`flagsLastModified`** (string fecha ISO `YYYY-MM-DD`, opcional): cuándo se tocó por última vez `flags` (añadir **o** quitar cualquier flag). **Un único timestamp global** (confirmado) — no uno por flag. **`set-metadata.py` lo escribe; ningún consumidor de este plan lo lee** — se guarda para uso futuro (ordenar por actividad reciente, detectar marcas viejas olvidadas), igual que `risk` queda declarado en el schema sin que este plan lo escriba. Decisión 6.10.

> El campo **`risk`** se añade en el plan aparte ([`design-move-risk-to-metadata.md`](design-move-risk-to-metadata.md)). El `metadata.schema.json` de este plan ya deja hueco para él (`"risk"` opcional) para no tener que re-tocar el schema en el change 2.

**Por qué array y no `{"priority": bool, "workinprogress": bool}`:** con objeto de booleanos, añadir una flag obliga a que todos los lectores conozcan la clave nueva o la traten como `false` implícito, y "¿qué flags existen?" no está en ningún sitio. Con array + enum en el schema, el catálogo vive en **un** sitio, añadir una es additivo, e iterar "los iconos de este cambio" es un `for f in flags`.

### Lo que **NO** va aquí

- **El código.** Es el nombre de la carpeta. Redundante y genera trabajo de reconciliación para `pv-update`.
- **El estado de workflow** (`inProgress`, etc.). Es la carpeta padre.
- **`type`, `name`.** Se derivan de `description.md`.
- Nada que `pv-do` / `pv-version` necesiten *escribir* como parte de su lógica.

### Schema

Un JSON Schema propio: `.claude/skills/pv-internal-workflow/metadata.schema.json`, referenciado por los scripts que leen/escriben `.metadata.json` y por `pv-update` para auditar (igual que `pv-init/schema.json` para `pv-context.json`). El enum de `flags` es el **catálogo canónico** de flags del framework.

```json
{
  "$id": "metadata.schema.json",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "flags": {
      "type": "array",
      "uniqueItems": true,
      "items": { "enum": ["priority", "workinprogress"] }
    },
    "flagsLastModified": { "type": "string" },
    "risk": { "type": ["integer", "null"], "minimum": 0, "maximum": 10 }
  }
}
```

(`risk` queda declarado aunque este plan no lo escriba nunca — lo usará el change 2 sin re-tocar el schema.)

---

## 4. Skills y scripts afectados

### 4.1 `pv-internal-workflow` — dueño del fichero

- **Creación.** `pv-new` / `pv-fix` crean la carpeta del cambio (vía `pv-internal-workflow`). Propuesta: **`.metadata.json` solo aparece cuando se añade la primera flag**. "Sin fichero = `flags: []`" mantiene limpias las carpetas que nadie ha marcado y hace la retrocompatibilidad un no-problema (§5).
- **Nuevo script `set-metadata.py`** (en `.claude/skills/pv-internal-workflow/scripts/`), additivo. Un único script para todas las mutaciones de `.metadata.json`:
  - `--xxxx <code>` + resolución del estado buscando la carpeta (o `--state <state>` explícito).
  - **Sobre `flags`:** `--add-flag <name>`, `--remove-flag <name>`, `--toggle-flag <name>` (repetibles). Valida `<name>` contra el enum del schema; error claro si no. Rechaza cualquier operación si la carpeta resuelta está bajo `todo/`. Actualiza `flagsLastModified` a la fecha de hoy en cada mutación efectiva.
  - `--work-folder` como override (mismo patrón que `move-change.py`) para que `pv.py --testconfig` lo apunte a fixtures.
  - Read-modify-write **con lock** (decisión 6.11): toma un file lock (sobre `.metadata.json` o un `.metadata.json.lock` adyacente) durante el ciclo leer-modificar-escribir, para que un toggle desde `pv.py` y otro desde una sesión de Claude Code en paralelo no se pisen. Nada de last-write-wins. Crea `.metadata.json` si no existe; **nunca borra** el fichero (aunque `flags` quede `[]`). Preserva campos desconocidos (p.ej. el `risk` que añade el change 2).
  - Salida: una línea de confirmación en texto plano (sin ANSI), como `delete-todo.py`. Además `--print`: emite el `.metadata.json` resultante como JSON, para que los callers no tengan que releerlo.
  - (El change 2 le añadirá `--set-risk <0-10>`; la firma no cambia para nada de flags.)
- **`move-change.py`**: **sin cambios — verificado.** Hace `shutil.move()` sobre el directorio completo (`scripts/move-change.py:100`), sin allowlist, sin `glob`, sin lista fija de ficheros. `.metadata.json` viaja dentro de la carpeta en todos los movimientos de workflow (`inProgress → implemented → closed`). El riesgo solo existiría si el script copiara fichero-a-fichero (`for f in source.glob("*.md")` o lista fija de nombres) — no es el caso.
- **`delete-todo.py`**: sin cambios (borra la carpeta entera).

### 4.2 `pv-status` — lo lee y lo expone

Aquí está el **valor real** de las flags: que el status las muestre y filtre.

- **Módulo compartido de `pv-status`** (donde vive `terminal_output.py` o uno nuevo): el **mapa canónico** flag → (icono emoji, icono ASCII, label humano) + helpers `flags_prefix(flags, color)` y `flag_label(value, color)` (pseudocódigo en §8.9). El mapa vive **aquí y solo aquí**; `pv.py` lo consume por el camino de §4.4.
- **`collect_status.py`** — `build_entry()` (~línea 157): añadir lectura de `.metadata.json` → nuevos campos `"flags": list[str]` (default `[]` si no hay fichero/campo o está mal formado; filtrar defensivamente valores fuera del enum) y opcionalmente `"flagsLastModified": str | None`.
- **`filter_status.py`**:
  - `render_terminal()` ficha detalle: **reordena la línea 1** a `flags · code · [type] · (status) · Risk` (decisión 6.14) — hoy es `(status)  code  [type]  Risk`; `status` se mueve a después del `[type]` y `flags_prefix()` va al principio del todo (`⭐⚙️  1001  [🔧 Fix]  (implemented)  Risk: 3/10`).
  - **Nuevo modo `--flag <name>`** (repetible, semántica **OR** — decisión 6.12): lista las entradas cuyo `flags[]` contiene **alguna** de las flags pasadas, cruzando estados — análogo a `--search-id` / `--search-content`. Sin modo AND: el caso de uso (`pv.py` "Show changes by flag", §8.5) elige **una** flag de una lista; si algún día hace falta intersección se añade un `--flag-mode all` explícito, no ahora.
- **`render_status.py`** (las 3 páginas de "Project status", chat y `--terminal`): cada fila/bloque de cambio antepone `flags_prefix(entry["flags"])` al id y **adopta el mismo orden de línea 1** (`flags · code · [type] · (status) · Risk`, decisión 6.14) para no divergir de `filter_status.py`. Orden fijo de iconos independientemente del orden del array. **Solo marcar** — no se reordena la *lista* por `priority` (confirmado); el reorden es de los *campos dentro de la línea*, no del orden de las entradas.
- **Plantillas** `STATUS.template.md` / `STATUS.filtered.template.md`: los iconos de flags van **en primer lugar**, como columna `Flags` inicial — tal y como se ve en el mockup de §8.6 (confirmado).
- **`list_todo.py`**: **sin cambios** — los `todo` no llevan flags.

#### 4.2.1 Reorden de la línea 1 de la ficha (decisión 6.14) — detalle

**Qué cambia.** La primera línea de cada ficha de cambio pasa de:
```
(inProgress)  00192  [🆕 Change]  Risk: 5/10        ← hoy
```
a:
```
⭐⚙️  00192  [🆕 Change]  (inProgress)  Risk: 5/10   ← nuevo
```
Orden canónico: **`flags · code · [type] · (status) · Risk`**. Dos movimientos: (a) `flags_prefix()` se antepone (aditivo, es la feature), y (b) **`(status)` se desplaza de la primera posición a después de `[type]`** (reorden real de un campo existente).

**Por qué el reorden y no solo anteponer.** Con `flags` delante, `(status)` en segunda posición deja el `code` —el dato que el usuario busca para identificar la entrada— en tercer lugar, detrás de dos elementos decorativos. Poniendo `code` inmediatamente tras las flags, la columna de códigos queda casi alineada entre entradas (los iconos son el único prefijo variable) y `(status)` / `Risk` quedan agrupados como metadatos al final.

**Alcance.** Afecta a **`filter_status.py`** (ficha detalle: `--search-id`, `--search-content`, `--state`, `--flag`) y a **`render_status.py`** (bloques de detalle de las 3 páginas de "Project status", chat y `--terminal`). **No** afecta a: las tablas markdown de `STATUS*.template.md` (tienen sus propias columnas, §8.6), `list_todo.py`, ni los listados propios de `pv.py` (§8.3/§8.4, formato `code — name` sin type/status/risk).

**Coste / riesgo.** Es un cambio de formato **visible para usuarios que no usan flags**. No rompe nada funcional (nadie parsea esa línea programáticamente: `pv.py` delega el render entero), pero:
- Cualquier documentación/screenshot que reproduzca la línea 1 queda obsoleta → checklist §9.
- Tests de `pv-status` que hagan *golden-file* / *snapshot* de la salida de `filter_status.py` o `render_status.py` fallarán y hay que regenerarlos.
- El paso 7 de pruebas verifica el orden nuevo **también en fichas sin flags**.

**Reversibilidad.** Alta — es un cambio de orden de concatenación en el `render_*()`, sin persistencia. Si se decide revertir, se revierte solo esto sin tocar nada de flags (el prefijo `flags_prefix()` es independiente del orden de los demás campos).

**Si se prefiere minimizar impacto:** alternativa descartada = anteponer `flags_prefix()` dejando `(status)` donde está (`⭐⚙️  (inProgress)  00192  [🆕 Change]  Risk`). Es puramente aditivo, cero regresión de formato, pero mantiene `code` en tercera posición. El usuario pidió explícitamente el orden `flags · code · type · status · risk` → se implementa el reorden.

### 4.3 `pv-update` — audita

- **Auditoría** de `.metadata.json` contra `metadata.schema.json`: JSON inválido, `flags` no-array o con valores fuera del enum, claves desconocidas. Repara/reporta según su política actual (igual que valida `pv-context.json` contra `schema.json`).
- **`.metadata.json` bajo `todo/`**: es un error (los `todo` no llevan flags) → `pv-update` lo reporta / borra.
- Las flags **no necesitan migración**: "sin fichero/campo = `flags: []`". Cero trabajo one-shot en este plan (el change 2 sí trae migración, para `risk`).

### 4.4 `pv.py` (vía `dev-onescript`)

Requisito explícito: **todas las listas de cambios de `pv.py` muestran los iconos de las flags de cada cambio.** Inventario:

| Listado | Origen | Cómo se muestran las flags |
|---|---|---|
| "General project status" (3 páginas) | delegado → `render_status.py --terminal` | lo pinta `render_status.py` (§4.2). `pv.py` no toca nada. |
| "Changes info > Search by state" | delegado → `filter_status.py <state> --terminal` | lo pinta `filter_status.py`. |
| "Changes info > Search by id / by content" | delegado → `filter_status.py --search-* --terminal` | ídem (ficha detalle, iconos en línea 1). |
| "Ideas in todo/" | delegado → `list_todo.py --terminal` | **nada** — los `todo` no llevan flags. |
| **"Close an implemented entry"** — `show_selection()` de `list_implemented_entries()` | **propio de `pv.py`** (`labels = f"{code} — {name}"`) | **cambio en `pv.py`**: anteponer iconos al label. |
| **"Toggle a flag on a change"** (nuevo) — `show_selection()` de cambios | **propio de `pv.py`** | el listado de selección muestra los iconos actuales. |

La mayoría "sale gratis" (render delegado; el trabajo está en `pv-status`). Lo **propio de `pv.py`** es leer `.metadata.json` por carpeta para `list_implemented_entries()` y el listado de la opción nueva.

**Cómo obtiene `pv.py` los iconos sin duplicar el mapa.** El mapa flag→icono/label vive en `pv-status` (§4.2), y `pv.py` es un fichero único autocontenido que **no importa nada** — así que no puede reutilizar ese mapa por import. La solución: un **script de solo lectura nuevo en `pv-status`**, `read-flags.py`, que `pv.py` invoca vía `run_script()` igual que ya invoca `render_status.py` / `filter_status.py`. Interfaz mínima:
- `read-flags.py --xxxx <code> [--xxxx <code> ...] [--state <state>] [--work-folder <path>] --terminal` → **acepta varios `--xxxx` en una sola invocación** (decisión 6.13) y emite **una línea por código**, en el mismo orden, con el `flags_prefix` ya renderizado (`⭐ ⚙️  `, respetando `NO_COLOR`) o línea vacía si ese cambio no tiene flags.
- `pv.py`'s `list_implemented_entries()` lo llama **una sola vez** con todos los códigos de la lista y reparte las líneas de salida por posición — **1 subproceso, no N** (el arranque de Python en Windows es lento; batch de entrada desde el día 1, no como optimización posterior).
- Va a `SCRIPTS_ACCEPTING_WORK_FOLDER` (y `SCRIPTS_ACCEPTING_WIDTH` si necesita el ancho).

Detalle fino (formato exacto de salida, qué hace si un `--xxxx` no resuelve) al plan técnico; las decisiones de diseño — *script de lectura, no import* + *batch de entrada* — están tomadas.

**Opciones de menú nuevas:**
- **"Toggle a flag on a change"** (muta estado) — dentro de "Changes info": `show_selection()` de cambios → `show_selection()` de flags (labels legibles "Priority" / "Work in progress", con `[x]`/`[ ]` según estén activas) → `confirm()` → `run_script(WORKFLOW_SCRIPTS / "set-metadata.py", "--xxxx", code, "--toggle-flag", value)`. Patrón "opción que muta estado" del design doc. Los labels son presentación; al script se le pasa el valor del enum.
- **"Show changes by flag"** (solo lectura) → `run_script(STATUS_SCRIPTS / "filter_status.py", "--flag", value, "--terminal")`.
- Posible: en la Selección incrustada de la ficha detalle (hoy "Delete this idea" para `todo`), añadir "Toggle Priority" / "Toggle Work in progress" para cambios (no `todo`).

**Mecánica:**
- `SCRIPTS_ACCEPTING_WORK_FOLDER` en `pv.py`: añadir `set-metadata.py` (y el script de lectura si se crea). `filter_status.py` ya está ahí, y con `--flag` sigue igual.
- **Sin escritura directa de `pv.py`** a `.metadata.json` — todo por `run_script()`. (Contrasta con `framework.onescript.width`, escalar único en `pv-context.json`; aquí hay un script dueño en `pv-internal-workflow`.)
- Actualizar **ambos** design docs de `pv.py` (`.es`/`.en`): jerarquía de pantallas, grafo de navegación, dependencias externas (scripts nuevos), nota de que `filter_status.py` gana el modo `--flag`, y una nota en "Estilo / Info delegada" sobre el prefijo de iconos.

---

## 5. Retrocompatibilidad

- **Carpetas existentes** (sin `.metadata.json`): todos los lectores tratan "fichero/campo ausente" como `flags: []`. **Cero migración.**
- **Proyectos en versión anterior del framework**: al actualizar, nada que hacer para flags; el primer toggle crea el fichero.
- **`git`**: `.metadata.json` se versiona como cualquier otro fichero de la carpeta. **Confirmar que no cae en un `.gitignore`** de `workFolder` — al ser dotfile, un `.gitignore` con `*` + `!*.md` lo excluiría.
- **Herramientas que listan la carpeta** (`ls`, `glob`): al ser dotfile no aparece por defecto — deseable para no ensuciar. `move-change.py` ya lo arrastra (mueve el directorio entero, §4.1 — verificado); cualquier copia recursiva futura tiene que incluir dotfiles.
- **Concurrencia**: `set-metadata.py` usa file lock (§4.1, decisión 6.11), así que dos toggles simultáneos (`pv.py` + Claude Code) no corrompen ni pierden flags. No hay lock entre *lectores* (`read-flags.py`, `collect_status.py`) y un escritor: un lector puede ver el estado justo antes o justo después de un toggle — aceptable, el peor caso es un icono desactualizado hasta el siguiente refresco.

---

## 6. Decisiones

**Todas resueltas** (usuario, 2026-09-03):

| # | Decisión | Resolución |
|---|---|---|
| 6.1 | ¿`risk` en este plan? | **No** — plan aparte: [`design-move-risk-to-metadata.md`](design-move-risk-to-metadata.md). Este plan solo hace flags. |
| 6.2 | ¿`workinprogress` en qué estados? | `inProgress` e `implemented`. En `todo` no (los `todo` no llevan flags en absoluto). |
| 6.3 | Iconos: ¿emoji o ASCII? | Emoji por defecto (⭐ ⚙️); fallback ASCII (`[P]` `[W]`) cuando `supports_color()` es `False`. Centralizado en `flags_prefix()`. |
| 6.3b | Emoji de ancho variable (⚙️ con VS16): ¿padear el prefijo a ancho fijo para cuadrar columnas? | **No.** En modo color, `flags_prefix()` emite `" ".join(icons) + "  "` sin padding. El prefijo va siempre al principio de una línea/fila donde nada a su derecha se alinea verticalmente con la fila de al lado, así que **se acepta que una fila con flags quede ligeramente desplazada** respecto a las que no tienen — es cosmético y va al margen izquierdo. No se fuerza ASCII en ninguna vista con color (ni siquiera si `render_status.py` tuviera columnas ASCII alineadas). El fallback ASCII (`supports_color() == False`) sí es de ancho determinista y cuadra solo. `⚙️` se escribe con VS16 (`U+2699 U+FE0F`); si en el terminal objetivo se ve mal, quitarlo es un cambio de una línea en `FLAG_ICONS`, no bloqueante. |
| 6.4 | Modo chat (markdown): ¿columna `Flags` o prefijo en `Code`? | **Columna `Flags` como primera columna**, tal y como se ve en el mockup de §8.6. |
| 6.5 | ¿Ordenar `priority` primero o solo marcar? | **Solo marcar.** `--flag priority` ya da la lista filtrada. |
| 6.6 | Iconos en `pv.py`: ¿import o script? | **Script de lectura nuevo** `read-flags.py` en `pv-status`, invocado vía `run_script()` (`pv.py` no importa nada). Interfaz en §4.4. |
| 6.7 | Nombre del fichero | `.metadata.json`. |
| 6.8 | ¿Flujo "cambio → `todo`"? | **No existe** — se elimina del plan cualquier manejo de reconversión. Regla única: los `todo` nunca llevan `.metadata.json`; `set-metadata.py` rechaza bajo `todo/`; `pv-update` reporta si aparece. |
| 6.9 | (Aclaración) ¿Qué entra por `/pv-new`? | Esta feature completa (el sistema `.metadata.json` + flags) se documenta como change formal vía `/pv-new` antes de implementar, por el alcance cross-skill. Al revisar este plan directamente, ese paso ya está en marcha. |
| 6.10 | `flagsLastModified`: ¿lo lee algo en este plan? | **No.** Se escribe siempre; ningún consumidor lo lee todavía. Se guarda para uso futuro (orden por actividad, marcas viejas), igual que `risk` en el schema. |
| 6.11 | `set-metadata.py`: ¿lock en el read-modify-write? | **Sí, con file lock.** Un toggle desde `pv.py` y otro desde Claude Code en paralelo no se pisan. Nada de last-write-wins. |
| 6.12 | `filter_status.py --flag` repetible: ¿OR o AND? | **OR** (unión). Sin modo AND — el uso real elige una flag; si hiciera falta intersección, `--flag-mode all` explícito más adelante. |
| 6.13 | `read-flags.py`: ¿una llamada por entrada o batch? | **Batch de entrada desde el día 1.** Varios `--xxxx` por invocación, una línea de salida por código. `list_implemented_entries()` hace 1 subproceso, no N. |
| 6.14 | Orden de la línea 1 de la ficha | `flags · code · [type] · (status) · Risk`. Reordena el actual `(status)  code  [type]  Risk` de `filter_status.py` (status pasa tras el type) y aplica igual a `render_status.py`, en las 3 vistas de ficha (§8.5, §8.7, §8.8), por una sola convención en `pv-status`. **Único punto no-aditivo del plan** — detalle, alcance, coste y alternativa descartada en §4.2.1. Implica: regenerar snapshots/golden-files de tests de `pv-status`, actualizar docs que reproduzcan la línea 1 (§9), y verificar el orden en fichas sin flags (§7.7). |
| — | `todo` y flags | Los `todo` **nunca** llevan flags ni `.metadata.json`. No hay volcado informativo (no hay flujo de reconversión). |
| — | `flagsLastModified` | Un único timestamp global, no uno por flag. |
| — | `move-change.py` | **Verificado:** `shutil.move()` del directorio completo — `.metadata.json` viaja solo, sin cambios de código. |

---

## 7. Orden de implementación (si se aprueba)

1. `/pv-new` → `description.md`; `/pv-how` → `plan.md`.
2. `pv-internal-workflow`: `metadata.schema.json` (enum de flags = catálogo canónico, con `risk` ya declarado para el change 2) + `set-metadata.py` (`--add-flag`/`--remove-flag`/`--toggle-flag`, `--work-folder`, `--print`, rechazo bajo `todo/`) + contrato de `.metadata.json` en `SKILL.md`. (`move-change.py` ya verificado: `shutil.move()` del directorio completo — nada que tocar.)
3. `pv-status`: mapa canónico flag → icono/label + `flags_prefix()` / `flag_label()` → `collect_status.py` (campo `flags`) → `filter_status.py` (`--flag` + **reorden línea 1 a `flags · code · [type] · (status) · Risk`, decisión 6.14/§4.2.1**) → `render_status.py` (mismo reorden de línea 1 + iconos en cada fila) → **`read-flags.py`** nuevo (para `pv.py`). `list_todo.py` sin cambios. **Regenerar aquí** los snapshots/golden-files de tests de `pv-status` que capturen la línea 1.
4. `pv-update`: auditoría de `.metadata.json` contra el schema; reportar `.metadata.json` bajo `todo/`.
5. `/pv-do` para propagar a la doc de features/arquitectura.
6. `dev-onescript`: en `pv.py` → `list_implemented_entries()` antepone iconos (vía `read-flags.py`), opciones "Toggle a flag on a change" y "Show changes by flag", `SCRIPTS_ACCEPTING_WORK_FOLDER`, ambos design docs.
7. Pruebas end-to-end con `sandbox-test1/pv-test.py --testconfig` contra los fixtures de `sandbox-test1/previo-sdd/changes/`: marcar/desmarcar cada flag en un cambio, ver iconos en las listas del inventario (§4.4), intentar marcar un `todo` (debe fallar), `NO_COLOR` (fallback ASCII), toggles concurrentes (lock, decisión 6.11), **el nuevo orden de línea 1 `flags · code · [type] · (status) · Risk` también en fichas SIN flags** (regresión 6.14), regresión de opciones no relacionadas.
8. **Documentación en español** (§9): actualizar todos los ficheros del checklist.
9. **Traducción a inglés** (§10): regenerar cada `.en.md` desde su `.es.md` con `en-translate` (traduce *hacia* inglés) (y editar los `SKILL.md` directamente en inglés).

---

## 8. Ejemplos y mockups

> Mockups sobre las carpetas fixture reales de `sandbox-test1/previo-sdd/changes/` (`00193` fast en `implemented`, `00210` change en `implemented`, `a3f9k`/`q7m2z` ideas en `todo`, `00192`/`00184`/`00196`/`00224` en `inProgress`). *Antes* = salida actual verificada; *después* = propuesta.

### 8.1 Contenido de ejemplo de `.metadata.json`

**Cambio con las dos flags** — `changes/inProgress/00192/.metadata.json`:
```json
{
  "flags": ["priority", "workinprogress"],
  "flagsLastModified": "2026-09-03"
}
```

**Cambio solo priorizado** — `changes/inProgress/00184/.metadata.json`:
```json
{
  "flags": ["priority"],
  "flagsLastModified": "2026-09-01"
}
```

**Cambio en el que se trabaja ahora, sin priorizar** — `changes/inProgress/00196/.metadata.json`:
```json
{
  "flags": ["workinprogress"],
  "flagsLastModified": "2026-09-03"
}
```

**Cambio en `implemented` con retoques activos** — `changes/implemented/00210/.metadata.json`:
```json
{
  "flags": ["workinprogress"],
  "flagsLastModified": "2026-09-03"
}
```

**Cambio sin flags:** no tiene `.metadata.json`. Los lectores lo tratan como `flags: []`.

**Idea en `todo/`:** **nunca** tiene `.metadata.json`. `set-metadata.py` rechaza cualquier operación bajo `todo/`, y `pv-update` reporta el fichero si aparece ahí.

### 8.2 Árbol de una carpeta de cambio

```
changes/inProgress/00192/
├── description.md      ← sin cambios
├── plan.md             ← sin cambios (el risk sigue en su header hasta el change 2)
├── history.md          ← sin cambios
└── .metadata.json      ← NUEVO (dotfile; solo si el cambio tiene alguna flag)
```

### 8.3 `pv.py` — "Close an implemented entry" (listado **propio** de `pv.py`)

Lo construye `list_implemented_entries()` en `pv.py` → el prefijo de iconos es un **cambio real en `pv.py`**.

**Antes:**
```
--------------------------------------------------------------------------------
Implemented entries, pending closure:
  1. 00193 — "Ajustar imagen..." muestra imagen antigua tras pegar estilo solo
  en cara trasera
  2. 00210 — Profundidad/extrusión configurable para todos los componentes
  a. Close all
--------------------------------------------------------------------------------
Choose an entry to close (number, 'a' to close all, or empty to cancel):
```

**Después** (`00193` con `["workinprogress"]`, `00210` sin flags):
```
--------------------------------------------------------------------------------
Implemented entries, pending closure:
  1. ⚙️  00193 — "Ajustar imagen..." muestra imagen antigua tras pegar estilo
  solo en cara trasera
  2. 00210 — Profundidad/extrusión configurable para todos los componentes
  a. Close all
--------------------------------------------------------------------------------
Choose an entry to close (number, 'a' to close all, or empty to cancel):
```

**Después, fallback ASCII** (`NO_COLOR` / terminal sin color):
```
  1. [W] 00193 — "Ajustar imagen..." muestra imagen antigua tras pegar estilo
  2. 00210 — Profundidad/extrusión configurable para todos los componentes
```

### 8.4 `pv.py` — nueva opción "Toggle a flag on a change"

```
================================================================================
                              Previo: Changes info                              
================================================================================
  1. Search by id
  2. Search by content
  3. Search by state
  4. Toggle a flag on a change        ← NUEVA
  5. Show changes by flag             ← NUEVA (solo lectura)
  6. Back
================================================================================
Choose an option: 4

--------------------------------------------------------------------------------
Pick a change:
  1. ⭐⚙️  00192 — "Ajustar imagen..." muestra imagen antigua tras pegar estilo
  2. ⭐  00184 — Migración ficha→carta conserva referencias rotas
  3. ⚙️  00196 — Validación de numeroMaximoCaras fuera de rango
  4. 00224 — Zoom del editor no respeta el límite inferior
--------------------------------------------------------------------------------
Choose a change (number, or empty to cancel): 4

--------------------------------------------------------------------------------
Flags on 00224 — Zoom del editor no respeta el límite inferior:
  1. [ ] ⭐ Priority
  2. [ ] ⚙️ Work in progress
--------------------------------------------------------------------------------
Choose a flag to toggle (number, or empty to cancel): 2
Add flag 'Work in progress' to 00224?
(y/N): y
Flag 'Work in progress' added to 00224.

Press Enter to return to the menu...
```

Segunda pasada sobre el mismo cambio: `2. [x] ⚙️ Work in progress`, y el `confirm()` diría "Remove flag 'Work in progress' from 00224?". Los labels ("Priority", "Work in progress") son presentación en `pv.py`; a `set-metadata.py` se le pasa el valor del enum (`priority`, `workinprogress`).

Si el cambio elegido no existe / está en `todo`: mensaje de error de `set-metadata.py` ("flags no aplican a todo/"), sin tocar nada.

### 8.5 `pv.py` — "Show changes by flag" → `filter_status.py --flag` (render delegado)

```
Choose an option: 5

--------------------------------------------------------------------------------
  1. Priority
  2. Work in progress
--------------------------------------------------------------------------------
Choose a flag (number, or empty to cancel): 1

================================================================================
                        PROJECT STATUS — flag: priority                         
                             Generated: 2026-09-03                              
================================================================================

⭐⚙️  00192  [🆕 Change]  (inProgress)  Risk: 5/10
created: 2026-08-07, planned: 2026-08-19
> "Ajustar imagen..." muestra imagen antigua tras pegar estilo solo en cara
  trasera
  ...
extra files: 1

⭐  00184  [🆕 Change]  (inProgress)  Risk: ?
created: 2026-08-05, planned: pending
> Migración ficha→carta conserva referencias rotas
  ...
extra files: 0

================================================================================
```

**Orden de la línea 1** (decisión 6.14): `flags · code · [type] · (status) · Risk: N`. Reordena lo que hoy pinta `filter_status.py` (`(status)  code  [type]  Risk` → status pasa a después del type). Aplica a **todas** las fichas de `filter_status.py` (§8.5, §8.7, §8.8) por coherencia — no solo a esta vista.

(El `Risk: N/10` de la línea 1 sigue saliendo de `plan.md` en este plan; lo mueve el change 2.)

### 8.6 `pv-status` modo chat (markdown) — tabla de estado

`STATUS.template.md`. Los iconos de flags van **en primer lugar**.

**Antes:**
```markdown
| Code | Description | Risk |
|------|-------------|------|
| 🆕 00192 | "Ajustar imagen..." muestra imagen antigua... | 5/10 |
| 🆕 00184 | Migración ficha→carta conserva referencias rotas | ? |
```

**Después** (columna `Flags` como primera columna — decisión §6.4):
```markdown
| Flags | Code | Description | Risk |
|-------|------|-------------|------|
| ⭐⚙️ | 🆕 00192 | "Ajustar imagen..." muestra imagen antigua... | 5/10 |
| ⭐ | 🆕 00184 | Migración ficha→carta conserva referencias rotas | ? |
|  | 🆕 00224 | Zoom del editor no respeta el límite inferior | ? |
```

**Alternativa considerada y descartada** (§6.4) — prefijo dentro de la celda `Code`, sin columna nueva:
```markdown
| Code | Description | Risk |
|------|-------------|------|
| ⭐⚙️ 🆕 00192 | "Ajustar imagen..." muestra imagen antigua... | 5/10 |
| ⭐ 🆕 00184 | Migración ficha→carta conserva referencias rotas | ? |
| 🆕 00224 | Zoom del editor no respeta el límite inferior | ? |
```

### 8.7 `pv-status` "General project status" — detalle por estado (render delegado)

`render_status.py --terminal`, página de detalle de `IN PROGRESS`. Mismo reorden de línea 1 que `filter_status.py` (decisión 6.14): `flags · code · [type] · (status) · Risk`.

**Antes:**
```
(inProgress)  00192  [🆕 Change]  Risk: 5/10
created: 2026-08-07, planned: 2026-08-19
> "Ajustar imagen..." ...
```

**Después:**
```
⭐⚙️  00192  [🆕 Change]  (inProgress)  Risk: 5/10
created: 2026-08-07, planned: 2026-08-19
> "Ajustar imagen..." ...
```

### 8.8 Ficha detalle (`filter_status.py --search-id`) — render delegado

`pv.py` "Search by id" / prompt de id de "Project status". Iconos al principio de la línea 1; orden `flags · code · [type] · (status) · Risk` (decisión 6.14).

**Antes:**
```
(inProgress)  00192  [🆕 Change]  Risk: 5/10
created: 2026-08-07, planned: 2026-08-19
> "Ajustar imagen..." muestra imagen antigua tras pegar estilo solo en cara
  trasera
  ...
extra files: 1
```

**Después:**
```
⭐⚙️  00192  [🆕 Change]  (inProgress)  Risk: 5/10
created: 2026-08-07, planned: 2026-08-19
> "Ajustar imagen..." muestra imagen antigua tras pegar estilo solo en cara
  trasera
  ...
extra files: 1
```

### 8.9 Helper canónico (pseudocódigo, vive en `pv-status`)

```python
# Un solo sitio para todo lo relativo a una flag: valor del enum, icono
# emoji, icono ASCII y label humano (el que ve el usuario en pv.py).
FLAG_ICONS       = {"priority": "⭐",  "workinprogress": "⚙️"}
FLAG_ICONS_ASCII = {"priority": "[P]", "workinprogress": "[W]"}
FLAG_LABELS      = {"priority": "Priority", "workinprogress": "Work in progress"}
FLAG_ORDER       = ["priority", "workinprogress"]  # orden fijo de pintado

def flags_prefix(flags: list[str], *, color: bool = True) -> str:
    """'⭐ ⚙️  ' para ['workinprogress','priority']; '' para [].

    Sin padding a ancho fijo (decisión 6.3b): en modo color el ancho
    real de ⚙️ es impredecible entre terminales, pero el prefijo va
    siempre al margen izquierdo de una línea/fila sin columnas que
    cuadrar a su derecha, así que se acepta el desplazamiento. El
    modo ASCII sí es de ancho determinista.
    """
    table = FLAG_ICONS if color else FLAG_ICONS_ASCII
    icons = [table[f] for f in FLAG_ORDER if f in flags]
    return (" ".join(icons) + "  ") if icons else ""

def flag_label(value: str, *, color: bool = True) -> str:
    """'⭐ Priority' — para los show_selection() de pv.py."""
    icon = (FLAG_ICONS if color else FLAG_ICONS_ASCII)[value]
    return f"{icon} {FLAG_LABELS[value]}"
```

- Cualquier lista de cambios (en `pv-status`, o en `pv.py` vía el script de lectura) antepone `flags_prefix(entry["flags"])` al identificador.
- Los `show_selection()` de flags en `pv.py` muestran `flag_label(v)` para cada `v in FLAG_ORDER` y pasan `v` (valor del enum) a `set-metadata.py` / `filter_status.py --flag`.
- Añadir una flag futura = una entrada en `FLAG_ICONS` / `FLAG_ICONS_ASCII` / `FLAG_LABELS` / `FLAG_ORDER` + el enum del schema. Nada más.

---

---

## 9. Documentación afectada

> Regla del framework: la documentación se actualiza **cuando el change se implementa**, no ahora (los planes son "no implementado"). Esta sección es el checklist para ese momento. Todos los docs `pv-*` tienen versión ES y EN que son **traducción exacta** una de otra — se editan **siempre las dos a la vez**, nunca una sin la otra.

### 9.1 Docs de diseño de `pv.py` (los edita `dev-onescript`, paso §7.6)

| Fichero | Qué cambia |
|---|---|
| `.claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md` **+** `.en.md` | **Jerarquía de Pantallas**: añadir "Toggle a flag on a change" y "Show changes by flag" bajo "Changes info". **Flujo de Navegación** (grafo Mermaid): nodos y aristas de las dos opciones nuevas. **Dependencias Externas** (tabla de scripts): añadir `set-metadata.py` (pv-internal-workflow) y `read-flags.py` (pv-status); anotar que `filter_status.py` gana el modo `--flag`. **Estilo por Tipo de Pantalla / Info delegada**: nota sobre el prefijo de iconos de flags que ahora anteponen `render_status.py` / `filter_status.py` / `read-flags.py`, y que `list_implemented_entries()` (listado propio) también los muestra. **Organización del Fichero**: si `pv.py` gana un helper o consts para las opciones nuevas, reflejarlo en la tabla de bloques. **Diagrama de Componentes**: `pv.py → read-flags.py` y `pv.py → set-metadata.py` como nuevas aristas subprocess. |

### 9.2 Doc de diseño del framework

| Fichero | Qué cambia |
|---|---|
| `.claude/pv-doc/pv-design/pv-design.es.md` **+** `.en.md` | **Responsabilidades de skills**: `pv-internal-workflow` gana `set-metadata.py` + `metadata.schema.json` (mutación y contrato de `.metadata.json`); `pv-status` gana lectura de `flags`, el modo `filter_status.py --flag`, `read-flags.py`, y el mapa canónico flag→icono/label; `pv-update` audita `.metadata.json` contra su schema. **Ficheros de una carpeta de change/fix**: añadir `.metadata.json` (dotfile, opcional, estado mutable: `flags`) junto a `description.md` / `plan.md` / `history.md`. **Si hay tabla de "qué scripts tiene cada skill"**: añadir los scripts nuevos. **`collect_status.py`**: menciona que ahora también devuelve `flags` por entrada. **Formato de la ficha de cambio (decisión 6.14)**: si el doc reproduce el formato de la línea 1, actualizarlo al orden `flags · code · [type] · (status) · Risk` (antes `(status) code [type] Risk`); es un cambio de formato de `filter_status.py` + `render_status.py`, no solo del prefijo de flags. |

### 9.3 Guía de usuario

| Fichero | Qué cambia |
|---|---|
| `.claude/pv-doc/pv-guide.es.md` **+** `.en.md` | **Sección de `pv.py` / "consultar el estado sin pasar por Claude Code"** (~línea 397 en la ES): documentar las dos opciones nuevas del menú (marcar/desmarcar flags en un cambio; listar cambios por flag) y que las listas de cambios muestran los iconos ⭐/⚙️. **Árbol de `changesDir`** (~línea 116): si lista el contenido de una carpeta de change, mencionar `.metadata.json`. **Posible sección nueva "Flags / foco de trabajo"** explicando `priority` y `workinprogress` a nivel usuario. **Si la guía muestra una ficha de cambio de ejemplo** (salida de "Search by id" / "Project status"): actualizar la línea 1 al orden `flags · code · [type] · (status) · Risk` (decisión 6.14). No toca la parte de `**Risk**` (eso es el change 2). |

### 9.4 README

| Fichero | Qué cambia |
|---|---|
| `README.es.md` **+** `README.md` (EN) | Solo si enumeran capacidades de `pv.py` o el contenido de una carpeta de change. Revisar; probablemente un retoque menor o nada. |

### 9.5 `SKILL.md` afectados (no son "docs" pero se actualizan igual)

| Fichero | Qué cambia |
|---|---|
| `pv-internal-workflow/SKILL.md` | Contrato de `.metadata.json` + `metadata.schema.json`, uso de `set-metadata.py` (args, rechazo bajo `todo/`), nota de que `move-change.py` arrastra el dotfile. |
| `pv-status/SKILL.md` | `filter_status.py --flag`, `read-flags.py`, campo `flags` en la salida de `collect_status.py`, el mapa canónico. **Si documenta el formato de la ficha**: nuevo orden de línea 1 `flags · code · [type] · (status) · Risk` (decisión 6.14). |
| `pv-update/SKILL.md` | Nueva comprobación: `.metadata.json` contra schema + `.metadata.json` bajo `todo/` es error. |
| `dev-onescript/SKILL.md` | Si su lista de "scripts que `pv.py` puede invocar" o su checklist de doc-sync cambia. |

---

## 10. Traducción de la documentación a inglés

Paso final, **después** de haber actualizado toda la documentación en español (§9). Cada doc `pv-*` mantiene su par `.es.md` / `.en.md` como traducción exacta; tras editar las versiones ES hay que regenerar las EN (y viceversa donde la fuente editada fue la EN).

- Ficheros cuya **fuente editada es la versión ES** → generar la `.en.md` con **`en-translate`** (la skill se nombra por el idioma destino: `en-translate` = hacia inglés):
  - `.claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md` → `.en.md`
  - `.claude/pv-doc/pv-design/pv-design.es.md` → `.en.md`
  - `.claude/pv-doc/pv-guide.es.md` → `.en.md`
  - `README.es.md` → `README.md`
- Ficheros cuya **fuente canónica es inglés** (se editan directamente en EN; si hiciera falta una versión ES, se genera con **`es-translate`**): los `SKILL.md` y `*.template.md` del framework, y la documentación técnica (`architectureDocDir` / `styleBibleDocDir`) — que además **no** tiene versión ES (siempre inglés técnico). En la práctica, para este change: editar los `SKILL.md` afectados (§9.5) directamente en inglés; no hay traducción que hacer ahí.
- Regla operativa: no dar por cerrada la documentación hasta que `diff` conceptual entre cada par `.es.md` / `.en.md` sea nulo (misma estructura de secciones, mismas tablas, mismos ejemplos), usando la skill de traducción correspondiente en la dirección correcta según cuál se editó primero.

