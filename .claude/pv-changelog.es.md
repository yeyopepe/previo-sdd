# Changelog de Previo v0.9.7b4 (desde v0.9.6)

## Índice

- ⭐[Novedades](#novedades)
  - Hooks específicos de proyecto en puntos fijos de cada flujo
- ✏️[Cambios](#cambios)
  - El pipeline personalizado de `pv-version` se sustituye por el nuevo esquema de hooks
  - `how-to-compile-version.md` pasa a llamarse `how-to-compile.md`
  - `pv-init`/`pv-update` ahora crean y auditan el esquema de hooks

## ⭐Novedades

- **Hooks específicos de proyecto en puntos fijos de cada flujo** — `pv-new`, `pv-how`, `pv-fix`, `pv-do` y `pv-version` exponen ahora uno o varios puntos de inserción donde un proyecto puede definir sus propios pasos (comandos a ejecutar), guardados en un fichero por punto bajo `{workFolder}/stuff/hooks/<flujo>/`. Entre los usos posibles están registrar un cambio nuevo en un tracker externo, cargar contexto antes de analizar, ejecutar tests o un linter tras implementar, o comprobar precondiciones antes de que empiece una entrega. Un hook sin pasos definidos se salta en silencio, así que los proyectos existentes siguen funcionando exactamente igual que antes hasta que decidan añadir algo; si un paso definido falla, el flujo se detiene y explica el motivo en vez de continuar.

## ✏️Cambios

- **El pipeline personalizado de `pv-version` se sustituye por el nuevo esquema de hooks** — el antiguo fichero único con tres secciones fijas (`custom-version-pipeline.md`) se sustituye por cuatro ficheros de hook independientes (`stuff/hooks/version/`), lo que añade al flujo de entrega dos puntos de inserción nuevos: uno que se ejecuta antes que nada (útil para abortar pronto, por ejemplo si el árbol de git está sucio o la rama no es la correcta) y otro justo después de resolver el código de versión, además de los puntos ya existentes tras el build y tras el changelog.
- **`how-to-compile-version.md` pasa a llamarse `how-to-compile.md`** — mismo propósito (documentar el procedimiento del proyecto para compilar/generar el entregable), solo cambia el nombre del fichero; el contenido existente se conserva y solo hace falta renombrarlo.
- **`pv-init`/`pv-update` ahora crean y auditan el esquema de hooks** — un proyecto nuevo recibe automáticamente el conjunto completo de ficheros semilla de hooks, y `pv-update` en un proyecto ya existente detecta ahora un fichero de pipeline heredado que haya quedado suelto (lo borra automáticamente si es una semilla sin tocar, o lo reporta para migración manual si ya contiene pasos escritos por el proyecto) y cualquier fichero de hook con un nombre no canónico (lo renombra automáticamente, conservando su contenido).
