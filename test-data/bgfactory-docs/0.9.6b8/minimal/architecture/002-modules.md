# 002 — Module responsibility map

**Area**: Architecture

Minimal-level map: one row per module, its responsibility, and whether it is pure (no DOM, no cross-layer import). Exact signatures live in the code — see referenced `file:symbol`.

## `src/data/`

| Module | Responsibility |
|---|---|
| `data/version.js` | `CURRENT_VERSION` string constant (`'v00230'`). Sole source of the app version. |
| `data/defaultResources.js` | `DEFAULT_RESOURCES` array. Seeded once into a brand-new session. Pure. |

## `src/core/` — central state / persistence / bus

| Module | Responsibility | Pure |
|---|---|---|
| `core/eventBus.js` | Synchronous pub/sub (`on`/`off`/`emit`). `Map<string, Set<handler>>`. | yes |
| `core/state.js` | The single `state` object + panel-state vars. All mutations + `emit`. Hosts `sacarCartaDeMazo` and the 7 load-time migrations. | no (owns state) |
| `core/persistence.js` | `saveState`/`loadState` (localStorage), `readSeedState` (embedded JSON), `parseImportedComponents`, `buildComponentsExport`. Legacy key aliases. | reads DOM seed el |
| `core/component.js` | Generic component model: `createComponent`, `updateComponent`, clone/copy id generation (`nextCloneId`/`nextCopyId`/`nextGroupId`), linked-copy sync (`syncCopyWithOriginal`, `NON_SYNCED_PROPERTY_KEYS`). | yes |
| `core/resource.js` | Gallery-resource model (image / font), `RESOURCE_TYPES`, extension→type map, "resource in use by component" query. | yes |
| `core/tag.js` | Tag model (`createTag`), name-taken check, "components using tag" query. | yes |
| `core/group.js` | Group-property registry (`createGroup`, `updateGroup`, `getEffectiveGeneralProps`, `deriveMissingGroups`). `id` always caller-assigned. | yes |
| `core/deck.js` | "Mazo" (deck) pure logic: shuffle (Fisher-Yates + `Math.random`), `computeSacarCartaDeMazo`, `getCartaIdsEnAlgunMazo`, `rectsOverlap`. | yes |
| `core/dice.js` | "Dado" pure logic: parse custom value list, validate, roll, `getPosibleValores`. | yes |
| `core/interactions.js` | `TYPE_INTERACTIONS` registry — which per-click interactions each component type has; `isInteractionActive`. | yes |
| `core/cardProportions.js` | `CARD_PROPORTIONS` catalog (poker/tarot/square/hex/…), `CARD_DESIGN_WIDTH`. | yes |
| `core/cardFaceElements.js` | Combined stacking order of shapes + text boxes on a card face. | yes |
| `core/textBoxLayout.js` | Card text-box alignment/margins → flex layout styles. | yes |
| `core/colorUtils.js` | `hexToRgba(hex, transparenciaPercent)`. | yes |
| `core/textSort.js` | `sortByName` — locale/accent-insensitive sort by `.name`. Returns a new array. | yes |
| `core/textVariables.js` | `{name}` text-variable substitution in free-text fields (`tooltipTexto`, `tituloTexto`). Extensible via `getAvailableVariables`. | yes |
| `core/markdown.js` | Thin wrapper over `vendor/marked.js` (`markdownToHtml`). Output still goes through `sanitizeHtml`. | yes |
| `core/sanitizeHtml.js` | `sanitizeHtml(html)` — strips `<script>`, `on*` attrs, `javascript:` in `href`/`src`. [gotcha] denylist, not allowlist. | yes |
| `core/imageConversion.js` | `convertImageToWebP` (canvas). Applied on gallery upload. | yes (canvas) |
| `core/fileExport.js` | `downloadJson(filename, data)` — Blob + anchor click. | no (DOM) |
| `core/importMerge.js` | Merge an imported selection into current state per mode (add/overwrite) and duplicate-id behavior. Plain data in/out. | yes |
| `core/fichaMigration.js` | Extinct `'ficha'` type → `'carta'`. Never throws. | yes |
| `core/appTitle.js` | `DEFAULT_APP_TITLE`, `getFullAppTitle`, `formatVersion`. | yes |
| `core/styleClipboard.js` | In-memory only "copy/paste card style" clipboard. Never persisted. Holds one style. | yes (module state) |

## `src/ui/` — DOM

Grouped by role. All render to / manipulate the DOM.

### Generic reusable widgets (domain-agnostic)

