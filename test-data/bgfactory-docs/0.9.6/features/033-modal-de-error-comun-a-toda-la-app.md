# 033 — Modal de error común a toda la app

**Area**: Notificación de errores

Cualquier error de la aplicación (recuperación de estado fallida, formato de fichero no soportado, recurso en uso al intentar eliminarlo, importación de componentes inválida, etc.) se comunica siempre con el mismo elemento: una ventana modal con el detalle del error y un botón "Cerrar", en vez de un aviso breve tipo toast. Así, cualquier error se ve y se comporta igual en toda la app, con independencia de dónde ocurra.

Los avisos que no son de error (confirmaciones de éxito, como "Guardado como...") siguen mostrándose como un aviso breve (toast), sin cambios.

- **Available in**: toda la app, cualquier modo.
- **Code**: 00024.
- **Since**: 2026-07-18
- **Last modified**: 2026-07-18
