# Changelog de Previo v0.9.8b5 (desde v0.9.7)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como sub-viñetas debajo (sin encabezado, sin enlace). En el índice, ese mismo tema se colapsa en una sola línea `📂{Tema} (N cambios)`, sin listar sus entradas. Las entradas sin agrupar aparecen como viñetas normales de primer nivel en ambos sitios (título simple en el índice, viñeta completa con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - Nueva skill para reorganizar la documentación técnica: `/pv-review-doc-tech`
- ✏️[Cambios](#cambios)
  - Las llaves de los marcadores de plantilla ya no se filtran a los ficheros generados

## ⭐Novedades

- **Nueva skill para reorganizar la documentación técnica: `/pv-review-doc-tech`** — una nueva skill de mantenimiento periódico que relee por completo cada carpeta configurada en `docs.tech` (arquitectura y guía de estilo) y la reorganiza —moviendo, agrupando o consolidando contenido mal ubicado o duplicado— sin borrar ningún dato, reescribir ninguna frase ni añadir contenido nuevo. Regenera automáticamente el `INDEX.md` de cada carpeta y señala cualquier duda (como un posible cambio de espacio de nombres) para que el usuario decida, en vez de asumirlo por su cuenta.

## ✏️Cambios

- **Las llaves de los marcadores de plantilla ya no se filtran a los ficheros generados** — al rellenar una plantilla, el framework ahora elimina correctamente el envoltorio `[[[...]]]` que rodea las etiquetas fijas en inglés (p. ej. `**[[[Name]]]**:` pasa a ser `**Name**:`), en vez de limitarse a no traducirlas, lo que antes podía dejar las llaves sin quitar en un `description.md`/`plan.md` generado. `pv-update` ahora también detecta y repara cualquier fichero en el que esto haya ocurrido (`marker-literal:*`).