| Module | Responsibility |
|---|---|
| `ui/table.js` | Infinite table with pan/zoom. Recreated on every repaint; camera kept in module scope. Knows nothing about components. |
| `ui/contextMenu.js` | Generic cursor-anchored context menu (module singleton, no overlay). |
| `ui/columnHeaderMenu.js` | Column sort/filter dropdown (module singleton). Sibling of `contextMenu.js`. |
| `ui/toast.js` | Non-blocking 3s toast. |
| `ui/errorModal.js` | App-wide error modal. All errors go through `showErrorModal`. |
| `ui/progressModal.js` | "Operation in progress" modal — no manual close, resolves when `work` finishes. |
| `ui/helpIcon.js` | Reusable "?" icon opening a text/HTML modal. |
| `ui/resizeHandle.js` | Reusable corner resize handle (`attachResizeHandle`, axis `x`/`y`/both). |
| `ui/rotationSlider.js` | Reusable −360°..360° rotation slider, magnetized at 90° multiples. |
| `ui/elementSelectionModal.js` | Three-block grouped selection list (Components/Resources/Tags), each with "select all block". |
| `ui/fontFaceRegistry.js` | Keeps one `<style>` with an `@font-face` per font resource. `syncFontFaces`. |

### Table column behavior

| Module | Responsibility |
|---|---|
| `ui/tableColumnMenu.js` | Per-column sort/filter, opens `columnHeaderMenu.js`. Used by the 3 edit-mode floating panels. |
| `ui/tableColumnResize.js` | Manual column-width drag, reuses `resizeHandle.js` (axis `x`) on `<th>`. |
| `ui/tableColumnMenu.js` / `ui/columnHeaderMenu.js` | (see above) |

### Edit-mode floating panels

| Module | Responsibility |
|---|---|
| `ui/componentList.js` | Collapsible floating panel — component table (Id, Type, Actions), row selection. |
| `ui/resourceList.js` | Same for resources (images + fonts). |
| `ui/tagList.js` | Same for tags (no Type column, no clone). |
| `ui/appTitle.js` | Header title: editable free text in edit mode + non-editable version. |
| `ui/editModeToggle.js` | Enter/leave edit mode: entry button (play), own toolbar + exit button (edit); import/export wiring. |
| `ui/globalShortcuts.js` | Global keys (ESC/ENTER/DEL/arrows) — direct equivalents of existing buttons; knows only the modal DOM pattern. |
| `ui/editModeToggle.js` | (see above) |

### Component rendering

| Module | Responsibility |
|---|---|
| `ui/componentRenderer.js` | Renders game components onto the infinite table's world element. Knows the component model. `formatComponentIdentifier`. |
| `ui/resizeHandle.js` | (reused here) |

### Modals — one file per dialog

`ui/*Modal.js` (≈35 files). Each opens one dialog for a specific edit/config task. Non-exhaustive grouping:

| Group | Modules |
|---|---|
| Component lifecycle | `componentModal`, `componentTypeModal`, `componentTitleModal`, `copyComponentModal`, `componentCopiesModal`, `componentRenderer` (render, not modal) |
| Card design | `visualEditorModal`, `cardShapeModal`, `cardTextBoxModal`, `cardBackgroundColorModal`, `imageAdjustModal` |
| Board design | `boardColorModal`, `boardImageModal`, `boardPatternModal` |
| Dice | `diceFontModal`, `diceResultModal` |
| Deck ("mazo") | `mazoContentModal`, `insertIntoMazoModal` |
| Groups / tags | `groupModal`, `tagModal`, `tagDeleteConfirmModal` |
| Resources | `resourceModal`, `resourceReplaceConfirmModal`, `batchUploadSummaryModal`, `imageAdjustModal` |
| Import / export | `exportSelectionModal`, `importSelectionModal`, `importConfirmModal`, `importReportModal`, `importConversionErrorModal` |
| Style clipboard | `styleClipboardSelectionModal`, `styleClipboardErrorModal` |
| Confirm / error | `bulkDeleteConfirmModal`, `errorModal`, `progressModal` |

## `src/modes/`

| Module | Responsibility |
|---|---|
| `modes/edit/editMode.js` | Edit screen: infinite table with selectable/editable components + the 3 floating panels + edit toolbar. ~924 lines — the composition hub of edit mode. |
| `modes/play/playMode.js` | Play screen: components rendered directly on the infinite table; per-type click interactions (`CLICK_INTERACTION_KEY_BY_TYPE`), context-menu selection (single transient `selectedComponentId`). |

## `src/main.js`

Bootstrap. Reads DOM anchors (`#mode-switcher`, `#edit-toolbar`, `#content`, `#app-title`, `#app-version`), subscribes `renderAll` + `persistState` to every `*:changed` event, initializes global shortcuts, hydrates state (load → seed → default), calls `syncFontFaces`.
