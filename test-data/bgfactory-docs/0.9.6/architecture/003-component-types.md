# 003 — Implemented component types

**Area**: Component types

Eight types. Creation always goes through `ui/componentTypeModal.js` (list of available types, not a dropdown) — on accept, the component is created with `createDefaultComponent(type)` (`ui/componentModal.js`) with default values, added to state, and `ui/componentModal.js` opens over that component to configure it.

> Catalog of every type-specific property as it appears in the modal's "Específicas" tab (order, sections, visibility condition, sub-modals): see the functional entry "Catálogo de propiedades de componentes, grupos y etiquetas" (`../features/040-catalogo-de-propiedades-de-componentes-grupos-y-etiquetas.md`).

## `'texto'`

First concrete type. No image background, automatic size by default.

| Property | Type | Default | Description |
|---|---|---|---|
| `contenido` | string | — | Text shown |
| `tamañoFuente` | number | — | Size in pixels |
| `colorTexto` | string (hex) | black | Text color |
| `colorFondo` | string (hex or empty) | empty (transparent) | Background color |

## `'tableroSimple'`

Square element resizable to any proportion, configurable border and background. `width`/`height` set to `200px` by default (never automatic size). Current type name; the earlier name (`'tablero'`) was migrated on load until 00250 removed all pre-1.0 save migrations — a component created with the current version is already `'tableroSimple'`.

| Property | Type | Default | Description |
|---|---|---|---|
| `bordeColor` | string (hex) | `#000000` | Border color, `box-sizing: border-box`. Kept in `properties` when `bordeActivo === false` |
| `bordeGrosor` | number, px 1–20 | `2` | Border thickness. Clamp in `ui/componentModal.js` (`renderBoardSpecificFields`) fires on the `input` event: `parsed = parseInt(value, 10)`; `bordeGrosor = Number.isNaN(parsed) ? 2 : Math.min(Math.max(parsed, 1), 20)`. `'25' → 20`, `'0' → 1`, `'-5' → 1`, non-numeric (`''`, `'abc'`) → `2` (default, not 1) |
| `bordeActivo` | boolean | `true` | Checkbox "Activar borde". `false`: no border drawn (`border-style: none`); `bordeColor`/`bordeGrosor` kept in `properties` |
| `biselado` | boolean | `true` | `true`: two-tone bevel — `borderTopColor`/`borderLeftColor` = `shadeColor(bordeColor, +0.35)` (lighter), `borderBottomColor`/`borderRightColor` = `shadeColor(bordeColor, -0.35)` (darker); style exception — see `../style/`. `false`: `board.style.borderColor = bordeColor` (4 sides equal) |
| `sombra` | boolean | `true` | `true`: contact shadow level 1. `false`: flat, no shadow (class `.board--sin-sombra`) |
| `fondoTipo` | `'colorPatron' \| 'imagen' \| 'color'` | — | Which background configuration is active. `'color'` = solid color fill (change 00156). Switching between them does not clear the others' configuration — all three blocks coexist in `properties` |
| `colorSolido` | string (hex or empty) | `#ffffff` | Solid background color when `fondoTipo === 'color'`. Empty string → `background-color: transparent` (checkbox "transparente" in `ui/boardColorModal.js`) |
| `patronColor` | string (hex) | — | Grid pattern color |
| `patronGrosor` | number, px 1–20 | `1` | Pattern line thickness |
| `patronForma` | `'cuadrada' \| 'hex-vertical' \| 'hex-horizontal'` | — | Cell shape. `'hexagonal'` (legacy value) is resolved as an alias of `'hex-horizontal'` **on render only** (`ui/componentRenderer.js`); the stored value is never rewritten |
| `patronFilas`, `patronColumnas` | number, 1–50 | — | Grid dimensions |
| `imagenResourceId` | string \| null | `null` | Id of a `'imagen'` resource as background (`background-size: cover`). Missing / nonexistent resource → `background-color: #ffffff` fallback, no `background-image`. Does not use `component.image` |

