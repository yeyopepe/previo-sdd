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

Commented example (delete once real nodes exist):

```
# auth.token.session                       concept.   anchor: src/auth/token.ts#SessionToken
# auth.token.session.ttl.value = 3600      assertion (scalar)
# auth.token.session.refresh.rule:         assertion (non-scalar -> notation block)
#     pre:  state in {AUTHENTICATED, EXPIRED} and now - token.exp < 7d
#     post: token'.exp = now + auth.token.session.ttl.value
# auth.decision.circuit-breaker-over-retry decision.  no code anchor
# ui.grid.columns = 16                     style assertion (same tree)
```

Seeded at init (minimal). `pv-do` extends this over time.

```
state.store                              concept.  anchor: src/core/state.js
state.store.mode = 'play' | 'edit'       assertion (scalar). anchor: src/core/state.js#MODES
state.store.components                   concept.  anchor: src/core/state.js (state.components)
state.store.resources                    concept.  anchor: src/core/state.js (state.resources)
state.store.tags                         concept.  anchor: src/core/state.js (state.tags)
state.store.groups                       concept.  anchor: src/core/state.js (state.groups)
state.event-bus                          concept.  anchor: src/core/eventBus.js
state.event-bus.emit-on-mutation.rule:   assertion (non-scalar).
    every exported setter in src/core/state.js mutates in place, then emit('<domain>:changed')
    main.js subscribes each '<domain>:changed' to renderAll() and persistState()

persist.storage                          concept.  anchor: src/core/persistence.js
persist.storage.key = 'bgfactory:state'  assertion (scalar). anchor: src/core/persistence.js#STORAGE_KEY
persist.storage.load-guard.rule:         assertion (non-scalar).
    accept saved state iff parsed.version === data.version.current AND Array.isArray(parsed.components)
    else treat as no saved state
persist.seed.embedded                    concept.  anchor: src/core/persistence.js#readSeedState
persist.migration.ficha-to-carta         concept.  anchor: src/core/fichaMigration.js
data.version.current                     concept.  anchor: src/data/version.js#CURRENT_VERSION

component.model                          concept.  anchor: src/core/component.js#createComponent
component.model.id                       concept.  anchor: createComponent (crypto.randomUUID())
component.model.type                     concept.  free string; catalog in src/ui/componentTypeModal.js#COMPONENT_TYPES
component.model.order                    concept.  z-index; assigned/compacted by src/core/state.js
component.model.copyOf                   concept.  linked-copy link. anchor: src/core/component.js
component.copy.sync.rule:                assertion (non-scalar). anchor: src/core/state.js#replaceComponent
    on replaceComponent of an original (copyOf == null), propagate synced fields to every c where c.copyOf === id
component.group                          concept.  anchor: src/core/group.js#createGroup
component.group.dissolve.rule:           assertion (non-scalar). anchor: src/core/state.js#removeComponent
    a group left with <= 1 member is dissolved; its record is removed from state.groups
component.tag                            concept.  anchor: src/core/tag.js#createTag
resource.model                           concept.  anchor: src/core/resource.js#createResource
resource.type = 'imagen' | 'tipografia' assertion (scalar). anchor: src/core/resource.js#RESOURCE_TYPES
resource.upload.webp.rule:               assertion (non-scalar). anchor: src/core/imageConversion.js#convertImageToWebP
    png/jpg/jpeg gallery uploads convert to WebP (quality 0.92); original kept on failure

play.interactions.registry               concept.  anchor: src/core/interactions.js#TYPE_INTERACTIONS
play.interactions.by-type = { dado: 'lanzar', carta: 'voltear', mazo: 'sacarCarta' }   assertion (scalar).
deck.shuffle                             concept.  anchor: src/core/deck.js#shuffleCartaIds (Fisher-Yates + Math.random)

security.sanitize.user-html              concept.  anchor: src/core/sanitizeHtml.js#sanitizeHtml
security.sanitize.user-html.rule:        assertion (non-scalar).
    all user-authored HTML (document-viewer component) passes sanitizeHtml before DOM insertion
    sanitizeHtml strips <script>, inline event handlers, javascript: URLs
    marked.js output (src/core/markdown.js) is also routed through sanitizeHtml

build.pipeline                           concept.  anchor: src/scripts/build.py
build.output = 'src/_output/versions/index-vXXXX.html'   assertion (scalar). XXXX = data.version.current

ui.table.infinite                        concept.  anchor: src/ui/table.js (pan/zoom, module-level camera, not persisted)
ui.tokens                                concept.  anchor: src/styles/main.css (:root custom properties)
ui.modal.pattern                         concept.  anchor: DOM `.modal-overlay > .modal > .modal__footer`
ui.modal.pattern.footer-buttons = '.btn-cancel' | '.btn-accept' | '.btn-eliminar'   assertion (scalar). anchor: src/ui/globalShortcuts.js
```

