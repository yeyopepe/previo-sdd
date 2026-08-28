# Informe comparativo de documentación — Previo 0.9.6b9 (nivel `minimal`) vs. baseline

**Fecha:** 2026-08-28
**Objeto:** Comparar la documentación de **arquitectura** y de **estilo (Style Bible)** que Previo 0.9.6b9 genera en nivel `minimal` (solo mirando el código de la app) frente a la documentación de referencia (`_baseline`), creada y mantenida a mano a lo largo de la evolución del proyecto.

**Fuentes:**
- Referencia: `test-data/bgfactory-docs/_baseline/architecture/` y `.../style/`
- Bajo prueba: `test-data/bgfactory-docs/0.9.6b9/minimal/architecture/` y `.../style/`

---

## 1. Resumen ejecutivo

| Dimensión | Baseline | 0.9.6b9 / minimal | Ratio |
|---|---|---|---|
| Arquitectura — nº de ficheros de contenido | 6 (+ INDEX + 2 versiones alt.) | 4 (+ INDEX + `00-namespace`) | — |
| Arquitectura — palabras (sin INDEX ni namespace) | ~18.700 | ~2.250 | **~12 %** |
| Style Bible — nº de ficheros de contenido | 3 (+ INDEX) | 3 (+ INDEX) | — |
| Style Bible — palabras (sin INDEX) | ~8.300 | ~1.500 | **~18 %** |

**Veredicto general:** el nivel `minimal` de 0.9.6b9 produce una documentación **estructuralmente correcta, precisa en lo que afirma y notablemente bien organizada** (notación compacta, namespace único, tablas densas, etiquetas `[gotcha]`). Es un buen "mapa de orientación" para alguien que aterriza en el código. Pero **no es sustituto del baseline**: deja fuera ~85-90 % del contenido de referencia, y lo que falta no es "relleno" sino precisamente el conocimiento que un modelo de lenguaje no puede reconstruir leyendo el código una sola vez — reglas transversales, excepciones catalogadas, el *porqué* de cada decisión, y los checklists de "qué revisar al tocar X".

Para el propósito declarado del nivel `minimal` (contexto de arranque compacto, no enciclopedia), el resultado es **adecuado**. Como documentación única del proyecto, sería **insuficiente**.

---

## 2. Arquitectura

### 2.1 Cobertura estructural

