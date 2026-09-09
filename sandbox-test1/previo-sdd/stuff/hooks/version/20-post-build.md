# version/20 — post-build

Project-specific steps `pv-version` runs **after the deliverable's artifacts are copied to `{workFolder}/versions/{XXXX}/files/`** and before the documentation is zipped (between steps 4 and 5). LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/version/20-post-build.md` — created only if absent, never overwritten.

Substitutable here: `{workFolder}`, `{XXXX}`, and the `{workFolder}/versions/{XXXX}/` paths (`.../files/`, `.../docs/`). No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-version` stops and explains — it doesn't work around it.

### Step 1: Ejecutar la batería de tests funcionales

Antes de copiar la documentación y generar el changelog, ejecutar toda la
batería de tests funcionales del proyecto (`src/test/functional/*.test.js`)
contra el código fuente real del repo — el mismo que se acaba de empaquetar en
el entregable. Guardar siempre un informe del resultado dentro de la carpeta de
la versión y, si algún test falla, detener aquí la preparación de la versión.

**Command(s) to run**

Desde la raíz del repo:

```
npm test
```

Interpretación del código de salida (documentado en
`previo-sdd/design/docs/architecture/011-functional-test-framework.md`):

- `0` — todos los tests pasan y sin anomalías de trazabilidad.
- `1` — algún test falla o hay una anomalía de trazabilidad.
- `2` — el navegador headless (Playwright/Chromium) no está instalado. En ese
  caso, ejecutar una sola vez:

  ```
  npm run test:setup
  ```

  y volver a ejecutar `npm test`. Si el segundo intento vuelve a dar `2`, es un
  fallo real de entorno: detener la preparación de la versión e informar al
  usuario de que no se ha podido preparar el entorno de tests (mostrando la
  salida de `npm run test:setup` / `npm test`). No reintentar más veces.

**Generated file(s)**

`previo-sdd/versions/{XXXX}/test-report.md` — informe de esta ejecución
concreta. Se genera SIEMPRE, haya o no fallos. Formato (texto plano dentro del
`.md`, sin tablas):

```
Versión: {XXXX}
Fecha: {YYYY-MM-DD HH:MM}

Resultado: Correcto            <- "Con fallos" si hubo algún fallo
Total: {N} — Correctos: {X} — Fallidos: {Y}
```

Los totales se leen de la línea `Total: N — OK: X — FALLOS: Y` que imprime
`npm test` en su resumen final. Si `Fallidos` > 0, añadir a continuación:

```

Tests fallidos:

{bloque de fallos copiado literalmente de la salida de `npm test`}
```

El bloque de fallos es tal cual lo imprime `npm test`: por cada fallo, la línea
`  ✗ <fichero> › <caso>` seguida de `      esperado:` / `      obtenido:` (o
`      error:` si no es un fallo de aserción). No reformatear.

**Notes**

- Este paso corre después de que el ZIP del entregable ya está construido y
  copiado a `files/` (paso 4 de `pv-version`), y antes de `copy-docs.py` y del
  changelog (pasos 5–6). Se acepta que el entregable ya exista aunque los tests
  fallen.
- **Si `npm test` termina con código `0`**: continuar con el flujo normal de
  `pv-version` (copiar documentación, changelog, resumen). No hace falta
  informar nada especial salvo que el paso se ejecutó correctamente.
- **Si `npm test` termina con código `1`** (algún test falla): NO continuar con
  el resto de `pv-version`. El `test-report.md` ya queda guardado con el detalle
  de los fallos. Informar al usuario de que hay tests fallidos e indicarle la
  ruta `previo-sdd/versions/{XXXX}/test-report.md` para consultar el detalle —
  **no volcar la lista completa de fallos en la conversación**. A continuación
  preguntarle explícitamente si quiere analizar esos fallos:
  - Si responde que sí: indicarle que cada fallo puede tratarse como una
    corrección (`/pv-fix`) o un cambio (`/pv-new`) del proyecto, o simplemente
    comentarse en la conversación; no se dispara ninguna acción automática. La
    preparación de la versión queda detenida en este punto.
  - Si responde que no: la preparación de la versión queda detenida, sin
    generar nada más.
- `pv-version` paso 4.1 ya establece que un fallo de un paso de este hook
  detiene la release; este paso se apoya en ese comportamiento nativo para los
  casos de parada.
