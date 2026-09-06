- **Name**: Modal de carga al agrupar y desagrupar en modo edición
- **Code**: 00224
- **Type**: change
- **Creation date**: 2026-08-19

## Full description

Al agrupar o desagrupar elementos en modo edición, la aplicación muestra la modal de "operación en curso" (spinner + texto breve, ya usada en otras acciones potencialmente lentas de la app, como al añadir varias cartas a un mazo) mientras dura la operación. Objetivo: dar feedback visual al usuario cuando la selección afectada es grande, en vez de que la pantalla quede momentáneamente sin respuesta sin ninguna explicación.

Se aplica en los tres puntos donde hoy se puede agrupar o desagrupar en modo edición:

1. Opción "Agrupar" del menú contextual de un elemento.
2. Opción "Desagrupar" del menú contextual de un elemento.
3. Botón "Desagrupar" de la fila de un grupo en el panel flotante "Componentes".

**Comportamiento de la modal**: aparece justo al iniciar cualquiera de estas tres acciones y se cierra ella sola en cuanto termina — no tiene botones ni ninguna vía para cerrarla manualmente (ni click fuera, ni tecla Escape), igual que el resto de modales de este tipo ya presentes en la app.

**Texto mostrado**, según el número de elementos afectados:
- Al agrupar: "Agrupando N elemento(s)…"
- Al desagrupar: "Desagrupando N elemento(s)…"

### Preguntas de alcance resueltas con el usuario

- **¿Sigue siendo una operación bloqueante mientras dura, o debe dejar de bloquear la pantalla (troceando el trabajo para que no se note la espera)?** El usuario confirmó explícitamente que quiere reutilizar el mismo comportamiento que ya tienen las demás modales de este tipo en la app: la operación sigue ejecutándose de un tirón mientras dura, la modal solo añade el aviso visual de que hay algo en curso. No se pidió ningún mecanismo nuevo para trocear el trabajo ni evitar el bloqueo en sí.
- **¿Se aplica en los tres puntos donde hoy existe agrupar/desagrupar, o solo en el menú contextual?** Confirmado que se aplica en los tres.
- **Casos borde de error o cancelación a mitad**: no aplican — al ser una operación que se ejecuta de un tirón, no hay ningún estado intermedio que gestionar, igual que en el resto de usos de esta misma modal ya presentes en la app.

## Notas técnicas

- Patrón ya existente a reutilizar tal cual: `ui/progressModal.js`, función `runWithProgressModal(text, work)`. Documentado en `design/docs/style/03-modales-menus.md` §12.1.2 ("Modal de operación en curso").
- Ya usado en el propio `src/modes/edit/editMode.js` para "añadir cartas a un mazo" (línea ~766 antes del cambio) — mismo patrón exacto a replicar, incluido el texto en formato `"Verbo N elemento(s)…"`.
- Puntos a modificar en `src/modes/edit/editMode.js`:
  - Entrada de menú "Agrupar" (handler `onClick`, aprox. líneas 654-667).
  - Entrada de menú "Desagrupar" (handler `onClick`, aprox. líneas 668-679).
  - Callback `onUngroup` pasado al panel de Componentes (aprox. líneas 802-810).
- `runWithProgressModal` ya está importado en `editMode.js` (usado por el caso del mazo) — no requiere nuevo import.
- Sin dimensión visual nueva (reutiliza `.progress-modal` sin cambios), sin nueva navegación UI y sin datos estructurados nuevos.
