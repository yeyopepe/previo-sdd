# Modales, menús, tooltips, patrones de identificación

Ver `INDEX.md` para el mapa completo de la Style Bible.

## 12. Icono de ayuda (modal al pulsar)

Patrón estándar para ayuda contextual en cualquier punto de la app: `.help-icon`, círculo de 16px con "?" (`ui/helpIcon.js`, `createHelpIcon({ text, html })`).

- Aspecto: círculo 16px, fondo `var(--text-muted)` (`var(--accent-blue)` + `box-shadow: 0 2px 5px rgba(44,125,216,.35)` en `:hover`, transición 150ms), texto "?" en `var(--text-light)`, `font-size: 0.7rem`, `cursor: help`, sin borde.
- **Modal**: al pulsar el icono se abre siempre una modal con el texto/HTML, sin importar su longitud o formato. Reutiliza `.modal-overlay`/`.modal` (sin patrón nuevo), botón "Cerrar" (`.btn-cancel`), `z-index: 1000` (mismo reservado para overlays de modal).
- Cualquier ayuda contextual nueva: reutilizar `ui/helpIcon.js` en vez de crear una modal ad-hoc.

## 12.1 Modal de error

Patrón estándar para comunicar cualquier error de la app: `showErrorModal(title, message, detail)` (`ui/errorModal.js`).

- Reutiliza `.modal-overlay`/`.modal` (sin patrón nuevo), botón "Cerrar" (`.btn-cancel`), `z-index: 1000`.
- Diferencia respecto al modal informativo genérico: cabecera (`.modal__header--error`) incluye icono circular de alerta (`.modal__error-icon`, "!" sobre `var(--error)`) junto al título.
- Mensaje técnico adicional (p. ej. error de `JSON.parse`): bloque monoespaciado (`.modal__error-detail`) debajo del mensaje principal.
- Único punto de la app para comunicar errores: cualquier error nuevo usa `ui/errorModal.js`, nunca `ui/toast.js` u otro aviso ad-hoc — el toast queda reservado a confirmaciones/avisos de éxito.

## 12.1.1 Modal de éxito

Patrón para confirmar de forma bloqueante un resultado positivo que necesita quedarse visible hasta que el usuario lo cierra (a diferencia de `ui/toast.js`, para confirmaciones breves sin detalle que revisar): `.modal__header--success` / `.modal__success-icon`, equivalente en verde (`var(--success)`) del modal de error — mismo layout de cabecera, mismo `.modal-overlay`/`.modal`, mismo `z-index: 1000`.

- Ejemplo: `ui/batchUploadSummaryModal.js` (resumen tras subir varios recursos/carpeta a la galería) — icono "✓" sobre `var(--success)`, recuento de añadidos y, si aplica, tabla de omitidos (patrón de tabla de `ui/importReportModal.js`, misma CSS que `.import-report-modal__table`).
- Cualquier aviso de éxito futuro que deba quedarse visible: reutilizar este patrón en vez de crear variante ad-hoc.

## 12.1.2 Modal de operación en curso

Patrón para informar de una operación potencialmente lenta y bloqueante, devolviendo el control al jugador en cuanto termina (cambio 00214): `ui/progressModal.js`, `runWithProgressModal(text, work)`.

- A diferencia de cualquier otra modal de la app, **no reutiliza `.modal`** — bloque propio `.progress-modal` (fondo blanco, `border-radius: var(--radius-lg)`, `box-shadow: var(--shadow-2)`, mismo `.modal-overlay`/`z-index: 1000`) sin header/content/footer: solo un spinner (`.progress-modal__spinner`, círculo `40px`, borde `4px` en `var(--accent-blue-light)` con el segmento superior en `var(--accent-blue)`, giro continuo) y un texto breve (`.progress-modal__text`) debajo, centrado.
- **Primer y único uso de `@keyframes` en el proyecto**: `@keyframes progress-modal-spin` (rotación 360° continua, `0.8s linear infinite`).
- **Sin ningún botón ni vía de cierre manual** (ni click fuera del overlay, ni ESC) — única modal de la app así. Aparece al empezar la operación asociada y se cierra sola en cuanto termina; no es cancelable a medias.
- `work` se ejecuta dentro de un doble `requestAnimationFrame` anidado tras insertar la modal en el DOM, para garantizar que el navegador ha completado un ciclo de pintado real (con el spinner ya visible) antes de que empiece el bloqueo síncrono del trabajo real — `setTimeout(fn, 0)` no ofrece esa garantía (solo asegura orden en la cola de tareas, no que haya habido un repintado de por medio; bug 00218).
- Primer uso: arrastrar una selección múltiple de cartas sobre un mazo en modo edición (`023-componente-mazo.md`) — texto "Añadiendo N carta(s) al mazo…", `work` reposiciona las cartas arrastradas y las inserta en el mazo (el reposicionamiento va dentro de `work`, no antes: es la parte más lenta de la operación — bug 00219).
- Segundo uso: confirmar importación de fichero (`ui/importConfirmModal.js`, botón "Importar", cambio 00222) — texto "Importando…", `work` ejecuta la migración de fichas, `mergeImportedGame` y las cargas (`loadComponents`/`loadResources`/`loadTags`/`loadGroups`) en `ui/editModeToggle.js`.
- Cualquier operación futura potencialmente lenta y bloqueante: reutilizar este patrón en vez de dejar al jugador sin aviso.

## 12.2 Cursores

Convención general: cualquier elemento clicable muestra `cursor: pointer` al pasar el ratón, salvo que ya tenga uno de estos cursores más específicos (prioridad sobre el genérico):

| Cursor | Uso |
|---|---|
| `grab` / `grabbing` | Arrastrar la mesa infinita (`.infinite-table`) o un panel flotante por su cabecera (`.component-panel__header`, `.resource-panel__header`) |
| `move` | Mover un componente sobre la mesa (`.text-box--movable`, `.board--movable`, `.dice--movable`) |
| `nwse-resize` | Manejador de redimensionado (`.resize-handle`, `02-componentes-layout.md` §11) |
| `not-allowed` | Botón deshabilitado (`.btn-accept:disabled`) |
| `help` | Icono de ayuda contextual (`.help-icon`) |

