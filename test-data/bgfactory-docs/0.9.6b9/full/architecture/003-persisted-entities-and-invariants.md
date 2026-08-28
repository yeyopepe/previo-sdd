# 003 — Persisted entities and invariants
**Area**: Data model

Persisted entities and their invariants. Namespace: [00-namespace.md](00-namespace.md). Field shapes are canonical here; exact code lives at the cited `file#symbol`.

## Component

Factory [src/core/component.js#createComponent](../../../src/core/component.js). Generic entity — no subclasses; `type` is a free string, behavior branches on it in `ui/`/`modes/`.

```
Component = {
  id: string,                         # crypto.randomUUID(), or derived id for clone/copy (see below)
  type: string = 'generico',
  name: string = '',
  properties: object = {},             # type-specific bag; per-type defaults in ui/componentModal.js
  image: string | null = null,         # resourceId
  x: number = 0,
  y: number = 0,
  width: number | null = null,
  height: number | null = null,
  profundidad: number = 0,             # 3D extrusion thickness (px)
  colorExtrusion: string | null = null,
  bloqueado: string ∈ {'ninguno','juego','todos'} = 'ninguno',
  mostrarTooltip: bool = false,
  tooltipTexto: string = '',
  mostrarTitulo: bool = false,
  tituloTexto: string = '',
  tituloColorTexto: string = '#000000',
  tituloColorFondo: string = '#ffffff',
  tituloFondoTransparencia: number = 0,
  subirAlMoverInteractuar: bool = false,   # bump order→1 on move/interact (play mode)
  oculto: bool = false,
  etiquetaIds: string[] = [],          # tag membership (flat, many-to-many)
  order: number | null = null,         # 1..n stacking; assigned/recomputed by state.js
  copyOf: string | null = null,        # linked-copy: id of the original
  sincronizado: bool = true,           # copy follows original's bloqueado/oculto
  groupId: string | null = null,       # component-grouping membership
  interaccionesDesactivadas: string[] = [],
  accionClickDerecho: string ∈ {'ninguno','menuContextual'} = 'ninguno',
}
```

### Known `type` values

`carta`, `mazo`, `dado`, `tableroSimple`, `tableroPersonalizado`, `documento`, `texto`. Default `generico`.
Extinct (migrated on load): `ficha` → `carta`, `tablero` → `tableroSimple`.

### Per-type `properties` defaults

Live in [src/ui/componentModal.js](../../../src/ui/componentModal.js): `DEFAULT_BOARD_PROPERTIES`, `DEFAULT_DADO_PROPERTIES`, `DEFAULT_DOCUMENTO_PROPERTIES`, `DEFAULT_CARTA_PROPERTIES`, `DEFAULT_MAZO_PROPERTIES`, `DEFAULT_TABLERO_PERSONALIZADO_PROPERTIES`. `createDefaultComponent(type)` sets `width`/`height`/`properties` and, for `carta`/`mazo`/`dado`, `subirAlMoverInteractuar = true`.

Shared **face** shape (used by `carta.caraFrontal`/`caraTrasera` and `tableroPersonalizado.cara` — one visual editor serves both):

```
Face = {
  imagenResourceId: string | null,
  ajusteImagen: { zoom: number = 100, posX: number = 50, posY: number = 50, rotation?: number },
  formas: Forma[],            # geometric shapes (custom board + card; card faces added formas later)
  textBoxes: TextBox[],
  bordeColor: string,
  bordeGrosor: number,
  transparenciaImagen: number = 0,
}
```

- `carta`: `{ proporcion, esquinasRedondeadas, caraActual ∈ {'frontal','trasera'} = 'trasera', medidasReales: true, caraFrontal: Face, caraTrasera: Face }`. `medidasReales` marks real-px content (new cards born `true`; old ones migrated — see [002](002-state-event-bus-and-render-persist-wiring.md)).
- `mazo`: `{ cartaIds: string[] = [], orientacion, forma, disposicion ∈ {'arriba','abajo','derecha','izquierda'}, textoCartaRevelada, caraCartaRevelada, imagenResourceId }`.
- `dado`: `{ colorCuerpo, colorNumeros, modoCaras ∈ {'numeroMaximo','lista'}, numeroMaximoCaras = 6, listaValores: string (comma-sep), fuenteResourceId, resultadoActual }`.
- `tableroSimple`: `{ bordeColor, bordeGrosor, bordeActivo, biselado, sombra, fondoTipo, colorFondo, patronColor, patronGrosor, patronForma ∈ {'cuadrada','hexagonal'}, patronFilas, patronColumnas, imagenResourceId, colorSolido }`.
- `documento`: `{ tipoContenido ∈ {'texto',...}, contenido: string, formato ∈ {'markdown','html'}, url: string }`.

### Card proportion catalog

[src/core/cardProportions.js#CARD_PROPORTIONS](../../../src/core/cardProportions.js) — `{ value, label, ratio, shape ∈ {'rect','hex','triangle','circular'} }`. Poker/tarot/square/circular/hex/triangle/free.

## Linked copies

- Created via `createCopy(component, components)` → id `{originalId}-COPY-{NNN}` (`NNN` = first free 3-digit int among siblings). `copyOf = originalId`, `sincronizado = true`.
- `state.replaceComponent(originalId, updated)` propagates synced fields to every `copyOf === originalId` via [component.js#syncCopyWithOriginal](../../../src/core/component.js).
- Synced: `type, name, image, width, height, profundidad, colorExtrusion, all *tooltip*/*titulo* fields, subirAlMoverInteractuar, etiquetaIds, interaccionesDesactivadas, accionClickDerecho, config/design properties`.
- `NON_SYNCED_PROPERTY_KEYS` = per-type interaction state never propagated: `dado.resultadoActual`, `carta.caraActual`.
- `x`, `y`, `order` of a copy: never touched.
- `bloqueado`/`oculto`: synced only while `copy.sincronizado !== false`; setting either directly on a synced copy flips it to `sincronizado = false`.
- [gotcha] `removeComponent(originalId)` cascade-deletes every copy of that original.
- If the original's `id` changes, copy ids are renamed (`renameCopyId`, prefix swap, `-COPY-NNN` suffix kept).

## Clones

`cloneComponent(component, components)` → id `{rootId}({n})` (`rootId` = base id minus any `(n)` suffix — clones of clones share the root family). Independent copy (no `copyOf` link), `x/y + 30`, `order = null`, `groupId = null`.

## Resource

[src/core/resource.js](../../../src/core/resource.js).

```
Resource = { id: string, name: string, type: string ∈ {'imagen','tipografia'}, dataUrl: string, fileName: string, mimeType: string }
```

- `resourceTypeForFileName(name)`: extension allow-list → `'imagen'` | `'tipografia'` | `null`. Images: `png jpg jpeg gif svg webp`. Fonts: `ttf otf woff woff2`.
- Raster images (`png jpg jpeg`) converted to WebP on upload ([imageConversion.js](../../../src/core/imageConversion.js), quality 0.92).
- `DEFAULT_RESOURCES` ([src/data/defaultResources.js](../../../src/data/defaultResources.js)): seeded once on a brand-new session. Fixed string ids (filename minus extension), not UUIDs.
- `isResourceInUse(id, components)` / `getComponentsUsingResource(id, components)`: **deep recursive walk** of every component's `properties` + `image` — blocks deletion of an in-use resource.

## Tag ("Etiqueta")

[src/core/tag.js](../../../src/core/tag.js). `Tag = { id: string, name: string }`.
- Membership is on the component: flat `etiquetaIds: string[]`, many-to-many.
- `getComponentsUsingTag(tagId, components)` — components whose `etiquetaIds` includes `tagId`.
- `isTagNameTaken` — case-insensitive, trimmed.

## Group (component grouping)

[src/core/group.js](../../../src/core/group.js). Registry of shared properties for a set of components with the same `groupId`.

```
Group = {
  id: string,                 # NOT auto-generated: nextGroupId() → 'grupo-N', or user-edited in ui/groupModal.js
  bloqueado: string ∈ {'ninguno','juego','todos'} = 'ninguno',
  mostrarTooltip: bool = false,
  mostrarTitulo: bool = false,
  subirAlMoverInteractuar: bool = false,
  oculto: bool = false,
  etiquetaIds: string[] = [],
}
```

- `getEffectiveGeneralProps(component, groups)`: **while `component.groupId` resolves to a registered group, that group's general props override the component's own** (`bloqueado, oculto, mostrarTooltip, mostrarTitulo, subirAlMoverInteractuar, etiquetaIds`). Fallback to own props if `groupId` is null or unregistered.
- inv: a group with ≤1 member is invalid → `state.removeComponent` auto-dissolves it (members' `groupId` → null, registry entry destroyed).
- `deriveMissingGroups(components, existingGroups)`: backfill — one default `Group` per distinct `groupId` present in `components` with ≥2 members and no existing registry entry.

## Persistence

[src/core/persistence.js](../../../src/core/persistence.js).

| Concern | Value |
|---|---|
| localStorage key | `'bgfactory:state'` — single slot per browser profile |
| Save payload | `{ version, components, panelState, resources, resourcePanelState, resourcesSeeded, tags, tagPanelState, componentGroups, appTitle }` |
| Save failure | quota / other error swallowed silently, app continues |
| `parseState(raw)` reject | `{error:true}` if JSON invalid, `version !== CURRENT_VERSION`, or `components` not array |
| Legacy key reads | `tags` ← `tags ?? groups ?? decks`; `tagPanelState` ← `tagPanelState ?? groupPanelState ?? deckPanelState` |
| `readSeedState()` | reads `<script type="application/json" id="initial-state">` embedded in the document; used when no localStorage |
| `parseImportedComponents(raw)` | [gotcha] **no version check** — importing a file from another app version is the main use case, only requires `components` to be an array |
| Export format | `buildComponentsExport()` → `{ version, components, resources, tags, componentGroups, appTitle }` — panel/UI state deliberately excluded |

## Versioning

[src/data/version.js](../../../src/data/version.js): `CURRENT_VERSION = 'v{NNNNN}'` (currently `v00230`). Single source of truth. `build.py` increments it on every build. Independent of any change/fix code.
