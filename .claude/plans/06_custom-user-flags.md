# `custom-user-flags.md`: flags de estado definibles por el usuario

## Context

El framework pv-* marca cada change/fix con **flags de estado**. Hoy el catálogo es
**cerrado y hardcodeado**: exactamente dos valores, `priority` (⭐) y `workinprogress`
(⚙️), escritos a mano en 6 sitios distintos del código. No hay forma de que un equipo
añada flags propios ("blocked", "in review", "needs-QA"...) para adaptar el sistema a su
proceso.

**Objetivo:** que los 2 flags actuales **sigan fijos** (siempre presentes, no editables,
no borrables) y que el usuario pueda **añadir flags propios `(name, emoji)`** en una
sección nueva de `.claude/pv-context.json`. Todo el framework (pv-status, pv.py,
set-metadata.py, filtros, auditoría) debe tratarlos igual que a los dos fijos.

## Estado actual: dónde vive el catálogo

El "catálogo canónico" de flags está duplicado literalmente en:

| Fichero | Qué define |
|---|---|
| `.claude/skills/pv-internal-workflow/metadata.schema.json` (L12) | enum `["priority","workinprogress"]` del campo `flags` |
| `.claude/skills/pv-status/scripts/terminal_output.py` (L37-41) | `FLAG_ICONS`, `FLAG_ICONS_ASCII`, `FLAG_LABELS`, `FLAG_ORDER` |
| `.claude/skills/pv-status/scripts/collect_status.py` (L71) | `KNOWN_FLAGS` |
| `.claude/skills/pv-internal-workflow/scripts/set-metadata.py` (L64) | `VALID_FLAGS` |
| `.claude/skills/pv-init/assets/pv.py` (L154-157) | `FLAG_VALUES`, `FLAG_LABELS`, `FLAG_ICONS`, `FLAG_ICONS_ASCII` |
| `.claude/skills/pv-update/scripts/audit-context.py` (L179) | `KNOWN_FLAGS` (validación de `.metadata.json`) |

`filter_status.py` no lo redefine: importa `read_flags` de `collect_status` y usa
`term.FLAG_ORDER`.

**Consecuencia de diseño:** hay que convertir esas 6 copias estáticas en **una función
de carga común** que devuelva los 2 fijos + los del `pv-context.json`.

Formato en disco (no cambia): `{workFolder}/changes/{state}/{xxxx}/.metadata.json`,
campo `flags: string[]`. Un dotfile que solo existe cuando el change tiene al menos un
flag o un valor de risk. Las entradas `todo/` nunca llevan flags.

## Diseño propuesto

### 1. Nueva sección en `.claude/pv-context.json`

Dentro de `framework`, nueva clave `customFlags` (array, opcional, default `[]`):

```json
"framework": {
  "customFlags": [
    { "name": "blocked", "emoji": "🚫", "label": "Blocked",   "ascii": "[B]" },
    { "name": "review",  "emoji": "👀", "label": "In review",  "ascii": "[R]" }
  ]
}
```

Campos por entrada:

- `name` (**required**): identificador en `.metadata.json`. `^[a-z][a-z0-9]*$`, 2-20
  chars. No puede ser `priority` ni `workinprogress` (reservados).
- `emoji` (**required**): 1 emoji para la vista con color.
- `label` (**required**): texto humano ("Blocked").
- `ascii` (opcional, default `[` + primera letra de `name` en mayúscula + `]`): fallback
  sin color / `NO_COLOR`. Debe ser de ancho fijo (validar longitud).

Reglas: `name` único entre las entradas y distinto de los 2 fijos;
`additionalProperties: false`.

### 2. Nuevo módulo compartido: `flag_catalogue.py`

Crear `.claude/skills/pv-status/scripts/flag_catalogue.py` — módulo **sin dependencias**
(patrón de los demás scripts pv-status) que:

- Define los 2 fijos:
  `BUILTIN_FLAGS = [("priority","⭐","[P]","Priority"), ("workinprogress","⚙️","[W]","Work in progress")]`.
- `load_flag_catalogue(root=None, context_path=None) -> list[FlagDef]`: localiza el repo
  root, lee `.claude/pv-context.json`, parsea `framework.customFlags`, **valida
  defensivamente** (descarta entradas malformadas o con `name` colisionando/inválido,
  sin reventar — igual que `read_flags` hoy hace "drop values outside KNOWN_FLAGS"), y
  devuelve `builtins + custom` en ese orden (builtins primero = orden de pintado).
  Acepta `root` / `context_path` explícitos para el test-harness (`--testconfig`,
  `--work-folder`).
- Helpers derivados, para no repetir dict-comprehensions por todo el código:
  - `flag_names(cat) -> list[str]`
  - `icons_map(cat, *, color) -> dict[str,str]`
  - `labels_map(cat) -> dict[str,str]`
  - `flag_order(cat) -> list[str]`

