# 024 — Migración de fichas antiguas a Carta/Ficha

**Area**: Mesa de juego

El tipo de componente independiente "Ficha" (piezas/tokens simples, cuadrados o circulares, con borde y fondo configurables) se ha retirado: su caso de uso queda cubierto por "Carta/Ficha" con proporción "Cuadrada" o "Circular" (ver más arriba). Ya no se puede dar de alta ningún componente "Ficha" nuevo, pero cualquier ficha guardada de una partida anterior sigue estando disponible: se convierte automáticamente a "Carta/Ficha" (forma cuadrada → proporción "Cuadrada", forma circular → proporción "Circular"; borde, imagen de fondo con su ajuste, o texto centrado — como un único cuadro de texto que ocupa toda la carta — se trasladan tal cual; un color de fondo sólido sin imagen ni texto no tiene equivalente y se pierde, quedando la carta en blanco con el borde migrado, igual que cualquier otra carta sin diseño) mostrando de entrada la cara frontal (con el diseño migrado, en vez de la trasera en blanco de una carta nueva) y sin etiqueta asignada.

Esta conversión ocurre de forma automática y sin ningún aviso al abrir la app, tanto si el guardado viene del propio navegador como de un fichero HTML exportado con estado embebido — mismo criterio ya seguido con otras migraciones silenciosas de datos de versiones anteriores.

Al **importar** un fichero JSON de componentes sobre una partida ya abierta (ver [Exportar/importar componentes en JSON, con selección](032-exportar-importar-componentes-en-json-con-seleccion.md)), si alguna de las fichas incluidas no se puede convertir por tener datos corruptos o inesperados (por ejemplo, una forma no reconocida, o le falta información imprescindible de su diseño), la importación no se completa en silencio: antes de aplicar ningún cambio a la partida actual se muestra un aviso con el listado de las fichas afectadas y el motivo de cada error, con dos opciones:

- **Available in**: arranque de la app (migración silenciosa) e importación explícita de componentes (con aviso de errores).
- **Code**: 00087.
- **Since**: 2026-07-25
- **Last modified**: 2026-07-25
