# Modelo de datos de componente

Modelo genérico y extensible: no requiere cambios estructurales al definir tipos concretos (cartas, tokens, tablero, tracks...). Ver `02-component-types.md` para los tipos implementados.

```js
{
  id: string,          // identificador único (crypto.randomUUID(), editable por el usuario en la modal)
  type: string,         // libre, p.ej. "carta", "token", "tableroSimple", "texto"
  name: string,
  properties: object,   // pares clave-valor libres, específicos de cada tipo
  image: string | null, // referencia a un recurso, opcional (sin uso actual, ver tabla)
  x: number,             // posición en el mundo de la mesa, píxeles
  y: number,             // posición en el mundo de la mesa, píxeles
  width: number | null,  // ancho en píxeles, null = automático según contenido
  height: number | null, // alto en píxeles, null = automático según contenido
  bloqueado: 'ninguno' | 'juego' | 'todos',
  mostrarTooltip: boolean,
  tooltipTexto: string,
  mostrarTitulo: boolean,
  tituloTexto: string,
  tituloColorTexto: string,
  tituloColorFondo: string,
  tituloFondoTransparencia: number,
  subirAlMoverInteractuar: boolean,
  oculto: boolean,
  etiquetaIds: string[],
  order: number,
  copyOf: string | null,
  sincronizado: boolean,
  groupId: string | null,
  interaccionesDesactivadas: string[],
  accionClickDerecho: 'ninguno' | 'menuContextual',
}
```

## Campos generales

