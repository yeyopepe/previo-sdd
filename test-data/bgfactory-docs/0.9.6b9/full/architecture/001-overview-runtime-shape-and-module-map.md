# 001 — Overview, runtime shape and module map
**Area**: Overview

Namespace root: [00-namespace.md](00-namespace.md). Cite concepts/assertions by canonical path, not by re-description.

## Product

- BG Factory: client-only visual board-game editor. Deliverable = one self-contained `.html` file (JS/CSS/images/fonts inlined).
- No backend, no accounts, no network calls at runtime. Fully offline after load.
- Two runtime modes: `edit` (author components) and `play` (interact with pieces on an infinite table).

## Runtime shape

- Dev-time: ES modules under `/src`, loaded via `<script type="module" src="main.js">`.
- Build-time: [src/scripts/build.py](../../../src/scripts/build.py) walks the ES import graph from `main.js`, rewrites `import`/`export` into a tiny `require`/`module.exports` runtime, inlines assets as `data:` URIs, emits `src/_output/versions/index-v{NNNNN}.html`.
- [gotcha] `build.py` mutates source: increments `CURRENT_VERSION` in [src/data/version.js](../../../src/data/version.js) by 1 on every run, before bundling, and writes it back to disk.
- No Node, no npm, no bundler. Single vendored lib: [src/vendor/marked.js](../../../src/vendor/marked.js).

## Layers

Import direction is enforced by convention (comments in code), not tooling.

| Layer | Path | Responsibility | May import |
|---|---|---|---|
| data | `src/data/` | static catalogs (`version.js`, `defaultResources.js`) | nothing |
| core | `src/core/` | pure domain logic, central state, event bus. No DOM. | `core/`, `data/` |
| ui | `src/ui/` | DOM rendering, modals, panels, infinite table | `core/`, `ui/` |
| modes | `src/modes/edit/`, `src/modes/play/` | top-level screen composition per mode | `core/`, `ui/` |
| bootstrap | `src/main.js` | hydrate state, wire eventBus → render/persist | all |

- [gotcha] `ui/` must NOT import `modes/`. Cross-mode domain operations (e.g. `deck.sacarCartaDeMazo`) live in [src/core/state.js](../../../src/core/state.js), not in a mode file, so `ui/` can reach them.

## core/ module map

| File | Responsibility | Purity |
|---|---|---|
| `state.js` | central singleton state + getters/mutators + load-time migration pipeline | mutates module state, emits events |
| `eventBus.js` | pub/sub (`on`/`off`/`emit`), synchronous | mutates listener map |
| `persistence.js` | localStorage read/write, seed read, import parse, export build | localStorage I/O |
| `component.js` | `Component` factory + clone/copy/group id helpers + copy-sync | pure |
| `resource.js` | `Resource` (image/font) factory + in-use detection (deep walk) | pure |
| `tag.js` | `Tag` factory + `getComponentsUsingTag` | pure |
| `group.js` | component-grouping registry factory + `getEffectiveGeneralProps` + backfill | pure |
| `deck.js` | shuffle, reveal-zone geometry, `computeSacarCartaDeMazo` | pure |
| `dice.js` | face-value list, roll, validate | pure |
| `interactions.js` | `TYPE_INTERACTIONS` registry + `isInteractionActive` | pure |
| `textVariables.js` | `{name}` substitution in free-text fields | pure |
| `importMerge.js` | merge imported game into current state (add/overwrite × conflict modes) | pure |
| `fichaMigration.js` | extinct `ficha` → `carta` conversion, best-effort, never throws | pure |
| `markdown.js` | `marked` wrapper → always piped through `sanitizeHtml` | pure |
| `sanitizeHtml.js` | strip `<script>`, `on*`, `javascript:` before DOM insertion | DOM (detached template) |
| `cardProportions.js` | proportion catalog (poker/tarot/square/circular/hex/triangle/free) | pure data |
| `cardFaceElements.js` | combined stacking order of formas + textBoxes on a card face | pure |
| `colorUtils.js` | `hexToRgba` | pure |
| `textBoxLayout.js` | text align/margins → flex style | pure |
| `textSort.js` | `sortByName` (locale `es`, accent-insensitive) | pure |
| `styleClipboard.js` | in-memory card-style copy/paste, never persisted | module state |
| `appTitle.js` | app title + non-editable version suffix | pure |
| `fileExport.js` | `downloadJson` via Blob + object URL | DOM |
| `imageConversion.js` | raster image → WebP via canvas on upload | canvas |

## modes/ + ui/ high level

| File | Role |
|---|---|
| `modes/edit/editMode.js` (~924 lines) | infinite table + 3 floating panels (components / resources / tags), multi-select, group ops, context menu, resource upload flows |
| `modes/play/playMode.js` (~283 lines) | infinite table, direct piece rendering, per-type click interactions, right-click menu (per-component configurable) |
| `ui/table.js` | `createInfiniteTable` (pan/zoom world), `fitToBounds` |
| `ui/componentRenderer.js` | `renderComponentsOnTable`, `paintCartaFace`, `getComponentsBounds`, `formatComponentIdentifier` |
| `ui/componentModal.js` | per-type `DEFAULT_*_PROPERTIES`, `createDefaultComponent`, main edit modal |
| `ui/visualEditorModal.js` | shared visual editor for card faces + custom board (image + formas + textBoxes) |
| `ui/globalShortcuts.js` | ESC/Enter/Delete/arrows — domain-agnostic, knows only modal DOM contract |
| `ui/*Modal.js` (~40 files) | one modal per task; DOM contract `.modal-overlay > .modal > .modal__footer` with `.btn-cancel`/`.btn-accept`/`.btn-eliminar` |
