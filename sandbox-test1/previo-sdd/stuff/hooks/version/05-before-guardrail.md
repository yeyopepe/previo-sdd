# version/05 — before-guardrail

Project-specific steps `pv-version` runs **at the very start**, before step 0.5 (the `implemented/` must be empty guardrail) and before the version code `{XXXX}` is resolved or `versions/{XXXX}/` is created. It's the earliest possible abort point — it can stop the release before even checking `implemented/`. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/version/05-before-guardrail.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-version` stops and explains — it doesn't work around it.

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
