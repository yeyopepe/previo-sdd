# Style Bible — índice

Convenciones de estilo vigentes de la app en `/src` (`src/styles/main.css` + `src/ui/*.js` + `src/modes/*`). Toda UI nueva sigue estas reglas.

Arquitectura técnica general (capas, modelo de datos, build): ver `design/docs/architecture/INDEX.md`.

## 1. Stack de estilos

- CSS plano, un único fichero: [main.css](../../src/styles/main.css). Sin preprocesador ni CSS-in-JS.
- DOM construido con JS vanilla (`document.createElement`, `className`, `classList`). Sin framework de componentes.
- Ficheros en `src/ui/*.js` = los "componentes".
- No añadir dependencias de UI (React, Tailwind, etc.) sin acordarlo antes. App = vanilla JS + CSS plano.

## 7. Nomenclatura de clases — BEM

Convención: `bloque__elemento--modificador`.

- Bloque en kebab-case: `.component-list`, `.modal`, `.infinite-table`, `.edit-mode-panel`, `.help-icon`, `.board`, `.board-image-modal`, `.component-type-modal`. Nombres en inglés, sin relación con el identificador `'tableroSimple'` del tipo de componente — no se renombran al renombrar ese tipo.
- Elemento con doble guion bajo: `.component-list__item`, `.modal__header`, `.modal__tabs`, `.modal__field`, `.infinite-table__world`, `.help-icon__tooltip`.
- Modificador con doble guion: `.text-box--selectable`, `.text-box--movable`, `.modal__field--checkbox`.
- Estados transitorios (no BEM, clases simples añadidas/quitadas por JS): `.grabbing`, `.active`, `.lifted`, `.drop-target`.
  - Sin prefijo de bloque, usadas tal cual.
  - Siempre junto a `classList.add/remove`, nunca reemplazando `className` entero.
  - Excepción: `.carta--flip-feedback` sí lleva prefijo `carta--` pese a ser transitorio — describe un estado exclusivo de ese bloque, no genérico como `.lifted`.
  - `.is-copy`: mismo criterio "sin prefijo del bloque" aunque no es transitorio (se mantiene mientras `component.copyOf` no sea `null`). Transversal a los 7 tipos de componente. Añadida por `ui/componentRenderer.js` junto a la clase `--selectable` propia del tipo. Usada por `main.css` para pintar en rojo el contorno de selección y `.component-id-label` (ver `03-modales-menus.md` §12.3).
  - `.is-group-passenger`: mismo criterio que `.is-copy` (sin prefijo de bloque, transversal a los 7 tipos, añadida por `ui/componentRenderer.js` junto a `--selectable`/`--selected`). Se aplica cuando el componente pertenece a un grupo (`groupId` no nulo, ver `design/docs/architecture/04-modes.md`, "Grupos en modo edición") y está seleccionado como pasajero — arrastrado a la selección por pertenecer al grupo, sin haber sido el objetivo directo del click. `main.css` la pinta en gris (`var(--text-muted)`) en vez del azul/rojo habitual, sin variante de `:hover` (solo aplica junto a `--selected`). Si coincide con `.is-copy` sobre el mismo elemento, gana `.is-group-passenger` (declarada después en la cascada).
- Excepción histórica (no siguen BEM): `.btn-cancel`, `.btn-accept`, `.btn-eliminar`.
  - Nuevas variantes de botón standalone (no ligadas a un bloque existente): usar patrón `.btn-<intención>`.
  - `.btn-duplicate`: mismo aspecto que `.btn-cancel` (fondo/color/hover/disabled idénticos). Usado cuando un footer de modal necesita una acción no destructiva/no primaria distinta de "Cancelar" — permite a `ui/globalShortcuts.js` localizar el "Cancelar" real sin ambigüedad al pulsar ESC (`querySelector('.modal__footer .btn-cancel')`).
  - `.btn-sacar` (`ui/mazoContentModal.js`): botón pequeño por fila de `.mazo-contenido__item`. Fondo `var(--bg-subtle)`, hover `var(--accent-blue)`/texto claro — mismo criterio que `.context-menu__item:hover`.
