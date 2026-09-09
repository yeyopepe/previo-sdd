# how/10 — before-analysis

Project-specific steps `pv-how` runs **at the start of step 3 (analyze and write `plan.md`)**, before it invokes `pv-internal-tech-analysis` to gather technical context. Runs on a re-analysis too (step 2 → "re-analyze"); it does **not** run when the user chooses "implement the current `plan.md`" (step 2 → jump to 3.1), since that path does no analysis. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/how/10-before-analysis.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it to load context the analysis should always have and that today depends on the user pasting it in: refresh generated types / an OpenAPI spec, dump the DB schema, regenerate a module index, pull an external dependency's docs into a local file `pv-internal-tech-analysis` can read as part of `sourcecodeDir`/docs.

Substitutable here: `{workFolder}` and `{xxxx}` (the entry already exists at `{changesDir}/inProgress/{xxxx}/` from step 1). Paths like `description.md` or the entry folder aren't dedicated variables — compose them from those two, e.g. `{workFolder}/changes/inProgress/{xxxx}/description.md`. A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-how` stops and explains — it doesn't work around it.

### Step 1: Regenerar el índice de módulos del código fuente

Antes de analizar la solución técnica de `{xxxx}`, regenerar el índice de
módulos de `src/` para que `pv-internal-tech-analysis` trabaje sobre un mapa
actualizado (funciones exportadas, en qué fichero, qué importa a qué). El
índice se mantiene aparte de la documentación de arquitectura y es fácil que
quede desfasado tras varias iteraciones.

**Command(s) to run**

Desde la raíz del repo:

```
node src/scripts/build-module-index.js
```

**Generated file(s)**

`previo-sdd/design/docs/architecture/090-module-index.md` — índice regenerado,
un bloque por módulo de `src/`. Se considera correcto si el script termina con
código `0` e imprime la línea `Índice de módulos: NN módulos escritos`.

**Notes**

- Es un fichero generado, no escrito a mano: `build-module-index.js` lo
  sobrescribe entero en cada ejecución. `pv-do` no debe editarlo luego a mano.
- Si el script falla (código ≠ 0), detener el análisis e informar al usuario:
  planificar sobre un índice desfasado es peor que parar.
- No toca `src/`; solo lee el código y reescribe ese único `.md` bajo la carpeta
  del framework.
