# 039 — Barra de controles superior: modos, importar y exportar

**Area**: Mesa de juego

En la cabecera de la aplicación, a la derecha del título, hay una fila de controles siempre visible:

- **En modo juego**: «Importar», «Exportar», un separador vertical, «Modo Edición», «Ajustar zoom» y «Configuración».
- **En modo edición**: «Modo Juego», «Ajustar zoom» y «Configuración» en la cabecera; y una segunda franja, justo debajo, con «Importar» y «Exportar».

El botón de cambio de modo se llama **«Modo Edición»** cuando se está en modo juego (lleva al modo edición) y **«Modo Juego»** cuando se está en modo edición (vuelve al modo juego). Está siempre en el mismo sitio, en la fila de la cabecera, se esté en el modo que se esté. Junto a él, «Ajustar zoom» encuadra la vista para que todos los elementos de la mesa quepan en pantalla, y «Configuración» abre el panel de ajustes (ver [Aplicación multi-idioma y panel de configuración](038-aplicacion-multi-idioma-y-panel-de-configuracion.md)).

«Importar» y «Exportar» tienen el **mismo aspecto en los dos modos** (blanco sobre el fondo oscuro de la cabecera) y abren, respectivamente, el flujo de importación y el menú de exportación (ver [Exportar/importar componentes en JSON, con selección](032-exportar-importar-componentes-en-json-con-seleccion.md)). El botón de configuración se distingue visualmente de «Modo Edición»/«Modo Juego» y «Ajustar zoom»: estos últimos son botones de acción destacada (azul), mientras que el de configuración va en blanco sobre fondo oscuro. Un separador vertical divide, en la fila de la cabecera, el bloque de importar/exportar del bloque de acciones.

«Exportar» es un **desplegable**: al abrirse ofrece «Exportar juego (.json)» (única opción activa, que lanza el flujo de exportación descrito en [Exportar/importar componentes en JSON, con selección](032-exportar-importar-componentes-en-json-con-seleccion.md)) y, tras un separador, dos opciones futuras ya visibles pero desactivadas y marcadas con la etiqueta «Próximamente»: «Exportar recursos (.zip)» y «Exportar hoja de producción (.csv)». El desplegable se cierra al elegir «Exportar juego (.json)», al hacer click fuera de él o al pulsar la tecla ESC.

- **Available in**: Modo juego y modo edición, fila de controles de la cabecera
- **Code**: 00244, 00171
- **Since**: 2026-09-03
- **Last modified**: 2026-09-06