| Tema del baseline | Fichero baseline | ¿Cubierto en minimal? | Dónde / observaciones |
|---|---|---|---|
| Objetivo y restricciones del prototipo | `INDEX.md` §1 | ✅ Parcial | `001-overview` primer párrafo. Falta el detalle de "doble clic, sin servidor, sin Node, build en Python". |
| Arquitectura por capas + grafo de dependencias | `INDEX.md` §2 | ✅ Bien | `001-overview` "Layers" (tabla con "May import"). Equivalente y hasta más legible. La regla `ui/ ↛ modes/` está capturada como invariante (`arch.layer.ui.no-modes-import`) y como `[gotcha]`. |
| Convenciones de código (módulos ES, sin deps, comentarios) | `INDEX.md` §7 | ⚠️ Muy parcial | `001-overview` "Stack" menciona vanilla ES modules. **Falta** toda la política de comentarios ("solo el porqué no evidente", estilo telegráfico, excepción `vendor/`). |
| **Checklist al añadir un tipo/colección nuevo** (10 puntos transversales) | `INDEX.md` §8 | ❌ **Ausente** | Es el contenido más valioso del baseline y **no tiene equivalente**. Ver §2.3. |
| Modelo genérico de componente (todos los campos + tabla "quién lo edita") | `01-component-model.md` | ✅ Parcial | `004-data-model` tiene el shape completo en notación compacta con defaults. **Falta** la columna "Quién lo edita", los matices por campo (p. ej. `image` sin uso real, `tooltipTexto` no es override de grupo pero `mostrarTooltip` sí), y las notas de migración por campo. |
| Lógica de `order` (addComponent, compactOrders, reorderGroupBlock) | `01-component-model.md` | ⚠️ Muy parcial | `004` da la invariante "contiguo 1..N" y menciona `compactOrders`/`addComponent pushes to front`. **Falta** `reorderComponent`, `reorderGroupBlock` (mover bloque de grupo), el clamp `[1, n-k+1]`. |
| Copias vinculadas (`copyOf`): sincronización campo a campo, cascada, modal reducida | `01-component-model.md` | ⚠️ Parcial | `004` (`model.component.copy.*`) captura: qué se sincroniza, qué no (`resultadoActual`/`caraActual`), cascada de borrado, `sincronizado` gobierna `bloqueado`/`oculto`. **Falta** `nextCopyId`, `renameCopyId`, la modal `copyComponentModal.js`, el menú contextual condicionado. |
| Sistema de variables de texto (`{cards_current}`, `getAvailableVariables`) | `01-component-model.md` | ⚠️ Mínimo | `003-file-and-symbol-map` menciona `textVariables.js` en una línea. **Falta** el mecanismo, el punto de extensión, el comportamiento "literal si no aplica". |
| **Los 8 tipos de componente y sus propiedades específicas** | `02-component-types.md` (4.100 palabras) | ❌ **Casi ausente** | `004` solo lista el enum `type ∈ {carta, mazo, dado, ...}`. **No hay ni una tabla de `properties` por tipo.** Ver §2.3. |
| Modelo de etiqueta (`tag`) | `03-groups-resources.md` | ⚠️ Mínimo | `004` da el shape (`id`, `name`) y "many-to-many via etiquetaIds". **Falta** `isTagNameTaken`, alta al vuelo, panel dedicado, cadena de compatibilidad `decks→groups→tags`. |
| Modelo de grupo (`group`) + propiedades efectivas | `03-groups-resources.md` | ✅ Parcial | `004` (`model.group.*`) captura bien: shape, `getEffectiveGeneralProps` (override), `autoDissolve` ≤1 miembro, `deriveMissingGroups`. Buena densidad. **Falta** `isGroupIdTaken`, el detalle de edición desde `groupModal.js`. |
| Modelo de recurso / galería + conversión WebP | `03-groups-resources.md` | ✅ Parcial | `004` (`model.resource.*`): shape, `type ∈ {imagen, tipografia}`, WebP q=0.92, `inUse` bloquea borrado. **Falta** `resourceTypeForFileName` (extensiones), `DEFAULT_RESOURCES`, `resourcesSeeded`, siembra. |
| Migración de `'ficha'` → `'carta'` (mapeo campo a campo, dos puntos de uso) | `03-groups-resources.md` | ⚠️ Mínimo | `004` lista `migrateFichas` en la tabla de migraciones (una fila). **Falta** todo el mapeo (`forma`→`proporcion`, `fondoTipo`, errores) y la diferencia carga silenciosa vs. importación interrumpible. |
| Portapapeles de estilo (`styleClipboard.js`) | `03-groups-resources.md` | ⚠️ Mínimo | `003` menciona el fichero. **Falta** el shape del dato, `validateStyleClipboardForPaste`, el flujo copiar/pegar, "solo en memoria". |
| Modo juego vs. modo edición (paneles, selección múltiple, Ctrl+click) | `04-modes.md` | ⚠️ Parcial | `002-state-events` cubre el estado transitorio (`selectedComponentIds`, `primarySelectedIds`, cámara) y que se resetea al recargar. La *mecánica* (clic normal reemplaza, Ctrl añade, redimensionado solo con 1) está en `style/002` (interacción). **Falta** la vista de conjunto de qué hace cada modo. |
| **Grupos en modo edición** (selección atómica, menú Agrupar/Desagrupar con tabla de habilitación, movimiento en bloque, anidación visual en panel) | `04-modes.md` (~1.500 palabras) | ❌ **Casi ausente** | `004`/`00-namespace` dan `effectiveProps` y `autoDissolve`. **Falta** toda la interacción: la tabla "2+ unidades / 1 unidad / es grupo", filas sintéticas del panel, `reorderGroupBlock`, edición individual de miembro agrupado. |
| Menú contextual de componente (juego y edición) | `04-modes.md` | ⚠️ Parcial | `style/002` menciona `ui.contextMenu` y el `<select>` inline. **Falta** `accionClickDerecho === 'ninguno'` retorna sin nada, toggle binario de `bloqueado`, "Añadir a etiqueta". |
| Indicadores visuales (candado, oculto, copia) | `04-modes.md` | ⚠️ Parcial | Repartido entre `arch` y `style`. `style/003` no los detalla; el baseline `style/03` §12.3 sí (esquinas, colores, permanencia). |
| Cartas dentro de un mazo (no se dibujan en ningún modo) | `04-modes.md` | ❌ Ausente | Ligado a la ausencia del tipo `'mazo'`. |
| Paneles Recursos / Etiquetas (subida single/multi/folder, avisos de duplicado) | `04-modes.md` | ⚠️ Mínimo | `002`/`003` mencionan los 3 paneles y `panelState`. **Falta** todo el flujo de subida, `batchUploadSummaryModal`, orden alfabético, borrado con `isResourceInUse`. |
| Título de cabecera editable (`appTitle`) | `04-modes.md` | ⚠️ Mínimo | `003` (`appTitle.js`, `formatVersion`). **Falta** la edición in-place, `v.NNNNN` vs. `CURRENT_VERSION`, nombre de fichero por defecto. |
| Z-index de paneles flotantes (`panelStackOrder`) | `04-modes.md` | ✅ Bien | `style/001` (tabla z-index) + `style/002` (`panelStackOrder`, `15 + index`, no persistido). Capturado. |
| **Capa UI — módulos reutilizables** (`table.js`, `resizeHandle.js`, `rotationSlider.js`, `contextMenu.js`, `visualEditorModal.js`, `imageAdjustModal.js`, `globalShortcuts.js`, todos los `*Modal.js` con su firma) | `05-ui-layer.md` (3.900 palabras) | ⚠️ Parcial | `003-file-and-symbol-map` **lista todos los ficheros con una línea de responsabilidad cada uno** — buena cobertura de "qué hay". **Falta** por completo la firma/contrato de cada función (`renderComponentsOnTable({...})`, `attachResizeHandle({...})`, `openImageAdjustModal({...})`), los parámetros, la regla del `overflow: hidden` en contenedor interno, etc. |
| Build pipeline (grafo de imports, shim require, inline de assets, mutación de versión) | `06-persistence-build*.md` | ✅ **Bien** | `001-overview` "Build pipeline" (5 pasos) + `[gotcha]` "build.py mutates the repo" + formato `v{NNNN}` + fallo si falta `{VERSION}`. Muy buena captura, comparable al baseline. |
| Persistencia / autoguardado / arranque | `06-persistence-build*.md` | ✅ **Bien** | `002-state-events` "Render + persist wiring" (tabla evento→efecto), `arch.persist.*`, `parseState.reject`, secuencia de arranque numerada, `[gotcha]` sobre `resourcesSeeded` antes de `loadComponents`. Comparable al baseline. |
| Exportar/Importar con selección + `mergeImportedGame` (merge por tipo, keep-both, reparación de refs rotas, informe) | `06-persistence-build_v3.md` | ❌ **Ausente** | `004` menciona `model.persist.export` (shape) y `parseImportedComponents` "version-tolerant". **Falta** todo el flujo de importación: modales, modos add/overwrite, conflict keep-both, `nextImportedId`, reparación post-merge, `openImportReportModal`. |

