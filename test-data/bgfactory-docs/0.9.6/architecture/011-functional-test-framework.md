# 011 — Functional test framework

**Area**: Testing

Location: `src/test/`. Dev-only. Nothing here enters the deliverable: `src/scripts/build.py` walks imports from `src/main.js` only (`ENTRY_MODULE = 'main.js'`, `visit_module(ENTRY_MODULE)`), and no `src/test/` file is reachable from `src/main.js`. `src/scripts/generate-version.py` unchanged.

> **[importante] Regla de cobertura por cambio.** Todo cambio que **añada** funcionalidad debe añadir los tests funcionales correspondientes (`src/test/functional/*.test.js`, con su `registerFeature` y códigos `FT-<NNN>-<nn>`). Todo cambio que **modifique** funcionalidad debe actualizar los tests existentes para reflejar el nuevo comportamiento. Todo cambio que **elimine** funcionalidad debe borrar los tests que la validaban (y, si procede, sus fixtures). El cambio no se considera completo hasta que `npm test` pasa y `TRACEABILITY.md` queda regenerado sin anomalías.

## Files and responsibilities

| File | Runtime | Responsibility |
|---|---|---|
| `package.json` (repo root) | — | Dev project descriptor. `"private": true`, `"type": "module"`. `devDependencies.playwright` pinned. Scripts: `test`, `test:setup`, `test:all` (see *Install and run*). Not consumed by `build.py` or the deliverable. |
| `src/test/setup.js` | Node | Orchestrates `npm install` (skipped if `node_modules/playwright/package.json` exists) then `npx playwright install chromium`. Idempotent. |
| `src/test/run.js` | Node | Only file importing Node built-ins and `playwright`. Static HTTP server over `src/` + Chromium headless driver + per-file navigation + summary + screenshot + `generateTraceability` call + exit code. |
| `src/test/runner-page.html` | Browser (headless) | Page loaded per test file. Replicates the 5 containers of `src/index.html` (`#app-title`, `#edit-toolbar`, `#mode-switcher`, `#content`, `#app-version`) + `<script type="application/json" id="initial-state">`. Inline `<script type="module">` reads `?file=`, imports `./harness.js`, dynamic-imports the test file, runs `harness.run()`, publishes results on `window`. Does NOT load `main.js` or `styles/main.css`. |
| `src/test/harness.js` | Browser | Own test engine. No Node/Playwright import. Runs inside the headless page. |
| `src/test/helpers.js` | Browser | State reset, mode mounting, fixture loading, deterministic mocks. Imports from `../core/*`, `../modes/*`, `../ui/editModeToggle.js`. |
| `src/test/traceability.js` | Node | `generateTraceability(featuresDir, features, outPath)`. Invoked by `run.js` after the batch. |
| `src/test/functional/*.test.js` | Browser | One file per feature or feature group. Test cases. |
| `src/test/fixtures/*.json` | data | Games in `buildComponentsExport` format (`{ version, components, resources, tags, componentGroups, appTitle }`), loaded via `loadFixture(...)`. `errantes-componentes.json`, `mazo-repetido.json` = stress fixtures. |
| `src/test/TRACEABILITY.md` | generated | Feature ↔ test map. Regenerated on every `npm test`. `[gotcha]` not hand-editable — overwritten. Versioned; no dates or last-run status inside, so its diff only reflects coverage changes. |
| `src/test/_screenshots/` | generated | Per-file failure screenshot. Git-ignored. |

## Test levels

| Level | Mounts | Asserts on |
|---|---|---|
| state | nothing (imports `core/*`, calls actions directly) | `state.js` getters, emitted events |
| ui | `mountEditMode()` / `mountPlayMode()` (see `helpers.js` contract) | `#content` DOM + state |

Each test picks its level. A test file declares which `design/docs/features/` entry it validates via `registerFeature`.

## Engine contract (`harness.js`)

