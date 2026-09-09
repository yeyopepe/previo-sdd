# 004 — Class naming (BEM) and JS component patterns

**Area**: Layout & components

## Style stack

- Plain CSS, a single file: `src/styles/main.css`. No preprocessor or CSS-in-JS.
- DOM built with vanilla JS (`document.createElement`, `className`, `classList`). No component framework.
- Files in `src/ui/*.js` = the "components".
- Do not add UI dependencies (React, Tailwind, etc.) without agreeing it first. App = vanilla JS + plain CSS.

## Class naming — BEM

Convention: `block__element--modifier`.

- Block in kebab-case: `.component-list`, `.modal`, `.infinite-table`, `.edit-mode-panel`, `.help-icon`, `.board`, `.board-image-modal`, `.component-type-modal`. Names in English, unrelated to the `'tableroSimple'` component-type identifier — they are not renamed when that type is renamed.
- Element with a double underscore: `.component-list__item`, `.modal__header`, `.modal__tabs`, `.modal__field`, `.infinite-table__world`, `.help-icon__tooltip`.
- Modifier with a double dash: `.text-box--selectable`, `.text-box--movable`, `.modal__field--checkbox`.
- Transient states (not BEM, simple classes added/removed by JS): `.grabbing`, `.active`, `.lifted`, `.drop-target`.
  - No block prefix, used as-is.
  - Always with `classList.add/remove`, never replacing the whole `className`.
  - Exception: `.carta--flip-feedback` does carry the `carta--` prefix despite being transient — it describes a state exclusive to that block, not a generic one like `.lifted`.
  - `.is-copy`: the same "no block prefix" criterion even though it is not transient (kept while `component.copyOf` is not `null`). Cross-cutting over the 7 component types. Added by `ui/componentRenderer.js` alongside the type's own `--selectable` class. Used by `main.css` to paint the selection outline and `.component-id-label` red (see `003-modales-menus.md`, Component identifier label).
  - `.is-group-passenger`: same criterion as `.is-copy` (no block prefix, cross-cutting over the 7 types, added by `ui/componentRenderer.js` alongside `--selectable`/`--selected`). Applied when the component belongs to a group (`groupId` non-null, see `../architecture/005-modes.md`, "Groups in edit mode") and is selected as a passenger — dragged into the selection by belonging to the group, without being the direct target of the click. `main.css` paints it gray (`var(--text-muted)`) instead of the usual blue/red, with no `:hover` variant (it only applies alongside `--selected`). If it coincides with `.is-copy` on the same element, `.is-group-passenger` wins (declared later in the cascade).
- Historical exception (do not follow BEM): `.btn-cancel`, `.btn-accept`, `.btn-eliminar`.
  - New standalone button variants (not tied to an existing block): use the `.btn-<intent>` pattern.
  - `.btn-duplicate`: same look as `.btn-cancel` (identical background/color/hover/disabled). Used when a modal footer needs a non-destructive/non-primary action distinct from "Cancelar" — lets `ui/globalShortcuts.js` locate the real "Cancelar" unambiguously on ESC (`querySelector('.modal__footer .btn-cancel')`).
  - `.btn-sacar` (`ui/mazoContentModal.js`): a small per-row button of `.mazo-contenido__item`. Background `var(--bg-subtle)`, hover `var(--accent-blue)`/light text — the same criterion as `.context-menu__item:hover`.
- A button that belongs to an already-existing block (e.g. a `.component-list` row): does not use the `.btn-*` exception. Normal BEM with a modifier: `.component-list__action-btn--danger`.
- IDs (`#mode-switcher`, `#content`, `#app-version`, `#edit-toolbar`): reserved for unique layout containers in `index.html`. Never for reusable components.
  - A unique layout container may still hold internal BEM structure under a block named after it: `#app-version` contains `.app-version__name` + `.app-version__repo` (00243). The block name (`app-version`) matches the ID; the ID stays the styling/JS hook for the container, the `__element` classes for its parts.
  - `#mode-switcher` also follows this: its header-row buttons use `.mode-switcher__mode-btn` / `.mode-switcher__fit-btn` / `.mode-switcher__settings-btn` (`__element` classes under the ID-matching block, 00244; see `002-componentes-layout.md`, "Header control row").