### 2.2 Lo que el nivel `minimal` hace bien

1. **Namespace único (`00-namespace.md`).** Innovación respecto al baseline: un árbol canónico de nombres (`arch.*`, `model.*`, `ui.*`) donde cada concepto tiene exactamente una ruta. Facilita el cruce de referencias y evita ambigüedad. El baseline no tiene esto.
2. **Notación compacta y consistente.** `field: type = value`, `field: type in {a,b,c}`, invariantes `inv:` / `assert` / `post:`. Densa y sin prosa de relleno.
3. **Anclas al código (`anchor: src/core/persistence.js#STORAGE_KEY`).** Casi cada afirmación apunta a un símbolo concreto. El baseline lo hace en prosa ("vive en `core/state.js`"); aquí es sistemático.
4. **Etiquetas `[gotcha]`.** Captura varios peligros reales:
   - `ui/` no puede importar de `modes/` → por eso `sacarCartaDeMazo` vive en `state.js`.
   - `build.py` incrementa y reescribe `CURRENT_VERSION` en el repo.
   - Comentarios del código citan rutas `design/docs/**` que ya no existen (**dato valioso y correcto** — el baseline lo asume implícito).
   - Estado transitorio (`selectedComponentIds`, cámara) deliberadamente no persistido, se resetea al recargar.
