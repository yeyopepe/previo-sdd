# do/20 — before-finish

Project-specific steps `pv-do` runs **as the last thing before finishing** — after the code is implemented and the synced documentation is updated (end of step 2.1), and before the change/fix folder is moved to `implemented/` (step 3). `pv-fix`'s fast-track branch also runs these steps after it applies a trivial change and writes `## Applied changes`, before it moves the folder. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/do/20-before-finish.md` — created only if absent, never overwritten.

Substitutable here: `{workFolder}` and `{xxxx}` (the change/fix folder is still at `{workFolder}/changes/inProgress/{xxxx}/` at this point). No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-do` stops and explains — it doesn't work around it.

### Step 1: Build interna de verificación tras implementar el cambio

Con el código de `{xxxx}` ya implementado y la documentación actualizada,
lanzar una build interna del proyecto para confirmar que el bundle sigue
generándose sin errores con el cambio dentro. Es la misma build que se usa
para probar a mano; NO es el entregable oficial (eso lo hace `pv-version`).

**Command(s) to run**

Desde la raíz del repo:

```
python src/scripts/build.py
```

**Generated file(s)**

`src/_output/versions/index-v{NNNNN}.html` — el bundle autocontenido, con
`{NNNNN}` el nuevo número de build (`build.py` lo incrementa en
`src/data/version.js`). Se considera correcto si el script termina con código
`0` e imprime la línea `Build generada en src\_output\versions\index-vNNNNN.html`.

**Notes**

- `build.py` incrementa `CURRENT_VERSION` en `src/data/version.js` como efecto
  secundario. Ese cambio queda sin commitear en el árbol de trabajo — es
  correcto, es la fuente de verdad del contador interno; no lo descartes.
- Si `build.py` falla (código ≠ 0), detener aquí: **no** mover la carpeta a
  `implemented/`. Informar al usuario del error de build (con la salida del
  script) para que lo corrija antes de reintentar `pv-do`.
- Este paso no ejecuta la batería de tests funcionales (`npm test`) — eso se
  hace en el hook `20-post-build` de `pv-version`, sobre el entregable ya
  empaquetado.
