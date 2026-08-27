- **Creation date**: 2026-08-19
- **Risk**: 1/10 — Riesgo mínimo

## (a) Notas funcionales

**Fuera de alcance:** no se toca ningún otro comportamiento de agrupar/desagrupar (reglas de habilitación del menú, edición de propiedades del grupo, disolución automática, etc.) ni el componente `ui/progressModal.js` en sí — se reutiliza tal cual, sin variante nueva. La operación sigue siendo síncrona y bloqueante mientras dura; no se trocea el trabajo en lotes ni se cede el hilo al navegador.

**Dudas resueltas con el usuario:** confirmado en la fase de análisis funcional (`description.md`) que la modal debe reutilizar exactamente el patrón ya existente (`runWithProgressModal`, mismo comportamiento que "añadir cartas a un mazo"), sin mecanismo nuevo de troceado asíncrono real. Confirmado también el alcance de los 3 puntos y el texto del mensaje.

## (b) Solución técnica

- [ ] **`src/modes/edit/editMode.js` — envolver "Agrupar" del menú contextual con `runWithProgressModal`.** En la entrada de menú `label: 'Agrupar'` (dentro de `generalItems`, handler `onClick` actual en torno a las líneas 654-667), mover todo el cuerpo actual del `onClick` dentro de un `work` pasado a `runWithProgressModal(text, work)`, en el mismo punto donde hoy se ejecuta directo:
  ```js
  onClick: () => {
    const count = affectedComponents.length;
    const text = `Agrupando ${count} elemento${count === 1 ? '' : 's'}…`;
    runWithProgressModal(text, () => {
      const newGroupId = nextGroupId(getComponents());
      const minOrder = Math.min(...affectedComponents.map((c) => c.order));
      for (const c of affectedComponents) {
        replaceComponent(c.id, updateComponent(c, { groupId: newGroupId }));
      }
      addGroup(createGroup({ id: newGroupId }));
      reorderGroupBlock(affectedComponents.map((c) => c.id), minOrder);
    });
  },
  ```
  `count` se calcula con `affectedComponents.length` (variable ya disponible en el closure, es la misma lista que usa el cuerpo actual). Ningún import nuevo: `runWithProgressModal` ya está importado (línea 34).
- [ ] **`src/modes/edit/editMode.js` — envolver "Desagrupar" del menú contextual con `runWithProgressModal`.** En la entrada de menú `label: 'Desagrupar'` (mismo bloque `generalItems`, handler `onClick` actual en torno a las líneas 668-679), mismo patrón:
  ```js
  onClick: () => {
    const groupId = selectedGroup?.id;
    const count = affectedComponents.length;
    const text = `Desagrupando ${count} elemento${count === 1 ? '' : 's'}…`;
    runWithProgressModal(text, () => {
      for (const c of affectedComponents) {
        replaceComponent(c.id, updateComponent(c, { groupId: null }));
      }
      if (groupId != null) removeGroup(groupId);
    });
  },
  ```
  `groupId` se lee de `selectedGroup?.id` **antes** de entrar en `work` (no depende de ningún estado que cambie durante la operación, solo se usa como valor cerrado), igual que en el código actual.
- [ ] **`src/modes/edit/editMode.js` — envolver `onUngroup` del panel de Componentes con `runWithProgressModal`.** En el callback `onUngroup` pasado a `renderComponentList` (en torno a las líneas 802-810), mismo patrón, usando `memberIds.length` como `count` (variable ya recibida como parámetro):
  ```js
  onUngroup: (memberIds) => {
    const first = getComponents().find((comp) => comp.id === memberIds[0]);
    const groupId = first?.groupId;
    const count = memberIds.length;
    const text = `Desagrupando ${count} elemento${count === 1 ? '' : 's'}…`;
    runWithProgressModal(text, () => {
      for (const id of memberIds) {
        const c = getComponents().find((comp) => comp.id === id);
        if (c) replaceComponent(id, updateComponent(c, { groupId: null }));
      }
      if (groupId != null) removeGroup(groupId);
    });
  },
  ```
  `first`/`groupId` se calculan antes de `work` (lectura previa, no mutan nada), igual que en el código actual — solo el bucle de mutación y el `removeGroup` final entran en `work`.

En los tres casos, el criterio es el mismo que ya documenta el proyecto para este patrón (bug 00219, `design/docs/style/03-modales-menus.md` §12.1.2): toda mutación de estado que dispare un re-render (`replaceComponent`/`addGroup`/`removeGroup`/`reorderGroupBlock`, todas ellas al final emiten el evento que hace que `main.js` vuelva a renderizar la pantalla activa) debe quedar dentro de `work`, nunca antes — así el doble `requestAnimationFrame` interno de `runWithProgressModal` garantiza que el spinner ya está pintado en pantalla cuando arranca el bloqueo síncrono real.

## (d) Cambios de estilo

`design/docs/style/03-modales-menus.md` §12.1.2 ("Modal de operación en curso") ya documenta el patrón en genérico y enumera sus usos ("Primer uso: arrastrar una selección múltiple de cartas sobre un mazo..."). Añadir ahí una frase indicando que agrupar/desagrupar en modo edición (00224) es un segundo uso del mismo patrón, sin ninguna variante nueva — no se documenta como excepción, solo se amplía la lista de usos existente.

## (e) Verificación

- [ ] En modo edición, seleccionar 2 o más elementos sueltos (ninguno ya agrupado) y elegir "Agrupar" en el menú contextual: aparece brevemente la modal con spinner y texto "Agrupando N elemento(s)…" (N = número de elementos seleccionados), se cierra sola, y los elementos quedan agrupados igual que antes del cambio (mismo comportamiento funcional, solo con la modal añadida).
- [ ] Con un grupo ya formado, seleccionar ese grupo y elegir "Desagrupar" en el menú contextual: aparece la modal con texto "Desagrupando N elemento(s)…" (N = número de miembros del grupo), se cierra sola, y los elementos quedan desagrupados igual que antes del cambio.
- [ ] Con un grupo ya formado, pulsar el botón "Desagrupar" de su fila en el panel flotante "Componentes": mismo comportamiento y mismo texto que el punto anterior, disparado desde este segundo punto de entrada.
- [ ] Ninguna otra acción del menú contextual ni del panel de Componentes (Ocultar/Mostrar, Clonar, Copiar, Eliminar, Editar) muestra la modal — solo agrupar y desagrupar.
- [ ] El resto de comportamiento de grupos (habilitación de "Agrupar"/"Desagrupar" según selección, disolución automática al quedar ≤1 miembro, edición de propiedades del grupo) sigue funcionando exactamente igual que antes del cambio.
