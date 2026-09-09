# 003 — Modals, menus, tooltips, identification patterns

**Area**: Modals & menus

## Help icon (modal on click)

Standard pattern for contextual help anywhere in the app: `.help-icon`, a 16px circle with "?" (`ui/helpIcon.js`, `createHelpIcon({ text, html })`).

- Look: 16px circle, background `var(--text-muted)` (`var(--accent-blue)` + `box-shadow: 0 2px 5px rgba(44,125,216,.35)` on `:hover`, 150ms transition), "?" text in `var(--text-light)`, `font-size: 0.7rem`, `cursor: help`, no border.
- **Modal**: clicking the icon always opens a modal with the text/HTML, regardless of its length or format. Reuses `.modal-overlay`/`.modal` (no new pattern), "Cerrar" button (`.btn-cancel`), `z-index: 1000` (the same reserved for modal overlays).
- Any new contextual help: reuse `ui/helpIcon.js` instead of creating an ad-hoc modal.

## Error modal

Standard pattern to communicate any error in the app: `showErrorModal(title, message, detail)` (`ui/errorModal.js`).

- Reuses `.modal-overlay`/`.modal` (no new pattern), "Cerrar" button (`.btn-cancel`), `z-index: 1000`.
- Difference from the generic informational modal: the header (`.modal__header--error`) includes a circular alert icon (`.modal__error-icon`, "!" over `var(--error)`) next to the title.
- Additional technical message (e.g. a `JSON.parse` error): a monospace block (`.modal__error-detail`) below the main message.
- The app's single point for communicating errors: any new error uses `ui/errorModal.js`, never `ui/toast.js` or another ad-hoc notice — the toast is reserved for success confirmations/notices and the one documented exception below.
- [gotcha] one deliberate exception (change 00230): app **startup** communicates an unrecoverable `localStorage` saved state with `showToast(...)`, **not** `showErrorModal`. The condition is fully recoverable (the app boots with the embedded seed or default content regardless); a blocking modal to dismiss before working would be disproportionate. `showErrorModal` remains the standard for every other error (import failures, resource-in-use, unsupported file format).
  - Toast text (since 00250, a single message for every non-restorable save — unreadable, no components array, or another app version): `No se ha podido recuperar el estado guardado.`
  - No CSS/visual change — reuses the existing `.toast` component (see `006-ui-layer.md` → `ui/toast.js`, and `007-persistence-build.md` for the startup flow).
  - Any future error condition that is both expected and fully self-recoverable at startup follows this exception; a genuine in-session failure still uses `showErrorModal`.

## Success modal

Pattern to confirm, in a blocking way, a positive result that needs to stay visible until the user closes it (unlike `ui/toast.js`, for brief confirmations with no detail to review): `.modal__header--success` / `.modal__success-icon`, the green equivalent (`var(--success)`) of the error modal — same header layout, same `.modal-overlay`/`.modal`, same `z-index: 1000`.

- Example: `ui/batchUploadSummaryModal.js` (summary after uploading several resources/a folder to the gallery) — "✓" icon over `var(--success)`, a count of additions and, if applicable, a table of skipped items (table pattern of `ui/importReportModal.js`, same CSS as `.import-report-modal__table`).
- Any future success notice that must stay visible: reuse this pattern instead of creating an ad-hoc variant.

## Settings panel (`ui/settingsModal.js`, 00244)

`openSettingsModal()` — opened by `.mode-switcher__settings-btn` in the header control row (`002-componentes-layout.md`, "Header control row"). Standard modal skeleton, no special width: `.modal-overlay`/`.modal` (default `max-width: 500px`), `.modal__header` (title "Configuración"), `.modal__content`, `.modal__footer` with a single `.btn-cancel` "Cerrar". `z-index: 1000`. Close by "Cerrar" / click outside overlay / ESC (via `ui/globalShortcuts.js`, `.modal__footer .btn-cancel`) — same as every other modal.

`.modal__content` layout:

| Element | Class | Notes |
|---|---|---|
| Language field | `.modal__field` (`<label>` + `<select>`) | `<select>` options are fixed literals `Español` / `English` (not translated). Below it a `.modal__hint` note. |
| Separator | `.modal__separator` (new) | `border: none; border-top: 1px solid var(--border-neutral); margin: 0`. Thin divider between body blocks of a modal. |
| Version field | `.modal__field` (`<label>` + read-only value) | Read-only value `.settings-modal__version` (new): `font-size: 0.875rem; color: var(--text-muted)`. Shows `getFullAppTitle(getAppTitle())`. |

- Re-renders its own `.modal__header`/`.modal__content`/`.modal__footer` on `language:changed` (`../architecture/010-internationalization-i18n.md`) — the modal stays open, its text switches language in place.
- Reserved (unpainted) slot at the end of `.modal__content` for change 00231's changelog section.

## In-progress operation modal

Pattern to inform of a potentially slow, blocking operation, returning control to the player as soon as it finishes (change 00214): `ui/progressModal.js`, `runWithProgressModal(text, work)`.

- Unlike any other modal in the app, it **does not reuse `.modal`** — its own block `.progress-modal` (white background, `border-radius: var(--radius-lg)`, `box-shadow: var(--shadow-2)`, same `.modal-overlay`/`z-index: 1000`) with no header/content/footer: only a spinner (`.progress-modal__spinner`, `40px` circle, `4px` border in `var(--accent-blue-light)` with the top segment in `var(--accent-blue)`, continuous spin) and a brief text (`.progress-modal__text`) below, centered.
- **First and only use of `@keyframes` in the project**: `@keyframes progress-modal-spin` (continuous 360° rotation, `0.8s linear infinite`).
- **No button or manual close path** (neither click outside the overlay, nor ESC) — the app's only modal like this. It appears when the associated operation starts and closes on its own as soon as it finishes; it is not cancelable midway.
- `work` runs inside a double nested `requestAnimationFrame` after inserting the modal into the DOM, to guarantee the browser has completed a real paint cycle (with the spinner already visible) before the synchronous blocking of the real work starts — `setTimeout(fn, 0)` does not offer that guarantee (it only ensures order in the task queue, not that a repaint happened in between; bug 00218).
- First use: dragging a multi-selection of cards onto a deck in edit mode (`023-componente-mazo.md`) — text "Añadiendo N carta(s) al mazo…", `work` repositions the dragged cards and inserts them into the deck (the repositioning goes inside `work`, not before: it is the slowest part of the operation — bug 00219).
- Second use: confirming a file import (`ui/importConfirmModal.js`, "Importar" button, change 00222) — text "Importando…", `work` runs the ficha migration, `mergeImportedGame` and the loads (`loadComponents`/`loadResources`/`loadTags`/`loadGroups`) in `ui/editModeToggle.js`.
- Third use: grouping and ungrouping a selection in edit mode (`src/modes/edit/editMode.js`, change 00224) — text `"Agrupando N elemento(s)…"` / `"Desagrupando N elemento(s)…"` (singular `"1 elemento…"` when `N === 1`), `work` runs the `groupId` reassignment of the affected components plus the group-record create/remove (`addGroup`/`removeGroup`) and, on grouping, the block repositioning (`reorderGroupBlock`). The `count` and other state reads are computed before `work`. Applies at the three grouping/ungrouping entry points: context-menu "Agrupar" and "Desagrupar", and the "Desagrupar" button of the group row in the floating "Componentes" panel. No new variant of the pattern.
- Any future potentially slow, blocking operation: reuse this pattern instead of leaving the player with no notice.

## Startup splash / welcome screen

Pattern for the welcome screen shown once on every app load (change 00245): `ui/splashScreen.js`, `showSplashScreen()`. Sibling of "In-progress operation modal" — same "overlay with no buttons that closes itself" criterion, different purpose (a timed welcome, not an operation notice).