- Regla de refuerzo: `input[type="checkbox"]`, `input[type="radio"]`, `.modal__field select` llevan `cursor: pointer` explícito en `main.css`, sin depender del estilo por defecto del navegador.
- **Modo juego**: componentes sobre la mesa usan siempre uno de 3 cursores fijos, nunca el puntero por defecto.
  - `move`: componente se puede arrastrar (checkbox "Bloqueado" desmarcado).
  - `pointer`: solo responde a un click sin poder arrastrarse (p. ej. dado "Bloqueado" — siempre se puede lanzar con click aunque no se mueva).
  - `grab`/`grabbing`: al arrastrar la propia mesa.
  - Cuando un componente admite ambas interacciones a la vez (dado no bloqueado: arrastrable y lanzable con click; carta no bloqueada: arrastrable y volteable con click), prevalece `move`.

## 12.3 Etiqueta identificativa de componente (modo edición)

Patrón para mostrar "qué es" un componente de la mesa sin abrirlo — distinto del icono de ayuda (§12): no es ayuda contextual, es identificación del elemento bajo el cursor.

- **Modo juego**: tooltip propio `.component-tooltip` (ya no el `title` nativo del navegador), disparado en `:hover` sobre todo el componente vía la clase marcadora `.component-tooltip-host`. Contenido: texto personalizado de `tooltipTexto` (con formato básico — negrita, cursiva, saltos de línea, listas — saneado por `sanitizeBasicTooltipHtml`, `ui/componentRenderer.js`) si el componente tiene ese campo relleno; si está vacío, cae al mismo `"<Tipo>: <id>"` de siempre (p. ej. "Dado: 3fa8..."). Aspecto compartido con el tooltip flotante genérico: fondo `var(--bg-toolbar)`, texto `var(--text-light)`, `box-shadow: var(--shadow-2)` — clase propia (no reutiliza `.help-icon`, §12, que abre modal al pulsar en vez de mostrar tooltip), porque el disparador cambia (todo el componente, no un icono fijo de 16px). Anclado sobre el `position: absolute` que el elemento raíz del componente ya tiene fijado para su colocación x/y en la mesa — nunca se sobrescribe ese `position` para "anclar" el tooltip, ya sirve tal cual de contexto de posicionamiento.
- **Modo edición**: etiqueta propia `.component-id-label` superpuesta a la esquina superior izquierda del componente, dentro de su área (no sobresaliendo por encima — evita depender de espacio libre arriba y quedar oculta tras cabecera/elemento fijo cerca del borde de la mesa).
  - Mismo texto/formato que en modo juego.
  - Fondo `var(--accent-blue-dark)`, texto `var(--text-light)`, `font-size: 0.72rem`, `border-radius: var(--radius-sm)`, sombra pequeña (`box-shadow: 0 2px 4px rgba(0,0,0,.25)`) para leerse "pegada" a la pieza.
  - `pointer-events: none` — no intercepta arrastre/selección del elemento debajo.
  - Visible solo en `:hover` y `.<tipo>--selected` (mismos momentos que el contorno azul discontinuo de selección), nunca de forma permanente.
  - No se recorta ni envuelve en varias líneas si el id es más largo que el componente — puede sobresalir de su ancho (ayuda de edición, no arte final).

## 12.3.1 Título de componente (modo juego)

Etiqueta configurable por componente, distinta de la anterior (§12.3): no identifica "qué es" el componente, es un rótulo de contenido libre que el usuario diseña — sustituye (00212) a la antigua etiqueta fija de nº de cartas de `'mazo'`, generalizada a los 8 tipos.

- `.component-title-label`, pintada por `attachComponentTitle` (`ui/componentRenderer.js`) cuando `mostrarTitulo` (override de grupo, como `mostrarTooltip`) está activo y `tituloTexto` no está vacío — vacío no pinta ningún nodo, a diferencia del tooltip (§12.3) que cae al identificador.
- **Siempre visible** en Modo Juego mientras esté activa (no depende de `:hover`, a diferencia de `.component-tooltip`) — mismo criterio de visibilidad permanente que tenía la antigua `.mazo-count-label`.
- Mismo anclaje que tenía `.mazo-count-label`: fuera de la caja del componente, pegada a su esquina superior izquierda (`top: -1.6rem; left: 2px`), `pointer-events: none`.
- Contenido: `tituloTexto` con formato básico saneado (mismo `sanitizeBasicTooltipHtml` que el tooltip) y variables de texto resueltas (`core/textVariables.js`, `01-component-model.md`).
- Color de texto/fondo/transparencia: `tituloColorTexto`/`tituloColorFondo`/`tituloFondoTransparencia`, aplicados **inline** por `attachComponentTitle` (`element.style.color`/`backgroundColor`), no como token CSS fijo — excepción justificada porque es dato de usuario configurable por componente, no un valor del sistema de diseño (mismo criterio ya aceptado para `colorFondo`/`colorFondoTransparencia` de `TextBox`/`Forma` de carta, vía `hexToRgba`).
- Editado desde sección "Ayuda jugador" de `ui/componentModal.js`: checkbox "Mostrar título de componente" + botón "Editar título de componente…" que abre `ui/componentTitleModal.js` (sub-modal sin tabs, mismo patrón que `ui/boardPatternModal.js`: contenido, color de texto, color de fondo, transparencia del fondo con slider + campo numérico sincronizado — `.modal__opacity-value`, mismo patrón ya usado en `ui/cardShapeModal.js`).

### Indicador de bloqueo (`.component-lock-badge`)

Insignia hermana de `.component-id-label` en criterio de superposición (esquina del componente, contenedor exterior, `pointer-events: none`), con diferencias deliberadas:

