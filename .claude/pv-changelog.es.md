# Changelog de Previo v0.9.8 (desde v0.9.7)

## Índice

- ⭐[Novedades](#novedades)
  - 📂Autoactualización del framework (2 cambios)
  - 📂Mantenimiento de arquitectura y documentación (2 cambios)
  - Guía de usuario
  - Framework de anotaciones de revisión en mockups
- ✏️[Cambios](#cambios)
  - El ciclo de vida de los mockups ahora tiene acciones explícitas de cierre y descripción
  - Todas las skills ahora verifican la instalación del framework antes de ejecutarse
  - El número máximo de caracteres de la descripción del cambio ahora es configurable

## ⭐Novedades

- 📂**Autoactualización del framework**:
  - **`/pv-update install` instala o actualiza el propio framework** — un nuevo modo explícito que resuelve la última versión oficial de GitHub (o la que se le pida), avisa sobre pre-releases y sobre reinstalaciones de la misma versión, se niega a hacer downgrade, y solo instala después de que el usuario confirme por su nombre la versión exacta resuelta. Si tiene éxito, ejecuta automáticamente la auditoría de configuración habitual contra la versión recién instalada.
  - **`pv.py` puede instalar una nueva versión de Previo desde su propio menú** — una nueva opción "Instalar nueva versión de Previo" reproduce el mismo flujo de resolución-confirmación-instalación que `/pv-update install`, sin necesidad de abrir Claude Code.
- 📂**Mantenimiento de arquitectura y documentación**:
  - **Nueva skill: `/pv-review-architecture`** — analiza el código fuente real del proyecto contra una checklist de principios de diseño agnósticos del lenguaje (separación de responsabilidades, SOLID, tamaño de fichero, nomenclatura, capas, DRY/KISS) y genera una lista numerada de propuestas de reorganización puras (dividir, fusionar, reubicar, renombrar), sin añadir ni eliminar nunca funcionalidad. Para cada propuesta aceptada, puede convertirla en una idea anotada (`pv-todo`) o en un cambio documentado (`pv-new`).
  - **Nueva skill: `/pv-review-doc-tech`** — reorganiza las carpetas de documentación técnica del proyecto (`architectureDocDir`, `styleBibleDocDir`) solo a nivel de estructura: mueve contenido mal ubicado al fichero/categoría correcto, fusiona duplicados y corrige agrupaciones incorrectas, sin borrar, reescribir ni añadir contenido en ningún caso.
- **Nueva guía de usuario** — un documento completo de incorporación (`pv-guide`) que recorre la configuración inicial, el flujo natural de definición-planificación-implementación de un cambio, la preparación de versiones y las skills de mantenimiento, pensado para alguien nuevo en el framework.
- **Framework de anotaciones de revisión en mockups** — los mockups HTML (`design_*.html`) ahora incorporan una barra de herramientas de revisión estándar y autocontenida (notas fijadas a elementos, notas generales, mostrar/ocultar, guardar), que permite a quien revisa dejar comentarios directamente sobre el mockup en lugar de solo en el chat.

## ✏️Cambios

- **El ciclo de vida de los mockups ahora tiene acciones explícitas de cierre y descripción** — tanto la skill de mockups HTML como la de ASCII incorporan una acción `ensure-closed` (que resuelve cualquier anotación pendiente en un mockup antes de considerarlo definitivo) y una acción `describe` (un resumen en texto plano del contenido visual de un mockup para que otra skill lo use como referencia, sin leer el fichero en bruto). `pv-new`, `pv-fix` y `pv-how` ahora pasan por estas acciones en los puntos correspondientes de su flujo en lugar de leer los ficheros de mockup directamente.
- **Todas las skills ahora verifican la instalación del framework antes de ejecutarse** — `pv-fix`, `pv-how`, `pv-do`, `pv-new`, `pv-todo`, `pv-status` y el resto de skills `pv-*` comprueban ahora el estado de la instalación del framework como primer paso, y se detienen con un mensaje claro que señala `/pv-update install` si algo falla, en lugar de dar un error menos claro más adelante en su propio flujo.
- **El número máximo de caracteres de la descripción del cambio ahora es configurable** — la vista de detalle de `pv.py` incorpora un nuevo ajuste para cambiar cuántos caracteres de la descripción de un cambio se muestran, junto al ajuste ya existente de ancho de terminal.
