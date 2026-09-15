# 035 — Título de componente

**Area**: Mesa de juego

Cualquier componente de la mesa (cuadro de texto, tablero simple, tablero personalizado, dado, visor de documentos, carta o mazo) puede mostrar una etiqueta con contenido libre, fija a la esquina superior izquierda del componente, en modo juego.

En las propiedades del componente (modal de edición, pestaña "Generales", sección "Ayuda jugador"), un checkbox "Mostrar título de componente" activa o desactiva la etiqueta — desactivado por defecto. Un botón "Editar título de componente…" abre una ventana propia con: el contenido del título (admite varias líneas, etiquetas HTML básicas —negrita, cursiva, subrayado, listas— y variables de texto, ver [Identificación de componentes al pasar el ratón](025-identificacion-de-componentes-al-pasar-el-raton.md)), el color del texto (negro por defecto), el color de fondo (blanco por defecto) y el nivel de transparencia del fondo. Con el checkbox activado pero sin contenido, no se muestra ninguna etiqueta.

A diferencia del tooltip (que solo aparece al pasar el ratón por encima), el título, una vez activado, es siempre visible en modo juego. En modo edición nunca se muestra.

Cuando el componente pertenece a un "Grupo" (ver [Etiquetas, organización de elementos por nombre](008-grupos-organizacion-de-elementos-por-nombre.md)), el checkbox "Mostrar título de componente" del grupo manda sobre el del propio componente mientras dure la agrupación — mismo criterio que "Mostrar tooltip". El contenido, los colores y la transparencia siempre son propios de cada componente, nunca del grupo. "Copiar estilo"/"Pegar estilo" (disponible en "Carta") y la sincronización de [copias vinculadas](005-elementos-tipo-copia-vinculados-y-sincronizados-con-un-original.md) incluyen el bloque completo del título.

Este cambio sustituye a la antigua etiqueta fija de número de cartas que mostraba siempre el componente "Mazo" (ver [Componente "mazo"](023-componente-mazo.md)): quien quiera recuperar ese comportamiento puede activar "Mostrar título de componente" en un mazo con un texto como `"{cards_current} cartas"`.

- **Available in**: modo juego, en cualquiera de los 8 tipos de componente, activable/configurable desde sus propiedades (modo edición).
- **Code**: 00212, 00220.
- **Since**: 2026-08-15
- **Last modified**: 2026-08-15
