# Changelog de Previo v0.9.8rc1 (desde v0.9.7)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten un mismo asunto. En la sección de detalle, un tema se representa como `- 📂**{Tema}**:` con sus entradas anidadas como sub-viñetas indentadas debajo (sin encabezado, sin enlace). En el índice, ese mismo tema se reduce a una única línea simple `📂{Tema} (N cambios)`, sin listar sus entradas miembro. Las entradas no agrupadas aparecen como viñetas normales de primer nivel en ambos sitios (título simple en el índice, viñeta completa con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - Nuevo framework de anotaciones de revisor sobre mockups HTML
  - 📂Autoinstalación del framework (2 cambios)
  - 📂Autorreparación de la auditoría de `pv-update` (2 cambios)
  - 📂Nuevas skills de mantenimiento (2 cambios)
- ✏️[Cambios](#cambios)
  - Los mockups y sus ficheros de apoyo se trasladan a una nueva estructura de carpetas
  - La guía propia del framework se traslada a su propia carpeta
  - Ninguna skill `pv-*` lee ni edita ya un fichero de mockup directamente
  - Se aclaran las etiquetas del menú de configuración de `pv.py`
  - Los menús de `pv.py` ahora se cierran con la tecla "X"

## ⭐Novedades

- **Nuevo framework de anotaciones de revisor sobre mockups HTML** — cada mockup incorpora ahora un runtime autocontenido que permite al revisor fijar notas sobre un elemento concreto o dejar notas generales, sin salir del propio mockup. Antes de volver a presentarlo, el framework resuelve automáticamente cada nota abierta: si detecta con confianza qué cambio pide, lo aplica directamente sobre el mockup y cierra la nota; si la nota es ambigua, o si su elemento vinculado ya no existe en el mockup ("nota huérfana"), pregunta al revisor antes de tocar nada. Ninguna skill `pv-*` (`pv-new`, `pv-fix`, `pv-how`) lee ni edita ya un fichero de mockup directamente: todas pasan exclusivamente por las acciones `describe` (referencia visual en texto) y `ensure-closed` (resolución de anotaciones) de la skill de mockups configurada, lo que además permite sustituir la skill de mockups HTML por una propia (Figma, librería de componentes, etc.) sin tocar el resto del framework.
- 📂**Autoinstalación del framework**:
  - **`pv-update` incorpora un modo de instalación explícito (`/pv-update install`)** para instalar o actualizar el propio framework `pv-*` (no solo auditar su configuración) a una versión igual o posterior a la instalada, mediante un protocolo estricto de resolución, confirmación e instalación que nunca degrada la versión de forma silenciosa y siempre indica el nombre exacto de la versión de destino antes de tocar nada; si tiene éxito, encadena automáticamente con el modo de auditoría/reparación existente para verificar la versión recién instalada.
  - **El menú de configuración de `pv.py` incorpora la opción "Instalar nueva versión de Previo"**, conectada al mismo mecanismo de instalación que `/pv-update install`, que permite actualizar o reinstalar el framework sin pasar por Claude Code.
- 📂**Autorreparación de la auditoría de `pv-update`**:
  - **La auditoría de `pv-update` ahora detecta y corrige sintaxis de plantilla que haya quedado sin resolver** — si un `description.md`/`plan.md` generado todavía muestra la marca de plantilla `[[[Etiqueta]]]` en bruto en lugar de la etiqueta ya resuelta, la auditoría elimina automáticamente los corchetes.
  - **La auditoría de `pv-update` ahora migra los ficheros antiguos de mockups/datos a la convención actual de carpetas y nombres** — los mockups sueltos en la raíz de una entrada (previos a la subcarpeta `mockups/`) se trasladan a `mockups/`, y los ficheros `design_navigation_*.md`/`design_data_*.md` que aún conservan el prefijo retirado `design_` se renombran a `navigation_*.md`/`data_*.md`, ambos casos de forma automática.
- 📂**Nuevas skills de mantenimiento**:
  - **`pv-review-doc-tech`** vuelve a leer por completo cada carpeta `docs.tech` configurada y la reorganiza — trasladando o fusionando contenido, corrigiendo contenido archivado bajo el Área incorrecta — sin añadir, eliminar ni reescribir nunca un dato.
  - **`pv-review-architecture`** revisa el código fuente real del proyecto frente a una checklist estructural fija (separación de responsabilidades, tamaño, SOLID, DRY, KISS, acoplamiento, nomenclatura) y produce una lista numerada de propuestas de reorganización pura (mover/dividir/fusionar/renombrar, nunca funcionalidad nueva o eliminada); para cada propuesta que el usuario acepta, la enruta a `pv-todo` o `pv-new` según lo que elija.

## ✏️Cambios

- **Los mockups y sus ficheros de datos/navegación de apoyo se trasladan a una nueva estructura de carpetas** — los mockups `design_*.html`/`design_*.txt` ahora residen en una subcarpeta `mockups/` dentro de cada entrada de cambio/fix en lugar de estar sueltos en su raíz, y `design_navigation_*.md`/`design_data_*.md` se renombran a `navigation_*.md`/`data_*.md` (siguen sueltos en la raíz de la entrada). `pv-new`, `pv-fix`, `pv-how`, `pv-todo` y `pv-status` se actualizaron todos a esta convención. **Acción requerida tras actualizar**: ejecuta `/pv-update` — detecta y migra automáticamente cualquier entrada que aún esté en la estructura antigua.
- **La guía propia del framework se traslada a su propia carpeta** — `pv-guide.en.md`/`pv-guide.es.md` ahora residen en `.claude/pv-doc/pv-guide/` en lugar de directamente en `.claude/pv-doc/`. **Acción requerida tras actualizar**: vuelve a ejecutar `/pv-update` o reinstala, para que se actualice cualquier referencia del proyecto a la ruta plana antigua.
- **Ninguna skill `pv-*` lee ni edita ya un fichero de mockup directamente** — `pv-new`, `pv-fix` y `pv-how` pasan ahora exclusivamente por la acción `describe` de la skill de mockups configurada para obtener una referencia visual en texto plano, y por su acción `ensure-closed` para resolver las anotaciones de revisor pendientes; un proyecto que aporte una implementación propia de `framework.skills.mockups` debe soportar ahora ambas acciones (además de las entradas `style_context`/`language`) para seguir siendo un sustituto directo válido.
- **Se aclaran dos etiquetas del menú de configuración de `pv.py`** — "Change max character width" pasa a ser "Change terminal max character width", y "Check Previo versions" pasa a ser "Check product versions".
- **Los menús de `pv.py` ahora se cierran con la tecla "X" en lugar de una opción numerada al final**, de modo que la opción de salir ya no cambia de número al añadir o quitar elementos del menú.