- **Does not reuse `.modal`/`.modal-overlay`.** Own blocks:

  | Block | Key style | Notes |
  |---|---|---|
  | `.splash-overlay` | `position: fixed; inset: 0; background-color: var(--bg-table); background-image: radial-gradient(circle, var(--bg-table-dot) 1.5px, transparent 1.5px); background-size: 32px 32px; z-index: 1300` | Game-table ground — the dotted table background (`001-tokens-visual.md`, "Table dotted background"), replicated from `.infinite-table` (no `background-position` — static overlay); the startup splash shows "over the table" (00248, was `background: #ffffff`). NOT the `rgba(0,0,0,0.5)` scrim of `.modal-overlay` — no dimming, no blur. `z-index: 1300` is the project's highest (above `.export-menu`/`.toast` at 1200/1100, `.context-menu` at 1050, `.modal-overlay` at 1000). Flexbox-centers `.splash-window`. |
  | `.splash-window` | `width: min(90vw, 520px); background: linear-gradient(135deg, #e3effb 0%, #eef1fb 45%, #f7ecf6 100%); border-radius: var(--radius-lg); box-shadow: var(--shadow-2); overflow: hidden` | No header, no footer, no buttons. `box-shadow` = elevation level 2 (`001-tokens-visual.md`). `overflow: hidden` clips the bottom bar to the radius. The `linear-gradient` is a deliberate exception to "no flashy gradients" (`004-naming-and-patterns.md`, see there). |
  | `.splash-window__logo` | `aspect-ratio: 1 / 1; background-size: contain; background-position: center; background-repeat: no-repeat; mask-image: radial-gradient(circle at 50% 50%, #000 55%, transparent 78%)` (with `-webkit-` prefix) | One of 4 logos via classes `.splash-window__logo--1..--4`, each `background-image: url(../resources/img/bgfactory-logo-color_<n>.webp)` (a `background-image`, never `<img>`, so `build.py` inlines it — see `../architecture/007-persistence-build.md`). `background-size: contain` = whole image, no crop/distort. `mask-image` fades the WebP's own light background into the window gradient — no visible rectangle. [gotcha] box is `1 / 1`, not `4 / 3` (00246): the 4 logos are near-square (884×876 … 1024×1048), so a `4 / 3` box left side gutters and the mask faded the box edge, not the painted logo edge → a visible white rectangle. Square box + circular mask makes the mask bite the real logo edge. |
  | `.splash-window__title` | `<p>`, `font-size: 2.25rem; font-weight: 700; color: var(--text-primary); line-height: 1.2` | Child `<sup>`: `font-size: 0.5em; font-weight: 600; color: var(--text-muted); margin-left: 0.15em; vertical-align: super`. Fixed brand string `"Board Game Factory" + "(2026)"`, not through `t()`. |
  | `.splash-window__link` (00247) | `<a>`, `margin-top: -0.5rem; font-size: 0.875rem; color: inherit; text-decoration: underline; cursor: pointer` | External link `href="https://github.com/yeyopepe/bgfactory" target="_blank" rel="noopener"`, text = fixed literal `"View on Github"` (not `t()`, see `005-text-links-and-external-links.md`). Between `.splash-window__title` and `.splash-window__progress`; centered by `.splash-window`'s `align-items: center`; `margin-top: -0.5rem` offsets part of the `gap: 1rem`. Only interactive element of the splash; clicking it opens a new tab and does NOT close the overlay. Follows `ui.link` — no `:hover`/`:visited`/`:active` variant. |
  | `.splash-window__progress` | `position: absolute; left/right: 0; bottom: 0; height: 4px; background: rgba(44, 125, 216, 0.15)` | Faint rail of `--accent-blue`, flush to the window's bottom edge, full width. |
  | `.splash-window__progress-fill` | `height: 100%; width: 100%; background: var(--accent-blue); transform-origin: left; animation: splash-progress-fill 3s linear forwards` | `@keyframes splash-progress-fill { from { transform: scaleX(0) } to { transform: scaleX(1) } }`. Duration `3s` (00247, was 5s). Animates `transform` (compositor-only, no layout) — same technique as `@keyframes progress-modal-spin`. [gotcha] two earlier attempts failed in the real browser (animate on first paint depends on a paint that `main.js`'s blocking bootstrap defers): a JS-class-toggled `transition: width` (00245) and a `@keyframes` on `width` (00246). `transform: scaleX` (00246 follow-up) starts reliably as soon as the element enters the render tree. Animates ALWAYS — not gated by `prefers-reduced-motion` (functional time indicator, same as `progress-modal-spin`). |

- **No manual close path** — no `click`/`keydown` listener on the overlay, no button (the `.splash-window__link` `<a>` is the sole exception, and it does not close it). `window.setTimeout(() => overlay.remove(), 3000)` (00247, was 5000), never cancelled: always lasts 3s exactly. [gotcha] the overlay lacks the `.modal-overlay` class, so `ui/globalShortcuts.js` (ESC/ENTER) never targets it.
- Fill animation is `@keyframes splash-progress-fill` (00246) — the 2nd `@keyframes` in the project, alongside `@keyframes progress-modal-spin` (`001-tokens-visual.md`, `004-naming-and-patterns.md`). Not gated by `prefers-reduced-motion` — the project has no `prefers-reduced-motion` handling anywhere.
- Visual reference: the approved mockups `previo-sdd/changes/implemented/00245/design_splash-screen*.html` (one per logo). Exact appearance and value rationale live there.
- Any future timed, non-dismissable welcome/intro overlay: reuse this pattern.

## Cursors

General convention: any clickable element shows `cursor: pointer` on hover, unless it already has one of these more specific cursors (priority over the generic one):

| Cursor | Use |
|---|---|
| `grab` / `grabbing` | Dragging the infinite table (`.infinite-table`) or a floating panel by its header (`.component-panel__header`, `.resource-panel__header`) |
| `move` | Moving a component on the table (`.text-box--movable`, `.board--movable`, `.dice--movable`) |
| `nwse-resize` | Resize handle (`.resize-handle`, `002-componentes-layout.md` §11) |
| `not-allowed` | Disabled button (`.btn-accept:disabled`) |
| `help` | Contextual help icon (`.help-icon`) |

- Reinforcement rule: `input[type="checkbox"]`, `input[type="radio"]`, `.modal__field select` carry an explicit `cursor: pointer` in `main.css`, not relying on the browser's default style.
- **Play mode**: components on the table always use one of 3 fixed cursors, never the default pointer.
  - `move`: the component can be dragged ("Bloqueado" checkbox unchecked).
  - `pointer`: it only responds to a click without being draggable (e.g. a "Bloqueado" die — it can always be rolled with a click even if it does not move).
  - `grab`/`grabbing`: when dragging the table itself.
  - When a component supports both interactions at once (an unlocked die: draggable and click-rollable; an unlocked card: draggable and click-flippable), `move` prevails.

## Component identifier label (edit mode)

Pattern to show "what" a component on the table is without opening it — distinct from the "Help icon" above: it is not contextual help, it is identification of the element under the cursor.

- **Play mode**: an own tooltip `.component-tooltip` (no longer the browser's native `title`), triggered on `:hover` over the whole component via the marker class `.component-tooltip-host`. Content: the custom text of `tooltipTexto` (with basic formatting — bold, italic, line breaks, lists — sanitized by `sanitizeBasicTooltipHtml`, `ui/componentRenderer.js`) if the component has that field filled; if empty, it falls back to the same `"<Type>: <id>"` as always (e.g. "Dado: 3fa8..."). Look shared with the generic floating tooltip: background `var(--bg-toolbar)`, text `var(--text-light)`, `box-shadow: var(--shadow-2)` — its own class (does not reuse `.help-icon`, see "Help icon" above, which opens a modal on click instead of showing a tooltip), because the trigger changes (the whole component, not a fixed 16px icon). Anchored on the `position: absolute` the component's root element already has set for its x/y placement on the table — that `position` is never overwritten to "anchor" the tooltip, it already serves as a positioning context.
- **Edit mode**: an own label `.component-id-label` overlaid on the component's top-left corner, within its area (not protruding above — avoids depending on free space above and getting hidden behind a header/fixed element near the table edge).
  - Same text/format as in play mode.
  - Background `var(--accent-blue-dark)`, text `var(--text-light)`, `font-size: 0.72rem`, `border-radius: var(--radius-sm)`, small shadow (`box-shadow: 0 2px 4px rgba(0,0,0,.25)`) to read "stuck" to the piece.
  - `pointer-events: none` — does not intercept drag/selection of the element beneath.
  - Visible only on `:hover` and `.<type>--selected` (the same moments as the blue dashed selection outline), never permanently.
  - Not clipped or wrapped over several lines if the id is longer than the component — it may protrude past its width (an editing aid, not final art).

## Component title (play mode)

A per-component configurable label, distinct from the previous one ("Component identifier label"): it does not identify "what" the component is, it is a free-content caption the user designs — it replaces (00212) the old fixed card-count label of `'mazo'`, generalized to the 8 types.

- `.component-title-label`, painted by `attachComponentTitle` (`ui/componentRenderer.js`) when `mostrarTitulo` (group override, like `mostrarTooltip`) is active and `tituloTexto` is non-empty — empty paints no node, unlike the tooltip ("Component identifier label") which falls back to the identifier.
- **Always visible** in play mode while active (does not depend on `:hover`, unlike `.component-tooltip`) — the same permanent-visibility criterion the old `.mazo-count-label` had.
- Same anchoring as `.mazo-count-label` had: outside the component's box, flush to its top-left corner (`top: -1.6rem; left: 2px`), `pointer-events: none`.
- Content: `tituloTexto` with basic sanitized formatting (the same `sanitizeBasicTooltipHtml` as the tooltip) and text variables resolved (`core/textVariables.js`, `../architecture/002-component-model.md`).
- Text/background/transparency color: `tituloColorTexto`/`tituloColorFondo`/`tituloFondoTransparencia`, applied **inline** by `attachComponentTitle` (`element.style.color`/`backgroundColor`), not as a fixed CSS token — a justified exception because it is per-component user-configurable data, not a design-system value (the same criterion already accepted for `colorFondo`/`colorFondoTransparencia` of a card's `TextBox`/`Forma`, via `hexToRgba`).
- Edited from the "Ayuda jugador" section of `ui/componentModal.js`: "Mostrar título de componente" checkbox + "Editar título de componente…" button that opens `ui/componentTitleModal.js` (sub-modal with no tabs, same pattern as `ui/boardPatternModal.js`: content, text color, background color, background transparency with a slider + synced numeric field — `.modal__opacity-value`, the same pattern already used in `ui/cardShapeModal.js`).

### Lock indicator (`.component-lock-badge`)

A badge sibling of `.component-id-label` in overlay criterion (component corner, outer container, `pointer-events: none`), with deliberate differences:

- Top-**right** corner (not left, to not overlap the identifier label).
- `18px` circle, background `rgba(0,0,0,.55)`, lock stroke in `var(--text-light)` (contrast over any component background/image) instead of a rectangular label with text.
- Visible **permanently** while `component.bloqueado` is active (not only `:hover`/selection).
- Edit mode only (`showLockIndicator`, `ui/componentRenderer.js`). In play mode the lock is not shown over the component, only via the context menu ("Component context menu").

### "Oculto" indicator (`.component-hidden-badge`)

Same visual pattern as `.component-lock-badge` (`18px` circle, background `rgba(0,0,0,.55)`, icon `var(--text-light)`, `pointer-events: none`, permanent while `component.oculto` is active, edit mode only via `showHiddenIndicator`), a crossed-eye icon instead of a lock.

- Anchored in the bottom-**right** corner (not the lock's top-right) so it coexists without overlapping when a component is both locked and hidden.

### Anchoring of the badges over the text box (`.text-box`)

`.text-box` has no fill box (see `../architecture/006-ui-layer.md`): the four badges (`.component-lock-badge`, `.component-hidden-badge`, `.component-copy-badge`, `.component-has-copies-badge`) would anchor to the corners of an invisible area larger than the glyphs and end up detached from the text.

- Own overrides in `main.css`, without touching the base rules (the rest of the types use them): `.text-box > .component-lock-badge` → `top: -0.55rem; right: -0.55rem`; `.text-box > .component-hidden-badge` → `bottom: -0.55rem; right: -0.55rem`; `.text-box > .component-copy-badge`, `.text-box > .component-has-copies-badge` → `bottom: -0.55rem; left: -0.55rem`.
- "Stuck outside the corner" criterion of the visible text, the same as `.component-title-label` (`top: -1.6rem`), instead of the corner of a box.
- Each badge's icon, color, size and logical corner are kept — only the anchoring offset changes for this type.
- The clipping of `.text-box`'s own text lives in an inner `div` (`../architecture/006-ui-layer.md`), so the outer container is free for label and badges like the rest of the types.

### "Copia" indicator (`.component-copy-badge`)

Same overlay pattern as lock/hidden (`18px` circle, icon `var(--text-light)`, `pointer-events: none`, permanent while `component.copyOf` is not `null`, edit mode only via `showCopyIndicator`), an icon of two overlapping squares.

- Two deliberate differences:
  - Background `var(--error)` instead of the neutral `rgba(0,0,0,.55)` of the other two — the first use of this token outside its error/destructive-action semantics (decided explicitly only for this indicator, does not reopen the convention for other uses).
  - Anchored in the bottom-**left** corner — the last of the four free (top-left: identifier label; top-right: lock; bottom-right: hidden).

### "Tiene copias" indicator (`.component-has-copies-badge`)

Same icon and bottom-left corner as `.component-copy-badge`, but with background `var(--accent-blue-dark)` — the same blue `.component-id-label` already uses (see "Component identifier label" above) — precisely to differ at a glance from the copy indicator (which stays red), instead of sharing its visual family. `pointer-events: none`, permanent while the component has linked copies, edit mode only via `showCopyIndicator`, in a pill shape to incorporate the copy count (e.g. "(2)") next to the icon.

- Anchored in the bottom-**left** corner, exactly like `.component-copy-badge` — mutually exclusive (an original component never has its own `copyOf`, so it never shows both badges at once).
- Fixed height `18px` (matching the other badges), variable width by the number's digit count (padding and `border-radius: 9px` for the rounded shape).
- Same icon size as the other badges (`14px` in this pill, `18px` in the copy circle), same inner-spacing criterion (`gap: 3px` between icon and number).

### Selection outline and label in red for copies

Besides the previous badge: when a component with `copyOf` non-null is on `:hover`/`.<type>--selected`, the dashed selection outline and the `.component-id-label` background (normally `var(--accent-blue)`/`var(--accent-blue-dark)`) are painted `var(--error)` — the same tone as the copy indicator, reinforcing at a glance that the element is a copy.

- Activated with the class `is-copy` (`ui/componentRenderer.js`, alongside the type's own `--selectable` class, when `showCopyIndicator` is active and `component.copyOf` is not `null`) — a simple class with no block prefix, same criterion as `.grabbing`/`.active`/`.lifted` (`004-naming-and-patterns.md`, Class naming), a cross-cutting state over the 7 component types.
- The 6 per-type `--selectable`/`--selected` blocks (`.text-box`, `.board`, `.tablero-personalizado`, `.dice`, `.document-viewer`, `.carta` — also covers `mazo`, which reuses its classes) each include the `.is-copy`-qualified variant.

### Action buttons overlaid on an image (`.resource-modal__zoom-btn`)

An *interactive* variant of this section's same visual language (background `rgba(0,0,0,.55)`, icon `stroke="currentColor"` in `var(--text-light)`) for when what is overlaid is a real action button, not a passive indicator — zoom controls over the preview of an Image resource (`ui/resourceModal.js`).

- Deliberately does **not** use `.align-group`/`.align-group__btn` ("Group of icon-only buttons", meant for selectable options with an `active` state over a form background): these buttons are momentary actions with no "active" state and need guaranteed contrast over an arbitrary content image, not a neutral modal background.
- `32px` square, `border-radius: var(--radius-sm)`, hover `rgba(0,0,0,.72)`, `title`/`aria-label` as the only accessible label (icon-only button, §9 in `002-componentes-layout.md`).
- Any future action control overlaid on an arbitrary image/visual content: reuse this criterion instead of `.align-group` or an ad-hoc overlay.

## Wide modals (exception to `max-width: 500px`)

`.modal` uses `max-width: 500px` by default. When the content needs more space (several columns, long lists), the modal adds a second own block class with its own `max-width`, instead of overriding the default value ad-hoc.

| Class | Modal / file | Width |
|---|---|---|
| `.component-editor-modal` | Component editing (`ui/componentModal.js`, `openComponentModal`) | `clamp()` with `75vw`, bounded between `400px` and `min(1000px, 90vw)` — recomputed dynamically on window resize with no JS |
| `.card-editor-modal` | Visual editor (`ui/visualEditorModal.js`), of one or two faces by type (`'carta'` two faces, `'tableroPersonalizado'` one) | `width: fit-content; max-width: min(1500px, 95vw)`; `position: relative` (anchors its two `.resize-handle`, §11 of `002-componentes-layout.md`). Fits the content because the width varies by the active card proportion. Modifier `.card-editor-modal--maximized` (header button "Modal maximize/restore button"): `width: 90vw; max-width: 90vw; height: 90vh; max-height: 90vh` (00235; `width: 90vw` added 00240). [gotcha] both `width` and `height` are fixed values, not just `max-*` — the modal inherits `width: fit-content` from `.card-editor-modal`, so with `max-width` alone it stays content-sized (`.modal-overlay` centers, does not stretch) and grows only in whichever dimension does carry a fixed value (bug 00240: maximize only enlarged height, not width — was masked before 00237 by the `CANVAS_MAX_SIDE * 3` ceiling indirectly pushing the `fit-content` width to ~1140px). Manual resize with a double corner handle (`.resize-handle` + `.resize-handle--tl` over the modal itself): the JS switches it to `position: fixed` with inline `width`/`height` and cancels `max-width`/`max-height` while that size lasts; `.card-editor-modal > .resize-handle { z-index: 1 }` so the toolbar does not cover it. Canvas sizing when maximized or manually resized (00235, refined 00237): `.card-editor-modal .modal__content { display: flex; flex-direction: column; min-height: 0 }` + `.card-editor-modal__faces { flex: 1 1 auto; align-items: center; justify-content: center }` — the faces row fills the leftover vertical space of `.modal__content`; JS (`getEffectiveCanvasMaxSide` / `getEditorWorkArea`, see `../architecture/006-ui-layer.md`) scales each face's canvas to the largest size fitting BOTH the per-face width and the height of the real interior work area, keeping the design aspect ratio, so `align-items`/`justify-content: center` leave it centered in the slack. [gotcha] `min-height: 0` on `.card-editor-modal .modal__content` is load-bearing (00237): without it the inherited `overflow-y: auto` stops `.card-editor-modal__faces` from actually stretching, so `align-items: center` has no slack and the canvas sits pinned to the top with all the leftover space below. [gotcha] 00237 also removed the `CANVAS_MAX_SIDE * 3` ceiling from `getEffectiveCanvasMaxSide()`: a width-bound landscape design (`'tableroPersonalizado'`) now fills the real available width of a maximized window instead of stopping at ~1140px. Because `getEditorWorkArea()` measures a `flex-wrap` actions row of the *previous* render, `renderFaces()` runs one `requestAnimationFrame` convergence pass in maximized/manual state (re-measures at the new width, re-renders once if the canvas side differs `> 1` px — bounded, not a loop; detail in `../architecture/006-ui-layer.md`). `overflow-y: auto` (from `.modal__content`) is the fallback when the window shrinks below the `CANVAS_MIN_SIDE`-floored canvas. The editor faces never stack: `.card-editor-modal__faces { flex-wrap: nowrap }` + the per-face canvas bounded by the available width (00233/00235). Neither the maximized nor the manual size persists between openings; also "Restaurar" ("Modal maximize/restore button") discards the manual size and returns to the default `fit-content` |
| `.image-adjust-modal--large` | Image-adjust window of one or two faces (`ui/imageAdjustModal.js`) | `width: fit-content; max-width: min(1500px, 95vw)` — same criterion as `.card-editor-modal`, the combined width of preview boxes varies by faces shown |
| `.element-selection-modal` | Export/import with selection | `max-width: 640px` |
| `.import-report-modal` | Import report with a table (`ui/importReportModal.js`); also reused as-is by `ui/styleClipboardErrorModal.js` (error header, table of broken style-clipboard references). Adds the class `.error-cell` (`color: var(--error)`) to the error-reason cell in `.import-report-modal__table`, reusable by any table that highlights an error cell | `max-width: 640px` |
| `.resource-modal--image` | Editing an Image resource (`ui/resourceModal.js`) — more space for the enlarged preview with zoom/pan. Only if the resource is an Image; the Typeface modal uses the generic `.modal` | `width: fit-content; max-width: min(800px, 95vw)` |
| `.board-image-modal` | Background image gallery for a simple board/card/custom board (`ui/boardImageModal.js`). Thumbnail `.board-image-modal__thumb` `140px`, grid `.board-image-modal__gallery` `minmax(160px, 1fr)` | `max-width: min(900px, 90vw)` — fixed, the content is a grid of thumbnails that reflows on its own |

- Any new modal that needs more width: an own block class added to `modal.className` (e.g. `'modal my-modal'`), with its `max-width` (or `width: fit-content` + a cap if the content is of variable width) in `main.css` — never inline `style="max-width:…"`.

## Modal maximize/restore button

First use of this pattern: `.card-editor-modal__maximize-btn` — an own block of that modal (not a standalone `.btn-*` exception, since it hangs off `.card-editor-modal`).

- Placed in `.modal__header`, between the title and the `.help-icon` if there is one.
- Toggles between two local SVG icons (`createMaximizeIcon`/`createRestoreIcon` in `ui/visualEditorModal.js`) by a boolean state local to that opening of the modal, with no persistence between uses.
- `margin-left: auto` — it ends up, together with the `.help-icon` that follows it, stuck to the right edge of the header (title only on the left, available gap between the two).
- At rest: background `var(--bg-subtle)`, hover `var(--bg-hover)`, `border-radius: var(--radius-sm)`, transition `background var(--transition-fast)`.
- No text: exposes `title`/`aria-label` updated on each toggle ("Maximizar"/"Restaurar tamaño").
- The switch adds/removes the size modifier class ("Wide modals") on `.modal` — it never closes the modal (that depends only on its footer "Cancelar"/"Aceptar" buttons).
- Independent of the manual resize with corner handles (§11 of `002-componentes-layout.md`), when the modal supports it (`.card-editor-modal`): maximizing clears the manual-resize inline geometry styles (without deleting the stored manual size) and applies the class; **restoring also clears those inline styles and discards the manual size — it always returns to the modal's default size (`width: fit-content` centered), never to the manual size that might have been set with the handles** (00233). The button clears the inline styles before applying/removing the class, so `.card-editor-modal--maximized` wins without `!important`.
- Any future modal that needs maximize/restore: reuse this pattern (button, position, icons, no persistence).

## Grouped selection list (checklist)

Pattern to choose a subset of a collection organized by categories (`ui/elementSelectionModal.js`, used by the export/import-with-selection modals):

- A block per category (`.element-selection-group`), a header combining a "select the whole block" checkbox + the category title (`.element-selection-group__select-all`, background `var(--bg-subtle)`, same tone as the `.component-list` header).
- Below, a list of individual checks (`.element-selection-group__list`, own vertical scroll if it exceeds `12rem` in height; each item `.element-selection-group__item` hover `var(--bg-hover)`, same criterion as a `.component-list` row).
- A block with no elements is not painted (an empty category is not shown).
- Any future multi-selection organized in categories: reuse this pattern — same criterion as `.resize-handle` or `.help-icon`.

## Sections inside property tabs

Pattern to visually group several related fields inside a `ui/componentModal.js` tab (or an edit sub-modal) when the group grows enough to need separation, without justifying its own tab/sub-modal.

- A `.modal__section` block, implemented with `<fieldset class="modal__section">`.
  - Framed: `border: 1px solid var(--border-neutral)` (the same neutral gray as any thin border, no new color), `border-radius: var(--radius-sm)`.
  - `margin-top: 1rem` from the previous field (same spacing criterion as `001-tokens-visual.md`, Spacing), `padding: 1rem` inside.
  - Static visual grouping, always visible inside the already-active tab — it introduces no tabs, accordion or collapse.
- Title in `<legend class="modal__section-title">` (the `<legend>` itself cuts the `fieldset`'s top border, with no separate line/pseudo-element), color `var(--section-accent)`, uppercase — the only use of that tone in the app (see `001-tokens-visual.md`, Color dedicated to the `.modal__section` title).
- Two title kinds, by whether the group represents an entire enable/disable configuration:
  - **Merely informational** (`.modal__section-title`): text only, no control. The fields inside are always active.
  - **En/disabler** (`.modal__section-title--toggle`): same `<legend>`, preceded by a checkbox forming a row (`display:flex; align-items:center; gap:0.5rem`, like `.modal__field--checkbox` but acting as a section title). Controls whether the whole section is active: unchecked, the rest of the fields (`.modal__section--disabled`) are shown disabled (`opacity: 0.5; pointer-events: none`, plus `disabled` on each input from JS) without losing already-entered values; checked, they are enabled again as they were.
- `.modal__section--untitled`: same `<fieldset>`/CSS with no `<legend>`, for a group that needs the same frame but has no name of its own.

### Number + button that opens a separate modal

Pattern for potentially long read-only lists inside a section of the properties modal: a numeric counter (e.g. "5") followed by a button that opens an independent modal with the full list, avoiding letting the section's height get out of hand if there are many elements.

- A `.{block}-summary` block (e.g. `.component-copies-summary`) with a read row inside (`.{block}-summary__row` with `.{block}-summary__label` on the left and `.{block}-summary__value` on the right, same visual criterion as `.context-menu__info-label`/`__info-value` of "Component context menu" without literally reusing those classes if the block lives outside `.context-menu`), followed by a full-width button (`.{block}-summary__button` with `width: 100%`).
- The button reuses `.btn-cancel` — the same visual exception as the "Ver contenido del mazo" button of the deck edit modal ("Wide modals").
- The modal the button opens (`.{block}-modal`, e.g. `.component-copies-modal`) follows the standard `.modal` skeleton with a header, hint and content, with no special `max-width` needed (the default width `500px` is enough for id lists).
- First use: `.component-copies-summary` → `.component-copies-modal` (`ui/componentModal.js`, "Copias" tab + `ui/componentCopiesModal.js`) for the list of copies linked to an Original. That block now lives in its own "Copias" tab of the properties modal (no longer inside the "Generales" tab). The listing modal adds a status column (`.component-copies-modal__sync--yes/--no`) to differentiate synced from unsynced copies in a row (same status pattern for future read-only lists with per-element status).
- Section-to-own-tab promotion (`ui/componentModal.js`): a `fieldset.modal__section` outgrowing the "Generales" tab is moved to a dedicated tab of its own — no new CSS/markup, same `.modal__tab`/`switchTab` and same `fieldset.modal__section`. Instances: "Copias" (see above); "Interacciones programadas" → "Interacciones" tab (00251, i18n `componentModal.tab.interacciones`), placed before "Copias" (tab order `general`/`visual`/`specific`/`interacciones`/`copias`). Default active tab stays "Generales".
- Any potentially long read-only list inside a section: reuse this pattern instead of unrolling it inline.

### Uses of the pattern

- `ui/cardTextBoxModal.js` (card text box): "Borde" (en/disabler: "Activar borde" checkbox + color/thickness/line type), "Fondo" (informational: background color + a "Transparente" field checkbox — a field control, not a section one).
- Section order in the "Apariencia" tab (00253, extended by 00255): a reorder block after `renderSpecificTab()` forces the fixed order **Estilo → Forma → Borde → Extrusión → Efecto** for the managed sections, identifying them by `<legend>` text; "Tamaño" stays first, outside that group; unmanaged sections (`'tableroSimple'` background, `'mazo'` "Cartas reveladas"/"Imagen") keep their spot. This replaced the earlier per-type `insertBefore(section, extrusionSection)` (00252).
- `ui/componentModal.js`, type `'tableroSimple'`: "Efecto" (informational, i18n `common.visual`: "Biselado en el borde" checkbox field checked by default, see `004-naming-and-patterns.md` (What NOT to do) and "Bevel/depth" below; "Sombra" checkbox field checked by default, see `001-tokens-visual.md` (Elevation)) — last of the ordered group, after "Extrusión"; "Borde" (en/disabler: "Activar borde" checkbox + color/thickness 1–20, same pattern as `TextBox`/`Shape` — a new or old board starts with the checkbox checked) — before "Extrusión" in the ordered group; and untitled (`.modal__section--untitled`) the "Fondo" field in the "Específicas" tab (a selector with three options: "Color y patrón"/"Imagen"/"Color").
- `ui/componentModal.js`, type `'tableroPersonalizado'`: "Efecto" (informational, same "Biselado en el borde" and "Sombra" fields as `'tableroSimple'`, same position in the ordered group), followed in the "Específicas" tab by the "Editar diseño del tablero" button (no own `.modal__section`, a loose field).
- `ui/componentModal.js`, type `'texto'`: "Efecto" (informational, i18n `common.visual`: "Tamaño de fuente", "Color del texto", "Color de fondo" with a "Transparente" field checkbox) — last of the ordered group, after "Extrusión" ("Borde y extrusión" label for this type).
- `ui/boardPatternModal.js` ("Configurar fondo — Color y patrón"): two informational sections — "Configuración" (cell shape; Rows and Columns in the same row, row pattern of `004-naming-and-patterns.md`, Component patterns) and "Color" (background color with a "Transparente" checkbox, pattern color/thickness in the same row).
- `ui/boardColorModal.js` ("Configurar fondo — Color"): a third background type for `tableroSimple` alongside "Imagen"/"Color y patrón" — a single color field + a "Transparente" checkbox, no `.modal__section` (a single field).
- `ui/cardShapeModal.js` (card geometric shape): "Borde" (en/disabler: "Activar borde" checkbox + color/thickness 1–20, no difference from `TextBox` — a new shape starts with the checkbox checked), "Fondo" (informational, same criterion as `TextBox`).
- `ui/componentModal.js`, type `'mazo'`: "Forma" (informational: Forma, Orientación) lives in the **"Apariencia"** tab (in the ordered group, between "Estilo" and "Borde"); "Cartas reveladas" (informational: Disposición carta revelada, Texto carta revelada, Revelar carta) and "Imagen" (informational: preview + Elegir/Ajustar/Quitar image) live in the **"Específicas"** tab.

Any future group of fields with this need: reuse `.modal__section`/`.modal__section--untitled` with the corresponding title kind, instead of creating an ad-hoc frame or activation checkbox.

### Internal scroll zone inside a section

When a `.modal__section`'s content is a potentially long list (one per element of a collection that can grow, unlike a fixed group of fields like "Borde"/"Fondo"):

- The list is wrapped in its own container with `max-height` + `overflow-y: auto` — an approximate cap by number of visible rows, not an exact dynamic computation (same criterion as `.element-selection-group__list`, "Grouped selection list", cap `12rem`).
- The rest of the section (title, action rows like "+ Crear...") stays **outside** that container, so it does not scroll with the list.
- First use: `.tag-checkbox-list__scroll` in the "Etiquetas" section of `ui/componentModal.js` — cap `6.5rem` (~3 checkbox rows), the "+ Crear nueva etiqueta…" row outside the scroll zone, as a direct child of `.modal__section`, always visible.
- Any future section with this need: reuse this pattern (a scroll container separated from a fixed action row) instead of applying `max-height`/`overflow-y` to the whole section.

## Actions dropdown menu

Pattern to offer several variants of the same action from a single button, when they fit neither as modal options nor as separate buttons (`ui/resourceList.js`, `createAddMenu`):

- A button (`.resource-add__button`, same look as the button it replaces) unfolds a floating panel (`.resource-add__menu`, `position: absolute`, background `var(--accent-blue-light)`, `border: 1px solid rgba(44, 125, 216, 0.25)`, `border-radius: var(--radius-sm)`, `box-shadow: var(--shadow-2)` — level 2) with a list of items (`.resource-add__item`, separated by `border-bottom: 1px solid rgba(44, 125, 216, 0.25)`).
- Exception to the standard neutral hover: hover `var(--accent-blue)` (not `var(--bg-hover)`), the label and auxiliary note turn `var(--text-light)` in that state.
- Each item can carry a label (`.resource-add__item-label`, `color: var(--text-primary)` at rest) + an auxiliary note below (`.resource-add__hint`, `font-size: 0.75rem`, `color: var(--text-muted)`) to clarify that option's limitation.
- Opens/closes on clicking the button, also closes on a click outside or on choosing an item — the same close criterion as the modals (`.modal-overlay`'s `overlay`).
- Distinct from a modal (does not block the rest of the screen, no `overlay`) and from a native `<select>` (each item can carry additional content).
- Any similar future dropdown menu: reuse this pattern.

### Other uses of the pattern

- `ui/visualEditorModal.js`: the same classes (`resource-add`/`resource-add__button`/`resource-add__menu`/`resource-add__item`/`resource-add__item-label`) for the "Añadir elemento" button of each face of the card editor (Background image / Text box / Geometric shape) — confirms the pattern is domain-agnostic.
- `ui/columnHeaderMenu.js` (`openColumnHeaderMenu`): the same visual language (background `var(--accent-blue-light)`, border `rgba(44, 125, 216, 0.25)`, `border-radius: var(--radius-sm)`, `box-shadow: var(--shadow-2)`, hover `var(--accent-blue)`/text `var(--text-light)`) for the sort/filter menu on clicking a column name in the Componentes/Recursos/Etiquetas panels (see `../architecture/005-modes.md`), with its own classes (`.column-header-menu`/`.column-header-menu__item`/`.column-header-menu__separator`/`.column-header-menu__filter`).
  - Different content: two toggle-style sort rows (`.column-header-menu__item--active` on the active one, same "active option" convention as "Group of icon-only buttons" — background `var(--accent-blue)`, text `var(--text-light)`) and, if the column is filterable, a block with a native `<select>`.
  - **Positioning variant**: `position: fixed` inserted in `document.body`, computing the position from the clicked `<th>`'s `getBoundingClientRect()` and readjusting so it does not leave the window — the same mechanism as `.context-menu` ("Component context menu"), because its anchor point lives inside containers with `overflow: auto`/`overflow: hidden` that would clip a `position: absolute`.
  - Same `z-index` as `.context-menu` (`1050`) for the same reason: it can open with a modal already visible behind.
  - Any interactive column always shows an indicator next to its name (`.column-header-menu__indicator`, SVG icon `currentColor`), even with the menu closed and nothing applied yet.
  - Two color states: `var(--text-muted)` by default ("available but not active"), `var(--accent-blue)` (modifier `.column-header-menu__indicator--active`) when the column has a sort and/or filter applied.
- `.card-editor-modal__shape` (`ui/visualEditorModal.js`, card-editor geometric shape): a block sibling of `.card-editor-modal__textbox` — same `move` cursor, same blue dashed outline on `:hover`, same continuous `--selected` outline on selection, same `.resize-handle` in its bottom-right corner.
  - No own typeface/text content: only `border-radius` (`50%` if circular/elliptical, `0` if square), `background-color`, `border` (simple line, without the bevel reserved for `'tableroSimple'`/`'dado'` — visible only if `bordeActivo` is active).
  - Free resize on both axes with Shift forcing 1:1 (circular/elliptical type) reuses the generic behavior of `ui/resizeHandle.js` for `axis: 'both'` (the same as the "Circular" proportion of `'carta'`), with no own proportion `clamp`.

## Component context menu

Pattern for the right-click menu over a component on the table (`ui/contextMenu.js`, `openContextMenu`): reuses "Actions dropdown menu"'s visual language for `.resource-add__menu` — background `var(--accent-blue-light)`, border `rgba(44, 125, 216, 0.25)`, `border-radius: var(--radius-sm)`, `box-shadow: var(--shadow-2)`, hover `var(--accent-blue)`/text `var(--text-light)` — with its own classes (`.context-menu`/`.context-menu__item`/`.context-menu__separator`) instead of `.resource-add__*`, since it does not hang off a button but is positioned next to the cursor (`position: fixed`, readjusted after insertion so it does not leave the window).

- Each row: icon (`.context-menu__item-icon`, 18×18px) + text (`.context-menu__item-label`), separated by `border-bottom` as in `.resource-add__item`.
- Separator between the general and specific sections (`.context-menu__separator`, only if there is any specific action): a simple `border-top` of the same tone.
- `z-index: 1050` (in front of the modal overlay `1000` — this menu too can open with a modal already visible behind, e.g. the card editor).

### Menu sections

The menu organizes its content in up to five possible sections, in this order:

0. Read-only description line, before any other section.
1. General actions section, wired in code (today: Bloquear/Desbloquear in play mode; Clonar/Copiar/Eliminar in edit mode).
2. Per-component-type specific section (`specificItems` — e.g. "Barajar"/"Ver contenido..." for a deck, "Meter en mazo..." for a card if there is any deck in the game; same `.context-menu__item` rows with an icon as the general section).
3. Fixed read-only section (`interactionItems`) that shows what each kind of click does on that component, separated from the previous ones by its own `.context-menu__separator`.
4. Row with an inline `<select>` (see below).

The informational section (3) does not follow the interactive pattern (icon + blue hover):

- Small/uppercase/faint header (`.context-menu__info-title`, `font-size: 0.75rem`, `color: var(--text-muted)`, `text-transform: uppercase`).
- Read-only rows (`.context-menu__info-row`, no hover or `cursor: pointer`, flex with a label on the left and a value on the right), `.context-menu__info-label` + `.context-menu__info-value` (`0.8125rem`, smaller than action rows).
- Modifier `.context-menu__info-value--none` for "Ninguno" values (italic + slight opacity).
- The whole block in a `.context-menu__info` container with `cursor: default`.

### Menu in edit mode and the row with an inline `<select>`

`ui/contextMenu.js` is reused in edit mode (right click on a table element), with a general Clonar/Copiar/Eliminar section (same rows with an icon) and a specific section with a single "Añadir a etiqueta" row.

- That row introduces a fourth content kind, distinct from a direct-click action: a `.context-menu__select-row` block (`cursor: default`, no hover, separated by `border-bottom` like `.context-menu__item`) with a label on top (`.context-menu__select-row-label`) and a full-width native `<select>` below — same visual criterion as `.column-header-menu__filter`/`.column-header-menu__filter-label`/`.column-header-menu__filter select` ("Actions dropdown menu").
- Choosing a real option (not the "Elegir etiqueta…" placeholder) runs the action and closes the menu, like clicking any action row.
- With no options available (e.g. "Añadir a etiqueta" with no tags created): the `<select>` is disabled (same `:disabled` as the rest of the controls — background `var(--border-neutral)`, `cursor: not-allowed`), shows "Sin etiquetas" instead of the usual placeholder.

### Description line

`description` identifies the component the menu was opened over, computed at open time from its current state: the very first row, with its own `.context-menu__separator` always present between it and the rest of the menu (unlike the separator between the general/specific sections, this one does not depend on there being content after it).

- A `.context-menu__description` block (`cursor: default`, no hover or action, column layout) with two stacked lines, distinct from the label/value row pattern of `.context-menu__info-row`:
  - `.context-menu__description-main`: text "Type: id" (same `"<Type>: <id>"` format as "Component identifier label"), `font-weight: 600`, `color: var(--text-primary)`.
  - `.context-menu__description-extra` (only if applicable): a differentiating property by component type (e.g. a die's number of faces, a board's "AAxBB" size, a deck's number of cards), `font-size: 0.75rem`, `color: var(--text-muted)`.
- Does not reuse `.context-menu__info-*` because that family is meant for label/value pairs in a row, not this block of two stacked lines.

Any future context menu: reuse this pattern instead of creating an ad-hoc one — the same criterion as `.resize-handle`, `.help-icon` or `.resource-add__menu`.

## Copy/Paste a component's style

Pattern to copy a component's visual style and paste it onto another of the same type (`ui/componentModal.js` + `core/styleClipboard.js`, implemented today only for `'carta'`): a general app convention — if extended to other types, it must look and behave the same, changing only the checklist's element list.

- **An own section in the configuration modal**: inside the type's specific tab, `fieldset.modal__section` "Estilo de \<type\>" (merely informational variant, "Sections inside property tabs") with a two-button row `.style-actions-row` (`display: flex; gap: 0.5rem`, each button `.btn-cancel` with `flex: 1`) — "Copiar estilo" and "Pegar estilo" — and a `p.modal__hint` below (`font-size: 0.75rem`, `color: var(--text-muted)`) explaining what is copied/pasted.
  - "Pegar estilo" is shown `disabled` (with a `title` indicating the reason) while nothing has been copied in the session — `.btn-cancel:disabled` the same generic disabled criterion (`opacity: 0.5; cursor: not-allowed`, no `transform` on hover).
- **Selection modal on copy**: a single fixed group (not a dynamic collection) with the BEM classes of "Grouped selection list" (`element-selection-group`/`__select-all`/`__list`/`__item`), all items checked by default, each with an optional auxiliary note on the right (`.element-selection-group__item-hint`, `font-size: 0.75rem`, `color: var(--text-muted)`, `margin-left: auto` — same criterion as `.resource-add__hint`) with that element's current value. The confirm button is disabled if no item remains checked.
- **Copy confirmation**: `ui/toast.js` ("Success modal" — not a modal, a brief confirmation with no detail to review) with the text "Estilo copiado".
- **Paste error**: if something copied is no longer valid in the project (a reference to a deleted tag/resource), an error modal with a standard header (`modal__header--error`/`modal__error-icon`, "Error modal") and detail in a table — reusing **as-is, with no own CSS**, `.import-report-modal`/`.import-report-modal__table` ("Wide modals"), columns by domain (for "Copiar/Pegar estilo": Elemento/Referencia/Detalle).
  - All-or-nothing paste: any issue, and no change is applied to the destination.
  - Only a "Cerrar" button (no alternative "continue anyway" action).

Any future component type that incorporates "Copiar/Pegar estilo": reuse this same pattern (section, checklist, toast, error modal), changing only which elements appear in the checklist.

## Group of icon-only buttons: single option or combinable switches

A shared pattern (`.align-group`/`.align-group__btn`, `ui/cardTextBoxModal.js`) to represent several icon options instead of text, in two variants with the same markup and the same visual states.

- Container `.align-group` (`display:flex; gap:0.25rem`) with one `.align-group__btn` per option (square button `32×32px`, centered SVG icon `stroke="currentColor"`, `title`/`aria-label` as an accessible label).
- At rest: background `var(--bg-subtle)`. Hover: `var(--bg-hover)`. Active option (`.align-group__btn.active`): background `var(--accent-blue)`, text/icon `var(--text-light)` — same visual language as `.modal__tab.active`, adapted to an icon-only square button.
- **Single option** (horizontal/vertical alignment of the text within a card's `TextBox`): clicking a button updates the associated data and recomputes `active` on all buttons of the group — never more than one option active at a time.
- **Independent, combinable switches** ("Text style": Bold/Italic/Underline of a card's `TextBox`): each button represents its own boolean and toggles only its own `active` class, without affecting the others — any number can be active at once, including none.
- Distinct from a native `<select>` (the active option highlighted without unfolding anything) and from a checklist ("Grouped selection list", meant for longer dynamic lists, not 2-3 fixed icons).
- Any future icon-only group: reuse this pattern — the same criterion as `.resize-handle`, `.help-icon` or `.resource-add__menu`.

## Editable header title

Pattern for the only in-place editable text outside a modal/form (`ui/appTitle.js`): the header `<h1>`, whose free text (everything but the version, never editable) can be edited at any time in edit mode.

- **`.app-title--hoverable`** (edit mode, not editing): a modifier on the `h1` — `cursor: pointer` (convention of "Cursors", no own specific cursor), a pencil icon (`.app-title__pencil`, inline SVG `stroke="currentColor"`) hidden by default (`opacity: 0`), shown only on `:hover` (`opacity: 0.85`, transition `var(--transition-fast)`) — never permanently visible (unlike the lock/hidden badges of "Component identifier label").
- **`.app-title--editing`** (edit mode, editing): replaces the text with `.app-title__input` — an `<input type="text">` with custom styling (not the generic form-field one, to keep the `h1`'s own size/typography: `font: inherit`, background `rgba(255,255,255,0.08)` over the header's dark gradient, border `2px solid var(--accent-blue)`, text `var(--text-light)`) — followed by `.app-title__version`, the version in `var(--text-muted)`, no interaction, outside the `<input>` itself.
- In play mode, or edit mode with no active hover/editing: the `h1` carries neither class — it behaves as the generic `h1` (`001-tokens-visual.md`, Typography), with no special cursor or icon.

Any future title/label that needs in-place editing directly over the visible element (instead of opening a modal): reuse this criterion (discreet hover with an icon, replacement with a context-tailored `<input>`, confirmation with blur/Enter).

## Slider with magnetic marks

First use of this pattern in the project: there was no precedent of `<datalist>` or reference marks over an `<input type="range">` before `ui/rotationSlider.js` (-360° to 360° rotation control of `ui/imageAdjustModal.js`, `ui/cardShapeModal.js`, `ui/cardTextBoxModal.js` — see `../architecture/006-ui-layer.md`). The value's sign indicates the rotation direction (negative counterclockwise, positive clockwise); the track center (0°) is not at the end but roughly in the middle.

- A `.rotation-field` block (`div.modal__field.rotation-field`) with: `<label>`, a track (`.rotation-slider__track`) overlaying the `<input type="range">` and the visual marks (`.rotation-slider__marks` > `.rotation-slider__mark`, one per reference value), numeric labels below (`.rotation-slider__labels`) and, to the right of the track, a synced numeric field (`.rotation-slider__value` > `<input type="text">` + `<span>`) — the same slider↔text pattern as "Zoom"/"Transparencia" of `ui/imageAdjustModal.js`.
- Active mark: `.rotation-slider__mark--active` over the mark closest to the current value, within the magnet threshold.
- **The magnet threshold as a module constant**, not a "magic" value scattered through the code: `ROTATION_SNAP_THRESHOLD_DEG` in `ui/rotationSlider.js`. When dragging the slider, if the raw value falls within that distance of a mark, it is forced to the mark's exact value before propagating — it is not just a visual guide, it adjusts the real data.
- It deliberately coexists with two existing quick actions on the same field (`rotation`): the context menu ("Component context menu") offers "Girar 90° (horario)" (+90°) and "Girar 90° (antihorario)" (-90°), both cyclic (on passing an end of the range, they wrap to the opposite end: e.g. from 360° they go to -270°), with no code relation to this slider — two editing mechanisms for the same field, one quick and cyclic, the other precise and full-range.
- Any future control that needs to "choose a value in a continuous range, with discrete references it is worth aligning to": reuse this pattern instead of a plain slider or a `<select>` of fixed values.

## Illustrative per-row icon in the "Add component" list

`.component-type-modal__icon` (`ui/componentTypeModal.js`): an illustrative icon of the component type in each row of the "Add component" modal's list, between the `<input type="radio">` and the label's `<span>` (row order: radio, icon, text).

- Hardcoded linear inline SVG per type: the `icon` property of each `COMPONENT_TYPES` entry. `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, `stroke-linecap`/`stroke-linejoin` `round` — the same iconography as `ui/editModeToggle.js` and `ui/componentList.js`. A distinct one per each of the 7 types.
- Container `<span class="component-type-modal__icon">`, `22×22px`, `flex-shrink: 0`, `innerHTML` = the SVG. Decorative: `aria-hidden="true"` (the type name in the adjacent text `<span>` is the row's real label).
- Color by state (`color`, inherited by `stroke="currentColor"`):
  - at rest: `var(--text-muted)`.
  - row `[hover]` (`.component-type-modal__item:hover`) or a row with its radio checked (`.component-type-modal__item:has(input:checked)`): `var(--accent-blue)`.
  - Transition `color var(--transition-fast)`.
- "Selected" state resolved with `:has(input:checked)`, not with a class added by JS — the same criterion as the only other use of `:has()` in `main.css` (`.document-viewer__content li:has(> input[type="checkbox"]:first-child)`). The `:hover` reinforces the row's already-existing border highlight (`.component-type-modal__item:hover`), with no new visual pattern.
- Does not use `.icon-frame` (that class has no own base rule in `main.css`; its size depends on the context — toolbar, export menu). This icon sets its own `22×22px` in the block class.
- Distinct from the icon-only button group ("Group of icon-only buttons", `.align-group`): there each icon **is** the clickable control; here the icon is purely illustrative inside a `<label>` whose real control is the radio.

## Bevel/depth — "Tablero simple", "Tablero personalizado", "Dado"

Complementary to their contact shadow.

- `'tableroSimple'` (`ui/componentRenderer.js`): simulates relief on the border by splitting the chosen color into two tones (lighter top/left, darker bottom/right), computed with `shadeColor` (`core/colorUtils.js`). No shadow or gradient — the contact shadow (`.board`, level 1) is a separate CSS `box-shadow`, not computed by this helper.
- `'dado'` (`ui/componentRenderer.js`, `renderDiceSilhouette`): draws only the main silhouette, a thin outline and internal faceting lines (4/8/9+ results), all with `shadeColor` — it no longer draws depth as a duplicated SVG polygon. `'dado'`'s depth/extrusion becomes "one more type" of the general property `profundidad`/`colorExtrusion` (see "Configurable extrusion", `001-tokens-visual.md`, Elevation), applied as stacked `filter: drop-shadow` over the `.dice` container. Its contact shadow (`.dice`) still uses `filter: drop-shadow` (non-rectangular silhouette), independent of the extrusion.
- `'tableroPersonalizado'`: same two-tone criterion as `'tableroSimple'` (`.tablero-personalizado`, same level-1 shadow).
  - Difference from "Carta" (they share the same visual editor `ui/visualEditorModal.js` but not this treatment): parameter `borderStyle: 'bisel'` reuses `shadeColor` for the design canvas border, instead of the simple border of `'carta'` (`borderStyle: 'simple'`).
- Technique scoped to these three types — not applied to any other type without an explicit decision.
- In `'tableroSimple'` and `'tableroPersonalizado'` (not in `'dado'`, always beveled) the bevel is optional: property `biselado` (boolean, `true` by default), "Biselado en el borde" checkbox in the "Visual" section (informational, first of the specific-properties tab, see "Sections inside property tabs" above).
  - Unchecked: paints the same `bordeColor` on all four sides without splitting into two tones (does not omit the property).
  - Points where it is applied: the table (`ui/componentRenderer.js`, both types) and, for `'tableroPersonalizado'`, the canvas preview in the Visual editor (`ui/visualEditorModal.js`, parameter `bevelEnabled` of `openVisualEditorModal`, read once on opening the editor).

## Rounded corners of "Carta"

- `'carta'` (`ui/componentRenderer.js`, `.carta` in `main.css`) uses `var(--radius-lg)` as the base in the CSS class — the same radius as "highlighted containers" (`.modal`, floating panels). Not a special value.
- For the five rectangular/square proportions: `8px` (`var(--radius-lg)`) is the default result of the `esquinasRedondeadas` property (boolean; see `../architecture/003-component-types.md`, type `'carta'`), applied as an inline style (`getCartaShapeCss`, `core/cardProportions.js`) — priority over the class.
- "Esquinas redondeadas" checkbox (`ui/visualEditorModal.js`, toolbar next to the Proporción selector, visible only if `showProporcionSelector` is `true`, i.e. only for `'carta'`) unchecked → `border-radius: 0`.
- Circular and Hexagonal are unaffected: they keep a fixed clip (`50%`/`clip-path`).
- Reuses `.modal__field--checkbox` as-is (the same pattern as "Bloqueado"/"Oculto" in `ui/componentModal.js`) — no new visual pattern.
- A card also carries a level-1 contact shadow (like the rest of the game pieces), unaffected by this property.

## "Mazo" reuses the `.carta` class

- `'mazo'` (`ui/componentRenderer.js`): no new BEM block for its box — being visually "a face-down card", it reuses `.carta` as-is (same `--radius-lg`, same level-1 shadow, same `--selectable`/`--selected`/`--movable` modifiers).
  - It only adds `.mazo--clickable` ("draw a card" cursor, equivalent to `.carta--clickable`/`.dice--clickable`).
- `.mazo-reveal-zone` ("reveal zone"): an own block, does not share a look with `.carta` — a box with a dashed border `var(--border-neutral)`, text `var(--text-muted)`, `pointer-events: none`. The same neutral tone as a read-only informational row (`.context-menu__info-row`, see "Component context menu" above).
- `.btn-sacar` (`ui/mazoContentModal.js`): a standalone button that does not hang off any existing BEM block (historical exception, see `004-naming-and-patterns.md`, Class naming).

## Circular shape of "Mazo"

- The `forma` property of `'mazo'` sets `border-radius: 50%` inline when it is `'circular'` — priority over the class `.carta`'s `var(--radius-lg)`. The same mechanism as the `'circular'` proportion of "Carta", not a new exception.
- Applied to the deck box and to its inner clipped content (back of the top card, or "empty deck" icon).
- Contact shadow: no special treatment (unlike "Carta"'s hexagonal silhouettes) — `box-shadow` already follows the element's `border-radius`, projects a circular shadow automatically.
- `.mazo-reveal-zone` adopts the same criterion: `border-radius: 50%` inline if the deck is circular, instead of the default `var(--radius-sm)`.

## Card thumbnail in the "Deck content" modal

- `.mazo-contenido__thumb` (`ui/mazoContentModal.js`, block `.mazo-contenido__item`): an adjustable thumbnail of each card's front face in the "Ver contenido del mazo" modal's list (source: the deck's context menu in play mode or the deck's tab in edit mode).
  - Dimensions: the card's real width and height, scaled proportionally to fit within a maximum `THUMB_MAX_WIDTH` × `THUMB_MAX_HEIGHT` (42 × 58 pixels).
  - Shape: reuses `getCartaShapeCss` (`core/cardProportions.js`) to apply the same `border-radius` and `clip-path` as the real card by its `proporcion` (rectangular with rounded corners by default, circular, hexagonal, triangular).
  - Border: a neutral decorative "slot" border (`1px solid var(--border-neutral)`) only in rectangular/square proportions (where `clip-path: 'none'`). In hexagonal and triangular proportions (`clip-path` active) it is omitted, because CSS `border` does not follow the clipped silhouette — consistent with the real card on the table also not simulating a uniform-thickness border in those proportions (that two-nested-layer mechanism belongs to the card's choosable-color border, not applicable here).

## Hexagonal clip of "Carta"

- Proportions `'hex-vertical'`/`'hex-horizontal'`: do not use `var(--radius-lg)` or `border-radius: 50%` — clip with `clip-path` (exact regular-hexagon polygon, sharp vertices with no bevel or rounding). The only way to achieve a straight-edged silhouette.
- Applied at three points: card on the table (play/edit), each face's canvas in the card editor, image-adjust mask.
- Contact shadow: cannot be `box-shadow` (it would follow the rectangular box, not the hexagon) — uses `filter: drop-shadow` (class `.carta--hex`), the same criterion as `.dice`.

**Border in hexagonal proportions.**

- The border also cannot be painted with the CSS `border` property (always parallel to the rectangular box; clipping with `clip-path` cuts through the border at an angle instead of following the edges).
- Fix (`ui/componentRenderer.js`, `ui/visualEditorModal.js`): two nested, concentric `clip-path` layers.
  - Outer layer: filled with the border color, clipped with the full hexagon.
  - Inner layer: content (image, text boxes), clipped with a smaller hexagon.
  - The gap between the two = border, uniform thickness.
- The inner hexagon is computed with `getHexInnerClipPath` (`core/cardProportions.js`): these proportions' `ratio` always forces a regular hexagon, so shifting the six edges inward by a constant distance is equivalent to scaling the vertices from the center by a factor obtained from the apothem (`width/2` in `'hex-vertical'`, `height/2` in `'hex-horizontal'`).
- Technique scoped to these two proportions — the rest keep using normal CSS `border` (box and visible silhouette coincide).

## Triangular clip and border of "Carta"

- Proportions `'triangulo'`/`'triangulo-invertido'`: same mechanism as the hexagonal ones.
  - Clip with `clip-path` (straight-edged silhouette, not a strictly equilateral triangle — it occupies the full width and height of the square box, see `../architecture/003-component-types.md`).
  - Contact shadow with `filter: drop-shadow` (shared class `.carta--hex, .carta--triangle` in `main.css` — same reason: a non-rectangular silhouette cannot project a `box-shadow`).
  - Border via two nested `clip-path` layers.
- Technical difference: computing the inner clip.
  - Regular hexagon: the incenter coincides with the box center (`50%, 50%`), inradius = half the side.
  - This triangle: the incenter is **not** at the box center. `getTriangleInnerClipPath` (`core/cardProportions.js`, sibling of `getHexInnerClipPath`, not a generalization) scales from the real incenter of each variant (`TRIANGLE_GEOMETRY`, standard incenter/inradius formulas from the vertices).

## Drop-zone highlight on a deck — "Mazo" during a card drag

Transient state while a card (or a cards-only selection, in edit mode) is dragged over a deck.

- Transient state `.drop-target` (`src/styles/main.css`), added/removed by `ui/componentRenderer.js` (`updateMazoDropHighlight`/`clearMazoDropHighlight`) on the `'mazo'` element.
- Applies in both modes (play and edit) equally — it lives in the shared render point (`renderComponentsOnTable`).
- Trigger: when the dragged card's rectangle overlaps a deck (same overlap criterion as the insertion drag&drop). Highlighted only if the dragged selection contains cards only (in play mode it is always a single card, in edit mode it can be a multi-selection if all are cards; if the selection mixes component types, nothing is highlighted).
- Solid blue outline + halo (`outline: 3px solid var(--accent-blue)` + `box-shadow` with `var(--accent-blue-light)`) — visually distinct from the dashed selection outline (`.carta--selected`, `dashed`), so as not to confuse the "drop zone" semantics with "selected element".
- Always removed on mouse release, whether or not the card is inserted into the deck — the table is fully redrawn if the insertion runs anyway.

## "Carta" flip feedback

A second transient state distinct from `.lifted` (see `001-tokens-visual.md`, "'Lift' effect on dragging in play mode").

- State `.carta--flip-feedback` (`src/styles/main.css`): visually confirms a card changed face (click on `'carta'` in play mode, `onCartaFlip`).
- Unlike `.lifted`, it is not added/removed from the drag code (`mousedown`/`mousemove`/`mouseup`).
  - `ui/componentRenderer.js` detects the flip by data diff: it compares each card's current `caraActual` against the last seen, in an own module `Map` (`lastCaraById`), unrelated to any drag state.
  - It is applied/removed on creating the node in each render, with its own `setTimeout` (`flipFeedbackTimeouts`) — needed because `onCartaFlip` triggers a synchronous re-render that already destroyed the original node before any added class could be seen.
- Applies a vertical offset + a slight scale (`transform: translate(0, -6px) scale(1.03)`) alongside `box-shadow: var(--shadow-2)`, transitioning with `var(--transition-fast)` like `.lifted`.
- Does not replace or reuse `.lifted`: independent states, no shared variables or code paths, do not coexist in practice (a click without a drag never activates the lift).
- Does not reopen the general ban on complex animations: no `@keyframes` or narrative animations.
