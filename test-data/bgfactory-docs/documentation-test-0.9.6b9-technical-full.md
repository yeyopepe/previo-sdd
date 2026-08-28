# Informe comparativo de documentación TÉCNICA — Previo 0.9.6b9 (nivel `full`) vs. baseline

**Fecha:** 2026-08-28
**Objeto:** Comparar la documentación **técnica** (arquitectura + Style Bible) que Previo 0.9.6b9 genera en nivel `full` (solo mirando el código de la app) frente a la documentación de referencia (`_baseline`), creada y mantenida a mano a lo largo de la evolución del proyecto.

**Fuentes:**
- Referencia: `test-data/bgfactory-docs/_baseline/architecture/` y `.../style/`
- Bajo prueba: `test-data/bgfactory-docs/0.9.6b9/full/architecture/` y `.../style/`

> Informe hermano de `documentation-test-0.9.6b9-technical-minimal.md` (mismo método, misma pareja arquitectura+estilo, pero para el nivel `full` en lugar de `minimal`).

---

## 1. Resumen ejecutivo

| Dimensión | Baseline | 0.9.6b9 / **full** | (recordatorio: `minimal`) |
|---|---|---|---|
| Arquitectura — ficheros de contenido | 6 (+ INDEX + 2 alt.) | **5** (+ INDEX + `00-namespace`) | 4 |
| Arquitectura — palabras (sin INDEX/namespace) | ~18.700 | **~4.350** (~23 % del **volumen**) | ~2.250 (~12 %) |
| Style Bible — ficheros de contenido | 3 (+ INDEX) | **5** (+ INDEX) | 3 |
| Style Bible — palabras (sin INDEX) | ~8.300 | **~3.600** (~43 % del **volumen**) | ~1.500 (~18 %) |
| Cobertura conceptual (temas del baseline tratados) | 100 % (referencia) | **~75–85 %** (ver §2.1 / §3.1) | ~40–50 % |
| `[gotcha]` / `[motivación]` explícitos | dispersos en prosa | **densos y etiquetados** | presentes |
| Tabla de decisiones de diseño registradas | no formalizada | **sí** (`005`, 11 filas con racional) | no |
| Sección de seguridad | dispersa / implícita | **sí, dedicada** (`005` + `security.*`) | no |

> **Dos métricas distintas, no confundir.** El ratio de palabras (**~23 % arquitectura / ~43 % estilo**) mide **volumen de prosa**, no cantidad de información cubierta. Por **conceptos del baseline efectivamente tratados**, `full` está en **~75–85 %** (tabla §2.1: de ~30 temas, la mayoría ✅ *Bien* o mejor —varios *"Supera al baseline"*—, solo 2 ❌ ausentes y ~8 ⚠️ parciales). La diferencia entre ambos números se explica por **densidad de escritura**: `full` tabula y comprime en notación lo que el baseline desarrolla en prosa (una fila de tabla ≈ un párrafo del baseline). El volumen que realmente falta **no está repartido**: se concentra en tres documentos densos del baseline (`02-component-types.md` 4.100 pal., `03-modales-menus.md` 5.900 pal., `05-ui-layer.md` 3.900 pal. → ~14.000 de las ~18.700 palabras de arquitectura), donde `full` comprime a tabla o cubre ~la mitad de los patrones. Cuando este informe dice "cubre ~23 %", se refiere **siempre a volumen**.

**Veredicto general:** el nivel `full` es un **salto cualitativo grande respecto a `minimal`**, no solo cuantitativo. En volumen es ~23 % de arquitectura y ~43 % de estilo del baseline —pero cubre la gran mayoría de sus **conceptos**— y, a diferencia de `minimal`, **incluye contenido que el baseline no tiene**: una tabla de decisiones de diseño con racional, una sección de seguridad con modelo de amenazas y huecos del sanitizador, un mapa de módulos con columna de pureza, y contratos de API (event bus, getters/mutators, `renderComponentsOnTable` opts).

Sigue **sin sustituir al baseline** como documentación única: le falta el catálogo de los 8 tipos de componente al nivel de detalle del baseline (`02-component-types.md`, 4.100 palabras → aquí ~1 tabla comprimida), el catálogo de ~20 patrones visuales de modal/menú (`03-modales-menus.md`, 5.900 palabras → aquí ~5 bloques), el checklist "qué revisar al añadir un tipo", y toda la interacción fina de grupos en el panel. Pero como **documentación técnica de referencia autónoma, el nivel `full` ya es utilizable** — un desarrollador nuevo puede orientarse y tomar decisiones con ella; solo necesitará leer código para los detalles finos de un tipo concreto.

**Comparación directa `minimal` → `full`:** `full` no es "`minimal` con más palabras". Reorganiza (arquitectura pasa de 4 a 5 docs temáticos: Overview / State&events / Data model / Interaction model / Build&security; estilo de 3 a 5: Tokens / Layout / Components / Interaction&a11y / Writing), añade tablas de input→efecto por modo, añade la capa de seguridad y de decisiones, y sube la densidad de `[gotcha]`. El namespace crece de ~730 a ~1.660 palabras y ahora cubre `security.*`, `import.*`, `deck.*`, `interactions.*`, `text-variables.*`.

---

## 2. Arquitectura

### 2.1 Cobertura estructural

