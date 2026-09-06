# 004 — Interaction states, feedback, and accessibility
**Area**: Interaction & a11y

Interaction states, transient feedback, and the current accessibility posture. Source: [src/styles/main.css](../../../src/styles/main.css), `src/ui/*.js`, [src/ui/globalShortcuts.js](../../../src/ui/globalShortcuts.js).

## Interaction states

Fixed tags: `[hover]`, `[focus]`, `[active]`, `[disabled]`, `[selected]`, `[loading]`, `[empty]`.

### Inputs / selects / textareas

- `[focus]` — `outline: none`, `border-color: var(--accent-blue)`, `box-shadow: 0 0 0 3px rgba(44,125,216,0.15)`. Uniform across every text field, filter box, number input, `<select>`, `<textarea>`. Number inputs additionally hide spin buttons (`appearance: textfield`).
- `[disabled]` (order input, select) — `background: var(--bg-subtle)` or `--border-neutral`, `color: var(--text-muted)`, `cursor: not-allowed`.

### Buttons

- `[hover]` primary — `opacity: 0.9`; footer primary also `translateY(-1px)` + accent-tinted shadow.
- `[hover]` secondary/neutral — `background: var(--bg-hover)`.
- `[disabled]` — `opacity: 0.5`, `cursor: not-allowed`, hover suppressed. [gotcha] `globalShortcuts` Enter binding checks `acceptBtn.disabled` and does nothing if set — disabled state is functional, not just visual.

### Rows (tables, lists, menu items)

- `[hover]` — `background: var(--bg-hover)` (neutral tables) or `background: var(--accent-blue)` + `color: var(--text-light)` (menus).
- `[selected]` — `background: rgba(44,125,216,0.15)`.
- Menu `[disabled]` item — `cursor: not-allowed`, `opacity: 0.6`, muted, no hover.

### Selectable game pieces (per block: `.carta`, `.board`, `.dice`, `.document-viewer`, `.text-box`, `.tablero-personalizado`)

| State | Appearance |
|---|---|
| `[hover]` | `outline: 2px dashed var(--accent-blue)` |
| `[selected]` | `outline: 3px dashed var(--accent-blue)`, `outline-offset: 4px` |
| `[hover]`/`[selected]` + `.is-copy` | outline + id-label become `var(--error)` |
| `[selected]` + `.is-group-passenger` | outline + id-label become `var(--text-muted)` (grey — dragged into selection, not directly clicked) |
| `[hover]`/`[selected]` | `.component-id-label` flips to `display: block` |

- [gotcha] Outline is **dashed** for selection; a **solid** outline (`.drop-target`, `.card-editor-modal__*--selected`, `.dice-font-modal__item--selected`) means something else (drop zone / editor-canvas selection).

## Transient feedback

| Class | Trigger | Effect | Applied by |
|---|---|---|---|
| `.lifted` | drag start in play mode (`liftOnDrag`) | `transform: translate(-2px,-4px)` + `box-shadow: 6px 7px 9px 2px rgba(0,0,0,.35)` | `componentRenderer.js` on mousedown/up |
| `.carta--flip-feedback` | card flip completes | `transform: translate(0,-6px) scale(1.03)` + `--shadow-2` | `componentRenderer.js` timer |
| `.drop-target` | card dragged over a deck (rect overlap) | solid accent outline + accent-light halo | `componentRenderer.js` |
| `.resize-handle--active` | resize in progress | grip → accent + `scale(1.15)` | `resizeHandle.js` / `tableColumnResize.js` |
| `.column-header-menu__item--active` | sort applied | persists accent bg with no hover | `columnHeaderMenu.js` |
| progress modal | blocking op (import, bulk card→deck) | spinner + text, no dismiss | `runWithProgressModal()` |
| toast | brief confirmation ("Etiqueta añadida") | `.toast--visible` for a timeout | `showToast()` |

All transitions use `var(--transition-fast)` (150ms ease) unless noted.

## Feedback surfaces — which to use

| Situation | Surface |
|---|---|
| brief non-blocking confirmation | toast (`showToast`) |
| blocking work in progress | `runWithProgressModal` |
| single-item destructive confirm | native `confirm()` |
| multi-item destructive confirm | dedicated modal listing affected items (`openBulkDeleteConfirmModal`, `openTagDeleteConfirmModal`, `openResourceReplaceConfirmModal`) |
| error, blocking | `showErrorModal(title, message, detail?)` — `.modal__header--error` + red circle icon; optional `.modal__error-detail` monospace block |
| success acknowledgement in a modal | `.modal__header--success` + green circle icon |
| inline field error | `.modal__error` (`--error`, `0.75rem`, below the field) |
| post-action report (import warnings) | `.import-report-modal` with a table; error rows use `.error-cell` (`color: var(--error)`) |

## Accessibility — current state (facts, not compliance claims)

| Aspect | Current state |
|---|---|
| Keyboard | Global: Escape → cancel, Enter → accept, Delete → delete, arrows → move selection ([globalShortcuts.js](../../../src/ui/globalShortcuts.js)). No focus trap in modals. No documented tab order. `.tag-list__row:focus` → `background: rgba(44,125,216,0.15)` (only list with a focus style). |
| Focus visibility | Inputs: custom ring (`outline: none` + accent box-shadow). [gotcha] `outline: none` is set on inputs, buttons rely on the UA default outline (not overridden). Game pieces: no `:focus` style, not focusable. |
| ARIA | Sparse. `aria-label` on the fit-to-bounds button only. No `role`/`aria-*` on modals, menus, panels, or the context menu. `.modal-overlay` is not marked `role="dialog"`. |
| Contrast | `--text-primary #1a1a1a` on white ≈ 17:1 (pass). `--text-muted #666` on white ≈ 5.7:1 (pass AA normal). `--text-light #fff` on `--accent-blue #2c7dd8` ≈ 3.4:1 ([gotcha] below AA 4.5:1 for normal text — primary buttons use `font-size: 0.875rem`, borderline). `--text-muted` on `--bg-subtle #f0f0f0` ≈ 4.9:1. |
| Motion | No `prefers-reduced-motion` media query. All transitions/animations always run. |
| Color-only signalling | [gotcha] copy vs has-copies badge differ only by bg color; selection copy/group states differ only by outline color. No shape/text redundancy. |
| Screen reader | No live regions. Toasts (`display` toggle) and error modals are not announced. `alt` text: user-provided on resources, none on decorative UI icons (SVGs have no `<title>`/`aria-hidden`). |

- Records the state as-is. Not a conformance statement. A change touching any of these rows should note the delta explicitly.
