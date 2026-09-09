# do/10 — before-start

Project-specific steps `pv-do` runs **before it starts implementing** (at the top of step 2, before any code is edited). `pv-fix`'s fast-track branch also runs these steps before it applies a trivial change, since it edits code directly without going through `pv-do`. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/do/10-before-start.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Substitutable here: `{workFolder}` and `{xxxx}` (the change/fix code being implemented — its folder already exists at `{workFolder}/changes/inProgress/{xxxx}/`). A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-do` stops and explains — it doesn't work around it.

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
