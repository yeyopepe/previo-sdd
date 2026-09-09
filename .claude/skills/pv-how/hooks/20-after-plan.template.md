# how/20 — after-plan

Project-specific steps `pv-how` runs **after step 3.1 (the risk median is written to `.metadata.json` and verified)** and before step 3.2 (asking whether to implement). The point is after 3.1 on purpose, so a step here can read the already-persisted risk median and publish it where the team consumes it. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/how/20-after-plan.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it for checks on the plan itself and for export: a `plan.md` format linter, verifying the paths cited in sections (c)/(d) exist, opening the implementation ticket in a tracker with the plan summary and the risk median.

Substitutable here: `{workFolder}` and `{xxxx}`. The path to `plan.md` isn't a dedicated variable — compose it: `{workFolder}/changes/inProgress/{xxxx}/plan.md` (same for `description.md`, `.metadata.json`). A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-how` stops and explains — it doesn't work around it.

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