`terminal_output.py` pasa a **importar de este módulo** en vez de definir las constantes
literales. `flags_prefix()` / `flag_label()` reciben (o cargan) el catálogo en lugar de
usar globals fijas.

### 3. Cambios por consumidor

**`terminal_output.py`**
- Borra `FLAG_ICONS/_ASCII/_LABELS/FLAG_ORDER` literales; los deriva del catálogo.
  Preferible `flags_prefix(flags, catalogue=None, *, color)` → si `catalogue is None`,
  lo carga.
- Un flag presente en `.metadata.json` pero **no** en el catálogo actual (p. ej. el
  usuario borró un custom flag del JSON): se ignora silenciosamente en el render (ya es
  el comportamiento con `read_flags`).
- `flags_prefix()` ya no fija ancho en modo color (decisión 6.3b): sirve igual para
  emojis custom.

**`collect_status.py`**
- `KNOWN_FLAGS` deja de ser tupla literal → `read_flags(entry_dir, catalogue=None)` que
  carga perezosamente (mejor que evaluar al importar, por el test-harness).
- `read_flags` sigue normalizando al orden del catálogo y descartando desconocidos.

**`filter_status.py`**
- `--flag` deja de validar contra `term.FLAG_ORDER` fijo → valida contra
  `flag_names(load_flag_catalogue())`. El mensaje de error lista los válidos
  dinámicamente.
- `collect_by_flag`, columnas y prefijos: sin cambios de lógica, ya delegan en
  `read_flags` / `term.flags_prefix`.

**`set-metadata.py`** (pv-internal-workflow)
- `VALID_FLAGS` literal → cargado del catálogo. Este script ya resuelve `workFolder`
  desde `pv-context.json` (`load_work_folder`), así que añadir la carga del catálogo del
  mismo fichero es natural. Respeta `--work-folder` para tests.
- `apply_flag_ops` ordena por `VALID_FLAGS`; pasa a ordenar por el orden del catálogo
  (builtins, luego custom en orden de declaración).
- Mensajes `--help` de `--add-flag/--remove-flag/--toggle-flag`: "Valid: {lista
  dinámica}".

**`read-flags.py`** (pv-status): sin cambios de lógica — ya delega todo en
`collect_status.read_flags` + `terminal_output.flags_prefix`. Solo se actualiza el
docstring (L2, "canonical flag map (terminal_output.FLAG_*)") para apuntar a
`flag_catalogue.py`.

**`pv.py`** (asset de pv-init, fichero autónomo sin imports)
- No puede importar `flag_catalogue.py`. `pv.py` ya lee `CONTEXT_PATH` para otras cosas;
  añadir una función local `load_flag_catalogue()` que parsee `framework.customFlags` de
  ese mismo JSON (`ACTIVE_CONFIG_PATH`, para respetar `--testconfig`) y construya
  `FLAG_VALUES/FLAG_LABELS/FLAG_ICONS/FLAG_ICONS_ASCII` en runtime, en vez de las 4
  constantes literales (L154-157). Son ~20 líneas y mantiene la política actual de
  "sincronizado a mano con terminal_output", pero ahora ambos leen la misma fuente (el
  JSON).
- **Carga perezosa, no al importar:** el catálogo se recalcula en cada uso (o se
  invalida tras editarlo desde el submenú de Configuration, ver §3bis), para que un flag
  recién creado aparezca sin reiniciar `pv.py`.
- **Flag no configurado → se ignora, sin error.** `load_flag_catalogue()` descarta
  entradas malformadas del JSON (patrón `load_onescript_width`: `try/except`, fallback
  silencioso). Y en cualquier punto que itere sobre los flags de un change leídos de
  `.metadata.json` (`read_change_flags`, `_toggle_flags_on`, los prefijos de
  `flag_prefixes_for` vía `read-flags.py`), un valor que no esté en `FLAG_VALUES` **no
  se pinta, no se lista y no rompe** el menú — exactamente como ya hace
  `collect_status.read_flags` ("values outside KNOWN_FLAGS are dropped").
  `read_change_flags` ya filtra con `[f for f in FLAG_VALUES if f in present]`; basta con
  que `FLAG_VALUES` sea el catálogo dinámico para que esto quede cubierto.
- `FLAG_GROUPS` / `list_flaggable_changes` / `_toggle_flags_on` / `show_changes_by_flag`:
  sin cambios de lógica; iteran sobre `FLAG_VALUES`, que ahora incluye los custom.
- Actualizar el comentario "Canonical flag catalogue -- kept in sync BY HAND": ahora la
  fuente única es `framework.customFlags` + los 2 builtins, replicados en
  `flag_catalogue.py` (scripts) y en la función local de `pv.py`.