- Esquina superior **derecha** (no izquierda, para no solapar con la etiqueta identificativa).
- Círculo `18px`, fondo `rgba(0,0,0,.55)`, trazo del candado en `var(--text-light)` (contraste sobre cualquier fondo/imagen del componente) en vez de etiqueta rectangular con texto.
- Visible de forma **permanente** mientras `component.bloqueado` esté activo (no solo `:hover`/selección).
- Solo en modo edición (`showLockIndicator`, `ui/componentRenderer.js`). En modo juego el bloqueo no se muestra sobre el componente, solo vía menú contextual (§12.8).

### Indicador de "Oculto" (`.component-hidden-badge`)

Mismo patrón visual que `.component-lock-badge` (círculo `18px`, fondo `rgba(0,0,0,.55)`, icono `var(--text-light)`, `pointer-events: none`, permanente mientras `component.oculto` esté activo, solo modo edición vía `showHiddenIndicator`), icono de ojo tachado en vez de candado.

- Anclada en esquina inferior **derecha** (no superior derecha del candado) para convivir sin solaparse cuando un componente está bloqueado y oculto a la vez.

### Indicador de "Copia" (`.component-copy-badge`)

Mismo patrón de superposición que candado/oculto (círculo `18px`, icono `var(--text-light)`, `pointer-events: none`, permanente mientras `component.copyOf` no sea `null`, solo modo edición vía `showCopyIndicator`), icono de dos cuadrados superpuestos.

- Dos diferencias deliberadas:
  - Fondo `var(--error)` en vez del `rgba(0,0,0,.55)` neutro de las otras dos — primer uso de este token fuera de su semántica de error/acción destructiva (decidido explícitamente solo para este indicador, no reabre la convención para otros usos).
  - Anclada en esquina inferior **izquierda** — la última de las cuatro libre (superior izquierda: etiqueta identificativa; superior derecha: candado; inferior derecha: oculto).

### Indicador de "Tiene copias" (`.component-has-copies-badge`)

Mismo icono y esquina inferior izquierda que `.component-copy-badge`, pero con fondo `var(--accent-blue-dark)` — mismo azul que ya usa `.component-id-label` (§12.3, "Etiqueta identificativa de componente") — precisamente para diferenciarse a simple vista del indicador de copia (que sigue en rojo), en vez de compartir su familia visual. `pointer-events: none`, permanente mientras el componente tenga copias vinculadas, solo modo edición vía `showCopyIndicator`, en forma de píldora para incorporar el número de copias (p. ej., "(2)") junto al icono.

- Anclada en esquina inferior **izquierda**, exactamente igual que `.component-copy-badge` — mutuamente excluyente (un componente original nunca tiene `copyOf` propio, así que nunca muestra las dos insignias a la vez).
- Altura fija `18px` (match con los otros badges), ancho variable según cantidad de dígitos del número (padding y `border-radius: 9px` para la forma redondeada).
- Mismo tamaño de icono que los otros badges (`14px` en esta píldora, `18px` en el círculo de copia), mismo criterio de espacio interior (`gap: 3px` entre icono y número).

### Contorno de selección y etiqueta en rojo para copias

Además de la insignia anterior: cuando un componente con `copyOf` no nulo está en `:hover`/`.<tipo>--selected`, el contorno discontinuo de selección y el fondo de `.component-id-label` (normalmente `var(--accent-blue)`/`var(--accent-blue-dark)`) se pintan en `var(--error)` — mismo tono que el indicador de copia, refuerza de un vistazo que el elemento es una copia.

- Se activa con la clase `is-copy` (`ui/componentRenderer.js`, junto a la clase `--selectable` propia del tipo, cuando `showCopyIndicator` está activo y `component.copyOf` no es `null`) — clase simple sin prefijo de bloque, mismo criterio que `.grabbing`/`.active`/`.lifted` (`INDEX.md` §7), estado transversal a los 7 tipos de componente.
- Los 6 bloques `--selectable`/`--selected` por tipo (`.text-box`, `.board`, `.tablero-personalizado`, `.dice`, `.document-viewer`, `.carta` — cubre también `mazo`, que reutiliza sus clases) incluyen cada uno la variante calificada con `.is-copy`.

### Botones de acción superpuestos a una imagen (`.resource-modal__zoom-btn`)

Variante *interactiva* del mismo lenguaje visual de esta sección (fondo `rgba(0,0,0,.55)`, icono `stroke="currentColor"` en `var(--text-light)`) para cuando lo superpuesto es un botón de acción real, no un indicador pasivo — controles de zoom sobre la vista previa de un recurso Imagen (`ui/resourceModal.js`).

- Deliberadamente **no** usa `.align-group`/`.align-group__btn` (§12.10, pensado para opciones seleccionables con estado `active` sobre fondo de formulario): estos botones son acciones momentáneas sin estado "activo" y necesitan contraste garantizado sobre imagen de contenido arbitrario, no fondo neutro de modal.
- Cuadrado `32px`, `border-radius: var(--radius-sm)`, hover `rgba(0,0,0,.72)`, `title`/`aria-label` como única etiqueta accesible (botón icono-solo, §9 en `02-componentes-layout.md`).
- Cualquier control de acción futuro superpuesto sobre imagen/contenido visual arbitrario: reutilizar este criterio en vez de `.align-group` o un overlay ad-hoc.

## 12.4 Modales anchas (excepción a `max-width: 500px`)

`.modal` usa por defecto `max-width: 500px`. Cuando el contenido necesita más espacio (varias columnas, listas largas), la modal añade una segunda clase de bloque propia con su propio `max-width`, en vez de sobrescribir el valor por defecto ad-hoc.

