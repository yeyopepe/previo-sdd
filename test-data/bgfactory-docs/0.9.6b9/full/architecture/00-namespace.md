# 00 — Namespace

Single canonical name tree for this project. Every concept and every assertion (architecture and style alike) has exactly one path here. Style concepts live on the `ui.*` branch -- there is no separate namespace file for the style bible.

## Notation

Compact notation for structured data:

```
field: type                  required field
field?: type                 optional field
field: type = value          default value
field: type in {a, b, c}     enum / allowed set
field: type [min..max]       range
```

Invariants -- executable vs declarative:

- `assert <expr>` when there is a program point where the condition can be checked with the values at hand.
- declarative `inv: ...` / `pre:` / `post:` (propositional logic, `and or not -> forall`) when it quantifies over an abstract set, talks about an FSM state, or a non-observable global property.
- If both forms fit, the `assert` governs and the declarative one is a restatement.

Boundary between a leaf's two forms:

- `path = <scalar>` -- a simple value (number, enum, boolean).
- `path:` then a notation block -- an assertion with logical structure (a contract, a logic expression).

## Tree

Segment order: aggregate to part, module to detail. `<area>.<aggregate>.<entity>.<field-or-assertion>`.

- `auth.token.session.exp` -- OK (area auth -> aggregate token -> entity session -> field exp)
- `auth.session.token.exp` -- wrong (inverts aggregate and entity)

Domain terms with no standard English translation: if the concept has a code symbol, the path uses the symbol name; if it has none, the slug may stay in the project's language for that one node (e.g. `billing.recargo-equivalencia`), noted here as an explicit exception with a one-line approximate-English gloss.

Paths use code symbol names as coded (Spanish identifiers: `carta`, `mazo`, `dado`, `bloqueado`, `etiquetaIds`, `caraFrontal`, `disposicion`, ...). No standard-English-translation exceptions needed — every domain term here has a code symbol.

## Tree

### app

```
app.build                                 concept.  anchor: src/scripts/build.py
app.build.output = src/_output/versions/index-v{NNNNN}.html
app.build.deliverable.self-contained:
    inv: output HTML has no external references — JS, CSS, images, fonts all inlined (data: URIs / <style> / <script>)
app.build.import-support:
    inv: only  import { named } from '...'  and  export function / export const  are supported
         (no default/namespace/side-effect import, no export default / export {} / export let / export class)
app.build.version-bump.rule:
    pre:  version.js has CURRENT_VERSION = 'v{N}'
    post: CURRENT_VERSION' = 'v{N+1}', written to disk before bundling
app.version.current                        concept.  anchor: src/data/version.js#CURRENT_VERSION
app.version.format = 'v{NNNNN}'
app.mode                                   concept.  anchor: src/core/state.js#MODES
app.mode.values in {'play', 'edit'}
```

### arch

```
arch.layers                               concept.
arch.layers.order = ['data', 'core', 'ui', 'modes']   # import direction: later may import earlier
arch.decision.ui-cannot-import-modes      decision.  no code anchor
    rule: files under src/ui/ must not import from src/modes/
    consequence: cross-mode ops (e.g. deck.sacarCartaDeMazo) live in src/core/state.js
arch.decision.generic-component-no-subclasses  decision.  no code anchor
    rule: single Component shape; `type: string` branches behavior in ui/ and modes/
```

### state

```
state.singleton                           concept.  anchor: src/core/state.js
state.singleton.shape:
    { mode, components: Component[], resources: Resource[], tags: Tag[], groups: Group[] }
state.persist.decision.synchronous-full   decision.  anchor: src/main.js
    rule: every *:changed event triggers a full synchronous saveState() to localStorage; no debounce
    post: localStorage['bgfactory:state'] reflects state after every mutation
state.persist.save-failure:
    inv: a localStorage quota/write error is swallowed; app continues
state.load.migrations                      concept.  anchor: src/core/state.js#loadComponents
state.load.migrations.order = ['migrateFichas','migrateCartaMedidasReales','migrateGrupoIdToEtiquetaIds','migrateDeckIdToEtiqueta','migrateBloqueado','migrateAccionClickDerecho','migrateTableroSimple','compactOrders']
state.load.migrations.contract:
    inv: every migration is in-place, best-effort, never throws (must not block startup)
state.load.seed-flag-order.rule:
    pre:  no localStorage, or hydrating from saved state
    post: resourcesSeeded hydrated BEFORE loadComponents/loadResources (those autosave synchronously)
state.transient.selection                  concept.  anchor: src/modes/edit/editMode.js#selectedComponentIds
    inv: kept in module-level vars outside the render fn; survives components:changed remount; not persisted
```

