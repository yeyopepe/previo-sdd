# 020 — Componente "dado"

**Area**: Mesa de juego

Tercer tipo de componente: un dado con representación 2D plana (sin perspectiva ni vista isométrica), con color del cuerpo y color de los números configurables de forma independiente, y una tipografía a elegir entre las disponibles en la galería de recursos (con muestra de texto en la propia fuente; si no hay ninguna disponible, se usa la tipografía por defecto de la app). El número de resultados posibles se configura de dos formas alternables sin perder la configuración de la que no está activa:

- **Número máximo de caras**: entre 2 y 100; cada tirada da un número al azar entre 1 y ese máximo.
- **Lista de valores**: texto libre separado por comas, donde un valor vacío o formado solo por espacios en blanco cuenta como una cara más (mínimo 2 valores en total, de los cuales al menos uno no puede estar vacío); cada tirada da uno de esos valores literales al azar (incluida una cara vacía, que se muestra sin ningún carácter), no necesariamente numéricos.

La silueta frontal del dado varía según la cantidad de resultados posibles configurada: triángulo (4), cuadrado liso (6), rombo (8), o una esfera facetada (decágono dividido en un abanico de triángulos) para 9 o más y como respaldo genérico para cualquier otra cantidad (2, 3, 5 o 7). Tiene un contorno fino oscuro de acabado (misma familia de recurso que el bisel del tablero simple, sin degradados difuminados) y una sombra de contacto suave que sigue el contorno de la silueta y lo asienta sobre la mesa, igual que el resto de piezas de juego. La sensación de grosor la da la propiedad general "Extrusión" (cambio 00210, pestaña "Visuales" — ver [Alta/edición/borrado de componentes con modal de tabs](002-alta-edicion-borrado-de-componentes-con-modal-de-tabs.md)), con un valor inicial que aproxima el aspecto que tenía antes; ya no es un mecanismo propio y fijo del dado.

En modo juego, un click sobre el dado lo lanza: durante ~1 segundo muestra un parpadeo de resultados aleatorios entre los posibles, mientras el propio dado tiembla ligeramente (pequeño desplazamiento aleatorio, sin rotación) para reforzar la sensación de que está en juego, y al terminar fija el resultado final y deja de temblar (los clicks durante la tirada se ignoran); un doble click abre una modal con el resultado actual a tamaño grande. En modo edición no hay lanzamiento: el dado se comporta como cualquier otro componente (selección, edición, movimiento, redimensionado siempre cuadrado). "Bloqueado" solo afecta a si se puede arrastrar, nunca a si se puede lanzar. Al crear el dado, o si la configuración de caras cambia de forma que el resultado actual deje de ser válido, se fija automáticamente como resultado el primero de los posibles según la configuración vigente.

- **Available in**: renderizado sobre la mesa en modo juego y modo edición; alta eligiendo "Dado" en la modal previa de tipo al pulsar "+ Añadir componente" (ver [Alta/edición/borrado de componentes con modal de tabs](002-alta-edicion-borrado-de-componentes-con-modal-de-tabs.md)); lanzamiento, temblor y modal de resultado grande solo en modo juego.
- **Code**: 00020, 00031, 00063, 00129, 00210.
- **Since**: 2026-07-19
- **Last modified**: 2026-08-19