| Clase | Modal / fichero | Ancho |
|---|---|---|
| `.component-editor-modal` | Edición de componentes (`ui/componentModal.js`, `openComponentModal`) | `clamp()` con `75vw`, acotado entre `400px` y `min(1000px, 90vw)` — recalculado dinámicamente en redimensionados de ventana sin JS |
| `.card-editor-modal` | Editor visual (`ui/visualEditorModal.js`), de una o dos caras según tipo (`'carta'` dos caras, `'tableroPersonalizado'` una) | `width: fit-content; max-width: min(1500px, 95vw)` — se ajusta al contenido porque el ancho varía según la proporción de carta activa. Admite modificador `.card-editor-modal--maximized` (botón en cabecera) que sustituye por `width: 97vw; max-width: none` y anula `max-height: 80vh` de `.modal` |
| `.image-adjust-modal--large` | Ventana de ajuste de imagen de una o dos caras (`ui/imageAdjustModal.js`) | `width: fit-content; max-width: min(1500px, 95vw)` — mismo criterio que `.card-editor-modal`, ancho combinado de cajas de previsualización varía según caras mostradas |
| `.element-selection-modal` | Exportar/importar con selección | `max-width: 640px` |
| `.import-report-modal` | Informe de importación con tabla. Reutilizada tal cual por `ui/importConversionErrorModal.js` (errores al convertir fichas durante importación, cabecera de error §12.1, dos botones de acción como `ui/groupDeleteConfirmModal.js`). Añade clase `.error-cell` (`color: var(--error)`) a celda de motivo de error en `.import-report-modal__table`, reutilizable por cualquier tabla que destaque una celda de error | `max-width: 640px` |
| `.resource-modal--image` | Edición de recurso tipo Imagen (`ui/resourceModal.js`) — más espacio para vista previa ampliada con zoom/pan. Solo si el recurso es Imagen; la modal de Tipografía usa `.modal` genérico | `width: fit-content; max-width: min(800px, 95vw)` |
| `.board-image-modal` | Galería de imágenes de fondo para tablero simple/carta/tablero personalizado (`ui/boardImageModal.js`). Miniatura `.board-image-modal__thumb` `140px`, grid `.board-image-modal__gallery` `minmax(160px, 1fr)` | `max-width: min(900px, 90vw)` — fijo, contenido es grid de miniaturas que se recoloca solo |

- Cualquier modal nueva que necesite más ancho: clase de bloque propia añadida a `modal.className` (p. ej. `'modal mi-modal'`), con su `max-width` (o `width: fit-content` + tope si el contenido es de ancho variable) en `main.css` — nunca `style="max-width:…"` inline.

## 12.4.1 Botón maximizar/restaurar de modal

Primer uso de este patrón: `.card-editor-modal__maximize-btn` — bloque propio de esa modal (no excepción `.btn-*` standalone, ya que cuelga de `.card-editor-modal`).

- Colocado en `.modal__header`, entre el título y el `.help-icon` si lo hay.
- Alterna entre dos iconos SVG locales (`createMaximizeIcon`/`createRestoreIcon` en `ui/cardEditorModal.js`) según estado booleano local a esa apertura de la modal, sin persistencia entre usos.
- `margin-left: auto` — queda, junto con el `.help-icon` que le sigue, pegado al borde derecho de la cabecera (título solo a la izquierda, hueco disponible entre ambos).
- Reposo: fondo `var(--bg-subtle)`, hover `var(--bg-hover)`, `border-radius: var(--radius-sm)`, transición `background var(--transition-fast)`.
- Sin texto: expone `title`/`aria-label` actualizados en cada toggle ("Maximizar"/"Restaurar tamaño").
- El interruptor añade/quita la clase modificadora de tamaño (§12.4) sobre `.modal` — nunca cierra la modal (depende solo de sus botones de pie "Cancelar"/"Aceptar").
- Cualquier modal futura que necesite maximizar/restaurar: reutilizar este patrón (botón, posición, iconos, sin persistencia).

## 12.5 Lista de selección agrupada (checklist)

Patrón para elegir un subconjunto de una colección organizada por categorías (`ui/elementSelectionModal.js`, usado por modales de exportar/importar con selección):

- Bloque por categoría (`.element-selection-group`), cabecera que combina checkbox "seleccionar todo el bloque" + título de categoría (`.element-selection-group__select-all`, fondo `var(--bg-subtle)`, mismo tono que cabecera de `.component-list`).
- Debajo, lista de checks individuales (`.element-selection-group__list`, scroll vertical propio si excede `12rem` de alto; cada ítem `.element-selection-group__item` hover `var(--bg-hover)`, mismo criterio que fila de `.component-list`).
- Bloque sin elementos no se pinta (no se muestra categoría vacía).
- Cualquier selección múltiple futura organizada en categorías: reutilizar este patrón — mismo criterio que `.resize-handle` o `.help-icon`.

## 12.6 Secciones dentro de pestañas de propiedades

Patrón para agrupar visualmente varios campos relacionados dentro de una pestaña de `ui/componentModal.js` (o sub-modal de edición) cuando el grupo crece lo bastante como para necesitar separación, sin justificar pestaña/sub-modal propios.

- Bloque `.modal__section`, implementado con `<fieldset class="modal__section">`.
  - Encuadrada: `border: 1px solid var(--border-neutral)` (mismo gris neutro de cualquier borde fino, sin color nuevo), `border-radius: var(--radius-sm)`.
  - `margin-top: 1rem` respecto al campo anterior (mismo criterio de espaciado de `01-tokens-visual.md` §4), `padding: 1rem` interior.
  - Agrupación visual estática, siempre visible dentro de la pestaña ya activa — no introduce tabs, acordeón ni colapso.
- Título en `<legend class="modal__section-title">` (el propio `<legend>` corta el borde superior del `fieldset`, sin línea/pseudo-elemento aparte), color `var(--section-accent)`, mayúsculas — único uso de ese tono en la app (ver excepción de color en `INDEX.md` §13).
- Dos tipos de título, según si el grupo representa una configuración activable/desactivable entera:
  - **Meramente informativo** (`.modal__section-title`): solo texto, sin control. Campos de dentro siempre activos.
  - **Des/activador** (`.modal__section-title--toggle`): mismo `<legend>`, precedido de checkbox formando una fila (`display:flex; align-items:center; gap:0.5rem`, igual que `.modal__field--checkbox` pero haciendo de título de sección). Controla si la sección entera está activa: desmarcado, resto de campos (`.modal__section--disabled`) se muestran deshabilitados (`opacity: 0.5; pointer-events: none`, más `disabled` en cada input desde JS) sin perder valores ya introducidos; marcado, se habilitan de nuevo tal cual estaban.