| Tema del baseline | Fichero baseline | ¿Cubierto en `full`? | Dónde / observaciones | vs. `minimal` |
|---|---|---|---|---|
| Objetivo y restricciones | `INDEX.md` §1 | ✅ **Bien** | `001` "Product": cliente puro, un `.html` autocontenido, sin backend/cuentas/red, offline tras carga, dos modos. | ⬆️ más completo |
| Arquitectura por capas + grafo de dependencias | `INDEX.md` §2 | ✅ **Bien** | `001` "Layers" (tabla con "May import") + `arch.layers.order` + `[gotcha] ui/ ↛ modes/` con su consecuencia (`sacarCartaDeMazo` en `state.js`). Equivalente al baseline y con la regla como decisión registrada (`005`). | ≈ igual |
| **Mapa de módulos `core/`** | (disperso en baseline) | ✅ **Supera al baseline** | `001` "core/ module map": **23 ficheros, uno por fila, con columna de pureza** (`pure` / `mutates module state` / `localStorage I/O` / `DOM` / `canvas`). El baseline no tiene una tabla así. | ⬆️ nuevo |
| Convenciones de código (módulos ES, comentarios) | `INDEX.md` §7 | ⚠️ Parcial | `005` "Build pipeline" documenta qué `import`/`export` soporta el build (solo named). `style/005` cubre naming de identificadores. **Falta** la política de comentarios ("solo el porqué no evidente", estilo telegráfico, excepción `vendor/`). | ⬆️ algo más |
| **Checklist al añadir un tipo/colección** (10 puntos) | `INDEX.md` §8 | ❌ **Ausente** | Sigue sin equivalente. `003` lista dónde viven los `DEFAULT_*_PROPERTIES` y menciona la detección profunda de `isResourceInUse`, pero **no como checklist accionable "revisa estos N sitios"**. Pérdida heredada de `minimal`. | ≈ igual (ausente) |
| Modelo genérico de componente (shape + tabla "quién lo edita") | `01-component-model.md` | ✅ **Bien** para el shape | `003` "Component": shape completo en notación con defaults y comentarios por campo (`profundidad` = extrusión 3D, `subirAlMoverInteractuar` = bump order en play). **Falta** la columna "Quién lo edita" (qué pestaña/modal toca cada campo) y algunos matices (`tooltipTexto` no es override de grupo pero `mostrarTooltip` sí). | ⬆️ más detalle |
| Lógica de `order` | `01-component-model.md` | ✅ **Bien** | `002` tabla de mutadores: `addComponent` (bump +1, nuevo=1), `reorderComponent` (clamp `1..n`), `reorderGroupBlock` (bloque de N, sin early-exit), `compactOrders` en carga. Cubre lo esencial. **Falta** el clamp `[1, n-k+1]` del bloque y el detalle del panel. | ⬆️ mucho más |
| Copias vinculadas (`copyOf`) | `01-component-model.md` | ✅ **Bien** | `003` "Linked copies": id `-COPY-NNN`, campos sincronizados (lista completa), `NON_SYNCED_PROPERTY_KEYS`, `x/y/order` nunca, `bloqueado/oculto` solo si `sincronizado`, poner cualquiera de los dos directamente lo pone `sincronizado=false`, cascada de borrado, `renameCopyId`. **Muy buena cobertura.** Falta: la modal reducida `copyComponentModal.js`, el menú contextual condicionado. | ⬆️ mucho más |
| Clones (`cloneComponent`, `nextCloneId`) | `01-component-model.md` | ✅ **Bien** | `003` "Clones": id `{rootId}({n})`, sin `copyOf`, `x/y +30`, `order=null`, `groupId=null`. Equivalente al baseline. | ⬆️ nuevo |
| Sistema de variables de texto (`{cards_current}`) | `01-component-model.md` | ✅ **Bien** | `002`/namespace `text-variables.*`: `resolveTextVariables`, `getAvailableVariables`, `{ mazo: {'cards_current'} }`, `[gotcha]` deja literal si no aplica. Cubierto. Falta: que se recalcula en cada render. | ⬆️ mucho más |
| **Los 8 tipos de componente y sus `properties`** | `02-component-types.md` (4.100 pal.) | ⚠️ **Comprimido** | `003` "Per-type `properties` defaults": una lista de ~6 líneas, una por tipo, con los campos de `properties` enumerados pero **sin defaults por campo, sin rangos, sin reglas de redimensionado, sin comportamiento de render**. Ej.: `dado: { colorCuerpo, ..., numeroMaximoCaras = 6, listaValores, ... }` — pero no "2–100", ni "mínimo 2 valores", ni las siluetas por nº de resultados. **El catálogo de proporciones de carta** se menciona (`shape ∈ {rect,hex,triangle,circular}`) pero no las 11 entradas ni el borde interior de doble `clip-path`. | ⬆️ algo más que `minimal` (que solo tenía el enum), pero muy lejos del baseline |
| Modelo de etiqueta (`tag`) | `03-groups-resources.md` | ✅ Parcial | `003` "Tag": shape, membership plana many-to-many, `getComponentsUsingTag`, `isTagNameTaken` (case-insensitive, trimmed), historial de rename `Mazo→Grupo→Etiqueta`. **Falta** el alta al vuelo desde la modal, el panel dedicado, la columna "Elementos". | ⬆️ más |
| Modelo de grupo + `getEffectiveGeneralProps` | `03-groups-resources.md` | ✅ **Bien** | `003` "Group": shape, override de props del registro sobre el miembro, auto-disolución ≤1, `deriveMissingGroups`, `id` no autogenerado (`grupo-N` vía `nextGroupId`). Como **decisión registrada** en `005` (`group.decision.group-props-override-member`). Falta: `isGroupIdTaken`, edición desde `groupModal.js`. | ⬆️ más |
| Modelo de recurso + WebP + `DEFAULT_RESOURCES` | `03-groups-resources.md` | ✅ **Bien** | `003` "Resource": shape, `resourceTypeForFileName` con **las extensiones exactas** (`png jpg jpeg gif svg webp` / `ttf otf woff woff2`), WebP q=0.92 solo raster, `DEFAULT_RESOURCES` sembrado una vez con ids fijos, `isResourceInUse` deep walk bloquea borrado. **Muy buena.** Falta: `resourcesSeeded` backfill para guardados antiguos. | ⬆️ mucho más |
| Migración de `'ficha'` → `'carta'` | `03-groups-resources.md` | ⚠️ Parcial | `002` pipeline de migración lista `migrateFichas` (paso 1) con una línea. `004` (import) y `005` (namespace `import.ficha-migration`) mencionan la conversión y el flujo interrumpible (continue-without / abort). **Falta** el mapeo campo a campo (`forma`→`proporcion`, `fondoTipo`, qué cuenta como error). | ⬆️ más |
| Portapapeles de estilo | `03-groups-resources.md` | ⚠️ Mínimo | `001` module map: "in-memory card-style copy/paste, never persisted". `style/003` no lo cubre. **Falta** el shape del dato, `validateStyleClipboardForPaste`, el flujo. | ⬆️ algo |
| **Pipeline de migración al cargar** (8 pasos ordenados) | `06-persistence-build*.md` | ✅ **Bien** | `002` "Load-time migration pipeline": **los 8 pasos en orden con qué hace cada uno**, + contrato ("best-effort, in-place, never throw") + `[motivación]` sobre el rename chain. Comparable al baseline. | ⬆️ mucho más |
| Modo juego vs. modo edición | `04-modes.md` | ✅ **Bien** | `004` documento entero. Play: filtros (oculto vía `getEffectiveGeneralProps`, cartas en mazo), **tabla input→efecto** (click en dado/carta/mazo, drag carta sobre mazo, drag pieza, right-click), menú contextual. Edit: 3 paneles, `selectedComponentIds` vs. `primarySelectedIds`, reglas de selección, unidad = grupo o componente. **Muy buena cobertura.** | ⬆️ mucho más |
| **Grupos en modo edición** (tabla de habilitación, filas sintéticas del panel, `reorderGroupBlock`, edición individual) | `04-modes.md` (~1.500 pal.) | ⚠️ Parcial | `004` "Context menu (edit)" tiene la **tabla de reglas** (`unitCount`, `canGroup`, `canUngroup`, menú suprimido si multi-unit con grupo, grupo único → opera sobre el registro). Cubre el *criterio*. **Falta** la parte de UI del panel: filas sintéticas de grupo, anidación visual `--member`, orden editable del bloque, "Clonar"/"Copiar" deshabilitados en miembro agrupado. | ⬆️ bastante más |
| Menú contextual (juego y edición) | `04-modes.md` | ✅ **Bien** | `004` cubre ambos: juego (Bloquear/Desbloquear toggle, omitido para copia sincronizada, `Barajar`/`Ver contenido` de mazo, `Meter en mazo` de carta, filas de interacción), edición (`Ocultar`/`Clonar`/`Copiar`/`Eliminar`/`Agrupar`/`Desagrupar`, `Añadir a etiqueta`). Falta: `<select>` inline, deshabilitado sin etiquetas. | ⬆️ mucho más |
| Cartas dentro de un mazo (no se dibujan en ningún modo) | `04-modes.md` | ✅ **Bien** | `004` play filtra `getCartaIdsEnAlgunMazo`; namespace `deck.cards-hidden-when-in-deck`. Cubierto. | ⬆️ nuevo |
| Indicadores visuales (candado, oculto, copia) | `04-modes.md` | ✅ **Bien** (en estilo) | `style/003` "Overlaid piece badges": tabla de 4 badges con esquina/bg/significado, `pointer-events:none`, `[gotcha]` copy vs has-copies solo se distinguen por color. Mejor organizado que el baseline. | ⬆️ mucho más |
| Paneles Recursos / Etiquetas (subida single/multi/folder, duplicados) | `04-modes.md` | ⚠️ Parcial | `004` menciona los flujos de subida en `editMode.js`. `003` da las allowlists. **Falta** el detalle: `batchUploadSummaryModal`, subcarpetas filtradas, `resourceReplaceConfirmModal`, orden alfabético. | ⬆️ algo |
| Título de cabecera editable (`appTitle`) | `04-modes.md` | ⚠️ Parcial | `002` state shape (`appTitle`), `style/005` (`DEFAULT_APP_TITLE`, `formatVersion` → `v.{NNNNN}`, sufijo no editable). **Falta** la edición in-place, el nombre de fichero por defecto. | ⬆️ algo |
| Z-index de paneles flotantes | `04-modes.md` | ✅ **Bien** | `style/001` "Z-index ladder" (tabla completa) + `style/002` (`applyPanelStackOrder`, `15 + stackIndex`, transitorio). | ⬆️ más |
| **Capa UI — contratos de funciones** (`renderComponentsOnTable({...})`, `attachResizeHandle`, `openImageAdjustModal`, etc.) | `05-ui-layer.md` (3.900 pal.) | ⚠️ Parcial | `001` "modes/ + ui/ high level" (tabla de ~8 ficheros clave con rol) + `004` menciona `renderComponentsOnTable(worldEl, components, opts)` y que `opts` difiere por modo. **Falta** la firma completa con el significado de cada parámetro (`onSelect`, `onToggleSelect`, `selectedIds`, `onMove`, `canMove`, `identifyMode`, `liftOnDrag`, `showLockIndicator`…), y la regla del `overflow:hidden` en contenedor interno. | ⬆️ algo más que `minimal` |
| Build pipeline | `06-persistence-build*.md` | ✅ **Supera al baseline** | `005` "Build pipeline": **8 pasos detallados** (version bump, DFS del grafo, transform por módulo con los patrones regex, runtime shim, inline CSS/HTML, `{VERSION}` placeholder, output gitignored) + `[gotcha]` sobre `IMPORT_PATTERN`/`EXPORT_*_PATTERN` (solo named), tabla MIME, `obfuscate_bundle.js` opcional. Más completo que el baseline. | ⬆️ más |
| Persistencia / autoguardado / arranque | `06-persistence-build*.md` | ✅ **Bien** | `002` "Render/persist wiring" (tabla evento→efecto), "Startup sequence" numerada con **dos `[gotcha]` sobre el orden de `resourcesSeeded`** (antes de `loadComponents`, y `markResourcesSeeded` antes de añadir). `003` "Persistence" tabla. Comparable/superior al baseline. | ⬆️ más |
| Exportar/Importar con selección + `mergeImportedGame` | `06-persistence-build_v3.md` | ✅ **Bien** | `004` "Import / export": **flujo de 6 pasos** (`parseImportedComponents` sin version gate → selección → confirm `{mode, conflictMode}` → migración de fichas con errores → `mergeImportedGame` pura dentro de `runWithProgressModal` → `overwrite` aplica `appTitle`, merge de grupos). Namespace `import.*`. **Falta** el detalle de `nextImportedId` (keep-both), la reparación post-merge de refs rotas y `openImportReportModal` (mencionado en `style/004` como surface, no su lógica). | ⬆️ mucho más |
| **Seguridad** (modelo de amenazas, `sanitizeHtml`, huecos) | (disperso/implícito en baseline) | ✅ **Supera al baseline** | `005` "Security posture": modelo de amenazas (el `.html` reabre contenido de usuario, posible origen `file://`), `sanitizeHtml` (qué quita: `<script>`, `on*`, `javascript:` en href/src), **`[gotcha]` denylist no allowlist con la lista exacta de huecos** (`<iframe>`/`<object>`/`<embed>`, `style`, `srcdoc`, `data:`, `formaction`, SVG script), **`documento` embebe url en `<iframe>` SIN `sandbox`**, tabla de otras superficies cubiertas. El baseline no tiene esto formalizado. | ⬆️ **nuevo, valioso** |
| **Decisiones de diseño registradas** | (no formalizado en baseline) | ✅ **Supera al baseline** | `005` "Recorded design decisions": **11 filas** (`python-not-node`, `custom-require-runtime`, `ui-cannot-import-modes`, `generic-component-no-subclasses`, `synchronous-full-persist`, `best-effort-load-migrations`, `import-skips-version-check`, `pure-compute-caller-applies`, `sanitize-denylist`, `group-props-override-member`, `build-owns-version-counter`), **cada una con racional**. Contenido genuinamente nuevo. | ⬆️ **nuevo, valioso** |
| Configuración / entorno | (implícito baseline) | ✅ | `005` "Configuration / environment": sin env vars, sin config, sin feature flags; solo Python 3 en PATH; lista de gitignored. | ⬆️ nuevo |