### events

```
events.bus                                concept.  anchor: src/core/eventBus.js
events.bus.api = ['on', 'off', 'emit']
events.bus.delivery = 'synchronous'
events.catalog = ['mode:changed','components:changed','panelState:changed','resources:changed','resourcePanelState:changed','tags:changed','tagPanelState:changed','appTitle:changed']
events.alias.tags:changed = ['decks:changed', 'groups:changed']       # legacy names still emitted/listened
events.alias.tagPanelState:changed = ['deckPanelState:changed', 'groupPanelState:changed']
events.gotcha.groups-changed-is-tags:
    inv: 'groups:changed' is a legacy alias of 'tags:changed', NOT an event for the component-grouping registry
```

### component

```
component                                 concept.  anchor: src/core/component.js#createComponent
component.id = crypto.randomUUID()  |  derived clone/copy id
component.type: string = 'generico'
component.type.known in {'carta','mazo','dado','tableroSimple','tableroPersonalizado','documento','texto','generico'}
component.type.extinct: 'ficha' -> 'carta' ; 'tablero' -> 'tableroSimple'   (migrated on load)
component.properties: object = {}          # type-specific; defaults in src/ui/componentModal.js
component.bloqueado in {'ninguno', 'juego', 'todos'} = 'ninguno'
component.order: number | null             # 1..n stacking; assigned/recomputed by src/core/state.js
component.etiquetaIds: string[] = []       # tag membership, flat, many-to-many
component.accionClickDerecho in {'ninguno', 'menuContextual'} = 'ninguno'
component.copy                             concept.  anchor: src/core/component.js#createCopy
component.copy.id.format = '{originalId}-COPY-{NNN}'
component.copy.link: copyOf = originalId, sincronizado: bool = true
component.copy.sync.rule:
    post: replaceComponent(originalId, u) propagates synced fields to every c where c.copyOf == originalId
    inv:  x, y, order of a copy are never propagated
    inv:  dado.resultadoActual and carta.caraActual (NON_SYNCED_PROPERTY_KEYS) are never propagated
    inv:  bloqueado/oculto propagate only while copy.sincronizado != false
component.copy.cascade-delete:
    post: removeComponent(originalId) also removes every c where c.copyOf == originalId
component.clone                            concept.  anchor: src/core/component.js#cloneComponent
component.clone.id.format = '{rootId}({n})'   # rootId strips any trailing (n); no copyOf link
component.face                             concept.  anchor: src/ui/componentModal.js#DEFAULT_CARTA_PROPERTIES
    shared shape for carta.caraFrontal/caraTrasera and tableroPersonalizado.cara
    { imagenResourceId, ajusteImagen:{zoom,posX,posY,rotation?}, formas:[], textBoxes:[], bordeColor, bordeGrosor, transparenciaImagen }
component.carta.caraActual in {'frontal', 'trasera'} = 'trasera'
component.carta.medidasReales = true       # new cards; old cards migrated to real-px
component.mazo.cartaIds: string[] = []
component.mazo.disposicion in {'arriba','abajo','derecha','izquierda'}
component.dado.modoCaras in {'numeroMaximo', 'lista'}
```

### resource