### 3bis. Nuevo apartado en el submenú "Configuration" de `pv.py`: gestionar custom flags

`show_settings_menu()` (L744-752) gana una tercera opción, **"Manage custom flags"**, que
abre un sub-submenú con:

- **Listado**, siempre visible arriba: los 2 builtins marcados como `(fixed)` /
  intocables + los custom actuales con su emoji, `name`, `label` y `ascii`.
- **"Add a flag"**:
  1. `name`: pide identificador. Valida `^[a-z][a-z0-9]*$`, 2-20 chars, no colisiona con
     builtins ni con un custom existente. Mensaje claro y vuelta al menú si falla (no
     escribe nada).
  2. `emoji`: pide 1 emoji (no vacío).
  3. `label`: pide texto humano (no vacío; default = `name` capitalizado si Enter).
  4. `ascii`: opcional; Enter → `[` + inicial de `name` en mayúscula + `]`. Si se da,
     valida ancho fijo razonable (p. ej. 2-4 chars).
  5. `confirm(...)` mostrando la entrada resultante y el fichero destino
     (`ACTIVE_CONFIG_PATH.name`), luego escribe.
- **"Remove a flag"**:
  - `show_selection` **solo con los custom** (los 2 builtins nunca aparecen aquí → no se
    pueden borrar). Si no hay custom flags: mensaje "No custom flags to remove
    (`priority` and `workinprogress` are fixed)." y vuelta.
  - Aviso, si el flag elegido está en uso por algún change (barato: reutiliza
    `filter_status.py --flag <name>` o un escaneo directo de `.metadata.json`): "N
    change(s) still carry this flag; they'll simply stop showing it." — no bloquea, el
    borrado es reversible recreando el flag. `confirm(...)` y escribe.
- **Escritura**: función `save_custom_flags(flags: list[dict])` — read-modify-write sobre
  `ACTIVE_CONFIG_PATH` con `json.load` + `json.dump(indent=2, ensure_ascii=False)`,
  preservando todos los demás campos y el orden de claves, creando
  `framework.customFlags` si no existe (mismo patrón exacto que `save_onescript_width`).
  Amplía la nota "the only place pv.py writes its config file" del docstring de
  `save_onescript_width` para incluir `framework.customFlags`.
- Tras cualquier alta/baja: invalida/recalcula el catálogo en memoria para que el resto
  de menús (y "Toggle a flag on a change") reflejen el cambio en la misma sesión.
- Actualizar el docstring de módulo de `pv.py` (la lista de opciones de "Configuration",
  L40-50) con el nuevo apartado y la mención de que ahora `framework.customFlags` es un
  segundo bloque que pv.py escribe.
- Actualizar `schema.json` no hace falta más allá de §4 (la escritura de pv.py produce
  exactamente la forma que §4 define).

**`audit-context.py`** (pv-update)
- `KNOWN_FLAGS` literal → `flag_names(load_flag_catalogue(root))` (ya tiene `root`).
- La validación de `.metadata.json` (`metadata-flags-unknown-value`) pasa a aceptar
  builtins + custom actuales. Un flag en disco que ya no está en el JSON → sigue siendo
  warning "optional" (útil: avisa de flags huérfanos tras borrar un custom flag), con el
  texto ajustado a "not in the current flag catalogue (2 builtin + N custom from
  pv-context.json)".
- Nueva validación del bloque `framework.customFlags`: entradas malformadas, `name`
  reservado, `name` duplicado, `emoji` ausente, `ascii` de ancho no fijo → problema
  "optional" o "required" según gravedad.

### 4. Schema de `pv-context.json`

`.claude/skills/pv-init/schema.json`: añadir `framework.customFlags` con `type: array`,
`items` = objeto `{name, emoji, label, ascii?}`, `additionalProperties: false`.
`uniqueItems` por `name` no se expresa directo en JSON Schema → lo valida
`audit-context.py`. Descripción larga al estilo del resto del fichero (qué es, quién lo
escribe — el usuario a mano —, que los 2 builtins **no** van aquí, que no hace falta
ningún script de sync tras editarlo).

### 5. pv-init

`.claude/skills/pv-init/SKILL.md`: pv-init **no pregunta** por `customFlags` (mismo
patrón que `skills.mockups` / `numberWidth`). Si el usuario ya lo tiene, el merge lo
preserva. Documentar que es campo de edición manual y que, a diferencia de
`skillModels`, no requiere ningún script de sync — lo leen los scripts en runtime.

### 6. Documentación

- `.claude/skills/pv-internal-workflow/metadata.schema.json`: el `flags.items.enum` fijo
  ya no vale. Cambiar a `type: string` + `pattern` y mover la explicación: "valores
  válidos = 2 builtin + los de `framework.customFlags` en pv-context.json;
  `audit-context.py` valida contra el catálogo real". Actualizar la frase "adding a flag
  = one enum value here + ... FLAG_* maps" → "un builtin nuevo se añade en
  `flag_catalogue.py`; un flag de usuario se añade en `pv-context.json` sin tocar
  código".
