# Tipos de componente implementados

Ocho tipos. Alta siempre pasa por `ui/componentTypeModal.js` (lista de tipos disponibles, no desplegable) — al aceptar, se crea con `createDefaultComponent(type)` (`ui/componentModal.js`) con valores por defecto, se añade al estado, y se abre `ui/componentModal.js` sobre ese componente para configurarlo.

## `'texto'`

Primer tipo concreto. Sin fondo de imagen, tamaño automático por defecto.

| Propiedad | Tipo | Default | Descripción |
|---|---|---|---|
| `contenido` | string | — | Texto que se muestra |
| `tamañoFuente` | number | — | Tamaño en píxeles |
| `colorTexto` | string (hex) | negro | Color del texto |
| `colorFondo` | string (hex o vacío) | vacío (transparente) | Color de fondo |

## `'tableroSimple'`

Elemento cuadrado redimensionable a cualquier proporción, borde y fondo configurables. `width`/`height` fijados a `200px` por defecto (nunca tamaño automático). Nombre de tipo actual; guardados con el nombre anterior (`'tablero'`) se migran silenciosamente al cargar (`core/state.js`, `migrateTableroSimple`).

| Propiedad | Tipo | Default | Descripción |
|---|---|---|---|
| `bordeColor` | string (hex) | negro | Color del borde, `box-sizing: border-box` |
| `bordeGrosor` | number, px 1–20 | `2` | Grosor del borde |
| `biselado` | boolean | `true` | `true`: borde en dos tonos derivados de `bordeColor` (bisel/relieve, excepción de estilo — ver `design/docs/style/`). `false`: borde plano de un color |
| `sombra` | boolean | `true` | `true`: sombra de contacto nivel 1. `false`: plano sin sombra (clase `.board--sin-sombra`) |
| `fondoTipo` | `'colorPatron' \| 'imagen'` | — | Qué configuración de fondo está activa. Cambiar de una a otra no borra la configuración de la anterior — ambos bloques conviven en `properties` |
| `patronColor` | string (hex) | — | Color del patrón de cuadrícula |
| `patronGrosor` | number, px 1–20 | `1` | C |
| `patronForma` | `'cuadrada' \| 'hex-vertical' \| 'hex-horizontal'` | — | Forma de celda. `'hexagonal'` (valor legacy) se interpreta como alias de `'hex-horizontal'` al renderizar y se normaliza al guardar de nuevo |
| `patronFilas`, `patronColumnas` | number, 1–50 | — | Dimensiones de la cuadrícula |
| `imagenResourceId` | string \| null | `null` | Id de recurso tipo `'imagen'` como fondo (`background-size: cover`). No usa `component.image` |

Renderizado del patrón: cuadrículas cuadradas/rectangulares usan doble `linear-gradient` CSS (`background-size` = tamaño de celda, grosor = `patronGrosor`). Hexagonales dibujan un `<svg>` con un polígono por hexágono (`renderHexGrid` de `ui/componentRenderer.js`, parametrizada por orientación): `'hex-vertical'` = pointy-top (vértices arriba/abajo), `'hex-horizontal'` = flat-top (vértices izquierda/derecha).

Configuración de fondo se edita en sub-modales `ui/boardPatternModal.js` (color y patrón) y `ui/boardImageModal.js` (imagen).

## `'dado'`

Elemento siempre cuadrado (ancho = alto también al redimensionar), nunca tamaño automático. `width`/`height` fijados a `100px` por defecto. Lógica de sorteo/validación vive en `core/dice.js` (sin dependencias de otras capas: `getPosibleValores`, `getResultadoInicial`, `esResultadoValido`, `tirarDado`, `isListaValoresValida`).

| Propiedad | Tipo | Default | Descripción |
|---|---|---|---|
| `colorCuerpo` | string (hex) | gris neutro | Color del cuerpo |
| `colorNumeros` | string (hex) | negro | Color del resultado impreso |
| `modoCaras` | `'numeroMaximo' \| 'lista'` | — | Configuración activa. Cambiar de modo no borra el otro — ambos conviven |
| `numeroMaximoCaras` | number, 2–100 | `6` | En modo `'numeroMaximo'`: resultado entre 1 y este máximo |
| `listaValores` | string (valores separados por comas) | — | En modo `'lista'`: resultado es uno de estos valores literales. Requiere ≥2 valores no vacíos tras recortar espacios |
| `fuenteResourceId` | string \| null | `null` | Id de recurso tipo `'tipografia'` para el texto del resultado (elegido en `ui/diceFontModal.js`). `null` o recurso inexistente usa tipografía por defecto |
| `resultadoActual` | string | calculado | Resultado mostrado. Se recalcula cuando cambia la configuración de caras y deja de ser válido |

