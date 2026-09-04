---
name: pv-version
description: Prepares a project release/version at {workFolder}/versions/{XXXX}/ — generates the deliverable, copies the current technical documentation, and chains pv-internal-changelog for the functional changelog. Part of the pv-* framework. Trigger: /pv-version <XXXX>, or when the user asks to prepare/package a deliverable version.
argument-hint: <XXXX of the version to prepare>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b14
  uses: [pv-internal-changelog]
---

# pv-version

Orchestrates preparing a project release: resolves change/fix entries pending closure, generates the deliverable, copies the current technical documentation, and chains `pv-internal-changelog` to draft the functional changelog from `{workFolder}/changes/closed/`.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation, including the fixed messages below. Copying technical documentation and generating the deliverable are copy/build operations, not new prose (`language` doesn't apply); it chains `pv-internal-changelog` for `changelog.md`. `{workFolder}/stuff/how-to-compile-version.md` and `{workFolder}/stuff/custom-version-pipeline.md`, which this skill reads/writes/executes directly (see steps 0.2, 0.6 and 3), also follow `interaction.language` — there's no dedicated language field for `stuff/*` in the schema. If `language` is not configured anywhere, everything is English.

**This skill is installed framework, not editable from a consumer project.** If the user asks to change *how* the version flow works (add a step, change the order, a precondition check, publish something when it finishes), the right answer is **not** to edit this `SKILL.md`, `workflow.version.md`, or any file under `.claude/skills/pv-*/`. There are exactly two customization points, both in `{workFolder}/stuff/`: compiling the deliverable → `how-to-compile-version.md` (steps 3–4); the project's own steps at three points of the flow (before starting / in the middle / at the end) → `custom-version-pipeline.md` (step 0.6). If what's asked doesn't fit either one, say so and propose opening a change in the framework repo — never a local patch to the skill. The presence of `framework.frameworkStatus` in `pv-context.json` means these skills are managed via `pv-update`; editing them by hand leaves them inconsistent (step 0 already checks versions).

`{workFolder}` is `.claude/pv-context.json`'s `framework.workFolder` value (default `"/previo-sdd"`, never asked/confirmed by `pv-init`). Inside it, `changes/`, `versions/` and `stuff/` are fixed-name subfolders the framework creates by itself — not asked about or configured separately. `{workFolder}/stuff/` holds this skill's own project-specific files: `how-to-compile-version.md` (how to build the deliverable) and `custom-version-pipeline.md` (the project's own steps at three points of the flow — see step 0.6). `{workFolder}/versions/{XXXX}/` is a free-text numbering space, chosen by the user on each invocation, with no relation to change/fix's `xxxx` nor to any other folder called "versions" that might exist in the repo (e.g. a build script's own output): this skill never reads or writes outside `{workFolder}/versions/`.

**Before any other step**, read [`workflow.version.md`](workflow.version.md) — it's the source of truth for this flow's sequence and branches (see `pv-design.en.md`'s "Workflow diagrams" section for the notation). If it doesn't exist or can't be followed, stop and report that instead of improvising the flow from the prose below. The numbered steps that follow are each node's detail (which script to run, what exact text to use) — the diagram governs sequence and branching; if the two ever disagree, the diagram wins and this prose gets corrected to match. Don't confuse it with [`version-flow-diagram.template.md`](version-flow-diagram.template.md): that one is a simplified, user-facing diagram shown as-is when the user asks how the process works (step 0.1) — it doesn't drive this skill's own execution.

## 0. Framework initialized

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Additionally, before continuing, check that the framework's installed version is verified: read `metadata.version` from `.claude/skills/pv-init/SKILL.md`'s frontmatter (a handful of lines, not the whole file) and compare it against `framework.frameworkStatus.lastVerifiedVersion` in the `pv-context.json` you already loaded. If `frameworkStatus` is missing entirely, or `lastVerifiedVersion` doesn't match `pv-init/SKILL.md`'s real version, don't continue: tell the user the framework was updated (or has never been verified) and that they must run `pv-update` first — a stale `pv-context.json` can mean outdated templates, marker conventions, or other assumptions this skill relies on. Same stop if `framework.frameworkStatus.blocked` is already `true` (show `blockedReason` if present). This is a cheap, live comparison of two version strings already in hand — it doesn't require `pv-update` to have run before for the check itself to work, only for it to pass.

## 0.1. Process diagram, on demand

At any point during invocation, if the user asks how the process works or explicitly asks for "the diagram"/"the flow", show [`version-flow-diagram.template.md`](version-flow-diagram.template.md)'s full content as-is (without regenerating or paraphrasing it) and continue wherever the flow had gotten to.

## 0.2. Purely informational invocation about the build process

The user might invoke this skill only to report a change in the build/deliverable-generation procedure (e.g. "the build now also generates a rules PDF", "change the build command to..."), without explicitly asking to prepare a release right now.

If that's the intent: update `{workFolder}/stuff/how-to-compile-version.md` with the new information, following [`how-to-compile-version.template.md`](how-to-compile-version.template.md) (including its support for multi-step/multi-artifact processes if applicable — see the template itself), and **don't continue with the rest of the flow**. Explicitly ask the user whether they want to launch the versioning process now with this now-updated procedure. Only if they specifically confirm, continue with step 0.5; if they don't confirm (or don't answer that), stop here.

## 0.5. Guardrail: `implemented/` must be empty before starting

When starting the versioning process there can be no change/fix in the `implemented` state. List `{workFolder}/changes/implemented/`'s folders; if there's any, **there's no way to proceed at all** (not creating the version's folder, nor anything that follows) until all of them are resolved.

For each folder found, explicitly ask the user whether that change/fix moves to `closed`:

- If they confirm, run (from the repo root):

  ```
  python .claude/skills/pv-internal-workflow/scripts/move-change.py --xxxx <xxxx> --from implemented --to closed
  ```

- If they don't confirm, **wait for the user's confirmation** without continuing the flow — the entry isn't skipped or ignored, there's no "continue anyway".

Repeat until `implemented/` is empty; only then continue with step 0.6.

## 0.6. Load the custom pipeline

Look for `{workFolder}/stuff/custom-version-pipeline.md`. If it doesn't exist, continue as normal without saying anything (an old project that hasn't run `pv-update` since this was added won't have it — same behavior as before). If it exists, **read it and parse its steps per section**: three fixed `##` headings (`## Before starting` / `## In the middle` / `## At the end`, translated to `interaction.language`), each holding 0..N `### Step N: {name}` blocks with `**Command(s) to run**` / `**Generated file(s)**` / `**Notes**` (same shape as `how-to-compile-version.md`). A section with zero steps is skipped silently at its anchor.

Each step is prose + a command block run from the repo root, with a note of what it produces / how to verify. Substitutable variables: `{workFolder}` everywhere; `{XXXX}` and the `{workFolder}/versions/{XXXX}/` paths (`.../files/`, `.../docs/`) **only** in "In the middle" and "At the end" — "Before starting" runs before step 1, so `{XXXX}` isn't resolved there. Don't substitute anything now; do it at each anchor, at execution time. Nothing else is substituted — a step needing e.g. the current branch runs its own command for it.

Same guardrail as step 0.2/§top: if the user is asking to *change* how the flow works, and it fits one of the three sections, the fix is to edit this file (via this skill), not `SKILL.md` or `workflow.version.md`.

## 0.7. Hook: "Before starting"

If the custom pipeline (step 0.6) defines steps for the "Before starting" section, run them **now**, in order, before resolving `XXXX`. Only `{workFolder}` is substituted here — `{XXXX}` and the `versions/{XXXX}/` paths aren't available yet. Run each step's command(s) from the repo root and verify what it says it produces. If a step's command fails or its expected output doesn't appear, **stop and explain it to the user** instead of improvising an alternative — same criterion as step 4. If there are no steps for this section, continue silently.

## 1. Resolve `XXXX`

If not given when invoking, ask explicitly — don't assume it. It's free text chosen by the user, not computed or validated against `numberWidth` (a numbering space independent from change/fix's).

## 2. Create the version's folder

Run from the repo root:

```
python .claude/skills/pv-version/scripts/init-version-folder.py --xxxx <XXXX>
```

Creates `{workFolder}/versions/{XXXX}/` with empty `files/` and `docs/` subfolders, and prints the created path. If `{workFolder}/versions/{XXXX}/` already exists, the script exits with an error without touching anything — in that case, ask the user whether they want to continue over what already exists (regenerate) or choose another `XXXX`, and return to this step with the new value if applicable.

## 3. Check `how-to-compile-version.md`

Look for `{workFolder}/stuff/how-to-compile-version.md` (the project's own file, not the skill's nor `pv-context.json`'s: it's a shell/build procedure, not declarative configuration).

- **If it doesn't exist**: ask the user for this project's exact procedure to generate the deliverable (which command(s) to run, where the resulting file ends up and how to identify it — or, if the process has several steps generating different artifacts, each step with its own command and resulting file), and write it following [`how-to-compile-version.template.md`](how-to-compile-version.template.md). Don't continue with step 4 in the same reply without having saved the file.
- **If it already exists**: read it and follow it as-is, without asking again.

## 4. Generate the version

Run the command(s) `how-to-compile-version.md` gives (one per step, if the procedure has several) and locate the resulting file(s) as it describes. If any command fails or the expected file doesn't show up, stop and explain it to the user instead of improvising an alternative solution.

With all artifacts located, copy them to `{workFolder}/versions/{XXXX}/files/` by running from the repo root (one `--source` per artifact, even if it comes from a single step):

```
python .claude/skills/pv-version/scripts/copy-build-artifacts.py --xxxx <XXXX> --source <artifact-path-1> [--source <artifact-path-2> ...]
```

### 4.1. Hook: "In the middle"

With the artifacts now in `{workFolder}/versions/{XXXX}/files/` and before step 5, if the custom pipeline (step 0.6) defines steps for the "In the middle" section, run them in order. `{XXXX}` and the `{workFolder}/versions/{XXXX}/` paths (`.../files/`, `.../docs/`) are available and substituted. Run each step's command(s) from the repo root and verify its output. If a step fails, **stop and explain it** — don't improvise an alternative. No steps for this section: continue silently.

## 5. Copy technical and functional documentation

Only if step 4 generated the deliverable correctly. Run from the repo root:

```
python .claude/skills/pv-version/scripts/copy-docs.py --xxxx <XXXX>
```

Reads `.claude/pv-context.json`'s `framework.docs.tech.architectureDocDir`, `framework.docs.tech.styleBibleDocDir` and `framework.docs.functional.featuresDocPathDir` (all three required and always configured), zips each one (the whole folder with all its files, including its `INDEX.md`; or the single `.md` file, if that path isn't a folder) and saves it at `{workFolder}/versions/{XXXX}/docs/`. If the script exits non-zero because a doc dir is missing from the config or points at a non-existent path, stop and tell the user to run `/pv-update` first — don't work around it. Note what was copied (the script returns this in its JSON `copied` list) for step 7's summary.

## 6. Generate the changelog

Invoke the `pv-internal-changelog` skill (Skill tool) passing it the destination folder `{workFolder}/versions/{XXXX}/`.

### 6.1. Hook: "At the end"

After the changelog is drafted and before the step 7 summary, if the custom pipeline (step 0.6) defines steps for the "At the end" section, run them in order. `{XXXX}` and the `{workFolder}/versions/{XXXX}/` paths are available and substituted. Run each step's command(s) from the repo root and verify its output. If a step fails, **stop and explain it** — don't improvise. This hook runs before the summary on purpose, so step 7 can report what it produced. No steps for this section: continue silently.

## 7. Confirm to the user

Summarize what was generated: the deliverable in `files/`, the three zipped docs in `docs/`, and that the changelog ended up in `changelog.md` — use the summary `pv-internal-changelog` returns to you (number of entries per section, including Fixes, and whether `{workFolder}/changes/closed/`'s folders were deleted or not). If the custom pipeline ran, also mention which sections executed and what they produced — especially "At the end" (e.g. "uploaded to X", "release notes in `notes.pdf`").