```
describe(name: string, fn: () => void)
it(name: string, fn: () => void | Promise<void>)          name starts with FT-<NNN>-<nn>
beforeEach(fn) / afterEach(fn)                             root-level or inside a describe; async allowed
expect(actual) -> { toBe, toEqual, toBeTruthy, toBeFalsy, toBeNull,
                    toContain, toHaveLength, toBeGreaterThan, toThrow }
registerFeature({ primary: number, secondary?: number[] = [] })   once per test file
getRegisteredFeature() -> { primary, secondary } | null
run() -> Promise<Array<{ name, status: 'pass' | 'fail', expected?, actual?, error? }>>
```

- `expect` matcher failure throws `Error` with `.expected`, `.actual`, `.isAssertion = true`.
- `toEqual` = deep structural equality (plain objects/arrays).
- `run()` order per `it`: root `beforeEach` -> block `beforeEach` -> body -> block `afterEach` -> root `afterEach`. `afterEach` runs even if the body threw. An `afterEach` throw fails an otherwise-passing case.
- `registerFeature` stores into a module variable; `getRegisteredFeature()` reads it back.

## Helper contract (`helpers.js`)

```
resetState()                     loadComponents/Resources/Tags/Groups([]) + loadPanelState/
                                 ResourcePanelState/TagPanelState({}) + loadAppTitle(DEFAULT_APP_TITLE) +
                                 loadTableText('') + loadResourcesSeeded(false) +
                                 localStorage.removeItem('bgfactory:state' | 'bgfactory:lang')
mountChrome()                    renderModeSwitcher(#mode-switcher) + renderEditToolbar(#edit-toolbar)
                                 [motivación] in production main.js#renderAll mounts these, not renderEditMode/renderPlayMode
mountEditMode() -> HTMLElement    ensureI18n (idempotent) + setMode(EDIT) + mountChrome() + renderEditMode(#content); returns #content
mountPlayMode() -> HTMLElement    same, PLAY
mountAppTitle() -> HTMLElement    ensureI18n (idempotent) + renderAppTitle(#app-title); returns #app-title
                                 [motivación] production main.js#renderAll repaints #app-title on every *:changed; tests call it explicitly after a state/mode change they want reflected
loadFixture(name) -> merged       fetch ./fixtures/<name>.json -> parseImportedComponents -> mergeImportedGame(mode:'overwrite') -> loadComponents/Resources/Tags
mockRandom(seq: number[])         Math.random cycles through seq
captureDownload()                 patches URL.createObjectURL + HTMLAnchorElement.prototype.click; records { filename, _pending: Promise<parsed> }
getLastDownload() -> Promise<{ filename, data }>   [async] Blob.text() is async
injectFileImport(obj, { mode='overwrite', conflictMode='overwrite' })   mergeImportedGame directly, bypasses ui/editModeToggle.js modals
restoreAllMocks()                 restores Math.random, URL.createObjectURL, HTMLAnchorElement.prototype.click
dispatchContextMenu(el, { x=0, y=0 })   el.dispatchEvent(mousedown {button:2}) THEN el.dispatchEvent(contextmenu {button:2}); both { bubbles:true, cancelable:true, clientX:x, clientY:y }
getOpenContextMenu() -> HTMLElement | null   document.body.querySelector('.context-menu')
```

- [gotcha] `dispatchContextMenu` fires `mousedown` before `contextmenu`, not `contextmenu` alone. The browser emits `mousedown` first on a real right-click; `ui/contextMenu.js` closes an already-open menu from that `mousedown` (`handleOutsideClick`) *before* the mode's `onContextMenu` runs for the new target. Without the leading `mousedown`, a "menu already open, right-click another element" case ends with selection cleared: the previous menu's `onClose` runs after the new selection is set (`modes/play/playMode.js#onContextMenu` sets `selectedComponentId`, then calls `openContextMenu`, which closes the prior menu → its `onClose` nulls `selectedComponentId`).
- `getOpenContextMenu` reads `document.body`, not `#content`: `ui/contextMenu.js#openContextMenu` does `document.body.appendChild(menu)` (`position: fixed`), so a `#content`-scoped query never finds it.

## Batch execution flow (`run.js`)