Renderizado (`ui/componentRenderer.js`): silueta 2D plana que varía según nº de resultados posibles (triángulo/cuadrado/rombo/decágono faceteado, helper `renderDiceSilhouette`). Profundidad no es parte del dibujo SVG: usa la propiedad general de componente `profundidad`/`colorExtrusion` (ver `01-component-model.md` "Campos generales"), aplicada como `filter: drop-shadow` apilado sobre el contenedor `.dice` — mismo mecanismo que el resto de tipos, `'dado'` nace con `profundidad: 4` por defecto para aproximar la sensación de grosor que antes daba el polígono duplicado. En modo juego: click lanza el dado (parpadeo ~1s entre resultados, gestionado dentro de `componentRenderer.js`, fija resultado vía `onDiceResult`); doble click abre `ui/diceResultModal.js` a tamaño grande (`onDiceOpenResult`). En modo edición: sin lanzamiento, se comporta como cualquier componente (redimensionado siempre fuerza cuadrado).

## `'documento'`

"Visor de documentos": hoja fondo blanco, borde fino, sin bisel ni sombra. `width`/`height` fijados a `240×320px` por defecto (nunca automático).

| Propiedad | Tipo | Default | Descripción |
|---|---|---|---|
| `tipoContenido` | `'texto' \| 'url'` | — | Configuración activa. Cambiar no borra la otra |
| `contenido` | string | — | Texto/HTML pegado por el usuario (usado si `tipoContenido === 'texto'`) |
| `formato` | `'markdown' \| 'html'` | `'markdown'` | Cómo interpretar `contenido` |
| `url` | string | — | Página externa a embeber (usado si `tipoContenido === 'url'`) |

Soporte: `core/markdown.js` (`markdownToHtml(text)`) envuelve la librería vendorizada `vendor/marked.js` (marked v18.0.6, MIT — CommonMark + GFM completo). `core/sanitizeHtml.js` (`sanitizeHtml(html)`, basada en DOM) elimina `<script>`, atributos `on...`, y `href`/`src` con `javascript:` — imprescindible porque `marked` no sanitiza su salida y el estado se guarda como HTML autocontenido.

`vendor/` es la única excepción a las capas de `INDEX.md` §2: código de terceros tal cual, sin modificación funcional — necesario porque el build no admite paquetes npm/CDN.

Render: con `tipoContenido === 'texto'`, se inserta `sanitizeHtml(formato === 'html' ? contenido : markdownToHtml(contenido))`. Con `tipoContenido === 'url'`, se embebe en `<iframe sandbox="allow-scripts allow-same-origin allow-popups">` con aviso superpuesto si no dispara `load` en 3s o dispara `error` (heurística best-effort). Contenido siempre ajustado al ancho del componente (scroll solo vertical).

## `'carta'`

Rectángulo de proporción configurable, diseñado con el "Editor visual" (`ui/visualEditorModal.js`, ver `05-ui-layer.md`) — mismo editor que `'tableroPersonalizado'`. Etiqueta visible "Carta/Ficha" (absorbe el caso de uso del tipo `'ficha'` retirado, ver `03-groups-resources.md`); identificador de datos sigue siendo `'carta'`. Creado con `width`/`height` = `180 × (180 / ratio(proporción por defecto))` px, `bloqueado: false` por defecto.

Redimensionado: mantiene proporción configurada para las cinco proporciones rectangulares (`ui/resizeHandle.js` usa `getProporcionRatio(props.proporcion)` de `core/cardProportions.js`) — único modo de cambiar proporción es editar esa propiedad, no arrastrar el manejador. Excepción: `proporcion === 'circular'` tiene redimensionado libre en ambos ejes, Shift fuerza 1:1; nace con ancho = alto al crearse o cambiar a esta proporción. Redimensionar en la mesa cambia solo el tamaño del marco: el contenido (imagen, formas, textos) no se reescala, puede quedar recortado por `overflow: hidden` si no cabe (mismo criterio que `'tableroPersonalizado'`).

