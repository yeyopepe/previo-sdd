# 001 — Architecture overview

**Area**: Architecture

## What it is

BG Factory — visual editor + play surface for tabletop games. Ships as one self-contained `.html` (editor + data + assets). No install, no server, no accounts, no network at runtime.

## Stack

| Item | Value |
|---|---|
| Language | JavaScript, vanilla, ES modules (`import`/`export`) |
| Framework | none |
| Runtime deps | 2, vendored: `src/vendor/marked.js` (Markdown), `src/scripts/vendor/javascript-obfuscator.browser.js` (build only) |
| Package manager | none — no `package.json` anywhere |
| Build | `src/scripts/build.py`, pure Python 3, no Node |
| Persistence | `localStorage` (single slot) + embedded JSON seed in the document |
| Source root | `/src` (~83 `.js`, 1 `.css`, 1 `.html`) |

## Layers

Segment order = aggregate to detail. Import direction is strict; violations are called out inline in the code (see `state.js#sacarCartaDeMazo`).

| Layer | Dir | Responsibility | May import from |
|---|---|---|---|
| Data | `src/data/` | Static seed data, version constant. No logic, no deps. | (nothing) |
| Core | `src/core/` | Domain model, pure logic, central state, persistence, event bus. | `core/`, `data/`, `vendor/` |
| UI | `src/ui/` | DOM rendering, modals, the infinite table, toasts, shortcuts. | `core/`, `data/`, `ui/` |
| Modes | `src/modes/edit/`, `src/modes/play/` | Compose UI + core into the two top-level screens (edit / play). | `core/`, `ui/`, `data/` |
| Bootstrap | `src/main.js` | Wire event bus to render + persist; hydrate state on load. | everything |

- [gotcha] `ui/*` must NOT import from `modes/*`. `state.js#sacarCartaDeMazo` lives in `core/` (not `modes/play/`) specifically because `ui/componentModal.js` needs it and cannot reach `modes/`.
- `core/` split: pure per-type logic modules (`deck.js`, `dice.js`, `tag.js`, `group.js`, `cardProportions.js`, `textBoxLayout.js`, `colorUtils.js`, `textSort.js`, `cardFaceElements.js`) have zero cross-layer deps and are reused from both `ui/` and `modes/`.

## Runtime architecture

- **State**: single module-level `state` object in `core/state.js` (`mode`, `components`, `resources`, `tags`, `groups`) + separate module-level panel-state vars. Mutated only through `core/state.js` exports (`addX`/`replaceX`/`removeX`/`loadX`).
- **Notification**: every mutation `emit`s a named event on `core/eventBus.js` (`Map<eventName, Set<handler>>`, synchronous). No framework reactivity.
- **Render**: `main.js` subscribes `renderAll` to every `*:changed` event. `renderAll` fully rebuilds the active screen each time — `ui/table.js` is recreated on every repaint; camera (pan/zoom) is kept in module scope to survive the rebuild.
- **Persist**: `main.js` subscribes `persistState` to the same events → `core/persistence.js#saveState` writes the whole state to `localStorage` synchronously on every change.

## Data flow (load)

```
main.js
  1. persistence.loadState()            -> localStorage 'bgfactory:state'
  2. raw === null                       -> persistence.readSeedState()  (embedded <script id="initial-state">)
  3. seed also absent                   -> seedDefaultResources()  (data/defaultResources.js)
  4. state.loadResourcesSeeded(...)     BEFORE loadComponents/loadResources  [gotcha]
  5. state.loadComponents(...)          -> runs 7 in-place silent migrations, then compactOrders
```

- [gotcha] `resourcesSeeded` flag must be hydrated **before** `loadComponents`/`loadResources`: those emit `*:changed` → trigger synchronous autosave, which would persist `false` and re-seed default resources on every reload.

## Cross-cutting: backward-compatible loading

`core/state.js#loadComponents` runs 7 best-effort in-place migrations on every load (`migrateFichas`, `migrateCartaMedidasReales`, `migrateGrupoIdToEtiquetaIds`, `migrateDeckIdToEtiqueta`, `migrateBloqueado`, `migrateAccionClickDerecho`, `migrateTableroSimple`). `core/persistence.js#parseState` reads legacy key aliases (`decks`/`groups` → `tags`, `deckPanelState`/`groupPanelState` → `tagPanelState`).

- [motivación] Opening a file exported from a different app version is the primary use case, not an error — hence migrations never throw and never block startup.

## Key decisions

| Decision | Rationale |
|---|---|
| `build.decision.no-node` — build in pure Python | Project ships without any Node toolchain; contributors need only Python 3. |
| Single self-contained `.html` deliverable | Portability: copy the file anywhere, double-click, it runs offline with editor + data inside. |
| Own minimal pub/sub instead of a framework | No build step for the dev workflow (ES modules load natively); full rebuild-on-change is fast enough at this scale. |
| Full re-render on every change | Simplicity over granular DOM diffing; camera state kept in module scope to survive it. |
| Assets embedded as data URIs | Keeps the "one file" invariant; images converted to WebP on upload (`core/imageConversion.js`) to bound size. |

## See also

- `002-modules.md` — per-module responsibility map (`core/`, `ui/`, `modes/`).
- `003-persistence-and-model.md` — persisted shape, component model, migrations.
- `004-build.md` — `build.py` pipeline.
- `00-namespace.md` — canonical name tree.
