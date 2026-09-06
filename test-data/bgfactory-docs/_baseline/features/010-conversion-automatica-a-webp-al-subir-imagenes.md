# 010 — Conversión automática a WebP al subir imágenes

**Area**: Mesa de juego

Al subir una imagen a la galería de recursos — tanto al dar de alta un recurso nuevo desde el panel "Recursos" en modo edición, como al reemplazar el fichero de un recurso ya existente desde su modal de edición — la imagen se convierte automáticamente a formato WebP antes de guardarse (compresión con pérdida, calidad muy alta, imperceptible a la vista), para reducir el espacio que ocupa en el autoguardado del navegador, en el HTML exportado y en el JSON de exportar/importar componentes. El flujo de subida no cambia en nada: mismo selector de fichero, mismos pasos, sin ningún indicador de carga adicional.

Solo se convierten los formatos de origen PNG, JPG y JPEG; si el fichero subido ya es WebP no se reconvierte, y los SVG (vectoriales) y GIF (pueden ser animados) se guardan siempre tal cual, sin conversión. Si la conversión no puede realizarse por cualquier motivo, el fichero original se guarda sin transformar, sin bloquear la subida ni mostrar ningún error. Esta conversión solo afecta a subidas nuevas a partir de esta funcionalidad; las imágenes ya guardadas no se tocan ni se reconvierten automáticamente — los 38 recursos de imagen por defecto de la galería (ver [Panel flotante de recursos](006-panel-flotante-de-recursos-con-filtro-de-texto.md)) sí se migraron a WebP como parte puntual de esta implementación.

- **Available in**: modo edición.
- **Code**: 00073.
- **Since**: 2026-07-23
- **Last modified**: 2026-07-23
