# Comparativa de documentación técnica — `_baseline` vs `0.9.6b7/minimal`

**Fecha:** 2026-08-28
**Proyecto de prueba:** BG Factory (prototipo digital de juegos de mesa, HTML autocontenido, vanilla JS + CSS plano)
**Qué se compara:**

- `test-data/bgfactory-docs/_baseline/architecture` + `/style` — documentación **completa**, redactada durante la creación real del proyecto (equivale al modo `full` de `pv-init`, enriquecida además por sucesivos `pv-do`).
- `test-data/bgfactory-docs/0.9.6b7/minimal/architecture` + `/style` — documentación generada por `pv-init` en **modo minimal** (paso 5.5), partiendo *solo del mismo código fuente*, sin intervención manual.

---

## 1. Resumen cuantitativo

| Bloque | Baseline (líneas) | Minimal (líneas) | Ratio |
|---|---|---|---|
| architecture (sin variantes `_v2/_v3`) | ~ 761 (INDEX + 01–06) | 291 (INDEX + 00-namespace + 001 + 002) | ≈ 0,38× |
| style | 694 (INDEX + 01–03) | 185 (INDEX + 001 + 002 + 003) | ≈ 0,27× |
| **Total comparable** | **≈ 1.455** | **476** | **≈ 0,33×** |

| | Baseline | Minimal |
|---|---|---|
| Ficheros architecture | 6 temáticos + INDEX (+ 2 variantes de trabajo de `06`) | 3: `00-namespace`, `001-overview`, `002-file-map` + INDEX |
| Ficheros style | 3 temáticos + INDEX | 3: `001-overview`, `002-design-tokens`, `003-modals-menus` + INDEX |
| Idioma | Español (prosa) + identificadores en español | Inglés técnico + identificadores de dominio en español |
| Namespace tree | No existe como artefacto propio | Sí — `00-namespace.md` con árbol canónico sembrado |
| Nivel de detalle | Campo a campo, rama a rama, con `[gotcha]`/`[motivación]` abundantes | Responsabilidad general por fichero + decisiones e invariantes clave |

---

## 2. Arquitectura — qué conserva y qué pierde el minimal

### 2.1 Lo que el minimal SÍ captura bien

- **Decisiones arquitectónicas de primer orden**, todas presentes:
  - Entregable = HTML único autocontenido, sin servidor, sin Node, build en Python.
  - Arquitectura por capas `core → ui → modes`, con la regla dura "`core` no importa de `ui`/`modes`" y la lista de módulos `core` puros sin imports (`deck`, `dice`, `tag`, `colorUtils`, `cardProportions`, `textBoxLayout`, `cardFaceElements`).
  - Modelo runtime: store singleton + eventBus + `renderAll()` completo sin diffing + autosave síncrono en cada cambio.
  - Contrato de persistencia: `STORAGE_KEY`, shape guardado, *load guard* (`version` + `Array.isArray(components)`), fallback a semilla embebida, aliasing de claves `tags ?? groups ?? decks`, `deriveMissingGroups()`, migración silenciosa `ficha → carta`.
  - Invariante de seguridad XSS: todo HTML de usuario pasa por `sanitizeHtml`, y la salida de `marked.js` también (no autosanea).
  - Pipeline de build en 5 pasos.
- **`[gotcha]` verdaderamente críticos**, que sobreviven al recorte:
  - Hidratar `resourcesSeeded` *antes* de `loadComponents/loadResources` para que el primer autosave no persista `false` y resiembre en cada recarga.
  - Los módulos ES no cargan por `file://`; dev necesita servidor estático.
- **`00-namespace.md`**: un artefacto que el baseline **no tiene**. Aporta un árbol de nombres canónico (`state.store.*`, `persist.*`, `component.model.*`, `security.sanitize.*`, `ui.*`) con anclas a símbolos de código y una notación formal para invariantes (`assert` vs `inv:` declarativo). Es la base sobre la que `pv-do` irá colgando aserciones nuevas.
- **`002-file-map.md`**: una fila por fichero de `src/` con su responsabilidad general. Es un índice de navegación que el baseline solo ofrece de forma dispersa (dentro de `05-ui-layer.md` y de los checklists).

### 2.2 Lo que el minimal PIERDE respecto al baseline

Todo lo que en el baseline es "conocimiento de contrato a nivel de campo":

