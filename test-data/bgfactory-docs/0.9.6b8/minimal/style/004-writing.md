# 004 — Writing & naming conventions

**Area**: Style bible

## Code language

| Aspect | Convention |
|---|---|
| Identifiers (vars, functions, fields) | Mixed. Domain terms in **Spanish** (`bloqueado`, `etiquetaIds`, `mostrarTitulo`, `sacarCartaDeMazo`, `caraFrontal`, `profundidad`, `colorExtrusion`); generic/infra terms in **English** (`state`, `eventBus`, `emit`, `resizeHandle`, `order`, `visited`). Match the surrounding file. |
| Component types (`type` string) | Spanish, lowercase, no separator: `carta`, `mazo`, `dado`, `tableroSimple`, `tableroPersonalizado`, `texto`, `documento`, `generico`. |
| Comments | Spanish. Dense, explain *why* / gotchas / cross-layer constraints, not *what*. Frequently reference sibling files by path. |
| Some `ui/` module comments | English (`ui/table.js`, `ui/componentRenderer.js`, `ui/componentModal.js`, `ui/resizeHandle.js`, `ui/rotationSlider.js`). Pre-existing; not a rule to extend or revert. |
| Event names | `domain:changed` — colon-separated, English domain, always `:changed` (`components:changed`, `panelState:changed`, `appTitle:changed`). |
| Files | camelCase `.js` (`componentRenderer.js`, `tableColumnResize.js`). Modals: `<subject>Modal.js`. Confirm dialogs: `<subject>ConfirmModal.js`. |

## CSS class naming — BEM

Block `__element` `--modifier`. Blocks are kebab-case, usually the widget name.

```
.modal                        block
.modal__footer                element
.modal__tab.active            element + state (state as a plain class, not a BEM modifier)
.modal__section--disabled     element + modifier
.card-editor-modal__canvas    block (compound) + element
.carta--selected              block + modifier
.text-box--selectable.is-copy modifier + orthogonal state class (.is-copy, .active, .grabbing)
```

- Modifier `--x` for a variant of the block/element; a plain class (`.active`, `.is-copy`, `.grabbing`, `.grabbing`) for a runtime-toggled state.
- Compound block names are kebab-joined (`.column-header-menu`, `.batch-upload-summary-modal`).
- Block names for game pieces are the **Spanish** type (`.carta`, `.board` is the exception — English).
- [gotcha] `.board` (not `.tablero`) is the CSS block for board pieces, though the component `type` is `tableroSimple` / `tableroPersonalizado`.

## User-facing copy

| Aspect | Convention |
|---|---|
| Language | **Spanish** (`lang="es"` in `index.html`). All UI strings, labels, `aria-label`s, error messages, toasts. |
| Tone | Direct, second person implied, no exclamation. Button verbs in infinitive: "Exportar", "Barajar", "Ver contenido", "Meter carta en mazo". |
| Empty states | Distinguish "nothing yet" from "no match for current filter" — separate strings (`__empty` vs `__empty-filter`). |
| "Coming soon" | Label `__soon-tag` on a disabled menu item, not a separate dialog. |
| App name | "BG Factory" (`DEFAULT_APP_TITLE`). Version shown as `v.{NNNNN}` (`formatVersion`, strips the leading `v` of `CURRENT_VERSION` then re-prefixes `v.`). |

## Framework-doc language exception

This style bible and everything under `docs.tech` is technical **English** (framework rule — `docs.tech` has no language option), even though the codebase and product are Spanish. `docs.functional` (features) is Spanish, per `pv-context.json`.
