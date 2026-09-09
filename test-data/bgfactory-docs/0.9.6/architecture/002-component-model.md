# 002 — Component data model

**Area**: Data model

```js
{
  id: string,          // unique identifier (crypto.randomUUID(), user-editable in the modal)
  type: string,         // free, e.g. "carta", "token", "tableroSimple", "texto"
  name: string,
  properties: object,   // free key-value pairs, type-specific
  image: string | null, // reference to a resource, optional (unused currently, see table)
  x: number,             // position in table world, pixels
  y: number,             // position in table world, pixels
  width: number | null,  // width in pixels, null = automatic by content
  height: number | null, // height in pixels, null = automatic by content
  bloqueado: 'ninguno' | 'juego' | 'todos',
  mostrarTooltip: boolean,
  tooltipTexto: string,
  mostrarTitulo: boolean,
  tituloTexto: string,
  tituloColorTexto: string,
  tituloColorFondo: string,
  tituloFondoTransparencia: number,
  subirAlMoverInteractuar: boolean,
  oculto: boolean,
  etiquetaIds: string[],
  order: number,
  copyOf: string | null,
  sincronizado: boolean,
  groupId: string | null,
  interaccionesDesactivadas: string[],
  accionClickDerecho: 'ninguno' | 'menuContextual',
}
```

## General fields

