# 021 — Componente "Visor de documentos"

**Area**: Mesa de juego

Cuarto tipo de componente: una hoja con fondo blanco, borde fino y una sombra de contacto suave que la asienta sobre la mesa (como un papel apoyado encima), que muestra contenido renderizado, pensada para notas, reglas o material de referencia de la partida. El contenido siempre se ajusta al ancho del componente (nunca aparece scroll horizontal); si es más alto que el tamaño fijado, aparece scroll vertical dentro de ese tamaño.

El tipo de contenido se elige entre dos opciones, configurables sin perder la configuración de la que no está activa:

- **Texto**: un cuadro de texto multilínea donde pegar el contenido, junto con un selector de formato (Markdown, por defecto, o HTML) que indica cómo interpretarlo antes de mostrarlo. En formato Markdown se admite CommonMark + GitHub Flavored Markdown completo (encabezados, negrita/cursiva, citas anidadas, listas ordenadas/sin ordenar anidadas y con contenido enriquecido dentro de un elemento, tablas, texto tachado, listas de tareas `- [ ]`/`- [x]` mostradas como casilla deshabilitada de solo lectura, bloques de código, reglas horizontales, enlaces/auto-enlaces/referencias, imágenes, y HTML embebido dentro del propio texto). El HTML resultante (el pegado directamente, el generado a partir del Markdown, o el HTML embebido dentro de él) se sanitiza siempre antes de mostrarse (se elimina cualquier `<script>`, manejador de evento inline y enlace `javascript:`), ya que el estado de la partida se guarda y puede exportarse como un único fichero HTML autocontenido. Si el contenido pegado está mal formado, se muestra tal cual lo interprete el navegador o el conversor, sin validación ni aviso.
- **URL**: un campo de texto con la dirección de una página HTML externa, que se muestra embebida. Si el sitio de destino bloquea ser embebido, se muestra superpuesto el aviso "No se pudo cargar el contenido" (detección best-effort, no garantizada al 100% en todos los sitios/navegadores).

Un componente sin contenido (texto vacío, o antes de configurar nada) muestra simplemente la hoja en blanco, sin ningún aviso.

- **Available in**: renderizado sobre la mesa en modo juego y modo edición; alta eligiendo "Visor de documentos" en la modal previa de tipo al pulsar "+ Añadir componente" (ver [Alta/edición/borrado de componentes con modal de tabs](002-alta-edicion-borrado-de-componentes-con-modal-de-tabs.md)).
- **Code**: 00036, 00037, 00038, 00039, 00040, 00063.
- **Since**: 2026-07-19
- **Last modified**: 2026-07-23
