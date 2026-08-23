# Tokens visuales, tipografía, espaciado, bordes, elevación

Ver `INDEX.md` para el mapa completo de la Style Bible.

## 2. Design tokens (`:root`)

Todos los colores viven como custom properties en `:root`. Nunca hardcodear un color que ya tenga token — reutilizar el existente o añadir uno nuevo al `:root` si hace falta un tono nuevo y reutilizable.

```css
--bg-table:     #c2c2c2;  /* fondo de la mesa infinita */
--bg-toolbar:   #333333;  /* header y toolbars */
--bg-card:      #f5f5f5;  /* paneles/tarjetas (listas, panel de edición) */
--accent-blue:  #2c7dd8;  /* color de acción primario (botones, foco, tabs activas) */
--accent-blue-dark: #123a66;  /* fondo de la etiqueta identificativa de componente en modo edición (03-modales-menus.md §12.3) */
--accent-blue-light: #eaf3fc;  /* fondo claro para paneles que destacan como interactivos sin usar el azul sólido */
--text-primary: #1a1a1a;  /* texto sobre fondos claros */
--text-light:   #ffffff;  /* texto sobre fondos oscuros/de acento */
--text-muted:   #666666;  /* texto secundario */
--error:        #d32f2f;  /* estados de error y acciones destructivas */
--success:      #2e7d32;  /* estados de éxito/confirmación positiva */
--border-neutral: #dcdcdc;  /* todos los bordes finos neutros */
--bg-subtle:    #f0f0f0;  /* fondos neutros en reposo: cabecera de tabla, botón secundario */
--bg-hover:     #e8e8e8;  /* cualquier hover neutro: fila, botón secundario, tab */
--radius-sm:    4px;   /* radio de controles, ver §5 */
--radius-lg:    8px;   /* radio de contenedores destacados, ver §5 */
--shadow-1:     0 2px 6px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.08);  /* elevación nivel 1, ver §6 */
--shadow-2:     0 4px 20px rgba(0,0,0,0.15);  /* elevación nivel 2, ver §6 */
--transition-fast: 150ms ease;  /* transición estándar de hover/foco, ver §6 */
--section-accent: #5b5f97;  /* título de .modal__section (03-modales-menus.md §12.6), distinto de --accent-blue/--accent-blue-dark (interactivo/seleccionado) */
```

- Todos los grises neutros y las sombras/radios reutilizables ya son tokens — no quedan colores "puntuales" sin promover.
- Overlays que siguen siendo valores puntuales (no se repiten lo bastante para merecer token): `rgba(0,0,0,0.5)` (fondo de `.modal-overlay`), `rgba(255,255,255,0.1)` (hover en toolbar oscura).

## 3. Tipografía

- Fuente global: `system-ui, sans-serif`. Sin webfonts externas.
- Tamaños usados, de mayor a menor — reutilizar estos, no inventar tamaños intermedios:

| Tamaño | Uso |
|---|---|
| `4rem` | Resultado a tamaño grande del componente "Dado" (`ui/diceResultModal.js`) — excepción puntual para legibilidad desde lejos, único uso previsto |
| `1.5rem` | Título principal (`h1`) |
| `1.125rem` | Títulos de panel (`.edit-mode-panel h2`) |
| `0.875rem` | Texto de UI por defecto (botones, tabs, labels, inputs, items de lista) |
| `0.75rem` | Texto auxiliar (botones pequeños, error de validación, footer de versión) |

- `font-weight: 500` para labels de formulario. Resto: peso normal del navegador.

## 4. Espaciado

Escala basada en `rem`, pasos de `0.25rem`: `0.25rem`, `0.5rem`, `0.75rem`, `1rem`, `1.5rem`. No usar píxeles para padding/margin salvo casos ya existentes (bordes `1px`/`2px`).

- Padding de contenedor estándar: `1rem`.
- Padding de controles (botones, tabs): `0.5rem 1rem`.
- Gap entre elementos en flex: `0.5rem` (ajustado) o `1rem` (holgado).

## 5. Bordes y esquinas

Escala de dos radios:

- `var(--radius-sm)` (4px) — controles: botones (incl. pequeños dentro de items de lista), inputs, items pequeños de lista/galería.
- `var(--radius-lg)` (8px) — contenedores destacados: modal, paneles flotantes (`.component-panel`, `.resource-panel`), componente "Carta".
- Bordes: `1px solid var(--border-neutral)`, o `1px solid var(--text-light)` sobre fondo oscuro (toolbar).