5. **Tabla evento → efectos** (`002-state-events`): reproduce fielmente el cableado de `main.js` (`components:changed` → `renderAll` + `persistState`, etc.).
6. **`003-file-and-symbol-map`**: una fila por fichero fuente. Como índice de "dónde está qué", es exhaustivo y útil. Marca con `?` los ficheros no leídos en profundidad — honestidad sobre su propio alcance.
7. **Precisión.** No se detectan afirmaciones falsas. Lo que dice, lo dice bien. Los defaults (`zoom.min = 0.5`, `zoom.max = 2.5`, `radius.sm = 4px`, `STORAGE_KEY = "bgfactory:state"`) coinciden con el baseline.

### 2.3 Carencias críticas de arquitectura

Ordenadas por impacto:

1. **No existe documentación de los 8 tipos de componente.**
   El baseline dedica `02-component-types.md` (4.100 palabras) a `'texto'`, `'tableroSimple'`, `'dado'`, `'documento'`, `'carta'` (con sus 11 proporciones, shapes `Forma`/`TextBox`, recorte hex/triángulo), `'mazo'` (pila, zona de revelado, arrastrar cartas), `'tableroPersonalizado'`. El `minimal` solo tiene el enum de nombres en `004`. **Un desarrollador no puede añadir ni modificar un tipo con esta documentación** — no sabe qué `properties` lleva cada uno, ni sus defaults, ni sus reglas de redimensionado.

2. **Falta el checklist "qué revisar al añadir un tipo/colección" (`INDEX.md` §8 del baseline).**
   Son 10 puntos transversales (persistencia y `fileExport` serializan lista fija de campos; `isResourceInUse` recorre `properties` en profundidad; alta en `componentTypeModal.js` + `DEFAULT_*_PROPERTIES`; rama de dibujo en `componentRenderer.js`; `clamp` de proporción en `resizeHandle.js`; `getComponentsBounds`; recursos por defecto; guía de estilo; menú contextual; ficheros de prueba). Este es exactamente el tipo de conocimiento "sistémico" que no se deduce leyendo un fichero — hay que haber tropezado con ello. **Su ausencia es la pérdida más grave.**

3. **Falta toda la interacción de "Grupos en modo edición".**
   `getEffectiveGeneralProps` y `autoDissolve` están; pero la tabla de habilitación de "Agrupar"/"Desagrupar" según nº de unidades, las filas sintéticas del panel de Componentes, el movimiento en bloque, `reorderGroupBlock`, la anidación visual — nada de eso está.

4. **Los contratos de la capa UI no están.**
   `003` lista los ficheros, pero no las firmas. `renderComponentsOnTable(worldEl, components, { onSelect, onToggleSelect, selectedIds, onMove, onResize, canMove, onContextMenu, identifyMode, liftOnDrag, showLockIndicator, showHiddenIndicator })` — con el significado de cada parámetro — es información necesaria para tocar el render, y no aparece.

5. **Falta todo el flujo de Exportar/Importar con selección** (`mergeImportedGame`, modos, conflict-resolution, reparación de referencias, informe). Solo se menciona que `parseImportedComponents` es "version-tolerant".

6. **Detalle por campo del modelo de componente.** El shape está; los matices no (qué campo es override de grupo y cuál no, qué migración aplica a cada uno, `image` no lo usa ningún tipo, `subirAlMoverInteractuar` default distinto en `'carta'`/`'dado'`).

---

## 3. Style Bible (documentación de estilo)

### 3.1 Cobertura estructural