### 2.2 Lo que `full` hace bien (arquitectura)

1. **Contratos de API explícitos.** El event bus (`on/off/emit`, `Map<string, Set<handler>>`, síncrono, sin wildcard), el patrón getter/mutator por colección (`get/add/replace/remove/load{X}`), la tabla de qué evento emite cada mutador. El baseline lo cuenta en prosa; aquí está tabulado.
2. **Tabla de eventos con alias legacy.** `tags:changed` ← también emitido/escuchado como `decks:changed`/`groups:changed`, y el `[gotcha]` de que `groups:changed` **no** es el evento del registro de agrupación. Trampa real, bien marcada.
3. **Pipeline de migración completo y ordenado** (8 pasos), con el contrato "never throw" y la `[motivación]` del rename chain.
4. **Secuencia de arranque con los dos `[gotcha]` de orden** de `resourcesSeeded` — bugs reales evitados, documentados.
5. **Sección de seguridad dedicada** con modelo de amenazas y la lista exacta de huecos del sanitizador denylist. Esto es lo que un revisor de seguridad necesita y el baseline no lo reúne en un sitio.
6. **Tabla de decisiones con racional** — convierte "así está hecho" en "así está hecho *porque*". 11 decisiones.
7. **Mapa de módulos con columna de pureza** — de un vistazo se ve qué es lógica pura y qué toca DOM/localStorage/canvas.
8. **Namespace ampliado** (`security.*`, `import.*`, `deck.*`, `interactions.*`, `text-variables.*`, `globalShortcuts.*`) — más conceptos con ruta canónica que en `minimal`.
9. **Precisión de valores concretos**: extensiones de recurso exactas, q=0.92, `STORAGE_KEY = 'bgfactory:state'`, `CURRENT_VERSION = 'v00230'`, `MAZO_REVEAL_GAP = 20`, formato `v{NNNNN}`.

