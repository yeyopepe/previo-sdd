# Flujo de desarrollo/build y persistencia

## Desarrollo y build

```
dev:
  serve(src/index.html) via static-server   [required: <script type="module"> fails under file://]
  src/index.html references /src/* directly

build(src/scripts/build.py):
  pre:  entry == src/main.js
        toolchain == {python}                 [NOT {bundler, node}]
  proc: graph := resolve(import/export, from: entry)
        ∀ m ∈ graph: transform(m) → require/module.exports (runtime shim)
        inline(transform(graph), src/styles/main.css) into copy(src/index.html)
  post: output == src/_output/versions/index-v{NNNN}.html
        NNNN == CURRENT_VERSION  [src/data/version.js]
        output is self-contained  [portable deliverable]
```

## Persistencia y guardado a fichero

```
inv: src/index.html contains <script type="application/json" id="initial-state"></script>
inv: build(initial-state) == identity           [copied unmodified through build]
inv: download(initial-state) == current-state   [rewritten at export time, see fileExport]
```

```
boot(main.js):
  s := loadState()  [core/persistence.js, localStorage]
  pre(s valid):        loadComponents(s) ∧ loadResources(s) ∧ backfillDefaultResourcesIfNeeded(s)
  pre(s corrupt|incompatible): showToast(warning) ∧ exampleComponent() ∧ defaultResources()
  pre(s == ∅):
    seed := readSeedState()  [<script id="initial-state">]
    pre(seed ≠ ∅): loadComponents(seed) ∧ loadResources(seed) ∧ backfillDefaultResourcesIfNeeded(seed)
    pre(seed == ∅): exampleComponent() ∧ defaultResources()
```

### Autoguardado (`core/persistence.js`)

```
trigger := components:changed ∨ panelState:changed ∨ resources:changed
         ∨ resourcePanelState:changed ∨ tags:changed ∨ tagPanelState:changed
         ∨ appTitle:changed                                    [core/eventBus.js]

on trigger:
  localStorage ← { version: CURRENT_VERSION, components, panelState, resources,
                    resourcePanelState, resourcesSeeded, tags, tagPanelState, appTitle }

inv: appTitle == ∅ ∨ ¬isString(appTitle)  ⇒  effectiveAppTitle == DEFAULT_APP_TITLE   [core/appTitle.js]
inv: tags:changed  ⇒  renderAll() ∧ autosave()     [renderAll NOT triggered by other 6 events]
inv: scope(localStorage) == {browser, profile}     [NOT scoped per-file under file://]
inv: persist(selectedComponentIds) == false        [∀ panelState shape]
```

```
boot with valid localStorage save s:
  pre(panelState ∈ s):         hydrate(panelState) := loadPanelState(s)
  pre(panelState ∉ s):         panelState := DEFAULT_PANEL_STATE  [collapsed:false, position/width/height: default]
  # identical branching for resourcePanelState/tagPanelState (loadResourcePanelState/loadTagPanelState)

pre(¬isArray(s.resources)): s.resources := []  ∧  triggerBackfill(defaultResources)
pre(¬isArray(s.tags)):      s.tags := []       [no backfill]
```

```
fileExport(core/fileExport.js) writes fields:
  { components, panelState, resources, resourcePanelState, resourcesSeeded, tags, tagPanelState }
  |fields| == 7
```

<!-- id: persistence-backward-compat-chain -->
```
[breaking] read(tags)        := s.tags        ?? s.groups        ?? s.decks
[breaking] read(tagPanelState) := s.tagPanelState ?? s.groupPanelState ?? s.deckPanelState
  [parseState, parseImportedComponents — same chain documented in 03-groups-resources.md]
```

### Guardar a fichero (`core/fileExport.js`, botón "Guardar" en `ui/editModeToggle.js`)

```
buildExportHtml(components, resources, panelState, resourcePanelState, resourcesSeeded, tags, tagPanelState, appTitle):
  doc := clone(document.documentElement)   [CSS/JS already inlined by build]
  doc.querySelector('#initial-state').content ← currentState
  downloadHtml(doc) → Blob

pre: filename == getFullAppTitle(getAppTitle()) + '.html'   [prompt(), user-editable before confirm]
inv: overwrite(existingFile) == browser-decision   [NOT app-decision]
```

### Exportar/Importar con selección (`core/importMerge.js` + `ui/exportSelectionModal.js`/`ui/importSelectionModal.js`/`ui/importConfirmModal.js`/`ui/importReportModal.js` en `ui/editModeToggle.js`)