| Tema del baseline | Sección baseline | ¿Cubierto en minimal? | Observaciones |
|---|---|---|---|
| Stack de estilos (CSS plano, 1 fichero, vanilla JS, sin framework) | `INDEX.md` §1 | ✅ | `001-design-tokens` cabecera + `003` "CSS class naming". Capturado. |
| Design tokens `:root` (colores, radios, sombras, transición) | `01-tokens-visual.md` §2 | ✅ **Bien** | `001-design-tokens` reproduce **todos** los tokens en tabla (`--bg-table #c2c2c2`, `--accent-blue #2c7dd8`, `--section-accent #5b5f97`, `--shadow-1/2`, `--transition-fast 150ms ease`). Cobertura comparable al baseline, y añade columna "Usage". Muy buen resultado. |
| Regla `--accent-blue` = solo interactivo/seleccionado, nunca marca | `01-tokens-visual.md` §2 + `INDEX.md` §13 | ✅ **Bien** | Capturado como `[gotcha]` en `001` y como invariante `ui.tokens.accent-blue.rule` en el namespace. |
| Tipografía (escala de tamaños, pesos) | `01-tokens-visual.md` §3 | ✅ Parcial | `001` "Typography": familia, escala en rem, pesos 400/500/600. El baseline da una tabla tamaño→uso más explícita (`4rem` = resultado de dado, etc.); el minimal lista los rem sin uso asociado. |
| Espaciado (escala rem, pasos 0.25) | `01-tokens-visual.md` §4 | ❌ Ausente | No hay sección de espaciado. |
| Bordes y esquinas (escala de 2 radios) | `01-tokens-visual.md` §5 | ✅ | `001` "Radius" (tabla sm/lg con uso). |
| **Sistema de elevación de 3 niveles** (plano / flotante sutil / overlay; `.dice` usa `drop-shadow`; sombra opcional de tableros; extrusión configurable `profundidad`/`colorExtrusion`) | `01-tokens-visual.md` §6 | ⚠️ Muy parcial | `001` "Shadow" da los dos tokens y "level 1 / level 2". **Falta** el modelo de 3 niveles como sistema, la excepción `filter: drop-shadow` para siluetas no rectangulares, la sombra desactivable por componente, y **todo el mecanismo de extrusión configurable** (capas sólidas apiladas, `buildExtrusionLayers`, tope 40, sin efecto en `'texto'`). |
| Transiciones (150ms, no `:active`, no en contorno de selección) | `01-tokens-visual.md` §6 | ⚠️ Parcial | `001` "Motion" da el token. `003` menciona "all transitions 150ms". **Falta** "no usar `:active`", "no transicionar el contorno de selección ni el temblor del dado". |
| Botones (base compartida, primaria/secundaria/destructiva, hover, disabled, icono-solo, variantes de padding) | `02-componentes-layout.md` §9 | ✅ **Bien** | `style/002` "Buttons": tabla de clases + fondo + rol, propiedades compartidas (`padding: 0.5rem 1.5rem`, `border-radius: var(--radius-sm)`), estados `[hover]`/`[disabled]` con valores concretos (`opacity: 0.9`, `translateY(-1px)`, sombras de color). Cobertura muy buena. **Falta** el botón sobre fondo oscuro (toolbar), el botón cuadrado flotante `36px`, la variante `0.5rem 0.75rem`. |
| Layout (columna flex altura completa, header fijo, paneles) | `02-componentes-layout.md` §10 | ⚠️ Parcial | `002` "Floating panels" cubre los paneles (draggable/resizable/collapsible, `panelState`, z-order). **Falta** el layout de app (`body` flex column, header `3.5rem`, `#content` flex:1). |
| Z-index de overlays | `02-componentes-layout.md` §10 | ✅ **Bien** | `001` "Z-index scale" — tabla completa (`context menu 1000`, `modal overlay 1200`, panels `15 + stack`). **Discrepancia menor de valores** (ver §3.3). |
| Redimensionado (`.resize-handle`, esquina, `.resize-handle--tl`, variante columna) | `02-componentes-layout.md` §11 | ⚠️ Mínimo | `002` "Infinite table" menciona resize de paneles. **Falta** el patrón `.resize-handle` como bloque standalone, el aspecto (18px, grip diagonal `::after`), cursor `nwse-resize`, las variantes tl / columna. |
| Cabecera de tabla `sticky` | §11.1 | ❌ Ausente | — |
| Fila anidada `.component-list__row--member` (grupos) | §11.2 | ❌ Ausente | — |
| Nomenclatura BEM (`bloque__elemento--modificador`, estados transitorios sin prefijo, excepciones `.btn-*`, `.is-copy`/`.is-group-passenger`) | `INDEX.md` §7 | ✅ Parcial | `003` "CSS class naming": BEM-ish + `[gotcha]` sobre la excepción de botones de footer. **Falta** el detalle de estados transitorios (`.grabbing`, `.active`, `.lifted`), `.is-copy`/`.is-group-passenger` y su cascada, IDs reservados a layout. |
| Patrones de componente JS (función que crea `HTMLElement`, `className` una vez, `classList` para estados) | `INDEX.md` §8 | ✅ Parcial | `002` "Modal" da el contrato `.modal-overlay > .modal > .modal__footer`. **Falta** la regla general "un fichero por componente en `ui/`, camelCase; no `style.xxx=` salvo transforms dinámicos", y el patrón "color + grosor misma fila". |
| Icono de ayuda (`.help-icon`, modal al pulsar) | §12 | ❌ Ausente | — |
| **Modales de error / éxito / progreso** (`.modal__header--error`, `.modal__header--success`, `.progress-modal` con el único `@keyframes` del proyecto, sin cierre manual) | §12.1 / 12.1.1 / 12.1.2 | ⚠️ Mínimo | `002` "Feedback patterns" tiene una tabla (toast / error modal / progress modal / confirm / bulk confirm) con el fichero de cada uno. **Falta** todo el detalle visual: iconos, que `progress-modal` no reutiliza `.modal`, el `@keyframes progress-modal-spin`, el doble `requestAnimationFrame`. |
| Cursores (tabla de cursores por contexto, 3 cursores fijos en modo juego) | §12.2 | ❌ Ausente | — |
| **Etiqueta identificativa / título de componente / insignias** (`.component-id-label`, `.component-tooltip`, `.component-title-label`, badges de candado/oculto/copia/tiene-copias con sus 4 esquinas, colores, permanencia) | §12.3 (~1.500 palabras) | ❌ **Casi ausente** | `003` "Accessibility" menciona de pasada que hay iconos. `style/001` "Iconography" cubre la técnica de iconos inline SVG (24×24, `stroke=currentColor`, `stroke-width=2`) — eso **sí** está y bien. Pero las insignias y etiquetas de componente como sistema visual no están. |
| Modales anchas (tabla de clases con su `max-width`) | §12.4 | ❌ Ausente | — |
| Botón maximizar/restaurar de modal | §12.4.1 | ❌ Ausente | — |
| Checklist de selección agrupada (`.element-selection-group`) | §12.5 | ❌ Ausente | — |
| **Secciones dentro de pestañas** (`.modal__section` / `fieldset`, título informativo vs. des/activador, `--untitled`, zona con scroll interno, "número + botón que abre modal") | §12.6 (~1.200 palabras) | ❌ Ausente | Patrón muy usado en la app, sin rastro. |
| Menú desplegable de acciones (`.resource-add__menu` y reusos) | §12.7 | ⚠️ Mínimo | Solo se nombra `createFitButton`/menús en `002`. |
| Menú contextual de componente (`.context-menu`, 5 secciones, fila `<select>` inline, línea de descripción) | §12.8 | ⚠️ Parcial | `002` "Modal" no; pero `namespace` tiene `ui.modal.contract` y `002` menciona el `<select>` inline en la tabla de shortcuts/feedback. **Falta** la estructura de secciones, `.context-menu__info-*`, `.context-menu__description-*`. |
| Copiar/Pegar estilo (patrón visual) | §12.9 | ❌ Ausente | — |
| Grupo de botones icono-solo (`.align-group`, opción única vs. interruptores) | §12.10 | ❌ Ausente | — |
| Título de cabecera editable (`.app-title--hoverable` / `--editing`) | §12.11 | ❌ Ausente | — |
| Slider con marcas imantadas (`.rotation-field`, `ROTATION_SNAP_THRESHOLD_DEG`) | §12.12 | ❌ Ausente | — |
| Idioma (UI en español, infra en inglés, tabla por superficie) | (implícito en baseline) | ✅ **Bien** | `003` "Language": tabla por superficie + `[gotcha]` sobre símbolos que mezclan (`syncCopyWithOriginal` sobre campos español). **Aquí el minimal supera al baseline**, que no tiene una sección tan explícita. |
| Accesibilidad | (implícito en baseline) | ✅ **Aportación nueva** | `003` "Accessibility": estado observado (no claims), sin `prefers-reduced-motion`, contraste `--text-muted` como peor par, sin estrategia ARIA para paneles/menús. **El baseline no tiene esta sección.** Honesta y útil. |
| Microcopy (`confirm()` "¿Eliminar el/la…?", "Próximamente", toasts en pasado) | (disperso en baseline) | ✅ **Bien** | `003` "Microcopy patterns". Buena captura, incluso mejor organizada que el baseline. |
| Naming de versión (`v{NNNN}` / `v.{NNNN}`, `{VERSION}` marker) | `INDEX.md` + `06` baseline | ✅ **Bien** | `003` "Deliverable / version naming". Completo. |