| Campo | Tipo/valores | Default | Para qué sirve | Quién lo edita |
|---|---|---|---|---|
| `id` | string | UUID generado | Identificador único | `ui/componentModal.js`, tab "Generales" (validación no-vacío + unicidad en capa UI) |
| `type` | string libre | — | Tipo de componente (`'texto'`, `'tableroSimple'`, etc.) | Fijado al crear, no editable después |
| `name` | string | — | Nombre | — |
| `properties` | object | `{}` | Propiedades específicas del tipo | `ui/componentModal.js`, tab "Específicas" |
| `image` | string \| null | `null` | Sin uso por ningún tipo actual. Tipos con fondo de imagen (`'tableroSimple'`, `'carta'`, `'tableroPersonalizado'`) referencian un recurso vía `properties.imagenResourceId` o `properties.<cara>.imagenResourceId`, no vía `image` | — |
| `x`, `y` | number | `0` | Posición en el mundo de la mesa. Alta desde modo edición asigna posición inicial sin solapar componentes existentes | Arrastre en la mesa |
| `width`, `height` | number \| null | `null` | Tamaño en píxeles. `null` = automático según contenido. Se fijan al redimensionar desde modo edición | Redimensionado en la mesa |
| `profundidad` | number | `0` (`4` en `'dado'` nuevo) | Grosor en px de la extrusión visual (capas sólidas apiladas, `box-shadow`/`filter: drop-shadow` según tipo). Tope `40`. `0` = sin efecto. Sin efecto en `'texto'` cualquiera que sea su valor. Ver `ui/componentRenderer.js` (`buildExtrusionLayers`) y `design/docs/style/01-tokens-visual.md` §6 | Pestaña "Visuales" de `ui/componentModal.js`, campo "Profundidad" (`<input type="number">`, clamp `[0, 40]`) |
| `colorExtrusion` | string (hex) \| null | `null` | Color de la extrusión. `null` = cálculo automático `shadeColor(colorBase, -0.25)` (`colorBase` según tipo, ver `resolveExtrusionColor` en `ui/componentRenderer.js`) | Pestaña "Visuales", campo "Color de extrusión" (`<input type="color">`, sin control de reset a `null` — una vez elegido un color explícito no hay forma de volver al cálculo automático desde la UI) |
| `bloqueado` | `'ninguno' \| 'juego' \| 'todos'` | `'ninguno'` | Modo(s) donde el componente no se puede mover. Controla arrastre en `modes/play/playMode.js` (bloqueado salvo `'ninguno'`) y en `modes/edit/editMode.js` (bloqueado solo con `'todos'`), cada modo pasa su propio `canMove` a `renderComponentsOnTable` | Pestaña "Generales" de `ui/componentModal.js`, desplegable de 3 opciones ("Ninguno"/"Solo modo juego"/"Todos los modos") |
| `mostrarTooltip` | boolean | `false` | Si `ui/componentRenderer.js` renderiza un tooltip propio (`.component-tooltip`) en modo juego (`identifyMode` global `'tooltip'`) al pasar el ratón por encima. Contenido: `tooltipTexto` si tiene texto, si no el identificador del componente | Pestaña "Generales", sección "Ayuda jugador" |
| `tooltipTexto` | string | `''` | Texto mostrado en el tooltip de `mostrarTooltip` cuando no está vacío (si está vacío, se usa el identificador del componente). Admite formato básico saneado por `sanitizeBasicTooltipHtml` (`ui/componentRenderer.js`): `<b>`, `<strong>`, `<i>`, `<em>`, `<u>`, `<br>`, `<ul>`, `<ol>`, `<li>`, sin atributos — cualquier otra etiqueta se desenvuelve conservando su contenido. Admite también variables de texto (ver "Sistema de variables de texto" más abajo). No es override de grupo: `getEffectiveGeneralProps` (`core/group.js`) no lo expone, siempre sale del propio `component.tooltipTexto` aunque el componente pertenezca a un grupo (a diferencia de `mostrarTooltip`, que sí es override de grupo) | Pestaña "Generales", sección "Ayuda jugador", `<textarea>` deshabilitado mientras "Mostrar tooltip" esté desmarcado |
| `mostrarTitulo` | boolean | `false` | Si `ui/componentRenderer.js` renderiza una etiqueta propia (`.component-title-label`) en modo juego (`identifyMode` global `'tooltip'`), anclada a la esquina superior izquierda del componente, **siempre visible** mientras esté activo (no depende de `:hover`, a diferencia de `mostrarTooltip`). Vacío `tituloTexto` no pinta ningún nodo. Override de grupo, mismo criterio que `mostrarTooltip`: si el componente pertenece a un grupo, manda `getEffectiveGeneralProps` | Pestaña "Generales", sección "Ayuda jugador" (00212, sustituye a la antigua etiqueta fija de nº de cartas de `'mazo'`, ver `02-component-types.md`) |
| `tituloTexto` | string | `''` | Contenido del título. Mismo formato básico saneado y mismas variables de texto que `tooltipTexto`. Sin fallback al identificador (a diferencia de `tooltipTexto`): vacío = no se pinta nada. No es override de grupo, siempre del propio componente | Sub-modal "Editar título de componente" (`ui/componentTitleModal.js`), botón "Editar título de componente…" junto al checkbox `mostrarTitulo` |
| `tituloColorTexto` | string (hex) | `'#000000'` | Color del texto de la etiqueta del título | Sub-modal "Editar título de componente" |
| `tituloColorFondo` | string (hex) | `'#ffffff'` | Color de fondo de la etiqueta del título, combinado con `tituloFondoTransparencia` vía `hexToRgba` (`core/colorUtils.js`) | Sub-modal "Editar título de componente" |
| `tituloFondoTransparencia` | number, 0–100 | `0` (opaco) | Transparencia del fondo de la etiqueta del título. El texto del título no tiene transparencia propia | Sub-modal "Editar título de componente" |
| `subirAlMoverInteractuar` | boolean | `false` (`true` para `'carta'`/`'dado'`) | Si sube a `order = 1` al mover/interactuar en modo juego. `modes/play/playMode.js` invoca `reorderComponent(id, 1)` tras cada interacción propia de Modo Juego (arrastre, lanzamiento de dado, volteo de carta). Independiente de `bloqueado` | Pestaña "Generales" |
| `oculto` | boolean | `false` | Si el componente NO se renderiza en modo juego (filtrado antes de `renderComponentsOnTable`). En modo edición no restringe nada, solo añade insignia (`showHiddenIndicator`) | Pestaña "Generales", segundo checkbox tras "Bloqueado" |
| `etiquetaIds` | string[] | `[]` | Ids de etiquetas (`getTags()`) a las que pertenece el componente. Un componente puede pertenecer a varias etiquetas a la vez | Sección "Etiquetas" de la pestaña "Generales": checkbox por etiqueta existente, ordenados alfabéticamente, más fila "+ Crear nueva etiqueta…" |
| `order` | number | calculado | Posición de apilado en la mesa: `1` = más arriba, `n` = más abajo. Ver lógica dedicada más abajo | No editable directo salvo vía columna "Orden" del panel de Componentes |
| `copyOf` | string \| null | `null` | Id del componente original si este es una "Copia" vinculada. Ver "Copias vinculadas" más abajo | Creado por acción "Copiar", no editable |
| `sincronizado` | boolean | `true` | Solo con efecto si `copyOf` no es `null`: si `bloqueado`/`oculto` de esta copia siguen al original | `ui/copyComponentModal.js` |
| `groupId` | string \| null | `null` | Id del "Grupo" (`grupo-N`) al que pertenece el componente, si alguno. Plano, sin anidación: un grupo no puede contener a otro grupo. Ver "Grupos en modo edición" en `04-modes.md` | Entradas "Agrupar"/"Desagrupar" del menú contextual de modo edición |
| `interaccionesDesactivadas` | string[] | `[]` (todas activas) | Keys de `core/interactions.js` desactivadas para este componente | Pestaña "Generales", sección "Interacciones programadas": un `<select>` por interacción de click izquierdo que el `type` tenga registrada |
| `accionClickDerecho` | `'ninguno' \| 'menuContextual'` | `'ninguno'` | Qué hace el click derecho en Modo Juego | Pestaña "Generales", fila fija dentro de "Interacciones programadas" ("Click derecho"), independiente de `type` |

