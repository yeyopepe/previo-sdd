# 016 — Componente oculto en modo juego

**Area**: Mesa de juego

Cada componente (cuadro de texto, tablero simple, dado, visor de documentos, carta o mazo) tiene, en la pestaña "Generales" de su modal de configuración, un checkbox "Oculto" (junto a "Bloqueado", "Mostrar tooltip" y "Subir al mover/interactuar", con su propio icono de ayuda), desmarcado por defecto — un componente guardado antes de que existiera este checkbox se comporta como si estuviera desmarcado.

Cuando "Oculto" está marcado, ese componente deja de aparecer por completo en modo juego: no se ve en la mesa, no ocupa espacio, no se puede seleccionar ni interactuar con él, ni aparece en el menú contextual — se comporta exactamente como si no existiera para quien está jugando. En modo edición, en cambio, un componente marcado como "Oculto" se sigue mostrando, seleccionando, moviendo, redimensionando y editando con total normalidad; para poder identificarlo de un vistazo, muestra además una pequeña insignia de ojo tachado superpuesta en una esquina (esquina inferior derecha, para poder convivir sin solaparse con la insignia de candado de "Bloqueado" si el componente tiene ambas marcas activas a la vez).

- **Available in**: modo edición (checkbox editable en la modal de configuración, pestaña "Generales"; insignia de ojo tachado sobre los componentes ocultos); modo juego (el componente oculto no se renderiza en absoluto).
- **Code**: 00100.
- **Since**: 2026-07-28
- **Last modified**: 2026-07-28
