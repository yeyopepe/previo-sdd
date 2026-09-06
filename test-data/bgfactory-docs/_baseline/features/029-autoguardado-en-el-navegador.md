# 029 — Autoguardado en el navegador

**Area**: Persistencia y guardado

Cada alta, edición, movimiento, redimensionado o borrado de un componente se guarda automáticamente en `localStorage`, sin ninguna acción del usuario. Al reabrir la aplicación en el mismo navegador se recupera tal cual el último estado guardado; si nunca se ha guardado nada, arranca con la semilla embebida en el propio fichero (ver más abajo) o, en su defecto, con el componente de ejemplo. Si el estado guardado resulta corrupto o de una versión incompatible, se avisa brevemente y se arranca igualmente con ese mismo comportamiento de respaldo, sin bloquear la carga.

Además de los componentes, se guarda igual de automático el estado de los tres paneles flotantes del modo edición (Componentes, Recursos y Etiquetas: posición, ancho y colapsado/expandido; el ancho de cada columna de su tabla, solo en Componentes y Recursos — el panel de Etiquetas no tiene columnas redimensionables, ver [Panel flotante de componentes](003-panel-flotante-de-componentes-con-seleccion-resaltado-arrastre-y-redimensionado.md) y [Etiquetas, organización de elementos por nombre](008-grupos-organizacion-de-elementos-por-nombre.md)), cada vez que cambia. Si el guardado existente es de una versión anterior a esta funcionalidad y no incluye algún dato, ese aspecto del panel arranca con sus valores por defecto (expandido, posición, ancho y ancho de columna por defecto), igual que si nunca se hubiera guardado nada. Las etiquetas creadas desde la pestaña "Generales" de cualquier componente o desde el panel "Etiquetas" se guardan con el mismo criterio; un guardado anterior a esta funcionalidad simplemente arranca sin ninguna etiqueta.

El guardado es un único slot por navegador/perfil (no aislado por fichero): si se abren varias copias descargadas distintas en el mismo navegador, prevalece el último estado autoguardado sobre el contenido propio de la copia que se abra, salvo que sea la primera vez que se abre cualquier copia en ese navegador.

- **Available in**: automático, en cualquier modo (el estado de los paneles, solo en modo edición, que es donde existen).
- **Code**: 00011, 00014, 00053, 00064, 00079, 00190.
- **Since**: 2026-07-17
- **Last modified**: 2026-08-07
