# 002 — Design tokens

**Area**: Visual design tokens

Source of truth: `src/styles/main.css` `:root`. Namespace: `ui.tokens.*`.

## Color

| Token | Value | Usage |
|---|---|---|
| `--bg-table` | `#c2c2c2` | Infinite table ground. |
| `--bg-table-dot` | `rgba(0,0,0,0.09)` | Table dot-grid `radial-gradient` dots (1.5px). |
| `--bg-toolbar` | `#333333` | Header (`h1`, gradient `#3a3a3a`→this), edit toolbar, mode switcher, export menu. |
| `--bg-card` | `#f5f5f5` | Card component surface. |
| `--accent-blue` | `#2c7dd8` | Primary interactive: `.btn-accept`, focus borders, selected row, action buttons. |
| `--accent-blue-dark` | `#123a66` | Darker accent (emphasis on accent surfaces). |
| `--accent-blue-light` | `#eaf3fc` | Light fill for interactive panels / grouped rows, without the solid blue. |
| `--text-primary` | `#1a1a1a` | Body text. |
| `--text-light` | `#ffffff` | Text on dark/accent surfaces. |
| `--text-muted` | `#666666` | Secondary text, placeholders, disabled labels. |
| `--error` | `#d32f2f` | Error state, destructive action (`.btn-eliminar`, `.component-list__action-btn--danger`). |
| `--success` | `#2e7d32` | Success / positive confirmation state. |
| `--border-neutral` | `#dcdcdc` | All thin neutral borders. |
| `--bg-subtle` | `#f0f0f0` | Neutral resting fill: table header, secondary button. |
| `--bg-hover` | `#e8e8e8` | Any neutral hover: row, secondary button, tab. |
| `--section-accent` | `#5b5f97` | `.modal__section` legend title. Distinct from `--accent-blue` (which means interactive/selected). |

[gotcha] `--section-accent` is deliberately not `--accent-blue`: blue is reserved
for interactive/selected meaning, so section titles use their own violet-grey.

## Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `4px` | Controls: buttons, inputs, small list items. |
| `--radius-lg` | `8px` | Prominent containers: modal, panels, cards, card component. |

## Shadow

| Token | Value | Usage |
|---|---|---|
| `--shadow-1` | `0 2px 6px rgba(0,0,0,.10), 0 1px 2px rgba(0,0,0,.08)` | Level 1 — subtle float: panels, lists, table pieces, header. |
| `--shadow-2` | `0 4px 20px rgba(0,0,0,.15)` | Level 2 — overlay: modals, export menu. Highest. |

## Motion

| Token | Value | Usage |
|---|---|---|
| `--transition-fast` | `150ms ease` | Standard transition for background/opacity/border/transform on interactive elements. |

Ad-hoc (not tokenized): `.btn-accept:hover` / `.btn-eliminar:hover` add
`transform: translateY(-1px)` + a colored `box-shadow` matching the button base
color (`rgba(44,125,216,.35)` / `rgba(211,47,47,.3)`).

## Typography

- `body { font-family: system-ui, sans-serif }`. No custom UI font resource.
- No typographic scale tokenized; sizes set per component in `rem` (`h1` 1.5rem, buttons 0.875rem, modal text ~0.95rem).

## Spacing

[gotcha] No spacing-scale tokens. Padding/gap set per component, mostly in `rem`
multiples of 0.25 (`0.5rem`, `1rem`, `1.75rem 1.5rem`). Adding a change that needs
a shared spacing scale = new tokens, document here.