1. Start `node:http` static server over `src/` on `127.0.0.1`, ephemeral port (`listen(0)`). Handler resolves the request path and serves only if it stays within `SRC_DIR` (path-traversal block -> `403`); `Content-Type` by extension; `404` if absent.
2. `import('playwright')` -> `chromium.launch({ headless: true })`. If the import fails: instructions + `exit(2)`.
3. `readdir('src/test/functional')` filtered to `*.test.js`, sorted.
4. Per file: `page.goto('/test/runner-page.html?file=functional/<file>')`; `waitForFunction(window.__BGF_TEST_RESULTS__ !== undefined)`; read `window.__BGF_TEST_RESULTS__` and `window.__BGF_TEST_FEATURES__`.
5. First `fail` of a file -> `page.screenshot()` into `src/test/_screenshots/<file>.png`.
6. Print `Total: N — OK: X — FALLOS: Y`; per failure: `file › name`, `esperado:` / `obtenido:` or `error:`.
7. `generateTraceability(FEATURES_DIR, allFeatures, TRACEABILITY_OUT)`.
8. `browser.close()`, `server.close()`.
9. `process.exit(anyFailure || traceOutcome.hasAnomaly ? 1 : 0)`.

`FEATURES_DIR` = `previo-sdd/design/docs/architecture/../features` resolved from `run.js`.

### Isolation

One page navigation per test **file** (not per case). Navigation re-instantiates the ES module graph: fresh `core/state.js`, `core/eventBus.js` `listeners` `Map` empty — no leak between files. `beforeEach` inside a file only does `resetState()` + `localStorage` clear.

### Page ↔ driver contract

| `window` global | Set by | Read by | Shape |
|---|---|---|---|
| `__BGF_TEST_RESULTS__` | `runner-page.html` after `harness.run()` | `run.js` step 4 | `Array<{ name, status, expected?, actual?, error? }>` |
| `__BGF_TEST_FEATURES__` | `runner-page.html` from `harness.getRegisteredFeature()` | `run.js` step 4 | `{ primary: number, secondary: number[] } \| null` |

## Traceability (`traceability.js`)

`generateTraceability(featuresDir, features, outPath) -> { hasAnomaly: boolean }`

- Parses `<featuresDir>/INDEX.md` lines `- [NNN — Title](NNN-slug.md)` -> `Map<number, "NNN — Title">`. Non-matching lines skipped.
- `features`: `Array<{ file, primary: number, secondary: number[], caseCodes: string[] }>`. `caseCodes` = `FT-\d+-\d+` prefixes extracted by `run.js` from each `it` name.
- Writes `outPath`: `<!-- GENERADO AUTOMÁTICAMENTE ... -->` header, `| Funcionalidad | Tests |` table ordered by number (primary codes, then `<code> (secundaria)`, or `—`), then two sections:
  - "Tests que declaran una funcionalidad inexistente" — any `primary`/`secondary` `NNN` with no `INDEX.md` entry. Non-empty -> `hasAnomaly: true` -> `run.js` exit `1`.
  - "Funcionalidades sin ningún test" — informational only, never sets `hasAnomaly`.

### Test code convention

`FT-<NNN>-<nn>`: `<NNN>` = `design/docs/features/` entry number of the test's `primary` feature, `<nn>` = two-digit sequence within that feature. Carried as the `it` name prefix. `registerFeature({ primary, secondary })` per file supplies the feature link; `run.js`/`traceability.js` associate a file's `it` cases with its `primary`.

- Anomaly `NNN` inexistent = batch failure (`exit 1`). Feature with no test = report line only.
- `design/docs/features/` entries are never edited to record tests — the only test↔feature materialization is `TRACEABILITY.md`.

## External dependencies

- `playwright` — `devDependency`, pinned version. Chromium binary via `npx playwright install chromium`.
- `[gotcha]` Node/npm are test-only. `src/scripts/build.py` and the deliverable do not depend on them. `src/test/` never enters the bundle (`build.py` walks imports from `src/main.js` only).
- `.gitignore` (repo root): `node_modules/`, `/src/test/_screenshots/`.

## Install and run

| Command | Effect |
|---|---|
| `npm run test:setup` | `npm install` (if needed) + `npx playwright install chromium`. Run once, or after cloning. |
| `npm test` | `node src/test/run.js` — the batch. Requires setup done. |
| `npm run test:all` | `test:setup` then the batch, in one command. |