- `.modal__section--untitled`: mismo `<fieldset>`/CSS sin `<legend>`, para un grupo que necesita el mismo marco pero no tiene nombre propio.

### 12.6.1 Número + botón que abre modal aparte

Patrón para listas potencialmente largas de solo lectura dentro de una sección de la modal de propiedades: un contador numérico (p. ej. "5") seguido de un botón que abre una modal independiente con la lista completa, evitando descontrolar el alto de la sección si hay muchos elementos.

- Bloque `.{bloque}-summary` (p. ej. `.component-copies-summary`) con fila de lectura internamente (`.{bloque}-summary__row` con `.{bloque}-summary__label` a la izquierda y `.{bloque}-summary__value` a la derecha, mismo criterio visual que `.context-menu__info-label`/`__info-value` de §12.8 sin reutilizar literalmente esas clases si el bloque vive fuera de `.context-menu`), seguida de botón a todo lo ancho (`.{bloque}-summary__button` con `width: 100%`).
- Botón reutiliza `.btn-cancel` — misma excepción visual que el botón "Ver contenido del mazo" de la modal de edición de mazo (§12.4).
- La modal que abre el botón (`.{bloque}-modal`, p. ej. `.component-copies-modal`) sigue el esqueleto estándar de `.modal` con cabecera, pista/hint y contenido, sin `max-width` especial necesario (el ancho por defecto `500px` es suficiente para listas de ids).
- Primer uso: `.component-copies-summary` → `.component-copies-modal` (`ui/componentModal.js`, pestaña "Copias" + `ui/componentCopiesModal.js`) para la lista de copias vinculadas a un Original. Ese bloque vive ahora en su propia pestaña "Copias" de la modal de propiedades (no ya dentro de la pestaña "Generales"). La modal de listado añade columna de estado (`.component-copies-modal__sync--yes/--no`) para diferenciar copias sincronizadas de desincronizadas en una fila (mismo patrón de estado para futuras listas de solo lectura con estado por elemento).
- Cualquier lista de solo lectura potencialmente larga dentro de una sección: reutilizar este patrón en vez de desplegarla inline.

### Usos del patrón

- `ui/cardTextBoxModal.js` (cuadro de texto de carta): "Borde" (des/activador: checkbox "Activar borde" + color/grosor/tipo de línea), "Fondo" (informativo: color de fondo + checkbox de campo "Transparente" — control de campo, no de sección).
- `ui/componentModal.js`, tipo `'tableroSimple'`: "Visual" (informativa, primera sección de la pestaña: campo checkbox "Biselado en el borde" marcado por defecto, ver `INDEX.md` §13; campo checkbox "Sombra" marcado por defecto, ver `01-tokens-visual.md` §6), "Borde" (des/activador: checkbox "Activar borde" + color/grosor 1–20, mismo patrón que `TextBox`/`Shape` — un tablero nuevo o antiguo nace con el checkbox marcado), y sin título (`.modal__section--untitled`) el campo "Fondo" (selector con tres opciones: "Color y patrón"/"Imagen"/"Color").
- `ui/componentModal.js`, tipo `'tableroPersonalizado'`: "Visual" (informativa, mismos campos "Biselado en el borde" y "Sombra" que `'tableroSimple'`), seguida del botón "Editar diseño del tablero" (sin `.modal__section` propio, campo suelto).
- `ui/boardPatternModal.js` ("Configurar fondo — Color y patrón"): dos secciones informativas — "Configuración" (Forma de casilla; Filas y Columnas en la misma fila, patrón de fila de `INDEX.md` §8) y "Color" (Color de fondo con checkbox "Transparente", Color del patrón/Grosor en la misma fila).
- `ui/boardColorModal.js` ("Configurar fondo — Color"): tercer tipo de fondo de `tableroSimple` junto a "Imagen"/"Color y patrón" — un único campo de color + checkbox "Transparente", sin `.modal__section` (un solo campo).
- `ui/cardShapeModal.js` (figura geométrica de carta): "Borde" (des/activador: checkbox "Activar borde" + color/grosor 1–20, sin diferencia con `TextBox` — figura nueva nace con checkbox marcado), "Fondo" (informativo, mismo criterio que `TextBox`).
- `ui/componentModal.js`, tipo `'mazo'`: "Forma" (informativa: Forma, Orientación), "Cartas reveladas" (informativa: Disposición carta revelada, Texto carta revelada, Revelar carta) e "Imagen" (informativa: preview + Elegir/Ajustar/Quitar imagen).

Cualquier grupo de campos futuro con esta necesidad: reutilizar `.modal__section`/`.modal__section--untitled` con el tipo de título correspondiente, en vez de crear marco o checkbox de activación ad-hoc.

### 12.6.1 Zona con scroll interno dentro de una sección

Cuando el contenido de una `.modal__section` es una lista potencialmente larga (una por elemento de una colección que puede crecer, a diferencia de un grupo fijo de campos como "Borde"/"Fondo"):

- La lista se envuelve en contenedor propio con `max-height` + `overflow-y: auto` — tope aproximado por número de filas visibles, no cálculo dinámico exacto (mismo criterio que `.element-selection-group__list`, §12.5, tope `12rem`).
- El resto de la sección (título, filas de acción como "+ Crear...") queda **fuera** de ese contenedor, para no desplazarse junto con la lista.
- Primer uso: `.tag-checkbox-list__scroll` en sección "Etiquetas" de `ui/componentModal.js` — tope `6.5rem` (~3 filas de checkbox), fila "+ Crear nueva etiqueta…" fuera de la zona de scroll, como hijo directo de `.modal__section`, siempre visible.
- Cualquier sección futura con esta necesidad: reutilizar este patrón (contenedor de scroll separado de fila de acción fija) en vez de aplicar `max-height`/`overflow-y` a la sección entera.

## 12.7 Menú desplegable de acciones

Patrón para ofrecer varias variantes de una misma acción desde un único botón, cuando no encajan como opciones de modal ni como botones separados (`ui/resourceList.js`, `createAddMenu`):

