# 030 — Título de cabecera editable

**Area**: Persistencia y guardado

El título de la cabecera de la aplicación (el texto junto a la versión, en la franja superior) se puede editar en cualquier momento mientras se está en modo edición: un click sobre él lo convierte en un campo de texto, que se confirma perdiendo el foco o pulsando Enter. Si se confirma vacío, se recupera el texto que había justo antes de empezar a editar. El texto editado se ve igual en la cabecera y en el título de la pestaña del navegador, tanto en modo edición como en modo juego, aunque solo se puede editar en modo edición.

La versión (mostrada siempre junto al texto libre, con formato `v.NNNNN`) no se puede editar en ningún caso — sigue actualizándose únicamente con cada nueva versión del proyecto, igual que antes de esta funcionalidad.

El título editado se guarda junto con el resto de la partida (autoguardado en el navegador, y embebido en el fichero que genera "Guardar a fichero"), por lo que sobrevive a recargar la página y viaja con las copias descargadas del juego.

- **Available in**: modo edición (edición); ambos modos (visualización).
- **Code**: 00147.
- **Since**: 2026-08-05
- **Last modified**: 2026-08-05