Exit code `0` = all pass and no traceability anomaly; `1` = any failure or any `NNN` inexistent; `2` = `playwright` not installed.

## Release pipeline gate

`npm test` also runs automatically during release prep, wired as `### Step 1` of the `## In the middle` section of `previo-sdd/stuff/custom-version-pipeline.md` (consumed by `pv-version` step 4.1).

- Runs against the real `src/` tree — the same code just packaged into the deliverable ZIP (`pv-version` step 4 already ran).
- Order: after the deliverable ZIP + `copy-build-artifacts.py`, before `copy-docs.py` and the changelog (`pv-version` steps 5–6).
- Exit `2` handling in this context: run `npm run test:setup` once, re-run `npm test` once. Second `2` = environment failure, release stops.
- Exit `1` = release stops before `copy-docs.py`/changelog. The deliverable ZIP may already exist (built in step 4); `docs/*.zip` and `changelog.md` are not generated. User is pointed at the report path, not shown the failure list, then asked whether to analyze failures.
- Exit `0` = release continues normally.

| Artifact | Path | Contents |
|---|---|---|
| Per-version test report | `previo-sdd/versions/{XXXX}/test-report.md` | Written always (pass or fail). `Versión`, `Fecha` (`YYYY-MM-DD HH:MM`), `Resultado` ∈ {`Correcto`, `Con fallos`}, `Total: N — Correctos: X — Fallidos: Y`. On failure, appends `Tests fallidos:` + the `✗ <file> › <case>` / `esperado:`/`obtenido:` (or `error:`) block copied verbatim from `npm test` stdout. |

- [gotcha] `test-report.md` ≠ `TRACEABILITY.md`. `TRACEABILITY.md` (`src/test/`, versioned) carries no date or run status by design, so its diff only reflects coverage changes. `test-report.md` (`previo-sdd/versions/{XXXX}/`, per release) is a dated per-run execution record — a distinct file, one per prepared version.

## Decisions

- `test.decision.no-main-js` — the headless page does not load `src/main.js`. `[motivación]` `main.js` bootstrap wires ~18 `eventBus` listeners (`renderAll`/`persistState` on every `*:changed`) and the autosave; per-test explicit mounting (`mountChrome` + `renderEditMode`/`renderPlayMode`) keeps `resetState` deterministic and avoids listener accumulation. A boot/persistence case that genuinely needs the full `main.js` sequence would load it in its own `runner-page` (Playwright reloads per file, so it would not contaminate other files) — not needed by the current batch.
- `test.decision.page-reload-isolation` — isolation is one page navigation per test file. `[motivación]` `eventBus` `listeners` live in a module-level `Map`; a fresh module graph per file zeroes it with no manual `off()` bookkeeping.
- `test.decision.own-engine` — own `describe`/`it`/`expect` engine instead of a third-party runner. `[motivación]` the engine runs inside the browser page with no Node; the project takes no runtime dependency, and a third-party runner would not run in that context unbundled.
- `test.decision.playwright-over-jsdom` — real headless Chromium, not jsdom. `[motivación]` the fragile features (block drag with relative distances, `fitToBounds`, panel resize, card-over-deck overlap, `position: fixed` menu placement, dice/deck canvas) need real layout and canvas; jsdom provides neither.

## Test files

[gotcha] not a live inventory — `TRACEABILITY.md` (regenerated per `npm test`) is the authoritative feature↔test map, including per-file case counts. This table only records each file's feature link and level; case codes here are the seed set, not kept in sync as files grow.

