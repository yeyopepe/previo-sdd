# 002 — State, events and persistence
**Area**: Architecture

## Event bus

`arch.state.eventBus` — anchor: src/core/eventBus.js

- `on(name, handler) -> off-fn`, `off(name, handler)`, `emit(name, payload)`.
- Per-name `Set` of handlers. Synchronous dispatch.

## Central state

`arch.state.store` — anchor: src/core/state.js

- One module-level `state = { mode, components[], resources[], tags[], groups[] }`.
- Plus module-level singletons: `panelState`, `resourcePanelState`, `tagPanelState`, `appTitle`, `resourcesSeeded`.
- Every mutator `emit`s a `<x>:changed` event: `mode:changed`, `components:changed`, `panelState:changed`, `resources:changed`, `resourcePanelState:changed`, `tags:changed`, `tagPanelState:changed`, `groups:changed`, `appTitle:changed`.
- `getX()` return live references (not copies). Callers must not mutate returned arrays/objects in place.

## Render + persist wiring

`arch.state.wiring` — anchor: src/main.js

| Event | Effects |
|---|---|
| `mode:changed` | `renderAll` |
| `components:changed` | `renderAll`, `persistState` |
| `panelState:changed` | `persistState` |
| `resources:changed` | `renderAll`, `persistState`, `syncFontFaces` |
| `resourcePanelState:changed` | `persistState` |
| `tags:changed` | `renderAll`, `persistState` |
| `tagPanelState:changed` | `persistState` |
| `groups:changed` | `renderAll`, `persistState` |
| `appTitle:changed` | `renderAll`, `persistState` |

- `arch.render.model` — any `components:changed` / `mode:changed` fully rebuilds the active mode's DOM (`renderEditMode` / `renderPlayMode` clear their container and re-create).
- [gotcha] Transient session state that must survive a rebuild lives at module scope in `editMode.js` / `playMode.js` / `table.js`, NOT inside the render fn, and is deliberately not persisted: `selectedComponentIds`, `primarySelectedIds`, `panelStackOrder` (editMode); `selectedComponentId` (playMode); `cameraX`/`cameraY`/`zoom` (table). Reset on page reload.
- `persistState` is synchronous and fires on every relevant mutation (no debounce).

## Persistence

`arch.persist` — anchor: src/core/persistence.js

- `arch.persist.key = "bgfactory:state"` — anchor: src/core/persistence.js#STORAGE_KEY
- `saveState(...)` — `try/catch`, quota/other errors silently swallowed (no user interruption). anchor: src/core/persistence.js#saveState
- `loadState()` — `null` if key absent; else `parseState`. anchor: src/core/persistence.js#loadState
- `arch.persist.parseState.reject` — `parseState` returns `{error:true}` on: JSON parse failure, `parsed.version !== CURRENT_VERSION`, `!Array.isArray(parsed.components)`. anchor: src/core/persistence.js#parseState
- `readSeedState()` — reads `<script type="application/json" id="initial-state">` from the document; used on first run when nothing is stored. anchor: src/core/persistence.js#readSeedState
- `parseImportedComponents(raw)` — version-tolerant variant (no `version` check). Cross-version import is the primary use case, not an error. anchor: src/core/persistence.js#parseImportedComponents

## Startup sequence

`arch.startup` — anchor: src/main.js

1. Register all `on(...)` subscriptions; `initGlobalShortcuts`.
2. `loadState()`.
   - `saved.error` → `showErrorModal` + `seedDefaultResources`.
   - `saved` ok → hydrate `resourcesSeeded` flag BEFORE `loadComponents`/`loadResources` (both emit `*:changed` → synchronous autosave that would persist `false` otherwise), then load panel states, appTitle, components, resources, tags, groups (`deriveMissingGroups` backfill). Seed default resources if `!resourcesSeeded`.
   - no `saved` → `readSeedState()`; if present hydrate from it, else `seedDefaultResources`.
3. `syncFontFaces(getResources())`.