Esquinas: `border-radius: 8px` para las cinco proporciones rectangulares/cuadrada, condicionado a `esquinasRedondeadas` (`border-radius: 0` si desmarcada) — salvo `proporcion === 'circular'` (`border-radius: 50%` fijo, sin condicionar a `esquinasRedondeadas`). Mismo condicional aplicado al lienzo de cada cara en `ui/visualEditorModal.js` y a la máscara de `ui/imageAdjustModal.js`.

| Propiedad | Tipo | Default | Descripción |
|---|---|---|---|
| `proporcion` | ver `CARD_PROPORTIONS` abajo | `'5:7'` | Proporción/forma de la carta |
| `medidasReales` | boolean | `true` (nuevas/migradas) | Interno, no editable: marca si `caraFrontal`/`caraTrasera` están en píxeles reales. Solo lo consulta la migración de `core/state.js` para no reprocesar |
| `esquinasRedondeadas` | boolean | `true` | Esquinas redondeadas (`8px`) o cuadradas (`0`). Solo se muestra su control (checkbox en `ui/visualEditorModal.js`) cuando la proporción es rectangular/cuadrada (`isRectShape`) — circular y hexagonal no la usan. "Copiar/Pegar estilo" la incluye junto con `proporcion` |
| `caraActual` | `'frontal' \| 'trasera'` | `'trasera'` | Cara mostrada. En modo juego, click la alterna (`onCartaFlip`), independiente de `bloqueado`. Cada volteo dispara feedback visual breve (`.carta--flip-feedback`), detectado por diferencia de datos vía `Map` de módulo `lastCaraById`, no por evento de click |
| `caraFrontal`, `caraTrasera` | objeto, mismo shape | — | Diseño de cada cara, propio de esa carta. Ver shape abajo |

`CARD_PROPORTIONS` (`core/cardProportions.js`): `'5:7'` (Poker vertical), `'7:5'` (Poker horizontal), `'tarot-h'` (Tarot vertical 70×120mm), `'tarot-v'` (Tarot horizontal 120×70mm), `'1:1'` (Cuadrada), `'circular'` (resize libre), `'hex-vertical'`/`'hex-horizontal'` (Hexagonal, resize ratio fijo), `'triangulo'`/`'triangulo-invertido'` (vértice arriba/abajo, caja 1:1, resize ratio fijo). Cada entrada lleva campo `shape`; `getCartaShapeCss(value, esquinasRedondeadas = true)` traduce a `borderRadius`/`clipPath`: rectangular/cuadrada → `border-radius: 8px` o `0`; circular → `50%`; hexagonales/triangulares → `clip-path` con polígono exacto (no afectadas por `esquinasRedondeadas`). Aplicado en `ui/componentRenderer.js`, `ui/visualEditorModal.js` y `ui/imageAdjustModal.js` (este último con su propio vocabulario de `shape`, polígonos duplicados a propósito). `core/cardProportions.js` expone también `isRectShape(value)`. Sombra de carta hexagonal/triangular usa `filter: drop-shadow` (clase `.carta--hex, .carta--triangle`), igual que `'dado'` para siluetas no rectangulares. Borde de grosor uniforme en triangulares usa `getTriangleInnerClipPath` (hermana de `getHexInnerClipPath`): escala desde el incentro real de cada variante (`TRIANGLE_GEOMETRY`, constante precalculada), a diferencia del hexágono regular cuyo incentro coincide con el centro de la caja.

### Shape de `caraFrontal`/`caraTrasera`

`{ imagenResourceId, ajusteImagen, formas: Forma[], textBoxes: TextBox[], bordeColor, bordeGrosor, transparenciaImagen, fondoTipo, colorFondo }`

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `imagenResourceId` | string \| null | `null` | Recurso de imagen de fondo de la cara |
| `ajusteImagen` | `{ zoom, posX, posY, rotation }` | — | Mismo shape que usa `ui/imageAdjustModal.js` en general |
| `formas` | `Forma[]` | `[]` | Ver shape `Forma` abajo |
| `textBoxes` | `TextBox[]` | `[]` | Ver shape `TextBox` abajo |
| `bordeColor` | string (hex) | negro | Borde de la carta completa para esa cara |
| `bordeGrosor` | number, px **0**–20 | `0` | `0` es válido = "sin borde" (a diferencia de `'tableroSimple'`). Línea simple sin bisel |
| `transparenciaImagen` | number, 0–100 | `0` (opaca) | Transparencia de la imagen de fondo (`opacity = 1 - transparenciaImagen/100`), independiente del color de fondo/textBoxes/borde. Solo con efecto si hay `imagenResourceId`; se reinicia a `0` al cambiar de imagen |
| `fondoTipo` | `'imagen' \| 'color' \| undefined` | — | Ausente y `'imagen'` se tratan igual (pinta `imagenResourceId` si existe, blanco si no) — a diferencia de `Forma`, donde `undefined` se trata como `'color'`. Cambiar de uno a otro no borra el que queda inactivo |
| `colorFondo` | string (hex o vacío) | — | Color liso de fondo si `fondoTipo === 'color'` |

