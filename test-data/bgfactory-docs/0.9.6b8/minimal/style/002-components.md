# 002 — Reusable UI patterns

**Area**: Style bible

Shared visual patterns. One reusable JS builder per pattern (see `../architecture/002-modules.md` "Generic reusable widgets"). Reference the component file rather than re-describing its look.

## Modal

Structure: `.modal-overlay` > `.modal` > (`.modal__header`, optional `.modal__tabs`, `.modal__content`, `.modal__footer`).

| Part | Rule |
|---|---|
| `.modal-overlay` | `position: fixed` full-viewport, `background: rgba(0,0,0,0.5)`, flex-centered, `z-index: 1000`. |
| `.modal` | `background: white`, `border-radius: var(--radius-lg)`, `box-shadow: var(--shadow-2)`, `width: 90%`, `max-width: 500px`, `max-height: 80vh`, column flex. |
| `.modal__content` | `flex: 1`, `overflow-y: auto`, `padding: 1.5rem` — the only scrolling region. |
| `.modal__footer` | `border-top: 1px solid var(--border-neutral)`, buttons right-aligned (`justify-content: flex-end`), `gap: 0.5rem`. |
| Width variants | `.component-editor-modal` = `clamp(400px, 50vw, min(600px, 65vw))`; `.card-editor-modal` / `.image-adjust-modal--large` = `width: fit-content`. Recompute on resize via `clamp()` — no JS. |

Special modals with their own structure (no header/content/footer): `.progress-modal` (spinner + text, no close path), error/success variants use `.modal__header--error` / `--success` with `.modal__error-icon` / `.modal__success-icon`.

Tabs: `.modal__tab` (muted, `--bg-hover`) → `.modal__tab.active` (white bg, `--text-primary`, 2px `--accent-blue` bottom border).

Sections: `fieldset.modal__section` + `legend.modal__section-title` (color `--section-accent`). Toggle variant `--title--toggle` has a checkbox in the legend; `fieldset.modal__section--disabled` dims all non-legend children.

## Buttons

Shared base: `.btn-cancel, .btn-duplicate, .btn-accept, .btn-eliminar` — `padding: 0.5rem 1.5rem`, no border, `border-radius: var(--radius-sm)`, `font-size: 0.875rem`.

| Class | Role | Resting | `hover` | `disabled` |
|---|---|---|---|---|
| `.btn-accept` | Primary / confirm | `--accent-blue` bg, `--text-light` | `opacity: 0.9`, `translateY(-1px)`, blue glow shadow — only `:not(:disabled)` | `opacity: 0.5`, `cursor: not-allowed` |
| `.btn-cancel`, `.btn-duplicate` | Secondary | `--bg-subtle` bg, `--text-primary` | `--bg-hover` bg | `opacity: 0.5`, `cursor: not-allowed`, hover reverts to `--bg-subtle` |
| `.btn-eliminar` | Destructive | `--error` bg, `--text-light`, `margin-right: auto` (pushed to footer's left) | `opacity: 0.9`, `translateY(-1px)`, red glow shadow | — |

- [gotcha] `.btn-eliminar` sits at the **left** of the footer (`margin-right: auto`), not with the right-aligned cancel/accept pair.
- Toolbar/mode-switcher buttons are a separate style: `--accent-blue` (mode switcher) or outlined-on-dark (`.edit-toolbar button`, 1px `--text-light` border, transparent fill, `rgba(255,255,255,0.1)` on hover).
- A "coming soon" menu item uses `--item--soon`: `cursor: not-allowed`, `opacity: 0.5`, no hover background, plus a `__soon-tag` label.

## Menus (non-modal)

| Pattern | Class | Notes |
|---|---|---|
| Right-click context menu | `.context-menu` | Cursor-anchored, no overlay, light background. Module singleton (`ui/contextMenu.js`). `z-index: 1050`. |
| Column sort/filter dropdown | `.column-header-menu` | Opens under a column header. Sibling mechanic of context menu. `z-index: 1050`. |
| Export dropdown | `.export-menu` | Anchored under its button (`top: calc(100% + 0.5rem)`), `min-width: 220px`, **dark** background (`--bg-toolbar`) to match `.edit-toolbar` — deliberately not the light `.context-menu`. `z-index: 1200`. |
| "Add" split menu | `.resource-add` wrap + absolute menu | Relative wrap + absolute menu under button; same functional pattern as `.export-menu-wrap`. |

## Floating edit-mode panels

`.component-list` / resource / tag panels: collapsible, draggable, resizable (`ui/resizeHandle.js`), each rendered as a `<table>` with `border-collapse: collapse`, `font-size: 0.875rem`.

| Element | Rule |
|---|---|
| `th` | `position: sticky; top: 0`, `background: var(--bg-subtle)`, `font-weight: 500`, left-aligned. |
| `td` | `padding: 0.5rem`, `border-top: 1px solid var(--border-neutral)`. |
| `__empty` / `__empty-filter` | `--text-muted`, centered, `padding: 1rem` — distinct copy for "no items" vs "no match for filter". |
| Id cell | `max-width: 6rem`, ellipsis truncation. |
| Column resize | drag `<th>` edge, reuses `resizeHandle.js` axis `x` (`ui/tableColumnResize.js`). |

## Infinite table

`.infinite-table`: `--bg-table` fill + `radial-gradient` dot grid (`--bg-table-dot`, `1.5px` dot, `32px` tile), `cursor: grab` → `.grabbing` (`cursor: grabbing`) while panning, `user-select: none`. `.infinite-table__world` is the pan/zoom transform layer (`transform-origin: 0 0`).

## Icons

Inline SVG, 24×24 `viewBox`, `fill: none`, `stroke: currentColor`, `stroke-width: 2`, built per-call in JS (`createXIcon()` helpers in `editMode.js` / `playMode.js`). [gotcha] no shared icon file / sprite — each icon is a local helper. Chrome icons wrapped in `.icon-frame` (16–18px).