Pattern rendering: square/rectangular grids use a double CSS `linear-gradient` (`background-size` = cell size, thickness = `patronGrosor`). Hexagonal grids draw an `<svg>` with one polygon per hexagon (`renderHexGrid` of `ui/componentRenderer.js`, parameterized by orientation): `'hex-vertical'` = pointy-top (vertices up/down), `'hex-horizontal'` = flat-top (vertices left/right).

Background configuration is edited in sub-modals `ui/boardPatternModal.js` (color and pattern), `ui/boardImageModal.js` (image) and `ui/boardColorModal.js` (solid color). Each sub-modal's `onAccept` writes only its own keys — that is why switching `fondoTipo` does not destroy the inactive options' config.

## `'dado'`

Always-square element (width = height on resize too), never automatic size. `width`/`height` set to `100px` by default. Roll/validation logic lives in `core/dice.js` (no dependencies on other layers: `getPosibleValores`, `getResultadoInicial`, `esResultadoValido`, `tirarDado`, `isListaValoresValida`).

| Property | Type | Default | Description |
|---|---|---|---|
| `colorCuerpo` | string (hex) | neutral gray | Body color |
| `colorNumeros` | string (hex) | black | Printed result color |
| `modoCaras` | `'numeroMaximo' \| 'lista'` | — | Active configuration. Switching mode does not clear the other — both coexist |
| `numeroMaximoCaras` | number, 2–100 | `6` | In `'numeroMaximo'` mode: result between 1 and this maximum |
| `listaValores` | string (comma-separated values) | — | In `'lista'` mode: result is one of these literal values. Requires ≥2 non-empty values after trimming |
| `fuenteResourceId` | string \| null | `null` | Id of a `'tipografia'` resource for the result text (chosen in `ui/diceFontModal.js`). `null` or a nonexistent resource uses the default typeface |
| `resultadoActual` | string | computed | Result shown. Recomputed when the face configuration changes and it stops being valid |

Rendering (`ui/componentRenderer.js`): flat 2D silhouette that varies by number of possible results (triangle/square/rhombus/faceted decagon, `renderDiceSilhouette` helper). Depth is not part of the SVG drawing: it uses the general component property `profundidad`/`colorExtrusion` (see `002-component-model.md` "General fields"), applied as stacked `filter: drop-shadow` over the `.dice` container — same mechanism as the rest of the types; `'dado'` starts with `profundidad: 4` by default to approximate the thickness feel the duplicated polygon used to give. In play mode: click rolls the die (~1s flicker between results, handled inside `componentRenderer.js`, sets result via `onDiceResult`); double click opens `ui/diceResultModal.js` at large size (`onDiceOpenResult`). In edit mode: no rolling, behaves like any component (resize always forces square).

## `'documento'`

"Document viewer": white-background sheet, thin border, no bevel or shadow. `width`/`height` set to `240×320px` by default (never automatic).

| Property | Type | Default | Description |
|---|---|---|---|
| `tipoContenido` | `'texto' \| 'url'` | — | Active configuration. Switching does not clear the other |
| `contenido` | string | — | Text/HTML pasted by the user (used if `tipoContenido === 'texto'`) |
| `formato` | `'markdown' \| 'html'` | `'markdown'` | How to interpret `contenido` |
| `url` | string | — | External page to embed (used if `tipoContenido === 'url'`) |

Support: `core/markdown.js` (`markdownToHtml(text)`) wraps the vendored library `vendor/marked.js` (marked v18.0.6, MIT — full CommonMark + GFM). `core/sanitizeHtml.js` (`sanitizeHtml(html)`, DOM-based) strips `<script>`, `on...` attributes, and `href`/`src` with `javascript:` — essential because `marked` does not sanitize its output and state is saved as self-contained HTML.

`vendor/` is the only exception to the layers of `001-overview.md` (Layered architecture): third-party code as-is, no functional modification — needed because the build does not accept npm/CDN packages.

Render: with `tipoContenido === 'texto'`, `sanitizeHtml(formato === 'html' ? contenido : markdownToHtml(contenido))` is inserted. With `tipoContenido === 'url'`, it is embedded in `<iframe sandbox="allow-scripts allow-same-origin allow-popups">` with an overlay notice if it does not fire `load` within 3s or fires `error` (best-effort heuristic). Content always fitted to the component width (vertical scroll only).

