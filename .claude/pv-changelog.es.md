# Changelog de Previo v0.9.6b14 (desde v0.9.6b13)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subviñetas debajo (sin encabezado ni enlace). En el Índice, ese mismo tema se colapsa en una única línea simple `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas sin agrupar aparecen como viñetas de primer nivel normales en ambos sitios (solo el título en el Índice, viñeta completa con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - 📂Pasos personalizados por proyecto en el flujo de versión (4 cambios)
- ✏️[Cambios](#cambios)
  - Los cambios se eligen por id al activar un flag

## ⭐Novedades

- 📂**Pasos personalizados por proyecto en el flujo de versión**:
  - **El flujo de versión ejecuta los pasos propios del proyecto en tres puntos fijos** — `pv-version` ahora busca `{workFolder}/stuff/custom-version-pipeline.md` y, si existe, ejecuta los pasos que define en tres momentos de la versión: antes de empezar, a mitad (una vez que los artefactos del entregable están en su sitio) y al final (después de redactar el changelog, antes del resumen final). Cada paso es texto más un comando que se ejecuta desde la raíz del repositorio, con `{workFolder}`, `{XXXX}` y las rutas `versions/{XXXX}/` sustituidos donde correspondan. Una sección sin pasos se omite en silencio, y un proyecto que nunca creó el fichero se comporta exactamente igual que antes. Si un paso personalizado falla, la versión se detiene y se explica el problema en lugar de buscar un rodeo. Esta es la forma prevista de extender el flujo (por ejemplo, publicar una release o ejecutar una comprobación previa) — los ficheros de la skill no están pensados para editarse a mano. El resumen final ahora también indica qué secciones personalizadas se ejecutaron y qué produjeron.
  - **Los proyectos nuevos se generan con el fichero de pipeline personalizado** — `pv-init` ahora crea `{workFolder}/stuff/custom-version-pipeline.md` desde el principio, con solo sus tres encabezados de sección fijos y ningún paso, para que el mecanismo de personalización sea descubrible. Nunca se sobrescribe, así que un proyecto que ya ha añadido pasos los conserva.
  - **`pv-update` comprueba que el fichero de pipeline personalizado está presente** — en proyectos generados antes de que este fichero existiera, `pv-update` ahora detecta que `{workFolder}/stuff/` no tiene `custom-version-pipeline.md` y recrea la semilla vacía (tres secciones, cero pasos). Solo se comprueba la presencia del fichero, nunca su contenido, y un fichero existente se deja intacto. Ejecuta `/pv-update` una vez para incorporarlo en un proyecto existente.
  - **La guía documenta el nuevo punto de personalización** — `pv-guide` ahora tiene una sección "Pasos personalizados en el pipeline de versión" dentro de "Más formas de personalizar Previo", que describe los dos ficheros de personalización en `{workFolder}/stuff/`, los tres puntos de enganche y qué variables puede usar cada uno.

## ✏️Cambios

- **Los cambios se eligen por id al activar un flag** — en el flujo "Activar un flag en un cambio" (la consola de proyecto de `pv-init`), la lista de cambios ya no muestra un número de fila paralelo junto a cada entrada. Los cambios se siguen agrupando por estado, pero ahora escribes el id (código) propio del cambio para elegirlo, en vez de cotejar una numeración aparte. Escribir un id que no está en la lista deja el selector abierto con un aviso breve en lugar de fallar.
