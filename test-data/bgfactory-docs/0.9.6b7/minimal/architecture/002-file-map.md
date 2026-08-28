# 002 — File & symbol map

**Area**: Architecture

Minimal-level map: one row per source file, general responsibility only. Exact
signatures live in the code — cite `file:symbol`.

## `src/`

| File | Responsibility |
|---|---|
| `main.js` | Bootstrap. Hydrate state (saved → embedded seed → defaults), subscribe every `<domain>:changed` to `renderAll` + `persistState`, init global shortcuts, seed default resources once. |

## `src/core/` — domain & infrastructure

| File | Responsibility |
|---|---|
| `eventBus.js` | Pub/sub. `on(name, handler) -> off`, `off`, `emit(name, payload)`. Decouples layers. |
| `state.js` | Central store: `state {mode, components, resources, tags, groups}` + panel-state singletons + appTitle + `resourcesSeeded`. Exported getters/setters mutate in place then `emit`. Owns `order` (z-index) compaction, copy-sync propagation on `replaceComponent`, auto-dissolve of groups left with ≤1 member. |
| `persistence.js` | Autosave to `localStorage` (`STORAGE_KEY="bgfactory:state"`), load + validate (`version`/`components` guard), read embedded seed, build export payload, parse imported components. Back-compat key aliasing. |
| `component.js` | Generic component model. `createComponent(...)` (id `crypto.randomUUID()`, free `type`, `properties` k/v, position/size, lock/tooltip/title/depth fields, `copyOf`/`sincronizado`, `groupId`, `etiquetaIds`). `updateComponent`, `cloneComponent`, `createCopy`, `syncCopyWithOriginal`, `renameCopyId`, `nextGroupId`, `normalizeComponentEtiquetaIds`. |
| `deck.js` | Pure "Mazo" logic. `shuffleCartaIds` (Fisher-Yates + `Math.random`), `computeSacarCartaDeMazo`, `getCartaIdsEnAlgunMazo`, `rectsOverlap`. No cross-layer deps. |
| `dice.js` | Pure "Dado" logic. Parse/validate custom value list, `getPosibleValores`, `tirarDado`. |
| `group.js` | Group property record. `createGroup({id,...})` (id set by caller, not auto), `updateGroup`, `getEffectiveGeneralProps` (group props override member props), `deriveMissingGroups`, `getGroupsUsingTag`. |
| `tag.js` | Minimal tag model (cross-type element grouping). `createTag`, `updateTag`, `isTagNameTaken`, `getComponentsUsingTag`. |
| `resource.js` | Gallery resource model (image / font), file bytes as data URI. `RESOURCE_TYPES`, `createResource`, `resourceTypeForFileName`, `findResourceByName`, `getComponentsUsingResource`. |
| `interactions.js` | Central registry: which click interactions each component type has in play mode. `TYPE_INTERACTIONS` (`dado→lanzar`, `carta→voltear`, `mazo→sacarCarta`), `getInteractionsForType`, `isInteractionActive`. |
| `importMerge.js` | Merge an imported selection (components/resources/tags) into current state per mode (add/overwrite) and duplicate-id behaviour (overwrite/keep-both). Plain data in/out, no DOM, no `state.js`. |
| `fileExport.js` | `downloadJson(filename, data)` via Blob + object URL. |
| `persistence.js` export helpers | `buildComponentsExport`, `parseImportedComponents` (used by `editModeToggle.js`). |
| `styleClipboard.js` | In-memory only "copy/paste card style" clipboard. Never persisted/exported. Single slot, no history. |
| `textVariables.js` | Runtime `{name}` substitution in free-text fields (`tooltipTexto`, `tituloTexto`). `getAvailableVariables` (e.g. `cards_current` for `mazo`), `resolveTextVariables`. Designed to extend by adding variables only. |
| `sanitizeHtml.js` | Strip `<script>`, inline handlers, `javascript:` URLs from user HTML before DOM insertion. Used by document-viewer component. |
| `markdown.js` | `markdownToHtml(text)` — thin wrapper over `vendor/marked.js`. Output still routed through `sanitizeHtml`. |
| `colorUtils.js` | `hexToRgba(hex, transparenciaPercent)`, `shadeColor`. Card TextBox/Shape backgrounds. |
| `cardProportions.js` | Static catalog `CARD_PROPORTIONS` (poker/tarot/square/circular/hex/triangular ratios + shape). `CARD_DESIGN_WIDTH`. |
| `cardFaceElements.js` | Combined stacking order of shapes + textBoxes on a card face. Optional `orden` field; in-memory fallback ordering when absent. |
| `textBoxLayout.js` | Translate a TextBox align/margins to flex layout styles. Pure data. |
| `textSort.js` | `sortByName` (locale `es`, accent-insensitive), `compareValues` (numeric-if-both-numeric) for panel column sort. |
| `imageConversion.js` | `convertImageToWebP(file, dataUrl)` on gallery upload (quality 0.92). Falls back to original on failure. |
| `fichaMigration.js` | Migrate removed `ficha` type → `carta`. Pure, never throws; returns valid card `properties` + error list. |
| `appTitle.js` | Editable free title + non-editable version suffix. `DEFAULT_APP_TITLE="BG Factory"`, `formatVersion`, `getFullAppTitle`. |

