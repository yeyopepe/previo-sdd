# 011 — Búsqueda de imagen en el modal "Elegir imagen"

**Area**: Mesa de juego

La modal "Elegir imagen" (galería en grid de miniatura + nombre, usada al configurar el fondo "Imagen" de [Componente "tablero simple"](018-componente-tablero-simple.md) y al elegir la imagen de cada cara de [Componente "carta"](022-componente-carta.md)) muestra un cuadro de texto de búsqueda ("Buscar imagen…") encima de la galería, solo cuando hay al menos una imagen disponible. El filtrado ocurre en tiempo real según se escribe, comparando el texto con el nombre de cada imagen de forma insensible a mayúsculas/minúsculas y a tildes (mismo criterio de normalización que el filtro del panel de recursos, ver sección anterior). Si ninguna imagen coincide, la galería se sustituye por un mensaje indicándolo. Si había una imagen ya seleccionada y el filtro la oculta, la selección se mantiene internamente: "Aceptar" la sigue aplicando si no se cambia de selección. El cuadro de búsqueda se reinicia vacío cada vez que se abre la modal.

- **Available in**: modo edición.
- **Code**: 00055.
- **Since**: 2026-07-21
- **Last modified**: 2026-07-21
