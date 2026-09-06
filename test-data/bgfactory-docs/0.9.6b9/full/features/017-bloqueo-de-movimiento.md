# 017 — Bloqueo de movimiento
**Area**: Gestión de componentes

Cada componente o grupo tiene un bloqueo de movimiento con tres valores: nunca bloqueado, bloqueado solo en modo juego, o bloqueado siempre (también en edición). Un componente bloqueado no se puede arrastrar en el modo correspondiente.

En modo juego el menú contextual de la pieza permite bloquear y desbloquear rápidamente (alternando entre nunca y solo en juego). Una copia sincronizada no ofrece esa opción: su bloqueo sigue al del original. En modo edición, un indicador permanente en una esquina de la pieza marca que está bloqueada.

- **Available in**: Modo edición (ventana de propiedades) y modo juego (menú contextual)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
