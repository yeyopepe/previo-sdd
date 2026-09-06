# 022 — Mazo
**Area**: Tipos de componente

El mazo es una pila ordenada y barajable de cartas. Se configuran su orientación y forma, una imagen propia para el dorso, y la zona de revelado: el lado de la pila donde aparecen las cartas al sacarlas, el texto de ese recuadro y la cara con la que se muestran las cartas reveladas.

En modo juego, el clic izquierdo saca la carta de arriba y la revela en la zona de revelado. El menú contextual añade barajar (mezcla el orden de la pila) y ver contenido (lista todas las cartas del mazo, con opción de sacar cualquiera). Una carta se mete en el mazo arrastrándola sobre él; también se puede meter una carta desde su propio menú contextual, eligiendo si va arriba o abajo de la pila.

Las cartas que están dentro de un mazo no se dibujan como piezas sueltas en la mesa. El tooltip del mazo puede mostrar cuántas cartas contiene en cada momento.

- **Available in**: Modo edición (ventana de propiedades) y modo juego
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