Notas sobre migraciones silenciosas al cargar (`core/state.js`, `loadComponents`), best-effort, sin bloquear el arranque:

- `bloqueado`: guardados con el booleano anterior se migran vía `migrateBloqueado` (`true` → `'juego'`, `false` → `'ninguno'`).
- `mostrarTooltip`, `tooltipTexto`, `mostrarTitulo`, `tituloTexto`, `tituloColorTexto`, `tituloColorFondo`, `tituloFondoTransparencia`, `oculto`, `subirAlMoverInteractuar`, `interaccionesDesactivadas`: ausencia del campo se comporta como su valor por defecto (desmarcado / `''` / `'#000000'`/`'#ffffff'` / `0` / `[]`), sin necesidad de migración explícita.
- `etiquetaIds`: componente sin este campo, o con el formato intermedio `grupoIds` (array) o el escalar `grupoId` anterior, se migra vía `migrateGrupoIdToEtiquetaIds`; cartas con `properties.deckId` asignado añaden automáticamente ese id vía `migrateDeckIdToEtiqueta` (ejecutada justo después). `core/component.js` expone la conversión pura como `normalizeComponentEtiquetaIds(component)`, reutilizada también por `core/importMerge.js` (`mergeImportedGame`) para que importar un fichero anterior a esta migración no falle.
- `accionClickDerecho`: componente guardado sin este campo se migra a `'menuContextual'` (`migrateAccionClickDerecho`), para conservar el comportamiento previo — a diferencia del resto de campos de esta familia, el default de un componente nuevo (`'ninguno'`) y el valor migrado de uno preexistente (`'menuContextual'`) son deliberadamente distintos.
- `groupId`: ausencia del campo se comporta como su valor por defecto (`null`, sin grupo), sin necesidad de migración explícita — mismo criterio que `mostrarTooltip`/`oculto`/`subirAlMoverInteractuar`.
- `profundidad`, `colorExtrusion`: ausencia del campo se comporta como su valor por defecto (`0`/`null`, sin efecto), sin necesidad de migración explícita — mismo criterio que `oculto`/`mostrarTooltip`.

`core/component.js` expone `createComponent()`/`updateComponent()` como única vía para construir/modificar componentes. `createComponent()` inicializa `x`/`y` a `0`; `width`/`height` a `null`. También expone `cloneComponent(component, components)` y `nextCloneId(baseComponentId, components)`:

