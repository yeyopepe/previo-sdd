# 002 — Buttons, layout, resize, sticky table header

**Area**: Layout & components

## Buttons

All buttons share this base (adapt background/border by context):

```css
padding: 0.5rem 1rem;   /* or 0.25rem 0.5rem if a small button inside an item */
border: none;           /* or 1px solid var(--text-light) on a dark background */
border-radius: var(--radius-sm);
cursor: pointer;
font-size: 0.875rem;    /* or 0.75rem if small */
transition: background var(--transition-fast), opacity var(--transition-fast);
```

- Primary action: background `var(--accent-blue)`, text `var(--text-light)`. Hover: `opacity: 0.9` + `transform: translateY(-1px)` + `box-shadow: 0 3px 8px rgba(44,125,216,.35)`.
- Secondary/cancel action: background `var(--bg-subtle)`, text `var(--text-primary)`. Hover: `var(--bg-hover)` — only `background` transition, no `transform`.
- Destructive action (delete/remove): background `var(--error)`, text `var(--text-light)`. Hover: `opacity: 0.9` + `transform: translateY(-1px)` + `box-shadow: 0 3px 8px rgba(211,47,47,.3)` — same treatment as primary, only background/shadow color changes.
  - Applies to `.btn-eliminar` (modals) and the BEM modifier `--danger` (e.g. `.component-list__action-btn--danger`).
  - Any action that deletes an element uses this color across the whole app, never the primary blue.
- Button on a dark background (toolbar): transparent, border `1px solid var(--text-light)`. Hover: `rgba(255,255,255,0.1)` with a `background` transition, no `transform`.

### Header control row (`#mode-switcher`, reorganized 00244)

`#mode-switcher` is the fixed top-right control row (`position: fixed; top: 0.5rem; right: 1rem; z-index: 101`, flex, `gap: 0.5rem`), populated in **both** modes now.

| Button | Class | Scheme | Notes |
|---|---|---|---|
| "Modo Edición" / "Modo Juego" | `.mode-switcher__mode-btn` | primary action (blue) | Mode-switch button, same look the old "Entrar/Salir del modo edición" had. Always in `#mode-switcher`, in both modes. Play mode = text-only; edit mode = icon + text. |
| "Ajustar zoom" | `.mode-switcher__fit-btn` | primary action (blue), icon-only | `padding: 0; width: 36px; height: 36px; justify-content: center`. `.icon-frame` `18×18`. |
| "Configuración" | `.mode-switcher__settings-btn` | "ghost on dark", icon-only | Same `36×36` size block as `.mode-switcher__fit-btn` (`.mode-switcher__fit-btn .icon-frame, .mode-switcher__settings-btn .icon-frame { 18×18 }`). `background: none; border: 1px solid var(--text-light)`; hover `rgba(255,255,255,0.1)`. **NOT blue** — visually separates it from the two blue actions. Gear glyph is a filled-silhouette SVG (`fill="currentColor"`), distinct from `.mode-switcher__fit-btn`'s stroked corner-frame icon. |
| "Importar" / "Exportar" | — (`.export-menu-wrap > button` for Export) | "ghost on dark" | `background: none; border: 1px solid var(--text-light)`; hover `rgba(255,255,255,0.1)` — the **same scheme as `.edit-toolbar button`**, so the file block looks identical in both modes. `#mode-switcher button` base: `padding: 0.5rem 1rem; display: inline-flex; align-items: center; gap: 0.375rem`; `.icon-frame` `16×16`. |

