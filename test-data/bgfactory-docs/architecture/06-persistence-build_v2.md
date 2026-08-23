# Flujo de desarrollo/build y persistencia

## Desarrollo y build

- Desarrollo: `src/index.html` requiere servidor estático local (p. ej. extensión "Live Server" de VSCode). `<script type="module">` no carga vía `file://`. `src/index.html` no es el entregable. `src/index.html` referencia los módulos de `/src` directamente.
- Build: `src/scripts/build.py` recorre el grafo `import`/`export` desde `src/main.js`. Sin bundler, sin Node.js — solo Python. Transforma cada módulo a sistema `require`/`module.exports` en runtime. Inserta el resultado y el CSS de `src/styles/main.css` dentro de una copia de `src/index.html`.
- Fichero de salida del build: `src/_output/versions/index-v{NNNN}.html`. `NNNN` = `CURRENT_VERSION` (`src/data/version.js`). Fichero único autocontenido — el entregable portable.

## Persistencia y guardado a fichero

<!-- id: initial-state-seed -->
`src/index.html` incluye `<script type="application/json" id="initial-state"></script>` vacío. Sobrevive al build (se copia tal cual). Se rellena en runtime antes de la descarga vía "Guardar" (`core/fileExport.js`, ver más abajo). Semilla de estado embebida en cada copia del HTML descargada.

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

<!-- id: autosave-events -->
- Suscrito a eventos (`core/eventBus.js`) desde `main.js`: `components:changed`, `panelState:changed`, `resources:changed`, `resourcePanelState:changed`, `tags:changed`, `tagPanelState:changed`, `appTitle:changed`.
- Ante cualquiera de esos eventos, serializa a `localStorage`: `{ version: CURRENT_VERSION, components, panelState, resources, resourcePanelState, resourcesSeeded, tags, tagPanelState, appTitle }`.
- [gotcha] Guardado sin `appTitle`, o con valor vacío/no-string, no bloquea ni marca error — se trata como `core/appTitle.js` → `DEFAULT_APP_TITLE`.
- `tags:changed` dispara además `renderAll` (repintado completo), no solo autoguardado.
- Slot de `localStorage`: uno por navegador/perfil. [gotcha] `localStorage` no se aísla por fichero bajo `file://` — dos ficheros HTML abiertos en el mismo navegador comparten el mismo slot. Sin conservación entre navegadores/dispositivos.
- Arranque con guardado válido en `localStorage`:
  - `panelState`/`resourcePanelState`/`tagPanelState` presentes → hidratados con `loadPanelState()`/`loadResourcePanelState()`/`loadTagPanelState()` antes del primer render.
  - Ausentes → cada panel usa sus valores por defecto: expandido, posición/ancho/alto por defecto.
- `resources`/`tags` ausentes o no-array en el guardado/semilla → se asume `[]`, no invalida el resto del estado. `resources` en ese caso dispara backfill de recursos por defecto (ver sección "Recursos por defecto y backfill"); `tags` no dispara backfill.
- `selectedComponentIds`: no forma parte de ningún `panelState`. Nunca se persiste.
- "Guardar a fichero" (`core/fileExport.js`) incluye 7 campos: `components`, `panelState`, `resources`, `resourcePanelState`, `resourcesSeeded`, `tags`, `tagPanelState`.

<!-- id: persistence-backward-compat-chain -->
[breaking] Compatibilidad hacia atrás — cadena de fallback de 3 niveles en lectura: `parseState`/`parseImportedComponents` leen `tags`/`tagPanelState`; si ausentes, `groups`/`groupPanelState`; si ausentes, `decks`/`deckPanelState`. Mismo mecanismo documentado en `03-groups-resources.md` para el modelo de etiqueta.

### Guardar a fichero (`core/fileExport.js`, botón "Guardar" en `ui/editModeToggle.js`)

- `buildExportHtml(components, resources, panelState, resourcePanelState, resourcesSeeded, tags, tagPanelState, appTitle)`:
  - clona `document.documentElement` (CSS/JS ya embebidos por el build)
  - sustituye el contenido de `#initial-state` por el estado actual
  - `downloadHtml()` descarga el resultado como `Blob`
- Botón pide nombre de fichero. Precargado: `getFullAppTitle(getAppTitle())` + `.html`.
- [gotcha] Sustitución de fichero anterior con el mismo nombre: decisión del navegador según su configuración, no de la app.

### Exportar/Importar con selección (`core/importMerge.js` + `ui/exportSelectionModal.js`/`ui/importSelectionModal.js`/`ui/importConfirmModal.js`/`ui/importReportModal.js` en `ui/editModeToggle.js`)

[gotcha] "Exportar"/"Importar" no operan sobre el mismo formato que "Guardar". "Guardar" serializa la app completa (7 campos, ver arriba). "Exportar"/"Importar" usan el JSON ligero de `core/persistence.js`: `buildComponentsExport`/`parseImportedComponents` → `{ version, components, resources, tags }`, sin `appTitle`. Permite seleccionar subconjunto.