- `nextCloneId` calcula el id del clon quitando cualquier sufijo `(n)` final del id original (para que clones de un clon compartan raíz/familia) y añade `(n)` con el siguiente entero libre para esa raíz.
- `cloneComponent` construye el objeto clon completo (copia superficial + `properties`/`id` propios, posición desplazada +30/+30 respecto al original) con `order: null`, resuelto al añadirse con `addComponent` (queda en `order = 1`, igual que un componente nuevo). También nace con `groupId: null`: un clon es independiente, no se incorpora automáticamente al grupo del componente clonado.

## Lógica de `order`

`order` determina el apilado visual en la mesa (sustituye al orden de inserción/creación). Toda la lógica vive en `core/state.js`, no en `core/component.js` (que solo declara el campo con valor por defecto `null`, sin poder calcularlo sin conocer el resto de la lista).

- `addComponent(component)`: asigna `order = 1` antes de añadirlo, desplazando en +1 el `order` de los componentes ya existentes. Se usa también al dar de alta el clon de un componente clonado desde el panel.
- `removeComponent(id)`: recompacta los órdenes restantes para que sigan siendo consecutivos de 1 a n (`compactOrders`, función interna).
- `reorderComponent(id, rawOrder)`: mueve un componente a nueva posición — lo saca de su hueco actual (compactando lo que iba detrás), lo inserta en la posición indicada (desplazando hacia abajo lo que esté ahí o después), clampea `rawOrder` a `[1, n]`.
- `loadComponents(components)`: pasa la lista por `compactOrders` al cargar, migrando silenciosamente guardados sin campo `order` (o con valores inválidos) a partir de su orden de inserción existente.
- `reorderGroupBlock(memberIds, rawTargetOrder)` (00204): generalización de `reorderComponent` para mover un **bloque** de N ids contiguos a la vez (los miembros de un grupo, ver "Grupos en modo edición" en `04-modes.md`) en vez de uno solo, dentro del mismo espacio compartido `order` 1..n. Un miembro de un grupo no edita su propio `order` directamente — el panel de Componentes deshabilita ese campo en su fila; se edita en bloque desde el "Orden" de la fila de su grupo, que mueve a todos sus miembros manteniendo el orden relativo que ya tenían entre sí y clampea la posición de arranque del bloque a `[1, n-k+1]` (`k` = tamaño del bloque) para que quepa entero. La acción "Agrupar" del menú contextual llama también a esta función (con la posición del menor `order` de los seleccionados) para consolidar a consecutivos cualquier selección de miembros dispersos por la lista en el momento de formar el grupo.

## Copias vinculadas (`copyOf`)

A diferencia de "Clonar" (independiente tras crearse), una **Copia** queda permanentemente vinculada a su componente original (`copyOf: string`, id del original) y se sincroniza automáticamente con él mientras ambos existan, con excepción de `bloqueado`/`oculto` condicionados por `sincronizado`.

- Se crea desde el panel de componentes con el botón "Copiar" (`ui/componentList.js`, junto a "Editar"/"Clonar"/"Eliminar"; oculto para filas que ya son copia — no se admiten copias de copias). Acción inmediata sin modal previa, nace siempre con `sincronizado: true`.
- **Id**: `${idOriginal}-COPY-XXX`, `XXX` = primer entero de 3 dígitos libre entre las copias ya vinculadas a ese original (`core/component.js`, `nextCopyId(originalId, components)`, filtra por `copyOf`, no por el propio `id`). `createCopy(component, components)` construye la copia completa (mismo offset +30/+30 y `order: null` que `cloneComponent`).
- **Sincronización en vivo**: vive en `core/state.js`, enganchada en `replaceComponent(id, updatedComponent)` — lógica específica de este vínculo, no un mecanismo genérico de eventos. Al actualizar un original, cada copia vinculada (`copyOf === id`) se sustituye vía `core/component.js` → `syncCopyWithOriginal(copy, original)`.
  - Siempre propagado: `type`, `name`, `image`, `width`, `height`, `profundidad`, `colorExtrusion`, `mostrarTooltip`, `tooltipTexto`, `mostrarTitulo`, `tituloTexto`, `tituloColorTexto`, `tituloColorFondo`, `tituloFondoTransparencia`, `subirAlMoverInteractuar`, `etiquetaIds`, `interaccionesDesactivadas`, `properties` de configuración/diseño del tipo (todo lo editable desde `ui/componentModal.js`).
  - `bloqueado`/`oculto`: solo se propagan si `copy.sincronizado` es `true` (default). Con `sincronizado: false`, quedan como valor propio de la copia.
  - Siempre independientes por copia, sin excepción: `x`/`y`, `order`, `groupId` (pertenencia a un "Grupo", ver `04-modes.md` — se trata igual que la posición, nunca se sincroniza; `createCopy` nace siempre con `groupId: null`), claves de `properties` que son estado de interacción de juego por tipo (`NON_SYNCED_PROPERTY_KEYS` en `core/component.js`: `resultadoActual` en `'dado'`, `caraActual` en `'carta'`).
  - Si el `id` del original cambia en la misma actualización: `renameCopyId` renombra el `id` de cada copia (conserva sufijo `-COPY-XXX`, sustituye solo el prefijo) y actualiza su `copyOf`.