| Field | Type/values | Default | Purpose | Edited by |
|---|---|---|---|---|
| `id` | string | generated UUID | Unique identifier | `ui/componentModal.js`, "Generales" tab (non-empty + uniqueness validation in UI layer) |
| `type` | free string | — | Component type (`'texto'`, `'tableroSimple'`, etc.) | Set on creation, not editable afterward |
| `name` | string | — | Name | — |
| `properties` | object | `{}` | Type-specific properties | `ui/componentModal.js`, "Específicas" tab |
| `image` | string \| null | `null` | Unused by any current type. Types with an image background (`'tableroSimple'`, `'carta'`, `'tableroPersonalizado'`) reference a resource via `properties.imagenResourceId` or `properties.<face>.imagenResourceId`, not via `image` | — |
| `x`, `y` | number | `0` | Position in the table world. Creation from edit mode assigns an initial position that does not overlap existing components | Drag on the table |
| `width`, `height` | number \| null | `null` | Size in pixels. `null` = automatic by content. Set on resize from edit mode | Resize on the table |
| `profundidad` | number | `0` (`4` on a new `'dado'`) | Thickness in px of the visual extrusion (stacked solid layers, `box-shadow`/`filter: drop-shadow` by type). Cap `40`. `0` = no effect. No effect on `'texto'` whatever its value. See `ui/componentRenderer.js` (`buildExtrusionLayers`) and `../style/001-tokens-visual.md` (Elevation) | "Apariencia" tab of `ui/componentModal.js`, section "Extrusión", "Profundidad" field (`<input type="number">`, clamp `[0, 40]`) |
| `colorExtrusion` | string (hex) \| null | `null` | Extrusion color. `null` = automatic computation `shadeColor(colorBase, -0.25)` (`colorBase` by type, see `resolveExtrusionColor` in `ui/componentRenderer.js`) | "Apariencia" tab, section "Extrusión", "Color de extrusión" field (`<input type="color">`, no reset-to-`null` control — once an explicit color is chosen there is no way back to automatic computation from the UI) |
| `bloqueado` | `'ninguno' \| 'juego' \| 'todos'` | `'ninguno'` | Mode(s) where the component cannot be moved. Governs drag in `modes/play/playMode.js` (locked unless `'ninguno'`) and in `modes/edit/editMode.js` (locked only with `'todos'`); each mode passes its own `canMove` to `renderComponentsOnTable` | "Generales" tab of `ui/componentModal.js`, 3-option dropdown ("Ninguno"/"Solo modo juego"/"Todos los modos") |
| `mostrarTooltip` | boolean | `false` | Whether `ui/componentRenderer.js` renders its own tooltip (`.component-tooltip`) in play mode (global `identifyMode` `'tooltip'`) on hover. Content: `tooltipTexto` if non-empty, otherwise the component identifier | "Generales" tab, "Ayuda jugador" section |
| `tooltipTexto` | string | `''` | Text shown in the `mostrarTooltip` tooltip when non-empty (if empty, the component identifier is used). Accepts basic formatting sanitized by `sanitizeBasicTooltipHtml` (`ui/componentRenderer.js`): `<b>`, `<strong>`, `<i>`, `<em>`, `<u>`, `<br>`, `<ul>`, `<ol>`, `<li>`, no attributes — any other tag is unwrapped keeping its content. Also accepts text variables (see "Text variable system" below). Not a group override: `getEffectiveGeneralProps` (`core/group.js`) does not expose it; it always comes from the component's own `component.tooltipTexto` even when the component belongs to a group (unlike `mostrarTooltip`, which is a group override) | "Generales" tab, "Ayuda jugador" section, `<textarea>` disabled while "Mostrar tooltip" is unchecked |
| `mostrarTitulo` | boolean | `false` | Whether `ui/componentRenderer.js` renders its own label (`.component-title-label`) in play mode (global `identifyMode` `'tooltip'`), anchored to the component's top-left corner, **always visible** while active (does not depend on `:hover`, unlike `mostrarTooltip`). Empty `tituloTexto` paints no node. Group override, same criterion as `mostrarTooltip`: if the component belongs to a group, `getEffectiveGeneralProps` governs | "Generales" tab, "Ayuda jugador" section (00212, replaces the old fixed card-count label of `'mazo'`, see `003-component-types.md`) |
| `tituloTexto` | string | `''` | Title content. Same basic sanitized formatting and same text variables as `tooltipTexto`. No fallback to the identifier (unlike `tooltipTexto`): empty = nothing painted. Not a group override, always the component's own | "Editar título de componente" sub-modal (`ui/componentTitleModal.js`), "Editar título de componente…" button next to the `mostrarTitulo` checkbox |
| `tituloColorTexto` | string (hex) | `'#000000'` | Text color of the title label | "Editar título de componente" sub-modal |
| `tituloColorFondo` | string (hex) | `'#ffffff'` | Background color of the title label, combined with `tituloFondoTransparencia` via `hexToRgba` (`core/colorUtils.js`) | "Editar título de componente" sub-modal |
| `tituloFondoTransparencia` | number, 0–100 | `0` (opaque) | Transparency of the title label background. The title text has no transparency of its own | "Editar título de componente" sub-modal |
| `subirAlMoverInteractuar` | boolean | `false` (`true` for `'carta'`/`'dado'`) | Whether it rises to `order = 1` on move/interact in play mode. `modes/play/playMode.js` calls `reorderComponent(id, 1)` after every play-mode interaction (drag, dice roll, card flip). Independent of `bloqueado` | "Generales" tab |
| `oculto` | boolean | `false` | Whether the component is NOT rendered in play mode (filtered before `renderComponentsOnTable`). In edit mode it restricts nothing, only adds a badge (`showHiddenIndicator`) | "Generales" tab, second checkbox after "Bloqueado" |
| `etiquetaIds` | string[] | `[]` | Ids of tags (`getTags()`) the component belongs to. A component can belong to several tags at once | "Etiquetas" section of the "Generales" tab: one checkbox per existing tag, alphabetically ordered, plus a "+ Crear nueva etiqueta…" row |
| `order` | number | computed | Stacking position on the table: `1` = topmost, `n` = bottommost. See dedicated logic below | Not directly editable except via the "Orden" column of the Components panel |
| `copyOf` | string \| null | `null` | Id of the original component if this is a linked "Copy". See "Linked copies" below | Created by the "Copiar" action, not editable |
| `sincronizado` | boolean | `true` | Only has effect if `copyOf` is not `null`: whether this copy's `bloqueado`/`oculto` follow the original | `ui/copyComponentModal.js` |
| `groupId` | string \| null | `null` | Id of the "Group" (`grupo-N`) the component belongs to, if any. Flat, no nesting: a group cannot contain another group. See "Groups in edit mode" in `005-modes.md` | "Agrupar"/"Desagrupar" entries of the edit-mode context menu |
| `interaccionesDesactivadas` | string[] | `[]` (all active) | Keys of `core/interactions.js` disabled for this component | "Interacciones" tab (00251), "Interacciones programadas" section: one `<select>` per left-click interaction the `type` has registered |
| `accionClickDerecho` | `'ninguno' \| 'menuContextual'` | `'ninguno'` | What right-click does in play mode | "Interacciones" tab, fixed row inside "Interacciones programadas" ("Click derecho"), independent of `type` |

Notes on default handling of absent fields on load. Since 00250, `core/state.js#loadComponents` runs **no** save migration — it only calls `compactOrders` (which now assumes every component carries an integer `order`) and stores the array. A component created with the current version already has every field below; the pre-1.0 saves these notes used to describe can no longer be in circulation.

