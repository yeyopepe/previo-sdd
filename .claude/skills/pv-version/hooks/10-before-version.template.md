# version/10 — before-version

Project-specific steps `pv-version` runs **before step 1**, after the `implemented/` guardrail (step 0.5) and before the version code `{XXXX}` is resolved. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/version/10-before-version.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Only `{workFolder}` is substitutable in this hook; `{XXXX}` and the `versions/{XXXX}/` paths don't exist yet. A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-version` stops and explains — it doesn't work around it.

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