- Botón que pertenece a un bloque ya existente (p. ej. fila de `.component-list`): no usa la excepción `.btn-*`. BEM normal con modificador: `.component-list__action-btn--danger`.
- IDs (`#mode-switcher`, `#content`, `#app-version`, `#edit-toolbar`): reservados a contenedores de layout únicos en `index.html`. Nunca para componentes reutilizables.

## 8. Patrones de componente (JS)

Cada "componente" = función que crea y devuelve un `HTMLElement` vía `document.createElement`, asigna `className` una vez en la creación, usa `classList.add/remove/toggle` solo para estados dinámicos posteriores.

```js
const modal = document.createElement('div');
modal.className = 'modal';
```

Ver forma completa en [componentModal.js](../../src/ui/componentModal.js).

- Un fichero por componente en `src/ui/`, camelCase (`componentList.js`, `componentModal.js`, `table.js`).
- Estados de UI (tab activa, arrastrando, seleccionable): siempre clase, nunca estilo inline.
- No usar `style.xxx =` desde JS para nada expresable como clase/token CSS.
  - Excepción legítima: transforms dinámicos calculados (p. ej. pan/zoom de `.infinite-table__world`) — valor puramente numérico, sin sentido como clase.

**Campo de color + grosor asociado, misma fila.** Cuando un modal tiene color y grosor conceptualmente ligados (borde/trazo), van en la misma fila, no apilados.

- Patrón: `componentModal.js` (borde de tablero), `cardEditorModal.js` (borde de cada cara de una carta).
- Estructura: `div.modal__field` exterior → `div` interior (`style.display='flex'; style.gap='0.5rem'`) → dos sub-`div` con `style.flex='1'` (color primero, grosor después).
- Única excepción admitida a "no `style.xxx=` desde JS": layout puntual a ese par de campos, no un estado/valor reutilizable como clase.
- **Precaución en contenedor de ancho variable/acotado**: los campos `flex:1` contienen `<input>` con `width:100%`. Si el contenedor no tiene ancho explícito en toda la cadena de ancestros (p. ej. columna dimensionada por su contenido, como cada cara de `cardEditorModal.js`), el `100%` no resuelve y el navegador cae al ancho nativo del `<input>` (mucho mayor de lo esperado). Solución: el contenedor de la fila fija su propio ancho explícito (`cardEditorModal.js` usa `faceCol.style.width` con el mismo valor calculado para el lienzo de la carta).
- **Extensión a N campos numéricos relacionados**: mismo patrón de fila (`display:flex; gap:0.5rem`, un sub-`div` por campo `flex:1`) cuando son más de 2 campos numéricos relacionados. Ejemplo: `ui/cardTextBoxModal.js`, fila de 4 campos "Arriba"/"Derecha"/"Abajo"/"Izquierda" (márgenes de `TextBox`, `<input type="number" min="0">` cada uno) — una sola fila de 4, no dos filas de 2.

## 13. Qué NO hacer

- No introducir un segundo sistema de tokens de color (Tailwind, otra paleta) — extender `:root` en `main.css`.
- No mezclar `style="color:#..."` inline para colores del catálogo de tokens (`01-tokens-visual.md` §2).
- No crear clases de un solo uso sin BEM salvo que encajen en la excepción `.btn-*`.
- No añadir degradados llamativos (más allá del degradado sutil ya existente del header) ni animaciones/transiciones complejas (`@keyframes`, animaciones narrativas).
  - Sombras y radios sí están permitidos: siguen siempre el sistema de elevación (`01-tokens-visual.md` §6) y la escala de radios (`01-tokens-visual.md` §5), nunca un valor ad-hoc por componente.

### Bisel/profundidad — "Tablero simple", "Tablero personalizado", "Dado"

Complementario a su sombra de contacto.