- Botón (`.resource-add__button`, mismo aspecto que el botón que sustituye) despliega panel flotante (`.resource-add__menu`, `position: absolute`, fondo `var(--accent-blue-light)`, `border: 1px solid rgba(44, 125, 216, 0.25)`, `border-radius: var(--radius-sm)`, `box-shadow: var(--shadow-2)` — nivel 2) con lista de ítems (`.resource-add__item`, separados por `border-bottom: 1px solid rgba(44, 125, 216, 0.25)`).
- Excepción al hover neutro estándar: hover `var(--accent-blue)` (no `var(--bg-hover)`), etiqueta y nota auxiliar pasan a `var(--text-light)` en ese estado.
- Cada ítem puede llevar etiqueta (`.resource-add__item-label`, `color: var(--text-primary)` en reposo) + nota auxiliar debajo (`.resource-add__hint`, `font-size: 0.75rem`, `color: var(--text-muted)`) para aclarar limitación de esa opción.
- Se abre/cierra al pulsar el botón, se cierra también al click fuera o al elegir ítem — mismo criterio de cierre que las modales (`overlay` de `.modal-overlay`).
- Distinto de una modal (no bloquea el resto de pantalla, sin `overlay`) y de un `<select>` nativo (cada ítem puede llevar contenido adicional).
- Cualquier menú desplegable similar futuro: reutilizar este patrón.

### Otros usos del patrón

- `ui/cardEditorModal.js`: mismas clases (`resource-add`/`resource-add__button`/`resource-add__menu`/`resource-add__item`/`resource-add__item-label`) para el botón "Añadir elemento" de cada cara del editor de cartas (Imagen de fondo / Cuadro de texto / Figura geométrica) — confirma que el patrón es agnóstico al dominio.
- `ui/columnHeaderMenu.js` (`openColumnHeaderMenu`): mismo lenguaje visual (fondo `var(--accent-blue-light)`, borde `rgba(44, 125, 216, 0.25)`, `border-radius: var(--radius-sm)`, `box-shadow: var(--shadow-2)`, hover `var(--accent-blue)`/texto `var(--text-light)`) para el menú de ordenación/filtrado al pulsar el nombre de una columna en paneles de Componentes/Recursos/Etiquetas (ver `design/docs/architecture/04-modes.md`), con clases propias (`.column-header-menu`/`.column-header-menu__item`/`.column-header-menu__separator`/`.column-header-menu__filter`).
  - Contenido distinto: dos filas de ordenación tipo interruptor (`.column-header-menu__item--active` en la activa, misma convención de "opción activa" que §12.10 — fondo `var(--accent-blue)`, texto `var(--text-light)`) y, si la columna es filtrable, bloque con `<select>` nativo.
  - **Variante de posicionamiento**: `position: fixed` insertado en `document.body`, calculando posición desde `getBoundingClientRect()` del `<th>` pulsado y reajustando para no salirse de la ventana — mismo mecanismo que `.context-menu` (§12.8), porque su punto de anclaje vive dentro de contenedores con `overflow: auto`/`overflow: hidden` que recortarían un `position: absolute`.
  - Mismo `z-index` que `.context-menu` (`1050`) por el mismo motivo: puede abrirse con modal ya visible detrás.
  - Cualquier columna interactiva muestra siempre indicador junto a su nombre (`.column-header-menu__indicator`, icono SVG `currentColor`), incluso con el menú cerrado y sin nada aplicado todavía.
  - Dos estados de color: `var(--text-muted)` por defecto ("disponible pero no activo"), `var(--accent-blue)` (modificador `.column-header-menu__indicator--active`) cuando la columna tiene orden y/o filtro aplicados.
- `.card-editor-modal__shape` (`ui/cardEditorModal.js`, figura geométrica del editor de cartas): bloque hermano de `.card-editor-modal__textbox` — mismo cursor `move`, mismo contorno discontinuo azul en `:hover`, mismo contorno continuo `--selected` al seleccionar, mismo `.resize-handle` en su esquina inferior derecha.
  - Sin tipografía/contenido de texto propio: solo `border-radius` (`50%` si circular/elíptica, `0` si cuadrada), `background-color`, `border` (línea simple, sin el bisel reservado a `'tableroSimple'`/`'dado'` — visible solo si `bordeActivo` está activo).
  - Redimensionado libre en ambos ejes con Shift forzando 1:1 (tipo circular/elíptico) reutiliza el comportamiento genérico de `ui/resizeHandle.js` para `axis: 'both'` (el mismo que la proporción "Circular" de `'carta'`), sin `clamp` de proporción propio.

## 12.8 Menú contextual de componente

Patrón para el menú de click derecho sobre un componente de la mesa (`ui/contextMenu.js`, `openContextMenu`): reutiliza el lenguaje visual de §12.7 para `.resource-add__menu` — fondo `var(--accent-blue-light)`, borde `rgba(44, 125, 216, 0.25)`, `border-radius: var(--radius-sm)`, `box-shadow: var(--shadow-2)`, hover `var(--accent-blue)`/texto `var(--text-light)` — con clases propias (`.context-menu`/`.context-menu__item`/`.context-menu__separator`) en vez de `.resource-add__*`, al no colgar de un botón sino posicionarse junto al cursor (`position: fixed`, reajustado tras insertarse para no salirse de la ventana).

- Cada fila: icono (`.context-menu__item-icon`, 18×18px) + texto (`.context-menu__item-label`), separadas por `border-bottom` como en `.resource-add__item`.
- Separador entre sección general y específica (`.context-menu__separator`, solo si hay alguna acción específica): simple `border-top` del mismo tono.
- `z-index: 1050` (por delante del overlay de modal `1000` — este menú también puede abrirse con modal ya visible detrás, p. ej. editor de cartas).

### Secciones del menú

El menú organiza su contenido en hasta cinco secciones posibles, en este orden:

