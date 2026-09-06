# 001 — Overview

**Area**: Architecture

## Product

BG Factory: visual editor to build and play digital board games. Deliverable =
one self-contained HTML file (JS, CSS, images, fonts inlined). Runs by
double-click in any modern browser. No install, account, server, or network.

## Stack

```
language: vanilla JS, ES modules (native, no bundler at dev time)
framework: none
styling: one file — src/styles/main.css (CSS custom properties in :root)
markdown: src/vendor/marked.js (CommonMark + GFM), wrapped by core/markdown.js
build: src/scripts/build.py (Python 3, no Node.js)
persistence: browser localStorage, single slot, key "bgfactory:state"
portability: full state also embeddable as JSON (export) or as an inline seed in the deliverable HTML
```

## Layers (`src/`)

| Layer | Dir | Responsibility | May import |
|---|---|---|---|
| entry | `main.js` | bootstrap: hydrate state from storage/seed, wire eventBus → render + persist, seed default resources | core, ui, modes, data |
| domain | `core/` | pure model + logic: component/deck/dice/group/tag/resource, state store, persistence, import merge, sanitize, layout math | core, data, vendor |
| modes | `modes/edit/`, `modes/play/` | compose ui widgets into the two operating modes over one shared state | core, ui |
| ui | `ui/` | DOM widgets and modals; `table.js` is domain-agnostic, the rest know the component model | core, ui |
| data | `data/` | static catalogs: `defaultResources.js`, `version.js` (`CURRENT_VERSION`) | — |

[gotcha] `core/` modules must not import from `ui/` or `modes/`. Pure-logic
`core/` files (`deck.js`, `dice.js`, `tag.js`, `colorUtils.js`,
`cardProportions.js`, `textBoxLayout.js`, `cardFaceElements.js`) import nothing
at all.

## Runtime model

```
state store:  core/state.js — module-level singleton `state` {mode, components[], resources[], tags[], groups[]}
              + panel-state singletons (component/resource/tag panels) + appTitle + resourcesSeeded flag
mutation:     exported setters mutate in place, then emit(<domain>:changed) on core/eventBus.js
reaction:     main.js subscribes every <domain>:changed to (a) renderAll() and (b) persistState()
render:       renderAll() fully rebuilds the active mode's DOM on every change (no diffing)
persist:      persistState() serializes whole state to localStorage synchronously on every change
```

[gotcha] Every `addResource()` / `loadComponents()` etc. triggers a synchronous
autosave. `main.js` hydrates the `resourcesSeeded` flag *before* calling
`loadComponents()`/`loadResources()` so the first autosave does not persist
`false` and re-seed default resources on every reload.

## Persistence contract

```
STORAGE_KEY = "bgfactory:state"                          (core/persistence.js)
saved shape: { version, components[], resources[], tags[], groups: componentGroups[],
               panelState, resourcePanelState, tagPanelState, appTitle, resourcesSeeded }
load guard:  parsed.version === CURRENT_VERSION AND Array.isArray(components), else { error: true }
```

- Version mismatch ⇒ treated as no saved state (falls back to embedded seed, then to default resources).
- Back-compat key aliasing (old "Mazo"/"Grupo" naming): `tags` ← `tags ?? groups ?? decks`; `tagPanelState` ← `tagPanelState ?? groupPanelState ?? deckPanelState`.
- `deriveMissingGroups()` backfills a group record per `groupId` present on components but absent from `componentGroups` (pre-group-registry saves).
- Silent migration of the removed `ficha` component type → `carta` on load, via `core/fichaMigration.js` (never throws; best-effort + error list, ignored on silent load).

## Security-relevant invariant

[motivación] Project state is reopened as a standalone HTML file in other
sessions, so any persisted user HTML is an XSS vector on reopen.

```
inv: all user-authored HTML (document-viewer component) passes core/sanitizeHtml.js before DOM insertion
     sanitizeHtml strips <script>, inline event handlers, and javascript: URLs
     marked.js output is NOT self-sanitizing → core/markdown.js output also routed through sanitizeHtml
```

## Build

`src/scripts/build.py`:

```
1. walk ES import graph from src/main.js
2. strip import/export → tiny runtime require/module.exports shim
3. inline CSS url(...) assets and HTML <img>/<link>/<source> refs as data: URIs
4. concat transformed modules + runtime + CSS into a copy of src/index.html
5. write src/_output/versions/index-vXXXX.html   (XXXX = CURRENT_VERSION in src/data/version.js)
```

[gotcha] ES modules do not load over `file://`; dev requires `src/index.html`
served by a local static server.

<Expanded by pv-do over time.>