## 6. Elevación, sombra y transición

Sistema de 3 niveles de elevación, reutilizable en toda la app.

- **Nivel 0 — plano**: mesa infinita y cualquier contenido embebido dentro de otro elemento (p. ej. `.document-viewer__content`). Sin sombra.
- **Nivel 1 — flotante sutil** (`box-shadow: var(--shadow-1)`): paneles de trabajo (`.component-panel`, `.resource-panel`), cabecera/toolbar (`h1`, `.edit-toolbar`), `.toast`, piezas de juego sobre la mesa (`.board`, `.tablero-personalizado`, `.carta`, `.document-viewer`).
  - `.dice`: usa `filter: drop-shadow(...)` en vez de `box-shadow`, para que la sombra siga la silueta real (triángulo/cuadrado/rombo/decágono) en vez de la caja cuadrada del contenedor.
  - `.carta--hex` (carta con proporción hexagonal): mismo criterio que `.dice` — silueta no rectangular, usa `filter: drop-shadow(...)`.
  - `.text-box` (texto suelto sobre la mesa, sin caja/fondo): usa `text-shadow` en vez de `box-shadow`, solo para legibilidad sobre cualquier color de mesa.
- **Nivel 2 — overlay** (`box-shadow: var(--shadow-2)`): modales (`.modal`) y `.help-icon__tooltip` — nivel más alto.
- **Sombra opcional de `'tableroSimple'`/`'tableroPersonalizado'`**: a diferencia del resto de piezas del nivel 1, su sombra de contacto puede desactivarse por componente.
  - Checkbox "Sombra" en sección "Visual" (`.modal__field--checkbox`, ver `03-modales-menus.md` §12.6).
  - `properties.sombra` (boolean, `true` por defecto).
  - Desmarcado: modificador `.board--sin-sombra`/`.tablero-personalizado--sin-sombra` (`box-shadow: none`) — componente queda en nivel 0.
  - Un tablero guardado sin esta propiedad se comporta como si estuviera marcado (con sombra) — sin cambio visual.
- El estado transitorio `.lifted` al arrastrar un componente en Modo Juego es el estado "en el aire" de este mismo sistema (sombra más pronunciada + desplazamiento fijo durante el arrastre) — no una excepción aislada. Detalle completo en `INDEX.md` §13.
- **Extrusión configurable** (`profundidad`/`colorExtrusion`, campo general de componente, `core/component.js`): capas sólidas apiladas sin blur, no sombra difusa. Concepto independiente y compatible con los 3 niveles de elevación — no introduce un cuarto nivel. Elevación = sombra de contacto con la mesa; extrusión = grosor/cuerpo del propio componente.
  - `profundidad`: número, px, `0` por defecto (sin efecto), tope `40`.
  - `colorExtrusion`: string color o `null` (cálculo automático `shadeColor(colorBase, -0.25)`, `colorBase` según tipo — ver `ui/componentRenderer.js`, `resolveExtrusionColor`).
  - Técnica: `Array.from({length: profundidad}, (_, i) => i+1)` capas de 1px de offset acumulado — `box-shadow: ${i+1}px ${i+1}px 0 0 ${color}` (tipos sin `clip-path`) o `filter: drop-shadow(${i+1}px ${i+1}px 0 ${color})` (tipos con `clip-path`: `'carta'` hex/triángulo, `'dado'`), unidas junto a la sombra de contacto de nivel 1 existente cuando aplica.
  - Sin efecto en `'texto'`, cualquiera que sea `properties.colorFondo`.
  - `'dado'` ya no tiene mecanismo propio de profundidad (polígono SVG duplicado) — usa este mecanismo general como cualquier otro tipo, aplicado sobre `.dice`.
- **Transiciones**: elementos interactivos (botones, filas de lista, tabs, items seleccionables, icono de ayuda, campos de formulario) llevan `transition: <propiedad> var(--transition-fast)` (150ms) en cambios de `:hover`/`:focus` — color de fondo/borde, `opacity`, `box-shadow`, y en botones de acción primaria/destructiva un ligero `transform: translateY(-1px)`.
  - No usar `:active`.
  - No usar transiciones en el contorno discontinuo de selección (`--selectable`/`--selected`) ni en el temblor/parpadeo del dado — son indicadores funcionales de estado y JS puro, no decoración (ver `INDEX.md` §13).
