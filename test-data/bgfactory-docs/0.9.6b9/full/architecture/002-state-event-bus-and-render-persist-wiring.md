# 002 — State, event bus, and render-persist wiring
**Area**: State & events

State singleton, event bus, and the render/persist wiring. Namespace: [00-namespace.md](00-namespace.md).

## Central state

[src/core/state.js](../../../src/core/state.js). Module singleton. Not exported directly — reached via getters/mutators only.

```
state = {
  mode: 'play' | 'edit' = 'play',
  components: Component[] = [],
  resources: Resource[] = [],
  tags: Tag[] = [],
  groups: Group[] = [],          # component-grouping registry, NOT tags
}
# module-level, outside `state`, persisted as sibling keys:
panelState:         PanelState
resourcePanelState: PanelState
tagPanelState:      PanelState
appTitle: string = 'BG Factory'
resourcesSeeded: bool = false    # once-only seed guard for DEFAULT_RESOURCES

PanelState = {
  collapsed: bool = false,
  position: { left: number, top: number } | null = null,
  width: number | null = null,
  height: number | null = null,
  columnWidths?: object,
}
```

### Getter / mutator pattern

Per collection: `get{X}()`, `add{X}()`, `replace{X}(id, updated)`, `remove{X}(id)`, `load{X}(arr)`.

| Op | Emits | Notes |
|---|---|---|
| `setMode(m)` | `mode:changed` | |
| `addComponent(c)` | `components:changed` | bumps every existing `order` +1, new component gets `order = 1` |
| `replaceComponent(id, u)` | `components:changed` | if `u` is an original (no `copyOf`): propagates synced fields to all `copyOf === id`; renames copy ids if original id changed |
| `removeComponent(id)` | `components:changed` (+ `groups:changed` if a group dissolved) | cascade-deletes all copies (`copyOf === id`); `compactOrders`; a group left with ≤1 member auto-dissolves and its registry entry is destroyed |
| `reorderComponent(id, raw)` | `components:changed` | clamps to `1..n`, shifts others |
| `reorderGroupBlock(memberIds, rawStart)` | `components:changed` | moves N contiguous group members as a block; no early-exit on unchanged start (must still consecutivize a scattered block) |
| `loadComponents(arr)` | `components:changed` | runs migration pipeline first (see below) |

- [gotcha] `sacarCartaDeMazo(mazoId, cartaId)` lives in `state.js`, not in `modes/play`, because `ui/` cannot import `modes/`. Pulls a card out of a deck's `cartaIds` (from any pile position, not only top), reveals it face-up in the deck's reveal zone, `reorderComponent(carta, 1)`.

### Load-time migration pipeline

`loadComponents(arr)` runs these in order. All **best-effort, in-place, never throw** — must not block startup.

```
1. migrateFichas              type 'ficha' → 'carta' (via fichaMigration.js)
2. migrateCartaMedidasReales  card content: design-units on abstract CARD_DESIGN_WIDTH canvas → real px
                              (multiply coords by the width-only scale factor the old renderer used)
3. migrateGrupoIdToEtiquetaIds  scalar `grupoId` / array `grupoIds` → `etiquetaIds: string[]`
4. migrateDeckIdToEtiqueta    `properties.deckId` (old per-card field) → append to `etiquetaIds`
5. migrateBloqueado           bool → 'ninguno' | 'juego' | 'todos'  (true≡'juego', false≡'ninguno')
6. migrateAccionClickDerecho  missing → 'menuContextual' (preserve old always-open behavior; new components born 'ninguno')
7. migrateTableroSimple       type 'tablero' → 'tableroSimple'
8. compactOrders              sort by `order` (fallback: array index), reassign contiguous 1..n
```

- [motivación] Historical rename chain: the tag concept was "Mazo" → "Grupo" → "Etiqueta". A separate, newer "Grupo" concept (component grouping) reuses the word — hence `grupoId` migrations map to `etiquetaIds`, while `groupId` (grouping) is unrelated.

## Event bus

[src/core/eventBus.js](../../../src/core/eventBus.js).

```
on(name: string, handler: fn) -> unsubscribe: fn
off(name: string, handler: fn) -> void
emit(name: string, payload: any) -> void      # synchronous, iterates a Set
```

Internal: `Map<string, Set<handler>>`. No wildcard, no priority, no async.

### Event catalog

| Canonical event | Payload | Legacy aliases still emitted/listened |
|---|---|---|
| `mode:changed` | `mode` | — |
| `components:changed` | `components[]` | — |
| `panelState:changed` | `panelState` | — |
| `resources:changed` | `resources[]` | — |
| `resourcePanelState:changed` | `resourcePanelState` | — |
| `tags:changed` | `tags[]` | `decks:changed`, `groups:changed` |
| `tagPanelState:changed` | `tagPanelState` | `deckPanelState:changed`, `groupPanelState:changed` |
| `appTitle:changed` | `appTitle` | — |

- [gotcha] `groups:changed` is a **legacy alias of `tags:changed`**, not an event for the component-grouping registry. Grouping changes are broadcast on `components:changed` (members carry `groupId`) plus `groups:changed` only on auto-dissolve — same channel name, historical collision.

## Render / persist wiring

[src/main.js](../../../src/main.js) is the only wiring point.

```
mode:changed              -> renderAll
components:changed         -> renderAll, persistState
panelState:changed        -> persistState
resources:changed         -> renderAll, persistState, syncFontFaces(resources)
resourcePanelState:changed -> persistState
tags:changed              -> renderAll, persistState
tagPanelState:changed     -> persistState
groups:changed            -> renderAll, persistState
appTitle:changed          -> renderAll, persistState
```

- `renderAll()` = re-render title + mode switcher + edit toolbar + active mode.
- [gotcha] Every mutation triggers a **synchronous** full `persistState()` to localStorage. No debounce. `saveState` swallows quota errors silently.
- [gotcha] Any `components:changed` fully remounts the active mode. Transient session state (multi-selection, panel z-order) is kept in module-level vars **outside** the render function so it survives the remount; it is not persisted.

## Startup sequence

[src/main.js](../../../src/main.js), after wiring:

```
saved = loadState()                        # localStorage 'bgfactory:state'
if saved.error:  showErrorModal + seedDefaultResources()
elif saved:
    loadPanelState / loadResourcePanelState / loadTagPanelState (if present)
    loadAppTitle(saved.appTitle)
    loadResourcesSeeded(saved.resourcesSeeded === true)   # BEFORE loadComponents/loadResources
    loadComponents(saved.components)
    loadResources(saved.resources)
    loadTags(saved.tags ?? [])
    loadGroups(deriveMissingGroups(components, saved.componentGroups ?? []))
    if !resourcesSeeded: seedDefaultResources()
else:                                        # no localStorage
    seed = readSeedState()                   # <script id="initial-state"> in the document
    if seed: hydrate from seed (same shape) ; else seedDefaultResources()
syncFontFaces(getResources())
```

- [gotcha] `resourcesSeeded` must be hydrated **before** `loadComponents`/`loadResources`: those emit `*:changed` → synchronous autosave, which would persist `false` if the flag isn't set yet.
- [gotcha] `seedDefaultResources()` calls `markResourcesSeeded()` **before** adding, because each `addResource` triggers a synchronous autosave.
