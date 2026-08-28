# 004 — Data model and persisted shape
**Area**: Architecture

## Component

`model.component` — anchor: src/core/component.js#createComponent

```
id: string                              crypto.randomUUID() for new; derived ids for clone `(n)` / copy `-COPY-NNN`
type: string ∈ {carta, mazo, dado, tableroSimple, tableroPersonalizado, texto, documento, generico}
name: string = ""
properties: object = {}                 type-specific bag
image: string | null = null             resource id
x: number = 0
y: number = 0
width: number | null = null
height: number | null = null
profundidad: number = 0                  3D extrusion thickness
colorExtrusion: string | null = null
bloqueado: string ∈ {ninguno, juego, todos} = "ninguno"
mostrarTooltip: bool = false
tooltipTexto: string = ""
mostrarTitulo: bool = false
tituloTexto: string = ""
tituloColorTexto: string = "#000000"
tituloColorFondo: string = "#ffffff"
tituloFondoTransparencia: number = 0
subirAlMoverInteractuar: bool = false    z-lift on move/interact
oculto: bool = false                     hidden from players in play mode
etiquetaIds: string[] = []               tag membership; flat first-level
order: number | null = null             shared 1..N stacking index; assigned/recomputed by state.js
copyOf: string | null = null            linked-copy: id of original
sincronizado: bool = true               linked-copy: while true, bloqueado/oculto follow original
groupId: string | null = null
interaccionesDesactivadas: string[] = []
accionClickDerecho: string ∈ {ninguno, menuContextual} = "ninguno"   (legacy saves migrate to "menuContextual")
```

- `model.component.order` — global namespace shared by ALL components, contiguous 1..N. `addComponent` pushes to front (order 1, others +1). `compactOrders` re-normalizes on load/remove. anchor: src/core/state.js#compactOrders
- `model.component.copy.sync` — `syncCopyWithOriginal` propagates type/name/image/size/depth/title/tooltip/tags/interaction-flags/design-`properties` from original to every `copyOf === original.id`. Interaction-state keys are NOT synced: `dado.resultadoActual`, `carta.caraActual`. `x`/`y`/`order` never synced. `bloqueado`/`oculto` synced only while `copy.sincronizado`. anchor: src/core/component.js#syncCopyWithOriginal
- `model.component.copy.cascade` — `removeComponent(originalId)` also removes every linked copy. anchor: src/core/state.js#removeComponent

## Resource

`model.resource` — anchor: src/core/resource.js#createResource

```
id: string = crypto.randomUUID()
name: string = ""
type: string ∈ {imagen, tipografia}
dataUrl: string                         embedded data: URI
fileName: string = ""
mimeType: string = ""
```

- `model.resource.webp` — uploaded png/jpg/jpeg converted to WebP (canvas, q=0.92); original kept on failure or other type. anchor: src/core/imageConversion.js#convertImageToWebP
- `model.resource.inUse` — `getComponentsUsingResource` scans `component.image` + recursive `properties` values. Deletion of an in-use resource is blocked. anchor: src/core/resource.js#getComponentsUsingResource

## Tag

`model.tag` — anchor: src/core/tag.js#createTag

```
id: string = crypto.randomUUID()
name: string = ""
```

- Component ↔ tag is many-to-many via `component.etiquetaIds`.

## Group

`model.group` — anchor: src/core/group.js#createGroup

```
id: string                              caller-assigned (nextGroupId → "grupo-N"), never auto
bloqueado: string ∈ {ninguno, juego, todos} = "ninguno"
mostrarTooltip: bool = false
mostrarTitulo: bool = false
subirAlMoverInteractuar: bool = false
oculto: bool = false
etiquetaIds: string[] = []
```

- `model.group.effectiveProps` — while `component.groupId != null` and a matching group record exists, `getEffectiveGeneralProps` returns the GROUP's general props, overriding the component's own. Fallback to component's own if no matching record. anchor: src/core/group.js#getEffectiveGeneralProps
- `model.group.autoDissolve` — a group reaching ≤1 member after a deletion auto-dissolves; its record is destroyed, members' `groupId` cleared. anchor: src/core/state.js#removeComponent

## Persisted / exported shape

`model.persist.shape` — anchor: src/core/persistence.js#saveState

```
version: string                         = CURRENT_VERSION
components: Component[]
panelState, resourcePanelState, tagPanelState: object   (autosave only; export omits)
resourcesSeeded: bool
tags: Tag[]
componentGroups: Group[]
appTitle: string
```

- `model.persist.export` — `buildComponentsExport` = `{ version, components, resources, tags, componentGroups, appTitle }` (no panel states). anchor: src/core/persistence.js#buildComponentsExport
- `model.persist.aliases` — `parseState` back-compat (rename history "Mazo"→"Grupo"→"Etiqueta"): `tags` ← `groups` ← `decks`; `tagPanelState` ← `groupPanelState` ← `deckPanelState`. `componentGroups` has NO alias (`groups` key is reserved as the legacy alias of `tags`). anchor: src/core/persistence.js#parseState

## Load-time migrations

`model.migrations` — all in `src/core/state.js#loadComponents`, run in order, all best-effort (never block startup):

| Fn | Effect |
|---|---|
| `migrateFichas` | `type "ficha"` → `"carta"` (via `fichaMigration.js`) |
| `migrateCartaMedidasReales` | card design-units → real pixels (scale by `width/CARD_DESIGN_WIDTH`), set `properties.medidasReales` |
| `migrateGrupoIdToEtiquetaIds` | scalar `grupoId` / array `grupoIds` → `etiquetaIds: string[]` |
| `migrateDeckIdToEtiqueta` | `properties.deckId` → append to `etiquetaIds` |
| `migrateBloqueado` | `bloqueado` bool → 3-value (`true`→`"juego"`, `false`→`"ninguno"`) |
| `migrateAccionClickDerecho` | missing `accionClickDerecho` → `"menuContextual"` |
| `migrateTableroSimple` | `type "tablero"` → `"tableroSimple"` |
| `compactOrders` | normalize `order` to contiguous 1..N |

Plus `deriveMissingGroups(components, savedGroups)` in `main.js`: one default group record per distinct `groupId` (2+ members) with no existing record. anchor: src/core/group.js#deriveMissingGroups
