# 001 — Design tokens: color, radius, shadow, type, motion, z-index
**Area**: Design tokens

All values from [src/styles/main.css](../../../src/styles/main.css) `:root`. Canonical paths on the `ui.*` branch of [../architecture/00-namespace.md](../architecture/00-namespace.md).

## Color tokens

| Token | Value | Usage |
|---|---|---|
| `--bg-table` | `#c2c2c2` | infinite table background |
| `--bg-table-dot` | `rgba(0,0,0,0.09)` | dotted grid on the table (radial-gradient, 32px cell) |
| `--bg-toolbar` | `#333333` | top toolbar, panel headers, tooltips, toasts, context-menu-on-dark |
| `--bg-card` | `#f5f5f5` | floating panel body background |
| `--accent-blue` | `#2c7dd8` | the single accent: primary buttons, selection outline, focus ring, active state, links |
| `--accent-blue-dark` | `#123a66` | `.component-id-label` bg, `has-copies` badge |
| `--accent-blue-light` | `#eaf3fc` | interactive light surfaces: context menu, resource add-menu bg |
| `--text-primary` | `#1a1a1a` | body text |
| `--text-light` | `#ffffff` | text on dark/accent surfaces |
| `--text-muted` | `#666666` | secondary text, hints, disabled, placeholders |
| `--error` | `#d32f2f` | destructive actions, error states, copy indicator (`.is-copy`) |
| `--success` | `#2e7d32` | success/confirmation states |
| `--border-neutral` | `#dcdcdc` | all thin neutral borders |
| `--bg-subtle` | `#f0f0f0` | resting neutral fills (table header, secondary button) |
| `--bg-hover` | `#e8e8e8` | any neutral hover (row, secondary button, tab) |
| `--section-accent` | `#5b5f97` | `.modal__section` legend title only — deliberately distinct from `--accent-blue` |

- [gotcha] Palette is neutral **grey**, not black/white. Table is `#c2c2c2`, not white. There is exactly **one** accent color (`--accent-blue`); no secondary accent — new interactive affordances reuse it.
- Focus ring is always `box-shadow: 0 0 0 3px rgba(44,125,216,0.15)` + `border-color: var(--accent-blue)` + `outline: none`. Repeated literally across every input; not tokenized.

## Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `4px` | controls: buttons, inputs, list items, badges, menus |
| `--radius-lg` | `8px` | containers: modals, floating panels, cards (`.carta`), custom boards |

## Shadow

| Token | Value | Usage |
|---|---|---|
| `--shadow-1` | `0 2px 6px rgba(0,0,0,.10), 0 1px 2px rgba(0,0,0,.08)` | level 1: floating-but-resting — panels, toolbar, game pieces, toast |
| `--shadow-2` | `0 4px 20px rgba(0,0,0,.15)` | level 2: overlays — modals, context menus, dropdowns |

- [gotcha] A game piece with a **non-rectangular** silhouette (`.dice`, `.carta--hex`, `.carta--triangle`) must use `filter: drop-shadow(...)`, NOT `box-shadow` — `box-shadow` follows the bounding box, `drop-shadow` follows the clipped shape. Rectangular pieces (`.carta`, `.board`, `.document-viewer`) use `box-shadow: var(--shadow-1)`.
- "Elevation system": pieces at rest carry `--shadow-1`; transient "lifted off the table" state is `.lifted` (`transform: translate(-2px,-4px)` + `box-shadow: 6px 7px 9px 2px rgba(0,0,0,.35)`), `.carta--flip-feedback` is a second brief lift (`translate(0,-6px) scale(1.03)` + `--shadow-2`).
- Ad-hoc accent-tinted shadows recur uquantized: `0 2px 6px rgba(44,125,216,.15)` (list item hover), `0 3px 8px rgba(44,125,216,.35)` (primary button hover). Not tokenized.

## Typography

| Property | Value |
|---|---|
| body font | `system-ui, sans-serif` |
| mono font | `ui-monospace, monospace` (ids, error detail, code) |
| base size | `1rem` body; app title `1.5rem` |
| common sizes | `0.875rem` (default control/table text), `0.75rem` (hints, badges, toast, captions), `0.8125rem`, `0.72rem` (id label) |
| weights used | `400`, `500` (table headers, labels), `600` (section titles, emphasis) |
| numeric | `font-variant-numeric: tabular-nums` on zoom-level readouts |

- No custom web font in the chrome. User-uploaded fonts (`type: 'tipografia'`) apply only to component content (dice result, card text) via `ui/fontFaceRegistry.js`.

## Motion

| Token | Value | Usage |
|---|---|---|
| `--transition-fast` | `150ms ease` | every hover/focus/active/state transition, every transient piece state |

- One-offs: `transform 60ms linear` / `transform 60ms` (resource preview zoom), `progress-modal-spin 0.8s linear infinite` (spinner), card-flip animation in `componentRenderer.js`.
- No `prefers-reduced-motion` handling anywhere (see [004](004-interaction-states-feedback-and-accessibility.md)).

## Z-index ladder

Fixed, documented inline. New layered UI slots into this ladder, does not invent a value.

| Layer | z-index |
|---|---|
| `#app-version`, `.component-tooltip` | 10 |
| floating panels (`.component-panel-container` etc.) | 15+ (assigned dynamically by `editMode.js#applyPanelStackOrder`, `15 + stackIndex`) |
| `.edit-toolbar` | 99 |
| `h1#app-title`, `#mode-switcher` | 100–101 |
| `.modal-overlay` | 1000 |
| `.context-menu`, `.column-header-menu` | 1050 (above modal — they open over the card-editor modal) |
| `.toast` | 1100 |
| `.export-menu` | 1200 (highest) |
| in-panel sticky `<th>` | 2 (local) |

## Spacing

- No spacing scale token. Values are `rem`-based ad hoc: `0.25 / 0.35 / 0.5 / 0.75 / 1 / 1.5 rem` dominate. Modal padding: header/footer `1rem`, content `1.5rem`. Panel header/footer padding `0.5rem 1rem`.
- Icon `currentColor` convention: all inline SVG icons use `stroke="currentColor"` / `fill` from the parent, sized 24×24 viewBox, rendered at 14–18px. No shared icon file — each `ui/*.js` inlines its own `createXIcon()` (see [003](003-reusable-components-and-patterns.md)).