```
inv: format(Guardar) == { components, panelState, resources, resourcePanelState, resourcesSeeded, tags, tagPanelState, appTitle }
inv: format(Exportar/Importar) == { version, components, resources, tags }
inv: format(Guardar) ≠ format(Exportar/Importar)   [appTitle ∉ Exportar/Importar; partial selection allowed]
```

**Exportar:**
```
pre: filename := prompt(getFullAppTitle(getAppTitle()) + '.json')  [openExportSelectionModal]
     selection := checkboxes(3 blocks)                             [ui/elementSelectionModal.js]
proc: (components', resources', tags') := filter(getComponents(), getResources(), getTags(), by: selection.ids)
      buildComponentsExport(components', resources', tags') → downloadJson
inv: validate(orphanReferences, selection) == false   [gotcha: no validation performed]
```

**Importar:**
```
1. parsed := parseImportedComponents(file)
2. selection := openImportSelectionModal(parsed)
3. (mode, conflictMode) := openImportConfirmModal()
     mode ∈ {add, overwrite}
     conflictMode ∈ {overwrite, keepBoth}
4. ∀ c ∈ selection where c.type == 'ficha':
     (c', errors) := migrateFichaComponent(c)
   pre(∃ c: errors ≠ ∅):
     openImportConversionErrorModal(errors)
     choice ∈ {abort, continue}
     pre(choice == abort):    ¬mergeImportedGame() ∧ ¬loadComponents() ∧ ¬loadResources() ∧ ¬loadTags()
     pre(choice == continue): selection := selection \ {c | errors(c) ≠ ∅}
5. finalState := mergeImportedGame(selection, mode, conflictMode)
```

```
mergeImportedGame(selection, mode, conflictMode):
  pre(mode == overwrite):
    finalState := selection   [insert into ∅, no conflict possible]
  pre(mode == add):
    ∀ type ∈ {components, resources, tags}:   [independent id-space per type]
      ∀ item ∈ selection[type]:
        pre(item.id ∉ existing[type]):
          existing[type] += item
        pre(item.id ∈ existing[type] ∧ conflictMode == overwrite):
          existing[type][item.id] := item
        pre(item.id ∈ existing[type] ∧ conflictMode == keepBoth):
          item.id := nextImportedId(item.id)   [suffix -imported / -imported(n), analogous to nextCloneId]
          rewrite(referencesTo: oldId, toward: item.id) ∀ imported component
          # etiquetaIds is a flat top-level field of component, same tier as `image` — NOT nested in properties
```

```
post-merge repair, ∀ component c ∈ imported:
  pre(c.resourceRef ∉ finalState.resources):
    c.resourceRef := null                       [same tolerance as: resource deleted while in use]
  ∀ tagId ∈ c.etiquetaIds where tagId ∉ finalState.tags:
    pre(∃ tag ∈ finalState.tags: tag.name == nameOf(tagId)):
      link(c, existingTag)
    pre(¬∃ such tag):
      finalState.tags += createTag(tagId)        [once per tagId, even if referenced by multiple components]
  report += { componentId, tipoError, solucion, elemento }  ∀ repair performed
inv: report ≠ [] ⇒ openImportReportModal(report)
```

```
removed(unused): getComponentsWithMissingResources [core/resource.js], getComponentsWithMissingDeck [core/deck.js]
  [superseded by: mergeImportedGame's report, from prior all-or-nothing confirm()-based import flow]
```

### Recursos por defecto y backfill (`data/defaultResources.js`, `main.js`)

<!-- id: default-resources-backfill -->
```
inv: resourcesSeeded == true  ⇒  seedDefaultResources() executed ≥1 time  [current or prior save]
inv: ∀ save-lineage: |{ t : seedDefaultResources() executed at t }| ≤ 1   [no reseed after manual delete]
```

```
pre(state == ∅ ∨ seed == ∅ ∨ state corrupt|incompatible):
  seedDefaultResources() → resources += DEFAULT_RESOURCES   [|DEFAULT_RESOURCES| == 38: 3 location-background + 35 backpack/object/event, data-URI, id == filename, NOT uuid]
  resourcesSeeded := true    [markResourcesSeeded()]

pre(state ∨ seed valid ∧ resourcesSeeded ≠ true):   [typically: save predates this feature]
  backfillDefaultResourcesIfNeeded() → resources += DEFAULT_RESOURCES  [once]
  resourcesSeeded := true
  # post-condition: user-deleted default resources do NOT reappear on subsequent loads
  #   [backfill gated by resourcesSeeded, not by presence/absence of each resource]
```