- `'tableroSimple'` (`ui/componentRenderer.js`): simula relieve en el borde repartiendo el color elegido en dos tonos (más claro arriba/izquierda, más oscuro abajo/derecha), calculados con `shadeColor` (`core/colorUtils.js`). Sin sombra ni degradado — la sombra de contacto (`.board`, nivel 1) es un `box-shadow` CSS aparte, no calculado por este helper.
- `'dado'` (`ui/componentRenderer.js`, `renderDiceSilhouette`): dibuja solo silueta principal, contorno fino y líneas internas de faceteado (4/8/9+ resultados), todo con `shadeColor` — ya no dibuja profundidad como polígono SVG duplicado. Profundidad/extrusión de `'dado'` pasa a ser "un tipo más" de la propiedad general `profundidad`/`colorExtrusion` (ver "Extrusión configurable", `01-tokens-visual.md` §6), aplicada como `filter: drop-shadow` apilado sobre el contenedor `.dice`. Su sombra de contacto (`.dice`) sigue usando `filter: drop-shadow` (silueta no rectangular), independiente de la extrusión.
- `'tableroPersonalizado'`: mismo criterio de dos tonos que `'tableroSimple'` (`.tablero-personalizado`, misma sombra nivel 1).
  - Diferencia con "Carta" (comparten el mismo editor visual `ui/visualEditorModal.js` pero no este tratamiento): parámetro `borderStyle: 'bisel'` reutiliza `shadeColor` para el borde del lienzo de diseño, en vez del borde simple de `'carta'` (`borderStyle: 'simple'`).
- Técnica acotada a estos tres tipos — no se aplica a ningún otro tipo salvo decisión explícita.
- En `'tableroSimple'` y `'tableroPersonalizado'` (no en `'dado'`, siempre biselado) el bisel es opcional: propiedad `biselado` (boolean, `true` por defecto), checkbox "Biselado en el borde" en sección "Visual" (informativa, primera de la pestaña de propiedades específicas, ver `03-modales-menus.md` §12.6).
  - Desmarcado: pinta el mismo `bordeColor` en los cuatro lados sin repartir en dos tonos (no omite la propiedad).
  - Puntos donde se aplica: la mesa (`ui/componentRenderer.js`, ambos tipos) y, para `'tableroPersonalizado'`, la previsualización del lienzo en el Editor visual (`ui/visualEditorModal.js`, parámetro `bevelEnabled` de `openVisualEditorModal`, leído una vez al abrir el editor).

### Esquinas redondeadas de "Carta"

- `'carta'` (`ui/componentRenderer.js`, `.carta` en `main.css`) usa `var(--radius-lg)` como base en la clase CSS — mismo radio que "contenedores destacados" (`.modal`, paneles flotantes). No es un valor especial.
- Para las cinco proporciones rectangulares/cuadrada: `8px` (`var(--radius-lg)`) es el resultado por defecto de la propiedad `esquinasRedondeadas` (boolean; ver `design/docs/architecture/02-component-types.md`, tipo `'carta'`), aplicado como estilo inline (`getCartaShapeCss`, `core/cardProportions.js`) — prioridad sobre la clase.
- Checkbox "Esquinas redondeadas" (`ui/visualEditorModal.js`, toolbar junto al selector de Proporción, solo visible si `showProporcionSelector` es `true`, es decir solo para `'carta'`) desmarcado → `border-radius: 0`.
- Circular y Hexagonal no se ven afectadas: mantienen recorte fijo (`50%`/`clip-path`).
- Reutiliza `.modal__field--checkbox` tal cual (mismo patrón que "Bloqueado"/"Oculto" en `ui/componentModal.js`) — sin patrón visual nuevo.
- Carta lleva también sombra de contacto nivel 1 (igual que el resto de piezas de juego), sin verse afectada por esta propiedad.

### "Mazo" reutiliza la clase `.carta`

- `'mazo'` (`ui/componentRenderer.js`): sin bloque BEM nuevo para su caja — al ser visualmente "una carta boca abajo", reutiliza `.carta` tal cual (mismo `--radius-lg`, misma sombra nivel 1, mismos modificadores `--selectable`/`--selected`/`--movable`).
  - Añade solo `.mazo--clickable` (cursor de "sacar carta", equivalente a `.carta--clickable`/`.dice--clickable`).
