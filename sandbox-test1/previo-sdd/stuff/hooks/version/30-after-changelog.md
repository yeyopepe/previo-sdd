# version/30 — after-changelog

Project-specific steps `pv-version` runs **after the changelog is drafted and before the final summary** (between steps 6 and 7). Runs before the summary on purpose, so step 7 can report what it produced (e.g. "uploaded to X", "release notes in `notes.pdf`"). LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/version/30-after-changelog.md` — created only if absent, never overwritten.

Substitutable here: `{workFolder}`, `{XXXX}`, and the `{workFolder}/versions/{XXXX}/` paths. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-version` stops and explains — it doesn't work around it.

### Step 1: Empaquetar el ZIP del entregable

Una vez que `previo-sdd/versions/{XXXX}/` ya tiene `docs/features.zip` y los
artefactos en `files/` (y, si la versión lleva cambios funcionales, el
`changelog.md`), empaquetar todo el contenido publicable en un único ZIP.

**Command(s) to run**

Desde la raíz del repo:

```
python src/scripts/package-version-zip.py {XXXX}
```

**Generated file(s)**

`previo-sdd/versions/{XXXX}/bgfactory_v{XXXX}.zip` (dentro de la propia carpeta de
la versión). En la raíz del ZIP:

- `changelog.md` (opcional: solo si existe; se omite en versiones sin cambios
  funcionales que registrar)
- `features.zip` (copiado de `docs/features.zip`)
- los ficheros sueltos de `files/*` (el HTML autocontenido y ambos README)
- la carpeta `files/samples/` íntegra, bajo `samples/` dentro del ZIP

**Notes**

- `changelog.md` es opcional; el resto de elementos son obligatorios y el script
  aborta sin dejar el ZIP a medias si falta alguno o si hay colisión de nombres
  dentro del comprimido.
- Si ya existía un `bgfactory_v{XXXX}.zip` previo, lo borra antes de regenerarlo.
- Solo requiere Python 3 de la librería estándar (sin Node.js).
