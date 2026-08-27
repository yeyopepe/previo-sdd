# Changelog de Previo v0.9.6b6 (desde v0.9.5)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subpuntos debajo (sin encabezado, sin enlace). En el índice, ese mismo tema se colapsa en una única línea plana `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas no agrupadas se listan como puntos de primer nivel normales en ambos sitios (solo el título en el índice, punto completo con título en negrita y resumen en el detalle).

## Índice

- ⭐[Nuevo](#nuevo)
  - Las skills ahora siguen un diagrama de flujo explícito
  - Motor común de gestión de ficheros para las carpetas de documentación
  - Resolución de rutas por clave lógica
- ✏️[Cambios](#cambios)
  - 📂Las tres carpetas de documentación ahora son obligatorias (5 cambios)
  - 📂Generación de documentación reestructurada (3 cambios)
  - La vía rápida de fix trivial ya no depende de que las carpetas de documentación estén configuradas
  - Las plantillas de plan y descripción protegen más marcadores estructurales
  - El lanzador recarga la lista de entradas cerrables tras cada cierre

## ⭐Nuevo

- **Las skills ahora siguen un diagrama de flujo explícito** — `pv-fix`, `pv-how`, `pv-new` y `pv-version` leen ahora cada una un diagrama de flujo Mermaid propio (`workflow.*.md` junto a la skill) como fuente autoritativa de su secuencia de pasos y sus ramas; los pasos en prosa son solo el detalle de cada nodo, y si ambos difieren, manda el diagrama.
- **Motor común de gestión de ficheros para las carpetas de documentación** — se introduce `pv-internal-doc-files`, un procedimiento compartido que gestiona la numeración de ficheros, la regeneración de `INDEX.md` y la localización/escritura de entradas para las tres carpetas de documentación (funcionalidades, arquitectura, biblia de estilo) con una única convención consistente.
- **Resolución de rutas por clave lógica** — se añade `resolve-path.py` (propiedad de `pv-init`), el único sitio que convierte una clave lógica (`workFolder`, `sourcecodeDir`, `changesDir`, `versionsDir`, `stuffDir`, `architectureDocDir`, `styleBibleDocDir`, `featuresDocPathDir`) en una ruta absoluta. Ahora cada skill de flujo le pide las rutas en vez de parsear `pv-context.json` por su cuenta; ante cualquier fallo, la skill llamante para y remite al usuario a `/pv-update`.

## ✏️Cambios

- 📂**Las tres carpetas de documentación ahora son obligatorias**:
  - **`docs.functional.featuresDocPathDir`, `docs.tech.architectureDocDir` y `docs.tech.styleBibleDocDir` son obligatorias** — `pv-init` configura y hace scaffold de las tres siempre; el schema de `pv-context.json` ahora las marca como obligatorias. Una configuración a la que le falte cualquiera de ellas es un estado roto, no un modo admitido de "documentación desactivada". **Al actualizar, ejecuta `/pv-update`** — añade cualquier carpeta de documentación ausente con su ruta por defecto y un `INDEX.md` placeholder vacío.
  - **`pv-do` para en vez de saltarse el paso en silencio** — donde antes se saltaba una actualización de documentación cuando la ruta correspondiente no estaba configurada, ahora resuelve las tres al principio y se detiene (dirigiendo al usuario a `/pv-update`) si alguna no puede resolverse a una carpeta real. Una carpeta que existe pero solo contiene su placeholder sigue siendo válida.
  - **`pv-how` exige que las carpetas de documentación se resuelvan** — la planificación ya no "continúa sin ellas" cuando faltan rutas de documentación; una carpeta de documentación irresoluble detiene el análisis y remite al usuario a `/pv-update`.
  - **`pv-version` exige que las carpetas de documentación se resuelvan** — `copy-docs.py` ya no se salta el zip de una documentación por una ruta sin configurar; una carpeta de documentación ausente o inexistente aborta ahora el paso, y la versión incluye siempre las tres documentaciones comprimidas.
  - **`pv-init` trata una carpeta de documentación ausente como estado roto, no como configuración incompleta** — en un proyecto ya inicializado, una carpeta de documentación obligatoria que se haya perdido dirige a `pv-init` a su rama de reparación (`pv-update`) en vez de al cuestionario de campos opcionales. Renunciar a *mantener* un área de documentación sigue estando bien: el campo y su carpeta vacía se conservan.
- 📂**Generación de documentación reestructurada**:
  - **Numeración de ficheros unificada en las tres carpetas de documentación** — los ficheros de `architectureDocDir` y `styleBibleDocDir` usan ahora la misma convención que `featuresDocPathDir`: un prefijo de 3 dígitos más un campo `**Area**` (p. ej. `001-{slug}.md`), en sustitución del prefijo de 2 dígitos anterior, con `INDEX.md` siempre regenerado en vez de escrito a mano. Los ficheros existentes en esas dos carpetas deberían renombrarse a la nueva convención al actualizar.
  - **La documentación de arquitectura sigue una lista de contenidos** — al actualizar `docs.tech.architectureDocDir`, el framework contrasta ahora el cambio con una lista fija de categorías de contenido (componentes, contratos, flujos de datos, decisiones, dependencias, modelo de datos, configuración) para decidir qué está ya cubierto y qué falta por documentar, además de la guía de estilo de redacción que ya existía.
  - **La documentación de funcionalidades se redacta a partir de un resumen** — `pv-internal-doc-features` recibe ahora un resumen de lo implementado más el contexto ya recopilado y redacta la entrada de funcionalidad él mismo (edición in situ o entrada nueva, qué diagramas se arrastran, redacción), en vez de que se le entregue el texto ya terminado para guardarlo; delega toda la ubicación de ficheros en `pv-internal-doc-files`.
- **La vía rápida de fix trivial ya no depende de que las carpetas de documentación estén configuradas** — los criterios de `pv-fix` para el atajo `fast` decían antes "si `docs.tech.*` está configurada"; como esas carpetas ahora siempre lo están, ese condicional desaparece. Las reglas en sí (un cambio de documentación solo de valores sigue siendo `fast`; un cambio significativo de arquitectura o estilo no) no cambian.
- **Las plantillas de plan y descripción protegen más marcadores estructurales** — los encabezados de sección siempre presentes de `plan.md` (`## (a) Functional notes`, `## (b) Technical solution`, `## (e) Verification`) y el encabezado `## Full description` de `description.md` están ahora marcados como etiquetas estructurales fijas en inglés. La comprobación de marcadores de `pv-update` también recorre ahora `plan.md` dentro de `implemented/` y reconoce los encabezados traducidos por versiones antiguas del framework como algo a restaurar, en cualquier idioma.
- **El lanzador recarga la lista de entradas cerrables tras cada cierre** — en `pv.py`, cerrar una entrada implementada vuelve a listar ahora las restantes para poder cerrar varias seguidas, en vez de volver al menú tras un único cierre.
