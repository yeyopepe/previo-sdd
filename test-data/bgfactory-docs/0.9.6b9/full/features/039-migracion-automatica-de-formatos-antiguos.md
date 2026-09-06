# 039 — Migración automática de formatos antiguos
**Area**: Persistencia e intercambio

Al abrir un juego guardado con una versión anterior de la aplicación, sus componentes se actualizan automáticamente al formato actual sin intervención del usuario: tipos de pieza renombrados o retirados, campos de agrupación y de etiqueta que cambiaron de forma, el bloqueo que pasó de sí/no a tres valores, el contenido de las cartas que pasó a medidas de píxel real, entre otros.

La migración es tolerante a fallos: si un dato concreto no se puede convertir, se hace lo posible y nunca se impide que la aplicación arranque.

- **Available in**: Al cargar un juego guardado o importado
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