- `.mazo-reveal-zone` ("zona de revelado"): bloque propio, no comparte aspecto con `.carta` — recuadro con borde punteado `var(--border-neutral)`, texto `var(--text-muted)`, `pointer-events: none`. Mismo tono neutro que una fila informativa de solo lectura (`.context-menu__info-row`, ver `03-modales-menus.md` §12.8).
- `.btn-sacar` (`ui/mazoContentModal.js`): botón standalone que no cuelga de ningún bloque BEM existente (excepción histórica de §7).

### Forma circular de "Mazo"

- Propiedad `forma` de `'mazo'` fija `border-radius: 50%` inline cuando vale `'circular'` — prioridad sobre `var(--radius-lg)` de la clase `.carta`. Mismo mecanismo que la proporción `'circular'` de "Carta", no una excepción nueva.
- Se aplica a la caja del mazo y a su contenido interior recortado (reverso de la carta de arriba, o icono de "mazo vacío").
- Sombra de contacto: sin tratamiento especial (a diferencia de siluetas hexagonales de "Carta") — `box-shadow` ya sigue el `border-radius` del elemento, proyecta sombra circular automáticamente.
- `.mazo-reveal-zone` adopta el mismo criterio: `border-radius: 50%` inline si el mazo es circular, en vez de `var(--radius-sm)` por defecto.

### Miniatura de carta de la modal "Contenido del mazo"

- `.mazo-contenido__thumb` (`ui/mazoContentModal.js`, bloque `.mazo-contenido__item`): miniatura ajustable de la cara frontal de cada carta en la lista de la modal "Ver contenido del mazo" (origen: menú contextual del mazo en Modo Juego o pestaña del mazo en Modo Edición).
  - Dimensiones: ancho y alto reales de la carta, escalados proporcionalmente para caber en máximo `THUMB_MAX_WIDTH` × `THUMB_MAX_HEIGHT` (42 × 58 píxeles).
  - Forma: reutiliza `getCartaShapeCss` (`core/cardProportions.js`) para aplicar el mismo `border-radius` y `clip-path` de la carta real según su `proporcion` (rectangular con esquinas redondeadas por defecto, circular, hexagonal, triangular).
  - Borde: neutro decorativo de "slot" (`1px solid var(--border-neutral)`) solo en proporciones rectangulares/cuadrada (donde `clip-path: 'none'`). En proporciones hexagonal y triangular (`clip-path` activo) se omite, porque `border` CSS no sigue la silueta recortada — diseño coherente con que la carta real sobre la mesa tampoco simula borde de grosor uniforme en esas proporciones (ese mecanismo de dos capas anidadas es propio del borde de color elegible de la carta, no aplicable aquí).

### Recorte hexagonal de "Carta"

- Proporciones `'hex-vertical'`/`'hex-horizontal'`: no usan `var(--radius-lg)` ni `border-radius: 50%` — recorte con `clip-path` (polígono exacto de hexágono regular, vértices agudos sin bisel ni redondeo). Única forma de conseguir silueta de aristas rectas.
- Se aplica en tres puntos: carta sobre la mesa (juego/edición), lienzo de cada cara en el editor de cartas, máscara de ajuste de imagen.
- Sombra de contacto: no puede ser `box-shadow` (seguiría la caja rectangular, no el hexágono) — usa `filter: drop-shadow` (clase `.carta--hex`), mismo criterio que `.dice`.

**Borde en proporciones hexagonales.**

- El borde tampoco puede pintarse con la propiedad CSS `border` (siempre paralela a la caja rectangular; al recortar con `clip-path` el corte atraviesa el borde en ángulo en vez de seguir las aristas).
- Solución (`ui/componentRenderer.js`, `ui/visualEditorModal.js`): dos capas de `clip-path` anidadas y concéntricas.
  - Capa exterior: rellena del color de borde, recortada con el hexágono completo.
  - Capa interior: contenido (imagen, cuadros de texto), recortada con hexágono más pequeño.
  - El hueco entre ambas = borde, grosor uniforme.
