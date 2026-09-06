# Flujo de desarrollo/build y persistencia

## Desarrollo y build

- **Desarrollo**: se abre `src/index.html` (no es el entregable) con un servidor estático local (p. ej. extensión "Live Server" de VSCode) — los módulos ES nativos (`<script type="module">`) no cargan correctamente vía `file://`. Este fichero referencia los módulos de `/src` directamente.
- **Build**: `src/scripts/build.py` recorre el grafo de `import`/`export` a partir de `src/main.js`, transforma cada módulo a un pequeño sistema `require`/`module.exports` en runtime (sin bundlers ni Node.js, solo Python), inserta el resultado junto con el CSS de `src/styles/main.css` dentro de una copia de `src/index.html`. Resultado: fichero único autocontenido escrito en `src/_output/versions/index-v{NNNN}.html` (`NNNN` = `CURRENT_VERSION` de `src/data/version.js`) — el entregable portable.

## Persistencia y guardado a fichero

`src/index.html` incluye `<script type="application/json" id="initial-state"></script>` vacío que sobrevive al build (se copia tal cual) y a la descarga en runtime (se rellena antes de descargar) — semilla de estado embebida en cada copia del HTML.

```
Arranque (main.js):
  loadState() [core/persistence.js, localStorage]
    → válido        → loadComponents(...) + loadResources(...) + backfillDefaultResourcesIfNeeded(...)
    → corrupto/incompatible → showToast(aviso) + componente de ejemplo + recursos por defecto
    → nada guardado  → readSeedState() [<script id="initial-state">]
                          → hay semilla → loadComponents(...) + loadResources(...) + backfillDefaultResourcesIfNeeded(...)
                          → sin semilla → componente de ejemplo + recursos por defecto
```

### Autoguardado (`core/persistence.js`)

- Suscrito a `components:changed`, `panelState:changed`, `resources:changed`, `resourcePanelState:changed`, `tags:changed`, `tagPanelState:changed`, `appTitle:changed` (`core/eventBus.js`) desde `main.js`.
- Serializa `{ version: CURRENT_VERSION, components, panelState, resources, resourcePanelState, resourcesSeeded, tags, tagPanelState, appTitle }` a `localStorage` ante cualquiera de esos cambios.
- Guardado sin `appTitle`, o con valor vacío/no-string, se trata como `core/appTitle.js` → `DEFAULT_APP_TITLE`.
- `tags:changed` dispara además repintado completo (`renderAll`), no solo autoguardado.
- Un único slot por navegador/perfil (`localStorage` no se aísla por fichero bajo `file://`), sin conservación entre navegadores/dispositivos.
- Al arrancar, con guardado válido en `localStorage` que trae `panelState`/`resourcePanelState`/`tagPanelState`, se hidratan con `loadPanelState()`/`loadResourcePanelState()`/`loadTagPanelState()` antes del primer render; si no los hay, cada panel usa sus valores por defecto (expandido, posición/ancho/alto por defecto).
- `resources` y `tags`: si faltan o no son array en el guardado/semilla, se asume `[]` en vez de invalidar todo el estado (`resources` además dispara backfill de recursos por defecto; `tags` no necesita backfill).
- Selección de fila (`selectedComponentIds`) no forma parte de ningún `panelState`, nunca se persiste.
- "Guardar a fichero" (`core/fileExport.js`) incluye los siete campos: `components`, `panelState`, `resources`, `resourcePanelState`, `resourcesSeeded`, `tags`, `tagPanelState`.
- **Compatibilidad hacia atrás**: `parseState`/`parseImportedComponents` leen `tags`/`tagPanelState`, con fallback encadenado a `groups`/`groupPanelState` y luego a las claves más antiguas `decks`/`deckPanelState` si las anteriores no están presentes.

### Guardar a fichero (`core/fileExport.js`, botón "Guardar" en `ui/editModeToggle.js`)

- `buildExportHtml(components, resources, panelState, resourcePanelState, resourcesSeeded, tags, tagPanelState, appTitle)` clona `document.documentElement` (CSS/JS ya embebidos por el build), sustituye el contenido de `#initial-state` por el estado actual, `downloadHtml()` lo descarga como `Blob`.
- Botón pide nombre de fichero, precargado con el título completo de cabecera (`getFullAppTitle(getAppTitle())` + `.html`).
- El navegador decide, según su configuración, si sustituye o no un fichero anterior con el mismo nombre.

### Exportar/Importar con selección (`core/importMerge.js` + `ui/exportSelectionModal.js`/`ui/importSelectionModal.js`/`ui/importConfirmModal.js`/`ui/importReportModal.js` en `ui/editModeToggle.js`)