Coordenadas (`x`/`y`/`width`/`height` de cada `Forma`/`TextBox`, `tamañoFuente` de cada `TextBox`) se guardan en píxeles reales, fijos con independencia del tamaño de la carta — mismo criterio que `'tableroPersonalizado'`. Cartas guardadas con el sistema anterior (lienzo abstracto de 300px reescalado por un factor uniforme) se migran una vez al cargar (`core/state.js`, `migrateCartaMedidasReales`, ver `06-persistence-build.md`).

**Orden de apilado dentro de una cara**: imagen de fondo siempre en el extremo inferior, fuera de cualquier orden. `formas` y `textBoxes` comparten un único orden de apilado mezclado (campo `orden` de cada elemento) — cualquier figura puede quedar por encima o debajo de cualquier cuadro de texto. `core/cardFaceElements.js` (módulo de datos puro) combina ambos arrays: `getOrderedFaceElements(cara)` devuelve la lista de fondo a frente (fallback en memoria para elementos sin `orden`, sin migrar datos); `bringElementToFront`/`sendElementToBack` fijan el `orden` de un elemento por encima/debajo de todos los demás de su cara. Reutilizado por `ui/visualEditorModal.js` y `ui/componentRenderer.js` → `paintCartaFace`.

**Menú contextual del lienzo** (`ui/visualEditorModal.js`, click derecho, reutiliza `ui/contextMenu.js`): sobre un elemento — "Copiar", "Pegar", "Eliminar" (sin confirmación), "Colocar arriba"/"Colocar abajo". En zona vacía — solo "Pegar". `generalItems`/`specificItems` admiten `disabled: boolean`.

- **Copiar/Pegar**: `copiedElement`, variable de módulo (`{ kind, data } | null`, sobrevive a cerrar/reabrir el editor, no persiste). "Copiar" guarda copia superficial (`{ ...element }`) sin `id`; copiar uno nuevo sustituye al anterior. "Pegar" siempre visible, `disabled: !copiedElement`; crea elemento con `id` nuevo en el punto de click (`screenToDesignPoint`), lo añade a `cara.formas`/`cara.textBoxes`, lo sube al frente, lo selecciona.
- Elementos nuevos ("Añadir elemento") y duplicados desde la modal de edición se colocan por encima de todos los demás de su cara.
- **Borrado con SUPR**: `handleKeyDown` de `visualEditorModal.js` gestiona `e.key === 'Delete'` (mismo valor que `ui/globalShortcuts.js`) — con elemento seleccionado y foco fuera de campo editable, lo elimina vía `removeElement` (misma función que "Eliminar" del menú).

### Shape `Forma`

`{ id, tipo: 'circular' | 'cuadrada' | 'redondeada', x, y, width, height, colorFondo, colorFondoTransparencia, fondoTipo: 'color' | 'imagen' | undefined, imagenResourceId, ajusteImagen, imagenTransparencia, bordeActivo, bordeColor, bordeGrosor, orden, rotation: number (-360-360) | undefined }`

