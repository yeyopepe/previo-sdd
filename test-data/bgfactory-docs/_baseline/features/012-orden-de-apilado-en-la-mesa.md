# 012 — Orden de apilado en la mesa

**Area**: Mesa de juego

Cada componente tiene un orden explícito (1 = el más arriba de todos en la mesa de juego, n = el más abajo, siendo n el número total de componentes) que determina su apilado visual, sustituyendo al orden de inserción/creación usado anteriormente. Se controla desde la columna "Orden" del panel flotante de componentes (ver [Panel flotante de componentes](003-panel-flotante-de-componentes-con-seleccion-resaltado-arrastre-y-redimensionado.md)): el cuadro de texto de cada fila solo admite dígitos, y al confirmar (perder el foco o pulsar Enter) reordena la lista y actualiza el apilado en la mesa. Si el valor introducido coincide con el de otro componente, ese componente y los que había detrás se desplazan un puesto para dejarle hueco; los valores fuera de rango (menor que 1 o mayor que n) se ajustan al límite más cercano, y un valor vacío al confirmar descarta el cambio y restaura el anterior.

Al crear un componente nuevo, o al clonar uno ya existente (ver [Panel flotante de componentes](003-panel-flotante-de-componentes-con-seleccion-resaltado-arrastre-y-redimensionado.md)), se le asigna automáticamente el primer puesto (queda por encima de todos), desplazando un puesto hacia abajo a los que ya hubiera. Al eliminar un componente, los órdenes restantes se recalculan para seguir siendo consecutivos de 1 a n, sin huecos. El orden se guarda como parte del estado del componente (ver [Autoguardado en el navegador](029-autoguardado-en-el-navegador.md)), igual que el resto de sus propiedades.

- **Available in**: modo edición (control del orden); el apilado resultante se refleja en modo juego y modo edición.
- **Code**: 00027, 00082, 00084.
- **Since**: 2026-07-19
- **Last modified**: 2026-07-24
