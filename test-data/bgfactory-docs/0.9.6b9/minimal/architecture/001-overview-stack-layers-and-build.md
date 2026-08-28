# 001 — Overview, stack, layers and build
**Area**: Architecture

Client-only board-game editor. Ships as one self-contained HTML file (JS + CSS + images + fonts inlined). No server, no accounts, no network at runtime (one exception: `documento` component external-URL `<iframe>`). Runs from `file://` only after build; dev runs `src/index.html` under a static server (ES modules).

## Stack

- Vanilla ES modules, no framework, no runtime transpile. anchor: src/main.js
- Build: `src/scripts/build.py`, Python stdlib only, no Node. anchor: src/scripts/build.py
- Vendored 3rd-party: `marked` (Markdown). anchor: src/vendor/marked.js
- Persistence: `localStorage`, single slot. anchor: src/core/persistence.js#STORAGE_KEY

## Layers

`arch.layer.*` — enforced by convention + code comments only, no tooling gate.

| Layer | Path | Role | May import |
|---|---|---|---|
| `arch.layer.data` | `src/data/` | static seed data | (nothing) |
| `arch.layer.core` | `src/core/` | domain model, pure logic (no DOM), central state, persistence, migrations | `core`, `data`, `vendor` |
| `arch.layer.modes` | `src/modes/{edit,play}/` | per-mode orchestration of table + panels | `core`, `ui` |
| `arch.layer.ui` | `src/ui/` | DOM rendering, modals, panels, infinite table | `core`, `ui` |
| `arch.layer.bootstrap` | `src/main.js` | wires eventBus → render/persist, hydrates state on load | all |

- [gotcha] `arch.layer.ui` must NOT import from `arch.layer.modes`. `sacarCartaDeMazo` lives in `src/core/state.js` (not `playMode.js`) specifically because both modes use it and `ui/*` cannot reach `modes/*`. anchor: src/core/state.js#sacarCartaDeMazo
- [gotcha] Source comments across `src/core/` and `src/ui/` cite doc paths `design/docs/architecture/**` and `design/docs/style/**` that do not exist on disk. Stale. Canonical docs now under `previo-sdd/docs/{architecture,style,features}`.

## Build pipeline

`arch.build.pipeline` — anchor: src/scripts/build.py

1. Walk ES import graph from `src/main.js`; topological order.
2. Strip `import`/`export`; wrap each module in `__modules['path'] = function(module, exports, require){…}`; minimal `require`/`__cache` runtime prepended.
3. Inline CSS `url(...)` assets and HTML `<img>/<link>/<source>` refs as `data:` URIs (skips `data:`/`http(s)`/`//`/`#`).
4. Concatenate runtime + wrapped modules + `require('main.js')`; embed bundle in `<script>` and CSS in `<style>` inside a copy of `src/index.html`.
5. Output `src/_output/versions/index-v{NNNN}.html` (git-ignored).

- [gotcha] `build.py` mutates the repo: reads `CURRENT_VERSION` from `src/data/version.js`, increments by 1, writes it back before bundling. anchor: src/data/version.js#CURRENT_VERSION
- `arch.build.version.format` — `v` + zero-padded digits, e.g. `v00230`. Width preserved from prior value.
- `src/index.html` must contain literal `{VERSION}` in `<title>`; build replaces it with `v.{NNNN}` and fails hard if absent.
