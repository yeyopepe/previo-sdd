# 008 — Borrado masivo con confirmación
**Area**: Gestión de componentes

Al eliminar dos o más componentes seleccionados a la vez, se abre una ventana que enumera todos los componentes afectados y pide confirmación explícita antes de borrarlos. Para un solo componente basta con un aviso de confirmación simple.

El borrado tiene en cuenta las copias vinculadas: si entre los afectados hay un original con copias, esas copias también se eliminan.

- **Available in**: Modo edición (menú contextual y panel de componentes, sobre una selección múltiple)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