### 2.3 Carencias que persisten (arquitectura)

1. **El catálogo de los 8 tipos sigue comprimido.** `003` da una lista de campos de `properties` por tipo, pero sin defaults por campo, rangos, reglas de redimensionado ni comportamiento de render. El baseline `02-component-types.md` (4.100 palabras) es una especificación de tipo; `full` da ~1 tabla. **Un desarrollador puede saber *qué campos* tiene un `dado` pero no que `numeroMaximoCaras` va de 2 a 100, ni cómo cambia la silueta.**
2. **Falta el checklist "qué revisar al añadir un tipo/colección"** (§8 del baseline). Sigue sin equivalente accionable.
3. **Contratos de la capa UI incompletos.** Se nombra `renderComponentsOnTable(worldEl, components, opts)` pero no se enumeran las `opts` con su semántica. El resto de la capa UI (`resizeHandle`, `rotationSlider`, `imageAdjustModal`, `visualEditorModal`, `contextMenu`) aparece en el module map con una línea, sin firma.
4. **Interacción de grupos en el panel de Componentes**: el *criterio* (tabla de reglas) está; la *UI* (filas sintéticas, anidación `--member`, orden de bloque, acciones deshabilitadas) no.
5. **Detalle por campo del modelo de componente**: falta "quién lo edita" y qué campo es override de grupo.
6. **Reparación post-merge de importación** (refs rotas → null, etiqueta ausente → crear/vincular, informe fila a fila) solo aparece como "surface" en `style/004`, no su lógica en arquitectura.

---

## 3. Style Bible

### 3.1 Cobertura estructural

