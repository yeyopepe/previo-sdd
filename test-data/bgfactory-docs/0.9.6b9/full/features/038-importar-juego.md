# 038 — Importar juego
**Area**: Persistencia e intercambio

Importar carga un fichero JSON exportado previamente, aunque provenga de una versión distinta de la aplicación (ese es el caso de uso principal, no un error). Primero se elige mediante casillas qué componentes, recursos y etiquetas del fichero se traen.

Después se elige cómo fusionar: añadir el contenido importado al juego actual o sobrescribir todo el juego con el importado; y qué hacer ante un identificador que ya existe: sobrescribir el existente o mantener ambos. Al sobrescribir todo el juego se aplica también el título del fichero importado.

Los componentes en un formato antiguo se convierten al vuelo durante la importación; si alguno da errores de conversión, se listan y se ofrece continuar sin ese componente o abortar. Mientras se aplica la importación se muestra una ventana de operación en curso, y al terminar se muestra un informe si hubo avisos.

- **Available in**: Modo edición (botón Importar de la barra de herramientas)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