## `'carta'`

Rectangle of configurable proportion, designed with the "Visual editor" (`ui/visualEditorModal.js`, see `006-ui-layer.md`) — same editor as `'tableroPersonalizado'`. Visible label "Carta/Ficha" (absorbs the use case of the retired `'ficha'` type, see `004-groups-resources.md`); data identifier remains `'carta'`. Created with `width`/`height` = `180 × (180 / ratio(default proportion))` px, `bloqueado: false` by default.

Resize: keeps the configured proportion for the five rectangular proportions (`ui/resizeHandle.js` uses `getProporcionRatio(props.proporcion)` from `core/cardProportions.js`) — the only way to change proportion is to edit that property, not drag the handle. Exception: `proporcion === 'circular'` has free resize on both axes, Shift forces 1:1; starts with width = height on creation or on switching to this proportion. Resizing on the table changes only the frame size: the content (image, shapes, texts) is not rescaled, may be clipped by `overflow: hidden` if it does not fit (same criterion as `'tableroPersonalizado'`).

Corners: `border-radius: 8px` for the five rectangular/square proportions, gated by `esquinasRedondeadas` (`border-radius: 0` if unchecked) — except `proporcion === 'circular'` (`border-radius: 50%` fixed, not gated by `esquinasRedondeadas`). The same condition applies to each face's canvas in `ui/visualEditorModal.js` and to the `ui/imageAdjustModal.js` mask.

| Property | Type | Default | Description |
|---|---|---|---|
| `proporcion` | see `CARD_PROPORTIONS` below | `'5:7'` | Proportion/shape of the card |
| `medidasReales` | boolean | `true` | Internal, not editable: marks whether `caraFrontal`/`caraTrasera` are in real pixels. Always `true` for a card created with the current version; no longer read by any load-time migration (removed in 00250) |
| `esquinasRedondeadas` | boolean | `true` | Rounded corners (`8px`) or square (`0`). Its control (checkbox in `ui/visualEditorModal.js`) is shown only when the proportion is rectangular/square (`isRectShape`) — circular and hexagonal do not use it. "Copiar/Pegar estilo" includes it alongside `proporcion` |
| `caraActual` | `'frontal' \| 'trasera'` | `'trasera'` | Face shown. In play mode, click toggles it (`onCartaFlip`), independent of `bloqueado`. Each flip triggers a brief visual feedback (`.carta--flip-feedback`), detected by data diff via a module `Map` `lastCaraById`, not by a click event |
| `caraFrontal`, `caraTrasera` | object, same shape | — | Design of each face, specific to that card. See shape below |

`CARD_PROPORTIONS` (`core/cardProportions.js`): `'5:7'` (Poker vertical), `'7:5'` (Poker horizontal), `'tarot-h'` (Tarot vertical 70×120mm), `'tarot-v'` (Tarot horizontal 120×70mm), `'1:1'` (Square), `'circular'` (free resize), `'hex-vertical'`/`'hex-horizontal'` (Hexagonal, fixed-ratio resize), `'triangulo'`/`'triangulo-invertido'` (vertex up/down, 1:1 box, fixed-ratio resize). Each entry carries a `shape` field; `getCartaShapeCss(value, esquinasRedondeadas = true)` translates to `borderRadius`/`clipPath`: rectangular/square → `border-radius: 8px` or `0`; circular → `50%`; hexagonal/triangular → `clip-path` with an exact polygon (not affected by `esquinasRedondeadas`). Applied in `ui/componentRenderer.js`, `ui/visualEditorModal.js` and `ui/imageAdjustModal.js` (the latter with its own `shape` vocabulary, polygons deliberately duplicated). `core/cardProportions.js` also exposes `isRectShape(value)`. Hexagonal/triangular card shadow uses `filter: drop-shadow` (class `.carta--hex, .carta--triangle`), like `'dado'` for non-rectangular silhouettes. Uniform-thickness border on triangular shapes uses `getTriangleInnerClipPath` (sibling of `getHexInnerClipPath`): it scales from the real incenter of each variant (`TRIANGLE_GEOMETRY`, precomputed constant), unlike the regular hexagon whose incenter coincides with the box center.

