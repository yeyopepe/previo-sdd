# 034 — Aviso al borrar un recurso en uso
**Area**: Recursos e imágenes

Al intentar eliminar un recurso que sigue estando usado por algún componente, la operación se bloquea y se muestra un aviso con la lista de componentes que lo referencian. El recurso solo se puede borrar cuando ningún componente lo usa.

La comprobación de uso recorre todas las propiedades del componente a cualquier nivel de anidamiento (por ejemplo, imágenes dentro de las caras de una carta).

- **Available in**: Modo edición (al eliminar un recurso de la galería)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
