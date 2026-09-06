# 003 — Modo edición y modo juego
**Area**: Mesa y navegación

La aplicación funciona en dos modos separados que comparten la misma mesa y el mismo contenido.

En modo edición el usuario crea, configura, clona, agrupa, etiqueta y borra componentes, y gestiona la galería de recursos y las etiquetas mediante tres paneles flotantes. Los componentes se seleccionan y se editan; el clic sobre uno abre su ventana de propiedades.

En modo juego los paneles desaparecen y los componentes quedan listos para usarse como piezas: se arrastran, se lanzan los dados, se voltean las cartas, se roban cartas de los mazos. El clic izquierdo dispara la interacción propia de cada tipo y el clic derecho abre un menú contextual configurable por componente. Los componentes ocultos no se muestran y el bloqueo de movimiento se respeta según su configuración.

Se entra en modo edición con un botón situado en la esquina superior derecha y se vuelve a modo juego desde la barra de herramientas de edición.

- **Available in**: Toda la aplicación; se alterna con el botón de entrada en modo juego y la barra de herramientas de edición
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
