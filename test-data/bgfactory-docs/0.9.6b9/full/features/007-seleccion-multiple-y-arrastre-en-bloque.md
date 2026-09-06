# 007 — Selección múltiple y arrastre en bloque
**Area**: Gestión de componentes

El clic normal sobre un componente lo selecciona en exclusiva (o deselecciona si ya era el único seleccionado). Con Ctrl o Cmd pulsado, el clic añade o quita ese componente de la selección sin tocar el resto. La selección también se puede hacer desde las filas del panel de componentes.

Con varios componentes seleccionados, arrastrar uno mueve todos a la vez manteniendo las distancias relativas entre ellos. Las flechas del teclado desplazan la selección un píxel (diez con Mayús pulsada). Los componentes con el movimiento totalmente bloqueado no se mueven.

Un grupo entra y sale de la selección siempre como bloque atómico: seleccionar un miembro selecciona el grupo entero. El componente realmente clicado y los que se han arrastrado a la selección por pertenecer a su grupo se distinguen visualmente por el color del contorno.

- **Available in**: Modo edición (mesa y panel de componentes)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