A diferencia de "Guardar" (app completa), "Exportar"/"Importar" trabajan con el JSON ligero de `core/persistence.js` (`buildComponentsExport`/`parseImportedComponents`: `{ version, components, resources, tags }`, sin `appTitle` — selección parcial, no "la partida completa"), permitiendo elegir un subconjunto.

- **Exportar**: `openExportSelectionModal` sustituye al `prompt()` de nombre de fichero por modal con ese campo (precargado con el mismo título completo + `.json` que usa "Guardar" con `.html`) más los tres bloques de selección (`ui/elementSelectionModal.js`); al confirmar, `ui/editModeToggle.js` filtra `getComponents()`/`getResources()`/`getTags()` por los ids marcados antes de llamar a `buildComponentsExport`/`downloadJson` (firma de esas funciones sin cambios — reciben listas ya filtradas). Sin validación de referencias huérfanas en la selección exportada.
- **Importar**: tras `parseImportedComponents`, `openImportSelectionModal` muestra los elementos del fichero para elegir cuáles importar; al confirmar, `openImportConfirmModal` pide modo (`add`/`overwrite`) y comportamiento ante id duplicado (`overwrite`/`keepBoth`). Antes de `mergeImportedGame` (ver `03-groups-resources.md`), `ui/editModeToggle.js` pasa cada componente seleccionado de tipo `'ficha'` por `migrateFichaComponent`; si alguno devuelve errores, se abre `openImportConversionErrorModal` con la lista antes de tocar el estado — "Abortar importación" no llama a `mergeImportedGame` ni a `loadComponents`/`loadResources`/`loadTags` (partida actual intacta); "Continuar sin esas fichas" sigue el flujo excluyéndolas del `selectedComponents`. Con las fichas ya migradas (o sin ninguna que migrar), `core/importMerge.js` (`mergeImportedGame`) calcula el estado final:
  - `overwrite` (modo): parte de listas vacías, inserta directamente lo seleccionado (sin conflicto posible).
  - `add` (modo): fusiona lo seleccionado con lo existente por tipo (componentes/recursos/etiquetas, cada uno con su propio espacio de ids); ante id ya existente, `conflictMode: 'overwrite'` reemplaza el elemento existente, `conflictMode: 'keepBoth'` renombra el importado con sufijo `-imported`/`-imported(n)` (`nextImportedId`, análogo a `nextCloneId` pero genérico por tipo) — referencias de componentes importados a un recurso/etiqueta renombrado se reescriben al nuevo id antes de fusionar (`etiquetaIds` es propiedad plana de primer nivel del componente, igual que `image`, no una clave dentro de `properties`); componentes ya existentes no se tocan.
  - Tras la fusión: referencia de un componente recién importado a recurso ausente del estado final se descarta (campo a `null`, tolerado igual que recurso borrado en uso); cada id ausente de `etiquetaIds` (puede haber varios por componente) se procesa por separado — se autocrea una etiqueta con ese id (una sola vez por id aunque varios componentes lo referencien), o se vincula a la etiqueta existente con el mismo nombre si la hay. Cada caso genera fila de informe (`{ componentId, tipoError, solucion, elemento }`); si hay alguna, `ui/editModeToggle.js` abre `openImportReportModal(report)` al terminar.
  - Funciones previas `getComponentsWithMissingResources` (`core/resource.js`) y `getComponentsWithMissingDeck` (`core/deck.js`) del flujo de importación anterior (todo-o-nada con `confirm()`) se han eliminado por quedar sin uso — el informe de `mergeImportedGame` las sustituye con más detalle.

### Recursos por defecto y backfill (`data/defaultResources.js`, `main.js`)

- Sesión totalmente nueva (nada guardado, sin semilla embebida, o guardado corrupto/incompatible): se siembran los 38 recursos de `DEFAULT_RESOURCES` (`seedDefaultResources()`) — 3 imágenes de fondo de localización + 35 imágenes de mochila/objetos/eventos, embebidas como data URI con id fijo (nombre de fichero) en vez de UUID — y se marca `resourcesSeeded = true` (`markResourcesSeeded()`).
- Guardado o semilla válidos (con componentes existentes) pero `resourcesSeeded` no es `true` (típicamente guardado anterior a esta funcionalidad, `resources` vacío o inexistente): `backfillDefaultResourcesIfNeeded()` los siembra igualmente esa vez, y a partir de ahí quedan como recursos normales — si el usuario los borra, no reaparecen en cargas posteriores (backfill no se repite una vez `resourcesSeeded` es `true`).