```
resource                                  concept.  anchor: src/core/resource.js#createResource
resource.shape = { id, name, type, dataUrl, fileName, mimeType }
resource.type in {'imagen', 'tipografia'}   # anchor: src/core/resource.js#RESOURCE_TYPES
resource.upload.allowlist.image = ['png','jpg','jpeg','gif','svg','webp']
resource.upload.allowlist.font = ['ttf','otf','woff','woff2']
resource.upload.raster-to-webp.rule:
    pre:  uploaded file extension in {png, jpg, jpeg}
    post: stored dataUrl is WebP, re-encoded through canvas   # anchor: src/core/imageConversion.js
resource.in-use.detection:
    inv: isResourceInUse walks component.image + every nested value of component.properties (deep)
resource.defaults                         concept.  anchor: src/data/defaultResources.js#DEFAULT_RESOURCES
    inv: seeded once on a brand-new session; ids are fixed strings, not UUIDs
```

### tag

```
tag                                       concept.  anchor: src/core/tag.js#createTag
tag.shape = { id, name }
tag.membership:
    inv: stored on the component as etiquetaIds: string[]; a component may belong to many tags
tag.history: name concept was renamed 'Mazo' -> 'Grupo' -> 'Etiqueta'   # legacy persisted keys: decks, groups
```

### group

```
group                                     concept.  anchor: src/core/group.js#createGroup
group.shape = { id, bloqueado, mostrarTooltip, mostrarTitulo, subirAlMoverInteractuar, oculto, etiquetaIds }
group.id.format = 'grupo-N'               # anchor: src/core/component.js#nextGroupId ; not auto-generated at createGroup
group.decision.group-props-override-member  decision.  anchor: src/core/group.js#getEffectiveGeneralProps
    rule: while component.groupId resolves to a registered group, that group's general props override the component's own
group.auto-dissolve:
    inv: a group with <= 1 member is removed on state.removeComponent (members' groupId -> null, registry entry destroyed)
group.backfill                            concept.  anchor: src/core/group.js#deriveMissingGroups
    rule: one default Group per distinct groupId with >= 2 members and no existing registry entry
```

### deck

```
deck.sacarCartaDeMazo                     concept.  anchor: src/core/state.js#sacarCartaDeMazo
    rule: pull cartaId out of mazo.properties.cartaIds (any pile position), reveal face-up in the reveal zone
deck.reveal-zone                          concept.  anchor: src/core/deck.js#getMazoRevealZoneRect
    rule: rect adjacent to the side named by mazo.properties.disposicion (fallback 'derecha'), gap = MAZO_REVEAL_GAP = 20
deck.shuffle                              concept.  anchor: src/core/deck.js#shuffleCartaIds
    rule: Fisher-Yates + Math.random(), non-mutating
deck.decision.pure-compute-caller-applies  decision.  anchor: src/core/deck.js#computeSacarCartaDeMazo
    rule: computeSacarCartaDeMazo returns changes; caller applies via replaceComponent/reorderComponent
deck.cards-hidden-when-in-deck:
    inv: a card whose id is in getCartaIdsEnAlgunMazo(components) is not rendered as a standalone table component
```

### interactions

```
interactions.registry                     concept.  anchor: src/core/interactions.js#TYPE_INTERACTIONS
interactions.registry.keys = { dado: 'lanzar', carta: 'voltear', mazo: 'sacarCarta' }
interactions.active.rule:
    inv: isInteractionActive(c, key) == not c.interaccionesDesactivadas.includes(key)
```

### persistence

```
persistence.storage-key = 'bgfactory:state'   # anchor: src/core/persistence.js#STORAGE_KEY
persistence.slot:
    inv: single slot per browser profile
persistence.parseState.reject:
    inv: rejects if JSON invalid, or parsed.version != CURRENT_VERSION, or parsed.components not an array
persistence.legacy-key-reads:
    tags       <- parsed.tags ?? parsed.groups ?? parsed.decks
    tagPanelState <- parsed.tagPanelState ?? parsed.groupPanelState ?? parsed.deckPanelState
persistence.seed                          concept.  anchor: src/core/persistence.js#readSeedState
    rule: reads <script type="application/json" id="initial-state"> from the document; used when no localStorage
persistence.decision.import-skips-version-check  decision.  anchor: src/core/persistence.js#parseImportedComponents
    rule: parseImportedComponents has no version gate; only requires components to be an array
persistence.export.format = { version, components, resources, tags, componentGroups, appTitle }   # anchor: buildComponentsExport
    inv: panel/UI state is excluded from the export
```

