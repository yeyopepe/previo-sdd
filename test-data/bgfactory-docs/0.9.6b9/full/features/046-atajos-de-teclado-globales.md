# 046 — Atajos de teclado globales
**Area**: Interacción en modo juego

La aplicación responde a atajos de teclado que replican acciones ya existentes. Con una ventana abierta: Escape cancela, Intro acepta (salvo mientras se escribe en un área de texto o si el botón está deshabilitado) y Suprimir dispara el borrado de esa ventana si lo tiene.

En modo edición y sin ninguna ventana abierta: Suprimir elimina la selección actual y las flechas la desplazan un píxel, o diez con Mayús pulsada. Con una ventana abierta, las flechas no mueven nada para no arrastrar una pieza de la mesa por debajo.

- **Available in**: Toda la aplicación
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
