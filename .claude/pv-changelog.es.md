# Changelog de Previo v0.9.8b11 (desde v0.9.7)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subelementos indentados debajo (sin encabezado, sin enlace). En el índice, ese mismo tema se colapsa en una única línea plana `📂{Tema} (N cambios)` sin listar sus entradas miembro. Las entradas sin agrupar se listan como elementos normales de primer nivel en ambos sitios (título simple en el índice, elemento completo con título en negrita más resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - 📂Skills de mantenimiento (2 cambios)
  - 📂Instalar y actualizar el propio framework (2 cambios)
  - Los mockups ahora recurren al código real y señalan huecos de documentación
  - Recuento de mockups en la tarjeta de detalle del estado
  - Los mockups ahora se pueden anotar directamente en el navegador
  - Nuevas acciones de mockups para resolver anotaciones y describir su contenido
- ✏️[Cambios](#cambios)
  - 📂Estructura de carpetas de las entradas (2 cambios)
  - 📂Ciclo de revisión de mockups (3 cambios)
  - La comprobación de versión del framework ahora es un único script compartido
  - Ajustes de texto y navegación en el menú de `pv.py`
  - La generación de mockups ya no resuelve por su cuenta la guía de estilo ni el idioma
  - El instalador ya no ofrece una versión anterior a la instalada

## ⭐Novedades

- 📂**Skills de mantenimiento**:
  - **`/pv-review-doc-tech` reorganiza la documentación técnica** — un nuevo pase periódico opcional que relee por completo cada carpeta bajo `docs.tech` (arquitectura y guía de estilo) y la reorganiza —moviendo, agrupando o consolidando contenido— sin reescribir, borrar ni añadir hechos en ningún momento. Regenera automáticamente el índice de la documentación y señala para que decida el usuario cualquier cosa que no pueda corregir de forma segura (como un cambio de espacio de nombres necesario).
  - **`/pv-review-architecture` propone reorganizaciones de código** — un nuevo pase opcional que revisa el código fuente real frente a una checklist fija (separación de responsabilidades, tamaño de ficheros/clases, SOLID, DRY, KISS, acoplamiento, estructura de carpetas, naming) y devuelve una lista numerada de propuestas de reorganización. Nunca cambia el comportamiento ni escribe código por sí mismo; para cada propuesta que el usuario elija, la deriva al cuaderno de ideas o al flujo de cambios estándar.
- 📂**Instalar y actualizar el propio framework**:
  - **`pv-update` ahora puede instalar o actualizar el framework** — un nuevo modo `/pv-update install` resuelve la versión solicitada (la última versión oficial, o una concreta), muestra siempre también la última pre-release, y solo instala después de que el usuario confirme explícitamente por nombre la versión exacta resuelta. Rechaza cualquier downgrade de plano. Si tiene éxito, vuelve a verificar y reparar automáticamente la configuración del proyecto frente a la versión recién instalada.
  - **`pv.py` puede instalar una nueva versión de Previo directamente desde su menú** — una nueva opción "Install new Previo version" dentro de Configuration lista las versiones disponibles (la última oficial, y la pre-release si es más reciente) e instala la elegida tras confirmación explícita, sin necesitar Claude Code.
- **Los mockups ahora recurren al código real y señalan huecos de documentación** — al generar un mockup visual, si la guía de estilo no cubre algo necesario, la skill de mockups ahora busca la convención real ya usada en el código de la app antes de recurrir a un placeholder neutro. Cualquier hueco de este tipo se informa de vuelta para poder registrarlo como tarea de documentación pendiente en vez de reutilizarlo en silencio.
- **Recuento de mockups en la tarjeta de detalle del estado** — la vista de detalle en terminal de `pv-status` ahora muestra cuántos ficheros de mockup tiene una entrada, por separado del resto de sus ficheros adicionales.
- **Los mockups ahora se pueden anotar directamente en el navegador** — cada mockup `design_*.html` generado ahora incluye una barra de revisión ligera integrada: puedes anclar una nota a cualquier elemento o añadir una nota general, verlas listadas en dos paneles (generales y vinculadas), y guardar el fichero ya anotado. Esto sustituye a describir los cambios deseados en prosa por chat, permitiendo anclarlos directamente sobre el propio diseño visual.
- **Nuevas acciones de mockups para resolver anotaciones y describir su contenido** — la skill de mockups incorpora `ensure-closed` (resuelve toda anotación pendiente de un mockup, aplicando el cambio pedido y preguntando directamente si una nota es ambigua) y `describe` (una descripción en texto plano del contenido visual de un mockup, para otra skill que necesite una referencia sin abrir el fichero).

## ✏️Cambios

- 📂**Estructura de carpetas de las entradas**:
  - **Los mockups ahora viven en su propia subcarpeta `mockups/`** — los ficheros de mockup visual (`design_*.html`/`design_*.txt`) de una entrada de cambio/fix ahora se guardan en una subcarpeta dedicada `mockups/` en vez de sueltos junto al resto de documentos de la entrada.
  - **Los ficheros de navegación y datos perdieron el prefijo `design_`** — `design_navigation_*.md` y `design_data_*.md` pasan a llamarse `navigation_*.md` y `data_*.md`. Las entradas existentes con la estructura anterior se migran automáticamente la próxima vez que se ejecute `pv-update`.
- 📂**Ciclo de revisión de mockups**:
  - **Los mockups vuelven a presentarse solo cuando toda anotación está resuelta** — antes de volver a mostrar un mockup al usuario, `pv-new`/`pv-fix` ahora resuelven automáticamente cualquier anotación pendiente hecha en el navegador, en vez de depender de que el usuario describa el cambio deseado en el chat.
  - **`pv-how` ya no da por hecho que los mockups de una entrada están limpios** — comprueba por su cuenta si hay anotaciones pendientes antes de analizar una entrada, aunque `pv-new`/`pv-fix` ya la hubieran validado antes en la misma sesión.
  - **`pv-how` ya no abre los ficheros de mockup directamente** — ahora obtiene su referencia visual para planificar a través de la propia descripción que genera la skill de mockups del fichero, en vez de leer el HTML crudo.
- **La comprobación de versión del framework ahora es un único script compartido** — cada skill ahora verifica que el framework esté correctamente instalado y actualizado a través de un único script de comprobación compartido, en vez de que cada una haga su propia comparación interna; si el framework no está correctamente instalado, ahora se dirige al usuario al nuevo modo de instalación de `pv-update`.
- **Ajustes de texto y navegación en el menú de `pv.py`** — "Check Previo versions" pasa a ser "Check product versions" y "Change max character width" pasa a ser "Change terminal max character width"; la opción de salir de cualquier menú ahora se selecciona con `X` en vez de con un número al final.
- **La generación de mockups ya no resuelve por su cuenta la guía de estilo ni el idioma** — la skill de mockups ahora recibe los fragmentos relevantes de la guía de estilo y el idioma del texto de ejemplo de quien la invoca, en vez de resolverlos por su cuenta. Esto le permite funcionar de forma autocontenida si se copia a otro proyecto.
- **El instalador ya no ofrece una versión anterior a la instalada** — tanto `pv-update install` como el propio menú de instalación de `pv.py` filtran cualquier versión listada anterior a la instalación actual, y avisan antes de reinstalar la misma versión exacta desde cero.
