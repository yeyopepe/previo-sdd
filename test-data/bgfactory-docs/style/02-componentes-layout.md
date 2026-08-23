# Botones, layout, redimensionado, cabecera de tabla fija

Ver `INDEX.md` para el mapa completo de la Style Bible.

## 9. Botones

Todos los botones comparten esta base (adaptar fondo/borde según contexto):

```css
padding: 0.5rem 1rem;   /* o 0.25rem 0.5rem si es un botón pequeño dentro de un item */
border: none;           /* o 1px solid var(--text-light) sobre fondo oscuro */
border-radius: var(--radius-sm);
cursor: pointer;
font-size: 0.875rem;    /* o 0.75rem si es pequeño */
transition: background var(--transition-fast), opacity var(--transition-fast);
```

- Acción primaria: fondo `var(--accent-blue)`, texto `var(--text-light)`. Hover: `opacity: 0.9` + `transform: translateY(-1px)` + `box-shadow: 0 3px 8px rgba(44,125,216,.35)`.
- Acción secundaria/cancelar: fondo `var(--bg-subtle)`, texto `var(--text-primary)`. Hover: `var(--bg-hover)` — solo transición de `background`, sin `transform`.
- Acción destructiva (eliminar/borrar): fondo `var(--error)`, texto `var(--text-light)`. Hover: `opacity: 0.9` + `transform: translateY(-1px)` + `box-shadow: 0 3px 8px rgba(211,47,47,.3)` — mismo tratamiento que primaria, cambia solo color de fondo/sombra.
  - Aplica a `.btn-eliminar` (modales) y al modificador BEM `--danger` (p. ej. `.component-list__action-btn--danger`).
  - Cualquier acción que elimine un elemento usa este color en toda la app, nunca el azul primario.
- Botón sobre fondo oscuro (toolbar): transparente, borde `1px solid var(--text-light)`. Hover: `rgba(255,255,255,0.1)` con transición de `background`, sin `transform`.
- Deshabilitado: `opacity: 0.5; cursor: not-allowed`, sin `transform` en hover.
- Sin `:active` — feedback de interacción es el cambio de `opacity`/`background`/`box-shadow`/`transform` en `:hover`, con transición de 150ms (`var(--transition-fast)`).
- **Botón icono-solo** (acción sin texto visible): icono SVG con `stroke="currentColor"` (hereda color de texto/borde del contexto), siempre con `title`/`aria-label` como etiqueta accesible.
  - Dentro de un botón de barra ya existente (p. ej. `.edit-toolbar button`): mismo padding/tamaño que los botones con texto de ese bloque — solo cambia el contenido.
  - Botón flotante cuadrado independiente (p. ej. `.mode-switcher__fit-btn`): `padding: 0`, ancho/alto fijo (`36px`), icono centrado (`display: inline-flex; align-items: center; justify-content: center`), mismo fondo/color de acción primaria del contexto.
- **Botón de texto completo en espacio reducido**: cuando un botón con texto va encajado entre elementos estrechos (no en fila de acciones holgada) — p. ej. `.card-editor-modal__adjust-image`, entre las dos caras de una carta — usa `padding: 0.5rem 0.75rem` como variante intermedia entre el estándar (`0.5rem 1rem`) y el pequeño de item (`0.25rem 0.5rem`). Reutilizar `0.75rem` en vez de introducir un cuarto valor ad-hoc.

## 10. Layout

- App = columna flex de altura completa: `html, body { height: 100% }`, `body { display:flex; flex-direction:column; height:100vh }`. Header fijo (`h1`, `3.5rem`) + `#content` flexible (`flex: 1 1 auto; min-height: 0`).
- Paneles laterales de ancho fijo: `400px` (`.component-list`, `.edit-mode-panel`).
- Posición inicial por defecto de paneles flotantes del modo edición: ambos anclados al lado derecho, apilados verticalmente (`.component-panel-container` arriba, `.resource-panel-container` debajo) — solo posición de partida, el usuario puede arrastrar cada panel libremente después.
- `z-index` de `.component-panel-container`/`.resource-panel-container`/`.tag-panel-container`: no es valor CSS fijo — se calcula en `modes/edit/editMode.js` (`applyPanelStackOrder`, base `15`, uno por posición en `panelStackOrder`) para reflejar cuál de los tres está en primer plano tras la última interacción del usuario.
  - Al ser `position: absolute` dentro de `tableContainer` (no `fixed`), quedan fuera de la tabla de capas siguiente, pero siempre muy por debajo de su primera capa (`99`, toolbar de edición).

### Z-index de overlays (`position: fixed`)

| z-index | Capa |
|---|---|
| `10` | Footer de versión |
| `99` | Toolbar de edición |
| `100` | Header |
| `101` | Mode switcher |
| `1000` | Overlay de modal |
| `1050` | Menú contextual de componente (`.context-menu`, `03-modales-menus.md` §12.8) y menú de cabecera de columna (`.column-header-menu`, `03-modales-menus.md` §12.7) |

- `1050` es el nivel más alto de la app, no el overlay de modal — ambos menús pueden abrirse con una modal ya visible detrás (p. ej. el editor de cartas) y deben quedar por delante de ella.
- Al añadir un elemento fijo/absoluto nuevo: elegir su `z-index` respetando este orden (por debajo del modal, por encima del contenido normal).

## 11. Redimensionado (manejador de esquina)

Patrón estándar para hacer redimensionable cualquier elemento de la app (no exclusivo de un componente): `.resize-handle`, bloque standalone (no sigue BEM de ningún otro bloque, excepción similar a `.btn-*`), implementado en `ui/resizeHandle.js` (`attachResizeHandle`).