Tercer tipo de elemento repetible dentro de una cara (junto a imagen de fondo única y `textBoxes`). Mismo comportamiento de interacción que `TextBox`: seleccionable, editable con doble click (`ui/cardShapeModal.js`), arrastrable, redimensionable, duplicable, eliminable, con el mismo menú contextual.

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `x`, `y`, `width`, `height` | number | — | Mismas unidades que `TextBox` (píxeles reales) |
| `orden` | number \| undefined | fallback si ausente | Menor = más adelante en el apilado. Ver "Orden de apilado" arriba |
| `rotation` | número entero, `-360`-`360` \| `undefined` | equivalente a `0` | Gira la figura completa (borde+relleno) sobre su centro (`transform: rotate`) — a diferencia de `ajusteImagen.rotation`, que solo rota la imagen de relleno. `x`/`y`/`width`/`height` no cambian al girar, el contenido puede recortarse. El signo indica el sentido: negativo antihorario, positivo horario. Conviven dos vías de edición: "Girar 90° (horario)"/"Girar 90° (antihorario)" del menú contextual (ciclan ±90° dando la vuelta al extremo opuesto del rango al superarlo) y el slider de rotación (`ui/rotationSlider.js`) dentro de `ui/cardShapeModal.js`, con marcas imantadas cada 90º (simétricas a ambos lados de 0) pero libre para cualquier ángulo intermedio |
| `tipo` | `'circular'\|'cuadrada'\|'redondeada'` | — | `'redondeada'`: esquinas curvas `border-radius: 8px` (`SHAPE_BORDER_RADIUS`) |
| `fondoTipo` | `'color'\|'imagen'\|undefined` | `undefined` ≈ `'color'` | Cambiar de uno a otro no borra el otro |
| `colorFondo` | string (hex o vacío) | vacío | Con `fondoTipo === 'color'` |
| `colorFondoTransparencia` | number, 0–100 | `0` (opaco) | Transparencia sobre `colorFondo` (`core/colorUtils.js` → `hexToRgba`). Solo con efecto y control habilitado si `colorFondo` no vacío |
| `imagenResourceId` | string \| null | `null` | Con `fondoTipo === 'imagen'`. Sustituye por completo a `colorFondo` al pintar (no se combinan) |
| `ajusteImagen` | `{ zoom, posX, posY, rotation }` | reinicia a `{ zoom:100, posX:50, posY:50 }` al elegir/cambiar imagen | Mismo shape que `cara.ajusteImagen` |
| `imagenTransparencia` | number, 0–100 | `0` (opaco) | Transparencia sobre la imagen de fondo (`fondoTipo === 'imagen'`), independiente de `colorFondoTransparencia` y del borde. Se reinicia a `0` al elegir/cambiar imagen; se conserva al cambiar `fondoTipo` a `'color'` y volver a `'imagen'`. Se ajusta desde el slider "Transparencia" dentro de "Ajustar imagen…" (`ui/imageAdjustModal.js`), no en el panel de edición de la figura |
| `bordeColor`, `bordeGrosor`, `bordeActivo` | hex / px 1–20 / boolean | negro / `2` / `true` | Borde simple (`border` CSS), sin bisel especial. Sección "Borde" en `ui/cardShapeModal.js` usa patrón toggle en el `<legend>` |

Al pintar, imagen se recorta al `tipo` de la figura (mismo `border-radius`) en contenedor interno `overflow: hidden`, borde por encima sobre el contenedor exterior. Cambiar `tipo` conserva `imagenResourceId`/`ajusteImagen` (independientes de `tipo`); duplicar/copiar-pegar los lleva también. Redimensión: `tipo === 'circular'` libre en ambos ejes, Shift fuerza 1:1; `'cuadrada'`/`'redondeada'` libre sin restricción. Cambiar a `'circular'` con `width !== height` iguala ambos al mayor (círculo perfecto). Se pinta en `ui/visualEditorModal.js` y `ui/componentRenderer.js` → `paintCartaFace`, sin `pointer-events` fuera del editor.

Botón "Añadir elemento" de cada cara (menú desplegable): "Elegir imagen…", "+ Texto", "Figura geométrica" (crea figura circular por defecto, centrada, lado `designWidth * 0.3`), "Color de fondo…" (abre `ui/cardBackgroundColorModal.js`, activa `fondoTipo = 'color'` en la cara). Las dos últimas opciones no añaden elemento repetible: son configuración única de la cara, mutuamente excluyente entre sí.

### Shape `TextBox`

