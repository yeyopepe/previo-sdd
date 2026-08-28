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

### arch — architecture

```
arch.layer.data                          concept.  src/data/
arch.layer.core                          concept.  src/core/
arch.layer.modes                         concept.  src/modes/
arch.layer.ui                            concept.  src/ui/
arch.layer.bootstrap                     concept.  anchor: src/main.js
arch.layer.ui.no-modes-import:           assertion
    inv: no file under src/ui/ imports from src/modes/
arch.state.eventBus                      concept.  anchor: src/core/eventBus.js
arch.state.store                         concept.  anchor: src/core/state.js
arch.state.wiring                        concept.  anchor: src/main.js
arch.render.model:                       assertion
    inv: on components:changed or mode:changed, the active mode's DOM is fully rebuilt
arch.persist                             concept.  anchor: src/core/persistence.js
arch.persist.key = "bgfactory:state"     assertion (scalar).  anchor: src/core/persistence.js#STORAGE_KEY
arch.persist.parseState.reject:          assertion
    post: parseState -> {error:true} when JSON invalid, or parsed.version != CURRENT_VERSION, or not Array.isArray(parsed.components)
arch.startup                             concept.  anchor: src/main.js
arch.build.pipeline                      concept.  anchor: src/scripts/build.py
arch.build.version.format = "v{NNNN}"    assertion (scalar).  anchor: src/data/version.js#CURRENT_VERSION
arch.decision.single-html-deliverable    decision.  no code anchor. one self-contained HTML, no server/accounts/runtime-network
arch.decision.full-rebuild-render        decision.  no code anchor. no diffing; every state change re-creates the mode DOM
```

### model — domain data model

```
model.component                          concept.  anchor: src/core/component.js#createComponent
model.component.order:                   assertion
    inv: components' `order` form a contiguous 1..N sequence across ALL components
model.component.copy.sync                concept.  anchor: src/core/component.js#syncCopyWithOriginal
model.component.copy.sync.nonSynced = {dado.resultadoActual, carta.caraActual}   assertion (scalar)
model.component.copy.cascade:            assertion
    post: removeComponent(id) also removes every component with copyOf == id
model.resource                           concept.  anchor: src/core/resource.js#createResource
model.resource.type ∈ {imagen, tipografia}   assertion (scalar)
model.resource.webp                      concept.  anchor: src/core/imageConversion.js#convertImageToWebP
model.resource.inUse                     concept.  anchor: src/core/resource.js#getComponentsUsingResource
model.tag                               concept.  anchor: src/core/tag.js#createTag
model.group                             concept.  anchor: src/core/group.js#createGroup
model.group.effectiveProps              concept.  anchor: src/core/group.js#getEffectiveGeneralProps
model.group.effectiveProps.rule:         assertion
    inv: component.groupId != null ∧ group record exists ⟹ general props come from the group, not the component
model.group.autoDissolve:               assertion
    post: a group with <= 1 member after a deletion is removed; members' groupId cleared
model.persist.shape                     concept.  anchor: src/core/persistence.js#saveState
model.persist.export                    concept.  anchor: src/core/persistence.js#buildComponentsExport
model.persist.aliases                   concept.  anchor: src/core/persistence.js#parseState. tags<-groups<-decks; tagPanelState<-groupPanelState<-deckPanelState
model.migrations                        concept.  anchor: src/core/state.js#loadComponents. best-effort, never block startup
```

### ui — presentation / style

Style tokens and UI conventions hang here. See `styleBibleDocDir` for their values.

```
ui.table                               concept.  anchor: src/ui/table.js
ui.table.zoom.min = 0.5                 assertion (scalar).  anchor: src/ui/table.js#minZoom
ui.table.zoom.max = 2.5                 assertion (scalar).  anchor: src/ui/table.js#maxZoom
ui.tokens                              concept.  anchor: src/styles/main.css  (:root custom properties). values in styleBibleDocDir/001
ui.tokens.accent-blue.rule:            assertion
    inv: --accent-blue (#2c7dd8) is used only for interactive or selected state, never as a brand fill
ui.tokens.radius.sm = "4px"            assertion (scalar).  controls
ui.tokens.radius.lg = "8px"            assertion (scalar).  containers
ui.tokens.transition-fast = "150ms ease"   assertion (scalar)
ui.button.accept                      concept.  .btn-accept, background --accent-blue
ui.button.cancel                      concept.  .btn-cancel / .btn-duplicate, background --bg-subtle
ui.button.eliminar                    concept.  .btn-eliminar, background --error
ui.button.naming-exception:            assertion
    inv: footer/standalone action buttons (.btn-cancel/.btn-accept/.btn-eliminar/.btn-sacar/...) are flat classes, not BEM blocks
ui.panel                              concept.  anchor: src/modes/edit/editMode.js. 3 draggable/resizable/collapsible floating panels
ui.modal.contract                     concept.  .modal-overlay > .modal > .modal__footer with .btn-cancel / .btn-accept / .btn-eliminar
ui.shortcuts                          concept.  anchor: src/ui/globalShortcuts.js. every shortcut mirrors an existing button/action
ui.selection.outline:                  assertion
    inv: edit-mode selection outline — blue = directly clicked component; gray = rest of its group
ui.icons.inline-svg:                   assertion
    inv: icons are inline <svg> built in JS per use, 24x24, viewBox 0 0 24 24, fill=none, stroke=currentColor, stroke-width=2; no shared icon file
ui.lang:                               assertion
    inv: user-facing copy and domain identifiers are Spanish; infrastructure identifiers are English
```