- `.settings-modal__version` (`ui/settingsModal.js`, 00244): read-only version value inside the settings panel. `.modal__separator` (00244): thin body-block divider inside a modal — both plain BEM.

## Component patterns (JS)

Each "component" = a function that creates and returns an `HTMLElement` via `document.createElement`, assigns `className` once on creation, uses `classList.add/remove/toggle` only for later dynamic states.

```js
const modal = document.createElement('div');
modal.className = 'modal';
```

See the full form in `src/ui/componentModal.js`.

- One file per component in `src/ui/`, camelCase (`componentList.js`, `componentModal.js`, `table.js`).
- UI states (active tab, dragging, selectable): always a class, never an inline style.
- Do not use `style.xxx =` from JS for anything expressible as a CSS class/token.
  - Legitimate exception: dynamically computed transforms (e.g. pan/zoom of `.infinite-table__world`) — a purely numeric value, meaningless as a class.

**Color field + associated thickness, same row.** When a modal has conceptually linked color and thickness (border/stroke), they go in the same row, not stacked.

- Pattern: `componentModal.js` (board border), `ui/visualEditorModal.js` (border of each face of a card).
- Structure: outer `div.modal__field` → inner `div` (`style.display='flex'; style.gap='0.5rem'`) → two sub-`div` with `style.flex='1'` (color first, thickness second).
- The only admitted exception to "no `style.xxx=` from JS": one-off layout for that pair of fields, not a state/value reusable as a class.
- **Caution in a variable/bounded-width container**: the `flex:1` fields contain an `<input>` with `width:100%`. If the container has no explicit width anywhere in the ancestor chain (e.g. a column sized by its content, like each face of `ui/visualEditorModal.js`), the `100%` does not resolve and the browser falls back to the `<input>`'s intrinsic rendering width (the browser's default text-input size, unrelated to the surrounding layout). Fix: the row's container sets its own explicit width — `ui/visualEditorModal.js` (`renderFace`) sets `faceCol.style.width` to the same `canvasWidth` computed for that face's card canvas.
- **Extension to N related numeric fields**: same row pattern (`display:flex; gap:0.5rem`, one sub-`div` per `flex:1` field) when there are more than 2 related numeric fields. Example: `ui/cardTextBoxModal.js`, a row of 4 "Arriba"/"Derecha"/"Abajo"/"Izquierda" fields (`TextBox` margins, `<input type="number" min="0">` each) — a single row of 4, not two rows of 2.

## What NOT to do

- Do not introduce a second color-token system (Tailwind, another palette) — extend `:root` in `main.css`.
- Do not mix inline `style="color:#..."` for colors in the token catalog (`001-tokens-visual.md`, Design tokens).
- Do not create single-use classes without BEM unless they fit the `.btn-*` exception.
- Do not add flashy gradients or complex animations/transitions (`@keyframes`, narrative animations).
  - Gradient exceptions (closed list, each explicitly agreed): the subtle header gradient (`h1`); the startup splash window background `.splash-window` (`linear-gradient(135deg, #e3effb 0%, #eef1fb 45%, #f7ecf6 100%)`, change 00245, validated in mockups — `003-modales-menus.md`, "Startup splash / welcome screen"). No new gradient without the same explicit agreement.
  - Animation: exactly two `@keyframes` in the project, both bounded functional animations (not decorative/narrative): `progress-modal-spin` (in-progress-operation spinner, `003-modales-menus.md`) and `splash-progress-fill` (startup splash 3s time-indicator bar, 00246/00247, `001-tokens-visual.md` Transitions + `003-modales-menus.md`). No third `@keyframes` without an explicit decision.
  - Shadows and radii are allowed: they always follow the elevation system (`001-tokens-visual.md`, Elevation) and the radius scale (`001-tokens-visual.md`, Borders and corners), never an ad-hoc per-component value.

Bevel/depth, rounded-corner and clip-path exceptions for specific component types (`'tableroSimple'`/`'tableroPersonalizado'`/`'dado'` bevel, `'carta'`/`'mazo'` corners and hexagonal/triangular clips, drop-target and flip-feedback states) are cataloged per type in `003-modales-menus.md`; elevation/extrusion detail (including the die roll's flicker/shake and the "Lift" drag effect) lives in `001-tokens-visual.md`.
