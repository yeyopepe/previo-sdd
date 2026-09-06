# 003 — Persistence & domain model

**Area**: Architecture

## Persisted shape

`localStorage['bgfactory:state']` — one JSON object, written whole on every state change by `core/persistence.js#saveState`.

```
{
  version: string                 // must === CURRENT_VERSION on load, else { error: true }
  components: Component[]          // required; must be Array or load fails
  panelState: object|null
  resources: Resource[]
  resourcePanelState: object|null
  resourcesSeeded: boolean         // true once default resources have been seeded
  tags: Tag[]
  tagPanelState: object|null
  componentGroups: Group[]         // group-property registry; NOT under key `groups` (legacy alias of `tags`)
  appTitle: string
}
```

- `panelState` / `resourcePanelState` / `tagPanelState` shape: `{ collapsed: boolean, position: {x,y}|null, width: number|null, height: number|null }`.
- Embedded seed: `<script type="application/json" id="initial-state">` in `index.html` — same shape, read by `readSeedState` only when `localStorage` has nothing.
- Export JSON (`buildComponentsExport`): `{ version, components, resources, tags, componentGroups, appTitle }` — no panel state; parsed by `parseImportedComponents` with **no** version check.

## Load contract

```
persistence.load.rule:
  pre:  raw = localStorage.getItem('bgfactory:state')
  post: raw = null                                   -> return null   (caller falls back to seed)
  post: JSON.parse(raw) throws                       -> return { error: true }
  post: parsed.version != CURRENT_VERSION            -> return { error: true }
  post: not Array.isArray(parsed.components)         -> return { error: true }
  post: otherwise                                    -> return parsed slots + legacy-alias resolution
```

`{ error: true }` on browser autosave → `main.js` shows an error modal and seeds default resources. A version mismatch **when importing a file** is not an error (primary use case).

Legacy key aliases resolved by `parseState` / `parseImportedComponents`:

| Current key | Also read from (if current absent) |
|---|---|
| `tags` | `groups`, then `decks` |
| `tagPanelState` | `groupPanelState`, then `deckPanelState` |

## Load-time migrations

`core/state.js#loadComponents` runs these in order, in place, best-effort, never throwing:

| # | Migration | From → To |
|---|---|---|
| 1 | `migrateFichas` | type `'ficha'` → `'carta'` (via `fichaMigration.js`; sets `medidasReales: true`) |
| 2 | `migrateCartaMedidasReales` | card shapes/textBoxes in abstract design units → real pixels (×`width/CARD_DESIGN_WIDTH`) |
| 3 | `migrateGrupoIdToEtiquetaIds` | scalar `grupoId` / array `grupoIds` → `etiquetaIds: string[]` |
| 4 | `migrateDeckIdToEtiqueta` | `properties.deckId` → appended to `etiquetaIds` |
| 5 | `migrateBloqueado` | boolean `bloqueado` → `'ninguno'` \| `'juego'` \| `'todos'` (`true`→`'juego'`, `false`→`'ninguno'`) |
| 6 | `migrateAccionClickDerecho` | missing `accionClickDerecho` → `'menuContextual'` (new components start `'ninguno'`) |
| 7 | `migrateTableroSimple` | type `'tablero'` → `'tableroSimple'` |

Then `compactOrders(components)`. Separately, `main.js` calls `deriveMissingGroups` to backfill a default `componentGroups` entry per `groupId` present on components but absent from the registry.

## Component model

`core/component.js#createComponent` — generic entity, no per-type subclass. Type-specific data lives in `properties: {}` (free key-value). Fields (defaults shown):

```
id: string                              // crypto.randomUUID()
type: string = 'generico'               // free; known: carta|mazo|dado|tableroSimple|tableroPersonalizado|texto|documento
name: string = ''
properties: object = {}                 // per-type config + interaction state
image: string|null = null
x: number = 0
y: number = 0
width: number|null = null
height: number|null = null
profundidad: number = 0                  // 3D extrusion thickness
colorExtrusion: string|null = null
bloqueado: enum in {ninguno, juego, todos} = ninguno
mostrarTooltip: boolean = false
tooltipTexto: string = ''
mostrarTitulo: boolean = false
tituloTexto: string = ''
tituloColorTexto: string = '#000000'
tituloColorFondo: string = '#ffffff'
tituloFondoTransparencia: number = 0
subirAlMoverInteractuar: boolean = false
oculto: boolean = false
etiquetaIds: string[] = []
order: number|null = null               // stacking; assigned/recomputed by core/state.js
copyOf: string|null = null              // linked-copy back-reference
sincronizado: boolean = true            // while true, copy syncs bloqueado/oculto from original
groupId: string|null = null             // 'grupo-N' membership
interaccionesDesactivadas: string[] = []
accionClickDerecho: string = 'ninguno'  // new components; migrated ones -> 'menuContextual'
```

Type-specific `properties` keys are read by that type's pure module (`core/deck.js`, `core/dice.js`, `core/cardProportions.js`, …) and its modal — not enumerated here (see the code).

## Invariants

```
state.components.order.inv:
  inv: forall c in state.components . c.order in {1..state.components.length}
  inv: order is a contiguous permutation of 1..N   (compactOrders / reorderComponent / reorderGroupBlock maintain it)

group.dissolve.rule:
  post: after removeComponent, any group left with <= 1 member is dissolved:
        its members' groupId set to null AND its registry entry removed from state.groups
```

## Linked copies (`copyOf`)

- `replaceComponent(id, updated)` on an original (`!updated.copyOf`) propagates synced fields to every `c` with `c.copyOf === id` via `syncCopyWithOriginal`; renames each copy's `id` if the original's `id` changed (`renameCopyId`).
- `removeComponent(id)` cascades: also removes every `c` with `c.copyOf === id`.
- `NON_SYNCED_PROPERTY_KEYS` — per type, `properties` keys that are game interaction state and never sync: `dado: ['resultadoActual']`, `carta: ['caraActual']`.
- [gotcha] `x`, `y`, `order` of a copy are never synced from the original. `bloqueado`/`oculto` sync only while `copy.sincronizado !== false`.

## Id formats

| Kind | Format | Generator |
|---|---|---|
| Component | `crypto.randomUUID()` | `createComponent` |
| Clone | `${rootId}(${n})`, n = first free int | `nextCloneId` |
| Linked copy | `${originalId}-COPY-${nnn}`, 3-digit, first free | `nextCopyId` |
| Group | `grupo-${n}`, first free int | `nextGroupId` |
