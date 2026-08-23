# 005 — Elementos tipo Copia, vinculados y sincronizados con un original

**Area**: Mesa de juego

A diferencia de "Clonar" (copia completa e independiente desde el instante en que se crea), el botón "Copiar" de cada fila del panel de componentes (ver [Panel flotante de componentes](003-panel-flotante-de-componentes-con-seleccion-resaltado-arrastre-y-redimensionado.md)) crea de inmediato, sin ninguna modal previa, un elemento tipo Copia que queda permanentemente vinculado a su original y sincronizado con él mientras ambos existan en la partida.

**Identificador**: el id de una Copia es siempre el id del original con el sufijo `-COPY-XXX` (número de 3 dígitos, el primer hueco libre entre las copias de ese mismo original — si se borra una copia y no queda otra con ese hueco, se reutiliza al crear la siguiente). Si se cambia el id del original desde su modal de edición, se renombran automáticamente los ids de todas sus copias vinculadas, conservando el mismo sufijo y sustituyendo solo el prefijo.

**Qué se sincroniza automáticamente** en cuanto se edita el original: su tipo visual, nombre, imagen, ancho/alto, la etiqueta asignada, y todas las propiedades de configuración/diseño específicas de su tipo (color, fondo, proporción, diseño de caras de una carta, configuración de caras de un dado, contenido de un documento/texto, etc. — es decir, todo lo editable desde la modal de configuración del elemento). **Qué NO se sincroniza**, quedando siempre independiente por copia: la posición en la mesa, el orden de apilado, y el resultado de cualquier interacción de juego propia del tipo (el resultado actual de un dado, la cara mostrada de una carta) — cada copia puede moverse, lanzar su propio dado o voltear su propia carta de forma independiente, sin afectar al original ni a otras copias del mismo original.

**"Bloqueado" y "Oculto" con sincronización propia**: a diferencia del resto de propiedades, estos dos campos tienen su propio checkbox "Sincronizado" (marcado por defecto al crear la copia). Mientras está marcado, "Bloqueado" y "Oculto" de la copia siguen siempre el valor actual del original, igual que el resto de propiedades. Si se desmarca, la copia pasa a tener su propio valor de "Bloqueado"/"Oculto", independiente del original, hasta que se vuelva a marcar el checkbox (momento en el que adopta de inmediato el valor que tenga el original en ese instante). En modo juego, la opción "Bloquear"/"Desbloquear" del menú contextual de una copia solo está disponible cuando esa copia no está sincronizada — con "Sincronizado" marcado no aparece, porque su bloqueo depende siempre del original.

**Edición de una Copia**: al abrirla (desde "Editar" en su fila, o al hacer click/doble click sobre su representación en la mesa) se muestra una modal reducida, sin pestañas, con el id de la copia (solo lectura), un aviso indicando que es una copia de otro elemento, el checkbox "Sincronizado", los controles "Bloqueado" (desplegable de 3 opciones) y "Oculto" (checkbox) — habilitados solo si "Sincronizado" está desmarcado —, el id del elemento original, y tres botones: "Eliminar" (borra solo esa copia, con la misma confirmación estándar del resto de la app), "Cancelar" (cierra sin cambios) y "Aceptar" (confirma el estado de "Sincronizado" y, si aplica, el "Bloqueado"/"Oculto" propios fijados).

**No se admiten copias de copias**: los botones "Copiar" y "Clonar" no aparecen en la fila de un componente que ya es una Copia — solo "Editar" y "Eliminar".

**Borrado en cascada**: al eliminar el elemento original se eliminan automáticamente todas sus copias vinculadas, para no dejar copias huérfanas. Eliminar una copia individual (desde su fila o desde su modal reducida) no afecta al original ni a las demás copias.

**Alta**: "Copia" no es un tipo seleccionable en la modal previa "+ Añadir componente" (sigue siendo Cuadro de texto/Tablero simple/Tablero personalizado/Dado/Visor de documentos/Carta-Ficha/Mazo) — un elemento tipo Copia solo puede nacer copiando un componente ya existente.

**Distintivo visual en modo edición**: cualquier elemento tipo Copia muestra sobre sí mismo, en la mesa, una pequeña insignia roja permanente (esquina inferior izquierda) que permite identificarlo como copia a simple vista, sin necesidad de abrirlo. Convive sin solaparse con las insignias de "Bloqueado" y "Oculto" si el elemento también las tiene activas. Además, mientras el elemento está seleccionado o bajo el cursor, el contorno discontinuo y la etiqueta con su tipo/id (que ya se muestran para cualquier elemento en ese estado) se pintan en rojo en vez de azul. Solo aplica en modo edición; en modo juego una copia se ve como cualquier otro componente, sin ningún distintivo.

- **Available in**: modo edición (creación, edición reducida, borrado, y distintivo visual sobre la mesa); el resultado de la sincronización y la posición/estado independiente de cada copia se reflejan también en modo juego, igual que cualquier otro componente.
- **Code**: 00097, 00100, 00105, 00149, 00167.
- **Since**: 2026-07-27
- **Last modified**: 2026-08-06
