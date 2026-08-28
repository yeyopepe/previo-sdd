# Changelog de Previo v0.9.6b7 (desde v0.9.5)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subpuntos indentados debajo (sin encabezado, sin enlace). En el Índice, ese mismo tema se colapsa en una sola línea simple `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas no agrupadas se listan como puntos de primer nivel normales en ambos sitios (solo el título en el Índice, punto completo con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - 📂La documentación del proyecto ahora es obligatoria (2 cambios)
  - Nueva skill interna para la gestión de ficheros de documentación
  - Cada skill de flujo tiene ahora un diagrama de workflow
- ✏️[Cambios](#cambios)
  - 📂Disposición y índice de las carpetas de documentación (2 cambios)
  - La comprobación de salud del framework abarca más del historial de cambios
  - La plantilla de planificación ya no se bifurca según si la documentación está configurada
  - Cerrar entradas implementadas ya no te expulsa tras cada una

## ⭐Novedades

- 📂**La documentación del proyecto ahora es obligatoria**:
  - **La documentación técnica, de estilo y de funcionalidades siempre se crea** — `pv-init` ahora siempre crea y prepara la carpeta de documentación de arquitectura, la del style bible y la de funcionalidades en todos los proyectos. Nunca pregunta si las quieres ni permite eliminarlas; un proyecto que no tenga interés en mantener alguna conserva la carpeta vacía en lugar de borrarla. Los proyectos anteriores a este cambio se consideran necesitados de reparación y se derivan a `pv-update`.
  - **Todas las skills se niegan a ejecutarse en un proyecto al que le falte cualquiera de las tres carpetas de documentación** — `pv-new`, `pv-fix`, `pv-how`, `pv-do` y `pv-version` ahora se detienen y te indican que ejecutes `/pv-update` si la carpeta de documentación de arquitectura, de estilo o de funcionalidades falta en la configuración o no está en disco, en vez de omitir esa parte de su trabajo en silencio. Una carpeta vacía que solo contenga su placeholder es correcta y no dispara esto.
- **Nueva skill interna para la gestión de ficheros de documentación** — una nueva skill `pv-internal-doc-files` centraliza cómo cada carpeta de documentación almacena sus ficheros (un fichero numerado por tema, un índice autogenerado, localizar una entrada existente antes de escribir una nueva). `pv-internal-doc-features` ahora se centra únicamente en decidir qué dice una entrada de funcionalidad, y delega la gestión de ficheros en la nueva skill. Es fontanería interna, sin cambios en cómo invocas nada.
- **Cada skill de flujo tiene ahora un diagrama de workflow** — `pv-new`, `pv-fix`, `pv-how` y `pv-version` incluyen cada una un diagrama de su propia secuencia de pasos y bifurcaciones, que la skill trata ahora como la descripción autoritativa de su flujo (igual que ya hacía `pv-update`). El comportamiento no cambia; los flujos solo quedan fijados de forma explícita.

## ✏️Cambios

- 📂**Disposición y índice de las carpetas de documentación**:
  - **Los ficheros de documentación se numeran con tres dígitos y se agrupan por área** — los ficheros de cada carpeta de documentación usan ahora un prefijo de 3 dígitos (`001-`, `002-`…) en vez de dos, y cada fichero lleva una etiqueta de área que se usa para agruparlo en el índice de la carpeta. Las carpetas existentes siguen funcionando; los ficheros nuevos siguen la nueva convención.
  - **El índice de la documentación siempre se regenera, nunca se escribe a mano** — el `INDEX.md` de cada carpeta de documentación se produce ahora de forma determinista a partir de los ficheros de la carpeta (la documentación de funcionalidades ya funcionaba así; las carpetas de arquitectura y de estilo lo hacen ahora también).
- **La comprobación de salud del framework abarca más del historial de cambios** — la auditoría de `pv-update` comprueba ahora también los planes de las entradas ya implementadas, y señala los encabezados de sección traducidos (no solo las etiquetas de campo) en los documentos de cambio/fix, restaurándolos a su forma canónica. Los documentos creados por una versión anterior del framework cuyas plantillas aún estaban traducidas son el caso habitual que esto repara.
- **La plantilla de planificación ya no se bifurca según si la documentación está configurada** — las secciones "Cambios de arquitectura" y "Cambios de estilo" del plan se incluyen ahora simplemente cuando el cambio afecta de verdad a arquitectura o estilo, sin la anterior condición de "solo si esa documentación está configurada" (ya que ahora siempre lo está). Varios encabezados de sección del plan y de la descripción del cambio quedan además fijados en inglés con independencia del idioma configurado, para que los informes de estado sigan funcionando.
- **Cerrar entradas implementadas ya no te expulsa tras cada una** — cerrar entradas desde el ayudante `pv.py` vuelve ahora a listar las entradas pendientes restantes tras cada cierre, de modo que puedes cerrar varias seguidas sin volver a lanzarlo.
