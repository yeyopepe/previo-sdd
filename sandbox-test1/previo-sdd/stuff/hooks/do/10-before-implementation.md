# do/10 — before-implementation

Project-specific steps `pv-do` runs **before it starts implementing** (at the top of step 2, before any code is edited). `pv-fix`'s fast-track branch also runs these steps before it applies a trivial change, since it edits code directly without going through `pv-do`. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/do/10-before-implementation.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Substitutable here: `{workFolder}` and `{xxxx}` (the change/fix code being implemented — its folder already exists at `{workFolder}/changes/inProgress/{xxxx}/`). A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-do` stops and explains — it doesn't work around it.

### Step 1: Comprobar que el árbol de trabajo está limpio antes de tocar código

Antes de empezar a implementar el cambio `{xxxx}`, verificar que no hay
modificaciones sin commitear en el código fuente del repo. Así, el diff que
quede tras `pv-do` es exactamente el de este cambio y nada más — importante
porque `src/scripts/build.py` incrementa `src/data/version.js` como efecto
secundario y es fácil arrastrar cambios ajenos sin darse cuenta.

**Command(s) to run**

Desde la raíz del repo:

```
git status --porcelain -- src/
```

**Generated file(s)**

No genera ningún fichero — es una comprobación de precondición. Se considera
correcta si la salida es **vacía** (sin líneas). Si hay cualquier línea,
detener la implementación e informar al usuario de qué ficheros bajo `src/`
tienen cambios pendientes, para que decida si commitearlos, descartarlos o
seguir a pesar de todo (en cuyo caso re-lanzará `pv-do`).

**Notes**

- Solo mira `src/`; los cambios dentro de `previo-sdd/` (la propia carpeta del
  framework, p. ej. el `plan.md` que `pv-how` acaba de escribir) son esperados
  y no cuentan.
- No hace `git add`, `git stash` ni ninguna operación destructiva: solo lee el
  estado.
