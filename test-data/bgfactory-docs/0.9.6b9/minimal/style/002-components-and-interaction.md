# 002 — Components and interaction patterns
**Area**: Interaction patterns

## Modal

`ui.modal.contract` — fixed DOM structure, relied on by `src/ui/globalShortcuts.js`:

```
.modal-overlay > .modal > .modal__footer
    .btn-cancel      cancel  (ESC triggers .click())
    .btn-accept      accept  (Enter triggers .click() when !disabled)
    .btn-eliminar    delete  (Delete key triggers .click() when a modal is open)
```

- `.modal-overlay` z-index `1200` (above `.toast`, context menu). `box-shadow: var(--shadow-2)`, `border-radius: var(--radius-lg)`.
- Multiple overlays stack; `globalShortcuts` acts on the last `.modal-overlay` child of `<body>`.
- [gotcha] Enter is ignored while focus is in a `<textarea>` (newline wins). ESC/Enter only fire if the matching footer button exists.
- `.modal__section` title uses `--section-accent`, NOT `--accent-blue`.

## Buttons

`ui.button.*` — anchor: src/styles/main.css (`.btn-cancel, .btn-duplicate, .btn-accept, .btn-eliminar`)

| Class | Background | Text | Role |
|---|---|---|---|
| `.btn-accept` | `--accent-blue` | `--text-light` | primary / confirm |
| `.btn-cancel`, `.btn-duplicate` | `--bg-subtle` | `--text-primary` | secondary / dismiss |
| `.btn-eliminar` | `--error` | `--text-light` | destructive; `margin-right: auto` (pushed to footer left) |

Shared: `padding: 0.5rem 1.5rem`, `border: none`, `border-radius: var(--radius-sm)`, `font-size: 0.875rem`, `transition: … var(--transition-fast)`.

- `[hover]` `.btn-accept` / `.btn-eliminar`: `opacity: 0.9`, `transform: translateY(-1px)`, colored shadow (`rgba(44,125,216,0.35)` / `rgba(211,47,47,0.3)`).
- `[hover]` `.btn-cancel`: `background: var(--bg-hover)`.
- `[disabled]` all: `opacity: 0.5`, `cursor: not-allowed`, hover suppressed.
- [gotcha] Standalone action buttons that are not part of a BEM block (`.btn-sacar`, `.btn-cancel` etc.) are a documented naming exception — see [003](003-writing-and-accessibility.md).

## Floating panels (edit mode)

`ui.panel.*` — three panels: components, resources, tags. anchor: src/modes/edit/editMode.js

- Draggable (header `mousedown`), resizable, collapsible. Position / width / height / collapsed / columnWidths persisted via `panelState` / `resourcePanelState` / `tagPanelState`.
- z-order: `panelStackOrder` array (`['component','resource','tag']`), `mousedown` (capture) brings a panel to front; `z-index = 15 + index`. NOT persisted — resets on reload.
- `box-shadow: var(--shadow-1)`, `border-radius: var(--radius-lg)`.

## Infinite table

`ui.table` — anchor: src/ui/table.js

- Pan: left-drag on background. Zoom: wheel, cursor-anchored. `ui.table.zoom.min = 0.5`, `ui.table.zoom.max = 2.5`.
- Camera (`cameraX`/`cameraY`/`zoom`) is module-level, survives re-mount, NOT persisted.
- `fitToBounds(bounds)` — instant reframe (no transition) with `padding: 60`; `null` → neutral view.
- `.infinite-table.grabbing` while dragging.

## Selection (edit mode)

- `selectedComponentIds: Set` — Ctrl/Cmd-click adds/removes; plain click replaces with that one unit (or clears if it was the only one).
- A group selects/deselects as an atomic block (all members share `groupId`).
- `primarySelectedIds` — subset that was the direct click target. Outline only: `[selected]` blue outline = directly clicked; gray outline = rest of the group. Never used for action scope (that is always `selectedComponentIds`).

## Feedback patterns

| Pattern | When | Source |
|---|---|---|
| toast | lightweight confirmation ("Etiqueta añadida") | `src/ui/toast.js#showToast` |
| error modal | recoverable error / blocked action | `src/ui/errorModal.js#showErrorModal` |
| progress modal `[loading]` | long blocking op (import, adding cards to deck) — blocks input until done | `src/ui/progressModal.js#runWithProgressModal` |
| native `confirm()` | single-item destructive action | inline |
| bulk confirm modal | 2+ item destructive action; enumerates affected | `src/ui/bulkDeleteConfirmModal.js` |

## Keyboard shortcuts

`ui.shortcuts` — anchor: src/ui/globalShortcuts.js. Every shortcut is an equivalent of an existing button/action, no new behavior.

| Key | Modal open | No modal, edit mode |
|---|---|---|
| `Escape` | click `.btn-cancel` of top modal | — |
| `Enter` | click `.btn-accept` (unless in `<textarea>`, or disabled) | — |
| `Delete` | click `.btn-eliminar` if present | delete current selection |
| `Arrow*` | ignored (a card underneath must not move) | move selection by `1`px (`10`px with Shift) |

- Ignored when focus is in `<input>` / `<textarea>` (except ESC/Enter modal handling).
