# 026 — Migración automática de guardados antiguos

**Area**: Persistencia

Al cargar una partida guardada o importar un fichero de una versión anterior del editor, el contenido se adapta automáticamente al formato actual: tipos de componente renombrados o eliminados, cambios en cómo se guardan los grupos y las etiquetas, campos que pasaron de sí/no a varias opciones, y coordenadas de diseño de carta reescaladas. La migración nunca bloquea el arranque: si algo no se puede convertir, se conserva lo demás.

- **Available in**: Toda la aplicación
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