- Hexágono interior calculado con `getHexInnerClipPath` (`core/cardProportions.js`): el `ratio` de estas proporciones fuerza siempre hexágono regular, así que desplazar las seis aristas hacia dentro una distancia constante equivale a escalar los vértices desde el centro por un factor obtenido de la apotema (`width/2` en `'hex-vertical'`, `height/2` en `'hex-horizontal'`).
- Técnica acotada a estas dos proporciones — el resto sigue usando `border` CSS normal (caja y silueta visible coinciden).

### Recorte y borde triangulares de "Carta"

- Proporciones `'triangulo'`/`'triangulo-invertido'`: mismo mecanismo que las hexagonales.
  - Recorte por `clip-path` (silueta de aristas rectas, no triángulo estrictamente equilátero — ocupa ancho y alto completos de la caja cuadrada, ver `design/docs/architecture/02-component-types.md`).
  - Sombra de contacto con `filter: drop-shadow` (clase compartida `.carta--hex, .carta--triangle` en `main.css` — mismo motivo: silueta no rectangular no puede proyectar `box-shadow`).
  - Borde mediante dos capas de `clip-path` anidadas.
- Diferencia técnica: cálculo del recorte interior.
  - Hexágono regular: incentro coincide con el centro de la caja (`50%, 50%`), inradio = mitad del lado.
  - Este triángulo: incentro **no** está en el centro de la caja. `getTriangleInnerClipPath` (`core/cardProportions.js`, hermana de `getHexInnerClipPath`, no una generalización) escala desde el incentro real de cada variante (`TRIANGLE_GEOMETRY`, fórmulas estándar de incentro/inradio a partir de los vértices).

### Color dedicado al título de `.modal__section`

- Token `--section-accent` (`#5b5f97`): uso exclusivo en el texto del `<legend class="modal__section-title">` de una sección encuadrada (ver `03-modales-menus.md` §12.6).
  - No en ningún otro elemento, ni en el marco del `fieldset` (usa `--border-neutral` estándar).
- No reutiliza `--accent-blue`/`--accent-blue-dark` (en el resto de la app significan "interactivo/seleccionado": botón "Aceptar", contorno de selección, tab activa) — un título de sección no es interactivo.
- Excepción acotada a este único uso — no reutilizar `--section-accent` para otro fin sin decisión explícita.

### Parpadeo y temblor de la tirada del dado — no son animación CSS

- Efecto de "tirada" de `'dado'` (~1s de resultados aleatorios cambiando rápido antes de fijar el resultado final, `ui/componentRenderer.js`): cambio repetido de `textContent` mediante temporizador JS (`setInterval`/`setTimeout`), sin `transition` ni `@keyframes`.
- Temblor (pequeño desplazamiento aleatorio del dado durante ese mismo segundo): mismo temporizador, recalcula `transform: translate()` en cada tick — valor puramente numérico en JS, misma excepción documentada en §8 para transforms dinámicos (pan/zoom de la mesa), no animación/transición CSS.
- Ninguno de los dos entra en la prohibición de animaciones complejas de esta sección ni requiere excepción propia.

### Efecto "levantar" al arrastrar en Modo Juego

Integrado en el sistema de elevación (ver `01-tokens-visual.md` §6).

- Estado transitorio `.lifted` (`src/styles/main.css`), añadido/quitado por `ui/componentRenderer.js` (`beginDragLift`/`endDragLift`).
- Solo cuando `renderComponentsOnTable` recibe `liftOnDrag: true` (exclusivo de `modes/play/playMode.js`, nunca de `modes/edit/editMode.js`).
- Aplica desplazamiento fijo (`transform: translate(-2px, -4px)`) y sombra (`box-shadow: 6px 7px 9px 2px rgba(0,0,0,0.35)`) mientras se arrastra — simula que el componente se levanta y vuelve a apoyarse al soltar.
- Transiciona con `var(--transition-fast)`, simétrico al levantar y al soltar — no instantáneo.
- No reabre la prohibición general de animaciones complejas (`@keyframes`, narrativas): sigue aplicando sin cambios al resto de casos (temblor/parpadeo del dado, contorno `--selectable`/`--selected`).
- Es el estado "en el aire" del mismo sistema de elevación que usan en reposo el resto de piezas — acotado únicamente a este estado transitorio y este gesto (arrastre en Modo Juego).