- `#mode-switcher button` no longer sets `background: var(--accent-blue)` for every descendant (removed 00244). Blue is now opt-in per class (`.mode-switcher__mode-btn`, `.mode-switcher__fit-btn`); the file-block buttons fall through to the ghost scheme via `#mode-switcher > button:not(.mode-switcher__mode-btn):not(.mode-switcher__fit-btn):not(.mode-switcher__settings-btn)` and `#mode-switcher .export-menu-wrap > button`.
- `.edit-toolbar__exit-btn` and its rules removed (00244) — the mode-switch button no longer lives in `.edit-toolbar`.
- `#edit-toolbar > .mode-switcher__fit-btn` rules removed (00244) — "Ajustar zoom" is no longer a direct child of `#edit-toolbar`; it lives in `#mode-switcher` in both modes.
- **Header control-row separator**: a `.toolbar-divider` (`width: 1px; height: 1.5rem; background: rgba(255,255,255,0.2)`) between the file block (Importar/Exportar) and the action block (Modo, Ajustar zoom, Configuración). Present **only in play mode**, inside `#mode-switcher`. Edit mode never renders a `.toolbar-divider`: the file block lives in the `.edit-toolbar` band, and Importar/Exportar sit adjacent there with no divider between them.
- Edit mode: `.edit-toolbar` band holds `[Importar] [Exportar]` adjacent in a single `.toolbar-group` (`gap: 0.5rem`), no `.toolbar-divider` between them (00254). `.toolbar-divider` exists only in `#mode-switcher`, play mode.
- Disabled: `opacity: 0.5; cursor: not-allowed`, no `transform` on hover.
- No `:active` — interaction feedback is the `opacity`/`background`/`box-shadow`/`transform` change on `:hover`, with a 150ms transition (`var(--transition-fast)`).
- **Icon-only button** (action with no visible text): SVG icon with `stroke="currentColor"` (inherits the context's text/border color), always with `title`/`aria-label` as an accessible label.
  - Inside an existing bar button (e.g. `.edit-toolbar button`): same padding/size as that block's text buttons — only the content changes.
  - Standalone square icon-only button (`.mode-switcher__fit-btn`, `.mode-switcher__settings-btn`): `padding: 0; width: 36px; height: 36px`, centered icon (`display: inline-flex; align-items: center; justify-content: center`), `.icon-frame` `18×18`. Both live in `#mode-switcher` in both modes (00244) — see "Header control row" above for their schemes (fit = blue, settings = ghost). The size block uses `#mode-switcher .mode-switcher__fit-btn` / `#mode-switcher .mode-switcher__settings-btn` to win by specificity over `#mode-switcher button`'s `padding: 0.5rem 1rem` (a bare class loses and the icon distorts inside the `36×36`).
- **Full-text button in a tight space**: when a text button is wedged between narrow elements (not in a loose action row) — e.g. `.card-editor-modal__adjust-image`, between the two faces of a card — it uses `padding: 0.5rem 0.75rem` as an intermediate variant between the standard (`0.5rem 1rem`) and the small item one (`0.25rem 0.5rem`). Reuse `0.75rem` instead of introducing a fourth ad-hoc value.

## Layout

- App = full-height flex column: `html, body { height: 100% }`, `body { display:flex; flex-direction:column; height:100vh }`. Fixed header (`h1`, `3.5rem`) + flexible `#content` (`flex: 1 1 auto; min-height: 0`).
- Fixed-width side panels: `400px` (`.component-list`, `.edit-mode-panel`).
- Default initial position of edit-mode floating panels: both anchored to the right side, stacked vertically (`.component-panel-container` on top, `.resource-panel-container` below) — only a starting position, the user can drag each panel freely afterward.
- `z-index` of `.component-panel-container`/`.resource-panel-container`/`.tag-panel-container`: not a fixed CSS value — computed in `modes/edit/editMode.js` (`applyPanelStackOrder`, base `15`, one per position in `panelStackOrder`) to reflect which of the three is in front after the user's last interaction.
  - Being `position: absolute` inside `tableContainer` (not `fixed`), they fall outside the next layer table, but always well below its first layer (`99`, edit toolbar).

### Z-index of overlays (`position: fixed`)

| z-index | Layer |
|---|---|
| `10` | Version footer |
| `99` | Edit toolbar |
| `100` | Header |
| `101` | Header control row (`#mode-switcher`, populated in both modes; in play mode: Importar/Exportar/separator/Modo/Ajustar zoom/Configuración — the `separator` is play-mode only, never the `.edit-toolbar`) |
| `1000` | Modal overlay |
| `1050` | Component context menu (`.context-menu`, `003-modales-menus.md`, "Component context menu") and column-header menu (`.column-header-menu`, `003-modales-menus.md`, "Actions dropdown menu") |

- `1050` is the app's highest level, not the modal overlay — both menus can open with a modal already visible behind (e.g. the card editor) and must be in front of it.
- When adding a new fixed/absolute element: choose its `z-index` respecting this order (below the modal, above normal content).

### Version footer (`#app-version`)

`position: fixed; bottom: 1rem; right: 1rem; z-index: 10` (table above). `font-size: 0.75rem` (`001-tokens-visual.md`, Typography), `color: var(--text-muted)`, `line-height: 1.35`, `text-align: right`.

- Two fixed lines (00243): `.app-version__name` (`BG Factory v<NNNNN>`) + `.app-version__repo` (an external link, `004-naming-and-patterns.md` → BEM block `app-version`; link style in `005-text-links-and-external-links.md`). Fixed project content, not user-editable, identical in both modes.
- Optional user line (00250): `.app-version__table-text` + `.app-version__separator`, prepended above the two fixed lines, only when `state.tableText` (`00-namespace.md`) is non-empty. Built by `renderAppVersion()` in `src/main.js` bootstrap, not a `src/ui/*` module.

| Element | Rule |
|---|---|
| `.app-version__table-text` | `white-space: pre-line` (honors the user's line breaks); `margin-bottom: 0.25rem`. Plain text via `textContent`, never `innerHTML`. Inherits `font-size`/`color`/`text-align` from `#app-version`. |
| `.app-version__separator` | `<hr>`; `border: none; border-top: 1px solid var(--border-neutral)` (`001-tokens-visual.md`); `margin: 0 0 0.25rem`. Full width of the fixed-position `#app-version` box (no explicit `width`). |

- [gotcha] `state.tableText.trim() === ''` → neither `.app-version__table-text` nor `.app-version__separator` rendered; footer identical to 00243.
- User line is a local browser preference, editable in the settings panel (`006-ui-layer.md`, `ui/settingsModal.js`); the two fixed lines stay non-editable.

## Resize (corner handle)

Standard pattern to make any element in the app resizable (not exclusive to a component): `.resize-handle`, a standalone block (does not follow any other block's BEM, an exception similar to `.btn-*`), implemented in `ui/resizeHandle.js` (`attachResizeHandle`).

- Position: bottom-right corner of the element (`position: absolute; right: 0; bottom: 0`) — the host must be a positioned container (`position: relative/absolute`).
- Look: `18px` container with a `9px` diagonal grip (`::after` with gradients). Neutral gray by default, `var(--accent-blue)` + `transform: scale(1.15)` with a 150ms transition on `:hover`/`.resize-handle--active`. No own shadows or rounded corners.
- Cursor: `nwse-resize`, the same in all uses even if the element only resizes one axis (the same recognizable visual drag point across the app).
- Do not introduce a second resize pattern (side borders, multiple corners, etc.) without deciding it explicitly — reuse `ui/resizeHandle.js`.

### Second handle, top-left corner

`.resize-handle--tl`, applied alongside `.resize-handle` on the same host (same `ui/resizeHandle.js` mechanism, parameter `corner: 'tl'` — the same handle anchored to the opposite corner, not a second pattern).

- Any resizable element in the app can have this second handle.
- Differences from `.resize-handle`: position `left: 0; top: 0` instead of `right: 0; bottom: 0`. Same container/grip size, same `::after`, same look at rest/`:hover`/`.resize-handle--active`, same `nwse-resize` cursor (both corners on the same diagonal).
- When dragging it, the bottom-right corner stays fixed (the existing handle acts as an anchor). Whoever calls `attachResizeHandle` is responsible for also applying the position offset (`dx`/`dy` that `corner: 'tl'` exposes) to the host's model, not only the size.
- Hosts with a double handle (`.resize-handle` + `.resize-handle--tl`): floating panel `.component-panel`/`.resource-panel`; modal `.card-editor-modal` (visual editor — on starting the drag the JS pulls it out of the flexbox centering by switching it to `position: fixed` with its current geometry, so the corner opposite the handle has something to anchor to).

### Variant for a table column border

`.column-resize-handle`, applied alongside `.resize-handle` (same `ui/resizeHandle.js` mechanism, reused via `ui/tableColumnResize.js` — the same interaction oriented to a different border, not a second system).

- Differences from `.resize-handle`: occupies the full right border of the header cell (`top/bottom: 0`, not just the corner). Cursor `col-resize` instead of `nwse-resize`. Graphic: a thin vertical line (not a `::after` diagonal grip).
- Same neutral gray at rest and `var(--accent-blue)` on `:hover`/`.resize-handle--active`, same 150ms transition.

## Table header sticky on scroll (`position: sticky`)

First use of `position: sticky` in the project: `.component-list th`/`.resource-list th`/`.tag-list th` — `position: sticky; top: 0; z-index: 2;`, inside their own scrolling container (`.component-panel__body`/`.resource-panel__body`/`.tag-panel__body`, `overflow-y: auto`).

- Goal: the column header always visible when scrolling down a long list, instead of scrolling away with the rows.
- Condition for it to work: the header needs an opaque background (`background: var(--bg-subtle)`, all three already had it) — without it, row content would show through as it passes underneath.
- `z-index: 2` is local to the table itself (above the rows, which have no own `z-index`) — unrelated to the fixed `position: fixed` levels of the Layout section (panels, modal, menus).
- `position: sticky` is still a positioned element for the purpose of containing `position: absolute` descendants — `.column-resize-handle` keeps working with no changes over a `sticky` header, just like over a `relative` one.
- Any future table with its own internal scroll: reuse this same pattern (`sticky` header + opaque background + local `z-index`) instead of creating an ad-hoc one.

## Nested row under a parent block (`.component-list__row--member`, 00204)

First use of visual nesting inside a table row: a group's members are shown right below their group's row in `.component-list`, indented and with a different background — like a folder's expanded content. Since 00239 the group is collapsible (see "Collapsible group row" below): member rows render only while the group is expanded (or force-expanded by an active filter), collapsed by default.

- **Background**: `var(--accent-blue-light)` at rest (same token as "light background for interactive panels" of `001-tokens-visual.md` (Design tokens) — not a new ad-hoc value), `#ddebf9` on `:hover` (a darker tone of the same family), and the standard selection blue (`rgba(44,125,216,.15)`) if it is also selected — same priority criterion as any `.component-list__row--selected` row.
- **Indentation**: additional `padding-left` on `.component-list__id-cell` (not the whole row) — only the Id cell shifts, the rest of the columns (Orden, Tipo, Copia, Acciones) keep their normal table alignment.
- **No connector line or icon**: unlike a file tree with visual guides, here the indentation + the different background are enough to read as "content of the block above" — an explicit decision (confirmed on a mockup) to avoid adding visual noise.
- **Disabled field inside a nested row**: `.component-list__order-input:disabled` — background `var(--bg-subtle)`, text `var(--text-muted)`, `cursor: not-allowed` — same criterion as any disabled control in the app ("Buttons" above, "Disabled").
- Pattern scoped to this case for now — any other table that needs to nest rows under a parent can reuse it (background from the `--accent-blue-light` token, indentation only on the "identifying" cell, no connector line) instead of creating a new one.

## Collapsible group row (`.component-list__row--group`, 00239)

The `.component-list__row--group` row (a `groupId` with 2+ members) carries a collapse control at the start of its Id cell, before the group name. Members render only while expanded — see "Nested row under a parent block" above for the member-row look, unchanged.

- **Group name**: `.component-list__group-name` — `font-weight: 700`. Distinguishes the group row at a glance from a loose component row and from a member row (both normal weight).
- **Collapse triangle**: `.component-list__group-toggle` — a `<span>` holding a text glyph, `▸` collapsed / `▾` expanded. Same visual language as the `▾`/`▸` glyph in the three floating panels' headers (text character, gray, no background), one size up because it is a row-level control meant to be clicked.

  | Property | Value | Note |
  |---|---|---|
  | `display` | `inline-block` | — |
  | `width` | `16px` | fixed, so the name column starts aligned collapsed vs expanded |
  | `margin-right` | `5px` | gap to the group name |
  | `color` | `var(--text-muted)` (`#666666`) | at rest |
  | `font-size` | `0.9375rem` (15px) | vs ~13px for the panel-header triangle |
  | `line-height` | `1` | — |
  | `cursor` | `pointer` | — |
  | `user-select` | `none` | glyph not selectable as text |
  | `text-align` | `center` | glyph centered in the 16px box |

- `[hover]` on `.component-list__group-toggle` → `color: var(--accent-blue)` (`#2c7dd8`).
- `[gotcha]` click on the triangle carries `stopPropagation` — it toggles collapse and does NOT select the group; click anywhere else on the row still selects it and leaves collapse unchanged.
- Force-expanded state: with a text/column filter active, a matching group renders expanded regardless of its remembered state; the triangle shows `▾` and its click is inert while the filter is active.
- Mockups: [`design_componentes_grupo-plegado.html`](../../../changes/implemented/00239/design_componentes_grupo-plegado.html) / [`design_componentes_grupo-desplegado.html`](../../../changes/implemented/00239/design_componentes_grupo-desplegado.html).
- Reusable: any future collapsible/nested table row reuses this (bold identifier + `.component-list__group-toggle`-style text-glyph toggle, one size up from the panel-header triangle, `stopPropagation` on the toggle click) instead of a new pattern.
