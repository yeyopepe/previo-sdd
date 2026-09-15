# 005 — Play mode vs edit mode

**Area**: Modes

Both modes **share the same data model**: the component list in `core/state.js`. There are not two distinct models — edit mode creates/modifies components with `core/component.js`, play mode reads those same components to show/use them in the game.

- `ui/editModeToggle.js` implements an enter/exit flow (not a two-option selector) over `core/state.js` (`mode: 'play' | 'edit'`): `renderModeSwitcher` (**runs in both modes** since 00244 — no early return) and `renderEditToolbar` (edit mode only). Both operate over `setMode()`/event `mode:changed` of `core/state.js`, with no changes in that layer.
- `main.js` mounts both functions on every render (`renderModeSwitcher(#mode-switcher)` + `renderEditToolbar(#edit-toolbar)`, sibling containers after the `<h1>` in `index.html`). `renderEditToolbar` still `container.innerHTML = ''` + early-return when not in edit mode; `renderModeSwitcher` always paints.
- **`#mode-switcher` content (00244 reorg — canonical detail in [`006-ui-layer.md`](006-ui-layer.md), `ui/editModeToggle.js`):**
  - play mode: `[Importar] [Exportar] │ [Modo] [Ajustar zoom] [Configuración]` — `│` = a `.toolbar-divider` between the file block and the action block.
  - edit mode: `[Modo] [Ajustar zoom] [Configuración]` only (the file block lives in the `.edit-toolbar` strip).
- `renderEditToolbar` builds only the `.edit-toolbar` band: `[Importar] │ [Exportar]` inside one `.toolbar-group`, no mode button and no "Ajustar zoom" (those moved to `#mode-switcher`).
- `createModeButton()` — mode-switch button, class `mode-switcher__mode-btn`, primary-action blue, always in `#mode-switcher`: text `t('toolbar.modeEdit')` ("Modo Edición") in play mode, `t('toolbar.modePlay')` ("Modo Juego") in edit mode. Toggles via `setMode`.
- `createImportControls()` (no `buttonClassName` param any more) + `createExportMenu()` — "Importar"/"Exportar", same "ghost on dark" look in both host bars; hidden `<input type="file" accept=".json">` + button, `change` → `importComponentsFromFile`. One import flow, two call sites.
- [gotcha] importing does **not** call `setMode`. Final mode = mode active when "Importar" was pressed: from play mode you stay in play mode, from edit mode in edit mode. Post-import repaint comes from `loadComponents`/`loadResources`/`loadTags`/`loadGroups` emitting `components:changed`/`resources:changed`/`tags:changed`/`groups:changed`, all subscribed to `renderAll` in `main.js` → `renderActiveMode()` repaints `renderPlayMode`/`renderEditMode` as appropriate. No auto `fitToBounds` after import.
- "Ajustar zoom" button (`createFitButton(className)`, action `fitToBounds(getComponentsBounds(getComponents()))`): icon-only, class `.mode-switcher__fit-btn`, in `#mode-switcher` in **both modes** (since 00244; before that it was a floating child of `#edit-toolbar` in edit mode). Identical look/position across modes (see `../style/002-componentes-layout.md`, §9-§10).
- Mode change emits `mode:changed`; `main.js` re-renders the active screen (`modes/play/playMode.js` or `modes/edit/editMode.js`).

## Edit mode: table and panels

`modes/edit/editMode.js` renders an infinite table (pan/zoom) with components drawn directly on it (`ui/componentRenderer.js`, selectable with click), plus a floating "Componentes" panel (anchored top-right, collapsible) with a table listing (Id/Tipo/Acciones columns) and an edit modal (`ui/componentModal.js`).

| Trigger | Effect |
|---|---|
| Listing's "Editar" button, or click on the table representation | Opens the edit modal |
| Listing's "Eliminar" button | Deletes directly, asking for prior confirmation (deletion not available by clicking on the table) |
| "+ Añadir componente" button | Opens an empty modal to create a new one |

**Multi-selection with Ctrl**: a click on a table row or a table representation calls `toggleSelect(component, event)`, which manages a set of selected ids (`selectedComponentIds`, `Set<string>`, in-memory state, not persisted) instead of a single id.

