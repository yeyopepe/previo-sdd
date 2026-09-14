# fix/10 — before-entry

Project-specific steps `pv-fix` runs on the **fast-track branch** (trivial change, bug or not), right after `description.md`/`history.md` are created and before the change is applied to code. It's the fast-track's own barrier — distinct from the `do/10-before-implementation` / `do/20-after-implementation` hooks the fast-track also runs (those are `pv-do`'s, shared because the fast-track edits code the same way `pv-do` does). This one exists because a trivial change skips `plan.md` and `pv-how` entirely, so it's the only insertion point a project has before a fast-tracked edit lands. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/fix/10-before-entry.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it for a cheap minimum barrier on trivial changes: run the linter/formatter on the touched file(s), require a test already covers the touched line, block if a target file is on a do-not-touch-without-review list. Keep it fast — the whole appeal of the fast-track is that it's a single turn; a slow step here defeats that.

Substitutable here: `{workFolder}` and `{xxxx}` (the entry already exists at `{changesDir}/inProgress/{xxxx}/`). Paths like `description.md` or the entry folder aren't dedicated variables — compose them from those two, e.g. `{workFolder}/changes/inProgress/{xxxx}/description.md`. There is no dedicated variable for the target file(s) yet — a step needing them runs its own command (e.g. derive them from the request, or from `git status`/`git diff`). No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-fix` stops and explains — it doesn't apply the change and doesn't work around it.

### Step 1: Comprobar que el árbol de trabajo está limpio antes de aplicar el fix

Antes de tocar código para este fix rápido `{xxxx}`, verificar que no hay
modificaciones sin commitear en el código fuente del repo. Así, si algo sale
mal a mitad del turno, es fácil distinguir lo que trae este fix de lo que ya
estaba ahí.

**Command(s) to run**

Desde la raíz del repo:

```
git status --porcelain -- src/
```

**Generated file(s)**

No genera ningún fichero — es una comprobación de precondición. Se considera
correcta si la salida es **vacía** (sin líneas). Si hay cualquier línea,
detener antes de aplicar el fix e informar al usuario de qué ficheros bajo
`src/` tienen cambios pendientes, para que decida si commitearlos,
descartarlos o seguir a pesar de todo (en cuyo caso re-lanzará `pv-fix`).

**Notes**

- Solo mira `src/`; los cambios dentro de `previo-sdd/` (la propia carpeta del
  framework, p. ej. el `description.md` que este mismo `pv-fix` acaba de
  crear) son esperados y no cuentan.
- No hace `git add`, `git stash` ni ninguna operación destructiva: solo lee el
  estado.
