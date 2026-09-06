# 001 — Style bible overview

**Area**: Style bible

Style/UI conventions of BG Factory. Values are authoritative from `src/styles/main.css` (`:root` custom properties). Point at that file for anything not tabled here. Style concepts get a canonical path on the `ui.*` branch of `../architecture/00-namespace.md`.

## Medium

- Web, single stylesheet `src/styles/main.css` (~3373 lines), no preprocessor, no CSS framework.
- No dark mode, no theming layer. One palette.
- Font: `font-family: system-ui, sans-serif` on `body`. No web font shipped for the chrome (user-uploaded fonts are a *resource* feature, registered via `@font-face` by `ui/fontFaceRegistry.js`, not part of the style system).

## Design tokens

All defined once in `:root` (`src/styles/main.css:1-23`). Cite by `ui.*` path; value lives in the token.

### Color

| Token | Value | Usage |
|---|---|---|
| `--bg-table` | `#c2c2c2` | Infinite-table background (both modes); `body` background. |
| `--bg-table-dot` | `rgba(0,0,0,0.09)` | Dotted grid on the infinite table (`radial-gradient`, 32px tile). |
| `--bg-toolbar` | `#333333` | Header (`h1`), edit toolbar, export dropdown menu. |
| `--bg-card` | `#f5f5f5` | Card component surface. |
| `--accent-blue` | `#2c7dd8` | Primary interactive: `.btn-accept`, active tab underline, mode-switcher buttons, focus ring. |
| `--accent-blue-dark` | `#123a66` | Darker accent variant. |
| `--accent-blue-light` | `#eaf3fc` | Light fill for interactive panels — never the solid blue. Spinner track. |
| `--text-primary` | `#1a1a1a` | Default body text. |
| `--text-light` | `#ffffff` | Text on dark surfaces (toolbar, accent buttons). |
| `--text-muted` | `#666666` | Secondary text, empty-state text, column headers. |
| `--error` | `#d32f2f` | Error states and destructive actions (`.btn-eliminar`). |
| `--success` | `#2e7d32` | Success / positive confirmation. |
| `--border-neutral` | `#dcdcdc` | Every thin neutral border (modal dividers, table row separators). |
| `--bg-subtle` | `#f0f0f0` | Neutral resting fill (table header, secondary button). |
| `--bg-hover` | `#e8e8e8` | Any neutral hover (row, secondary button, tab). |
| `--section-accent` | `#5b5f97` | `.modal__section` legend title — deliberately distinct from `--accent-blue` (which means interactive/selected). |

- [gotcha] `--section-accent` (`#5b5f97`) is NOT `--accent-blue`. Section headings must not use the interactive-blue token.
- [gotcha] Interactive panel fills use `--accent-blue-light`, never solid `--accent-blue`.

### Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `4px` | Controls: buttons, inputs, small list items. |
| `--radius-lg` | `8px` | Prominent containers: modal, panels, cards, the card component. |

### Elevation (shadow)

| Token | Value | Level |
|---|---|---|
| `--shadow-1` | `0 2px 6px rgba(0,0,0,.10), 0 1px 2px rgba(0,0,0,.08)` | Level 1 — subtle float: panels, lists, pieces, header, toolbar. |
| `--shadow-2` | `0 4px 20px rgba(0,0,0,.15)` | Level 2 — overlay: modals, dropdown menus. Highest. |

### Motion

| Token | Value | Usage |
|---|---|---|
| `--transition-fast` | `150ms ease` | All hover/focus/active transitions. Single duration — no scale of durations. |

Named keyframes: `progress-modal-spin` (0.8s linear infinite) for the loading spinner.

### Spacing

No spacing-scale tokens. Spacing is written ad hoc in `rem` (`0.25`, `0.5`, `0.75`, `1`, `1.5`, `1.75`) and occasionally `px`. [gotcha] there is no `--space-*` scale — do not invent one; follow the `rem` steps already in use.

## z-index ladder

Single global stack, values assigned inline (not tokenized). Ascending:

| z-index | Element |
|---|---|
| 99 | `.edit-toolbar` |
| 100 | header `h1` |
| 101 | `#mode-switcher` |
| 1000 | `.modal-overlay` |
| 1050 | context menu / column-header menu (above modal overlay) |
| 1100 | `.toast` |
| 1200 | `.export-menu` (above everything, including toast) |

- [gotcha] the export dropdown (`1200`) is intentionally above the toast (`1100`), which was previously the ceiling.

## See also

- `002-components.md` — modal / button / menu / panel patterns and their states.
- `003-interaction-and-a11y.md` — interaction states, feedback surfaces, accessibility facts.
- `004-writing.md` — identifier naming, class naming (BEM), user-facing copy language.
