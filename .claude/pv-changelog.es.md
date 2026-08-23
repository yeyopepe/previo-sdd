# Changelog de Previo v0.9.6b3 (desde v0.9.5)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten asunto. En la sección de detalle, un tema se representa como `- 📂**{Tema}**:` con sus entradas anidadas como sub-bullets indentados debajo (sin encabezado, sin enlace). En el Índice, ese mismo tema se colapsa en una única línea plana `📂{Tema} (N cambios)`, sin listar sus entradas miembro. Las entradas sin agrupar se listan como bullets normales de primer nivel en ambos sitios (título simple en el Índice, bullet completo con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - Las skills ahora siguen un diagrama de flujo de trabajo explícito
  - Las carpetas de documentación comparten un único motor de gestión de ficheros
- ✏️[Cambios](#cambios)
  - La documentación de arquitectura ahora sigue una checklist de contenido
  - La documentación de funcionalidades ahora se redacta a partir de un resumen, no de contenido ya escrito
  - El nombrado de ficheros de documentación ahora es coherente en las tres carpetas de documentación

## ⭐Novedades

- **Las skills ahora siguen un diagrama de flujo de trabajo explícito** — `pv-fix`, `pv-how`, `pv-new` y `pv-version` leen ahora, cada una, un diagrama de flujo de trabajo en Mermaid dedicado como fuente de verdad para su secuencia de pasos y sus bifurcaciones, en lugar de basarse únicamente en instrucciones en prosa.
- **Las carpetas de documentación comparten un único motor de gestión de ficheros** — se introduce `pv-internal-doc-files`, un procedimiento compartido que ahora gestiona de forma coherente la numeración de ficheros, el índice y la localización/escritura de entradas en las tres carpetas de documentación (funcionalidades, arquitectura, guía de estilo).

## ✏️Cambios

- **La documentación de arquitectura ahora sigue una checklist de contenido** — al actualizar `docs.tech.architectureDocDir`, el framework ahora contrasta el cambio con una lista fija de categorías de contenido (componentes, contratos, flujos de datos, decisiones, dependencias, modelo de datos, configuración) para decidir qué ya está cubierto y qué falta por documentar, en lugar de basarse solo en pautas de estilo de escritura.
- **La documentación de funcionalidades ahora se redacta a partir de un resumen, no de contenido ya escrito** — al actualizar `docs.functional.featuresDocPathDir`, el framework ahora recibe un resumen de lo implementado y redacta él mismo la entrada de la funcionalidad (decidiendo si es una edición en el sitio o una entrada nueva, qué diagramas se trasladan y la redacción final), en lugar de recibir el texto ya terminado para simplemente guardarlo.
- **El nombrado de ficheros de documentación ahora es coherente en las tres carpetas de documentación** — los ficheros de `architectureDocDir` y `styleBibleDocDir` usan ahora la misma convención de numeración y de etiquetado por área que `featuresDocPathDir` (un prefijo de 3 dígitos más un campo `Area`, p. ej. `001-{slug}.md`), en sustitución del anterior prefijo de 2 dígitos. Al actualizar, los ficheros existentes en esas dos carpetas deben renombrarse a la nueva convención.