| Tema del baseline | Sección baseline | ¿Cubierto en `full`? | Observaciones | vs. `minimal` |
|---|---|---|---|---|
| Stack de estilos (CSS plano, 1 fichero, vanilla) | `INDEX.md` §1 | ✅ | `002` "Page shell" + `005` "CSS class naming" (menciona `main.css` ~3374 líneas, orden de bloques). | ⬆️ más |
| Design tokens `:root` | `01-tokens-visual.md` §2 | ✅ **Bien** | `001` "Color tokens": **tabla completa** con valor y uso (incl. `--bg-table-dot`, `--section-accent`). `[gotcha]` "paleta gris no blanco/negro, un solo acento". **Falta** que el focus ring `0 0 0 3px rgba(44,125,216,0.15)` no está tokenizado — aunque `full` **sí lo dice** explícitamente. | ⬆️ más |
| Regla `--accent-blue` = solo interactivo | `01-tokens-visual.md` + `INDEX.md` §13 | ✅ **Bien** | `001` `[gotcha]` + namespace `ui.selection.outline`. | ≈ |
| Tipografía | `01-tokens-visual.md` §3 | ✅ **Bien** | `001` "Typography": tabla con font body/mono, tamaños en uso, pesos, `tabular-nums` en lecturas de zoom. Comparable al baseline. | ⬆️ más |
| Espaciado | `01-tokens-visual.md` §4 | ⚠️ **Reconocido pero sin escala** | `001` "Spacing": **"No spacing scale token"** — lista los valores rem ad hoc dominantes (`0.25/0.35/0.5/0.75/1/1.5`), padding de modal/panel. El baseline sí presenta una escala; `full` documenta que **no la hay** como sistema. Honesto. | ⬆️ nuevo |
| Bordes y esquinas (2 radios) | `01-tokens-visual.md` §5 | ✅ **Bien** | `001` "Radius" tabla sm/lg con uso. | ⬆️ más |
| **Sistema de elevación de 3 niveles + extrusión** | `01-tokens-visual.md` §6 | ✅ **Bien** | `001` "Shadow": los 2 tokens + `[gotcha]` **silueta no rectangular usa `filter: drop-shadow`, no `box-shadow`** (con qué clases), "elevation system" (piezas en reposo `--shadow-1`, `.lifted` transitorio con valores exactos, `.carta--flip-feedback` segundo lift). **Falta**: el mecanismo de **extrusión configurable** (`profundidad`/`colorExtrusion`, capas apiladas, `buildExtrusionLayers`, tope 40) — igual que en `minimal`, **no aparece en estilo**; sí de refilón en `arch/003` (`profundidad: number = 0 # 3D extrusion thickness`). | ⬆️ bastante más (drop-shadow, lifted, flip-feedback) pero extrusión sigue casi ausente |
| Transiciones | `01-tokens-visual.md` §6 | ✅ **Bien** | `001` "Motion": token `--transition-fast`, one-offs (zoom 60ms, spinner 0.8s, card-flip), **"No `prefers-reduced-motion` anywhere"**. `004` lo repite. Falta: "no usar `:active`", "no transicionar el contorno de selección". | ⬆️ más |
| **Botones** (base, primaria/secundaria/destructiva, hover, disabled, variantes) | `02-componentes-layout.md` §9 | ✅ **Bien** | `003` "Buttons": tabla de 4 clases (bg/text/notas con **valores de hover exactos**: `translateY(-1px)`, `0 3px 8px rgba(44,125,216,.35)`, `.btn-eliminar` `margin-right:auto`). `[gotcha]` standalone sin bloque BEM. `004` repite estados. **Falta**: el botón sobre fondo oscuro (toolbar), el botón cuadrado flotante `36px`, la variante `0.5rem 0.75rem`. | ⬆️ más |
| **Layout** (columna flex, header fijo, `#content`) | `02-componentes-layout.md` §10 | ✅ **Bien** | `002` "Page shell": **bloque completo** (`body` flex column 100vh, `h1` 3.5rem gradiente z100, `#edit-toolbar` z99, `#mode-switcher` fixed z101, `#content` flex 1, `footer` fixed z10), `.infinite-table` con grid radial 32px. Comparable al baseline. `[gotcha]` sin media queries. | ⬆️ mucho más |
| Z-index de overlays | `02-componentes-layout.md` §10 | ✅ **Bien** | `001` "Z-index ladder" tabla. **Discrepancia de valores** (ver §4.2). | ⬆️ más |
| **Redimensionado** (`.resize-handle`, `--tl`, variante columna) | `02-componentes-layout.md` §11 | ✅ **Bien** | `003` "Other reusable widgets" fila `.resize-handle` (18px esquina inferior derecha, grip diagonal `#999` → accent + `scale(1.15)`, `--tl` top-left). `003` "Tables" cubre `.column-resize-handle`. **Falta**: cursor `nwse-resize` uniforme, mínimo interno 60px. | ⬆️ mucho más |
| Cabecera de tabla `sticky` | §11.1 | ✅ | `003` "Tables": `th: sticky top 0, z 2, bg var(--bg-subtle)`. | ⬆️ nuevo |
| Fila anidada `.component-list__row--member` | §11.2 | ✅ **Bien** | `003` "Tables": `--member` → `bg var(--accent-blue-light)`, id cell `padding-left: 1.75rem`, sin línea conectora, "reads as folder contents". Comparable al baseline. | ⬆️ nuevo |
| Nomenclatura BEM + estados transitorios + `.is-copy`/`.is-group-passenger` | `INDEX.md` §7 | ✅ **Bien** | `005` "CSS class naming": BEM-ish, **lista de state modifiers** (`.is-copy`, `.is-group-passenger`, `.is-empty`, `.grabbing`, `.active`, `.lifted`, `--visible`, `--selected`, `--maximized`…), `[gotcha]` excepción `.btn-*`. `004` cubre el uso visual de `.is-copy`/`.is-group-passenger`. **Falta**: la regla de orden en la cascada (`.is-group-passenger` gana a `.is-copy`), IDs reservados a layout. | ⬆️ mucho más |
| Patrones de componente JS | `INDEX.md` §8 | ✅ Parcial | `003` cubre botones/tablas/badges/option groups como patrones. `002` da el contrato de modal. **Falta**: "un fichero por componente en `ui/`, camelCase; no `style.xxx=` salvo transforms dinámicos", el patrón "color + grosor misma fila". | ⬆️ más |
| Icono de ayuda (`.help-icon`, modal) | §12 | ✅ | `003` "Other reusable widgets": `.help-icon` 16px, `bg --text-muted` → accent, `cursor: help`, abre modal. | ⬆️ nuevo |
| **Modales de error / éxito / progreso** | §12.1 / 12.1.1 / 12.1.2 | ✅ **Bien** | `002` `.progress-modal` (estructura propia, sin header/footer/botones, `runWithProgressModal`). `004` "Feedback surfaces" tabla completa (toast / progress / confirm / bulk modal / `showErrorModal` con `.modal__header--error` + icono rojo + `.modal__error-detail` mono / `.modal__header--success` verde / `.modal__error` inline / `.import-report-modal`). **Falta**: el `@keyframes progress-modal-spin` como "único del proyecto", el doble `requestAnimationFrame`. | ⬆️ mucho más |
| Cursores (tabla por contexto) | §12.2 | ⚠️ Disperso | `002`/`003` mencionan `cursor: grab`/`grabbing` (tabla, panel header), `cursor: move` (textbox/shape del editor), `cursor: help`, `cursor: not-allowed` (disabled). **Falta** la tabla consolidada y "3 cursores fijos en modo juego". | ⬆️ algo |
| **Etiqueta identificativa / título / tooltip / badges** | §12.3 (~1.500 pal.) | ✅ **Bien** | `003` "Overlaid piece badges" (tabla 4 badges) + "Contextual identifiers" (`.component-id-label` top-left `--accent-blue-dark` `0.72rem` solo en `:hover`/`--selected`, `.is-copy` → `--error`; `.component-title-label` play-only inline user-data; `.component-tooltip` reemplaza `title` nativo, `max-width 220px`). **Buena cobertura**, cercana al baseline. Falta: `.component-has-copies-badge` píldora con contador (sí mencionada), anclaje exacto, `sanitizeBasicTooltipHtml`. | ⬆️ **mucho más** (en `minimal` estaba casi ausente) |
| Modales anchas (tabla de clases con `max-width`) | §12.4 | ✅ **Bien** | `002` "Width variants": **tabla de 7 clases** con su regla de ancho (`.component-editor-modal` `clamp(...)`, `.card-editor-modal` `fit-content`, `--maximized` `97vw`, `.image-adjust-modal--large`, `.resource-modal--image`, `.element-selection-modal` 640px, `.import-report-modal`/`.board-image-modal`). Comparable al baseline. | ⬆️ nuevo |
| Botón maximizar/restaurar de modal | §12.4.1 | ⚠️ Mínimo | `002` menciona `.card-editor-modal--maximized` (`97vw`, unset `max-height`) y "maximize toggle". **Falta** el botón en sí (posición, iconos, sin persistencia). | ⬆️ algo |
| Checklist de selección agrupada (`.element-selection-group`) | §12.5 | ⚠️ Mínimo | `002` menciona `.element-selection-modal` (640px, "export/import checklist, 3 groups"). **Falta** el patrón (`__select-all`, `__list` con scroll a 12rem, `__item`). | ⬆️ algo |
| **Secciones dentro de pestañas** (`.modal__section` / fieldset) | §12.6 (~1.200 pal.) | ✅ Parcial | `002` "Modal structure": `.modal__section` = `<fieldset>` con borde `--border-neutral`, `<legend>` único usuario de `--section-accent` (uppercase), variante `--toggle` (legend con checkbox), `--disabled` (dim + `pointer-events:none`). Cubre el patrón base. **Falta**: `--untitled`, "zona con scroll interno", "número + botón que abre modal" (`.{bloque}-summary`), los ~8 usos catalogados. | ⬆️ **mucho más** (en `minimal` estaba ausente) |
| Menú desplegable de acciones (`.resource-add__menu` + reusos) | §12.7 | ✅ **Bien** | `002` "Menus": **lenguaje visual compartido** (`.resource-add__menu`, `.context-menu`, `.column-header-menu`, `.export-menu` dark) con bg/borde/hover exactos, `[motivación]` `position:fixed` en body por los `overflow` panels, `--item--active` mantiene accent. Comparable al baseline. | ⬆️ mucho más |
| Menú contextual (`.context-menu`, secciones, `<select>` inline, descripción) | §12.8 | ⚠️ Parcial | `002` cubre el aspecto y posicionamiento; `004` "arch" cubre las secciones lógicas (descripción / general / específica / interacción / select). **Falta** en estilo: `.context-menu__info-*`, `.context-menu__description-main/-extra`, `.context-menu__select-row`. | ⬆️ más |
| Copiar/Pegar estilo (patrón visual) | §12.9 | ❌ Ausente | Sin sección. `arch/001` lo menciona como módulo. | ≈ (ausente) |
| Grupo de botones icono-solo (`.align-group`) | §12.10 | ✅ Parcial | `003` "Option groups" fila `.align-group__btn` (32×32 icon-only, `.active` → accent bg). **Falta** la distinción "opción única vs. interruptores combinables". | ⬆️ nuevo |
| Título de cabecera editable (`.app-title--hoverable`/`--editing`) | §12.11 | ❌ **Ausente** en estilo | `style/005` da el texto (`DEFAULT_APP_TITLE`, `formatVersion`). **Falta** el patrón visual (icono lápiz en hover, sustitución por `<input>` a medida). | ≈ (ausente) |
| Slider con marcas imantadas (`.rotation-slider`) | §12.12 | ⚠️ Mínimo | `002` "Card / visual editor canvas": `.rotation-slider` `accent-color: var(--accent-blue)`, "tick marks magnetized every 90°". **Falta** `ROTATION_SNAP_THRESHOLD_DEG`, el bloque `.rotation-field`, la convivencia con "Girar 90°" del menú. | ⬆️ algo |
| Idioma (UI español, infra inglés) | (implícito baseline) | ✅ **Supera al baseline** | `005` "JS identifier language": **`[gotcha]` con la lista completa** de identificadores de dominio en español vs. infra en inglés, valores de enum en español, nombres de evento en inglés `namespace:verb`, convenciones de función (`createX`/`computeX`/`openXModal`/`renderX`/`nextX`). Tabla slug↔label de los 7 tipos. | ⬆️ más que `minimal`, más que baseline |
| Accesibilidad | (implícito baseline) | ✅ **Supera al baseline** | `004` "Accessibility — current state": **tabla de 7 aspectos** (Keyboard: sin focus trap, sin tab order; Focus: `outline:none` en inputs, botones con UA default; ARIA: solo `aria-label` en fit-button, `.modal-overlay` sin `role="dialog"`; **Contrast con ratios calculados** — `--text-light` sobre `--accent-blue` ≈ 3.4:1, `[gotcha]` bajo AA; Motion: sin `prefers-reduced-motion`; Color-only signalling: `[gotcha]` badges solo por color; Screen reader: sin live regions). "Facts, not compliance claims". El baseline no tiene esto. | ⬆️ más que `minimal`, **nuevo vs. baseline** |
| Microcopy (`confirm()`, "Próximamente", toasts) | (disperso baseline) | ✅ **Bien** | `005` "User-facing copy": español, tono `tú` imperativo, confirmaciones `¿...?` con target entre comillas, botones verb-first (lista), elipsis en acciones que abren modal, `Próximamente` + `--soon`, `showErrorModal(title, message, detail?)`. `005` "Numbers/units": `N caras`, `N cartas`, `{W}x{H}`, zoom en %. | ⬆️ más |
| Naming de versión (`v{NNNN}` / `v.{NNNN}`) | `INDEX.md` + `06` baseline | ✅ **Bien** | `005` + `arch/005` "Versioning": `CURRENT_VERSION = 'v{NNNNN}'` (`v00230`), `formatVersion()` → `v.{...}`, `{VERSION}` placeholder hard-error si falta. | ⬆️ más |