- `.claude/skills/pv-internal-workflow/SKILL.md`, `.claude/skills/pv-status/SKILL.md`,
  `.claude/skills/pv-update/SKILL.md`: actualizar las menciones al "catálogo de flags"
  para reflejar la fuente configurable.
- `.claude/pv-doc/pv-design/*` y `.claude/pv-doc/pv-design-onescript/*`: actualizar la
  sección que describe el catálogo de flags y el flujo "Toggle a flag".
- `.claude/skills/pv-status/scripts/read-flags.py` (L2) docstring → apuntar a
  `flag_catalogue.py`.

## Casos límite a cubrir

1. **`customFlags` ausente / `[]`** → comportamiento idéntico al actual (solo los 2
   builtins).
2. **`pv-context.json` no existe** (scripts corriendo fuera de un repo pv-init) →
   `load_flag_catalogue` devuelve solo builtins, no lanza.
3. **Entrada malformada** (falta `emoji`, `name` inválido, `name` = `priority`) → se
   descarta esa entrada, el resto del catálogo funciona; `audit-context.py` lo reporta.
4. **Flag custom borrado del JSON con `.metadata.json` que aún lo referencia** → render
   lo ignora; `pv-status` sigue funcionando; `audit-context.py` lo marca como flag
   huérfano (warning, no error).
5. **`name` de custom flag colisiona con builtin** → rechazado en carga y en auditoría.
6. **Emoji de ancho variable / doble** → `flags_prefix` ya no fija ancho en modo color
   (decisión 6.3b), sirve igual; el `ascii` fallback sí debe ser ancho fijo → validar
   longitud de `ascii`.
7. **`--testconfig` / `--work-folder`** en pv.py y set-metadata.py →
   `load_flag_catalogue` debe aceptar un root/context-path explícito para no romper el
   harness de tests.
8. **Orden de pintado** estable: builtins primero (en su orden histórico), luego custom
   en orden de declaración en el JSON.

## Tests

- `flag_catalogue.py`: unit tests de `load_flag_catalogue` (vacío, válido, malformado,
  colisión, sin fichero).
- `set-metadata.py`: toggle/add/remove de un custom flag; rechazo de `name` no listado;
  orden en el array resultante.
- `filter_status.py --flag customname`: filtra correctamente; `--flag inexistente` →
  error con lista dinámica.
- `collect_status.read_flags`: normaliza y descarta desconocidos con catálogo custom.
- `audit-context.py`: detecta `customFlags` malformado, `name` reservado, flag huérfano
  en `.metadata.json`.
- `pv.py`: fixture de `pv-context.json` con custom flags → "Toggle a flag" los muestra;
  `read-flags.py` los pinta.
- `pv.py` "Manage custom flags": alta válida escribe la entrada bien formada en
  `--testconfig`; alta con `name` reservado/inválido/duplicado no escribe nada; baja de
  un custom flag lo quita del JSON y no toca los builtins; "Remove a flag" nunca lista
  `priority`/`workinprogress`.
- `pv.py` con un `.metadata.json` que referencia un flag no presente en `customFlags`:
  "Toggle a flag", "General project status" y `read-flags.py` lo **ignoran** sin
  romperse.
- Regresión: fixture sin `customFlags` → salida byte-idéntica a la actual.

## Orden de implementación

1. `flag_catalogue.py` + sus tests.
2. `schema.json` + `metadata.schema.json`.
3. `terminal_output.py` y `collect_status.py` sobre el módulo nuevo.
4. `filter_status.py` (validación dinámica de `--flag`).
5. `set-metadata.py`.
6. `audit-context.py` (validación del nuevo bloque + flags huérfanos).
7. `pv.py` — loader local `load_flag_catalogue()` + `save_custom_flags()`.
8. `pv.py` — apartado "Manage custom flags" en el submenú Configuration (add / remove /
   listado), con ignorado silencioso de flags no configurados (§3bis).
9. Docs (SKILL.md × 3, pv-doc, docstrings, docstring de módulo de pv.py).
10. Suite de regresión completa + entrada de changelog del framework.

## Fuera de alcance

- Colores ANSI por-flag más allá de emoji + ascii.
- Migración de `.metadata.json` existentes (no hace falta: el formato de `flags` no
  cambia).
- **Editar** un custom flag existente desde pv.py (solo alta y baja; para cambiar emoji
  o label se borra y se recrea, o se edita el JSON a mano).
- Renombrar un `name` propagándolo a los `.metadata.json` que lo usan (borrar el flag
  simplemente hace que dejen de mostrarlo).
