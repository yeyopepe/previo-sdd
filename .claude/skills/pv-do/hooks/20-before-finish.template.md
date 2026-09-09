# do/20 — before-finish

Project-specific steps `pv-do` runs **as the last thing before finishing** — after the code is implemented and the synced documentation is updated (end of step 2.1), and before the change/fix folder is moved to `implemented/` (step 3). LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/do/20-before-finish.md` — created only if absent, never overwritten.

Substitutable here: `{workFolder}` and `{xxxx}` (the change/fix folder is still at `{workFolder}/changes/inProgress/{xxxx}/` at this point). No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-do` stops and explains — it doesn't work around it.

<!-- Add one "### Step N: {name}" block per step, in run order. Delete this comment when you add the first. -->

<!--
### Step 1: {name}

**Command(s) to run**

[Exact command(s), in order, from the repo root.]

**Generated file(s)**

[What the step produces and how to verify it — a path, a log line, an exit code. Omit if the step only checks a precondition.]

**Notes**

[Prerequisites, side effects, what not to touch. Optional.]
-->
