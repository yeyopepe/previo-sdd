# version/05 — before-guardrail

Project-specific steps `pv-version` runs **at the very start**, before step 0.5 (the `implemented/` must be empty guardrail) and before the version code `{XXXX}` is resolved or `versions/{XXXX}/` is created. It's the earliest possible abort point — it can stop the release before even checking `implemented/`. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/version/05-before-guardrail.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it to abort cheaply: git tree clean, on the right branch, CI green, no tag already exists with the planned name. Today the only automatic guardrail is `implemented/` being empty.

Only `{workFolder}` is substitutable in this hook; `{XXXX}` and the `versions/{XXXX}/` paths don't exist yet (same as `10-before-version`). A step needing anything else (current branch, timestamp…) runs its own command for it — e.g. `git rev-parse --abbrev-ref HEAD`. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-version` stops and explains — it doesn't work around it.

### Step 1: Comprobar que se está en `main` y con el árbol limpio

Antes de arrancar la preparación de una versión, verificar que la rama activa
es `main` y que no hay cambios sin commitear en ningún sitio del repo. Una
versión debe cortarse siempre desde un `main` limpio: el ZIP del entregable y
los ZIP de documentación se generan a partir del estado real del árbol de
trabajo, y cualquier cambio suelto se colaría en la entrega sin dejar rastro
en git.

**Command(s) to run**

Desde la raíz del repo:

```
git rev-parse --abbrev-ref HEAD
git status --porcelain
```

**Generated file(s)**

No genera ningún fichero — es una comprobación de precondición. Se considera
correcta si:

- la primera orden imprime exactamente `main`, y
- la segunda orden no imprime **ninguna** línea (árbol totalmente limpio).

Si la rama no es `main`, detener e informar al usuario de en qué rama está y de
que debe cambiar a `main` (o confirmar explícitamente que quiere cortar la
versión desde otra rama, en cuyo caso re-lanzará `/pv-version`). Si hay líneas
en `git status --porcelain`, detener e informar de la lista de ficheros
pendientes para que decida antes de continuar.

**Notes**

- Solo lee estado: no hace `git add`, `git stash`, `git checkout` ni ninguna
  operación que toque el árbol de trabajo.
- Corre antes incluso del guardarraíl de `implemented/` vacío (paso 0.5 de
  `pv-version`): si esto falla, no se llega a listar `changes/implemented/`.
