# 007 — Edición de un recurso Imagen, con vista previa ampliada de zoom y pan

**Area**: Mesa de juego

El botón "Editar" de un recurso de tipo Imagen (panel "Recursos") abre una ventana más ancha que el resto de modales de la app, con el campo "Nombre del recurso", una vista previa grande de la imagen y el botón "Cambiar imagen..." (que reemplaza el fichero manteniendo el mismo recurso).

Dentro de esa vista previa se puede inspeccionar la imagen en detalle:

- **Zoom**: con la rueda del ratón sobre la vista previa (centrado en el punto donde está el cursor, entre el 100% y el 500%), o con los botones `+`/`-` superpuestos en la esquina del marco (zoom centrado). Un tercer botón restablece la vista a su tamaño inicial (100%, centrada). El nivel de zoom actual se muestra siempre en la esquina del marco.
- **Mover la imagen (pan)**: con la imagen ampliada (zoom > 100%), se puede arrastrar con click izquierdo para desplazarla dentro del marco.
- El zoom/posición es puramente una ayuda de inspección visual: no se guarda en ningún sitio. Se reinicia cada vez que se abre la ventana, y también al reemplazar la imagen con "Cambiar imagen...".

La ventana de edición de un recurso de tipo Tipografía no se ve afectada por este cambio: conserva su tamaño y vista previa habituales.

- **Available in**: modo edición.
- **Code**: 00168.
- **Since**: 2026-08-06
- **Last modified**: 2026-08-06
