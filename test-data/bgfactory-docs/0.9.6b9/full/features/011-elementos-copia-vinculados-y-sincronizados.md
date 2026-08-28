# 011 — Elementos Copia vinculados y sincronizados
**Area**: Gestión de componentes

Una Copia es un componente vinculado a un original: cuando se cambia el original, todas sus copias se actualizan solas. Se sincronizan el tipo, el nombre, la imagen, el tamaño, las etiquetas, el título, el tooltip, el efecto de profundidad y la configuración de diseño propia del tipo.

El estado de juego propio de cada copia no se sincroniza: el resultado actual de un dado y la cara mostrada de una carta son independientes copia a copia. La posición y el orden de apilado de una copia tampoco se tocan nunca.

El bloqueo de movimiento y la ocultación siguen al original mientras la copia esté sincronizada; si se cambia uno de esos dos valores directamente sobre la copia, esa copia deja de estar sincronizada y conserva sus valores propios.

Eliminar el original elimina en cascada todas sus copias. Un indicador sobre la pieza marca de un vistazo si es una copia (insignia roja) o si tiene copias vinculadas (insignia con el número de copias). El identificador de una copia se deriva del original con el sufijo -COPY- y un número.

- **Available in**: Modo edición (panel de componentes, menú contextual, pestaña de copias de la ventana de propiedades)
- **Code**: init
- **Since**: 2026-08-28
- **Last modified**: 2026-08-28
