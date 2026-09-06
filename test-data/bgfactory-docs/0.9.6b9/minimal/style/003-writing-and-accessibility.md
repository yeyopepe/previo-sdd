# 003 — Writing, naming and accessibility
**Area**: Writing / naming conventions

## Language

| Surface | Language |
|---|---|
| User-facing UI copy | Spanish (`carta`, `mazo`, `dado`, `etiqueta`, `bloqueado`, "Barajar", "Ver contenido…") |
| `index.html` | `lang="es"` |
| Code comments | Spanish |
| Infrastructure identifiers | English (`eventBus`, `persistence`, `renderAll`, `loadComponents`) |
| Domain identifiers / fields | Spanish (`etiquetaIds`, `bloqueado`, `caraActual`, `disposicion`, `numeroMaximoCaras`) |

- [gotcha] A single symbol mixes both: `syncCopyWithOriginal`, `getComponentsUsingTag` (English verbs) operate on Spanish-named fields. Match the surrounding file — infra file → English, domain field → keep its Spanish name.

## CSS class naming

- BEM-ish: `.block__element--modifier` — `.component-list__row--selected`, `.modal__field--checkbox`, `.export-menu__item--soon`, `.component-list__action-btn--danger`.
- [gotcha] Footer action buttons are a documented exception to BEM: `.btn-cancel`, `.btn-accept`, `.btn-eliminar`, `.btn-duplicate`, `.btn-sacar` are standalone classes, no owning block. A new footer/standalone action button follows this flat form, not `.modal__btn--x`.

## Deliverable / version naming

- `CURRENT_VERSION` format `v{NNNN}` (zero-padded, width preserved). Displayed as `v.{NNNN}` (`formatVersion`, strips leading `v`).
- Built file: `src/_output/versions/index-v{NNNN}.html`.
- `<title>` marker: literal `{VERSION}` → `v.{NNNN}` at build; build fails hard if the marker is absent.
- Default game title: `"BG Factory"` (`DEFAULT_APP_TITLE`); used as default export filename (`{title} v.{NNNN}.json`).

## Microcopy patterns

- Destructive `confirm()` copy: `¿Eliminar el/la {tipo} "{id-o-nombre}"?`.
- "Próximamente" tag on not-yet-available menu items (`.export-menu__item--soon` + `.export-menu__soon-tag`).
- Import conflict report: one row per broken reference, `{tipoError} | {solución} | {elemento}`.
- Toasts are short imperative-past confirmations ("Etiqueta añadida").

## Accessibility

Current state observed in code (facts, not compliance claims):

- Keyboard: full modal flow operable via ESC / Enter / Delete (`ui.shortcuts`). Selection move via arrows in edit mode.
- `createFitButton` sets `title` + `aria-label="Ajustar zoom"`. Most other icon buttons rely on adjacent text label; icon-only buttons without `aria-label` exist.
- No `prefers-reduced-motion` handling — all transitions are `150ms ease` unconditionally. `[gotcha]` animations (dice roll `1000ms`, card flip) are not motion-reduction aware.
- Contrast: `--text-primary #1a1a1a` on `--bg-card #f5f5f5` / `--bg-subtle #f0f0f0` — high. `--text-muted #666666` on light backgrounds is the lowest-contrast pairing in use.
- No documented ARIA-role strategy for the custom panels / context menu / infinite table. Pending: define roles + focus order for `ui.panel.*` and `ui.contextMenu` if accessibility is prioritized.
