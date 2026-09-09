# 025 — Identificación de componentes al pasar el ratón

**Area**: Mesa de juego

Cualquier componente de la mesa (cuadro de texto, tablero simple, tablero personalizado, dado, visor de documentos, carta o mazo) puede mostrar información al pasar el ratón por encima, sin necesidad de abrirlo.

En modo edición, una etiqueta identificativa con el formato "Tipo: id" se muestra siempre, para cualquier componente, sin poder desactivarse (anclada a la esquina superior izquierda, visible al pasar el ratón por encima o cuando el componente está seleccionado).

En modo juego, cada componente tiene en sus propiedades generales (modal de edición, pestaña "Generales", sección "Ayuda jugador") un checkbox "Mostrar tooltip", desactivado por defecto: solo si está activado, ese componente muestra un tooltip propio al pasar el ratón por encima. El contenido del tooltip es configurable: un campo de texto "Tooltip" admite varias líneas y formato básico (negrita, cursiva, listas); si se deja vacío, se muestra el mismo "Tipo: id" que en modo edición. El texto del Tooltip admite también variables (ver más abajo).

**Variables de texto**: tanto el campo "Tooltip" como el campo "Título" de [Título de componente](035-titulo-de-componente.md) admiten variables con la forma `{nombre_variable}`, sustituidas por un valor real al mostrarse en modo juego. La primera variable disponible es `{cards_current}`, que se sustituye por el número de cartas actual — solo tiene efecto en un componente "Mazo"; en cualquier otro tipo de componente, se muestra tal cual, sin sustituir.

- **Available in**: modo juego (tooltip propio al pasar el ratón, con contenido personalizable, solo si el componente tiene "Mostrar tooltip" activado) y modo edición (etiqueta identificativa siempre visible en los mismos momentos en que ya se resalta la selección, sin depender de ningún checkbox).
- **Code**: 00032, 00034, 00208, 00212.
- **Since**: 2026-07-19
- **Last modified**: 2026-08-15