`{ id, contenido, fuenteResourceId, tamañoFuente, color, x, y, width, height, bordeActivo, bordeColor, bordeGrosor, bordeTipo: 'continua'|'punteada', colorFondo, colorFondoTransparencia, alineacionHorizontal: 'izquierda'|'centro'|'derecha', alineacionVertical: 'arriba'|'centro'|'abajo', margenSuperior, margenDerecha, margenInferior, margenIzquierda, negrita, cursiva, subrayado, orden, rotation: number (-360-360) | undefined }`

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `bordeActivo`, `bordeColor`, `bordeGrosor`, `bordeTipo` | boolean/hex/px 1–20/enum | `false`/negro/`2`/`'continua'` | Borde propio del cuadro. Si `bordeActivo` es `false`, no se dibuja pero color/grosor/tipo se conservan |
| `colorFondo`, `colorFondoTransparencia` | hex o vacío / 0–100 | vacío / `0` | Fondo propio, detrás del texto. Transparencia vía `hexToRgba`, solo con efecto si `colorFondo` no vacío |
| `alineacionHorizontal`, `alineacionVertical` | enum | `'izquierda'` / `'arriba'` | Posición del texto en la zona interior del cuadro (tras descontar márgenes) |
| `margenSuperior/Derecha/Inferior/Izquierda` | number, px | `0` | Reducen la zona interior sin cambiar tamaño del cuadro. Sin negativos ni tope propio |
| `negrita`, `cursiva`, `subrayado` | boolean | `false` | Interruptores independientes y combinables, aplicados al contenido completo (no a rangos) |
| `orden`, `rotation` | igual que `Forma` | — | Misma semántica y disparadores (menú contextual "Girar 90° (horario)"/"Girar 90° (antihorario)" + slider de rotación en `ui/cardTextBoxModal.js`) que en `Forma` |

`core/textBoxLayout.js` (módulo puro) expone `getTextBoxLayoutStyle(textBox, scale)`: traduce alineación+márgenes a `{ justifyContent, textAlign, paddingTop/Right/Bottom/Left }` (últimos 4 ya escalados en `px`) — punto único reutilizado por `ui/componentRenderer.js` y `ui/visualEditorModal.js`, ambos aplicando el resultado sobre contenedor `display:flex; flex-direction:column; box-sizing:border-box`.

Todos los campos de `TextBox` son opcionales y sin migración: ausencia se comporta como el default de la tabla (sin cambio visual).

Cara sin `imagenResourceId` ni `textBoxes`: carta se muestra en blanco con la proporción configurada, sin aviso.

`core/cardProportions.js` expone `CARD_PROPORTIONS`, `getProporcionRatio(value)` (fallback `'2:3'`), `CARD_DESIGN_WIDTH = 300` (constante histórica, solo usada por la migración `migrateCartaMedidasReales` para conocer el ancho de referencia de cartas guardadas con el sistema de "unidades de diseño" anterior).

## `'mazo'`

Pila ordenada de cartas boca abajo. Concepto independiente de "Etiqueta" (puramente organizativo) — ambos conviven sin relación entre sí. Creado con `width`/`height` = `180 × 180/getProporcionRatio('5:7')` px (mismo tamaño de partida que "Carta/Ficha"), `bloqueado: true` y `subirAlMoverInteractuar: true` por defecto. No admite proporciones especiales: solo orientación "Vertical"/"Horizontal", que al cambiarse transpone `width`/`height` (no resetea a tamaño por defecto).

| Propiedad | Tipo | Default | Descripción |
|---|---|---|---|
| `cartaIds` | string[] | `[]` | Lista ordenada de ids de componentes `'carta'` en el mazo — índice `0` es la de arriba. Referencia en sentido mazo→carta |
| `orientacion` | `'vertical'\|'horizontal'` | `'vertical'` | Solo determina forma de la caja al crearse/transponer. Solo se muestra su control cuando `forma === 'rectangular'` |
| `forma` | `'rectangular'\|'circular'` | `'rectangular'` | Silueta de la caja, independiente de `orientacion`. `'circular'` recorta caja/contenido/zona de revelado en redondo (`border-radius: 50%`). Cambiar a `'circular'` iguala `width`/`height` al mayor de los dos |
| `disposicion` | `'arriba'\|'abajo'\|'derecha'\|'izquierda'` | `'derecha'` | Lado del mazo donde se pinta la "zona de revelado" y aparece la carta al sacarla (`getMazoRevealZoneRect`). Se muestra también con `forma === 'circular'` (a diferencia de `orientacion`) |
| `textoCartaRevelada` | string | `'Carta revelada'` | Texto pintado dentro de la zona de revelado. Cadena vacía es un valor válido: la zona se pinta sin texto |
| `caraCartaRevelada` | `'frontal'\|'trasera'` | `'frontal'` | Cara con la que queda mostrada la carta al sacarla del mazo (`computeSacarCartaDeMazo` fija `caraActual` a este valor) — `'frontal'` es boca arriba, `'trasera'` boca abajo |
| `imagenResourceId` | `string\|null` | `null` | Imagen propia del mazo, independiente del contenido de la pila. `null`: sin imagen propia, ver comportamiento de fallback abajo |
| `ajusteImagen` | `{ zoom, posX, posY, rotation }\|undefined` | — | Solo presente si hay `imagenResourceId`. Mismo shape que usa `ui/imageAdjustModal.js` en general |
| `transparenciaImagen` | `number, 0–100\|undefined` | `0` cuando está presente | Solo presente si hay `imagenResourceId`; se reinicia a `0` al elegir/cambiar imagen |

