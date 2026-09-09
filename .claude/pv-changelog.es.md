# Changelog de Previo v0.9.7b1 (desde v0.9.6)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subpuntos indentados debajo (sin encabezado, sin enlace). En el índice, ese mismo tema se colapsa en una única línea simple `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas no agrupadas se listan como puntos de primer nivel normales en ambos sitios (solo el título en el índice, el punto completo con título en negrita y resumen en el detalle).

## Índice

- ✏️[Cambios](#cambios)
  - 📂Personalización de proyecto de pv-version (2 cambios)

## ✏️Cambios

- 📂**Personalización de proyecto de pv-version**:
  - **La personalización del pipeline de versión pasa de un único fichero a ficheros de hook por punto** — se retira el fichero único `{workFolder}/stuff/custom-version-pipeline.md` (con sus tres secciones `## Before starting` / `## In the middle` / `## At the end`). Ahora `pv-version` ejecuta los pasos específicos del proyecto desde un fichero por punto de inserción bajo `{workFolder}/stuff/hooks/version/`: `10-pre-release.md` (antes de resolver el código de versión), `20-post-build.md` (después de que los artefactos del entregable estén en `versions/{XXXX}/files/`) y `30-post-changelog.md` (después del changelog, antes del resumen final). `pv-init` siembra los tres ficheros (encabezado, sin pasos); un fichero sin pasos se omite en silencio, así que un proyecto que nunca los toca se comporta igual que antes. **Al actualizar:** ejecuta `/pv-update` una vez para crear `stuff/hooks/version/` y sus ficheros semilla. Si un proyecto ya tiene `custom-version-pipeline.md` con pasos propios, `/pv-update` lo señala con un mapeo sección→fichero (`## Before starting` → `10-pre-release.md`, `## In the middle` → `20-post-build.md`, `## At the end` → `30-post-changelog.md`); hay que mover los pasos a los ficheros de hook correspondientes a mano y borrar el fichero antiguo — `pv-version` ya no lo lee.
  - **El fichero del procedimiento de build se renombra a `how-to-compile.md`** — `pv-version` lee el procedimiento de build del entregable desde `{workFolder}/stuff/how-to-compile.md` en lugar del anterior `how-to-compile-version.md`, y solo reconoce el nombre nuevo. **Al actualizar:** `/pv-update` renombra el fichero en su sitio cuando solo está presente el nombre antiguo. Si existen a la vez `how-to-compile-version.md` y `how-to-compile.md`, `/pv-update` informa de ambos y no los toca para que el usuario los reconcilie (conservar el que esté vigente, borrar el otro).