- Exportar: `openExportSelectionModal` sustituye el `prompt()` de nombre de fichero por modal con ese campo (precargado con el mismo título completo + `.json` que usa "Guardar" con `.html`), más 3 bloques de selección (`ui/elementSelectionModal.js`). Al confirmar, `ui/editModeToggle.js` filtra `getComponents()`/`getResources()`/`getTags()` por los ids marcados antes de llamar a `buildComponentsExport`/`downloadJson` — firma de esas 2 funciones sin cambios, reciben listas ya filtradas. [gotcha] Sin validación de referencias huérfanas en la selección exportada.
- Importar:
  1. `parseImportedComponents` parsea el fichero.
  2. `openImportSelectionModal` muestra los elementos del fichero para elegir cuáles importar.
  3. Al confirmar, `openImportConfirmModal` pide modo (`add`/`overwrite`) y comportamiento ante id duplicado (`overwrite`/`keepBoth`).
  4. Antes de `mergeImportedGame` (ver `03-groups-resources.md`), `ui/editModeToggle.js` pasa cada componente seleccionado de tipo `'ficha'` por `migrateFichaComponent`.
     - Con `errors` en alguno: `openImportConversionErrorModal` con la lista, antes de tocar el estado. "Abortar importación" no llama a `mergeImportedGame` ni a `loadComponents`/`loadResources`/`loadTags` — partida actual intacta. "Continuar sin esas fichas" sigue el flujo excluyéndolas de `selectedComponents`.
     - Sin `errors` (o sin fichas que migrar): sigue directo al paso 5.
  5. `core/importMerge.js` (`mergeImportedGame`) calcula el estado final:
     - `overwrite` (modo): parte de listas vacías, inserta directamente lo seleccionado. Sin conflicto posible.
     - `add` (modo): fusiona lo seleccionado con lo existente por tipo (componentes/recursos/etiquetas, cada uno con su propio espacio de ids).
       - Id ya existente + `conflictMode: 'overwrite'` → reemplaza el elemento existente.
       - Id ya existente + `conflictMode: 'keepBoth'` → renombra el importado con sufijo `-imported`/`-imported(n)` (`nextImportedId`, análogo a `nextCloneId` pero genérico por tipo). Referencias de componentes importados a un recurso/etiqueta renombrado se reescriben al nuevo id antes de fusionar. `etiquetaIds` es propiedad plana de primer nivel del componente, igual que `image` — no una clave dentro de `properties`.
       - Componentes ya existentes: no se tocan.
  6. Tras la fusión:
     - Referencia de componente recién importado a recurso ausente del estado final → campo a `null`. Mismo tratamiento que recurso borrado en uso.
     - Cada id ausente de `etiquetaIds` (puede haber varios por componente) se procesa por separado: se autocrea una etiqueta con ese id (una sola vez por id, aunque varios componentes lo referencien), o se vincula a la etiqueta existente con el mismo nombre si la hay.
     - Cada caso genera fila de informe: `{ componentId, tipoError, solucion, elemento }`. Con alguna fila, `ui/editModeToggle.js` abre `openImportReportModal(report)` al terminar.
  - `getComponentsWithMissingResources` (`core/resource.js`) y `getComponentsWithMissingDeck` (`core/deck.js`), del flujo de importación anterior (todo-o-nada con `confirm()`), eliminadas por quedar sin uso. El informe de `mergeImportedGame` las sustituye con más detalle.

### Recursos por defecto y backfill (`data/defaultResources.js`, `main.js`)

<!-- id: default-resources-backfill -->
```
inv: resourcesSeeded == true  ⇒  DEFAULT_RESOURCES sembrados al menos una vez en el estado actual o en uno anterior
inv: seedDefaultResources() se ejecuta como máximo una vez por línea de estado (guardado→guardado, sin resembrar tras borrado manual)
```

- Sesión totalmente nueva — nada guardado, sin semilla embebida, o guardado corrupto/incompatible: `seedDefaultResources()` siembra los 38 recursos de `DEFAULT_RESOURCES` (3 imágenes de fondo de localización + 35 imágenes de mochila/objetos/eventos), embebidas como data URI, con id fijo (nombre de fichero) en vez de UUID. Marca `resourcesSeeded = true` (`markResourcesSeeded()`).
- Guardado o semilla válidos (con componentes existentes) pero `resourcesSeeded !== true` — típicamente guardado anterior a esta funcionalidad, `resources` vacío o inexistente: `backfillDefaultResourcesIfNeeded()` los siembra igualmente esa vez. [gotcha] A partir de ahí quedan como recursos normales — si el usuario los borra, no reaparecen en cargas posteriores. Backfill no se repite una vez `resourcesSeeded` es `true`.
