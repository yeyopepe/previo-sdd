# Changelog de Previo v0.9.8b8 (desde v0.9.7)

Nota: dentro de una sección, las entradas pueden agruparse bajo un tema cuando al menos dos entradas comparten asunto. En la sección de detalle, un tema es `- 📂**{Tema}**:` con sus entradas anidadas como sub-elementos indentados debajo (sin encabezado, sin enlace). En el índice, ese mismo tema se reduce a una única línea plana `📂{Tema} (N cambios)` sin listar sus entradas. Las entradas sueltas se listan como elementos normales en ambos sitios (título simple en el índice, elemento completo con título en negrita y resumen en el detalle).

## Índice

- ⭐[Nuevo](#nuevo)
  - 📂Skills de mantenimiento (2 cambios)
- ✏️[Cambios](#cambios)
  - La comprobación de instalación del framework se sustituye por un único script de estado
  - `pv-update` ahora puede instalar o actualizar el propio framework
  - Los mockups y los ficheros de flujo/datos se reorganizan en una subcarpeta `mockups/` dedicada
  - La generación de mockups ahora recurre a las convenciones reales del código cuando faltan en la guía de estilo
  - `pv-status` ahora muestra el número de mockups en la ficha de detalle de la entrada
- 🛠️[Arreglos](#arreglos)
  - Los marcadores de corchetes de las plantillas ya no corren riesgo de filtrarse a los documentos generados

## ⭐Nuevo

- 📂**Skills de mantenimiento**:
  - **`/pv-review-doc-tech` reorganiza la documentación técnica** — una nueva skill opcional que relee por completo cada carpeta bajo `docs.tech` y la reorganiza (moviendo, agrupando y consolidando contenido duplicado o mal ubicado) sin borrar nunca un hecho, reescribir una frase ni añadir contenido nuevo.
  - **`/pv-review-architecture` propone reorganizaciones de código** — una nueva skill opcional que revisa el código fuente real contra una checklist fija e independiente del lenguaje (separación de responsabilidades, SOLID, DRY, KISS, acoplamiento, naming) y genera una lista numerada de propuestas de reorganización estructural, que el usuario puede convertir en una idea anotada (`pv-todo`) o en un cambio documentado (`pv-new`).

## ✏️Cambios

- **La comprobación de instalación del framework se sustituye por un único script de estado** — la comprobación inicial de cada skill `pv-*` ahora ejecuta un único script compartido (`check-framework-status.py`) en vez de comparar los campos de versión por su cuenta. **Acción necesaria al actualizar:** si ese script no existe tras actualizar, hay que reinstalar el framework con `/pv-update install` antes de que ninguna skill pueda ejecutarse.
- **`pv-update` ahora puede instalar o actualizar el propio framework** — un nuevo modo explícito `/pv-update install` resuelve e instala una versión objetivo (la última por defecto), independiente de su modo de auditoría existente, que sigue sin tocar la red en ningún momento.
- **Los mockups y los ficheros de flujo/datos se reorganizan en una subcarpeta `mockups/` dedicada** — los mockups `design_*.html`/`design_*.txt` ahora viven en la subcarpeta `mockups/` de cada entrada en vez de sueltos en su raíz, y `design_navigation_*.md`/`design_data_*.md` pasan a llamarse `navigation_*.md`/`data_*.md`. **Acción necesaria al actualizar:** ejecutar `/pv-update`, que detecta y migra cualquier entrada que siga usando la organización antigua.
- **La generación de mockups ahora recurre a las convenciones reales del código cuando faltan en la guía de estilo** — cuando `docs.tech.styleBibleDocDir` no cubre un elemento que se está maquetando, las skills de mockups ahora buscan la convención real en el código fuente en vez de recurrir directamente a un placeholder neutro, y reportan ese hueco al llamador como deuda de documentación pendiente de registrar.
- **`pv-status` ahora muestra el número de mockups en la ficha de detalle de la entrada** — la vista de detalle en terminal indica cuántos ficheros contiene la subcarpeta `mockups/` de una entrada, junto a su recuento existente de ficheros adicionales.

## 🛠️Arreglos

- **Los marcadores de corchetes de las plantillas ya no corren riesgo de filtrarse a los documentos generados** — toda skill que rellena un campo de plantilla marcado con `[[[...]]]` ahora elimina explícitamente los triples corchetes al escribir el fichero real, y la auditoría de `pv-update` incorpora una comprobación dedicada (`marker-literal:*`) para detectar y reparar cualquier documento donde los corchetes hayan sobrevivido tal cual.