- `bloqueado`: the current field is `'ninguno' | 'juego' | 'todos'`; `createComponent` sets `'ninguno'`. (The earlier boolean form is no longer converted.)
- `mostrarTooltip`, `tooltipTexto`, `mostrarTitulo`, `tituloTexto`, `tituloColorTexto`, `tituloColorFondo`, `tituloFondoTransparencia`, `oculto`, `subirAlMoverInteractuar`, `interaccionesDesactivadas`: `createComponent` sets each (unchecked / `''` / `'#000000'`/`'#ffffff'` / `0` / `[]`).
- `etiquetaIds`: `createComponent` sets `[]`. `core/component.js` still exposes `normalizeComponentEtiquetaIds(component)` (accepts `grupoIds` array, scalar `grupoId`, or absence), used by `core/importMerge.js` (`mergeImportedGame`) so importing a file exported by an older version still normalizes its components. (The earlier `grupoId`/`grupoIds`/`properties.deckId` forms are no longer converted on startup.)
- `accionClickDerecho`: `createComponent` sets `'ninguno'` for a new component. (A save without the field is no longer migrated to `'menuContextual'`.)
- `groupId`: `createComponent` sets `null` (no group).
- `profundidad`, `colorExtrusion`: `createComponent` sets `0`/`null` (no effect).

`core/component.js` exposes `createComponent()`/`updateComponent()` as the only way to build/modify components. `createComponent()` initializes `x`/`y` to `0`; `width`/`height` to `null`. It also exposes `cloneComponent(component, components)` and `nextCloneId(baseComponentId, components)`:

- `nextCloneId` computes the clone id by stripping any trailing `(n)` suffix from the original id (so clones of a clone share root/family) and appending `(n)` with the next free integer for that root.
- `cloneComponent` builds the full clone object (shallow copy + own `properties`/`id`, position offset +30/+30 from the original) with `order: null`, resolved on `addComponent` (ends up at `order = 1`, like a new component). It also starts with `groupId: null`: a clone is independent, it is not automatically added to the cloned component's group.

> Catalog of these fields' UI controls (tab, section, screen order, visibility condition), and also of the group/tag property windows: see the functional entry "Catálogo de propiedades de componentes, grupos y etiquetas" (`../features/040-catalogo-de-propiedades-de-componentes-grupos-y-etiquetas.md`).

## `order` logic

`order` determines visual stacking on the table (replaces insertion/creation order). All logic lives in `core/state.js`, not in `core/component.js` (which only declares the field with default `null`, unable to compute it without knowing the rest of the list).

- `addComponent(component)`: assigns `order = 1` before adding, shifting existing components' `order` by +1. Also used when adding the clone of a component cloned from the panel.
- `removeComponent(id)`: recompacts the remaining orders so they stay consecutive from 1 to n (`compactOrders`, internal function).
- `reorderComponent(id, rawOrder)`: moves a component to a new position — removes it from its current slot (compacting what was behind), inserts it at the given position (shifting down whatever is there or after), clamps `rawOrder` to `[1, n]`.
- `loadComponents(components)`: runs the list through `compactOrders` on load, silently migrating saves without an `order` field (or with invalid values) from their existing insertion order.
- `reorderGroupBlock(memberIds, rawTargetOrder)` (00204): generalization of `reorderComponent` to move a **block** of N contiguous ids at once (the members of a group, see "Groups in edit mode" in `005-modes.md`) instead of a single one, within the same shared `order` space 1..n. A group member does not edit its own `order` directly — the Components panel disables that field in its row; it is edited as a block from the "Orden" of its group's row, which moves all members preserving their existing relative order and clamps the block's start position to `[1, n-k+1]` (`k` = block size) so it fits whole. The context menu's "Agrupar" action also calls this function (with the position of the lowest `order` among the selected) to consolidate any selection of members scattered through the list into consecutive positions at the moment the group is formed.

## Linked copies (`copyOf`)

