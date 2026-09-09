# how/10 — before-analysis

Project-specific steps `pv-how` runs **at the start of step 3 (analyze and write `plan.md`)**, before it invokes `pv-internal-tech-analysis` to gather technical context. Runs on a re-analysis too (step 2 → "re-analyze"); it does **not** run when the user chooses "implement the current `plan.md`" (step 2 → jump to 3.1), since that path does no analysis. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/how/10-before-analysis.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it to load context the analysis should always have and that today depends on the user pasting it in: refresh generated types / an OpenAPI spec, dump the DB schema, regenerate a module index, pull an external dependency's docs into a local file `pv-internal-tech-analysis` can read as part of `sourcecodeDir`/docs.

Substitutable here: `{workFolder}` and `{xxxx}` (the entry already exists at `{changesDir}/inProgress/{xxxx}/` from step 1). Paths like `description.md` or the entry folder aren't dedicated variables — compose them from those two, e.g. `{workFolder}/changes/inProgress/{xxxx}/description.md`. A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-how` stops and explains — it doesn't work around it.

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
