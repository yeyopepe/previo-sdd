# 003 — File and symbol map
**Area**: Architecture

One row per source file. `?` = not read in full during bootstrap; responsibility inferred from imports/callers.

## src/ (bootstrap)

| File | Responsibility |
|---|---|
| `src/main.js` | bootstrap: subscriptions, startup hydration, seed default resources |
| `src/index.html` | shell: `#app-title`, `#edit-toolbar`, `#mode-switcher`, `#content`, `#app-version`, `#initial-state`, `{VERSION}` marker |

## src/data/

| File | Responsibility |
|---|---|
| `src/data/version.js` | `CURRENT_VERSION` single source (format `v{NNNN}`); mutated by build.py |
| `src/data/defaultResources.js` | `DEFAULT_RESOURCES` seeded on first run |

## src/core/ (domain, no DOM)

| File | Responsibility |
|---|---|
| `src/core/eventBus.js` | pub/sub `on`/`off`/`emit` |
| `src/core/state.js` | central store; all mutators + `*:changed` emits; load-time migrations; `sacarCartaDeMazo` cross-mode op |
| `src/core/persistence.js` | localStorage autosave, seed read, import parse, export shape |
| `src/core/component.js` | `createComponent` model + defaults; clone/copy id generation; `syncCopyWithOriginal`; `normalizeComponentEtiquetaIds` |
| `src/core/group.js` | group property record; `getEffectiveGeneralProps` (group props override member props); `deriveMissingGroups` backfill |
| `src/core/tag.js` | tag model; `getComponentsUsingTag` |
| `src/core/resource.js` | resource model (`imagen`/`tipografia`); ext→type map; deep `properties` ref scan; `getComponentsUsingResource` |
| `src/core/deck.js` | pure deck logic: Fisher-Yates shuffle, reveal-zone rect by `disposicion`, `computeSacarCartaDeMazo`, `rectsOverlap` |
| `src/core/dice.js` | pure die logic: face values from `numeroMaximoCaras` or `listaValores`, `tirarDado` |
| `src/core/cardProportions.js` | 11 card proportions; hex/triangle `clip-path`; concentric inner-clip border math; `CARD_DESIGN_WIDTH` (legacy migration only) |
| `src/core/cardFaceElements.js` | ? ordering of card-face elements (`getOrderedFaceElements`) |
| `src/core/textBoxLayout.js` | text-box align/margin → flex layout style |
| `src/core/colorUtils.js` | `hexToRgba`, `shadeColor` (lighten/darken mix) |
| `src/core/textVariables.js` | `{name}` runtime substitution in free-text fields; `{cards_current}` for `mazo` |
| `src/core/markdown.js` | thin wrapper over vendored `marked` |
| `src/core/sanitizeHtml.js` | strip `<script>` + `on*` handlers, neutralize `javascript:` in `href`/`src`; for `documento` component |
| `src/core/textSort.js` | ? `sortByName` accent/case-insensitive (es locale) |
| `src/core/importMerge.js` | pure import merge: add/overwrite, id-conflict keep-both (`-imported` suffix), deep resource-ref remap, tag-name dedupe, broken-ref report |
| `src/core/fichaMigration.js` | ? `migrateFichaComponent` legacy `ficha`→`carta` conversion |
| `src/core/imageConversion.js` | upload image → WebP via canvas `toDataURL` q=0.92; original on failure/non-convertible |
| `src/core/fileExport.js` | `downloadJson` via Blob + anchor click |
| `src/core/appTitle.js` | `DEFAULT_APP_TITLE`, `formatVersion`, `getFullAppTitle` |
| `src/core/interactions.js` | per-type click interaction registry (`dado:lanzar`, `carta:voltear`, `mazo:sacarCarta`); `isInteractionActive` |
| `src/core/persistence.js` | (see above) |
| `src/core/styleClipboard.js` | ? copy/paste component appearance between components |
| `src/core/markdown.js` | (see above) |

## src/modes/

| File | Responsibility |
|---|---|
| `src/modes/edit/editMode.js` | edit mode: infinite table + 3 floating panels; multi-select, block move, bulk delete, clone/copy, group/ungroup, tag assignment, resource upload flows (single/multi/folder), drag-cards-onto-deck |
| `src/modes/play/playMode.js` | play mode: components rendered directly; dice roll / card flip / deck draw / shuffle / view-contents / insert-card; per-component right-click menu, lock/unlock, z-lift on move |

## src/ui/ (DOM; not read in full during bootstrap)

| File | Responsibility |
|---|---|
| `src/ui/table.js` | pan/zoom infinite table; module-level camera; `fitToBounds` |
| `src/ui/componentRenderer.js` | renders components onto table world; knows component model; hex/triangle grid drawing; tooltip sanitizer whitelist; `getComponentsBounds`, `formatComponentIdentifier` |
| `src/ui/componentModal.js` | component property editor modal; `createDefaultComponent` |
| `src/ui/editModeToggle.js` | mode-switch buttons, edit toolbar; export menu; import flow orchestration; fit button |
| `src/ui/globalShortcuts.js` | ESC/Enter/Delete/Arrows → existing modal buttons, or edit-mode selection delete/move; knows only modal DOM contract |
| `src/ui/componentList.js` | components panel table (sort/filter/search per column) |
| `src/ui/resourceList.js` / `resourceModal.js` | resources panel + editor |
| `src/ui/tagList.js` / `tagModal.js` / `tagDeleteConfirmModal.js` | tags panel + editor + delete confirm |
| `src/ui/groupModal.js` | group property editor |
| `src/ui/contextMenu.js` | shared context-menu builder (general + specific + interaction items) |
| `src/ui/visualEditorModal.js` | card / custom-board visual editor (image layers, shapes, text boxes) |
| `src/ui/table.js` | (see above) |
| `src/ui/toast.js` / `errorModal.js` / `progressModal.js` | transient feedback: toast, error modal, blocking progress modal (`runWithProgressModal`) |
| `src/ui/fontFaceRegistry.js` | `@font-face` registration from resources (`syncFontFaces`, `fontFamilyFor`) |
| `src/ui/diceResultModal.js` / `diceFontModal.js` | enlarged dice result; dice result font picker |
| `src/ui/mazoContentModal.js` / `insertIntoMazoModal.js` | deck contents viewer; insert-card-into-deck picker |
| `src/ui/*Modal.js` (board/card/import/export/batch/style-clipboard/etc.) | one modal per specific configuration or confirmation flow |
| `src/ui/table.js`, `resizeHandle.js`, `rotationSlider.js` | reusable interaction widgets |
| `src/ui/componentTypeModal.js` / `componentCopiesModal.js` / `componentTitleModal.js` | add-component type picker; copies manager; title editor |
| `src/ui/imageAdjustModal.js` | image fit/crop adjust (`applyImageAdjustStyle`) |
| `src/ui/columnHeaderMenu.js` / `tableColumnMenu.js` / `tableColumnResize.js` | table column header menu + resize |
| `src/ui/helpIcon.js` / `editModeToggle.js` | inline help icon; (toggle: see above) |

## src/scripts/

| File | Responsibility |
|---|---|
| `src/scripts/build.py` | deliverable build (see `arch.build.pipeline`) |
| `src/scripts/obfuscate_bundle.js` + `vendor/javascript-obfuscator.browser.js` | ? optional bundle obfuscation |