Unlike "Clonar" (independent once created), a **Copy** stays permanently linked to its original component (`copyOf: string`, the original's id) and syncs automatically with it while both exist, except for `bloqueado`/`oculto` gated by `sincronizado`.

- Created from the components panel with the "Copiar" button (`ui/componentList.js`, next to "Editar"/"Clonar"/"Eliminar"; hidden for rows that are already a copy — copies of copies are not allowed). Immediate action, no prior modal, always starts with `sincronizado: true`.
- **Id**: `${originalId}-COPY-XXX`, `XXX` = first free 3-digit integer among the copies already linked to that original (`core/component.js`, `nextCopyId(originalId, components)`, filters by `copyOf`, not by `id`). `createCopy(component, components)` builds the full copy (same +30/+30 offset and `order: null` as `cloneComponent`).
- **Live sync**: lives in `core/state.js`, hooked in `replaceComponent(id, updatedComponent)` — logic specific to this link, not a generic event mechanism. When an original is updated, each linked copy (`copyOf === id`) is replaced via `core/component.js` → `syncCopyWithOriginal(copy, original)`.
  - Always propagated: `type`, `name`, `image`, `width`, `height`, `profundidad`, `colorExtrusion`, `mostrarTooltip`, `tooltipTexto`, `mostrarTitulo`, `tituloTexto`, `tituloColorTexto`, `tituloColorFondo`, `tituloFondoTransparencia`, `subirAlMoverInteractuar`, `etiquetaIds`, `interaccionesDesactivadas`, `accionClickDerecho`, type configuration/design `properties` (everything editable from `ui/componentModal.js`).
  - `bloqueado`/`oculto`: propagated only if `copy.sincronizado` is `true` (default). With `sincronizado: false`, they stay as the copy's own value.
  - Always independent per copy, no exception: `x`/`y`, `order`, `groupId` (membership of a "Group", see `005-modes.md` — treated like position, never synced; `createCopy` always starts with `groupId: null`), `properties` keys that are per-type game interaction state (`NON_SYNCED_PROPERTY_KEYS` in `core/component.js`: `resultadoActual` on `'dado'`, `caraActual` on `'carta'`).
  - If the original's `id` changes in the same update: `renameCopyId` renames each copy's `id` (keeps the `-COPY-XXX` suffix, replaces only the prefix) and updates its `copyOf`.
- **Deletion**: `removeComponent(id)` cascade-deletes any linked copy (`copyOf === id`) — avoids orphan copies. Deleting an individual copy affects neither the original nor other copies.
- **Reduced modal**: `ui/copyComponentModal.js` (`openCopyComponentModal`) opens instead of `ui/componentModal.js` when `component.copyOf` is truthy (same entry point, `modes/edit/editMode.js` → `openEditModalFor`). No tabs: id (read-only), notice, "Sincronizado" checkbox, and inside the `fieldset.modal__section` "Bloqueado / Oculto" (disabled as a block when "Sincronizado" is checked) the "Bloqueado" (`<select>`) and "Oculto" (checkbox) controls. With "Sincronizado" checked, both controls show and force the original's value; unchecked, they become editable as the copy's own value. Original's id and Eliminar/Cancelar/Aceptar buttons unchanged. Apart from this modal, the "Ocultar"/"Mostrar" row of the edit-mode context menu (`005-modes.md`) is the only other path (outside this modal) that can alter a copy's `oculto` — and unlike the modal (which locks the field while `sincronizado: true`), that row always allows the change and automatically disables `sincronizado` when applied to a synced copy.
- **Play-mode context menu**: `modes/play/playMode.js` (`onContextMenu`) adds "Bloquear"/"Desbloquear" to a copy's menu only if it has `sincronizado: false` — with `sincronizado: true` (or absent), it does not appear, because the lock always follows the original.
- **Edit-mode visual indicator**: see `005-modes.md`, "Copia" indicator.

## Text variable system

`core/textVariables.js` (pure module, no dependencies) replaces occurrences of `{variable_name}` in a text with a value computed at render time, reused by `tooltipTexto` and `tituloTexto` (`ui/componentRenderer.js`, applied before `sanitizeBasicTooltipHtml`). Designed to grow with future variables without redesigning the mechanism — the single extension point is `getAvailableVariables`.

- `getAvailableVariables(component)`: returns the map `{ [name]: string }` of variables available for **that specific component**, by its `type`. Current implementation: `component.type === 'mazo'` → `{ cards_current: String(properties.cartaIds.length) }` (current card count of the deck); any other type → `{}` (no variable available).
- `resolveTextVariables(text, component)`: replaces each `{name}` in `text` with its value in `getAvailableVariables(component)` if that key exists. If the variable is not defined for the current component's type (e.g. `{cards_current}` on something that is not `'mazo'`), it is left **literal, unsubstituted** — never an empty string.
- Recomputed on every table render (the same moment the fixed `'mazo'` counter was recomputed before), so `cards_current` is always up to date with no special invalidation.
