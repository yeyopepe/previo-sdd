# new/20 — after-entry

Project-specific steps `pv-new` runs **at the end of step 5 (state the next step)**, after step 4 validated the `design_*` files with the user and before the skill hands off to `pv-how`. It's `pv-new`'s single otherwise-non-customizable exit point. In `todo` mode (`/pv-new todo <code>`) it runs **after** the `todo/` idea is deleted, with the entry already in `inProgress/`. LITERAL seed copied by `pv-init`/`pv-update` to `{workFolder}/stuff/hooks/new/20-after-entry.md` — created only if absent, never overwritten, so steps you add here survive a framework update.

Use it to register the entry where the team tracks it: an issue in a tracker, a post in a channel, a row in a `CHANGES.md` index, a label on a board.

Substitutable here: `{workFolder}` and `{xxxx}` (the entry is at `{changesDir}/inProgress/{xxxx}/`). The entry folder and its files aren't dedicated variables — compose them, e.g. `{workFolder}/changes/inProgress/{xxxx}/description.md`. A step needing anything else (current branch, timestamp…) runs its own command for it. No `### Step` blocks below = hook skipped silently. If any step's command fails or its expected output doesn't appear, `pv-new` stops and explains — it doesn't work around it (the entry is already documented on disk; only the external registration is missing).

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
