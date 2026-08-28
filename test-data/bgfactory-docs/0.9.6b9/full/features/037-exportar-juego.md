# 037 — Exportar juego
**Area**: Persistencia e intercambio

Exportar descarga una copia completa del juego en un fichero JSON que se puede compartir con cualquiera; quien lo reciba podrá abrirlo y seguir jugando o editando sin nada más. El fichero incluye los componentes, los recursos, las etiquetas, los grupos y el título del juego, pero no la configuración de los paneles flotantes.

Antes de descargar se elige, mediante casillas, qué componentes, recursos y etiquetas se incluyen, y el nombre del fichero. Los grupos referenciados por los componentes exportados se incluyen automáticamente.

El menú de exportación anuncia además la exportación de recursos en ZIP y de una hoja de producción en CSV como funciones próximas, todavía no disponibles.

- **Available in**: Modo edición (menú Exportar de la barra de herramientas)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
