# 004 — Ordenación y filtrado desde la cabecera de columna

**Area**: Mesa de juego

Al pulsar sobre el nombre de cualquier columna de las tablas de los tres paneles flotantes de modo edición (Componentes, Recursos y Etiquetas) se abre un menú desplegable con:

- **Ordenar A..Z** / **Ordenar Z..A**: cada opción funciona como un interruptor — al pulsarla se activa (y queda marcada dentro del propio menú); si ya estaba activa y se vuelve a pulsar, se desactiva y la tabla vuelve a su orden por defecto (alfabético por nombre en Recursos y Etiquetas, por la columna "Orden" en Componentes). Cada tabla admite una única columna ordenada a la vez: activar la ordenación de una columna desactiva automáticamente la que estuviera activa en cualquier otra columna de esa misma tabla.
- **Filtrar**: un desplegable con todos los valores distintos que existen en ese momento en esa columna, calculados sobre la lista completa (no sobre el resultado ya filtrado por otros criterios), más la opción "Todos" por defecto. Elegir un valor muestra solo las filas que lo tienen en esa columna. A diferencia de la ordenación, los filtros de columna sí son acumulables: se pueden tener varios activos a la vez en columnas distintas de la misma tabla (una fila debe cumplirlos todos para mostrarse), y conviven con el cuadro de filtro de texto libre de esa misma tabla, si lo tiene.

Cualquier columna que admita este menú muestra siempre un pequeño indicador junto a su nombre, tenga o no algo aplicado (fix 00172, corrige el comportamiento original del cambio 00165, en el que el indicador solo aparecía si esa columna ya tenía algo activo): en tono apagado mientras no tiene ninguna ordenación ni filtro, y destacado en cuanto pasa a tenerlos — así se distingue de un vistazo qué cabeceras se pueden pulsar, incluso sin haber aplicado nada todavía. Tanto la ordenación como los filtros de columna son estado transitorio de la sesión de edición en curso (igual que el cuadro de filtro de texto libre): no se guardan y se pierden al recargar la página, aunque sobreviven a los remontados provocados por altas/bajas/ediciones o por colapsar y expandir el panel.

Se ofrece en todas las columnas salvo "Acciones" (no es un dato de la fila). Única excepción a "Filtrar": la columna "Orden" del panel de Componentes solo ofrece las dos opciones de ordenar, sin filtro — es la posición de apilado en la mesa, ya editable directamente en la propia tabla.

Si un filtro (de columna o de texto libre) deja la tabla sin ninguna fila que mostrar, la cabecera de columna se sigue mostrando igual (fix 00172): solo se sustituye el cuerpo de la tabla por el mensaje de "sin resultados", nunca la cabecera entera. Así se puede seguir pulsando cualquier columna para abrir su menú y quitar el filtro que ha dejado la lista vacía, sin tener que recargar la página.

La cabecera de columna permanece siempre visible, fija en la parte superior, mientras se hace scroll por las filas de la tabla (fix 00173) — en las tres ventanas por igual.

- **Available in**: modo edición — en los tres paneles flotantes (ver [Panel flotante de componentes](003-panel-flotante-de-componentes-con-seleccion-resaltado-arrastre-y-redimensionado.md), [Panel flotante de recursos](006-panel-flotante-de-recursos-con-filtro-de-texto.md) y [Etiquetas, organización de elementos por nombre](008-grupos-organizacion-de-elementos-por-nombre.md)).
- **Code**: 00165, 00172, 00173, 00190.
- **Since**: 2026-08-06
- **Last modified**: 2026-08-07