### Shape of `caraFrontal`/`caraTrasera`

`{ imagenResourceId, ajusteImagen, formas: Forma[], textBoxes: TextBox[], bordeColor, bordeGrosor, transparenciaImagen, fondoTipo, colorFondo }`

| Field | Type | Default | Description |
|---|---|---|---|
| `imagenResourceId` | string \| null | `null` | Background image resource of the face |
| `ajusteImagen` | `{ zoom, posX, posY, rotation }` | — | Same shape `ui/imageAdjustModal.js` uses in general |
| `formas` | `Forma[]` | `[]` | See `Forma` shape below |
| `textBoxes` | `TextBox[]` | `[]` | See `TextBox` shape below |
| `bordeColor` | string (hex) | black | Border of the whole card for that face |
| `bordeGrosor` | number, px **0**–20 | `0` | `0` is valid = "no border" (unlike `'tableroSimple'`). Simple line, no bevel |
| `transparenciaImagen` | number, 0–100 | `0` (opaque) | Transparency of the background image (`opacity = 1 - transparenciaImagen/100`), independent of background color/textBoxes/border. Only has effect if there is `imagenResourceId`; resets to `0` on image change |
| `fondoTipo` | `'imagen' \| 'color' \| undefined` | — | Absent and `'imagen'` are treated the same (paints `imagenResourceId` if it exists, white otherwise) — unlike `Forma`, where `undefined` is treated as `'color'`. Switching does not clear the inactive one |
| `colorFondo` | string (hex or empty) | — | Solid background color if `fondoTipo === 'color'` |

Coordinates (`x`/`y`/`width`/`height` of each `Forma`/`TextBox`, `tamañoFuente` of each `TextBox`) are stored in real pixels, fixed regardless of card size — same criterion as `'tableroPersonalizado'`. (Cards saved with the earlier "design units" system, an abstract 300px canvas rescaled by a uniform factor, were migrated once on load until 00250 removed all pre-1.0 save migrations; a card created with the current version already stores real pixels.)

