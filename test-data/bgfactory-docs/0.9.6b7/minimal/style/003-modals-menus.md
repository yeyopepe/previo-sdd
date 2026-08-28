# 003 — Modals & menus

**Area**: Reusable components / Interaction patterns

Namespace: `ui.modal.*`. Anchors: `src/styles/main.css`, `src/ui/globalShortcuts.js`.

## Standard modal DOM pattern

```
.modal-overlay              position: fixed, inset 0, background rgba(0,0,0,.5), flex-center, z-index 1000
  > .modal                  background #fff, --radius-lg, --shadow-2, width 90% / max-width 500px, max-height 80vh, flex column
      > .modal__header      padding 1rem, border-bottom --border-neutral
          .modal__header-title
      > .modal__tabs        (optional) tabbed content
      > (content)           scrollable region
      > .modal__footer      padding 1rem, border-top --border-neutral, flex, gap .5rem, justify-content flex-end
          .btn-*            footer buttons (table below)
```

Width overrides:

| Class | Width rule |
|---|---|
| `.component-editor-modal` | `clamp(400px, 50vw, min(600px, 65vw))` |
| `.card-editor-modal`, `.image-adjust-modal--large` | `width: fit-content` (variable-width content) |

## Footer buttons

`.btn-cancel, .btn-duplicate, .btn-accept, .btn-eliminar` share:
`padding .5rem 1.5rem`, `border: none`, `--radius-sm`, `cursor: pointer`,
`font-size .875rem`, transition on background/opacity/transform/box-shadow.

| Variant | Base | Text | Notes |
|---|---|---|---|
| `.btn-cancel`, `.btn-duplicate` | `--bg-subtle` | `--text-primary` | Secondary. |
| `.btn-accept` | `--accent-blue` | `--text-light` | Primary confirm. |
| `.btn-eliminar` | `--error` | `--text-light` | Destructive. `margin-right: auto` → pinned to footer left. |

States:

- `[hover]` on `.btn-cancel`/`.btn-duplicate` → background `--bg-hover`.
- `[hover]` on `.btn-accept` (`:not(:disabled)`) → `opacity .9`, `translateY(-1px)`, `box-shadow 0 3px 8px rgba(44,125,216,.35)`.
- `[hover]` on `.btn-eliminar` → `opacity .9`, `translateY(-1px)`, `box-shadow 0 3px 8px rgba(211,47,47,.3)`.
- `[disabled]` (`.btn-cancel`/`.btn-duplicate`/`.btn-accept`) → `opacity .5`, `cursor: not-allowed`, hover neutralized.

[gotcha] `.btn-sacar` (play-mode "Sacar carta") follows the same standalone-class
exception — not a BEM `block__element`.

## Keyboard (globalShortcuts.js)

[motivación] Global keys are direct equivalents of existing buttons only — no new
action, confirmation, or validation.

```
ESC    → top .modal-overlay .btn-cancel   (else: clear selection)
ENTER  → top .modal-overlay .btn-accept
DEL    → top .modal-overlay .btn-eliminar (else, no modal: onDeleteSelected — main.js)
arrows → no modal: onMoveSelected(dx, dy) — main.js
```

`getTopModalOverlay()` = last `.modal-overlay` child of `<body>` (stacking order).

## Fieldset sections

`fieldset.modal__section` + `legend.modal__section-title` group related controls
inside a modal. Modifiers: `--toggle` (legend carries a checkbox), `--disabled`
(dims all children except legend), `--untitled`.

## Context menu (`src/ui/contextMenu.js`)

- Cursor-anchored, no overlay, does not block the rest of the screen.
- Closes on ESC **and** outside click (differs from a fixed dropdown-under-a-button, which closes only on outside click).
- Single instance: opening one closes the current.

## Toast (`src/ui/toast.js`)

- Non-blocking transient notice. `showToast(message)`, auto-hide after `3000ms`.
- Single `#toast` element reused.

## Progress modal (`.progress-modal`)

- Own structure — no header/content/footer, no buttons, no manual close.
- Spinner: 40px, `4px` border `--accent-blue-light` with `--accent-blue` top, `progress-modal-spin 0.8s linear infinite`.
- Sits above `.modal-overlay` (z-index 1000).