### 3.2 Lo que el nivel `minimal` hace bien (estilo)

1. **Tabla de tokens completa y con columna de uso.** Es el mejor apartado del `minimal` — reproduce fielmente `:root` y añade el "para qué" de cada token.
2. **`[gotcha]` de `--accent-blue`** como regla, no como dato.
3. **Iconografía** (`ui.icons.inline-svg`): captura correctamente la técnica (SVG inline en JS, 24×24, `viewBox 0 0 24 24`, `fill=none`, `stroke=currentColor`, `stroke-width=2`, sin sprite compartido).
4. **Tabla de botones** con valores concretos de hover/disabled.
5. **Secciones de Idioma y Accesibilidad**: aportaciones que el baseline no formaliza, redactadas con rigor ("facts, not compliance claims").
6. **Z-index como tabla** y el `ui.modal.contract` (`.modal-overlay > .modal > .modal__footer` con `.btn-cancel`/`.btn-accept`/`.btn-eliminar`, y qué tecla dispara cada uno).
7. **`[gotcha]` sobre Enter en `<textarea>`** (newline gana) — detalle real capturado.

### 3.3 Carencias críticas de estilo

1. **Falta casi todo el catálogo de patrones de componente (`03-modales-menus.md`, 5.900 palabras).**
   El baseline documenta ~20 patrones visuales reutilizables con nombre de clase, aspecto, cuándo usarlos y cuándo NO: help-icon, modales de error/éxito/progreso, cursores, insignias de componente, modales anchas, botón maximizar, checklist agrupado, `.modal__section`, menú desplegable, menú contextual, copiar/pegar estilo, `.align-group`, título editable, slider imantado. **El `minimal` cubre 2-3 de forma superficial.** Un desarrollador que quiera "hacer una modal nueva como las demás" no tiene la referencia.

