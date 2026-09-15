# 014 — Interacciones programadas de un componente

**Area**: Mesa de juego

Algunos tipos de componente tienen programada una interacción propia que se dispara con un click sobre ellos en Modo Juego: "Dado" ("Lanzar dado", una tirada aleatoria), "Carta/Ficha" ("Voltear carta", entre cara frontal y trasera) y "Mazo" ("Sacar carta de arriba"). "Cuadro de texto", "Tablero simple" y "Visor de documentos" no tienen ninguna interacción de este tipo.

La modal de configuración de un componente tiene una pestaña propia "Interacciones" (ver [Alta/edición/borrado de componentes con modal de tabs](002-alta-edicion-borrado-de-componentes-con-modal-de-tabs.md)), situada entre "Específicas" y "Copias", cuyo contenido es la sección "Interacciones programadas". Esa sección se muestra siempre (antes de existir el ajuste de click derecho descrito más abajo, solo aparecía si el tipo tenía alguna interacción de click izquierdo programada). Muestra un desplegable por cada interacción de click izquierdo que tenga el tipo, con las opciones "Ninguna" y el nombre de la interacción (esta última seleccionada por defecto). Un componente nuevo nace con todas sus interacciones activas.

Eligiendo "Ninguna" en el desplegable de una interacción, el click sobre ese componente deja de disparar esa acción concreta en Modo Juego (el dado no se lanza, la carta no voltea, el mazo no saca carta), sin afectar a nada más: el arrastre (según "Bloqueado"), el menú contextual de Modo Juego (Bloquear/Desbloquear y las acciones específicas del tipo, como "Barajar"/"Ver contenido..." en un mazo o "Meter en mazo..." en una carta) y, en el caso del dado, el doble-click que abre la modal de resultado a tamaño grande, siguen funcionando exactamente igual. En Modo Edición este ajuste no tiene ningún efecto, ya que estas interacciones nunca han estado disponibles ahí. La sección informativa "Interacciones" del propio menú contextual de Modo Juego (ver [Menú contextual de componente en modo juego](026-menu-contextual-de-componente-en-modo-juego.md)) refleja este ajuste: su fila "Clic izquierdo" pasa a mostrar "Ninguno" cuando está desactivado (fix 00116).

**Click derecho** (cambio 00142): la misma sección incluye, para los 6 tipos de componente por igual, una fila fija "Click derecho" con las opciones "Ninguno" (valor por defecto de un componente nuevo) y "Abrir menú contextual". Con "Ninguno" seleccionado, el botón derecho sobre ese componente en Modo Juego no hace nada — ni lo selecciona ni abre el menú contextual (ver [Menú contextual de componente en modo juego](026-menu-contextual-de-componente-en-modo-juego.md)); el resto de interacciones (arrastre, click izquierdo, doble click) no se ven afectadas, y el componente se sigue pudiendo bloquear/desbloquear desde Modo Edición. Un componente nuevo nace en "Ninguno".

Para un componente tipo "Copia" (ver [Elementos tipo Copia, vinculados y sincronizados con un original](005-elementos-tipo-copia-vinculados-y-sincronizados-con-un-original.md)), tanto las interacciones de click izquierdo como el ajuste de click derecho se sincronizan automáticamente con su original, igual que el resto de propiedades de configuración/diseño.

- **Available in**: modo edición (sección editable en la modal de configuración, pestaña "Interacciones"); modo juego (efecto de desactivar una interacción de click izquierdo o el click derecho, incluida la sección informativa del menú contextual).
- **Code**: 00115, 00116, 00142, 00251, 00250.
- **Since**: 2026-08-03
- **Last modified**: 2026-09-09