### 3.2 Lo que `full` hace bien (estilo)

1. **Tabla de "Feedback surfaces — which to use"** (`004`): 8 situaciones → superficie correcta. Es exactamente la guía "cuándo uso qué" que el baseline reparte por 5 secciones de `03-modales-menus.md`.
2. **Accesibilidad con ratios de contraste calculados** y `[gotcha]` sobre los que fallan AA. El baseline no lo tiene; `full` lo añade con rigor ("facts, not compliance claims").
3. **`[gotcha]` de `filter: drop-shadow` vs `box-shadow`** para siluetas no rectangulares, con las clases exactas — la trampa de CSS más recurrente del proyecto, bien capturada.
4. **Lenguaje visual de menús compartido** (`002`) con la `[motivación]` de `position:fixed` en body.
5. **Tabla de width variants de modal** (7 clases) — equivalente a la del baseline §12.4.
6. **Estados de interacción tabulados** (`004`): inputs, botones, filas, piezas de juego, cada uno con su `[hover]`/`[focus]`/`[selected]`/`[disabled]` y valores. Y el `[gotcha]` "dashed = selección, solid = otra cosa".
7. **`[gotcha]` de rutas `design/docs/**` obsoletas** (`005`) — igual que en arquitectura, dato correcto que el baseline asume implícito.
8. **Namespace `ui.*`** poblado (`ui.palette`, `ui.radius`, `ui.shadow`, `ui.zindex.ladder`, `ui.naming`, `ui.selection.outline`, `ui.piece.shadow.non-rect`).