- **Borrado**: `removeComponent(id)` elimina en cascada cualquier copia vinculada (`copyOf === id`) — evita copias huérfanas. Eliminar una copia individual no afecta al original ni a otras copias.
- **Modal reducida**: `ui/copyComponentModal.js` (`openCopyComponentModal`) se abre en vez de `ui/componentModal.js` cuando `component.copyOf` es truthy (mismo punto de entrada, `modes/edit/editMode.js` → `openEditModalFor`). Sin pestañas: id (solo lectura), aviso, checkbox "Sincronizado", y dentro de `fieldset.modal__section` "Bloqueado / Oculto" (deshabilitada en bloque cuando "Sincronizado" está marcado) los controles "Bloqueado" (`<select>`) y "Oculto" (checkbox). Con "Sincronizado" marcado, ambos controles muestran y fuerzan el valor del original; desmarcado, quedan editables como valor propio. Id del original y botones Eliminar/Cancelar/Aceptar sin cambios. Aparte de esta modal, la fila "Ocultar"/"Mostrar" del menú contextual de Modo Edición (`04-modes.md`) es la única otra vía (fuera del interior de esta modal) que puede alterar `oculto` de una copia — y a diferencia de la modal (que bloquea el campo mientras `sincronizado: true`), esa fila permite el cambio siempre y desactiva `sincronizado` automáticamente al aplicarlo sobre una copia sincronizada.
- **Menú contextual en modo juego**: `modes/play/playMode.js` (`onContextMenu`) solo añade "Bloquear"/"Desbloquear" al menú de una copia si tiene `sincronizado: false` — con `sincronizado: true` (o ausente), no aparece, porque el bloqueo sigue siempre al original.
- **Indicador visual en modo edición**: ver `04-modes.md`, indicador de "Copia".

## Sistema de variables de texto

`core/textVariables.js` (módulo puro, sin dependencias) sustituye ocurrencias de `{nombre_variable}` en un texto por un valor calculado en el momento de renderizar, reutilizado por `tooltipTexto` y `tituloTexto` (`ui/componentRenderer.js`, aplicado antes de `sanitizeBasicTooltipHtml`). Diseñado para ampliarse con variables futuras sin rediseñar el mecanismo — el punto único de extensión es `getAvailableVariables`.

- `getAvailableVariables(component)`: devuelve el mapa `{ [nombre]: string }` de variables disponibles para **ese componente concreto**, según su `type`. Implementación actual: `component.type === 'mazo'` → `{ cards_current: String(properties.cartaIds.length) }` (nº de cartas actual del mazo); cualquier otro tipo → `{}` (ninguna variable disponible).
- `resolveTextVariables(text, component)`: sustituye cada `{nombre}` de `text` por su valor en `getAvailableVariables(component)` si existe esa clave. Si la variable no está definida para el tipo del componente actual (p. ej. `{cards_current}` en algo que no es `'mazo'`), se deja **literal, sin sustituir** — nunca cadena vacía.
- Se recalcula en cada render de la mesa (mismo momento en que antes se recalculaba el contador fijo de `'mazo'`), así que el valor de `cards_current` queda siempre actualizado sin invalidación especial.
