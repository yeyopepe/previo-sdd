# 001 — Design tokens
**Area**: Visual design tokens

All tokens are CSS custom properties on `:root`. anchor: src/styles/main.css (`:root` block). Namespace: `ui.tokens.*`.

## Color

| Token | Value | Usage |
|---|---|---|
| `--bg-table` | `#c2c2c2` | infinite-table background (neutral gray) |
| `--bg-table-dot` | `rgba(0,0,0,0.09)` | table dot-grid pattern |
| `--bg-toolbar` | `#333333` | header `h1`, edit toolbar (dark) |
| `--bg-card` | `#f5f5f5` | card / piece surface |
| `--accent-blue` | `#2c7dd8` | interactive / selected ONLY (buttons, focus ring, selected row/outline) |
| `--accent-blue-dark` | `#123a66` | darker blue accent |
| `--accent-blue-light` | `#eaf3fc` | light fill for interactive panels; selection glow (`0 0 0 6px`) |
| `--text-primary` | `#1a1a1a` | body text |
| `--text-light` | `#ffffff` | text on dark/accent backgrounds |
| `--text-muted` | `#666666` | secondary text (version, hints) |
| `--error` | `#d32f2f` | error state, destructive action (`.btn-eliminar`) |
| `--success` | `#2e7d32` | success / positive confirmation |
| `--border-neutral` | `#dcdcdc` | all thin neutral borders |
| `--bg-subtle` | `#f0f0f0` | neutral resting fill (table header, secondary button) |
| `--bg-hover` | `#e8e8e8` | any neutral hover (row, secondary button, tab) |
| `--section-accent` | `#5b5f97` | `.modal__section` title — distinct from `--accent-blue` (interactive) |

- [gotcha] `--accent-blue` is reserved for interactive/selected state. Not a brand fill. A blue element means "you can act on this" or "this is selected".
- Base palette otherwise = neutral grays. No secondary hue beyond blue + error red + success green.

## Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `4px` | controls: buttons, inputs, small list items |
| `--radius-lg` | `8px` | containers: modal, panels, cards, game card piece |

## Shadow

| Token | Value | Usage |
|---|---|---|
| `--shadow-1` | `0 2px 6px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.08)` | level 1: subtle floating (panels, lists, pieces, header) |
| `--shadow-2` | `0 4px 20px rgba(0,0,0,0.15)` | level 2: overlay (modals, highest) |

## Typography

- `font-family: system-ui, sans-serif` (body). No custom UI font; resource fonts apply only to game components via `@font-face` (`ui.fontFaceRegistry`).
- Size scale in use (rem): `1.5` (h1), `1.125` / `0.95` (modal headings), `0.875` (default control/body), `0.8125`, `0.75`, `0.72`, `0.7` (dense labels, tags, hints).
- Weight: `400` default, `500` (labels, tab active, headings), `600` (emphasis headings).

## Motion

| Token | Value | Usage |
|---|---|---|
| `--transition-fast` | `150ms ease` | all hover/state transitions (background, opacity, transform, box-shadow) |

## Z-index scale

| Layer | z-index |
|---|---|
| table content | 1–2 |
| edit toolbar | 99 |
| header `h1` | 100 |
| mode switcher | 101 |
| floating panels | 15 + stack index (dynamic, `applyPanelStackOrder`) |
| context menu | 1000 |
| modal overlay | 1200 |

## Iconography

- `ui.icons.inline-svg` — icons are inline `<svg>` built in JS, one per use site. No shared icon file / sprite.
- Fixed attrs: `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"` (occasionally `2.5` for chevrons). 24×24 box; rendered size set by `.icon-frame` (typ. 18px).
- Repeated verbatim across `editMode.js`, `playMode.js`, `editModeToggle.js` — a new icon follows the same shape.
