# Changelog de Previo v0.9.8b6 (desde v0.9.7)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten un mismo asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como sub-viñetas debajo (sin encabezado, sin enlace). En el índice, ese mismo tema se reduce a una única línea plana `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas sin agrupar se listan como viñetas normales de primer nivel en ambos sitios (título simple en el índice, viñeta completa con título en negrita y resumen en el detalle).

## Índice

- ⭐[Novedades](#novedades)
  - 📂Skills de mantenimiento (2 cambios)
- ✏️[Cambios](#cambios)
  - 📂Ficheros de mockups y diseño reorganizados (4 cambios)
  - 📂Sintaxis de corchetes de plantilla corregida en todos los puntos donde podía filtrarse (2 cambios)
  - Los mockups ahora recurren al código real cuando falta contenido en la guía de estilo
  - `pv-status` informa por separado del número de ficheros de mockups
  - `pv-update` migra automáticamente las entradas a la nueva organización de mockups/ficheros

## ⭐Novedades

- 📂**Skills de mantenimiento**:
  - **`/pv-review-doc-tech` reorganiza la documentación técnica** — relee periódicamente cada carpeta de `docs.tech` entera y reorganiza su contenido (moviendo, agrupando, consolidando duplicados, corrigiendo etiquetas `**Area**` mal asignadas) sin borrar nunca un hecho, reescribir una frase o añadir contenido nuevo; regenera `INDEX.md` automáticamente y señala al usuario cualquier cosa que no sea seguro decidir por su cuenta (por ejemplo, un conflicto de namespace).
  - **`/pv-review-architecture` propone reorganizaciones de código** — revisa el código fuente real contra una checklist fija e independiente del lenguaje (separación de responsabilidades, tamaño de ficheros/clases, SOLID, DRY, KISS, acoplamiento/capas, naming, estructura de carpetas) y produce una lista numerada de propuestas de reorganización pura (mover/dividir/fusionar/renombrar), sin añadir ni cambiar nunca código funcional. Para cada propuesta que el usuario acepta, pregunta individualmente si debe registrarse como idea anotada (`pv-todo`) o como cambio documentado (`pv-new`) y la crea en consecuencia.

## ✏️Cambios

- 📂**Ficheros de mockups y diseño reorganizados**:
  - **Los mockups ahora viven en su propia subcarpeta `mockups/`** — los ficheros `design_*.html`/`design_*.txt` generados por `pv-new`/`pv-fix` se escriben en `{changesDir}/inProgress/{xxxx}/mockups/` en lugar de sueltos en la raíz de la entrada, manteniendo los ficheros de mockup separados del resto de documentos de la entrada.
  - **Los ficheros de navegación y datos se renombraron, eliminando el prefijo `design_`** — `design_navigation_*.md` y `design_data_*.md` ahora son `navigation_*.md` y `data_*.md`, y siguen sueltos en la raíz de la entrada (no son mockups) para distinguirlos con claridad del contenido de la subcarpeta `mockups/`.
  - **El flujo de degradación de `pv-todo` traslada la nueva organización** — al degradar un cambio (`/pv-todo change <xxxx>`) ahora se copia el subárbol completo de `mockups/` tal cual (marcado con una nota indicando que es material de referencia congelado, no un diseño vivo) y se preservan los ficheros `navigation_*.md`/`data_*.md` con sus nuevos nombres.
  - **La validación de consistencia de `pv-how` lee ambas ubicaciones nuevas** — validar los documentos de un cambio/fix antes del análisis ahora lee la subcarpeta `mockups/` y cualquier fichero `navigation_*.md`/`data_*.md` suelto como dos fuentes distintas, sin recurrir a la antigua organización suelta en la raíz ni al prefijo `design_` retirado.
- 📂**Sintaxis de corchetes de plantilla corregida en todos los puntos donde podía filtrarse**:
  - **Las plantillas del framework ahora explican cómo eliminar los marcadores `[[[...]]]`** — todas las skills que rellenan una plantilla (`pv-do`, `pv-new`, `pv-fix`, `pv-todo`, `pv-internal-workflow`, `pv-internal-doc-features`) indican ahora explícitamente que `[[[...]]]` es sintaxis exclusiva de plantilla que nunca debe llegar a un fichero generado, con un ejemplo resuelto de cómo eliminar los corchetes de la etiqueta.
  - **`pv-update` detecta y corrige sintaxis de corchetes que se haya colado** — una nueva comprobación, `marker-literal:*`, detecta un `description.md`/`plan.md` que todavía conserve la sintaxis literal `**[[[Name]]]**`/`## [[[Full description]]]` en lugar de la etiqueta ya desenvuelta, y la repara automáticamente eliminando solo los corchetes.
- **Los mockups ahora recurren al código real cuando falta contenido en la guía de estilo** — al generar un mockup en HTML o ASCII, si `docs.tech.styleBibleDocDir` no cubre un elemento necesario, las skills de mockups ahora buscan el estilo/convenciones reales ya presentes en el código fuente de la app en lugar de recurrir directamente a un placeholder neutro; todo lo reutilizado de esta forma se informa de vuelta como un "hueco de estilo encontrado" para que quien la invoque pueda marcarlo como tarea de documentación en lugar de absorberlo en silencio.
- **`pv-status` informa por separado del número de ficheros de mockups** — la ficha de detalle en modo terminal ahora muestra una línea dedicada `mockups: N` (recuento de ficheros dentro de la subcarpeta `mockups/` de la entrada) junto al recuento de "extra files" ya existente, que ya no incluye los ficheros de mockup.
- **`pv-update` migra automáticamente las entradas a la nueva organización de mockups/ficheros** — dos comprobaciones nuevas, `legacy-loose-mockups:*` y `legacy-design-prefix:*`, detectan entradas de `inProgress`/`implemented` que todavía siguen la organización antigua (mockups sueltos en la raíz de la entrada, o ficheros de navegación/datos que todavía conservan el prefijo `design_`) y las corrigen: creando `mockups/` y moviendo los ficheros dentro, o renombrando los ficheros para eliminar el prefijo retirado.
