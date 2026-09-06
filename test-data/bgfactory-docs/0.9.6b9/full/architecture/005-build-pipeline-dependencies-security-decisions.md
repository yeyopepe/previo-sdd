# 005 — Build pipeline, dependencies, security, decisions
**Area**: Build & security

Build pipeline, dependency surface, security posture, and recorded design decisions. Namespace: [00-namespace.md](00-namespace.md).

## Build pipeline

[src/scripts/build.py](../../../src/scripts/build.py). Pure Python 3, stdlib only, no Node.

```
1. version bump:   read CURRENT_VERSION 'v{N}' from src/data/version.js, +1, write back (before bundling)
2. module graph:   DFS from src/main.js over  import { ... } from '...';   (IMPORT_PATTERN, named imports only)
3. transform each module:
     export function f / export const X   ->  strip 'export', collect name, append  module.exports.f = f
     import { a, b } from './x'            ->  const { a, b } = require('resolved/rel/path');
     wrap:  __modules['rel/path'] = function(module, exports, require) { ... }
4. runtime prepend: minimal require()/__cache/__modules loader
5. CSS:   read styles/main.css, replace url(...) (non data:/http) with data: URIs (base64)
6. HTML:  read index.html, strip the <link>/<script> tags, inline <img>/<link>/<source> src/href as data: URIs,
          inject <style>{css}</style> after </title>, inject <script>{bundle}</script> before </body>
7. {VERSION} placeholder in <title> -> 'v.{version}'  (hard error if marker absent)
8. write src/_output/versions/index-v{version}.html   (gitignored: /src/_output/versions/*.*)
```

- [gotcha] `IMPORT_PATTERN` only matches `import { named } from '...'`. Default imports, namespace imports (`import * as`), side-effect imports are not supported — the codebase uses named imports exclusively.
- [gotcha] `EXPORT_FUNCTION_PATTERN` / `EXPORT_CONST_PATTERN` only match `export function` and `export const` at statement level. No `export default`, no `export { ... }`, no `export let/class`.
- MIME table in `build.py` covers png/jpg/jpeg/gif/svg/webp/ico + woff/woff2/ttf/otf/eot.
- `src/scripts/obfuscate_bundle.js` + `src/scripts/vendor/` exist alongside `build.py` (optional bundle obfuscation step, Node).

## Dependencies

| Dependency | Where | Purpose | Update mechanism |
|---|---|---|---|
| `marked` | vendored at [src/vendor/marked.js](../../../src/vendor/marked.js) | Markdown → HTML (CommonMark + GFM) for `documento` component | manual file replace |
| Python 3 stdlib | build only | `build.py` (`base64`, `re`, `pathlib`) | — |
| Node | build only, optional | `obfuscate_bundle.js` | — |

- No `package.json`, no lockfile, no runtime `npm` deps. Runtime is browser + inlined assets only.
- `marked` output is **not trusted**: always passed through `core/sanitizeHtml.js` before DOM insertion ([core/markdown.js](../../../src/core/markdown.js)).

## Security posture

Threat model: the exported single `.html` re-opens user-authored content in a fresh session, potentially from a `file://` origin. Pasted `<script>` or inline handlers would otherwise execute on reopen.

### sanitizeHtml

[src/core/sanitizeHtml.js#sanitizeHtml](../../../src/core/sanitizeHtml.js). Detached `<template>`, then:
- remove every `<script>`.
- remove every attribute whose lowercased name starts with `on`.
- remove `href`/`src` whose value matches `/^\s*javascript:/i`.

- [gotcha] Denylist, not allow-list. Does NOT handle: `<iframe>`/`<object>`/`<embed>`, `style` attributes, `srcdoc`, `data:` URIs in `href`/`src`, `formaction`, SVG-borne script.
- [gotcha] The `documento` component embeds an arbitrary user `url` in an `<iframe>` with **no `sandbox` attribute** ([componentRenderer.js](../../../src/ui/componentRenderer.js)).
- `security.decision.sanitize-denylist-not-allowlist`: current choice. Any change to `documento` rendering or `sanitizeHtml.js` must revisit whether an allow-list sanitizer + iframe `sandbox` is warranted.

### Other user-input surfaces (covered)

| Surface | Handling |
|---|---|
| image upload | extension allow-list ([resource.js#resourceTypeForFileName](../../../src/core/resource.js)); raster re-encoded through canvas → WebP ([imageConversion.js](../../../src/core/imageConversion.js)) |
| font upload | extension allow-list (`ttf otf woff woff2`) |
| JSON import | `parseImportedComponents` requires `components` array; merge is pure data, no eval |
| text variables | `{name}` substitution restricted to a fixed key set per type ([textVariables.js](../../../src/core/textVariables.js)) |

## Recorded design decisions

| Path | Decision | Rationale |
|---|---|---|
| `build.decision.python-not-node` | build tool is Python 3 stdlib, not a JS bundler | zero install beyond Python; contributors don't need a Node toolchain |
| `build.decision.custom-require-runtime` | hand-rolled `require`/`module.exports` shim instead of a real bundler | keeps `build.py` small; only needs named import/export support the codebase uses |
| `arch.decision.ui-cannot-import-modes` | `ui/` forbidden from importing `modes/` | one-way layer dependency; forces shared ops (`sacarCartaDeMazo`) into `core/state.js` |
| `arch.decision.generic-component-no-subclasses` | one `Component` shape, `type` string, behavior branches in `ui`/`modes` | new component types need no new entity class; `properties` bag absorbs type-specifics |
| `state.decision.synchronous-full-persist` | every mutation → full synchronous localStorage write, no debounce | simplicity; state is small enough (single-user, single table); quota errors swallowed |
| `state.decision.best-effort-load-migrations` | load-time migrations never throw, best-effort | a corrupt or partial legacy field must never block startup |
| `persistence.decision.import-skips-version-check` | `parseImportedComponents` has no `version` gate | cross-version file import is the primary use case, not an error |
| `deck.decision.pure-compute-caller-applies` | `computeSacarCartaDeMazo` returns changes; caller applies via `state.js` | keeps `deck.js` free of state/DOM deps; same pattern as `dice.js` |
| `security.decision.sanitize-denylist-not-allowlist` | `sanitizeHtml` strips known-bad, keeps the rest; `documento` iframe unsandboxed | see Security posture — flagged for revisit on any related change |
| `group.decision.group-props-override-member` | grouped component's general props come from the group registry, not its own fields | a group behaves as one unit on the table while grouped |
| `versions.decision.build-owns-version-counter` | `build.py` auto-increments `CURRENT_VERSION`; independent of change/fix codes | deliverable version is a monotonic build counter, decoupled from the pv-* workflow |

## Configuration / environment

- No env vars, no config files, no feature flags.
- Only environment requirement: Python 3 on `PATH` to run `build.py`; a modern browser to open the deliverable.
- Gitignored outputs: `node_modules/`, `dist/`, `__pycache__/`, `*.pyc`, `/src/_output/versions/*.*`, `/.claude/settings.json`, `/.claude/settings.local.json`.
