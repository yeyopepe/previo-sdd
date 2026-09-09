# how/20 — after-plan

Project-specific steps `pv-how` runs **after step 3.1 (the risk median is written to `.metadata.json` and verified)** and before step 3.2 (asking whether to implement). The point is after 3.1 on purpose, so a step here can read the already-persisted risk median and publish it where the team consumes it. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/how/20-after-plan.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it for checks on the plan itself and for export: a `plan.md` format linter, verifying the paths cited in sections (c)/(d) exist, opening the implementation ticket in a tracker with the plan summary and the risk median.

Substitutable here: `{workFolder}` and `{xxxx}`. The path to `plan.md` isn't a dedicated variable — compose it: `{workFolder}/changes/inProgress/{xxxx}/plan.md` (same for `description.md`, `.metadata.json`). A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-how` stops and explains — it doesn't work around it.

### Step 1: Validar que `plan.md` cita rutas de código reales

Tras escribir `plan.md` para `{xxxx}`, comprobar que todos los ficheros que la
sección (b) (y, si existen, la (c)/(d)) menciona como "a tocar" existen de
verdad en el repo. Un `plan.md` que cita rutas inexistentes casi siempre
significa un error de análisis que conviene resolver antes de que `pv-do`
empiece a implementar.

**Command(s) to run**

Desde la raíz del repo:

```
python previo-sdd/design/scripts/check-plan-paths.py --xxxx {xxxx}
```

El script lee `previo-sdd/changes/inProgress/{xxxx}/plan.md`, extrae toda ruta
que empiece por `src/` citada entre backticks y verifica que exista en disco.

**Generated file(s)**

No genera ningún fichero. Se considera correcto si el script termina con código
`0` e imprime `check-plan-paths: N rutas verificadas, 0 inexistentes`. Si
imprime alguna ruta bajo `RUTAS INEXISTENTES:` (código `1`), detener e informar
al usuario de la lista, para que corrija `plan.md` (o el propio análisis) antes
de decidir si implementar.

**Notes**

- Solo valida rutas bajo `src/`; las rutas de la propia carpeta del framework
  (`previo-sdd/…`) no se comprueban.
- Es una comprobación de solo lectura: no edita `plan.md` ni ningún otro
  fichero.
- Corre después de que la mediana de riesgo ya está en `.metadata.json`, así
  que un paso adicional podría además leerla de ahí para adjuntarla a un ticket.
