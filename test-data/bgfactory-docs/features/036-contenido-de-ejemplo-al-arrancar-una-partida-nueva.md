# 036 — Contenido de ejemplo al arrancar una partida nueva

**Area**: Mesa de juego

Al arrancar una partida totalmente nueva (sin ninguna partida guardada previamente en el navegador), la galería de recursos se rellena automáticamente con contenido de ejemplo mínimo, para mostrar de un vistazo lo que se puede hacer sin partir de una galería vacía ni de contenido real de ningún juego concreto.

La galería de recursos arranca con 2 recursos de ejemplo, uno por cada tipo de recurso admitido: una imagen de ejemplo (un cuadrado de color sólido con una etiqueta de texto "Ejemplo imagen" encima) y una tipografía de ejemplo (una fuente libre de licencia abierta). Ambos recursos se pueden editar o eliminar desde el panel de recursos igual que cualquier recurso subido por el usuario — ver [Panel flotante de recursos, con filtro de texto](006-panel-flotante-de-recursos-con-filtro-de-texto.md).

Una partida guardada con una versión anterior de la app que todavía no tuviera este contenido de ejemplo lo recibe una única vez la primera vez que se abre, sin sobrescribir nada de lo que el usuario ya tenga.

- **Available in**: modo edición (galería de recursos), al arrancar una partida nueva.
- **Code**: 00184
- **Since**: 2026-08-20
- **Last modified**: 2026-08-20
