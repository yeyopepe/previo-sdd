# new/20 — after-entry

Project-specific steps `pv-new` runs **at the end of step 5 (state the next step)**, after step 4 validated the `design_*` files with the user and before the skill hands off to `pv-how`. It's `pv-new`'s single otherwise-non-customizable exit point. In `todo` mode (`/pv-new todo <code>`) it runs **after** the `todo/` idea is deleted, with the entry already in `inProgress/`. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/new/20-after-entry.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it to register the entry where the team tracks it: an issue in a tracker, a post in a channel, a row in a `CHANGES.md` index, a label on a board.

Substitutable here: `{workFolder}` and `{xxxx}` (the entry is at `{changesDir}/inProgress/{xxxx}/`). The entry folder and its files aren't dedicated variables — compose them, e.g. `{workFolder}/changes/inProgress/{xxxx}/description.md`. A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-new` stops and explains — it doesn't work around it (the entry is already documented on disk; only the external registration is missing).

### Step 1: Añadir la entrada al índice `CHANGES.md` del repo

Con la entrada `{xxxx}` ya documentada en `inProgress/`, añadir una fila al
índice `CHANGES.md` de la raíz del repo, que el equipo consulta para ver de un
vistazo qué hay en curso sin abrir la carpeta `previo-sdd/changes/`.

**Command(s) to run**

Desde la raíz del repo:

```
python previo-sdd/design/scripts/append-changes-index.py --xxxx {xxxx}
```

El script lee el `**Type**` y el nombre/resumen de
`previo-sdd/changes/inProgress/{xxxx}/description.md` y añade (o actualiza, si
ya existía) una línea en `CHANGES.md` con la fecha de hoy, bajo la sección
`## En curso`.

**Generated file(s)**

`CHANGES.md` (raíz del repo) — con una nueva fila
`| {xxxx} | {tipo} | {nombre} | {YYYY-MM-DD} | inProgress |`. Se considera
correcto si el script termina con código `0` e imprime
`append-changes-index: fila de {xxxx} escrita`.

**Notes**

- `append-changes-index.py` es idempotente: si `{xxxx}` ya tenía fila, la
  reescribe en su sitio en vez de duplicarla.
- Deja `CHANGES.md` modificado sin commitear — es intencionado; el commit del
  índice va junto al del cambio cuando el equipo lo decida.
- Si el script falla (código ≠ 0), detener e informar al usuario: la entrada ya
  está documentada en disco, solo falta el alta en el índice.
