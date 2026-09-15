# 041 — Pantalla de bienvenida al arrancar la aplicación

**Area**: Mesa de juego

Al abrir la aplicación, y cada vez que se recarga, aparece durante unos segundos una pantalla de bienvenida centrada antes de mostrarse la mesa de juego.

Alrededor de la ventana de la pantalla de bienvenida se ve el fondo de la mesa de juego —el mismo tapete gris con patrón de puntos que se ve en la mesa— sin componentes ni interfaz y sin ninguna capa que lo oscurezca o difumine. La ventana de la pantalla de bienvenida se recorta sobre ese fondo por su sombra y su degradado propio.

La pantalla muestra uno de cuatro logotipos de la aplicación, elegido al azar en cada arranque (todos con la misma probabilidad, sin tener en cuenta cuál se mostró la vez anterior). El logotipo se ve completo, sin recortes ni deformación, y sus bordes se funden de forma suave con el fondo de la ventana, que es un degradado en tonos claros. Debajo del logotipo se lee el nombre de la aplicación, "Board Game Factory", con "(2026)" en superíndice.

Justo debajo del nombre hay un enlace con el texto "View on Github". Al pulsarlo se abre, en una pestaña nueva del navegador, el repositorio del proyecto en GitHub (el mismo destino que se enlaza desde el indicador de versión y desde el panel de configuración). El texto del enlace es fijo, igual en cualquier idioma de la aplicación. Se presenta como el resto de enlaces de texto de la aplicación: en el color del texto que lo rodea y subrayado, sin resaltarse en otro color. Pulsar el enlace **no cierra** la pantalla de bienvenida: se abre GitHub en otra pestaña y la pantalla sigue su curso y desaparece cuando se cumple su tiempo.

En el borde inferior de la ventana hay una fina barra azul que se llena de izquierda a derecha, a ritmo constante, a lo largo de los tres segundos que dura la pantalla. Cuando la barra se completa, la pantalla desaparece sola y queda visible la aplicación.

Aparte del enlace a GitHub, la pantalla de bienvenida no tiene ningún control: no se puede cerrar antes de tiempo, no reacciona a los clics sobre el resto de la ventana ni a las teclas. Siempre dura sus tres segundos. Aparece igual tanto si la aplicación estaba en modo juego como en modo edición, y no afecta al título de la partida ni al indicador de versión, que siguen mostrándose con normalidad una vez cerrada.

La barra azul se anima siempre, con independencia de que en el sistema operativo se haya activado la opción de reducir el movimiento o las animaciones.

- **Available in**: Al cargar o recargar la aplicación, en cualquier modo (juego o edición). Tanto en la versión de desarrollo como en el fichero HTML entregable.
- **Code**: 00245, 00246, 00247, 00248
- **Since**: 2026-09-06
- **Last modified**: 2026-09-06
