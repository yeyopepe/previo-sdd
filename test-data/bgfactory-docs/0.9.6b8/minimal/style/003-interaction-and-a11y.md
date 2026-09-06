# 003 — Interaction states, feedback & accessibility

**Area**: Style bible

## Selection / hover on table pieces

Applies to every selectable piece type: `.carta`, `.board`, `.text-box`, shapes (`--selectable` modifier + `--selected` state). Uniform pattern:

| Tag | Visual |
|---|---|
| `selectable` (resting) | `cursor: pointer`. |
| `hover` | `outline: 2px dashed var(--accent-blue)`. |
| `selected` | `outline: 3px dashed var(--accent-blue)`, `outline-offset: 4px`. |
| `hover`/`selected` + `.is-copy` | same outline in `--error` (red) instead of blue — reinforces "this is a linked copy" at a glance. |
| `hover`/`selected` + invalid/muted | `outline-color: var(--error)` / `var(--text-muted)` per context. |

- On `hover`/`selected`, the piece's `.component-id-label` becomes `display: block` (hidden otherwise). Copy → label background `--error`.
- [gotcha] selection is shown with a **dashed outline**, never a box-shadow or fill change. `outline` (not `border`) so it does not shift layout.

## Piece shape modifiers

`.carta--hex`, `.carta--triangle` (clip-path shapes), `.carta--movable` / `--clickable` (cursor affordance), `.carta--flip-feedback` (transient flip animation class).

## Form controls

`.modal__field input/select/textarea`:

| Tag | Visual |
|---|---|
| resting | 1px `--border-neutral`, `--radius-sm`. |
| `focus` | `outline: none` + border switches to `--accent-blue` (2px). [gotcha] focus is shown by **border color change**, not a browser outline — `outline: none` is deliberate and paired with a visible border treatment. |
| `disabled` | reduced opacity / `not-allowed` per control. |
| `error` | `.modal__error` block + `.modal__header--error` with `.modal__error-icon`; detail in `.modal__error-detail`. |

`input[type="color"]` and `select` have dedicated sizing rules — see `src/styles/main.css:550-585`.

## Feedback surfaces

| Need | Surface | Rule |
|---|---|---|
| Brief non-blocking notice | `.toast` (`ui/toast.js`) | Auto-dismiss `3000ms`. `z-index: 1100`. |
| Error (any) | `showErrorModal` (`ui/errorModal.js`) | [gotcha] ALL errors go through this modal — never a toast or ad-hoc alert for errors. |
| Long operation | `.progress-modal` (`ui/progressModal.js`) | No buttons, no manual close (no ESC, no click-out); resolves itself when `work` finishes. Spinner: 40px, 4px ring, `--accent-blue-light` track / `--accent-blue` head, `progress-modal-spin` 0.8s. |
| Contextual help | `.help-icon` "?" (`ui/helpIcon.js`) | Opens a text/HTML modal on click. |

## Keyboard

`ui/globalShortcuts.js` — global keys are **direct equivalents of existing buttons**, no new action/confirm/validation:

| Key | Action |
|---|---|
| `ESC` | Cancel — clicks the modal's `.btn-cancel` (knows only the `.modal-overlay > .modal > .modal__footer` DOM pattern). |
| `ENTER` | Accept — clicks `.btn-accept`. |
| `DEL` / `SUPR` | Delete selected component (edit mode only). |
| Arrows | Move selected component by `(dx, dy)` (edit mode only). |

- `tagList.js` rows set `tabIndex = 0` (focusable list rows). Most other list rows are click-only.

## Accessibility — recorded facts

State only what is verifiable. Current known state (bootstrap, minimal):

| Fact | Status |
|---|---|
| `aria-label` on icon-only buttons | Present on zoom-fit, "Limpiar búsqueda" clear buttons, card shape/textbox buttons, resource buttons, maximize button. Spanish text. |
| `aria-hidden="true"` | On the decorative title pencil icon. |
| Focus visible on form fields | Yes — via border-color change (see Form controls). `outline: none` on inputs is intentional, paired with the border treatment. |
| Focus visible on table pieces | Via `:hover`/`selected` dashed outline; no dedicated `:focus-visible` rule for pieces. |
| `prefers-reduced-motion` handling | [gotcha] NOT implemented — no `@media (prefers-reduced-motion)` block. Spinner and `translateY(-1px)` button hover always animate. |
| Roles / ARIA landmarks | Minimal — no `role=` landmarks on regions; structure relies on native `h1`, `footer`, `<table>`. |
| Contrast ratios | Not measured / not documented. Do not claim compliance. |

Pending to document as it gets addressed: `prefers-reduced-motion` fallback, `:focus-visible` for canvas pieces, contrast audit of `--text-muted` (`#666` on `#f0f0f0`).