### Resaltado de zona de suelta en mazo — "Mazo" durante arrastre de carta

Estado transitorio mientras una carta (o selección de solo cartas, en Modo Edición) se arrastra sobre un mazo.

- Estado transitorio `.drop-target` (`src/styles/main.css`), añadido/quitado por `ui/componentRenderer.js` (`updateMazoDropHighlight`/`clearMazoDropHighlight`) sobre el elemento del `'mazo'`.
- Aplica en ambos modos (Juego y Edición) por igual — vive en el punto de renderizado compartido (`renderComponentsOnTable`).
- Disparo: cuando el rectángulo de la carta bajo arrastre solapa con un mazo (mismo criterio de solape que el drag&drop de inserción). Solo se resalta si la selección arrastrada contiene únicamente cartas (en Modo Juego es siempre una sola carta, en Modo Edición puede ser selección múltiple si todas son cartas; si la selección mezcla tipos de componente, no se resalta nada).
- Contorno sólido azul + halo (`outline: 3px solid var(--accent-blue)` + `box-shadow` con `var(--accent-blue-light)`) — visualmente distinto del contorno discontinuo de selección (`.carta--selected`, `dashed`), para no confundir la semántica "zona de suelta" con "elemento seleccionado".
- Se retira siempre al soltar el ratón, se inserte o no la carta en el mazo — la mesa se redibuja completamente si se ejecuta la inserción de todos modos.

### Feedback de volteo de "Carta"

Segundo estado transitorio distinto de `.lifted`.

- Estado `.carta--flip-feedback` (`src/styles/main.css`): confirma visualmente que una carta cambió de cara (click sobre `'carta'` en Modo Juego, `onCartaFlip`).
- A diferencia de `.lifted`, no se añade/quita desde el código de arrastre (`mousedown`/`mousemove`/`mouseup`).
  - `ui/componentRenderer.js` detecta el volteo por diferencia de datos: compara `caraActual` actual de cada carta contra la última vista, en un `Map` de módulo propio (`lastCaraById`), ajeno a cualquier estado de arrastre.
  - Se aplica/retira al crear el nodo en cada render, con `setTimeout` propio (`flipFeedbackTimeouts`) — necesario porque `onCartaFlip` dispara un re-render síncrono que ya destruyó el nodo original antes de que pudiera verse cualquier clase añadida.
- Aplica desplazamiento vertical + ligera escala (`transform: translate(0, -6px) scale(1.03)`) junto a `box-shadow: var(--shadow-2)`, transicionando con `var(--transition-fast)` igual que `.lifted`.
- No sustituye ni reutiliza `.lifted`: estados independientes, sin variables ni rutas de código compartidas, no coexisten en la práctica (un click sin arrastre nunca activa el lift).
- No reabre la prohibición general de animaciones complejas: sin `@keyframes` ni animaciones narrativas.

## Ficheros hermanos

| Fichero | Cubre |
|---|---|
| `01-tokens-visual.md` | Design tokens (`:root`), tipografía, espaciado, bordes/esquinas, elevación/sombra/transición |
| `02-componentes-layout.md` | Botones, layout general (columna flex, z-index de overlays), redimensionado (manejador de esquina), cabecera de tabla fija (`sticky`) |
| `03-modales-menus.md` | Icono de ayuda, modales de error/éxito, cursores, etiquetas/insignias de componente, modales anchas, botón maximizar, checklist agrupado, secciones dentro de pestañas, menú desplegable de acciones, menú contextual, copiar/pegar estilo, grupo de botones icono-solo, título de cabecera editable, slider con marcas imantadas |
