# 007 — Development/build flow and persistence

**Area**: Persistence & build

## Development and build

- **Development**: `src/index.html` (not the deliverable) is opened with a local static server (e.g. VSCode's "Live Server" extension) — native ES modules (`<script type="module">`) do not load correctly via `file://`. This file references the `/src` modules directly.
- **Build**: `src/scripts/build.py` walks the `import`/`export` graph from `src/main.js`, transforms each module to a small runtime `require`/`module.exports` system (no bundlers or Node.js, only Python), inserts the result together with the CSS of `src/styles/main.css` inside a copy of `src/index.html`. Result: a single self-contained file written to `src/_output/versions/index-v{NNNN}.html` (`NNNN` = `CURRENT_VERSION` of `src/data/version.js`) — the portable deliverable.
  - Asset inlining: `build.py` (`embed_css_asset_urls` / `embed_html_asset_refs`) inlines as `data:` URIs only assets referenced from `main.css` `url(...)` or from `index.html` `<img>`/`<link>`/`<source>` — NOT assets referenced only from JS. `.webp` is a recognised MIME.
  - [gotcha] a module needing an image bundled (e.g. `ui/splashScreen.js`, 00245, the 4 `resources/img/bgfactory-logo-color_<n>.webp` splash logos) references it as `background-image: url(../resources/img/…)` in a `main.css` rule and toggles that class from JS — not as an `<img src>` set in JS, which `build.py` would leave as a live `file://`/HTTP path.

## Persistence and file save

`src/index.html` includes an empty `<script type="application/json" id="initial-state"></script>` that survives the build (copied as-is) and the runtime download (filled before downloading) — the state seed embedded in each copy of the HTML.

`parseState(raw)` return is discriminated, not a generic `{ error: true }`. Since 00250 there is a single error value — `{ error: 'corrupt' }` — for every non-restorable save; a wrong-version save is one more cause of it, with no branch or message of its own (no published version exists yet, so no old schema can be in circulation to migrate):

| Case | Return |
|---|---|
| `JSON.parse` throws | `{ error: 'corrupt' }` |
| `parsed` is an object ∧ `parsed.version !== CURRENT_VERSION` | `{ error: 'corrupt' }` (checked before the `components` check; the version check itself is kept, only its outcome is unified) |
| `parsed` falsy ∨ `!Array.isArray(parsed.components)` (with `parsed.version === CURRENT_VERSION`) | `{ error: 'corrupt' }` |
| otherwise | success object (no `error` field) |

`readSeedState()` unchanged: `return result.error ? null : result;` — any truthy `error` discards the embedded seed silently, falls to defaults.

```
Startup (main.js):
  showSplashScreen() [ui/splashScreen.js]  — step 0, before initI18n(). Overlay appended to document.body,
                                             self-removed after 5s. Independent of state/i18n/mode; does not
                                             alter any step below. See 006-ui-layer.md, 010-internationalization-i18n.md.
  loadState() [core/persistence.js, localStorage]
    null (key bgfactory:state absent)  → bootFromSeedOrDefaults()                                   — no notice
    { error: 'corrupt' }               → bootFromSeedOrDefaults() + showToast('No se ha podido recuperar el estado guardado.')
                                         (any non-restorable save: unparseable JSON, no components array, or other version)
    success object                     → hydrate panelState/resourcePanelState/tagPanelState + loadAppTitle + loadTableText + loadResourcesSeeded + loadComponents + loadResources + loadTags + loadGroups — no notice

bootFromSeedOrDefaults()  [local to main.js]:
  readSeedState() [<script id="initial-state">]
    → has seed → loadAppTitle + loadTableText + loadResourcesSeeded + loadComponents + loadResources + loadTags + loadGroups
    → no seed  → seedDefaultResources()
```

- [gotcha] startup never calls `showErrorModal` — a non-restorable `localStorage` save is a non-blocking `showToast`, not a modal to dismiss. `showErrorModal` (`ui/errorModal.js`) stays in use elsewhere (`ui/editModeToggle.js`, `modes/edit/editMode.js`).
- The `{ error: 'corrupt' }` path runs the exact same fallback as `null` (`bootFromSeedOrDefaults()`), plus a `showToast`.

### Autosave (`core/persistence.js`)

- Subscribed to `components:changed`, `panelState:changed`, `resources:changed`, `resourcePanelState:changed`, `tags:changed`, `tagPanelState:changed`, `appTitle:changed`, `tableText:changed` (`core/eventBus.js`) from `main.js`.
- `persistence.serializedFields` (see `00-namespace.md`): `saveState()` serializes `{ version: CURRENT_VERSION, components, panelState, resources, resourcePanelState, resourcesSeeded, tags, tagPanelState, componentGroups, appTitle, tableText }` to `localStorage` on any of those changes.
- A save with no `appTitle`, or with an empty/non-string value, is treated as `core/appTitle.js` → `DEFAULT_APP_TITLE`.
- `tableText` (00250): `parseState` returns `''` when `parsed.tableText` is missing or not a string. No migration — pre-00250 saves simply lack the key. NOT in `buildComponentsExport`/`parseImportedComponents` (local display preference, like `panelState`; see `state.tableText` in `00-namespace.md`).
- `tags:changed` also triggers a full repaint (`renderAll`), not only autosave.
- A single slot per browser/profile (`localStorage` is not isolated per file under `file://`), with no persistence across browsers/devices.
- On startup, with a valid save in `localStorage` that brings `panelState`/`resourcePanelState`/`tagPanelState`, they are hydrated with `loadPanelState()`/`loadResourcePanelState()`/`loadTagPanelState()` before the first render; if they are not there, each panel uses its default values (expanded, default position/width/height).
- `panelState` shape: `{ collapsed: boolean, position: {left,top}|null, width: number|null, height: number|null, columnWidths: object|null, expandedGroupIds: string[] }`.
  - `expandedGroupIds` (00239): `groupId`s of the "Componentes" panel's group rows the user expanded explicitly. Absence of a `groupId` = that group is collapsed (default state). Pruned of ids with no matching real group (2+ members) on every `renderComponentList` render — a stale `groupId` reused later never shows expanded by surprise. With a text/column filter active, matching groups render force-expanded regardless of `expandedGroupIds`, without mutating it.
  - [gotcha] `loadPanelState(newPanelState)` normalizes `expandedGroupIds` to `[]` when absent or not an array — pre-00239 saves simply lack the key, no migration.
  - NOT in `buildComponentsExport`/`parseImportedComponents` JSON (like the whole of `panelState`) — it is a local display preference, not part of the exported game.
- `resources` and `tags`: if they are missing or not an array in the save/seed, `[]` is assumed instead of invalidating the whole state. `componentGroups` follows the same criterion (`[]` if missing/not an array).
- Row selection (`selectedComponentIds`) is not part of any `panelState`, is never persisted.
- **Backward compatibility**: only `parseImportedComponents` (the import path) reads `tags`/`tagPanelState` with a chained fallback to `groups`/`groupPanelState` and then to the oldest keys `decks`/`deckPanelState`. Since 00250 `parseState` (startup) no longer does — it reads `tags`/`tagPanelState` only. `componentGroups` has no such alias — it is a new collection. See `group.persist.decision.key-componentGroups` and the "Backward compatibility" table in `004-groups-resources.md`.

### Language preference (`localStorage` key `bgfactory:lang`, change 00244)

- Separate `localStorage` key from the state slot `bgfactory:state`. Read by `initI18n()` (`core/i18n.js`) as the first step of `main.js` startup, before state resolution and startup toasts.
- Value ∈ `{'es', 'en'}` (`SUPPORTED_LANGUAGES`). Absent/unsupported → autodetection: `navigator.language` startsWith `'es'` ? `'es'` : `'en'`. Autodetection result is NOT written back — only an explicit `setLanguage()` writes.
- NOT in `persistence.serializedFields`, NOT in `buildComponentsExport`'s JSON. Survives `CURRENT_VERSION` changes (unlike `bgfactory:state`, discarded by `parseState` on version mismatch). No migration — pre-00244 saves simply lack the key.
- See [010 — Internationalization (i18n)](010-internationalization-i18n.md).

### File save

[gotcha] there is no whole-app "Guardar" action any more — `src/ui/editModeToggle.js` (`.edit-toolbar`) only offers "Importar"/"Exportar"; a full-app HTML download (`buildExportHtml`/`downloadHtml`) existed in earlier versions of `core/fileExport.js` but has since been removed (only present today inside `src/_output/versions/index-v*.html`, past build artifacts, not in current `/src`). `core/fileExport.js` now exposes only `downloadJson(filename, data)`, used by the "Exportar" flow below.

### Export/Import with selection (`core/importMerge.js` + `ui/exportSelectionModal.js`/`ui/importSelectionModal.js`/`ui/importConfirmModal.js`/`ui/importReportModal.js` in `ui/editModeToggle.js`)

The lightweight JSON of `core/persistence.js` (`buildComponentsExport(components, resources, tags, componentGroups, appTitle)` / `parseImportedComponents`) has shape `{ version, components, resources, tags, componentGroups, appTitle }` — a selectable subset of components/resources/tags, but always the full `componentGroups`/`appTitle` (no panel state: `panelState`/`resourcePanelState`/`tagPanelState`/`resourcesSeeded` are never included).

**Export**:
1. `openExportSelectionModal` shows a modal with a file-name field (prefilled with `getFullAppTitle(getAppTitle())` + `.json`) plus the three selection blocks (`ui/elementSelectionModal.js`), instead of a native `prompt()`.
2. On confirm, `ui/editModeToggle.js` filters `getComponents()`/`getResources()`/`getTags()` by the checked ids (those functions' signatures unchanged — they receive already-filtered lists; no orphan-reference validation on the exported selection).
3. `buildComponentsExport(...)` builds the JSON, `downloadJson` triggers the download.

**Import**:
0. Entry point: "Importar" button. Two call sites, same handler (`importComponentsFromFile`, `ui/editModeToggle.js`): `.edit-toolbar` (edit mode) and `#mode-switcher` (play mode) — both built by `createImportControls()` (see `../architecture/005-modes.md`). [gotcha] the flow never calls `setMode`; the mode active when the button was pressed is the mode after import completes/aborts. Post-import repaint is via the `*:changed` events (`loadComponents`/`loadResources`/`loadTags`/`loadGroups`), `renderAll` picks `renderPlayMode`/`renderEditMode`.
1. `parseImportedComponents` reads the file.
2. `openImportSelectionModal` shows the file's elements to choose which to import.
3. On confirm, `openImportConfirmModal` asks for mode (`add`/`overwrite`) and duplicate-id behavior (`overwrite`/`keepBoth`).
4. `ui/editModeToggle.js` calls `proceedWithImport(selectedComponents)` directly — since 00250 there is no `'ficha'` conversion step and no `openImportConversionErrorModal`. `core/importMerge.js` (`mergeImportedGame`) computes the final state:

   | Mode | Existing id | Effect |
   |---|---|---|
   | `overwrite` | — | Starts from empty lists, inserts the selection directly (no conflict possible) |
   | `add` | Not present | Merges the selection with the existing by type (components/resources/tags, each with its own id space) |
   | `add` | Present, `conflictMode: 'overwrite'` | Replaces the existing element |
   | `add` | Present, `conflictMode: 'keepBoth'` | Renames the imported one with a `-imported`/`-imported(n)` suffix (`nextImportedId`, analogous to `nextCloneId` but generic per type) — references of imported components to a renamed resource/tag are rewritten to the new id before merging (`etiquetaIds` is a flat top-level property of the component, like `image`, not a key inside `properties`) |

   Already-existing components are not touched in `add` mode.
5. After the merge: a reference of a freshly imported component to a resource absent from the final state is discarded (field to `null`, tolerated like a deleted resource in use); each id absent from `etiquetaIds` (there may be several per component) is processed separately — a tag with that id is auto-created (once per id even if several components reference it), or it is linked to the existing tag with the same name if there is one. Each case generates a report row (`{ componentId, tipoError, solucion, elemento }`); if there is any, `ui/editModeToggle.js` opens `openImportReportModal(report)` on finishing.

The previous functions `getComponentsWithMissingResources` (`core/resource.js`) and `getComponentsWithMissingDeck` (`core/deck.js`) of the earlier import flow (all-or-nothing with `confirm()`) have been removed for being unused — `mergeImportedGame`'s report replaces them with more detail.

### Default resources (`data/defaultResources.js`, `main.js`)

Since 00250 there is no retroactive backfill: the example resources are seeded only for a fully new session. A save or a seed that already carries data is never topped up, even if its `resourcesSeeded` is not `true`.

| State on load | Action |
|---|---|
| Fully new session (nothing saved and no embedded seed; or `parseState` returned an error and `readSeedState()` found no seed) | `seedDefaultResources()` seeds the 2 entries of `DEFAULT_RESOURCES` (see `004-groups-resources.md`), sets `resourcesSeeded = true` (`markResourcesSeeded()`) |
| Valid save, or a save that failed to restore but there is an embedded seed | `resourcesSeeded` is hydrated from the save/seed as-is; no seeding, no backfill |
| `resourcesSeeded` already `true` | If the user deletes the default resources, they do not reappear on later loads |
