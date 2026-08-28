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

Seeded at bootstrap (minimal level). `pv-do` extends this over time; nodes without `anchor:` and without `=`/`:` are provisional concept placeholders pending a code anchor.

```
# --- core state ---
state                                     concept.   anchor: src/core/state.js
state.mode                                concept.   anchor: src/core/state.js#MODES
state.mode.value: enum in {play, edit} = play
state.components                          concept.   anchor: src/core/state.js  (state.components array)
state.components.order.inv:               assertion (non-scalar -> notation block)
    inv: forall c in state.components . c.order in {1..state.components.length}
    inv: order values are a contiguous permutation of 1..N (compactOrders)
state.resources                           concept.   anchor: src/core/state.js  (state.resources array)
state.tags                                concept.   anchor: src/core/state.js  (state.tags array)
state.groups                              concept.   anchor: src/core/state.js  (state.groups array; group-property registry)
state.resourcesSeeded                     concept.   anchor: src/core/state.js#getResourcesSeeded
state.resourcesSeeded.value: boolean = false

# --- event bus ---
eventBus                                  concept.   anchor: src/core/eventBus.js
eventBus.on                               concept.   anchor: src/core/eventBus.js#on
eventBus.emit                             concept.   anchor: src/core/eventBus.js#emit
eventBus.events: enum in {mode:changed, components:changed, panelState:changed, resources:changed, resourcePanelState:changed, tags:changed, tagPanelState:changed, groups:changed, appTitle:changed}

# --- domain model ---
component                                 concept.   anchor: src/core/component.js#createComponent
component.type: string = 'generico'       concept.   (free string; known: carta, mazo, dado, tableroSimple, tableroPersonalizado, texto, documento)
component.copyOf?: string                 concept.   anchor: src/core/component.js  (linked-copy back-reference; null = not a copy)
component.groupId?: string                concept.   anchor: src/core/component.js  (grupo-N membership; null = ungrouped)
component.etiquetaIds: string[]           concept.   anchor: src/core/component.js  (tag membership)
component.bloqueado: enum in {ninguno, juego, todos} = ninguno
resource                                  concept.   anchor: src/core/resource.js#createResource
resource.type: enum in {imagen, tipografia}   anchor: src/core/resource.js#RESOURCE_TYPES
tag                                       concept.   anchor: src/core/tag.js#createTag
group                                     concept.   anchor: src/core/group.js#createGroup

# --- persistence ---
persistence                              concept.   anchor: src/core/persistence.js
persistence.storageKey.value = 'bgfactory:state'   anchor: src/core/persistence.js  (STORAGE_KEY)
persistence.load.rule:                    assertion (non-scalar -> notation block)
    pre:  raw = localStorage.getItem('bgfactory:state')
    post: raw = null -> load returns null (fall back to embedded seed)
    post: JSON.parse fails OR parsed.version != CURRENT_VERSION OR not Array(parsed.components) -> returns { error: true }
persistence.seed                          concept.   anchor: src/core/persistence.js#readSeedState  (<script type="application/json" id="initial-state"> in index.html)
persistence.export                        concept.   anchor: src/core/persistence.js#buildComponentsExport  (version-independent JSON: components, resources, tags, componentGroups, appTitle)
version.value = 'v00230'                  anchor: src/data/version.js#CURRENT_VERSION

# --- build ---
build.deliverable                         concept.   anchor: src/scripts/build.py  (single self-contained index-v{XXXX}.html; JS/CSS/assets inlined as data URIs)
build.decision.no-node                    decision.  no code anchor  (build is pure Python; project ships without a package.json)

# --- security ---
sanitizeHtml                              concept.   anchor: src/core/sanitizeHtml.js#sanitizeHtml
sanitizeHtml.rule:                        assertion (non-scalar -> notation block)
    post: removes <script>; removes on* attributes; removes href/src with javascript: protocol
    [gotcha] denylist, not allowlist -- does NOT strip <iframe>/<object>/<svg><script>/<style>/srcdoc/meta-refresh
```
