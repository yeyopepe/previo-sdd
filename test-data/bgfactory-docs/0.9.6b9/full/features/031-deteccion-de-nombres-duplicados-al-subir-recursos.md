# 031 — Detección de nombres duplicados al subir recursos
**Area**: Recursos e imágenes

Al añadir un recurso cuyo nombre ya existe en la galería (sin distinguir mayúsculas ni tildes), se pregunta si se quiere reemplazar el recurso existente o cancelar. En una subida en lote, los recursos sin conflicto se cargan directamente y los que colisionan se agrupan en una única ventana de confirmación de reemplazo; un nombre repetido dentro del propio lote cuenta como conflicto a partir del segundo fichero.

Cada subida en lote termina con un resumen de cuántos recursos se añadieron, cuántos se reemplazaron y cuántos se omitieron por formato o por estar en subcarpetas.

- **Available in**: Modo edición (al subir uno o varios recursos)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
