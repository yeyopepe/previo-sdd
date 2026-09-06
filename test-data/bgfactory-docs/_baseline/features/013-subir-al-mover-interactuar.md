# 013 — Subir al mover/interactuar

**Area**: Mesa de juego

Cada componente tiene, en la pestaña "Generales" de su modal de configuración (junto a "Bloqueado" y "Mostrar tooltip"), un checkbox "Subir al mover/interactuar" con su propio icono de ayuda. Marcado por defecto para "Carta/Ficha" y "Dado" (tipos pensados para piezas que se mueven o se usan activamente durante la partida); desmarcado por defecto para el resto — un componente guardado antes de que existiera este checkbox se comporta como si estuviera desmarcado.

Cuando está marcado, cada vez que el componente se mueve (arrastre) o resuelve su propia interacción de juego (voltear una carta, lanzar un dado) estando en Modo Juego, se coloca automáticamente encima de todos los demás componentes de la mesa (equivalente al orden "1", ver [Orden de apilado en la mesa](012-orden-de-apilado-en-la-mesa.md)). Si está desmarcado, no hay ningún cambio: el componente conserva la posición de apilado que ya tuviera. Este comportamiento es exclusivo de Modo Juego — moverlo en modo edición nunca lo reordena por este checkbox — y es independiente de "Bloqueado": un componente bloqueado sigue sin poder arrastrarse, pero sus interacciones propias (voltear, lanzar) pueden seguir disparando este reordenamiento aunque esté bloqueado, igual que ya ocurre con esas interacciones respecto al bloqueo.

- **Available in**: modo juego (efecto del reordenamiento); modo edición (checkbox editable en la modal de configuración, pestaña "Generales").
- **Code**: 00061.
- **Since**: 2026-07-22
- **Last modified**: 2026-07-22
