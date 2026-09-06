# 004 — Panel de componentes
**Area**: Gestión de componentes

Un panel flotante lista en forma de tabla todos los componentes del juego. Cada fila muestra el identificador del componente, su orden de apilado y botones de acción para editarlo, clonarlo, copiarlo o eliminarlo.

El panel se puede arrastrar por su cabecera a cualquier posición, colapsar para ocultar su contenido y redimensionar tanto en ancho como en alto; su posición, tamaño y estado de colapso se recuerdan entre sesiones. El ancho de cada columna de la tabla también es ajustable y se conserva.

Una caja de filtro de texto acota la lista a los componentes cuyo contenido coincide, con un botón para limpiar el filtro. Las cabeceras de columna permiten ordenar y filtrar por esa columna; la ordenación o filtro activos se indican junto al título de la cabecera. Los miembros de un [grupo](012-agrupacion-de-componentes.md) aparecen anidados bajo la fila de su grupo. Un botón al pie del panel añade un componente nuevo.

- **Available in**: Modo edición (panel flotante)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
