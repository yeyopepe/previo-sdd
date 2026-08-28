# 003 — Reusable components and patterns
**Area**: Components

Reusable UI patterns other screens must follow. Source: [src/styles/main.css](../../../src/styles/main.css), `src/ui/*.js`.

## Buttons

| Class | Bg | Text | Notes |
|---|---|---|---|
| `.btn-accept` | `--accent-blue` | `--text-light` | primary. `:hover:not(:disabled)` → `opacity .9`, `translateY(-1px)`, `0 3px 8px rgba(44,125,216,.35)`. `:disabled` → `opacity .5`, `cursor not-allowed` |
| `.btn-cancel`, `.btn-duplicate` | `--bg-subtle` | `--text-primary` | secondary. `:hover` → `--bg-hover` |
| `.btn-eliminar` | `--error` | `--text-light` | destructive. `margin-right: auto` in a footer (left-aligned). `:hover` → lift + `0 3px 8px rgba(211,47,47,.3)` |
| `.btn-sacar` | `--bg-subtle` → `--accent-blue` on hover | | small standalone action button in the deck-content list |

- [gotcha] `.btn-cancel / .btn-accept / .btn-eliminar / .btn-duplicate / .btn-sacar` are **standalone class names with no BEM block** — the documented exception to the naming rule (see [005](005-writing-and-naming-conventions.md)). Padding `0.5rem 1.5rem` (footer buttons) or smaller for inline. Shared `transition: background, opacity, transform, box-shadow var(--transition-fast)`.
- Panel-footer / resource-add buttons: full-width, `--accent-blue` bg, `:hover` → `opacity .9` (no lift).

## Option groups (single-select)

Convention for "pick exactly one": the selected option gets `background: var(--accent-blue); color: var(--text-light)` — same treatment as `.modal__tab.active` and `.column-header-menu__item--active`.

| Class | Shape |
|---|---|
| `.modal__tab` | text tab, active adds `border-bottom: 2px solid var(--accent-blue)` + white bg |
| `.align-group__btn` | 32×32 icon-only square, `.active` → accent bg |
| `.dice-font-modal__item--selected`, `.dice-font-modal__item` | list row, selected adds `border-color var(--accent-blue)` + `outline: 2px solid var(--accent-blue)` |
| `.board-image-modal__item--selected` | gallery tile, selected adds `border-color` + `outline: 2px solid var(--accent-blue)` |
| `.component-type-modal__item` | list row, `:hover` → `border-color var(--accent-blue)` + `0 2px 6px rgba(44,125,216,.15)` |

## Tables (in-panel and in-modal)

Same base for `.component-list`, `.resource-list`, `.tag-list`, `.*-modal__table`:

```
width 100%, border-collapse collapse, font-size 0.875rem
th: sticky top 0, z 2, padding .5rem, text-align left, font-weight 500, bg var(--bg-subtle)
td: padding .5rem, border-top 1px solid var(--border-neutral)
row:hover: bg var(--bg-hover)
row--selected: bg rgba(44,125,216,0.15)
```

- Nested/member row (group member under its group row): `.component-list__row--member` → `bg var(--accent-blue-light)`, id cell `padding-left: 1.75rem`, no connector line — reads as folder contents.
- Row action buttons: `.{x}-list__action-btn` — small (`0.75rem`), `--accent-blue`; `--danger` modifier → `--error` bg.
- Column resize: `.column-resize-handle` (vertical 6px hit area on the `<th>` right edge), grip `#999` → `--accent-blue` on hover/active. Widths persisted in `PanelState.columnWidths`.
- Empty states: `.{x}-list__empty` (nothing at all) vs `.{x}-list__empty-filter` (filtered to nothing) — both muted, centered, `padding 1rem`.

## Overlaid piece badges (edit mode)

Permanent (not hover-only) 18px badges in the four corners of a component:

| Class | Corner | Bg | Meaning |
|---|---|---|---|
| `.component-lock-badge` | top-right | `rgba(0,0,0,0.55)` | `bloqueado !== 'ninguno'` |
| `.component-hidden-badge` | bottom-right | `rgba(0,0,0,0.55)` | `oculto` |
| `.component-copy-badge` | bottom-left | `var(--error)` | is a linked copy |
| `.component-has-copies-badge` | bottom-left | `var(--accent-blue-dark)` | has copies — pill shape with count (doesn't fit the 18px circle) |

- All `pointer-events: none`, `box-shadow: 0 2px 4px rgba(0,0,0,.25)`, icon `padding 3px`.
- [gotcha] copy badge and has-copies badge share the bottom-left corner and the same icon; the **only** distinguisher is bg color (`--error` vs `--accent-blue-dark`).

## Contextual identifiers

- `.component-id-label`: top-left, `bg var(--accent-blue-dark)`, `0.72rem`, `pointer-events none`, `display: none` — shown only on `:hover`/`--selected` of a selectable piece. In `.is-copy` state the label bg becomes `--error`; `.is-group-passenger` → `--text-muted`.
- `.component-title-label` (`mostrarTitulo`): play mode only, always visible while active, anchored top-left outside the box. `background`/`color` applied inline per-component from `tituloColorFondo`/`tituloColorTexto` — **user data, not a token**.
- `.component-tooltip` (play mode, `identifyMode: 'tooltip'`): replaces native `title`. `bg var(--bg-toolbar)`, `--text-light`, `--shadow-2`, `max-width 220px`, above the piece, `:hover` on `.component-tooltip-host`, `pointer-events none`.

## Other reusable widgets

| Widget | Class | Spec |
|---|---|---|
| Help icon | `.help-icon` | 16px circle, `bg var(--text-muted)` → `var(--accent-blue)` on hover, `cursor: help`, opens a modal |
| Toast | `.toast` | fixed bottom-center, `bg var(--bg-toolbar)`, `0.75rem`, `--shadow-1`, `z 1100`; `.toast--visible` toggles `display` |
| Resize handle | `.resize-handle` | 18px bottom-right corner, diagonal grip `#999` → `--accent-blue` + `scale(1.15)` on hover/active; `--tl` variant top-left |
| Reveal zone | `.mazo-reveal-zone` | `2px dashed var(--border-neutral)`, muted text, `pointer-events none` — decorative deck reveal target |
| Drop target | `.drop-target` | transient: `3px solid var(--accent-blue)` + `box-shadow: var(--shadow-2), 0 0 0 6px var(--accent-blue-light)` while dragging a card over a deck |

## Icons

- No shared icon module. Each `ui/*.js` file defines its own `createXIcon()` returning an inline `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">`.
- Rendered size set by the container (`.icon-frame` 16px in toolbar, `.context-menu__item-icon` 18px, badge icons fill 18px with `padding: 3px`).
- Same silhouette duplicated across files if two contexts need it (e.g. the eye/hidden icon). Accepted — no dedup mechanism.