### 3.3 Carencias que persisten (estilo)

1. **La extrusión configurable (`profundidad`/`colorExtrusion`) sigue casi ausente.** Aparece como campo en `arch/003` ("3D extrusion thickness") pero **no hay ninguna explicación del mecanismo visual** (capas sólidas apiladas, `buildExtrusionLayers`, tope 40, sin efecto en `'texto'`, cómo convive con la sombra de contacto). El baseline le dedica media sección de `01-tokens-visual.md` §6.
2. **El catálogo de patrones de modal/menú sigue incompleto vs. baseline.** `full` cubre bien ~10 de los ~20 patrones de `03-modales-menus.md`. Faltan o quedan mínimos: copiar/pegar estilo (`.style-actions-row`), título editable in-place (`.app-title--*`), slider imantado (`.rotation-field` completo), botón maximizar (el botón, no el estado), checklist agrupado (el patrón, no la clase), `.modal__section` variantes `--untitled` / scroll interno / "número + botón".
3. **La sección "Qué NO hacer" / excepciones catalogadas** (`INDEX.md` §13 del baseline) no está como bloque. Partes sueltas sí (drop-shadow, `.lifted`, `.drop-target`, `--section-accent` único), pero no el bisel de dos tonos de `tableroSimple`/`tableroPersonalizado`/`dado` (`shadeColor`), ni el recorte hex/triángulo con doble `clip-path` anidado, ni "parpadeo/temblor del dado NO son animación CSS".
4. **Cursores**: sin tabla consolidada.
5. **Espaciado**: `full` documenta que **no hay escala** — correcto como hallazgo, pero si se quisiera imponer una, el baseline la tiene y `full` no la propone.

---

## 4. Diagnóstico transversal

### 4.1 Qué mejora `full` respecto a `minimal`

| Eje | `minimal` | `full` |
|---|---|---|
| Volumen arquitectura (palabras) | ~12 % del baseline | **~23 %** |
| Volumen estilo (palabras) | ~18 % del baseline | **~43 %** |
| Conceptos del baseline cubiertos | ~40–50 % | **~75–85 %** |
| Contratos de API | nombrados | **tabulados con firma** (event bus, mutadores, modal contract) |
| Comportamiento por modo | colapsado | **tabla input→efecto por modo** |
| Seguridad | ausente | **sección dedicada + modelo de amenazas + huecos del sanitizador** |
| Decisiones de diseño | ausente | **11 decisiones con racional** |
| Badges / identificadores de pieza (estilo) | casi ausente | **tabla completa 4 badges + contextual identifiers** |
| `.modal__section` (estilo) | ausente | **patrón base + 3 variantes** |
| Accesibilidad (estilo) | resumen honesto | **tabla 7 aspectos + ratios de contraste calculados** |
| Feedback surfaces (estilo) | tabla de 5 | **tabla de 8 "cuándo uso qué"** |
| Migración al cargar | 1 fila | **8 pasos ordenados + contrato + motivación** |

### 4.2 Qué NO mejora (heredado de `minimal`)

- **Catálogo de los 8 tipos**: sigue comprimido a ~1 tabla sin rangos/defaults/render.
- **Checklist "qué revisar al añadir un tipo"**: sigue ausente.
- **Contratos completos de la capa UI** (`renderComponentsOnTable` opts, `resizeHandle`, `imageAdjustModal`…): siguen sin enumerarse.
- **Extrusión configurable en estilo**: sigue casi ausente.
- **~10 patrones de `03-modales-menus.md`**: siguen mínimos o ausentes.
- **Sección "Qué NO hacer" / excepciones de CSS** como bloque: sigue disgregada.

