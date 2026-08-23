# 028 — Atajos de teclado en modo edición

**Area**: Mesa de juego

Cuatro atajos de teclado generales, equivalentes directos de botones o acciones ya existentes — no añaden ninguna acción, confirmación ni validación nueva, solo un disparador rápido de lo que ya existe:

- **ESC**: equivale al botón "Cancelar" (o "Cerrar", en ventanas que solo tienen ese botón de cierre) de la ventana modal que esté abierta en ese momento. Con varias modales abiertas a la vez (una lanzada desde dentro de otra), solo afecta a la última abierta, sin cerrar las de debajo.
- **INTRO**: equivale al botón "Aceptar" de la modal abierta, si la tiene y no está deshabilitado (p. ej. por una validación no superada) — en ventanas que solo tienen "Cerrar" no hace nada, al no existir botón "Aceptar". Con el foco en un cuadro de texto de varias líneas (p. ej. el contenido de un documento), Intro sigue insertando un salto de línea con normalidad en vez de disparar "Aceptar".
- **SUPR**: equivale al botón "Suprimir"/"Eliminar" de la modal abierta, si la tiene; si no hay ninguna modal abierta pero hay un componente seleccionado en el panel flotante o en la mesa, lo elimina directamente (mismo efecto que su botón "Eliminar" habitual, con la misma confirmación previa). Con el foco en cualquier campo de texto no interfiere con borrar caracteres mientras se escribe.
- **Flechas** (cambio 00145): con uno o varios componentes seleccionados en la mesa (panel flotante o click en la mesa) y sin ninguna modal abierta, desplazan el/los componente(s) seleccionado(s) 1 píxel por pulsación, o 10 píxeles si se mantiene pulsada la tecla SHIFT — mismo comportamiento que ya existía en el editor de diseño de cartas. Con varios componentes seleccionados a la vez, se mueven todos en bloque, manteniendo las distancias relativas entre ellos (igual que ya hace el arrastre con el ratón de una selección múltiple). Un componente con "Bloqueado" fijado a "Todos los modos" no se mueve con las flechas, igual que tampoco se puede arrastrar con el ratón en modo edición — salvo que pertenezca a un [grupo](034-agrupacion-de-elementos-agrupar-y-desagrupar.md), en cuyo caso se mueve igual que el resto de miembros. Sin ningún componente seleccionado, o con el foco en un campo de texto, las flechas no hacen nada.

Cuando el botón o la acción equivalente no existe en el contexto actual (p. ej. INTRO en una ventana que solo tiene "Cerrar", SUPR sin ninguna modal abierta y sin ningún componente seleccionado, o las flechas sin nada seleccionado), la tecla no hace nada. Todas las vías de borrado siguen pidiendo la misma confirmación que ya pedían sus botones equivalentes.

- **Available in**: modo edición. Las flechas no están disponibles en modo juego, al no existir ahí una selección de componente persistente equivalente (la única selección de modo juego vive ligada al menú contextual de click derecho, y se pierde al cerrarlo).
- **Code**: 00078, 00145, 00193.
- **Since**: 2026-07-24
- **Last modified**: 2026-08-13