**Stacking order within a face**: the background image is always at the bottom, outside any order. `formas` and `textBoxes` share a single mixed stacking order (each element's `orden` field) — any shape can be above or below any text box. `core/cardFaceElements.js` (pure data module) combines both arrays: `getOrderedFaceElements(cara)` returns the list from back to front (in-memory fallback for elements without `orden`, no data migration); `bringElementToFront`/`sendElementToBack` set an element's `orden` above/below all others of its face. Reused by `ui/visualEditorModal.js` and `ui/componentRenderer.js` → `paintCartaFace`.

**Canvas context menu** (`ui/visualEditorModal.js`, right-click, reuses `ui/contextMenu.js`): over an element — "Copiar", "Pegar", "Eliminar" (no confirmation), "Colocar arriba"/"Colocar abajo". In an empty area — only "Pegar". `generalItems`/`specificItems` accept `disabled: boolean`.

- **Copy/Paste**: `copiedElement`, module variable (`{ kind, data } | null`, survives closing/reopening the editor, does not persist). "Copiar" stores a shallow copy (`{ ...element }`) without `id`; copying a new one replaces the previous. "Pegar" always visible, `disabled: !copiedElement`; creates an element with a new `id` at the click point (`screenToDesignPoint`), adds it to `cara.formas`/`cara.textBoxes`, brings it to front, selects it.
- New elements ("Añadir elemento") and duplicates from the edit modal are placed above all others of their face.
- **Deletion with DEL**: `handleKeyDown` of `visualEditorModal.js` handles `e.key === 'Delete'` (same value as `ui/globalShortcuts.js`) — with an element selected and focus outside an editable field, deletes it via `removeElement` (same function as the menu's "Eliminar").

### `Forma` shape

`{ id, tipo: 'circular' | 'cuadrada' | 'redondeada', x, y, width, height, colorFondo, colorFondoTransparencia, fondoTipo: 'color' | 'imagen' | undefined, imagenResourceId, ajusteImagen, imagenTransparencia, bordeActivo, bordeColor, bordeGrosor, orden, rotation: number (-360-360) | undefined }`

Third kind of repeatable element within a face (alongside the single background image and `textBoxes`). Same interaction behavior as `TextBox`: selectable, editable with double click (`ui/cardShapeModal.js`), draggable, resizable, duplicable, deletable, with the same context menu.

| Field | Type | Default | Description |
|---|---|---|---|
| `x`, `y`, `width`, `height` | number | — | Same units as `TextBox` (real pixels) |
| `orden` | number \| undefined | fallback if absent | Lower = further forward in the stack. See "Stacking order" above |
| `rotation` | integer, `-360`-`360` \| `undefined` | equivalent to `0` | Rotates the whole shape (border+fill) about its center (`transform: rotate`) — unlike `ajusteImagen.rotation`, which rotates only the fill image. `x`/`y`/`width`/`height` do not change on rotation, content may be clipped. The sign indicates direction: negative counterclockwise, positive clockwise. Two editing paths coexist: "Girar 90° (horario)"/"Girar 90° (antihorario)" of the context menu (cycle ±90°, wrapping to the opposite end of the range on overflow) and the rotation slider (`ui/rotationSlider.js`) inside `ui/cardShapeModal.js`, with magnetic marks every 90° (symmetric on both sides of 0) but free for any intermediate angle |
| `tipo` | `'circular'\|'cuadrada'\|'redondeada'` | — | `'redondeada'`: curved corners `border-radius: 8px` (`SHAPE_BORDER_RADIUS`) |
| `fondoTipo` | `'color'\|'imagen'\|undefined` | `undefined` ≈ `'color'` | Switching does not clear the other |
| `colorFondo` | string (hex or empty) | empty | With `fondoTipo === 'color'` |
| `colorFondoTransparencia` | number, 0–100 | `0` (opaque) | Transparency over `colorFondo` (`core/colorUtils.js` → `hexToRgba`). Only has effect and an enabled control if `colorFondo` is non-empty |
| `imagenResourceId` | string \| null | `null` | With `fondoTipo === 'imagen'`. Fully replaces `colorFondo` on paint (not combined) |
| `ajusteImagen` | `{ zoom, posX, posY, rotation }` | resets to `{ zoom:100, posX:50, posY:50 }` on choosing/changing image | Same shape as `cara.ajusteImagen` |
| `imagenTransparencia` | number, 0–100 | `0` (opaque) | Transparency over the background image (`fondoTipo === 'imagen'`), independent of `colorFondoTransparencia` and the border. Resets to `0` on choosing/changing image; kept on switching `fondoTipo` to `'color'` and back to `'imagen'`. Adjusted from the "Transparencia" slider inside "Ajustar imagen…" (`ui/imageAdjustModal.js`), not in the shape's edit panel |
| `bordeColor`, `bordeGrosor`, `bordeActivo` | hex / px 1–20 / boolean | black / `2` / `true` | Simple border (CSS `border`), no special bevel. "Borde" section in `ui/cardShapeModal.js` uses a toggle pattern in the `<legend>` |

On paint, the image is clipped to the shape's `tipo` (same `border-radius`) in an inner `overflow: hidden` container, border above on the outer container. Changing `tipo` keeps `imagenResourceId`/`ajusteImagen` (independent of `tipo`); duplicating/copy-pasting carries them too. Resize: `tipo === 'circular'` free on both axes, Shift forces 1:1; `'cuadrada'`/`'redondeada'` free with no restriction. Switching to `'circular'` with `width !== height` equalizes both to the larger (perfect circle). Painted in `ui/visualEditorModal.js` and `ui/componentRenderer.js` → `paintCartaFace`, with no `pointer-events` outside the editor.

Each face's "Añadir elemento" button (dropdown menu): "Elegir imagen…", "+ Texto", "Figura geométrica" (creates a circular shape by default, centered, side `designWidth * 0.3`), "Color de fondo…" (opens `ui/cardBackgroundColorModal.js`, sets `fondoTipo = 'color'` on the face). The last two options do not add a repeatable element: they are single per-face configuration, mutually exclusive with each other.

### `TextBox` shape

`{ id, contenido, fuenteResourceId, tamañoFuente, color, x, y, width, height, bordeActivo, bordeColor, bordeGrosor, bordeTipo: 'continua'|'punteada', colorFondo, colorFondoTransparencia, alineacionHorizontal: 'izquierda'|'centro'|'derecha', alineacionVertical: 'arriba'|'centro'|'abajo', margenSuperior, margenDerecha, margenInferior, margenIzquierda, negrita, cursiva, subrayado, orden, rotation: number (-360-360) | undefined }`

| Field | Type | Default | Description |
|---|---|---|---|
| `bordeActivo`, `bordeColor`, `bordeGrosor`, `bordeTipo` | boolean/hex/px 1–20/enum | `false`/black/`2`/`'continua'` | The box's own border. If `bordeActivo` is `false`, it is not drawn but color/thickness/type are kept |
| `colorFondo`, `colorFondoTransparencia` | hex or empty / 0–100 | empty / `0` | Own background, behind the text. Transparency via `hexToRgba`, only has effect if `colorFondo` is non-empty |
| `alineacionHorizontal`, `alineacionVertical` | enum | `'izquierda'` / `'arriba'` | Text position within the box's inner area (after margins) |
| `margenSuperior/Derecha/Inferior/Izquierda` | number, px | `0` | Reduce the inner area without changing the box size. No negatives, no own cap |
| `negrita`, `cursiva`, `subrayado` | boolean | `false` | Independent, combinable switches, applied to the whole content (not ranges) |
| `orden`, `rotation` | same as `Forma` | — | Same semantics and triggers (context menu "Girar 90° (horario)"/"Girar 90° (antihorario)" + rotation slider in `ui/cardTextBoxModal.js`) as in `Forma` |

`core/textBoxLayout.js` (pure module) exposes `getTextBoxLayoutStyle(textBox, scale)`: translates alignment+margins to `{ justifyContent, textAlign, paddingTop/Right/Bottom/Left }` (last 4 already scaled in `px`) — single point reused by `ui/componentRenderer.js` and `ui/visualEditorModal.js`, both applying the result over a `display:flex; flex-direction:column; box-sizing:border-box` container.

All `TextBox` fields are optional and unmigrated: absence behaves as the table's default (no visual change).

A face with no `imagenResourceId` and no `textBoxes`: the card is shown blank with the configured proportion, no notice.

`core/cardProportions.js` also exposes `CARD_PROPORTIONS`, `getProporcionRatio(value)` (fallback `'2:3'`), `CARD_DESIGN_WIDTH = 300` (historical constant only: the reference width of the retired "design units" canvas; no live consumer since 00250 removed the card-rescale migration).

## `'mazo'`

Ordered face-down stack of cards. Concept independent of "Etiqueta" (purely organizational) — both coexist unrelated. Created with `width`/`height` = `180 × 180/getProporcionRatio('5:7')` px (same starting size as "Carta/Ficha"), `bloqueado: true` and `subirAlMoverInteractuar: true` by default. Does not accept special proportions: only "Vertical"/"Horizontal" orientation, which on change transposes `width`/`height` (does not reset to default size).

| Property | Type | Default | Description |
|---|---|---|---|
| `cartaIds` | string[] | `[]` | Ordered list of `'carta'` component ids in the deck — index `0` is the top one. Reference in deck→card direction |
| `orientacion` | `'vertical'\|'horizontal'` | `'vertical'` | Only determines the box shape on creation/transpose. Its control is shown only when `forma === 'rectangular'` |
| `forma` | `'rectangular'\|'circular'` | `'rectangular'` | Box silhouette, independent of `orientacion`. `'circular'` clips box/content/reveal zone to a round (`border-radius: 50%`). Switching to `'circular'` equalizes `width`/`height` to the larger of the two |
| `disposicion` | `'arriba'\|'abajo'\|'derecha'\|'izquierda'` | `'derecha'` | Side of the deck where the "reveal zone" is painted and the card appears when drawn (`getMazoRevealZoneRect`). Also shown with `forma === 'circular'` (unlike `orientacion`) |
| `textoCartaRevelada` | string | `'Carta revelada'` | Text painted inside the reveal zone. An empty string is a valid value: the zone is painted with no text |
| `caraCartaRevelada` | `'frontal'\|'trasera'` | `'frontal'` | Face the card ends up showing when drawn from the deck (`computeSacarCartaDeMazo` sets `caraActual` to this value) — `'frontal'` is face up, `'trasera'` face down |
| `imagenResourceId` | `string\|null` | `null` | The deck's own image, independent of the stack contents. `null`: no own image, see fallback behavior below |
| `ajusteImagen` | `{ zoom, posX, posY, rotation }\|undefined` | — | Present only if there is `imagenResourceId`. Same shape `ui/imageAdjustModal.js` uses in general |
| `transparenciaImagen` | `number, 0–100\|undefined` | `0` when present | Present only if there is `imagenResourceId`; resets to `0` on choosing/changing image |

`core/deck.js` (pure data module) exposes:
- `getCartaIdsEnAlgunMazo(components)`: `Set` of all ids referenced by any deck.
- `shuffleCartaIds(cartaIds)`: Fisher-Yates + `Math.random()`, same generator as `core/dice.js`.
- `computeSacarCartaDeMazo(mazo, carta)`: pure function, computes the changes of drawing any card from the stack (wherever it is); the card ends up with `caraActual` equal to the deck's `properties.caraCartaRevelada` (fallback `'frontal'`).
- `getMazoRevealZoneRect(mazo)`: rectangle of the "reveal zone", flush to the side indicated by `properties.disposicion` (fallback `'derecha'`).
- `rectsOverlap`: rectangle-overlap test.

While a card's id is in `cartaIds` of any deck, that card **is not drawn as an independent component on the table, in any mode** (unlike `oculto`, filtered only in play mode) — `modes/play/playMode.js` and `modes/edit/editMode.js` exclude those ids with `getCartaIdsEnAlgunMazo`. It still appears in the Components panel unfiltered.

`core/state.js` exposes `sacarCartaDeMazo(mazoId, cartaId)` (uses `computeSacarCartaDeMazo`, applies changes with `replaceComponent`/`reorderComponent`, brings the drawn card to front) — it lives in this layer because `ui/componentModal.js` also needs it and `ui/*` cannot import from `modes/*`.

**Rendering**: reuses the `.carta` class for the box (same radius/shadow), inline `border-radius: 50%` if `forma === 'circular'`. The deck displays one of three paint branches (in order):
1. **Own image + card present**: if the deck has `imagenResourceId` and `cartaIds.length > 0`, that image is painted (with its `ajusteImagen`/`transparenciaImagen`) via `paintCartaFace(contentParent, { imagenResourceId, ajusteImagen, transparenciaImagen, fondoTipo: 'imagen' }, 1, width, height)`.
2. **Card present (no own image)**: if `cartaIds.length > 0` and no own image, the top card's (`cartaIds[0]`) `caraTrasera` is painted via `paintCartaFace(contentParent, cara, renderScale, faceWidth, faceHeight)` — `renderScale = width / (cartaArriba.width || MIN_CARTA_WIDTH)` fits the card's real design into the deck box.
3. **Empty deck**: neutral placeholder (`renderMazoEmptyPlaceholder`, SVG icon).

Next to the deck the "reveal zone" is always painted (`renderMazoRevealZone`, in both modes): decorative box flush to the side indicated by `properties.disposicion` (`MAZO_REVEAL_GAP = 20px` separation in all 4 cases), same `forma` as the deck, with the text of `properties.textoCartaRevelada` (fallback `'Carta revelada'`). It follows the deck live during drag (`handleMouseMove` recomputes `getMazoRevealZoneRect` with the in-progress coordinates, passing `properties` too to respect the layout). `onMazoDraw` parameter of `renderComponentsOnTable`: click on the deck invokes it (exclusive to `modes/play/playMode.js`). The "Específicas" tab (edit mode) organizes its fields in three sections (`fieldset.modal__section`, see `../style/003-modales-menus.md` (Sections inside property tabs)): "Forma" (Forma, Orientación), "Cartas reveladas" (Disposición carta revelada, Texto carta revelada, Revelar carta) and "Imagen" (preview + "Elegir imagen…"/"Ajustar imagen…"/"Quitar imagen", same patterns as `ui/boardImageModal.js`/`ui/imageAdjustModal.js` used by other game elements); "Ver contenido del mazo" is outside any section. Since 00212, it no longer shows any fixed/automatic card counter — anyone who wants to see the card count in play mode must enable "Mostrar título de componente" (`002-component-model.md`) with a text using the `{cards_current}` variable (e.g. `"{cards_current} cartas"`), a generic mechanism of the 8 types, not exclusive to `'mazo'`.

**Context menu** (play mode): a deck adds "Barajar" (`shuffleCartaIds`) and "Ver contenido..." (`ui/mazoContentModal.js`); a card adds "Meter en mazo..." (`ui/insertIntoMazoModal.js`) only if at least one deck exists. Card count is shown in the menu's `description.extra`.

**`ui/mazoContentModal.js`**: lists all cards of the deck (front-face thumbnail + id + "Sacar" button per row, `cartaIds` order), reused from the context menu (play mode) and from the deck's specific tab (edit mode). Always reads the current state of `core/state.js` to refresh after each "Sacar" — mutation is done by whoever opens it, via `onSacar(cartaId)`.

**`ui/insertIntoMazoModal.js`**: deck dropdown + position dropdown ("Arriba del todo"/"Abajo del todo"); `onAccept({ mazoId, posicion })` adds the card's id to the start or end of `cartaIds`.

**Dragging cards onto a deck** (play mode and edit mode): `onMove` of `renderComponentsOnTable` (shared by both modes) detects overlap between the dragged card/selection and a deck. In play mode (single card, no `confirm()`): direct insertion at the end of `cartaIds` on drop. In edit mode (may be a multi-selection of only cards): `attemptDropOnMazo(groupIds, draggedRect)` asks for a native `confirm()` before adding at the end; reversible action. Overlap detection uses `rectsOverlap` in both modes. Visual highlight (blue outline + halo) is applied while dragging over the deck, in both modes, while the selection consists only of cards (no highlight if there is a mix of component types).

## `'tableroPersonalizado'`

Advanced board, coexists with `'tableroSimple'` (neither replaces the other) for when more than color/pattern/single image is needed. Designed with the same "Visual editor" (`ui/visualEditorModal.js`) as `'carta'`, but with a single face (does not flip) under `properties.cara` (same shape as `caraFrontal`/`caraTrasera` of `'carta'`: `imagenResourceId`, `ajusteImagen`, `formas`, `textBoxes`, `bordeColor`, `bordeGrosor`, `transparenciaImagen`). Created with `width`/`height` = `300 × 200px` by default (never automatic); unlike `'carta'`, free resize at any proportion (like `'tableroSimple'`).

| Property | Type | Default | Description |
|---|---|---|---|
| `cara` | object (same shape as a `'carta'` face) | — | Single design |
| `biselado` | boolean | `true` | Top level (not inside `cara`). Decides whether the border has a two-tone bevel or flat color |
| `sombra` | boolean | `true` | Top level. Contact shadow level 1 or flat (`.tablero-personalizado--sin-sombra`) |

The face design is stored directly in real pixels, fixed regardless of component size: painting (`ui/componentRenderer.js` → `paintCartaFace(tableroContent, cara, 1, width, height, 1)`) always uses scale `1`, `overflow: hidden` clips what does not fit — resizing changes only the visible frame. The Visual editor canvas represents the component's real size on open (not a fixed logical canvas). Border uses the same two-tone bevel as `'tableroSimple'`/`'dado'` (`core/colorUtils.js` → `shadeColor`) instead of the simple border of `'carta'`. No "Estilo" block (Copy/Paste style) in this version.
