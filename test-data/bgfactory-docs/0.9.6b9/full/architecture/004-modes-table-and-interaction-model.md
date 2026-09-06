# 004 — Modes, table, and interaction model
**Area**: Interaction model

Interaction model shared by both modes, and the edit/play mode differences. Namespace: [00-namespace.md](00-namespace.md).

## Infinite table

[src/ui/table.js](../../../src/ui/table.js). `createInfiniteTable(container) -> { worldEl, ... }`. Pan (drag background) + zoom (wheel) on a transformed world element. `fitToBounds(bounds, {padding=60})` — recenters/zooms to fit. `getComponentsBounds(components)` in [componentRenderer.js](../../../src/ui/componentRenderer.js) computes the bounding rect.

Both modes call `renderComponentsOnTable(worldEl, components, opts)` ([componentRenderer.js#renderComponentsOnTable](../../../src/ui/componentRenderer.js)). `opts` differ per mode (selection, drag lift, indicators, callbacks).

## Interaction registry

[src/core/interactions.js](../../../src/core/interactions.js).

```
TYPE_INTERACTIONS = {
  dado: [{ key: 'lanzar',    label: 'Lanzar dado' }],
  carta:[{ key: 'voltear',   label: 'Voltear carta' }],
  mazo: [{ key: 'sacarCarta', label: 'Sacar carta de arriba' }],
}
getInteractionsForType(type) -> entry[]
isInteractionActive(component, key) -> !component.interaccionesDesactivadas.includes(key)
```

Only these 3 types have a non-"Ninguno" left-click interaction. `modes/play` maps `type → key` via `CLICK_INTERACTION_KEY_BY_TYPE` (`dado→lanzar`, `carta→voltear`, `mazo→sacarCarta`).

## Play mode

[src/modes/play/playMode.js](../../../src/modes/play/playMode.js) (~283 lines).

- Renders components directly on the table. Filters out: hidden (`getEffectiveGeneralProps(...).oculto`) and cards inside any deck (`deck.getCartaIdsEnAlgunMazo`).
- Selection concept: single `selectedComponentId`, module-level, tied only to an open right-click menu.

### Input → effect

| Input | Condition | Effect |
|---|---|---|
| left click on `dado` | interaction active | roll (`dice.tirarDado`), set `properties.resultadoActual`; if `subirAlMoverInteractuar` → `reorderComponent(id,1)` |
| double click on `dado` | — | `openDiceResultModal` (enlarged result) |
| left click on `carta` | interaction active | flip `caraActual`; bump order if `subirAlMoverInteractuar` |
| left click on `mazo` | `cartaIds` non-empty | `sacarCartaDeMazo(mazo, cartaIds[0])`; bump order |
| drag `carta` onto a `mazo` (rect overlap) | — | append card id to `mazo.properties.cartaIds` (no confirm) |
| drag any piece | `getEffectiveGeneralProps(...).bloqueado === 'ninguno'` | move; group members follow by the same delta |
| right click | `component.accionClickDerecho !== 'ninguno'` | select + open context menu |

### Context menu (right click)

- Description row: `formatComponentIdentifier(component)` + extra (`N caras` / `WxH` / `N cartas`).
- General: `Bloquear`/`Desbloquear` (toggles `bloqueado` `'ninguno'↔'juego'`) — **omitted for a synced copy** (its lock follows the original).
- `mazo`-specific: `Barajar` (`deck.shuffleCartaIds`), `Ver contenido...` (`openMazoContentModal`).
- `carta`-specific: `Meter en mazo...` (`openInsertIntoMazoModal`, choose deck + top/bottom) — only if ≥1 deck exists.
- Interaction rows: `getInteractionItemsFor(component)` — shows left/double/right-click bindings; left-click row forced to "Ninguno" when its interaction is disabled.

## Edit mode

[src/modes/edit/editMode.js](../../../src/modes/edit/editMode.js) (~924 lines).

- Table + 3 floating panels: component list, resource gallery, tag list. Each draggable / collapsible / resizable; state in `PanelState` (persisted). Z-order: `panelStackOrder` (transient, reset on reload); `bringPanelToFront` on `mousedown` capture.
- Session selection (module-level, survives `components:changed` remount):
  - `selectedComponentIds: Set<id>` — the authoritative selection for all actions.
  - `primarySelectedIds: Set<id>` — subset that was the **direct** click target (not dragged in by group membership). Drives outline color only: blue = clicked, grey = group passenger.
- Selection rules:
  - Plain click: replace selection with the click unit (or clear if it was already the sole selection).
  - Ctrl/Cmd click: toggle the unit in/out without touching the rest.
  - **Unit** = the whole group if `component.groupId != null` (all same-`groupId` ids), else just `[component.id]`. A group enters/leaves selection atomically.
  - Tag-panel row click: replace selection with all members of that tag + tagged groups; also draws tagged cards out of any deck. No toggle.
- Keyboard (via [globalShortcuts.js](../../../src/ui/globalShortcuts.js), edit-mode only, no modal open): Delete → delete selection; arrows → move selection (1px, Shift 10px), respecting `canMove` (`bloqueado !== 'todos'`).

### Context menu (right click on a piece)

Operates on current selection. General items: `Ocultar`/`Mostrar`, `Clonar`, `Copiar`, `Eliminar`, `Agrupar`, `Desagrupar`. Specific: `Voltear carta` (if all-cards), `Añadir a etiqueta` (select).

| Rule | Expr |
|---|---|
| unit count | distinct `groupId`s + count of loose components |
| `canGroup` | `unitCount ≥ 2 ∧ ¬hasGroup` |
| `canUngroup` | `unitCount == 1 ∧ hasGroup` |
| menu suppressed | `unitCount ≥ 2 ∧ hasGroup` (mixed multi-unit with a group) |
| single whole group selected | `Ocultar`/`Añadir a etiqueta` operate on the **group registry**, not per member |

- `Agrupar`: `nextGroupId(components)` → set `groupId` on all → `addGroup(createGroup({id}))` → `reorderGroupBlock(memberIds, minOrder)`.
- `Desagrupar`: clear `groupId` on members → `removeGroup(groupId)`.

### Delete flow

`attemptDeleteComponents(components)`:
- 0 → nothing.
- 1 → native `confirm()`.
- ≥2 → `openBulkDeleteConfirmModal` (enumerates affected).

### Import / export

[src/ui/editModeToggle.js](../../../src/ui/editModeToggle.js) toolbar: Salir · Importar · Exportar (menu) · Fit-to-bounds.

- Export menu: `Exportar juego (.json)` active; `.zip` / `.csv` marked `Próximamente` (inert). Flow: `openExportSelectionModal` (pick components/resources/tags) → `downloadJson`. Groups referenced by exported components are included.
- Import flow:
  1. `parseImportedComponents` (no version gate).
  2. `openImportSelectionModal` (pick subset).
  3. `openImportConfirmModal` → `{ mode ∈ {'añadir','overwrite'}, conflictMode ∈ {'sobrescribir','mantener ambos'} }`.
  4. `ficha` components migrated (`fichaMigration`), per-component conversion errors → `openImportConversionErrorModal` (continue-without / abort).
  5. `importMerge.mergeImportedGame(...)` (pure) → `loadComponents/loadResources/loadTags/loadGroups` inside `runWithProgressModal`.
  6. `overwrite` also applies imported `appTitle`; group merge: `overwrite` = imported only, `añadir` = current + non-colliding imported (by id); `deriveMissingGroups` covers pre-`componentGroups` files.

## Global shortcuts

[src/ui/globalShortcuts.js](../../../src/ui/globalShortcuts.js). Domain-agnostic — knows only the modal DOM contract `.modal-overlay > .modal > .modal__footer` with `.btn-cancel`/`.btn-accept`/`.btn-eliminar`. `main.js` connects "Delete with no modal" → `onDeleteSelected`, arrows → `onMoveSelected`.

| Key | With top modal open | No modal |
|---|---|---|
| Escape | click `.btn-cancel` | nothing |
| Enter | click `.btn-accept` (unless disabled; ignored in `<textarea>`) | nothing |
| Delete | click `.btn-eliminar` (ignored in text input) | edit mode: delete selection |
| Arrows | nothing (incl. card editor, which handles its own arrows) | edit mode: move selection 1px / Shift 10px |
