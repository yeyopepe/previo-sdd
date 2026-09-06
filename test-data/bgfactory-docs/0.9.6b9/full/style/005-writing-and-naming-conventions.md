# 005 — Writing and naming conventions
**Area**: Writing & naming

Naming conventions across code and CSS, plus user-facing copy conventions. Source: [src/styles/main.css](../../../src/styles/main.css) comments, `src/**/*.js`.

## CSS class naming

- BEM-ish: `block__element--modifier`. Examples: `component-panel__header`, `context-menu__item--disabled`, `carta--selectable`.
- State modifiers on a shared class: `.is-copy`, `.is-group-passenger`, `.is-empty`, `.grabbing`, `.active`, `.lifted`, `--visible`, `--selected`, `--maximized`, `--dim`, `--focused`, `--active`.
- [gotcha] Documented naming exception: standalone action buttons carry **no block** — `.btn-cancel`, `.btn-accept`, `.btn-eliminar`, `.btn-duplicate`, `.btn-sacar`. Any new footer/standalone button follows this exception, not `some-block__btn`.
- One `main.css` file, ~3374 lines, ordered roughly: `:root` tokens → shell → table → panels → modals → menus → pieces → badges → widgets. New rules append near their sibling block; each block prefixed with a `/* ... */` comment stating purpose and cross-refs.
- [gotcha] Many CSS comments reference `design/docs/style/0N-*.md` / `design/docs/architecture/INDEX.md` — those paths **do not exist**. The live docs are `previo-sdd/docs/style/` and `previo-sdd/docs/architecture/`. Treat the comment paths as historical.

## JS identifier language

- [gotcha] Domain identifiers are **Spanish**, matching the domain vocabulary: `carta`, `mazo`, `dado`, `tablero`/`tableroSimple`/`tableroPersonalizado`, `documento`, `ficha` (extinct), `etiqueta`/`etiquetaIds`, `grupo`/`groupId`, `bloqueado`, `oculto`, `caraFrontal`/`caraTrasera`/`caraActual`, `disposicion`, `profundidad`, `colorExtrusion`, `sincronizado`, `subirAlMoverInteractuar`, `accionClickDerecho`, `interaccionesDesactivadas`, `resultadoActual`, `cartaIds`, `numeroMaximoCaras`, `listaValores`, `medidasReales`.
- English is used for generic/infrastructure names: `state`, `eventBus`, `emit`, `on`, `listeners`, `getComponents`, `renderAll`, `persistState`, `component`, `resource`, `tag`, `group`, `order`, `width`, `height`, `image`, `id`, `type`, `name`.
- Enum string values are Spanish lowercase: `bloqueado ∈ {'ninguno','juego','todos'}`, `caraActual ∈ {'frontal','trasera'}`, `disposicion ∈ {'arriba','abajo','derecha','izquierda'}`, `modoCaras ∈ {'numeroMaximo','lista'}`, `accionClickDerecho ∈ {'ninguno','menuContextual'}`.
- Event names are English `namespace:verb` past tense: `components:changed`, `mode:changed`, `appTitle:changed`. See [../architecture/00-namespace.md](../architecture/00-namespace.md) `events.*` for the catalog and legacy aliases.
- Functions: `camelCase`. Factories `createX`. Pure compute `computeX` / `getX`. Modal openers `openXModal`. Renderers `renderX`. Id generators `nextX` (`nextCloneId`, `nextCopyId`, `nextGroupId`).
- Files: `camelCase.js` (`editModeToggle.js`, `fichaMigration.js`). One responsibility per file. Modals: `xxxModal.js`.

## Component-type slug ↔ label

Type slug (persisted, Spanish camelCase) vs UI label (Spanish, `ui/componentTypeModal.js` / modal titles):

| `type` | UI label (approx) |
|---|---|
| `carta` | Carta |
| `mazo` | Mazo |
| `dado` | Dado |
| `tableroSimple` | Tablero simple |
| `tableroPersonalizado` | Tablero personalizado |
| `documento` | Visor de documentos |
| `texto` | Cuadro de texto |

## User-facing copy

- Language: **Spanish**. `<html lang="es">`.
- Tone: informal second person (`tú`) imperative for actions — "Pulsa para sacar la primera carta.", "¿Eliminar el componente ...?".
- Confirmations: question form, `¿...?`, name the target in quotes — `¿Eliminar la etiqueta "X"?`.
- Buttons: verb-first — `Entrar en modo edición`, `Salir del modo edición`, `Importar`, `Exportar juego (.json)`, `Barajar`, `Ver contenido...`, `Meter en mazo...`, `Añadir a etiqueta`, `Agrupar`, `Desagrupar`, `Ocultar`/`Mostrar`, `Bloquear`/`Desbloquear`.
- Ellipsis `...` on an action that opens a further modal (`Ver contenido...`, `Meter en mazo...`).
- Not-yet-available items: label + a `Próximamente` tag, item styled `--soon` (dimmed, `cursor: not-allowed`, inert).
- Errors: `showErrorModal(title, message, detail?)` — title short (`Error`, `Aviso`), message a full sentence, optional technical `detail` in a monospace block.
- Default app title: `'BG Factory'` (`core/appTitle.js#DEFAULT_APP_TITLE`); version suffix `v.{NNNNN}` appended, non-editable.
- Version display: `formatVersion()` → `v.{CURRENT_VERSION minus leading 'v'}`.

## Numbers / units in UI

- Dice faces shown as `N caras`; deck size as `N cartas`; board dims as `{W}x{H}` (rounded). Zoom shown as a percentage, `tabular-nums`.
