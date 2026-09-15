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

```
component                                concepto.  anchor: src/core/component.js#createComponent
component.decision.generic-extensible-model   decisión.  sin ancla
    [motivación] modelo genérico y extensible: ningún tipo concreto (carta, ficha, tablero, tracks...) requiere cambio estructural en el modelo — ver 002-component-model.md y 003-component-types.md
component.order = 1 .. n                  afirmación (1 = arriba, n = abajo)
component.order.rule:                     anchor: src/core/state.js
    addComponent asigna order = 1, desplaza el resto +1
    removeComponent recompacta 1..n (compactOrders)
    reorderComponent(id, raw) clampa raw a [1, n]
component.copyOf?: string = null          concepto.  anchor: src/core/component.js#createCopy
component.sincronizado: bool = true       afirmación (solo aplica si copyOf != null)
component.copy.decision.non-synced-keys   decisión.  anchor: src/core/component.js (NON_SYNCED_PROPERTY_KEYS)
    [motivación] x, y, order, groupId, properties.resultadoActual (dado), properties.caraActual (carta) nunca se propagan de un original a sus copias vinculadas
component.groupId?: string = null         concepto.
component.bloqueado: enum ∈ {ninguno, juego, todos} = ninguno   concepto.
component.oculto: bool = false            concepto.
component.subirAlMoverInteractuar: bool = false   concepto.
component.profundidad: number [0..40] = 0         concepto.  anchor: src/ui/componentRenderer.js#buildExtrusionLayers
component.colorExtrusion?: string = null          concepto.  anchor: src/ui/componentRenderer.js#resolveExtrusionColor
component.accionClickDerecho: enum ∈ {ninguno, menuContextual} = ninguno   concepto.
component.image?: string = null           concepto.
component.image.decision.unused           decisión.  sin ancla
    [gotcha] component.image no lo usa ningún tipo actual (verificado: solo se lee en core/resource.js para detección de uso, ningún tipo lo escribe); los fondos de imagen van por properties.imagenResourceId

group                                     concepto.  anchor: src/core/group.js#createGroup
group.id: string                          afirmación (mismo valor que el groupId de sus miembros; grupo-N o libre si se renombra)
group.id.rule:                            anchor: src/core/component.js#nextGroupId
    formato grupo-N, N = primer entero libre
group.effectiveProps.rule:                anchor: src/core/group.js#getEffectiveGeneralProps
    pre:  component.groupId != null ∧ ∃ g ∈ groups : g.id = component.groupId
    post: bloqueado, oculto, mostrarTooltip, mostrarTitulo, subirAlMoverInteractuar, etiquetaIds efectivos = los del registro g
    fallback: si no hay registro g, se usan los propios del componente
group.persist.decision.key-componentGroups   decisión.  sin ancla
    [motivación] la colección se persiste bajo la clave componentGroups, no groups, porque groups ya es alias de compatibilidad de tags

tag                                       concepto.  anchor: src/core/tag.js#createTag
tag.name.uniqueness.rule:                 anchor: src/core/tag.js#isTagNameTaken
    normalizado (trim, case-insensitive); true si otro tag con id != excludeId tiene el mismo nombre
tag.persist.decision.compat-chain        decisión.  sin ancla
    [motivación] parseState lee tags/tagPanelState, con fallback a groups/groupPanelState y luego a decks/deckPanelState

resource                                  concepto.  anchor: src/core/resource.js#createResource
resource.type: enum ∈ {imagen, tipografia}   concepto.
resource.usage.rule:                      anchor: src/core/resource.js#isResourceInUse
    recorre component.properties en profundidad (collectDeepValues) buscando el resourceId; getComponentsUsingResource añade component.image
resource.typeForFileName.rule:            anchor: src/core/resource.js#resourceTypeForFileName
    png/jpg/jpeg/gif/svg/webp -> imagen; ttf/otf/woff/woff2 -> tipografia; else null

i18n                                      concepto.  anchor: src/core/i18n.js
i18n.language.active: enum ∈ {es, en} = es concepto (en memoria).  anchor: src/core/i18n.js
i18n.language.persist.key = 'bgfactory:lang'   afirmación.  anchor: src/core/i18n.js (STORAGE_KEY)
i18n.language.resolve.rule:               anchor: src/core/i18n.js#initI18n
    localStorage[i18n.language.persist.key] ∈ SUPPORTED_LANGUAGES  → active = stored
    else  → navigator.language startsWith 'es' ? 'es' : 'en'   (no se escribe en localStorage)
i18n.language.persist.decision.separate-key   decisión.  sin ancla
    [motivación] parseState descarta bgfactory:state entero si version != CURRENT_VERSION; la preferencia de idioma no debe perderse en cada versión
i18n.t.rule:                              anchor: src/core/i18n.js#t
    CATALOG[active][key] → CATALOG['es'][key] → key
    entrada {one, other} + params.count → one si count===1, si no other
    interpola {name} con String(params[name]); resultado texto plano (textContent)
i18n.catalog.decision.pure-data           decisión.  sin ancla
    [motivación] data/i18n.<lang>.js son objetos planos clave→texto sin lógica ni imports; editar una traducción no puede romper comportamiento; añadir idioma = catálogo + entrada en SUPPORTED_LANGUAGES
i18n.event.language-changed               afirmación.  anchor: src/core/i18n.js#setLanguage
    setLanguage(code) emite 'language:changed' por core/eventBus.js; suscriptores: main.js#renderAll y cada modal abierto (re-textualiza)
i18n.compare.locale.rule:                 anchor: src/core/textSort.js, src/core/resource.js#findResourceByName
    localeCompare usa getLocale() (idioma activo), no 'es' fijo

persistence.serializedFields = [components, panelState, resources, resourcePanelState, resourcesSeeded, tags, tagPanelState, componentGroups, appTitle, tableText]
                                          afirmación.  anchor: src/core/persistence.js
state.tableText: string = ''              concepto.  anchor: src/core/state.js (tableText)
    texto libre del usuario para la esquina de la mesa (#app-version); editable en ui/settingsModal.js (00250)
    preferencia local, mismo criterio que appTitle/idioma: NO en persistence.buildComponentsExport ni parseImportedComponents
    parseState devuelve '' si parsed.tableText falta o no es string — guardados pre-00250 no traen la clave, sin migración
state.event.table-text-changed           afirmación.  anchor: src/core/state.js#setTableText
    setTableText(newText) normaliza a '' si no es string y emite 'tableText:changed' (payload: el nuevo string) por core/eventBus.js
    suscriptores: src/main.js → renderAll ∧ persistState; loadTableText(newText) hidrata en arranque sin emitir
appTitle.getVersionedProductName          concepto.  anchor: src/core/appTitle.js#getVersionedProductName
    `${DEFAULT_APP_TITLE} ${formatVersion()}` — literal fijo "BG Factory" + versión, independiente de state.getAppTitle() (00250)
    fuente única del nombre versionado; consumidores: ui/settingsModal.js (bloque Versión). main.js#renderAppVersion arma su propio `BG Factory ${CURRENT_VERSION}` (formato distinto, sin `v.`)
panelState.expandedGroupIds: string[]     concepto.  anchor: src/core/state.js (panelState)
    groupId[] de las filas de grupo del panel "Componentes" desplegadas explícitamente; ausencia = plegado (estado por defecto)
    se poda de groupId sin grupo real (2+ miembros) en cada renderComponentList; filtro activo fuerza desplegado sin mutar la lista
    NO en persistence.buildComponentsExport ni parseImportedComponents (como todo panelState) — preferencia local de visualización
    [gotcha] loadPanelState normaliza a [] si falta o no es array — guardados pre-00239 no traen la clave, sin migración
persistence.serializedFields.rule:        anchor: src/core/persistence.js (saveState/parseState)
    autosave serializa exactamente esa lista a localStorage; una colección/campo nuevo debe añadirse ahí y en la suscripción de autosave (007-persistence-build.md)
    [gotcha] core/fileExport.js NO participa en esta lista (solo expone downloadJson, un helper genérico) — corrección S2, el borrador original citaba fileExport.js como coautor de la serialización
persistence.parseState.result: enum ∈ {success-object, {error: 'corrupt'}}   afirmación.  anchor: src/core/persistence.js#parseState
persistence.parseState.result.rule:       anchor: src/core/persistence.js (parseState)
    JSON.parse lanza -> {error: 'corrupt'}
    parsed objeto ∧ parsed.version != CURRENT_VERSION -> {error: 'corrupt'} (antes del chequeo de components; el chequeo de versión se mantiene, solo se unifica su desenlace — 00250)
    parsed falsy ∨ !Array.isArray(parsed.components), con version correcta -> {error: 'corrupt'}
    resto -> objeto de éxito sin campo error
persistence.startup.rule:                  anchor: src/main.js (bootFromSeedOrDefaults + bloque de arranque)
    loadState() null -> bootFromSeedOrDefaults(), sin aviso
    {error: 'corrupt'} -> bootFromSeedOrDefaults() + showToast('No se ha podido recuperar el estado guardado.')  (cualquier guardado no restaurable: JSON ilegible, sin components, o de otra versión)
    objeto de éxito -> restaurar estado, sin aviso
    [gotcha] el arranque ya no usa showErrorModal; un guardado no restaurable es toast no bloqueante, no modal

splash                                    concepto (00245, 00247).  anchor: src/ui/splashScreen.js#showSplashScreen
    overlay de bienvenida al arrancar; showSplashScreen() sin params/retorno; SPLASH_DURATION_MS = 3000 (era 5000 hasta 00247), LOGO_COUNT = 4
    DOM propio (.splash-overlay > .splash-window > logo, título, .splash-window__link, .splash-window__progress), NO reutiliza .modal/.modal-overlay; primera sentencia de main.js, antes de initI18n()
    logo n = Math.floor(Math.random()*LOGO_COUNT)+1, sin estado de módulo; título "Board Game Factory" + <sup> "(2026)" por textContent, sin t()
    [gotcha] único elemento interactivo: ui.class.splash-window__link. Su clic NO cierra el overlay (no hay listener); el setTimeout de 3s no se cancela nunca
    [gotcha] sin listener click/keydown de cierre; overlay sin clase .modal-overlay -> ui/globalShortcuts.js no lo trata (ESC/ENTER no le afectan)
splash.duration.value = 3000ms            afirmación (00245 -> 00246 -> 00247)
    debe coincidir con la duración del @keyframes splash-progress-fill de ui.class.splash-window__progress-fill. SPLASH_DURATION_MS (src/ui/splashScreen.js) y esa duración CSS deben ser iguales. Era 5000ms hasta 00247.
splash.decision.bar-fill-scalex-keyframes   decisión (00245 -> 00246 -> ajuste 00246).  sin ancla
    la barra se llena con @keyframes splash-progress-fill: transform scaleX(0 -> 1), transform-origin left, 3s linear forwards (era 5s hasta 00247). NO transition, NO animación de width.
    [motivación] tres intentos: (1) 00245 transition: width disparada por toggle de clase JS tras doble rAF; (2) 00246 @keyframes sobre width. Ambos fallan en el navegador real: showSplashScreen() es la 1ª sentencia de main.js y el bootstrap síncrono (initI18n -> estado -> primer renderAll) bloquea el hilo y difiere el paint del que dependen; la animación llega "consumida". (3) ajuste 00246: @keyframes sobre transform scaleX — se compone en el compositor sin layout y arranca fiable al entrar el elemento en el árbol de render, igual que @keyframes progress-modal-spin.
    consecuencia: 2ª animación @keyframes del proyecto, junto a @keyframes progress-modal-spin (ui/progressModal.js) — ver 004-naming-and-patterns.md
    NO condicionada por prefers-reduced-motion: indicador funcional del tiempo restante, mismo criterio que progress-modal-spin
splash.decision.logo-as-css-background     decisión (00245).  sin ancla
    [motivación] los 4 logos se referencian como background-image en reglas .splash-window__logo--<n> de main.css, no como <img> en JS — build.py solo incrusta como data URI assets citados desde CSS/HTML (embed_css_asset_urls), no desde JS
ui.class.splash-window__link              concepto de estilo (00247).  anchor: src/styles/main.css
    enlace externo del splash; <a href="https://github.com/yeyopepe/bgfactory" target="_blank" rel="noopener"> textContent "View on Github"
    sigue ui.link + ui.link.external (color: inherit; text-decoration: underline; sin :hover/:visited/:active; cursor pointer); margin-top -0.5rem (compensa gap de .splash-window); font-size 0.875rem
    [gotcha] texto LITERAL FIJO, NO t() — a diferencia de #app-version a y .settings-modal__repo a, que usan t('appVersion.repoLink'). Coherente con splash (título tampoco usa t()).
    3er sitio con el literal de URL del repo (junto a src/main.js#renderAppVersion y src/ui/settingsModal.js); no centralizada
splash.decision.logo-square-box            decisión (00246).  sin ancla
    .splash-window__logo: aspect-ratio 1/1 (no 4/3) + background-size contain + mask-image radial-gradient(circle at 50% 50%, #000 55%, transparent 78%)
    [motivación] con caja 4/3 los 4 logos casi-cuadrados (884×876 … 1024×1048) dejaban franjas y la máscara difuminaba el borde de la caja, no el del logo pintado -> recuadro blanco visible. Caja cuadrada: el background llena casi toda la caja y la máscara circular muerde el borde real del logo.

ui.token.accent-blue = #2c7dd8            afirmación de estilo.  anchor: src/styles/main.css
ui.token.accent-blue-dark = #123a66       afirmación de estilo.
ui.token.accent-blue-light = #eaf3fc      afirmación de estilo.
ui.token.section-accent = #5b5f97         afirmación de estilo.
ui.token.error = #d32f2f                  afirmación de estilo.
ui.token.radius-sm = 4px                  afirmación de estilo.
ui.token.radius-lg = 8px                  afirmación de estilo.
ui.token.shadow-1                         concepto de estilo.  anchor: src/styles/main.css
ui.token.shadow-2                         concepto de estilo.
ui.token.transition-fast = 150ms ease     afirmación de estilo.
ui.elevation.level0                       concepto de estilo (plano, sin sombra)
ui.elevation.level1                       concepto de estilo (flotación sutil, box-shadow shadow-1)
ui.elevation.level2                       concepto de estilo (overlay, box-shadow shadow-2)
ui.class.is-copy                          concepto de estilo.  anchor: src/ui/componentRenderer.js
ui.class.component-list__group-name       concepto de estilo (00239).  anchor: src/styles/main.css
    identificador de la fila de grupo en font-weight: 700; distingue la fila de grupo de una fila de componente suelto o de miembro
ui.class.component-list__group-toggle     concepto de estilo (00239).  anchor: src/styles/main.css
    triángulo de plegado en la celda de id de la fila de grupo; glifo de texto ▸ (plegado) / ▾ (desplegado), color ui.token.text-muted, hover ui.token.accent-blue
    mismo lenguaje visual que el triángulo de cabecera de panel flotante, font-size 0.9375rem (una talla mayor por ser control de fila)
    [gotcha] clic con stopPropagation: alterna plegado, NO selecciona el grupo; inerte mientras hay filtro activo (grupo desplegado forzado)
ui.class.is-group-passenger              concepto de estilo.  anchor: src/ui/componentRenderer.js
ui.class.decision.is-group-passenger-wins-over-is-copy   decisión.  sin ancla
    [motivación] .is-group-passenger se declara después en la cascada CSS, gana a .is-copy sobre el mismo elemento
ui.class.lifted                           concepto de estilo (estado transitorio, drag en modo juego)
ui.class.drop-target                      concepto de estilo (mazo resaltado durante drag de carta)
ui.class.carta--flip-feedback            concepto de estilo (feedback de cambio de cara)
ui.feedback.error.decision.modal-except-startup   decisión.  sin ancla
    [motivación] todo error de la app usa showErrorModal (ui/errorModal.js); única excepción (cambio 00230): el arranque comunica un estado guardado irrecuperable (otra versión, o corrupto) con showToast no bloqueante — condición esperada y autorrecuperable, un modal sería desproporcionado
ui.link                                   concepto de estilo (enlace de texto).  anchor: src/styles/main.css (#app-version a)
    color: inherit ∧ text-decoration: underline ∧ sin :visited/:hover/:active
    [gotcha] un enlace de texto NO es --accent-blue; se distingue solo por el subrayado, en el color de su contexto
ui.link.external                          concepto de estilo (enlace a destino fuera de la app)
    target="_blank" ∧ rel="noopener" ∧ texto = etiqueta legible, nunca la URL cruda
    referencia: enlace al repo (https://github.com/yeyopepe/bgfactory) en #app-version a y, replicado, en .settings-modal__repo a (00250) — mismo tratamiento
ui.class.settings-modal__repo             concepto de estilo (00250).  anchor: src/styles/main.css
    enlace a GitHub bajo la versión en el panel de Configuración; font-size 0.875rem, color var(--text-muted), margin-top 0.15rem; el <a> hereda color + text-decoration: underline (idéntico a #app-version a, ver ui.link)
ui.class.app-version                      concepto de estilo (footer de versión).  anchor: src/main.js#renderAppVersion
    #app-version contiene .app-version__name + .app-version__repo (00243)
    con state.tableText no vacío: antepone .app-version__table-text (texto plano, textContent, white-space: pre-line) + .app-version__separator (<hr>, border-top 1px var(--border-neutral)) (00250)
    [gotcha] .app-version__table-text y .app-version__separator NO se pintan si state.tableText.trim() === '' — footer idéntico a 00243
ui.class.mode-switcher__mode-btn          concepto de estilo (00244).  anchor: src/ui/editModeToggle.js#createModeButton
    botón de cambio de modo ("Modo Edición"/"Modo Juego"), acción primaria (azul), siempre en la fila de la cabecera (#mode-switcher) en ambos modos
ui.class.mode-switcher__settings-btn      concepto de estilo (00244).  anchor: src/ui/editModeToggle.js#createSettingsButton
    botón de configuración icono-solo 36×36, esquema "sobre fondo oscuro" (contorno claro, sin fondo azul), a diferencia de .mode-switcher__fit-btn
ui.class.decision.mode-switcher-both-modes   decisión (00244).  sin ancla
    [motivación] #mode-switcher se puebla en ambos modos (renderModeSwitcher ya no hace early return si !PLAY); #edit-toolbar solo aloja la franja .edit-toolbar con Importar/Exportar; el botón de modo y "Ajustar zoom" viven siempre en #mode-switcher
ui.class.splash-overlay                    concepto de estilo (00245, 00248).  anchor: src/styles/main.css
    overlay del splash de arranque; position fixed, inset 0, flex centrado, z-index 1300
    fondo (00248): fondo de la mesa de juego — background-color var(--bg-table) + background-image radial-gradient(circle, var(--bg-table-dot) 1.5px, transparent 1.5px) + background-size 32px 32px, replicado de .infinite-table (el <body> solo trae var(--bg-table) liso, sin el patrón). Sin capa de atenuación (sigue sin ser el rgba(0,0,0,0.5) de .modal-overlay). Era #ffffff opaco hasta 00248.
    [gotcha] el patrón de puntos de la mesa está duplicado en .infinite-table y .splash-overlay (no extraído a una utilidad) — si cambia, tocar ambos
    ver 003-modales-menus.md "Startup splash / welcome screen"
ui.class.splash-window                     concepto de estilo (00245, revisado 00246).  anchor: src/styles/main.css
    background linear-gradient(135deg, #e3effb 0%, #eef1fb 45%, #f7ecf6 100%), border-radius var(--radius-lg), box-shadow var(--shadow-2) (elevación nivel 2), overflow hidden; sin header/footer/botones
    hijos: .splash-window__logo (aspect-ratio 1/1, background-size contain, mask-image radial-gradient(circle at 50% 50%, #000 55%, transparent 78%); variantes --1..--4; ver splash.decision.logo-square-box), .splash-window__title (<p> 2.25rem/700 + <sup>), ui.class.splash-window__link (00247), .splash-window__progress / __progress-fill (este último: animation splash-progress-fill 3s linear forwards, 00247)
ui.zindex.max = 1300                       afirmación de estilo (00245)
    .splash-overlay; nuevo máximo del proyecto (antes 1200 en .export-menu). Escala completa en 001-tokens-visual.md "z-index scale"
ui.motion.reduced.rule:                    afirmación de estilo (00245 -> 00246 -> eliminado en ajuste 00246).  sin ancla
    el proyecto NO usa prefers-reduced-motion en ningún sitio. Las 2 animaciones (@keyframes progress-modal-spin, @keyframes splash-progress-fill) son indicadores funcionales, corren siempre.
    un @media (prefers-reduced-motion: reduce) para la barra del splash existió brevemente (00246) y se quitó en la misma sesión
test                                      concepto (framework de tests funcionales, 00238).  anchor: src/test/run.js
    ver 011-functional-test-framework.md
test.harness                              concepto.  anchor: src/test/harness.js#run
    motor describe/it/expect/beforeEach/afterEach/registerFeature/run propio, corre en el navegador headless, sin Node
test.helpers                              concepto.  anchor: src/test/helpers.js
    resetState / mountChrome / mountEditMode / mountPlayMode / loadFixture / mockRandom / captureDownload / getLastDownload / injectFileImport / restoreAllMocks
test.traceability.rule:                   afirmación.  anchor: src/test/traceability.js#generateTraceability
    genera src/test/TRACEABILITY.md cruzando design/docs/features/INDEX.md con registerFeature de cada fichero
    post: (∃ test con primary|secondary NNN ∧ NNN ∉ features/INDEX.md) ⟹ hasAnomaly ∧ run.js exit = 1
test.code.rule:                           afirmación (código de test)
    FT-<NNN>-<nn>: NNN = número de ficha design/docs/features/ de la funcionalidad principal; nn = correlativo de 2 dígitos; prefijo del nombre del it
test.release-gate.rule:                   afirmación (00239).  sin ancla (prosa de previo-sdd/stuff/custom-version-pipeline.md → In the middle → Step 1)
    npm test corre en pv-version paso 4.1, tras el ZIP del entregable y antes de copy-docs.py/changelog
    exit 2 ⟹ npm run test:setup + reintento único; segundo exit 2 ⟹ release se detiene
    exit 1 ⟹ release se detiene antes de docs/changelog (el ZIP del entregable puede ya existir)
    post: siempre se escribe previo-sdd/versions/{XXXX}/test-report.md (Resultado ∈ {Correcto, Con fallos}, totales; bloque de fallos literal de npm test si los hay)
    ver 011-functional-test-framework.md
test.decision.no-main-js                  decisión (00238).  sin ancla
    [motivación] la página headless no carga src/main.js; montaje explícito por test (mountChrome + renderEditMode/renderPlayMode) para que resetState sea determinista y no se acumulen los ~18 listeners del eventBus del bootstrap
test.decision.page-reload-isolation      decisión (00238).  sin ancla
    [motivación] aislamiento = una navegación de página por fichero de test; grafo de módulos ES fresco ⟹ Map de listeners del eventBus a cero, sin off() manual
test.decision.own-engine                 decisión (00238).  sin ancla
    [motivación] motor propio en vez de runner de terceros: corre dentro del navegador sin Node, el proyecto no adquiere dependencia de runtime
test.decision.playwright-over-jsdom      decisión (00238).  sin ancla
    [motivación] Chromium headless real, no jsdom: las funcionalidades frágiles (drag en bloque, fitToBounds, resize de paneles, solape carta-mazo, menús position:fixed, canvas de dado/mazo) necesitan layout y canvas reales
```