- Posición: esquina inferior derecha del elemento (`position: absolute; right: 0; bottom: 0`) — el host debe ser contenedor posicionado (`position: relative/absolute`).
- Aspecto: contenedor `18px` con grip diagonal `9px` (`::after` con gradientes). Gris neutro por defecto, `var(--accent-blue)` + `transform: scale(1.15)` con transición de 150ms en `:hover`/`.resize-handle--active`. Sin sombras ni bordes redondeados propios.
- Cursor: `nwse-resize`, igual en todos los usos aunque el elemento solo redimensione un eje (mismo punto de arrastre visual reconocible en toda la app).
- No introducir un segundo patrón de redimensionado (bordes laterales, esquinas múltiples, etc.) sin decidirlo explícitamente — reutilizar `ui/resizeHandle.js`.

### Segundo manejador, esquina superior izquierda

`.resize-handle--tl`, aplicada además de `.resize-handle` sobre el mismo host (mismo mecanismo de `ui/resizeHandle.js`, parámetro `corner: 'tl'` — mismo manejador anclado a la esquina opuesta, no un segundo patrón).

- Cualquier elemento redimensionable de la app puede tener este segundo manejador.
- Diferencias respecto a `.resize-handle`: posición `left: 0; top: 0` en vez de `right: 0; bottom: 0`. Mismo tamaño de contenedor/grip, mismo `::after`, mismo aspecto en reposo/`:hover`/`.resize-handle--active`, mismo cursor `nwse-resize` (ambas esquinas sobre la misma diagonal).
- Al arrastrarlo, la esquina inferior derecha queda fija (el manejador existente ejerce de ancla). Quien llama a `attachResizeHandle` es responsable de aplicar también el desplazamiento de posición (`dx`/`dy` que expone `corner: 'tl'`) sobre el modelo del host, no solo el tamaño.

### Variante para borde de columna de tabla

`.column-resize-handle`, aplicada además de `.resize-handle` (mismo mecanismo de `ui/resizeHandle.js`, reutilizado vía `ui/tableColumnResize.js` — misma interacción orientada a otro borde, no un segundo sistema).

- Diferencias respecto a `.resize-handle`: ocupa el borde derecho completo de la celda de cabecera (`top/bottom: 0`, no solo la esquina). Cursor `col-resize` en vez de `nwse-resize`. Grafismo: línea vertical fina (no grip diagonal `::after`).
- Mismo gris neutro en reposo y `var(--accent-blue)` en `:hover`/`.resize-handle--active`, misma transición de 150ms.

## 11.1 Cabecera de tabla fija al hacer scroll (`position: sticky`)

Primer uso de `position: sticky` en el proyecto: `.component-list th`/`.resource-list th`/`.tag-list th` — `position: sticky; top: 0; z-index: 2;`, dentro de su contenedor con scroll propio (`.component-panel__body`/`.resource-panel__body`/`.tag-panel__body`, `overflow-y: auto`).

- Objetivo: cabecera de columna siempre visible al bajar por una lista larga, en vez de desplazarse con las filas.
- Condición para que funcione: la cabecera necesita fondo opaco (`background: var(--bg-subtle)`, ya lo tenían las tres) — sin él, el contenido de las filas se transparentaría al pasar por debajo.
- `z-index: 2` es local a la propia tabla (por encima de las filas, que no tienen `z-index` propio) — sin relación con los niveles fijos de `position: fixed` de la sección Layout (paneles, modal, menús).
- `position: sticky` sigue siendo elemento posicionado a efectos de contener descendientes `position: absolute` — `.column-resize-handle` sigue funcionando sin cambios sobre una cabecera `sticky`, igual que sobre una `relative`.
- Cualquier tabla futura con scroll interno propio: reutilizar este mismo patrón (cabecera `sticky` + fondo opaco + `z-index` local) en vez de crear uno ad-hoc.

## 11.2 Fila anidada bajo un bloque padre (`.component-list__row--member`, 00204)

Primer uso de anidación visual dentro de una fila de tabla: los miembros de un grupo se muestran siempre justo debajo de la fila de su grupo en `.component-list`, indentados y con fondo distinto — como el contenido desplegado de una carpeta.

- **Fondo**: `var(--accent-blue-light)` en reposo (mismo token que "fondo claro para paneles interactivos" de `01-tokens-visual.md` §2 — no un valor ad-hoc nuevo), `#ddebf9` en `:hover` (un tono más oscuro de la misma familia), y el azul de selección estándar (`rgba(44,125,216,.15)`) si además está seleccionada — mismo criterio de prioridad que cualquier fila de `.component-list__row--selected`.
- **Indentación**: `padding-left` adicional en `.component-list__id-cell` (no en toda la fila) — solo la celda Id se desplaza, el resto de columnas (Orden, Tipo, Copia, Acciones) mantiene su alineación normal de tabla.
- **Sin línea conectora ni icono**: a diferencia de un árbol de ficheros con guías visuales, aquí basta la indentación + el fondo distinto para leerse como "contenido del bloque de encima" — decisión explícita (confirmada sobre maqueta) para no añadir ruido visual.
- **Campo deshabilitado dentro de una fila anidada**: `.component-list__order-input:disabled` — fondo `var(--bg-subtle)`, texto `var(--text-muted)`, `cursor: not-allowed` — mismo criterio que cualquier control deshabilitado de la app (§9, "Deshabilitado").
- Patrón acotado a este caso por ahora — cualquier otra tabla que necesite anidar filas bajo un padre puede reutilizarlo (fondo del token `--accent-blue-light`, indentación solo en la celda "identificadora", sin línea conectora) en vez de crear uno nuevo.