`core/deck.js` (módulo de datos puro) expone:
- `getCartaIdsEnAlgunMazo(components)`: `Set` con todos los ids referenciados por cualquier mazo.
- `shuffleCartaIds(cartaIds)`: Fisher-Yates + `Math.random()`, mismo generador que `core/dice.js`.
- `computeSacarCartaDeMazo(mazo, carta)`: función pura, calcula cambios de sacar una carta cualquiera de la pila (esté donde esté); la carta queda con `caraActual` igual a `properties.caraCartaRevelada` del mazo (fallback `'frontal'`).
- `getMazoRevealZoneRect(mazo)`: rectángulo de la "zona de revelado", pegada al lado indicado por `properties.disposicion` (fallback `'derecha'`).
- `rectsOverlap`: test de solape de rectángulos.

Mientras el id de una carta esté en `cartaIds` de cualquier mazo, esa carta **no se dibuja como componente independiente en la mesa, en ningún modo** (a diferencia de `oculto`, solo filtrado en modo juego) — `modes/play/playMode.js` y `modes/edit/editMode.js` excluyen esos ids con `getCartaIdsEnAlgunMazo`. Sigue apareciendo en el panel de Componentes sin filtrar.

`core/state.js` expone `sacarCartaDeMazo(mazoId, cartaId)` (usa `computeSacarCartaDeMazo`, aplica cambios con `replaceComponent`/`reorderComponent`, sube la carta extraída al frente) — vive en esta capa porque `ui/componentModal.js` también la necesita y `ui/*` no puede importar de `modes/*`.

**Renderizado**: reutiliza clase `.carta` para la caja (mismo radio/sombra), `border-radius` inline a `50%` si `forma === 'circular'`. Con `imagenResourceId` propio, se pinta siempre esa imagen (con su `ajusteImagen`/`transparenciaImagen`) vía `paintCartaFace(contentParent, { imagenResourceId, ajusteImagen, transparenciaImagen, fondoTipo: 'imagen' }, 1, width, height)`, sin relación con `cartaIds` — el mazo la muestra tenga o no cartas dentro. Sin `imagenResourceId` propio, se mantiene el comportamiento previo (fallback): pinta `caraTrasera` de la carta de arriba (`cartaIds[0]`) vía `paintCartaFace(contentParent, cara, renderScale, faceWidth, faceHeight)` — `renderScale = width / (cartaArriba.width || MIN_CARTA_WIDTH)` encaja el diseño real de la carta en la caja del mazo. Sin carta: placeholder neutro (`renderMazoEmptyPlaceholder`, icono SVG). Junto al mazo siempre se pinta la "zona de revelado" (`renderMazoRevealZone`, en ambos modos): recuadro decorativo pegado al lado indicado por `properties.disposicion` (`MAZO_REVEAL_GAP = 20px` de separación en los 4 casos), misma `forma` que el mazo, con el texto de `properties.textoCartaRevelada` (fallback `'Carta revelada'`). Sigue al mazo en vivo durante el arrastre (`handleMouseMove` recalcula `getMazoRevealZoneRect` con las coordenadas en curso, pasando también `properties` para respetar la disposición). Parámetro `onMazoDraw` de `renderComponentsOnTable`: click sobre el mazo lo invoca (exclusivo de `modes/play/playMode.js`). Pestaña "Específicas" (modo edición) organiza sus campos en tres secciones (`fieldset.modal__section`, ver `design/docs/style/03-modales-menus.md` §12.6): "Forma" (Forma, Orientación), "Cartas reveladas" (Disposición carta revelada, Texto carta revelada, Revelar carta) e "Imagen" (preview + "Elegir imagen…"/"Ajustar imagen…"/"Quitar imagen", mismos patrones de `ui/boardImageModal.js`/`ui/imageAdjustModal.js` que otros elementos del juego); "Ver contenido del mazo" queda fuera de cualquier sección. Desde 00212, ya no muestra ningún contador de cartas fijo/automático — quien quiera ver el número de cartas en Modo Juego debe activar "Mostrar título de componente" (`01-component-model.md`) con un texto que use la variable `{cards_current}` (p. ej. `"{cards_current} cartas"`), mecanismo genérico de los 8 tipos, no exclusivo de `'mazo'`.

