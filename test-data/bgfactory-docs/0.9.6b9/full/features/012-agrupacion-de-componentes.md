# 012 — Agrupación de componentes
**Area**: Gestión de componentes

Varios componentes seleccionados que no pertenezcan ya a ningún grupo se pueden agrupar en una unidad. Mientras dura la agrupación, el grupo tiene sus propias propiedades generales (bloqueo, ocultación, mostrar tooltip, mostrar título, subir al mover/interactuar y etiquetas) que gobiernan el comportamiento de todos sus miembros, sustituyendo a las propias de cada componente.

El grupo se selecciona, se mueve y se edita como un solo elemento; en el panel de componentes sus miembros aparecen anidados bajo la fila del grupo. Desde la ventana de propiedades del grupo se editan sus propiedades comunes y se puede renombrar.

Desagrupar deshace la unidad y devuelve a cada componente sus propias propiedades. Un grupo que se queda con un solo miembro (por ejemplo tras borrar los demás) se disuelve automáticamente.

- **Available in**: Modo edición (menú contextual y panel de componentes)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
