# Changelog de Previo v0.9.7 (desde v0.9.6)

## Índice

- ⭐[Novedades](#novedades)
  - 📂Sistema de hooks de proyecto (6 cambios)
- ✏️[Cambios](#cambios)
  - 📂Sistema de hooks de proyecto (4 cambios)
  - El scaffolding de `pv-init` ahora siembra la carpeta de hooks
- ❌[Eliminado](#eliminado)
  - Se elimina el antiguo pipeline personalizado de fichero único de `pv-version`

## ⭐Novedades

- 📂**Sistema de hooks de proyecto**:
  - **Se añaden puntos de inserción de hooks por flujo en todo el framework** — `pv-do`, `pv-how`, `pv-new`, `pv-fix` y `pv-version` exponen ahora puntos de personalización fijos como ficheros individuales bajo `{workFolder}/stuff/hooks/<flow>/<NN>-<slug>.md`, un fichero por punto de inserción, que contiene cero o más pasos (comando, salida esperada, notas). Un hook sin pasos se omite silenciosamente; un paso que falla detiene el flujo y explica el motivo. `stuff/` incorpora una subcarpeta `hooks/` con un subdirectorio por cada skill que expone hooks — ejecutar `pv-init` en un proyecto nuevo o `pv-update` en uno existente siembra los nuevos ficheros automáticamente, sin sobrescribir ningún contenido ya creado por el proyecto.
  - **`pv-how` incorpora dos puntos de hook** — uno antes de que empiece el análisis técnico, para cargar o actualizar contexto como tipos generados, un volcado del esquema de base de datos o documentación externa (se omite cuando el usuario elige implementar un `plan.md` ya existente en lugar de volver a analizar), y otro después de que se escriban `plan.md` y su puntuación de riesgo, antes de pedir al usuario que implemente, para validar o publicar el plan (p. ej. abrir un ticket).
  - **`pv-new` incorpora un punto de hook** — al terminar la entrada (y cualquier mockup), justo antes de pasar el control a `pv-how`, para registrar la entrada externamente (p. ej. un issue en el tracker, una publicación en un canal, una fila de índice). En modo todo se ejecuta después de eliminar la idea de origen.
  - **`pv-fix` incorpora un punto de hook para la vía rápida (cambio trivial)** — justo después de documentar la entrada, antes de tocar cualquier código; es el único punto de personalización disponible antes de que un cambio por vía rápida se aplique, ya que esta vía se salta por completo `plan.md`/`pv-how`. La vía rápida ahora también ejecuta los dos hooks de `pv-do` descritos más abajo, puesto que edita código de la misma forma que `pv-do`.
  - **`pv-version` incorpora un quinto punto de hook, el más temprano** — antes incluso de comprobar que `implemented/` está vacío, para comprobaciones de aborto baratas (árbol git limpio, rama correcta, CI en verde, etiqueta de versión aún no usada). Sus tres antiguas secciones de "pipeline personalizado" pasan a ser tres ficheros de hook independientes en lugar de secciones de un único fichero compartido (ver Cambios, más abajo).
  - **`pv-do` incorpora dos puntos de hook** — antes de editar cualquier código, y después de terminar el código y la documentación pero antes de mover la carpeta a `implemented/`. Ambos se ejecutan también desde la vía rápida de `pv-fix`.

## ✏️Cambios

- 📂**Sistema de hooks de proyecto**:
  - **El antiguo pipeline personalizado de `pv-version`, de fichero único y tres secciones, se sustituye por los nuevos ficheros de hook por punto** — las antiguas secciones fijas ("Antes de empezar" / "En medio" / "Al final") pasan a ser tres ficheros independientes, más el nuevo hook de comprobación inicial. **Requiere acción:** `pv-update` detecta el fichero heredado — si es una semilla vacía sin modificar, se elimina y se vuelve a sembrar automáticamente; si contiene pasos creados por el proyecto, **no** se migra automáticamente, y se informa del mapeo de sección a fichero para que el usuario pueda mover los pasos a mano.
  - **El fichero de procedimiento de compilación de `pv-version` se renombra de `how-to-compile-version.md` a `how-to-compile.md`** — mismo rol y formato, solo cambia el nombre. **Requiere acción:** `pv-update` renombra el fichero automáticamente cuando solo se encuentra el nombre antiguo; si existen ambos nombres, no se toca ninguno y se pide al usuario que los concilie manualmente.
  - **El alcance de auditoría/reparación de `pv-update` se amplía al nuevo sistema de hooks** — comprueba la presencia de cada fichero de hook, renombra cualquier fichero que use un nombre antiguo o no canónico conservando su contenido, y, dado que los ficheros de hook son en inglés técnico fijo sin opción de idioma, traduce automáticamente in situ cualquier contenido de pasos creado por el proyecto que se encuentre en otro idioma, sin tocar comandos ni rutas de fichero.
  - **`pv-do`, `pv-how`, `pv-new`, `pv-fix` y `pv-version` ahora se documentan explícitamente como framework instalado no editable** — una petición de cambiar el comportamiento de uno de estos flujos se responde ahora señalando el fichero de hook correspondiente en lugar de editar la skill a mano, ya que una skill editada a mano queda desincronizada del control de versiones de `pv-update`. Cada una de estas skills también incorpora un fichero de diagrama de flujo explícito (`workflow.do.md`, junto a los ya existentes para las demás) que documenta la secuencia completa del flujo, incluidos los puntos de ramificación de los hooks.
- **El scaffolding de `pv-init` ahora siembra la carpeta de hooks** — el scaffolding de proyecto siembra ahora `stuff/hooks/` y sus subcarpetas/ficheros semilla por skill, en lugar de la antigua semilla única de pipeline personalizado, como parte de la inicialización de un proyecto nuevo.

## ❌Eliminado

- **Se elimina el antiguo pipeline personalizado de fichero único de `pv-version`** — desaparece el fichero semilla de tres secciones sin pasos, sustituido por los ficheros de plantilla de hook independientes por punto descritos arriba.