0. Línea de descripción de solo lectura, antes de cualquier otra sección.
1. Sección general de acciones, cableada en código (hoy: Bloquear/Desbloquear en Modo Juego; Clonar/Copiar/Eliminar en Modo Edición).
2. Sección específica por tipo de componente (`specificItems` — p. ej. "Barajar"/"Ver contenido..." para un mazo, "Meter en mazo..." para una carta si existe algún mazo en la partida; mismas filas `.context-menu__item` con icono que la sección general).
3. Sección fija de solo lectura (`interactionItems`) que muestra qué hace cada tipo de click sobre ese componente, separada de las anteriores por `.context-menu__separator` propio.
4. Fila con `<select>` inline (ver más abajo).

La sección informativa (3) no sigue el patrón interactivo (icono + hover azul):

- Encabezado pequeño/mayúsculas/tenue (`.context-menu__info-title`, `font-size: 0.75rem`, `color: var(--text-muted)`, `text-transform: uppercase`).
- Filas de solo lectura (`.context-menu__info-row`, sin hover ni `cursor: pointer`, flex con label a la izquierda y valor a la derecha), `.context-menu__info-label` + `.context-menu__info-value` (`0.8125rem`, más pequeño que filas de acción).
- Modificador `.context-menu__info-value--none` para valores "Ninguno" (cursiva + ligera opacidad).
- Bloque completo en contenedor `.context-menu__info` con `cursor: default`.

### Menú en Modo Edición y fila con `<select>` inline

`ui/contextMenu.js` se reutiliza en Modo Edición (clic derecho sobre elemento de la mesa), con sección general Clonar/Copiar/Eliminar (mismas filas con icono) y sección específica con fila única "Añadir a etiqueta".

- Esa fila introduce un cuarto tipo de contenido, distinto de acción de click directo: bloque `.context-menu__select-row` (`cursor: default`, sin hover, separado por `border-bottom` igual que `.context-menu__item`) con etiqueta arriba (`.context-menu__select-row-label`) y `<select>` nativo a todo lo ancho debajo — mismo criterio visual que `.column-header-menu__filter`/`.column-header-menu__filter-label`/`.column-header-menu__filter select` (§12.7).
- Elegir opción real (no el placeholder "Elegir etiqueta…") ejecuta la acción y cierra el menú, igual que pulsar cualquier fila de acción.
- Sin opciones disponibles (p. ej. "Añadir a etiqueta" sin etiquetas creadas): `<select>` deshabilitado (mismo `:disabled` que resto de controles — fondo `var(--border-neutral)`, `cursor: not-allowed`), muestra "Sin etiquetas" en vez del placeholder habitual.

### Línea de descripción

`description` identifica el componente sobre el que se abrió el menú, calculada en el momento de abrirlo a partir de su estado actual: primera fila de todas, con `.context-menu__separator` propio siempre presente entre ella y el resto del menú (a diferencia del separador entre secciones general/específica, este no depende de que haya contenido después).

- Bloque `.context-menu__description` (`cursor: default`, sin hover ni acción, disposición en columna) con dos líneas apiladas, distinto del patrón label/valor en fila de `.context-menu__info-row`:
  - `.context-menu__description-main`: texto "Tipo: id" (mismo formato "`<Tipo>: <id>`" de §12.3), `font-weight: 600`, `color: var(--text-primary)`.
  - `.context-menu__description-extra` (solo si aplica): una propiedad diferenciadora según el tipo de componente (p. ej. número de caras de un dado, tamaño "AAxBB" de un tablero, número de cartas de un mazo), `font-size: 0.75rem`, `color: var(--text-muted)`.
- No reutiliza `.context-menu__info-*` porque esa familia está pensada para pares label/valor en fila, no este bloque de dos líneas apiladas.

Cualquier menú contextual futuro: reutilizar este patrón en vez de crear uno ad-hoc — mismo criterio que `.resize-handle`, `.help-icon` o `.resource-add__menu`.

## 12.9 Copiar/Pegar estilo de un componente

Patrón para copiar el estilo visual de un componente y pegarlo en otro del mismo tipo (`ui/componentModal.js` + `core/styleClipboard.js`, implementado hoy solo para `'carta'`): convenio general de la app — si se amplía a otros tipos, debe verse y comportarse igual, cambiando solo la lista de elementos del checklist.

- **Sección propia en la modal de configuración**: dentro de la pestaña específica del tipo, `fieldset.modal__section` "Estilo de \<tipo\>" (variante meramente informativa, §12.6) con fila de dos botones `.style-actions-row` (`display: flex; gap: 0.5rem`, cada botón `.btn-cancel` con `flex: 1`) — "Copiar estilo" y "Pegar estilo" — y `p.modal__hint` debajo (`font-size: 0.75rem`, `color: var(--text-muted)`) explicando qué se copia/pega.
  - "Pegar estilo" se muestra `disabled` (con `title` indicando el motivo) mientras no haya nada copiado en la sesión — `.btn-cancel:disabled` mismo criterio genérico de deshabilitado (`opacity: 0.5; cursor: not-allowed`, sin `transform` en hover).
- **Modal de selección al copiar**: un único grupo fijo (no colección dinámica) con clases BEM de §12.5 (`element-selection-group`/`__select-all`/`__list`/`__item`), todos los ítems marcados por defecto, cada uno con nota auxiliar opcional a la derecha (`.element-selection-group__item-hint`, `font-size: 0.75rem`, `color: var(--text-muted)`, `margin-left: auto` — mismo criterio que `.resource-add__hint`) con el valor actual de ese elemento. Botón de confirmar deshabilitado si no queda ningún ítem marcado.
- **Confirmación de copia**: `ui/toast.js` (§12.1.1 — no modal, confirmación breve sin detalle que revisar) con texto "Estilo copiado".
- **Error al pegar**: si algo copiado ya no es válido en el proyecto (referencia a etiqueta/recurso eliminado), modal de error con cabecera estándar (`modal__header--error`/`modal__error-icon`, §12.1) y detalle en tabla — reutilizando **tal cual, sin CSS propio**, `.import-report-modal`/`.import-report-modal__table` (§12.4), columnas según el dominio (para "Copiar/Pegar estilo": Elemento/Referencia/Detalle).
  - Pegado todo o nada: cualquier incidencia, no se aplica ningún cambio al destino.
  - Solo botón "Cerrar" (sin acción alternativa de "continuar sin eso", a diferencia de `ui/importConversionErrorModal.js`).