| Área | En baseline | En minimal |
|---|---|---|
| **Modelo de componente** | Tabla de ~30 campos: tipo, default, para qué sirve, quién lo edita, más notas de migración silenciosa campo a campo (`migrateBloqueado`, `migrateAccionClickDerecho`, `normalizeComponentEtiquetaIds`…) | Una frase: "`createComponent(...)` (id, `type` libre, `properties` k/v, posición/tamaño, campos lock/tooltip/title/depth, `copyOf`/`sincronizado`, `groupId`, `etiquetaIds`)" |
| **Lógica de `order`** | 5 funciones descritas (`addComponent`, `removeComponent`/`compactOrders`, `reorderComponent`, `loadComponents`, `reorderGroupBlock`) con su semántica de compactado y clamp | "Owns `order` (z-index) compaction" |
| **Copias vinculadas (`copyOf`)** | ~15 líneas: id `-COPY-XXX`, `syncCopyWithOriginal`, lista exacta de campos siempre propagados / condicionados por `sincronizado` / siempre independientes (`NON_SYNCED_PROPERTY_KEYS`), borrado en cascada, modal reducida | "copy-sync propagation on `replaceComponent`" + regla en namespace |
| **8 tipos de componente** | Fichero entero (`02-component-types.md`, 206 líneas): propiedades específicas por tipo, defaults, shapes anidados (`Forma`, `TextBox`, `caraFrontal/trasera`), reglas de redimensionado, migraciones de datos | Enumeración de los 7 nombres de tipo como "type-specific tab content" en `componentModal.js`. **Sin una sola propiedad específica.** |
| **Modos juego/edición** | Fichero entero (`04-modes.md`, 139 líneas): selección múltiple con Ctrl, grupos (selección atómica, propiedades efectivas `getEffectiveGeneralProps`, disolución automática, tabla de habilitación de "Agrupar"/"Desagrupar"), indicadores visuales, z-index de paneles flotantes, título editable | Dos filas en `002-file-map.md` con la responsabilidad general de `editMode.js` y `playMode.js` |
| **Capa UI** | Fichero entero (`05-ui-layer.md`, 75 líneas densas): contrato de cada widget reutilizable (`resizeHandle`, `rotationSlider`, `componentRenderer.renderComponentsOnTable` con todos sus parámetros, `contextMenu.openContextMenu`, cada `*Modal.js`) | Tabla resumida en `002-file-map.md`; los ~30 `*Modal.js` colapsados en **una sola fila** ("One modal each, per a specific edit/play action") |
| **Import/merge con selección** | ~30 líneas de flujo paso a paso (`mergeImportedGame`, modos `add`/`overwrite`, `conflictMode`, `nextImportedId`, reparación post-merge, informe) | "Merge an imported selection ... per mode (add/overwrite) and duplicate-id behaviour (overwrite/keep-both)" |
| **Recursos por defecto / backfill** | Invariantes formales + número concreto (baseline `_v2/_v3` hablan de 38 recursos), condición exacta de resiembra | "`DEFAULT_RESOURCES` — sample gallery resources seeded on first run" |
| **Sistema de variables de texto** | Descripción de `getAvailableVariables`/`resolveTextVariables`, comportamiento ante variable no definida ("literal, sin sustituir, nunca cadena vacía") | Una fila: "Runtime `{name}` substitution ... Designed to extend by adding variables only" |
| **Checklist "al añadir un tipo/colección nuevo"** | Sección entera de `INDEX.md`: 10 puntos transversales (persistencia, detección de uso de recurso, alta de tipo, renderizado, `getComponentsBounds`, guía de estilo, menú contextual, ficheros de prueba…) | **No existe.** |

**Diferencia clave:** el minimal describe *qué hace cada fichero*; el baseline describe *cómo se comporta el sistema*, incluyendo todos los invariantes, defaults, migraciones y trampas que no se deducen leyendo una firma de función.

---

## 3. Style bible — qué conserva y qué pierde el minimal

### 3.1 Lo que el minimal SÍ captura bien

- **El set completo de design tokens** (`002-design-tokens.md`): todos los colores de `:root` con valor y uso, radios, sombras, transición. Prácticamente equivalente al baseline `01-tokens-visual.md` §2, incluso conserva el `[gotcha]` de `--section-accent` (violeta-gris deliberadamente ≠ `--accent-blue` porque el azul significa "interactivo/seleccionado").
- Añade tokens que el baseline no listaba explícitamente (`--bg-table-dot`).
- **Convenciones de nomenclatura**: BEM, la excepción histórica de los 4 botones de footer (`.btn-cancel`/`.btn-duplicate`/`.btn-accept`/`.btn-eliminar` como clases standalone que `globalShortcuts.js` matchea literalmente), idioma de identificadores de dominio en español.
- **Patrón de modal estándar** (`003-modals-menus.md`): estructura DOM `.modal-overlay > .modal > .modal__header/__tabs/__footer`, overrides de anchura, tabla de variantes de botón con base/texto/estados, equivalencias de teclado (`ESC`/`ENTER`/`DEL`/flechas), `fieldset.modal__section` con sus modificadores, context menu, toast, progress modal (spinner 40px, `@keyframes progress-modal-spin`).
- Marca honestamente lo que **no** está tokenizado: sin escala tipográfica, sin escala de espaciado, `transform: translateY(-1px)` de hover ad-hoc — con la instrucción de "si un cambio necesita escala compartida, crea tokens y documéntalos aquí".