| File | Feature | Level |
|---|---|---|
| `functional/app-title.test.js` | 030 | state + ui |
| `functional/component-crud.test.js` | 002 | state |
| `functional/top-controls.test.js` | 039 | state + ui |
| `functional/fresh-boot.test.js` | 036 | state |
| `functional/autosave.test.js` | 029 | state |
| `functional/hidden-in-play.test.js` | 016 | ui |
| `functional/export-import.test.js` | 032 | state |
| `functional/synced-copies.test.js` | 005 (primary), 022 (secondary) | ui — worked example |
| `functional/carta.test.js` | 022 | state + ui |
| `functional/context-menu-play.test.js` | 026 | ui — `dispatchContextMenu` + `getOpenContextMenu` over `.context-menu` in `document.body`; `mockRandom` for deterministic `shuffleCartaIds` (FT-026-08) |
| `functional/edit-context-menu.test.js` | 027 (primary), 034 (secondary) | ui — `dispatchContextMenu` + `getOpenContextMenu`; local `seedMultiSelection` (plain + Ctrl `click` to build a real multi-selection before the right click); asserts `.context-menu__item--disabled` for row-enabling rules and `getComponents()` for effects. [gotcha] `editMode.js`'s `selectedComponentIds` is module state that `resetState()` does not clear — each case uses distinct component ids so the right click always hits the "replace selection" branch |
| `functional/infinite-table.test.js` | 001 | ui — mounts `createInfiniteTable` on an inline-sized host and parses `worldEl.style.transform` (`translate(x, y) scale(z)`); [gotcha] `table.js` camera (`cameraX`/`cameraY`/`zoom`) is module state `resetState()` does not clear — `beforeEach`/`afterEach` call `fitToBounds(null)`; CSS is not loaded so the host and the `.infinite-table` viewport get explicit inline `width`/`height` for `getBoundingClientRect()` to measure |
| `functional/component-modal-tabs.test.js` | 002 | state + ui — `openComponentModal` (`.modal-overlay` on `document.body`, 5 `.modal__tab`, `.btn-eliminar` only when editing, `.btn-accept` disabled on invalid id); spies `window.confirm` for delete; local `isIdValid` replicates the private `validateId`. Coexists with `component-crud.test.js` (same `primary: 2`); case codes continue from `FT-002-13` |
| `functional/component-transform.test.js` | 015 | state + ui — plain `click` replaces the whole selection (`toggleSelect` `else` branch), Ctrl+`click` adds; `.resize-handle` present only with `selectedIds.size === 1`; `.<type>--movable` / `.component-lock-badge` gated by group-effective `bloqueado` and mode; `moveSelectedComponent(dx, dy)` skips `bloqueado === 'todos'`. [gotcha] same `selectedComponentIds` module-state caveat — distinct ids per case |
| `functional/error-modal.test.js` | 033 | ui — `showErrorModal(title, message, detail)` builds `.modal-overlay > .modal` with `.modal__header--error` + `.modal__error-icon` `!`; `.modal__error-detail` only when `detail` passed; `.btn-cancel` and overlay `mousedown`+`click` close; asserts no `.toast` (error ⇒ modal, never toast) |
| `functional/component-title.test.js` | 035 | state + ui — model defaults (`createComponent`); `.component-title-label` painted in play mode only when `mostrarTitulo` and non-empty `tituloTexto`, never in edit mode; `mostrarTitulo` group override via `createGroup` + `loadGroups` (`getEffectiveGeneralProps`); `openComponentTitleModal` opacity slider/text sync, clamp 0–100, NaN discarded, Cancel does not call `onAccept` |
| `functional/version-indicator.test.js` | 037 | state + ui — `formatVersion`/`getVersionedProductName` off `CURRENT_VERSION`; `getTableText`/`setTableText` round-trip; [gotcha] `main.js#renderAppVersion` is **not exported** and the runner does not load `main.js`, so the one ui case replicates a minimal `renderAppVersionInto` inside the file (same technique as `fresh-boot.test.js`'s local `seedDefaultResources`) to check the `#app-version` structure (`.app-version__name`, `.app-version__repo a` with `target="_blank"`/`rel="noopener"`, `.app-version__table-text` + `.app-version__separator` above the fixed lines only when the free text is non-empty, rendered as plain text) |
| `functional/component-panel.test.js` | 003 | state + ui — `nextCloneId`/`cloneComponent`/`nextCopyId`/`createCopy` pure rules at state level; row selection/highlight, per-row action buttons (absent on a Copy row, disabled on a grouped component), bulk-vs-single delete (`bulkDeleteConfirmModal` list vs spied `confirm()`), collapsed group rows via `expandedGroupIds`, panel persistence read back from a seeded `panelState`, `onToggleCollapse` → `setPanelState`, `bringPanelToFront` z-index. [gotcha] `editMode.js`'s `selectedComponentIds`/`panelStackOrder` are module state `resetState()` does not clear — distinct ids per case; the z-index case restores the stack order by ending on the component panel |
| `functional/column-header-menu.test.js` | 004 (primary), 003 + 006 (secondary) | state + ui — `compareValues`; `attachColumnMenu`/`columnHeaderMenu` over both `.component-list` and `.resource-list`: always-present header indicator (off vs `--active`), menu in `document.body` outside `#content`, sort as an exclusive per-table toggle, accumulable column filters (AND), filter option values computed over the full list, "Orden" column sort-only, empty-filter body with header intact, column state surviving a remount. [gotcha] `componentList.js`/`resourceList.js` `columnSort`/`columnFilters`/`filterText` are module state `resetState()` does not clear — `beforeEach` mounts once on the empty list (which zeroes them) before seeding |
| `functional/resource-panel.test.js` | 006 | state + ui — `getComponentsUsingResource` (counts each component once, any depth), `sortByName` accent/case-insensitive; table columns `nombre`/`usos`/`tipo`/`acciones`, computed non-editable "Usos" cell, `sortByName` render order, live text filter over name/type-label/id (accent/case-insensitive, "Usos" excluded), empty-filter body, transient `filterText`, `resourcePanelState` independent from the component `panelState`. [gotcha] same `resourceList.js` module-state caveat — `beforeEach` mounts empty before seeding. [gotcha] the image type label "Imagen" contains the substring "ma", so short name filters must avoid it (`map`, not `ma`) |
| `functional/resource-image-modal.test.js` | 007 | ui — `openResourceModal` on a simulated image resource; parses `previewImg.style.transform` (`translate(x, y) scale(z)`): initial 100 %, `+`/`-` centered `zoomAt(0,0,·)`, lower clamp `ZOOM_MIN` (1) / upper clamp `ZOOM_MAX` (5), wheel zoom + `preventDefault`, reset to 100 % centered, zoom-level indicator always `/^\d+%$/`, pan only when `zoom > 1`, and the Typography modal has no `resource-modal--image` / zoom controls (`.resource-modal__font-preview` instead). CSS not loaded ⇒ `previewBox.getBoundingClientRect()` is 0×0, so the wheel case asserts direction, not the exact centered offset |
| `functional/multi-idioma.test.js` | 038 | state + ui |
| `functional/catalogo-propiedades.test.js` | 040 | state + ui |
| `functional/orden-apilado.test.js` | 012 | state + ui |
| `functional/subir-al-interactuar.test.js` | 013 | state + ui — drag/dice roll/card flip/card draw in `mountPlayMode` trigger `reorderComponent(id,1)` when `subirAlMoverInteractuar`; per-type default cases, independence from `bloqueado`, play-mode-only exclusivity, group override. [gotcha] the runner does not load CSS: stacking is checked via the model's `order`, not z-index |
| `functional/interacciones-programadas.test.js` | 014 (primary), 005 (secondary) | state + ui — `core/interactions.js` (`getInteractionsForType`/`isInteractionActive`); "Interacciones" tab of `openComponentModal` (`<select>` `activa`/`ninguna` + right-click row `ninguno`/`menuContextual`); play-mode effect (no `dice--clickable`/`carta--clickable`, `onContextMenu` does not open the menu); `.context-menu__info` section reflects "Ninguno" (`--none`); `syncCopyWithOriginal` propagates `interaccionesDesactivadas`+`accionClickDerecho` |
| `functional/visor-documentos.test.js` | 021 | state + ui — `core/markdown.js` (marked v18.0.6, one GFM case) and `core/sanitizeHtml.js` (strips `<script>`, `on*`, `javascript:`); text-branch render (`.document-viewer__content` = `sanitizeHtml(markdownToHtml(...))`) and URL-branch render (`<iframe sandbox>`, `.document-viewer__error` on the `error` event); blank sheet with no warning |

See also [007 — Development/build flow and persistence](007-persistence-build.md), [008 — Code conventions](008-code-conventions.md).