**Menú contextual** (modo juego): mazo añade "Barajar" (`shuffleCartaIds`) y "Ver contenido..." (`ui/mazoContentModal.js`); carta añade "Meter en mazo..." (`ui/insertIntoMazoModal.js`) solo si existe al menos un mazo. Nº de cartas se muestra en `description.extra` del menú.

**`ui/mazoContentModal.js`**: lista todas las cartas del mazo (miniatura de cara frontal + id + botón "Sacar" por fila, orden de `cartaIds`), reutilizada desde menú contextual (modo juego) y desde pestaña específica del mazo (modo edición). Lee siempre el estado actual de `core/state.js` para refrescarse tras cada "Sacar" — mutación la hace quien abre, vía `onSacar(cartaId)`.

**`ui/insertIntoMazoModal.js`**: desplegable de mazos + desplegable de posición ("Arriba del todo"/"Abajo del todo"); `onAccept({ mazoId, posicion })` añade el id de la carta al principio o final de `cartaIds`.

**Arrastrar cartas sobre un mazo** (modo juego y modo edición): `onMove` de `renderComponentsOnTable` (compartido por ambos modos) detecta solape entre la carta/selección bajo arrastre y un mazo. En modo juego (una sola carta, sin `confirm()`): inserción directa al final de `cartaIds` al soltar. En modo edición (puede ser selección múltiple de solo cartas): `attemptDropOnMazo(groupIds, draggedRect)` pide `confirm()` nativo antes de añadir al final; acción reversible. Detección de solape utiliza `rectsOverlap` en ambos modos. Resaltado visual (contorno azul + halo) se aplica mientras se arrastra sobre el mazo, en ambos modos, mientras la selección sea compuesta solo por cartas (no se resalta si hay mezcla de tipos de componente).

## `'tableroPersonalizado'`

Tablero avanzado, convive con `'tableroSimple'` (ninguno sustituye al otro) para cuando hace falta más que color/patrón/imagen única. Se diseña con el mismo "Editor visual" (`ui/visualEditorModal.js`) que `'carta'`, pero con una única cara (no se voltea) bajo `properties.cara` (mismo shape que `caraFrontal`/`caraTrasera` de `'carta'`: `imagenResourceId`, `ajusteImagen`, `formas`, `textBoxes`, `bordeColor`, `bordeGrosor`, `transparenciaImagen`). Creado con `width`/`height` = `300 × 200px` por defecto (nunca automático); a diferencia de `'carta'`, redimensionado libre en cualquier proporción (como `'tableroSimple'`).

| Propiedad | Tipo | Default | Descripción |
|---|---|---|---|
| `cara` | objeto (mismo shape que cara de `'carta'`) | — | Diseño único |
| `biselado` | boolean | `true` | Nivel superior (no dentro de `cara`). Decide si el borde tiene bisel de dos tonos o color plano |
| `sombra` | boolean | `true` | Nivel superior. Sombra de contacto nivel 1 o plano (`.tablero-personalizado--sin-sombra`) |

Diseño de la cara se guarda directamente en píxeles reales, fijo con independencia del tamaño del componente: pintado (`ui/componentRenderer.js` → `paintCartaFace(tableroContent, cara, 1, width, height, 1)`) usa siempre escala `1`, `overflow: hidden` recorta lo que no quepa — redimensionar cambia solo el marco visible. El lienzo del Editor visual representa el tamaño real del componente al abrirlo (no un lienzo lógico fijo). Borde usa el mismo bisel de dos tonos que `'tableroSimple'`/`'dado'` (`core/colorUtils.js` → `shadeColor`) en vez del borde simple de `'carta'`. Sin bloque "Estilo" (Copiar/Pegar estilo) en esta versión.
