# Changelog de Previo v0.9.6b12 (desde v0.9.6b11)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como subviñetas debajo (sin encabezado ni enlace). En el Índice, ese mismo tema se colapsa en una única línea simple `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas sin agrupar aparecen como viñetas de primer nivel normales en ambos sitios (solo el título en el Índice, viñeta completa con título en negrita y resumen en el detalle).

## Índice

- ✏️[Cambios](#cambios)
  - 📂Los mockups siguen el estilo documentado del proyecto (2 cambios)

## ✏️Cambios

- 📂**Los mockups siguen el estilo documentado del proyecto**:
  - **Los mockups ASCII reutilizan la disposición y los textos documentados** — antes de inventar estructura o texto de ejemplo, `pv-internal-mockups-ascii` ahora lee la guía de estilo del proyecto (solo lectura) y reutiliza sus convenciones reales de disposición, estados de los elementos y microcopy (etiquetas de botón, textos de estado, nomenclatura de flags). Cuando no hay guía de estilo configurada, remite al usuario a `/pv-init` o `/pv-update` y no genera nada; cuando la guía de estilo existe pero no cubre un elemento concreto, usa una disposición neutra de marcador de posición y señala esa carencia en el fichero.
  - **Los mockups HTML replican la identidad visual documentada** — antes de inventar cualquier estilo, `pv-internal-mockups-html` ahora lee la guía de estilo del proyecto (solo lectura) y reutiliza sus valores concretos (colores, tipografía, espaciado, nombres de tokens, componentes reutilizables, iconografía, microcopy) en vez de aproximarlos. Cuando no hay guía de estilo configurada, remite al usuario a `/pv-init` o `/pv-update` y no genera nada; cuando la guía de estilo existe pero no cubre lo que el mockup necesita, recurre a un estilo neutro y sobrio y anota esa carencia al principio del fichero. Los mockups siguen siendo autónomos: la apariencia documentada se copia en línea, nunca se enlaza desde la hoja de estilos real ni desde un CDN.