2. **El sistema de elevación de 3 niveles no está como sistema**, solo los dos tokens de sombra. Y **la extrusión configurable (`profundidad`/`colorExtrusion`) no aparece en absoluto** — ni en arquitectura ni en estilo, pese a ser un campo general de todos los componentes.

3. **Las excepciones catalogadas del baseline (`INDEX.md` §13, "Qué NO hacer") no están.**
   El baseline lista con precisión quirúrgica las excepciones aprobadas: bisel de dos tonos de `'tableroSimple'`/`'tableroPersonalizado'`/`'dado'` (`shadeColor`), `border-radius` de "contenedores destacados" reutilizado por `'carta'`, recorte hex/triángulo con doble `clip-path` anidado, `--section-accent` de uso único, parpadeo/temblor del dado que NO son animación CSS, efecto `.lifted`, `.drop-target` sobre mazo, `.carta--flip-feedback`. **Todo esto — que es literalmente "las trampas del CSS de este proyecto" — falta.** Es conocimiento imposible de reconstruir sin haberlo vivido.

4. **Nomenclatura BEM incompleta.** Falta el tratamiento de estados transitorios (`.grabbing`, `.lifted`, `.drop-target`, `.active`), las clases transversales `.is-copy` / `.is-group-passenger` y su orden en la cascada, la regla de IDs reservados a layout.

5. **Espaciado, redimensionado, cursores, cabecera sticky, filas anidadas**: sin cobertura.

---

## 4. Diagnóstico transversal

### 4.1 Qué tipo de conocimiento se pierde

El `minimal` captura bien **lo que es literal en el código**: shapes de datos, defaults, enums, nombres de fichero, cableado de eventos, pipeline de build, tokens CSS. Todo eso está en 1-2 sitios del código y se lee de una pasada.

El `minimal` **no captura lo que es emergente o histórico**:
- **Reglas transversales** ("estos 8 campos se serializan en 3 sitios; si añades uno, tócalos los 3").
- **Excepciones aprobadas** ("el bisel de dos tonos está permitido solo en estos 3 tipos").
- **El *porqué*** de las decisiones ("`sacarCartaDeMazo` está en `core/` porque `ui/` no puede importar `modes/`" — este sí lo pilla; pero la mayoría no).
- **Checklists de mantenimiento** ("al añadir un tipo, revisa estos 10 puntos").
- **Contratos de función** (firmas con el significado de cada parámetro).
- **El catálogo de patrones visuales** con "cuándo sí / cuándo no".