### import

```
import.flow.modes: mode in {'añadir', 'overwrite'} ; conflictMode in {'sobrescribir', 'mantener ambos'}
import.merge                              concept.  anchor: src/core/importMerge.js#mergeImportedGame
    inv: pure — receives and returns plain data; caller applies to state
import.ficha-migration.rule:
    pre:  imported component.type == 'ficha'
    post: converted via fichaMigration; per-component errors surfaced (continue-without / abort)
import.group-merge.rule:
    overwrite -> imported groups only
    añadir    -> current groups + imported groups not colliding by id
    then deriveMissingGroups over merged components
```

### text-variables

```
text-variables                           concept.  anchor: src/core/textVariables.js#resolveTextVariables
    rule: substitute {name} in tooltipTexto / tituloTexto from a fixed per-type key set
text-variables.available = { mazo: {'cards_current'} }   # anchor: getAvailableVariables
text-variables.gotcha.leave-literal:
    inv: a {name} not applicable to the component's type is left literal, never replaced with empty string
```

### security

```
security.threat-model:
    inv: exported single .html reopens user content in a fresh session, possibly from file:// origin
security.sanitizeHtml                     concept.  anchor: src/core/sanitizeHtml.js#sanitizeHtml
    rule: detached <template>; remove all <script>; remove attrs whose lowercased name starts 'on';
          remove href/src matching /^\s*javascript:/i
security.decision.sanitize-denylist-not-allowlist  decision.  anchor: src/core/sanitizeHtml.js
    known gaps: <iframe>/<object>/<embed>, style attrs, srcdoc, data: URIs in href/src, formaction, SVG script
    gap: documento component embeds user url in an <iframe> with no sandbox attribute
    consequence: revisit allow-list sanitizer + iframe sandbox on any change to documento rendering or sanitizeHtml
security.markdown.rule:
    inv: marked output is always passed through security.sanitizeHtml before DOM insertion   # anchor: src/core/markdown.js
```

### globalShortcuts

```
globalShortcuts                           concept.  anchor: src/ui/globalShortcuts.js#initGlobalShortcuts
globalShortcuts.modal-contract = '.modal-overlay > .modal > .modal__footer  with .btn-cancel / .btn-accept / .btn-eliminar'
globalShortcuts.bindings:
    Escape -> top modal .btn-cancel
    Enter  -> top modal .btn-accept (not in <textarea>, not if disabled)
    Delete -> top modal .btn-eliminar ; else (edit mode, no modal) delete selection
    Arrows -> (edit mode, no modal) move selection 1px / Shift 10px
```

### ui

Style-bible concepts hang here. See [../style/INDEX.md](../style/INDEX.md).

```
ui.palette                                concept.  anchor: src/styles/main.css  :root
ui.palette.neutral: table = #c2c2c2, toolbar = #333333, card-bg = #f5f5f5
ui.palette.accent-blue = #2c7dd8   (dark #123a66, light #eaf3fc)
ui.palette.error = #d32f2f ; ui.palette.success = #2e7d32 ; ui.palette.section-accent = #5b5f97
ui.radius.sm = 4px    # controls (buttons, inputs)
ui.radius.lg = 8px    # containers (modals, panels, cards)
ui.shadow.1 = floating contact shadow (panels, game pieces)
ui.shadow.2 = overlay shadow (modals)
ui.transition.fast = 150ms ease
ui.font.family = 'system-ui, sans-serif'   ; ui.font.mono = 'ui-monospace, monospace'
ui.zindex.ladder = { panels: 15+, h1: 100, toolbar: 99, modal-overlay: 1000, toast: 1100, export-menu: 1200 }
ui.naming = 'BEM-ish block__element--modifier'
ui.naming.exception = standalone buttons .btn-cancel / .btn-accept / .btn-eliminar / .btn-sacar carry no block
ui.selection.outline:
    inv: dashed outline; blue = selected/hover, red = .is-copy, grey = .is-group-passenger
ui.piece.shadow.non-rect:
    inv: dice and hex/triangle cards use filter: drop-shadow (follows silhouette), not box-shadow
```
