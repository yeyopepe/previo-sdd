# Changelog de Previo v0.9.7b2 (desde v0.9.6)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subpuntos debajo (sin encabezado ni enlace). En el índice, ese mismo tema se reduce a una única línea simple `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas sin agrupar se listan como puntos normales de primer nivel en ambos sitios (solo el título en el índice, el punto completo con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - `pv-do` incorpora hooks de proyecto
- ✏️[Cambios](#cambios)
  - 📂Hooks de proyecto y personalización del pipeline de publicación (4 cambios)

## ⭐Novedades

- **`pv-do` incorpora hooks de proyecto** — `pv-do` ahora ejecuta pasos específicos del proyecto en dos puntos del flujo de implementación: antes de empezar a editar código y después de terminar el código y la documentación sincronizada, pero antes de que el cambio pase a `implemented/`. Los pasos viven en `{workFolder}/stuff/hooks/do/10-before-start.md` y `20-before-finish.md`; un fichero que no existe o que no define pasos se omite en silencio, y un paso de hook cuyo comando falla detiene el flujo en lugar de sortearse.

## ✏️Cambios

- 📂**Hooks de proyecto y personalización del pipeline de publicación**:
  - **Los pasos del pipeline de publicación se dividen en un fichero por punto de inserción** — el único fichero `{workFolder}/stuff/custom-version-pipeline.md` de `pv-version` (un fichero con tres secciones `##`) se sustituye por tres ficheros separados en `{workFolder}/stuff/hooks/version/`: `10-pre-release.md` (antes de resolver el código de versión), `20-post-build.md` (después de copiar los artefactos del entregable) y `30-post-changelog.md` (después del changelog, antes del resumen). Al actualizar un proyecto, ejecuta `/pv-update` una vez para recrear la nueva estructura; un proyecto que todavía tiene el fichero único antiguo con pasos reales se marca con un mapeo sección→fichero para mover los pasos a mano — no se migra automáticamente.
  - **Renombrado del fichero de procedimiento de compilación** — `{workFolder}/stuff/how-to-compile-version.md` pasa a llamarse `how-to-compile.md`. `pv-version` solo lee el nombre nuevo, así que al actualizar un proyecto ejecuta `/pv-update`, que lo renombra en el sitio; si ya existen ambos nombres, pregunta cuál es el vigente.
  - **`pv-init` siembra las carpetas de hooks** — un proyecto recién generado ahora obtiene `{workFolder}/stuff/hooks/` con `hooks/version/` (los tres ficheros de `pv-version`) y `hooks/do/` (los dos ficheros de `pv-do`), cada uno sembrado solo con una cabecera y sin pasos, y nunca se sobrescriben, de modo que los puntos de personalización se descubren desde el principio.
  - **`pv-update` audita los ficheros de hooks y cualquier pipeline heredado** — la comprobación de salud ahora verifica que todos los ficheros de hooks de `pv-version` y `pv-do` estén presentes con su nombre canónico, renombra el que tenga un nombre incorrecto, borra la semilla intacta de un pipeline heredado de fichero único y vuelve a sembrar la nueva estructura, marca para migración manual un pipeline heredado que aún contenga pasos y detecta el renombrado de `how-to-compile-version.md` → `how-to-compile.md`.