Cualquier tipo de componente futuro que incorpore "Copiar/Pegar estilo": reutilizar este mismo patrón (sección, checklist, toast, modal de error), cambiando solo qué elementos aparecen en el checklist.

## 12.10 Grupo de botones icono-solo: opción única o interruptores combinables

Patrón compartido (`.align-group`/`.align-group__btn`, `ui/cardTextBoxModal.js`) para representar varias opciones con icono en vez de texto, en dos variantes con mismo marcado y mismos estados visuales.

- Contenedor `.align-group` (`display:flex; gap:0.25rem`) con un `.align-group__btn` por opción (botón cuadrado `32×32px`, icono SVG centrado `stroke="currentColor"`, `title`/`aria-label` como etiqueta accesible).
- Reposo: fondo `var(--bg-subtle)`. Hover: `var(--bg-hover)`. Opción activa (`.align-group__btn.active`): fondo `var(--accent-blue)`, texto/icono `var(--text-light)` — mismo lenguaje visual que `.modal__tab.active`, adaptado a botón cuadrado icono-solo.
- **Opción única** (alineación horizontal/vertical del texto dentro de un `TextBox` de carta): al pulsar un botón, se actualiza el dato asociado y se recalcula `active` en todos los botones del grupo — nunca más de una opción activa a la vez.
- **Interruptores independientes y combinables** ("Estilo de texto": Negrita/Cursiva/Subrayado de un `TextBox` de carta): cada botón representa su propio booleano y alterna solo su propia clase `active`, sin afectar a los demás — puede haber cualquier número activos a la vez, incluido ninguno.
- Distinto de un `<select>` nativo (opción activa destacada sin desplegar nada) y de un checklist (§12.5, pensado para listas dinámicas más largas, no 2-3 iconos fijos).
- Cualquier grupo icono-solo futuro: reutilizar este patrón — mismo criterio que `.resize-handle`, `.help-icon` o `.resource-add__menu`.

## 12.11 Título de cabecera editable

Patrón para el único texto editable in-place fuera de un modal/formulario (`ui/appTitle.js`): el `<h1>` de cabecera, cuyo texto libre (todo salvo la versión, nunca editable) se puede editar en cualquier momento en modo edición.

- **`.app-title--hoverable`** (modo edición, no editando): modificador sobre el `h1` — `cursor: pointer` (convención de §12.2, sin cursor específico propio), icono de lápiz (`.app-title__pencil`, SVG inline `stroke="currentColor"`) oculto por defecto (`opacity: 0`), mostrado solo con `:hover` (`opacity: 0.85`, transición `var(--transition-fast)`) — nunca visible de forma permanente (a diferencia de las insignias de candado/oculto de §12.3).
- **`.app-title--editing`** (modo edición, editando): sustituye el texto por `.app-title__input` — `<input type="text">` de estilo a medida (no el genérico de campo de formulario, para conservar tamaño/tipografía del propio `h1`: `font: inherit`, fondo `rgba(255,255,255,0.08)` sobre el degradado oscuro de cabecera, borde `2px solid var(--accent-blue)`, texto `var(--text-light)`) — seguido de `.app-title__version`, la versión en `var(--text-muted)`, sin interacción, fuera del propio `<input>`.
- En modo juego, o modo edición sin hover/edición activa: el `h1` no lleva ninguna de las dos clases — se comporta como el `h1` genérico (`01-tokens-visual.md` §3), sin cursor especial ni icono.

Cualquier título/etiqueta futuro que necesite edición in-place directamente sobre el elemento visible (en vez de abrir modal): reutilizar este criterio (hover discreto con icono, sustitución por `<input>` a medida del contexto, confirmación con blur/Enter).

## 12.12 Slider con marcas imantadas

Primer uso de este patrón en el proyecto: no había precedente de `<datalist>` ni de marcas de referencia sobre un `<input type="range">` antes de `ui/rotationSlider.js` (control de rotación -360º a 360º de `ui/imageAdjustModal.js`, `ui/cardShapeModal.js`, `ui/cardTextBoxModal.js` — ver `design/docs/architecture/05-ui-layer.md`). El signo del valor indica el sentido del giro (negativo antihorario, positivo horario); el centro de la pista (0º) no está en el extremo sino aproximadamente en el medio.

- Bloque `.rotation-field` (`div.modal__field.rotation-field`) con: `<label>`, pista (`.rotation-slider__track`) que superpone el `<input type="range">` y las marcas visuales (`.rotation-slider__marks` > `.rotation-slider__mark`, una por valor de referencia), etiquetas numéricas debajo (`.rotation-slider__labels`) y, a la derecha de la pista, campo numérico sincronizado (`.rotation-slider__value` > `<input type="text">` + `<span>`) — mismo patrón slider↔texto que "Zoom"/"Transparencia" de `ui/imageAdjustModal.js`.
- Marca activa: `.rotation-slider__mark--active` sobre la marca más cercana al valor actual, dentro del umbral de imán.
- **Umbral de imán como constante de módulo**, no un valor "mágico" disperso por el código: `ROTATION_SNAP_THRESHOLD_DEG` en `ui/rotationSlider.js`. Al arrastrar el slider, si el valor crudo cae a esa distancia o menos de una marca, se fuerza al valor exacto de la marca antes de propagarlo — no es solo guía visual, ajusta el dato real.
- Convive deliberadamente con dos acciones rápidas existentes sobre el mismo campo (`rotation`): el menú contextual (§12.8) ofrece "Girar 90° (horario)" (+90°) y "Girar 90° (antihorario)" (-90°), ambas cíclicas (al superar un extremo del rango, dan la vuelta al extremo opuesto: p.ej. de 360° pasa a -270°), sin relación de código con este slider — dos mecanismos de edición del mismo campo, uno rápido y cíclico, otro preciso y de rango completo.
- Cualquier control futuro que necesite "elegir un valor en un rango continuo, con referencias discretas hacia las que conviene alinearse": reutilizar este patrón en vez de un slider liso o un `<select>` de valores fijos.
