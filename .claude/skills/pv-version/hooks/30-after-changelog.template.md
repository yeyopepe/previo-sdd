# version/30 — after-changelog

Project-specific steps `pv-version` runs **after the changelog is drafted and before the final summary** (between steps 6 and 7). Runs before the summary on purpose, so step 7 can report what it produced (e.g. "uploaded to X", "release notes in `notes.pdf`"). LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/version/30-after-changelog.md` — created only if absent, never overwritten.

Substitutable here: `{workFolder}`, `{XXXX}`, and the `{workFolder}/versions/{XXXX}/` paths. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-version` stops and explains — it doesn't work around it.

<!-- Add one "### Step N: {name}" block per step, in run order. Delete this comment when you add the first. -->

<!--
### Step 1: {name}

**Command(s) to run**

[Exact command(s), in order, from the repo root.]

**Generated file(s)**

[What the step produces and how to verify it.]

**Notes**

[Prerequisites, side effects, what not to touch. Optional.]
-->