### 3.2 Lo que el minimal PIERDE respecto al baseline

| Área | En baseline | En minimal |
|---|---|---|
| **Sistema de elevación** | 3 niveles descritos con qué elemento va en cada uno, más los casos especiales (`.dice` usa `filter: drop-shadow`, `.carta--hex`, `.text-box` usa `text-shadow`), extrusión configurable (`profundidad`/`colorExtrusion`) como concepto ortogonal | Solo la tabla de tokens `--shadow-1`/`--shadow-2` con un uso de una línea |
| **Botones** | `02-componentes-layout.md` §9: CSS base completo, acción primaria/secundaria/destructiva/sobre-fondo-oscuro/deshabilitado, botón icono-solo, botón de texto en espacio reducido | Tabla de 3 variantes de footer en `003` |
| **Layout** | Columna flex de altura completa, paneles de ancho fijo, **tabla completa de z-index de overlays** (`10`/`99`/`100`/`101`/`1000`/`1050`), cabecera de tabla `position: sticky`, fila anidada `--member` | Solo `z-index 1000` del overlay de modal y `1050` mencionado de pasada; nada de `sticky` ni anidación |
| **Redimensionado** | §11: patrón `.resize-handle` completo, segundo manejador `--tl`, variante `.column-resize-handle` | Solo "panel resize, column resize" como primitiva reutilizable en `file-map` |
| **`03-modales-menus.md` (322 líneas)** | 20+ subsecciones: icono de ayuda, modal de error/éxito/operación-en-curso, cursores (tabla), etiqueta identificativa de componente + 4 insignias (candado/oculto/copia/tiene-copias) con anclaje por esquina, modales anchas (tabla de 7 clases), botón maximizar, checklist agrupado, secciones dentro de pestañas con todos sus usos catalogados, menú desplegable de acciones, menú contextual (5 secciones), copiar/pegar estilo, grupo de botones icono-solo, título de cabecera editable, slider con marcas imantadas | `003-modals-menus.md` (84 líneas): modal pattern, footer buttons, teclado, fieldset sections (3 líneas), context menu (3 líneas), toast (2 líneas), progress modal (3 líneas) |
| **Reglas "qué NO hacer"** | `INDEX.md` §13: no segundo sistema de tokens, no degradados llamativos, no animaciones complejas, y ~15 excepciones catalogadas una a una (bisel de tablero/dado, esquinas de carta, recorte hexagonal/triangular con doble `clip-path`, feedback de volteo, efecto "levantar", resaltado de zona de suelta…) | **No existe** ninguna de estas excepciones |
| **Cursores** | Tabla de 6 cursores + reglas de modo juego | No documentado |

**Diferencia clave:** el baseline de style es un catálogo exhaustivo de patrones visuales y de sus excepciones justificadas —el tipo de conocimiento que evita que dos desarrolladores resuelvan el mismo problema visual de forma distinta—. El minimal cubre el "esqueleto" (tokens + modal + un puñado de patrones) y deja fuera todo el catálogo de componentes visuales concretos y sus reglas.

---

## 4. Valoración de la utilidad de la versión minimal

### 4.1 Para qué SÍ sirve el minimal

1. **Arranque inmediato y barato.** Un tercio del volumen, generado sin coste de redacción manual. Para un proyecto nuevo o para uno donde nadie ha documentado nada, pasar de cero a estos 476 líneas es una mejora enorme por el precio.
2. **Onboarding y orientación.** `001-overview.md` + `002-file-map.md` responden bien a "¿qué es esto, cómo está montado, dónde toco X?". Un desarrollador nuevo sabe en 5 minutos que `core` no puede importar de `ui`, que el render es full-rebuild, que la persistencia tiene un load guard por versión, y en qué fichero vive cada cosa.
3. **Captura fiable de lo que de verdad importa no romper.** Las decisiones estructurales y los invariantes de seguridad/persistencia están todos. Los 2–3 `[gotcha]` que sí sobreviven (orden de hidratación de `resourcesSeeded`, `file://`, sanitize de `marked`) son precisamente los que más caro cuesta descubrir por las malas.
4. **`00-namespace.md` como cimiento incremental.** Es el mayor valor añadido neto del minimal frente al baseline: un árbol de nombres canónico con notación formal para invariantes, pensado para que `pv-do` cuelgue aserciones nuevas de forma ordenada en cada cambio. El baseline, más rico en prosa, carece de esta columna vertebral y por eso acumula variantes de trabajo sin consolidar (`06-persistence-build_v2.md`, `_v3.md`).
5. **Base honesta.** El minimal marca explícitamente lo que no está resuelto ("No spacing-scale tokens", "Expanded by pv-do over time") en vez de fingir cobertura.