Esto es coherente con lo esperable de una generación "solo mirando el código": un LLM leyendo `src/` una vez ve *qué hace* el código, no *qué convenciones lo gobiernan* ni *con qué te vas a tropezar*.

### 4.2 Precisión

**No se han detectado afirmaciones incorrectas** en el `minimal`. Es conservador: dice menos, pero lo que dice es fiable. Marca explícitamente su propio alcance (`?` en ficheros no leídos a fondo, "inferred from imports/callers"). Esto es un punto fuerte de diseño.

**Discrepancia menor a verificar contra el código fuente:** los valores de z-index difieren entre las dos documentaciones.

| Capa | Baseline (`02-componentes-layout.md` §10) | Minimal (`style/001`) |
|---|---|---|
| Overlay de modal | `1000` | `1200` |
| Menú contextual / menú de columna | `1050` | `1000` |
| Toolbar de edición | `99` | `99` ✅ |
| Header | `100` | `100` ✅ |
| Mode switcher | `101` | `101` ✅ |

Una de las dos está desactualizada respecto al CSS actual. Dado que el `minimal` se generó leyendo el código de 0.9.6b9 y el baseline puede haber quedado atrás, **es plausible que el `minimal` tenga razón aquí** — pero conviene confirmarlo en `src/styles/main.css`. (Si el `minimal` acierta, es un ejemplo de la generación automática detectando drift del baseline, igual que hace con las rutas `design/docs/**` obsoletas.)

### 4.3 Organización

En igualdad de contenido, el `minimal` está **mejor organizado** que el baseline:
- Namespace único evita duplicación y ambigüedad.
- Notación compacta uniforme.
- Anclas sistemáticas al código.
- `[gotcha]` como etiqueta de primera clase.
- Cada fichero abre con `**Area**:` y un `INDEX` navegable.

Si al nivel `minimal` se le pidiera *más profundidad* manteniendo este formato, el resultado sería excelente.

---

## 5. Conclusiones y recomendaciones

### 5.1 Sobre el nivel `minimal` como tal

**Cumple su propósito declarado.** Como contexto de arranque compacto —"dale a un agente/desarrollador nuevo un mapa fiable del sistema en 4.500 palabras"— es un buen artefacto: correcto, navegable, con las trampas estructurales principales señaladas y anclado al código.

**No sustituye documentación mantenida a mano.** Cubre ~12 % del volumen de arquitectura y ~18 % del de estilo del baseline, y lo que falta es desproporcionadamente el conocimiento de más valor (checklists, excepciones, contratos, catálogo de patrones, el *porqué*).

### 5.2 Prioridades si se quiere subir de nivel

Por orden de retorno:

1. **Tabla de `properties` por cada uno de los 8 tipos de componente** (hoy: cero cobertura, impacto: alto).
2. **Checklist "qué revisar al añadir un tipo/colección"** (§8 del baseline) — regenerable si el generador sabe buscar "listas fijas de campos serializados en varios sitios".
3. **Firmas de las funciones clave de la capa UI** (`renderComponentsOnTable`, `attachResizeHandle`, `openImageAdjustModal`, `openContextMenu`, `openVisualEditorModal`).
4. **Sección "Qué NO hacer" / excepciones catalogadas** de la Style Bible (§13 baseline).
5. **Sistema de elevación de 3 niveles + extrusión configurable** (hoy: solo 2 tokens de sombra).
6. **Catálogo de patrones de modal/menú** (`.modal__section`, modales de error/éxito/progreso, menú contextual con sus secciones, checklist agrupado).
7. **Flujo de Exportar/Importar** (`mergeImportedGame`, conflict-resolution, informe).

### 5.3 Verificación pendiente

- Confirmar en `src/styles/main.css` los z-index reales (§4.2). Si el `minimal` acierta, actualizar el baseline.
- Confirmar que las rutas `design/docs/**` citadas en comentarios del código están efectivamente obsoletas (el `minimal` lo afirma; encaja con que el baseline vive en `previo-sdd/docs/`).
