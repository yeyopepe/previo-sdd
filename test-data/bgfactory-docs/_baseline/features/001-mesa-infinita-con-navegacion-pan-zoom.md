# 001 — Mesa infinita con navegación pan/zoom

**Area**: Mesa de juego

Superficie de juego navegable arrastrando (pan) y con la rueda del ratón (zoom, acotado a un rango razonable), donde se renderizan los componentes de la partida. La posición y el zoom se mantienen tal como los deja el usuario durante toda la sesión, incluida cualquier acción que refresque la pantalla (mover/editar/añadir/eliminar un componente); no se persisten entre recargas de página.

Un botón "Ajustar zoom" (solo icono, con etiqueta accesible y tooltip nativo) reencuadra la vista al instante (sin animación) para que todos los componentes existentes queden visibles a la vez, con margen respecto al borde de la pantalla. Está disponible en el extremo superior derecho en ambos modos: como último botón de la barra de edición en modo edición, y como botón flotante junto a "Entrar en modo edición" en modo juego. Si no hay ningún componente, deja la vista neutra por defecto (zoom 1, centrada en el origen); si el contenido es muy pequeño o hay un único componente, el zoom se acerca como mucho hasta el límite máximo ya existente para el zoom manual. El resultado no se persiste, igual que el resto de posición/zoom de la mesa.

- **Available in**: modo juego y modo edición.
- **Code**: 00002, 00016, 00021.
- **Since**: 2026-07-17
- **Last modified**: 2026-07-18