| Trigger | Effect |
|---|---|
| Normal click | Replaces the whole selection with that single element (or empties it if it was the only one selected) |
| Ctrl+click (or Cmd+click) | Adds or removes that element without touching the rest |
| Any element in the set | Table and listing highlight all of them at once with the same dashed outline (`--selected`) |
| "Eliminar" with 2+ elements selected | DEL or the "Eliminar" button of any row of the selection open `ui/bulkDeleteConfirmModal.js` (lists id and type of each element) instead of the native `confirm()` used for a single component |
| Resize | Offered only with a selection of exactly one element |
| Dragging one of several selected | Moves them all as a block, keeping relative distances (computed in `editMode.js` from the dragged component's delta) |

## Groups in edit mode

Persistent, flat unit (no nesting) that groups 2+ components of any type, exclusive to edit mode. A group **is two things at once**: the `groupId` field (see `002-component-model.md`) shared by its members (the group's existence, as a selection/movement unit, is derived from which components share that value) and, since 00202, its own entry in the `groups` collection of `core/state.js` (`core/group.js`: `createGroup`/`updateGroup`/`isGroupIdTaken`/`getEffectiveGeneralProps`/`getGroupsUsingTag`/`deriveMissingGroups`), with the same general shape as a component (`bloqueado`, `oculto`, `mostrarTooltip`, `mostrarTitulo`, `subirAlMoverInteractuar`, `etiquetaIds`) plus its own `id` (same value as its members' `groupId`). Group membership (`groupId`) is also not synced between a linked copy and its original (`copyOf`): it is treated like position, never like tags.

**Effective properties of a grouped member — `group.effectiveProps.rule`** (`core/group.js#getEffectiveGeneralProps`, see `00-namespace.md`): while a component belongs to a group, its real behavior on the table (move lock, hidden in play mode, tooltip, title, "rise on move/interact") and its effective tags become those of the **group record**, not the component's own — they fully replace the component's own while grouped, without overwriting or losing them (they are read again as soon as the component stops belonging to a group, see "Dissolution"/"Desagrupar" below). Safeguard: if `groupId` matches no `groups` record (should not happen), it falls back to the component's own properties. Every point that previously read `component.bloqueado`/`.oculto`/`.mostrarTooltip`/`.mostrarTitulo`/`.subirAlMoverInteractuar`/`.etiquetaIds` directly to decide behavior (`ui/componentRenderer.js` — once per component, before the per-type branches —, `modes/edit/editMode.js` and `modes/play/playMode.js`) goes through this function instead; the only two exceptions are the `.is-group-passenger` badge (uses `groupId` to know membership, not the effective properties) and the `.is-copy`/selection border.

- **Atomic selection**: `editMode.js` computes, per click, the affected "unit" (`getSelectionUnit`) — if the clicked component has `groupId`, the unit is the whole group; otherwise it is just that component. A normal click replaces `selectedComponentIds` with the whole unit; Ctrl/Cmd+click adds or removes the whole unit (never a loose member of a group). A group always counts as "1 element" for multi-selection purposes, like a loose component.
- **Context menu — "Agrupar"/"Desagrupar"**: `handleComponentContextMenu` adds these two entries to the general section (alongside Ocultar/Mostrar, Clonar, Copiar, Eliminar), with enabling gated by the number of "units" of the resulting selection (each whole group = 1 unit, each loose component = 1 unit):

  | Active selection | Context menu | Agrupar | Desagrupar |
  |---|---|---|---|
  | 2+ units, none is a group | shown | enabled | disabled |
  | 2+ units, at least one is a group | no menu shown | — | — |
  | 1 unit, not a group | shown | disabled | disabled |
  | 1 unit, is a group | shown | disabled | enabled |

  "Agrupar" assigns a new `groupId` (`group.id.rule`, `core/component.js#nextGroupId`, format `grupo-N`, see `00-namespace.md`) to all affected components and creates its record (`addGroup(createGroup({ id: newGroupId }))`, default values — Bloqueado "Ninguno", Oculto/Tooltip/Título/Subir al mover unchecked, no tags). "Desagrupar" sets `groupId: null` on all members of the affected group and destroys its record (`removeGroup(groupId)`) — with no trace, each member immediately returns to being governed by its own individual properties (never modified during grouping).
  - Selection of a single whole group ("1 unit, is a group" row): the general items "Ocultar"/"Mostrar" and the specific "Añadir a etiqueta" of the same context menu operate over the **group record** (`replaceGroup`) instead of each member separately — unlike those same items with a selection of loose components, which do apply as a block to each one.
- **Automatic dissolution**: `core/state.js#removeComponent` checks, after each deletion (including the copy cascade), whether any affected group is left with ≤1 member; if so, it clears its `groupId` and removes its `groups` entry in the same step (a single `emit('groups:changed', ...)` if any was dissolved) — a group of 0 or 1 member makes no sense as a unit.
- **Editing the group's properties** (00202): the "Editar" button in the group's row of the "Componentes" panel (next to "Desagrupar", both enabled whenever the row exists) opens `ui/groupModal.js` (`openGroupModal`) — a single-tab "General" modal: the group's id (editable, validates non-empty and non-duplicate against `isGroupIdTaken(id, getGroups(), group.id)`, same criterion as a component's ID) plus the usual "General" and "Etiquetas" sections (same fields/options as `ui/componentModal.js`, applied here to `workingGroup`). On save with the id changed, `editMode.js#openEditModalForGroup` first updates the `groupId` of all members and only then `replaceGroup(group.id, updated)`, so no member is momentarily pointing at a `groupId` absent from `groups`.
- **Individual editing of a grouped member** (00201, partially reverts the original restriction of 00193): [gotcha] double click on the canvas remains blocked (`renderTable()` wraps `onSelect` with a guard `if (component.groupId != null) return;` before calling `openEditModalFor`), but the "Editar" button of its row in the `ui/componentList.js` panel is enabled again and opens the modal normally (`openEditModalFor` itself no longer has any `groupId` guard). "Eliminar" remains available with no restriction. "Clonar" and "Copiar" of the panel, however, become disabled while the component is grouped — unlike the context menu, where those same actions remain unrestricted when shown over a whole group ("Desagrupar" enabled case of the table above).
- **Block movement**: dragging any member moves all the others keeping relative distances (same mechanism as manual multi-selection, `onMove` in `renderTable()`). The lock that prevents moving them is no longer each member's individual one: `canMove` of `renderTable()`/`modes/play/playMode.js` and the `moveSelectedComponent` filter (keyboard shortcut) use `getEffectiveGeneralProps(component, getGroups()).bloqueado` (`group.effectiveProps.rule`) — while the component is grouped, the governing "Bloqueado" is the **group record's** (editable from its properties modal) — the member's own has no effect until ungrouped.
- **"Componentes" panel**: each group gets its own synthetic row (`ui/componentList.js`, derived at render time from `groupId` — not a row from a separate array), with id = `groupId`, "Tipo" column = "Grupo", no own "Copia" column, and as actions "Editar" (00202, see previous point) and "Desagrupar", both always enabled. Each member still also appears in its own normal row, with "Editar"/"Eliminar" enabled and "Clonar"/"Copiar" disabled (see previous point).
  - **Order and visual nesting** (00204): the group row has its own editable "Orden" (`buildGroupRows`, computed as the minimum `order` of its members). Editing it moves the **whole block** to that position (`core/state.js#reorderGroupBlock`, see `002-component-model.md`), making its members consecutive there and recompacting the rest to make room. A group's members are **always** shown nested right below their group's row (indented + different background, `.component-list__row--member`), never interleaved with other rows, with their own "Orden" field disabled (not individually editable — the group's controls it). `computeDisplayedList` sorts by column/`order` at the **block** level (each group or loose component is a sortable unit), never reordering the members of the same group among themselves (they always keep their own ascending `order`); with a text/column filter active, a group is shown if it or some member matches, but only the members that individually match appear nested below. It participates in the text filter and the column filter/sort like any component row (e.g. "Grupo" appears as a filterable value of the "Tipo" column, with no special treatment), except the "Orden" column (not filterable, see also above).
- **Distinct outline on the table by who was clicked** (00201): beyond the existing selection highlight (`--selected`), belonging to a group adds no permanent badge, but it does nuance the outline *while the group is selected*. `editMode.js` keeps, alongside `selectedComponentIds` (the full selection), a second module Set `primarySelectedIds` with the ids that were the *direct* target of a click (never the whole group unit dragged with it) — updated in `toggleSelect`/`handleComponentContextMenu` (the clicked component becomes the only primary id) and fully emptied in `selectTag` (tag selection has no individual "clicked one"). `renderComponentsOnTable` receives `primarySelectedIds` as a new parameter and adds the class `is-group-passenger` (alongside `--selected`) to any selected component that belongs to a group and whose id is not in `primarySelectedIds` — `main.css` paints it with `outline-color: var(--text-muted)` (gray), same pattern as `is-copy` (red) but with no `:hover` variant.
  - [gotcha] `.is-group-passenger` wins over `.is-copy` (declared later in the CSS cascade) — see `ui.class.decision.is-group-passenger-wins-over-is-copy` in `00-namespace.md`.

`modes/play/playMode.js` renders the same infinite table, with components of any type drawn generically via `ui/componentRenderer.js`. It keeps its own transient module-level selection state (`selectedComponentId`, outside `renderPlayMode` to survive remounts on `components:changed`), tied to the right-click context menu: it reuses the per-type `--selected` class (`ui/componentRenderer.js`, parameter `selectedIds`, passed as a set of a single element or empty) without using `onToggleSelect` (left click does not change its behavior). It shows no separate listing.

## Component context menu in play mode

A right click on a component in `modes/play/playMode.js` calls `onContextMenu` (parameter of `renderComponentsOnTable`, see `006-ui-layer.md`) to select it and open `ui/contextMenu.js` (`openContextMenu`) next to the cursor.

- If `component.accionClickDerecho === 'ninguno'`: the callback returns doing nothing (neither selects nor opens the menu).
- If `'menuContextual'`: opens the menu with a general "Bloquear"/"Desbloquear" row that toggles `component.bloqueado` (pattern `replaceComponent`/`updateComponent`) — a binary toggle over the 3-value field: "Bloquear" sets `'juego'`, "Desbloquear" sets `'ninguno'` (independent of the previous value).
- The menu accepts a block of per-type specific actions (`specificItems`), separated from the general one by a divider line only if the block is non-empty (see `'mazo'` in `003-component-types.md`).

## Element context menu in edit mode

`modes/edit/editMode.js` also connects `onContextMenu` in its `renderComponentsOnTable` call (`handleComponentContextMenu`), unlike `playMode.js`, without gating it on `accionClickDerecho` or `bloqueado` (both fields restrict nothing in this mode).

- A right click on a component whose unit (see "Groups in edit mode" above) is already fully in `selectedComponentIds` leaves the selection intact; otherwise it replaces it with that whole unit (same replacement criterion as `toggleSelect`, no toggle).
- [gotcha] Menu-visibility gate: `handleComponentContextMenu` counts "units" the same way as "Groups in edit mode" (`unitCount` = distinct `groupId`s + loose components; `hasGroup` = any `groupId`). With `unitCount >= 2 && hasGroup` (a whole group mixed with any other element) it `return`s **without opening any menu at all** — neither section.
- The menu always acts on the resulting set (`affectedComponents`):
  - General section: "Ocultar"/"Mostrar" (binary label by `affectedComponents.every(c => c.oculto)`; always enabled) toggles `oculto` of each affected (pattern `replaceComponent`/`updateComponent`) and, if the affected is a copy (`copyOf`) with `sincronizado: true`, disables the sync (`sincronizado: false`) in the same change. Followed by "Clonar" (`core/component.js#cloneComponent` + `addComponent`, one by one) and "Copiar" (same pattern with `createCopy`) — both disabled if no affected element is clonable (all with `copyOf`), silently skipping those that do have it in a mixed selection. "Eliminar" reuses `attemptDeleteComponents` (same path as DEL). "Agrupar"/"Desagrupar" close the section — enabled per the table in "Groups in edit mode" (`canGroup = unitCount >= 2 && !hasGroup`; `canUngroup = unitCount === 1 && hasGroup`), each wrapped in `runWithProgressModal` (async, double `requestAnimationFrame`). For a single whole group as selection, "Ocultar"/"Mostrar" and the specific "Añadir a etiqueta" operate over the **group record** (`replaceGroup`) instead of each member — see "Groups in edit mode".
  - Specific section: "Voltear carta" (`t('menu.flipCard')`, from 00205) — present **only** when `affectedComponents.length > 0 && affectedComponents.every(c => c.type === 'carta')`; on click, flips each affected card's `properties.caraActual` `'frontal'`↔`'trasera'` independently (`replaceComponent`/`updateComponent`), without touching `bloqueado`, `oculto` or a copy's sync. Then "Añadir a etiqueta" row — `<select>` (row type of `ui/contextMenu.js`, see `006-ui-layer.md`) with existing tags (`getTags()` + `core/textSort.js#sortByName`); choosing one adds its id to `etiquetaIds` of each affected element that did not have it (without touching the rest of `etiquetaIds`), shows `showToast('Etiqueta añadida')`. With no tag in the game, the row is disabled.

## Visual indicators in edit mode

| Indicator | Trigger passed to `renderComponentsOnTable` | Condition | Play mode |
|---|---|---|---|
| Lock badge | `showLockIndicator: true` | `bloqueado !== 'ninguno'` | Not passed — the lock is only perceived via the context menu |
| Hidden badge (bottom-right, coexists with lock) | `showHiddenIndicator: true` | `oculto` active | Not passed — `playMode.js` filters hidden components directly before rendering |
| Copy badge (bottom-left, background `var(--error)`, see `../style/001-tokens-visual.md`) | `showCopyIndicator: true` | `copyOf` non-null | Not passed. `ui/componentRenderer.js` adds the class `is-copy` (alongside `--selectable`), used by `main.css` to paint the selection/hover outline and the `.component-id-label` background red (instead of blue) |

**Restricted drag in edit mode**: `editMode.js` passes `canMove: (component) => component.bloqueado !== 'todos'` to `renderComponentsOnTable` — a component with `bloqueado: 'todos'` cannot be dragged even in edit mode, though it remains editable/resizable/deletable. `playMode.js` uses `canMove: (component) => component.bloqueado === 'ninguno'` (drag in play mode only if no lock is active).

## Cards inside a deck

[gotcha] a card referenced by `properties.cartaIds` of a `'mazo'` (`core/deck.js`, `getCartaIdsEnAlgunMazo`) is **not drawn on the table in any mode** — unlike `oculto`, which is filtered only in play mode. Both modes exclude it from the list passed to `renderComponentsOnTable`. It still appears in the floating Components panel (unfiltered), the only way to locate/edit it without drawing it from the deck. In edit mode, dragging a selection made entirely of cards to overlap a deck offers to add them all to it (see `'mazo'`, `003-component-types.md`).

## "Recursos" panel (edit mode)

`editMode.js` mounts a second floating window "Recursos" (`ui/resourceList.js`), independent of "Componentes" (own position/width/collapse, `resourcePanelState`), only in edit mode.

- The "+ Añadir recurso" button opens a menu (`createAddMenu`) with three options, each opening a hidden `<input type="file">` (same `accept` of combined extensions):
  - "Subir fichero" (single file).
  - "Subir varios ficheros" (`multiple`).
  - "Subir carpeta" (`multiple` + `webkitdirectory`, filters by `file.webkitRelativePath.split('/').length === 2` to keep only the top level).
- All three handlers validate the extension (`core/resource.js`, `resourceTypeForFileName`) and reuse the internal function `loadResourceFromFile(file, { id, replace })` (reads and creates via `createResource`/`addResource`, or `replaceResource` if `{ replace: true }`).
- **Duplicate-name notice**: before reading each valid file, it checks whether a resource with that name already exists (`core/resource.js`, `findResourceByName`, case- and accent-insensitive).
  - Single-file path: on a match, opens `ui/resourceReplaceConfirmModal.js` before continuing — confirm replaces keeping `id`; cancel adds nothing.
  - Multi-file/folder paths: separate files with no conflict (processed in parallel, `Promise.all`) from those that do (includes collisions among files of the batch itself, resolved against the first). If there is a conflict, a single `openResourceReplaceConfirmModal` lists all duplicate names before completing the load as a replacement; with no conflict they are added normally.
- On finishing, always `ui/batchUploadSummaryModal.js` (`openBatchUploadSummaryModal`) with a count of additions (includes replacements) and, if any, detail of items skipped by format (table) and by being in a subfolder (count); a folder with no valid file notifies with `showErrorModal`.
- The table is always sorted alphabetically by name (`core/textSort.js` → `sortByName`, case- and accent-insensitive), applied inside `renderBody` (covers the full listing and the text-box-filtered result).
- The "Editar" button opens `ui/resourceModal.js`. The "Eliminar" button (list or modal) first checks `isResourceInUse` (`resource.usage.rule`, see `00-namespace.md`) — if in use, it blocks deletion with a notice; otherwise it asks for standard confirmation and deletes. Both deletion points share the same internal function in `editMode.js`.

## "Etiquetas" panel (edit mode)

`editMode.js` mounts a third floating window "Etiquetas" (`ui/tagList.js`), independent of the other two (own position/width/collapse, `tagPanelState`), stacked by default below "Recursos", only in edit mode. No "Tipo" column (tags have no type) and no clone action.

- Same column resize (`columnWidths` in `tagPanelState`, `ui/tableColumnResize.js`) and same free-text filter box (module state `filterText`, searches by `name`/`id`) as "Componentes"/"Recursos".
- Default order (no active column sort): alphabetical by name (`sortByName`), same criterion as "Recursos" and the "Etiquetas" section of `ui/componentModal.js`.
- "Elementos" column: shows per tag `getComponentsUsingTag(tag.id, components).length` (same criterion as deleting a tag in use), recomputed on every repaint. `renderTagList` receives `components` as its third positional argument (between `tags` and the callbacks object), propagated from `editMode.js` with `getComponents()` — the full remount of `renderEditMode()` on `components:changed`/`tags:changed` already keeps it up to date. It participates in the column-header menu, like "Nombre".
- The tag has no visual representation of its own on the table, but its row **is selectable**: a click anywhere on the row (outside action buttons, `stopPropagation`) calls `onSelectTag`/`selectTag`, which fully replaces `selectedComponentIds` with the ids of `getComponentsUsingTag(tag.id, components)` — deselecting the existing first; unlike `toggleSelect`, this replacement is always unconditional, no toggle or additive Ctrl mode. A member that is a card stored inside a `'mazo'` (`core/deck.js#getCartaIdsEnAlgunMazo`) is first drawn to the table with `core/state.js#sacarCartaDeMazo` before being selected (cards of the same deck appear stacked in its reveal zone, with no special distribution). Selected members are highlighted on the table and in Componentes like any manual multi-selection. The tag row is highlighted with `:focus` (`.tag-list__row`) while it keeps the browser's real focus — it turns off when focus moves away, with no "active tag" JS state.
- The "+ Añadir etiqueta" button opens `ui/tagModal.js` in create mode (no `tag`, no "Eliminar"); each row's "Editar" button opens the same modal in edit mode (with `tag`, "Nombre" prefilled, extra "Eliminar" button). The "Eliminar" button (list or modal) first checks whether the tag is in use (`getComponentsUsingTag`, looks at `etiquetaIds` in any component type): if not, it asks for standard confirmation (`confirm()`) and deletes (`removeTag`); if so, it opens `ui/tagDeleteConfirmModal.js` with the list of affected elements (id and type) — on accept, the tag is deleted and each affected element loses only that id from its `etiquetaIds` (keeps any other tag it had; becomes "Sin etiqueta" only if it was the only one); on cancel nothing is done. Both deletion points share the internal function `attemptDeleteTag` in `editMode.js`, which accepts an `onDeleted` callback so `ui/tagModal.js` closes itself after the async deletion (unlike `ui/resourceModal.js`, whose deletion contract is synchronous by relying on the native `confirm()`).

## Column-header sort and filter menu

Pattern common to the three edit-mode tables (Componentes, Recursos, Etiquetas). Clicking any column's name (all but "Acciones"; in Componentes, "Orden" only sorts, does not filter) opens `ui/columnHeaderMenu.js` (`openColumnHeaderMenu`): a dropdown with "Ordenar A..Z"/"Ordenar Z..A" (toggle: clicking the active one turns it off) and, if the column is filterable, a `<select>` with the distinct values of that column over the full unfiltered list, plus "Todos" by default.

- Unlike `ui/resourceList.js#createAddMenu` (`position: absolute`), this menu uses `position: fixed` inserted in `document.body` (same mechanism as `ui/contextMenu.js`) because the `<th>` that opens it lives inside containers with `overflow: auto`/`overflow: hidden` that would clip a `position: absolute`.
- `ui/tableColumnMenu.js` (`attachColumnMenu`) connects each `<th data-col>` with the menu, computes distinct values per column, paints the indicator (`.column-header-menu__indicator`) on headers present in `columnDefs`.
- Each table keeps its own transient module state (not persisted): `columnSort` (`{ column, direction } | null`, a single active sort, mutually exclusive between that table's columns) and `columnFilters` (`{ [column]: value }`, accumulable in AND with the existing free-text filter box).
- `core/textSort.js` adds `compareValues(a, b)` (numeric if both `number`, otherwise `localeCompare` case- and accent-insensitive) as a generic comparator, without touching `sortByName` (default order of Recursos/Etiquetas with no sorted column).
- The indicator is always inserted, with the modifier `.column-header-menu__indicator--active` marking the only case with something actually applied. The three `renderBody` functions of `ui/componentList.js`/`ui/resourceList.js`/`ui/tagList.js` always build `<table>`+`<thead>` before checking whether the list is empty, replacing only the `<tbody>` with a message row (`colspan` over all columns) in that case — so the header (and the column menu) does not disappear with an empty list.

## UI refresh and transient module state

Any component create/edit/delete in edit mode emits `components:changed`, which triggers a refresh (`main.js` re-invokes `renderEditMode()` fully). That is why `modes/edit/editMode.js` keeps the selection as module-level state, outside `renderEditMode` — otherwise it would be lost on every move/resize/edit, not only on page reload.

Panel collapse, position/width/height (drag/resize) and column widths live in `core/state.js` (`panelState`, see `007-persistence-build.md`) because they are persisted in autosave. Panel resize (`ui/resizeHandle.js`, `axis: 'both'` while expanded) with no maximum width/height limit, only a minimum (minimum height keeps the table header + one row visible) and staying inside the screen's right/bottom edge; a collapsed panel (no visible listing area) goes back to horizontal-only resize (`axis: 'x'`).

## Editable header title

The `<h1>` of `index.html` (empty in the source file, `ui/appTitle.js` fills it at runtime) shows the free text saved in `core/state.js` (`appTitle`, see `007-persistence-build.md`) always followed by the version (`v.NNNNN`, formatted by `core/appTitle.js` → `formatVersion()` from `CURRENT_VERSION` — different from `footer#app-version`'s format, which shows `CURRENT_VERSION` without a dot; both formats coexist without being unified).

- Only in edit mode is the free text editable: a click on the `h1` turns it into an in-place `<input>` (transient state `editing`, module variable of `ui/appTitle.js`, not persisted), confirmed with `blur`/Enter calling `setAppTitle()` — an empty value reverts without calling `setAppTitle()`.
- The version is never editable, in any mode.
- The default file name for "Exportar" (`ui/editModeToggle.js`) is the full title (`getFullAppTitle(getAppTitle())`).
- The lightweight "Exportar" JSON (`core/persistence.js` → `buildComponentsExport`) includes the current `appTitle`; on "Importar" (`parseImportedComponents`), that title is applied (`setAppTitle`) only if the file brings it and the chosen import mode is "Sobrescribir todo el juego" — in "Añadir a lo existente" the current game's title is not touched.

## Stacking order (z-index) of the floating panels

`modes/edit/editMode.js` keeps `panelStackOrder`, a module variable (outside `renderEditMode`) with keys `'component'`/`'resource'`/`'tag'` ordered bottom to top.

- Each of the three panel containers (`listContainer`/`resourceListContainer`/`tagListContainer`) has a `mousedown` listener in the capture phase that calls `bringPanelToFront(key, panelsByKey)`: moves that key to the end of `panelStackOrder` and reapplies the `z-index` of all three containers (`applyPanelStackOrder`, value `15 + index`) so the interacted one is always on top.
- The fixed `z-index: 15` the three containers had before in `main.css` has been removed: that value is now always assigned by `applyPanelStackOrder` inline.
- Transient, does not live in `core/state.js` nor persist: on reload it always returns to the default order (`['component', 'resource', 'tag']`).
