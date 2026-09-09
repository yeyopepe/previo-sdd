# 037 — Indicador de versión y enlace al repositorio

**Area**: Mesa de juego

En la esquina inferior derecha de la pantalla aparece un pequeño texto gris, alineado a la derecha y anclado a esa esquina, con la información de la aplicación. De abajo a arriba lo componen:

- El nombre de la aplicación seguido de la versión actual del prototipo (por ejemplo, `BG Factory v00252`).
- Un enlace al repositorio del proyecto en GitHub. Al pulsarlo, abre el repositorio (`https://github.com/yeyopepe/bgfactory`) en una pestaña nueva del navegador, sin sacar al usuario de la aplicación. El texto del enlace se muestra en el idioma activo de la aplicación (`Ver en Github` en español, `View on GitHub` en inglés); ver [Aplicación multi-idioma y panel de configuración](038-aplicacion-multi-idioma-y-panel-de-configuracion.md).

Esas dos líneas son contenido fijo del proyecto: el usuario no puede editarlas, y se muestran igual en modo juego y en modo edición.

Por encima de ellas puede aparecer, además, un **texto libre que escribe el propio usuario** desde el panel de Configuración (ver [Aplicación multi-idioma y panel de configuración](038-aplicacion-multi-idioma-y-panel-de-configuracion.md)). Ese texto:

- Solo aparece cuando el usuario ha escrito algo. Mientras el campo de Configuración está vacío, la esquina muestra únicamente las dos líneas fijas, exactamente igual que antes, sin ningún hueco ni línea de más.
- Se muestra tal cual, como texto plano, respetando los saltos de línea que haya introducido el usuario. No se interpreta como HTML ni como ningún otro tipo de código o formato: si el usuario escribe algo con apariencia de etiqueta, se ve ese texto literal.
- Va en el mismo gris tenue y tamaño pequeño que el resto de la esquina, y queda separado de las dos líneas fijas por una fina línea horizontal.
- Se actualiza en el momento: al escribir o borrar en el campo de Configuración, la esquina de la mesa refleja el cambio al instante, sin cerrar la ventana ni recargar.
- Es una preferencia local de ese navegador: se conserva al recargar la página, pero no viaja con la partida (no se incluye al exportar una partida ni cambia al importar una) y no aparece al abrir la aplicación en otro navegador o perfil.

Todo el bloque (texto libre, si lo hay; nombre y versión; enlace) va en gris tenue, a tamaño pequeño y alineado a la derecha. El enlace se distingue del resto por ir subrayado, con el mismo color gris.

- **Available in**: Modo juego y modo edición, esquina inferior derecha de la pantalla
- **Code**: 00243, 00244, 00250
- **Since**: 2026-09-03
- **Last modified**: 2026-09-03