## `src/modes/`

| File | Responsibility |
|---|---|
| `edit/editMode.js` | Edit mode: infinite table with selectable/editable components + floating panels (components / resources / tags) with list, edit, delete, bulk delete, group, batch upload. |
| `play/playMode.js` | Play mode: infinite table rendering components directly; context-menu selection (transient, session-only); click interactions dispatched via `CLICK_INTERACTION_KEY_BY_TYPE` + `interactions.js`. |

## `src/ui/` — DOM widgets & modals

| File / group | Responsibility |
|---|---|
| `table.js` | Domain-agnostic infinite table: pan/zoom, module-level camera surviving remounts. Not persisted. |
| `componentRenderer.js` | Render components onto the table world element. Knows the component model. Dice blink/roll, markdown+sanitize for document viewer, image-adjust styles, `getComponentsBounds`, `formatComponentIdentifier`. |
| `componentModal.js` | Create/edit component, tabbed. Type-specific tab content for `texto`/`tableroSimple`/`tableroPersonalizado`/`dado`/`documento`/`carta`/`mazo`. |
| `componentTypeModal.js` | Pre-create type picker. `COMPONENT_TYPES` catalog, `getComponentTypeLabel`. |
| `visualEditorModal.js` | Large visual face editor (background image, shapes, text boxes). Card (2 faces, configurable proportion, simple border) and custom board (1 face, free resize, bevel border). |
| `componentList.js` / `resourceList.js` / `tagList.js` | Floating, collapsible edit-mode panels: list table with free-text filter and column resize. Components list = Id/Type/Actions with row selection. |
| `contextMenu.js` | Generic cursor-anchored menu (no overlay, closes on ESC or outside click). |
| `editModeToggle.js` | Enter/exit edit mode: entry button in play mode, own toolbar in edit mode; wires save/export/import. |
| `globalShortcuts.js` | Global keys (ESC/ENTER/DEL/arrows) as direct equivalents of existing buttons. Knows only the modal DOM pattern (`.modal-overlay > .modal > .modal__footer` with `.btn-cancel`/`.btn-accept`/`.btn-eliminar`); never imports `modes/*`. |
| `fontFaceRegistry.js` | Sync one `<style>` with one `@font-face` per font resource so its dataUrl is usable as `font-family`. `syncFontFaces`, `fontFamilyFor`. |
| `toast.js` | Non-blocking transient notice (`showToast`, 3000ms). |
| `helpIcon.js` | Reusable inline help icon (`createHelpIcon`). |
| `resizeHandle.js` / `tableColumnResize.js` / `tableColumnMenu.js` / `columnHeaderMenu.js` / `rotationSlider.js` | Reusable interaction primitives (panel resize, column resize/menu, rotation slider). |
| `*Modal.js` (board color/image/pattern, card background/shape/textbox, dice font/result, group, copy component, component copies/title/type, import confirm/selection/report/conversion-error, export selection, element selection, style-clipboard selection/error, resource replace confirm, tag delete confirm, bulk delete confirm, mazo content, insert into mazo, image adjust, batch upload summary, progress, error) | One modal each, per a specific edit/play action. Follow the shared overlay + `.modal` + `.modal__footer` pattern. |

## `src/data/`

| File | Responsibility |
|---|---|
| `defaultResources.js` | `DEFAULT_RESOURCES` — sample gallery resources seeded on first run. |
| `version.js` | `CURRENT_VERSION` — persistence guard + deliverable filename + displayed version. |

## `src/scripts/`

| File | Responsibility |
|---|---|
| `build.py` | Deliverable generator (see 001-overview "Build"). |
| `obfuscate_bundle.js` | Optional bundle obfuscation step. |

<Expanded by pv-do over time.>