### 4.2 Dónde el minimal se queda corto

1. **No sirve como contrato de API interna.** Para implementar un cambio que toque `renderComponentsOnTable`, `mergeImportedGame`, el shape de una `Forma` de carta o la sincronización de copias, el minimal no aporta lo necesario: hay que ir al código igualmente. El baseline te ahorra esa lectura casi siempre.
2. **Los 8 tipos de componente quedan como caja negra.** Es el núcleo funcional del producto (cartas, mazos, dados, tableros) y el minimal no documenta ni una propiedad específica, ni un default, ni una regla de redimensionado, ni una migración de datos. Aquí la pérdida es máxima.
3. **El style bible minimal no previene divergencia visual.** Sin el catálogo de insignias, cursores, modales anchas, secciones, menús y —sobre todo— sin la lista de excepciones justificadas de `INDEX.md §13`, un desarrollador nuevo reinventará patrones o introducirá el "segundo sistema de tokens" que el baseline prohíbe expresamente.
4. **Desaparecen los checklists transversales.** "Qué revisar al añadir un tipo/colección nuevo" (10 puntos) es puro conocimiento operativo que no está en ninguna firma de función y que el minimal no reconstruye.
5. **Riesgo de falsa sensación de cobertura.** `002-file-map.md` colapsa ~30 modales en una fila. Alguien puede creer que "está documentado" cuando en realidad solo está listado.

### 4.3 Conclusión

La versión **minimal cumple exactamente lo que promete `pv-init`**: "menos precisa al principio, se rellena y mejora automáticamente con cada `pv-do`". Como **punto de partida** es claramente útil y rentable —cubre decisiones, capas, contrato de persistencia, invariantes de seguridad y un mapa de ficheros navegable, más un `namespace` que el propio baseline no tiene—.

Como **documentación de referencia madura** no compite con el baseline: este proyecto, con 8 tipos de componente ricos, un editor visual, un sistema de grupos/copias/etiquetas y un style bible de 20+ patrones, es justo el caso donde el modo `full` (o el minimal ya engordado por muchos `pv-do`) rinde de forma muy superior. El minimal deja fuera todo el conocimiento a nivel de campo, de contrato de widget y de excepción de estilo, que es precisamente lo que hace que documentar valga la pena frente a leer el código.

**Recomendación de uso:** minimal como default para proyectos nuevos, pequeños o en fase temprana, y como red de seguridad para proyectos sin ninguna documentación; `full` cuando el proyecto ya tiene superficie funcional grande y estable —como BG Factory— y se espera que varias personas trabajen sobre él. En ambos casos, el valor real del minimal depende de que `pv-do` se use con disciplina después: sin ese engorde incremental, se queda en un buen overview y poco más.

---

## Anexo — Correspondencia de ficheros

| Baseline | Minimal equivalente | Cobertura |
|---|---|---|
| `architecture/INDEX.md` (objetivo, capas, convenciones de código, checklist) | `architecture/INDEX.md` (tabla) + `001-overview.md` | Parcial — falta convenciones de comentarios y checklist |
| `architecture/01-component-model.md` | fila de `002-file-map.md` + nodos `component.model.*` de `00-namespace.md` | Mínima |
| `architecture/02-component-types.md` | — (solo nombres de tipo) | Nula |
| `architecture/03-groups-resources.md` | filas de `002-file-map.md` (`group.js`, `tag.js`, `resource.js`) + `component.group.*` del namespace | Mínima |
| `architecture/04-modes.md` | 2 filas de `002-file-map.md` | Mínima |
| `architecture/05-ui-layer.md` | tabla `src/ui/` de `002-file-map.md` | Baja (nombres + responsabilidad de una línea) |
| `architecture/06-persistence-build.md` (+ `_v2`, `_v3`) | `001-overview.md` (secciones Persistence contract + Build) + `persist.*` del namespace | Media-alta — decisiones e invariantes sí, detalle de `mergeImportedGame` no |
| — | `architecture/00-namespace.md` | **Añadido neto del minimal** |
| `style/INDEX.md` (stack, BEM, patrones de componente JS, §13 qué NO hacer) | `style/001-overview.md` | Parcial — sin §13, sin patrones de componente JS |
| `style/01-tokens-visual.md` | `style/002-design-tokens.md` | **Alta** — casi equivalente |
| `style/02-componentes-layout.md` (botones, layout, z-index, resize, sticky) | disperso en `003` (footer buttons) + `file-map` | Baja |
| `style/03-modales-menus.md` (322 líneas, 20+ patrones) | `style/003-modals-menus.md` (84 líneas, ~7 patrones) | Media para el patrón de modal; baja para el resto |
