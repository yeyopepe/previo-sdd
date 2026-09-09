# Changelog de Previo v0.9.7b3 (desde v0.9.6)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten un asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subpuntos con sangría debajo (sin encabezado, sin enlace). En el Índice, ese mismo tema se colapsa en una única línea simple `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas sin agrupar se listan como puntos de primer nivel normales en ambos sitios (solo el título en el Índice, el punto completo con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - 📂Hooks de proyecto para el flujo de implementación (2 cambios)
- ✏️[Cambios](#cambios)
  - 📂La personalización del pipeline de release pasa a ficheros de hook (4 cambios)
- ❌[Eliminado](#eliminado)
  - Se elimina la plantilla del pipeline de release en fichero único heredada

## ⭐Novedades

- 📂**Hooks de proyecto para el flujo de implementación**:
  - **`pv-do` ejecuta pasos del proyecto antes y después de implementar** — `pv-do` ahora busca dos ficheros de hook opcionales en `{workFolder}/stuff/hooks/do/` (`10-before-start.md`, que se ejecuta antes de editar código; `20-before-finish.md`, que se ejecuta después de actualizar el código y la documentación y antes de que la carpeta del cambio/fix se mueva a `implemented/`). Cada uno contiene pasos definidos por el proyecto para ejecutar en ese punto; un fichero ausente o sin pasos se omite en silencio, así que los proyectos que no los usen no se ven afectados. Si un paso falla, `pv-do` se detiene y lo explica en lugar de buscar una alternativa.
  - **La vía rápida de `pv-fix` ejecuta los mismos hooks** — un fix trivialmente rápido edita el código directamente sin pasar por `pv-do`, y ahora ejecuta los mismos hooks `10-before-start` / `20-before-finish` en torno a esa edición. No hay un conjunto de hooks `fix/` aparte: la vía rápida comparte los de `pv-do`.

## ✏️Cambios

- 📂**La personalización del pipeline de release pasa a ficheros de hook**:
  - **Los pasos personalizados de `pv-version` son ahora un fichero por punto de inserción** — el único `{workFolder}/stuff/custom-version-pipeline.md` (con sus secciones `## Before starting` / `## In the middle` / `## At the end`) se sustituye por tres ficheros en `{workFolder}/stuff/hooks/version/`: `10-pre-release.md`, `20-post-build.md`, `30-post-changelog.md`. Cada uno se ejecuta en el mismo punto del flujo que la sección a la que sustituye. Los proyectos que hubieran añadido pasos al pipeline personalizado deben mover los pasos de cada sección al fichero de hook correspondiente (ver más abajo).
  - **`pv-update` migra o marca el fichero de pipeline antiguo** — al ejecutar `pv-update` ahora se detecta un `custom-version-pipeline.md` anterior a los hooks: una plantilla intacta (sin pasos) se elimina y se vuelve a sembrar la nueva estructura de hooks automáticamente; una que contiene pasos escritos por el proyecto se reporta como migración manual pendiente, con la correspondencia exacta sección→fichero, y no se corrige de forma automática. Hasta que se migre, esos pasos dejan de ejecutarse.
  - **El fichero del procedimiento de build se renombra a `how-to-compile.md`** — `{workFolder}/stuff/how-to-compile-version.md` pasa a ser `how-to-compile.md`. `pv-version` solo lee el nombre nuevo. `pv-update` renombra un fichero existente in situ; si existen ambos nombres, pregunta cuál es el vigente en lugar de adivinarlo.
  - **`pv-init` genera la nueva estructura `stuff/hooks/`** — un proyecto recién inicializado obtiene ahora `stuff/hooks/` con una subcarpeta por cada skill que expone hooks (`version/`, `do/`), presembrada con ficheros de hook que solo tienen la cabecera (sin pasos). Los ficheros existentes nunca se sobrescriben, así que los pasos que un proyecto ya hubiera añadido sobreviven a una reinicialización y a `pv-update`.

## ❌Eliminado

- **Se elimina la plantilla del pipeline de release en fichero único heredada** — la plantilla `custom-version-pipeline.md` que se distribuía con `pv-version` desaparece, sustituida por las plantillas de hook por punto de inserción. Ver la migración que gestiona `pv-update` más arriba.