### 4.3 Precisión

**No se han detectado afirmaciones incorrectas** en el nivel `full`. Como `minimal`, es conservador y fiable, y marca su alcance (`~924 lines`, `~283 lines`, `roughly ordered`). Los valores concretos que añade (extensiones, q=0.92, `v00230`, `MAZO_REVEAL_GAP = 20`, ratios de contraste) son verificables y coherentes con el baseline.

**Discrepancia de z-index (persiste desde `minimal`, con valores propios).** Las tres documentaciones difieren:

| Capa | Baseline (`02-componentes-layout.md`) | `minimal` (`style/001`) | **`full`** (`style/001`) |
|---|---|---|---|
| `.modal-overlay` | `1000` | `1200` | **`1000`** |
| `.context-menu` / `.column-header-menu` | `1050` | `1000` | **`1050`** |
| `.toast` | (no listado) | `1100` (como "toast") | **`1100`** |
| `.export-menu` | (no listado) | — | **`1200` (highest)`** |
| `#app-version` / `.component-tooltip` | `10` (footer) | — | **`10`** |
| toolbar / header / mode-switcher | `99` / `100` / `1050`(menú) | `99` / `100` / `101` | **`99` / `100–101`** |

**`full` coincide con el baseline** en modal (`1000`) y context-menu (`1050`), donde `minimal` discrepaba — y añade `.toast` (1100) y `.export-menu` (1200) que ninguno de los otros dos tenía. Esto sugiere que **`full` leyó el ladder del CSS con más cuidado**. Conviene confirmar en `src/styles/main.css` que el ladder real es `panels 15+ / toolbar 99 / header 100-101 / modal 1000 / menús 1050 / toast 1100 / export-menu 1200`; si es así, **`full` es la fuente más fiable de las tres** para z-index.

- Confirmar también que las rutas `design/docs/**` de los comentarios del CSS están efectivamente obsoletas (los tres docs lo afirman; encaja con que el baseline vive en `previo-sdd/docs/`).

### 4.4 Organización

`full` mantiene las ventajas de formato de `minimal` (namespace único, notación compacta, anclas al código, `[gotcha]`/`[motivación]` como etiquetas) y **añade estructura temática mejor calibrada**: arquitectura en 5 documentos con separación limpia (overview / estado+eventos / modelo de datos / interacción / build+seguridad), estilo en 5 (tokens / layout / componentes / interacción+a11y / escritura). Cada documento abre con `**Area**:` y un propósito. Es **más navegable que el baseline** (que tiene arquitectura en 6 ficheros con solapamiento y 2 versiones alternativas de `06-persistence-build`).

---

## 5. Conclusiones y recomendaciones

### 5.1 Sobre el nivel `full` como tal

**Es utilizable como documentación técnica de referencia autónoma.** A diferencia de `minimal` (buen mapa de arranque, insuficiente como doc única), el nivel `full` cubre lo bastante — y con contratos, tablas de comportamiento, seguridad y decisiones — como para que un desarrollador nuevo se oriente y decida con ella, recurriendo al código solo para el detalle fino de un tipo de componente concreto.

**No iguala al baseline en profundidad de dominio** — pero la brecha es de **detalle**, no de temas ausentes. En **volumen de prosa** es ~23 % (arquitectura) / ~43 % (estilo); en **conceptos cubiertos**, ~75–85 %. Lo que falta es sobre todo profundidad en cuatro puntos concretos: el catálogo exhaustivo de los 8 tipos (rangos, defaults por campo, reglas de render), el catálogo completo de patrones visuales de modal/menú, el checklist de mantenimiento, y las excepciones de CSS catalogadas.

**Aporta lo que el baseline no tiene**: tabla de decisiones con racional, sección de seguridad con modelo de amenazas y huecos del sanitizador, accesibilidad con ratios calculados, mapa de módulos con pureza, y un z-index ladder que parece más fiel al código actual que el del propio baseline.

### 5.2 Prioridades si se quiere cerrar la brecha con el baseline

Por orden de retorno:

1. **Expandir el catálogo de los 8 tipos**: por cada tipo, tabla de `properties` con default, rango y regla de redimensionado/render. Es la mayor carencia (impacto alto, y el generador tiene la info en las validaciones + `DEFAULT_*_PROPERTIES`).
2. **Checklist "qué revisar al añadir un tipo/colección"** (§8 baseline) — regenerable si el generador detecta "listas fijas de campos serializados/renderizados en varios sitios".
3. **Enumerar las `opts` de `renderComponentsOnTable`** y las firmas de `attachResizeHandle` / `openImageAdjustModal` / `openVisualEditorModal` / `openContextMenu`.
4. **Documentar la extrusión configurable en estilo** (mecanismo de capas, `buildExtrusionLayers`, tope 40, sin efecto en `'texto'`).
5. **Completar los ~10 patrones de modal/menú restantes** (copiar/pegar estilo, título editable in-place, slider imantado completo, botón maximizar, checklist agrupado, `.modal__section` variantes).
6. **Sección "Qué NO hacer" / excepciones de CSS** como bloque único (bisel de dos tonos, recorte hex/triángulo con doble clip-path, dado no-animación-CSS, `--section-accent` único…).
7. **Interacción de grupos en el panel de Componentes** (filas sintéticas, anidación `--member`, orden de bloque, acciones deshabilitadas).

### 5.3 Verificación pendiente

- **z-index**: confirmar en `src/styles/main.css` el ladder real. `full` parece el más fiable de los tres documentos; si se confirma, actualizar el baseline (y `minimal`).
- Confirmar que la lista de huecos del sanitizador denylist (`<iframe>`/`<object>`/`<embed>`, `style`, `srcdoc`, `data:`, `formaction`, SVG script) y el `<iframe>` sin `sandbox` del `documento` siguen vigentes en 0.9.6b9 — es el hallazgo de seguridad más accionable del informe.
- Confirmar que las rutas `design/docs/**` de los comentarios del código están obsoletas.
