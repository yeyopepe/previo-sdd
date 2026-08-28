# 002 — Layout: shell, panels, modals, menus
**Area**: Layout

Page shell, floating panels, modal structure, menu positioning. Source: [src/styles/main.css](../../../src/styles/main.css), [src/index.html](../../../src/index.html).

## Page shell

```
body: flex column, height 100vh
  h1#app-title      height 3.5rem, flex-shrink 0, linear-gradient(#3a3a3a → #333), z 100
  #edit-toolbar     (edit mode only) full width, bg #333, justify flex-end, z 99
  #mode-switcher     position fixed, top .5rem right 1rem, z 101
  #content          flex 1 1 auto, min-height 0   ← the infinite table lives here
  footer#app-version position fixed, bottom-right, z 10
```

- Single column, no responsive breakpoints. Layout assumes a desktop viewport; no media queries for width in the app chrome (only `clamp()` on `.component-editor-modal` width).
- `.infinite-table`: `100% × 100%`, `overflow: hidden`, `cursor: grab` (→ `grabbing` while panning), dotted radial-gradient grid `background-size: 32px 32px`. Inner `.infinite-table__world` is `position: absolute`, `transform-origin: 0 0`, pan/zoom via `transform`.

## Floating panels (edit mode)

Three panels, structurally identical: `.component-panel`, `.resource-panel`, `.tag-panel`.

```
.{x}-panel-container   position absolute, width 440px, default right: 1rem, stacked tops 1rem / 28rem / 55rem
.{x}-panel            bg var(--bg-card), radius --radius-lg, overflow hidden, box-shadow --shadow-1
  __header            bg #333, text light, padding .5rem 1rem, cursor grab (→ grabbing), user-select none
  __filter            (component + resource + tag) text input + clear button, border-bottom
  __body              height 320px, overflow auto (x and y)
  __footer            border-top, one full-width primary button
```

- Drag: `mousedown` on `__header`. Position persisted (`PanelState.position`), overrides the default `right`/`top` with explicit `left`/`top`.
- Resize: `.resize-handle` bottom-right corner; `.resize-handle--tl` top-left variant. Size persisted (`PanelState.width`/`height`).
- Collapse: header button toggles `PanelState.collapsed` (body hidden).
- Z-order: transient, `editMode.js#applyPanelStackOrder`; `mousedown` anywhere on a panel (capture phase) brings it to front (`bringPanelToFront`). Reset on reload.
- [gotcha] `.tag-panel` has the filter box but **no** add-menu — a single `+ Añadir etiqueta` footer button, not the dropdown `.resource-add` menu the resource panel uses.

## Modal structure

DOM contract (relied on by [globalShortcuts.js](../../../src/ui/globalShortcuts.js)):

```
.modal-overlay              position fixed, inset 0, bg rgba(0,0,0,0.5), flex center, z 1000
  .modal                    bg white, radius --radius-lg, box-shadow --shadow-2,
                            max-width 500px, width 90%, max-height 80vh, flex column
    .modal__header          padding 1rem, border-bottom
    [.modal__tabs]          optional; .modal__tab, active tab: white bg + border-bottom var(--accent-blue)
    .modal__content         flex 1, overflow-y auto, padding 1.5rem
    .modal__footer          padding 1rem, border-top, flex, justify flex-end, gap .5rem
      [.btn-eliminar]       margin-right auto (pushed to the left)
      .btn-cancel / .btn-accept
```

Width variants (own `max-width`/`width`, documented exceptions to the 500px default):

| Class | Width rule | Use |
|---|---|---|
| `.component-editor-modal` | `clamp(400px, 50vw, min(600px, 65vw))` | recalculates on resize, no JS |
| `.card-editor-modal` | `fit-content`, `max-width min(1500px, 95vw)` | variable-width content |
| `.card-editor-modal--maximized` | `97vw`, unset `max-height` | maximize toggle |
| `.image-adjust-modal--large` | `fit-content`, `max-width min(1500px,95vw)` | |
| `.resource-modal--image` | `fit-content`, `max-width min(800px,95vw)` | |
| `.element-selection-modal` | `max-width 640px` | export/import checklist (3 groups) |
| `.import-report-modal`, `.board-image-modal` | `max-width 640px` / `min(900px,90vw)` | |

- `.progress-modal`: own structure — no header/footer/buttons, no manual close. Spinner (`--accent-blue` ring) + text, centered. Used via `runWithProgressModal(text, fn)` to wrap blocking work (import, bulk card-into-deck).
- `.modal__section`: `<fieldset>` with `--border-neutral` border; `<legend class="modal__section-title">` is the only element using `--section-accent` (uppercase, `letter-spacing 0.02em`). `--toggle` variant = legend carries a checkbox; `--disabled` dims and disables its children (`opacity .5; pointer-events none`).

## Menus (dropdown / context / column-header)

Shared visual language — `.resource-add__menu`, `.context-menu`, `.column-header-menu`, `.export-menu` (dark variant):

```
bg var(--accent-blue-light)  (or var(--bg-toolbar) for .export-menu, on the dark toolbar)
border 1px rgba(44,125,216,0.25)
border-radius --radius-sm
box-shadow --shadow-2
overflow hidden
item: padding .5rem .75rem, border-bottom rgba(44,125,216,0.25) between items
item:hover: bg var(--accent-blue), color var(--text-light)
```

- `.context-menu` / `.column-header-menu`: `position: fixed` on `document.body`, `z-index 1050`. [motivación] fixed on body (not `absolute` under the trigger) because triggers live inside `overflow` panels that would clip an absolutely-positioned child.
- `.context-menu__item--disabled` / `select:disabled`: `cursor: not-allowed`, `opacity .6`, muted color, no hover response.
- `.column-header-menu__item--active` (current sort): stays `--accent-blue` bg even without hover, so the applied sort is visible.
- Non-clickable rows inside a menu (`__select-row`, `__description`, `__info-row`): `cursor: default`.

## Card / visual editor canvas

- `.card-editor-modal__canvas` / `.card-editor-modal__face`: white bg, `--border-neutral` border, `overflow hidden`. Two faces side by side (`__faces` flex wrap).
- `.card-editor-modal__textbox` / `__shape`: `cursor: move`, `:hover` → `1px dashed var(--accent-blue)`, `--selected` → `2px solid var(--accent-blue)` + `outline-offset 2px`. `.resize-handle` in the corner.
- `.image-adjust-modal__mask`: `cursor: move`; `--active` → `2px solid var(--accent-blue)` + `0 0 0 3px rgba(44,125,216,.25)`. Checkerboard backdrop `repeating-conic-gradient(#e8e8e8 0 25%, #f5f5f5 0 50%) 50% / 20px 20px`.
- `.rotation-slider`: `accent-color: var(--accent-blue)` on the range input, tick marks magnetized every 90°.
