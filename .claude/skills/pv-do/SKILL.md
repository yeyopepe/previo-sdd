---
name: pv-do
description: Implements a change/fix whose plan.md is already written at {changesDir}/inProgress/{xxxx}/ — edits the code per the technical solution, updates the synced documentation, and moves the entry to {changesDir}/implemented. Part of the pv-* framework. Trigger: /pv-do <xxxx>, or when the user asks to implement a change/fix already planned by pv-how (normally chained automatically from it).
argument-hint: <xxxx of the already-planned change/fix>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b11
  uses: [pv-internal-workflow, pv-internal-doc-features, pv-internal-doc-files, pv-internal-doc-technical, pv-internal-doc-style]
---

# pv-do

Takes an entry from `{changesDir}/inProgress/{xxxx}/` whose technical solution is already written in `plan.md` (by the `pv-how` skill) and carries it through to implemented: edits the code, updates the synced documentation, and moves the folder to `{changesDir}/implemented/{xxxx}/`.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. `docs.functional.featuresDocPathDir` (when a folder) follows `docs.functional.language`, but drafting it in that language is `pv-internal-doc-features`'s responsibility, not yours — you only tell it which language via context. Always write `docs.tech.architectureDocDir`/`styleBibleDocDir` in technical English — there is no `docs.tech.language`. The source (`plan.md`) may be in `changes.language`; translating to English when writing the reference document is your responsibility. In the legacy single-file case (step 2.1) where you write `FEATURES.template.md` yourself, the same applies — draft fresh in `docs.functional.language`, and the labels wrapped in `[[[...]]]` there (`Available in`, `Code`) stay fixed in English always — write them without the brackets (see the "Marker convention in templates" section of `pv-design.en.md`); `migrate-legacy-features-doc.py` parses `**Available in**` literally when the project later migrates to a folder. If `language` is not configured anywhere, everything is English.

**Source of truth.** This entry's `plan.md` is the guide for what to implement. If during implementation something doesn't line up with the real code, the code rules — stop and tell the user instead of improvising a different solution without telling them (see step 2). If the entry has a `history.md`, don't open it: it's prompt history for the exclusive use of `pv-new`/`pv-fix`, never information to take into account when implementing or documenting (step 2.1), and reading it would only spend context without adding anything.

**Never use git destructively nor commit without permission.** This skill edits code/documentation files and moves the change's folder (step 3), but never goes further on its own:

- Don't run `git commit` (nor `git add` followed by commit) unless the user explicitly asked for it in this turn. Finishing the implementation is not implicit authorization to commit.
- Don't run `git restore`, `git checkout -- <file>`, `git reset`, `git clean`, or any other command that discards changes in the working tree, even if the affected file seems unrelated to this entry. If running `git status`/`git add` shows changes from other work in progress (yours or the user's) that you don't want to include, say so and ask how to proceed — don't discard them yourself.
- If you need to check the repo's state (`git status`, `git diff`), do it only to verify your own work, never as a step before cleaning up or discarding files you haven't touched in this implementation.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Additionally, before continuing, check that the framework's installed version is verified: read `metadata.version` from `.claude/skills/pv-init/SKILL.md`'s frontmatter (a handful of lines, not the whole file) and compare it against `framework.frameworkStatus.lastVerifiedVersion` in the `pv-context.json` you already loaded. If `frameworkStatus` is missing entirely, or `lastVerifiedVersion` doesn't match `pv-init/SKILL.md`'s real version, don't continue: tell the user the framework was updated (or has never been verified) and that they must run `pv-update` first — a stale `pv-context.json` can mean outdated templates, marker conventions, or other assumptions this skill relies on. Same stop if `framework.frameworkStatus.blocked` is already `true` (show `blockedReason` if present). This is a cheap, live comparison of two version strings already in hand — it doesn't require `pv-update` to have run before for the check itself to work, only for it to pass.

`docs.tech.architectureDocDir`, `docs.functional.featuresDocPathDir` and `docs.tech.styleBibleDocDir` are always configured (`pv-init` writes and scaffolds all three; `schema.json` marks them required). They're used in step 2.1, where you resolve each via `resolve-path.py` (no skill parses `pv-context.json`'s path fields directly — see `pv-design.en.md`'s "Resolving paths"). If any resolution fails there, don't continue past step 2.1: tell the user the framework config is broken and they must run `/pv-update` first, then stop. A doc folder that resolves fine but only holds its placeholder `INDEX.md` (no `{NNN}-*.md` yet) is **not** a broken state — proceed normally, that's just documentation not populated yet.

## 1. Identify the entry to implement

If the user, when invoking this skill, gives an `xxxx`, a folder name, or a description of the change/fix, resolve it by searching **only** within `{changesDir}/inProgress/`, and check that it has `plan.md`:

- If the folder exists but does **not** have `plan.md` yet: don't continue. Tell the user that entry doesn't have a planned technical solution yet and that `pv-how` must be invoked on that `xxxx` first.
- If you don't find a matching folder within `{changesDir}/inProgress/`: if it exists with that `xxxx` under `{changesDir}/implemented/`, tell the user that change/fix is already implemented; if it doesn't exist anywhere, tell them you can't find it and ask for the correct `xxxx` or folder.

**If they give nothing** (e.g. they invoke `/pv-do` with no arguments): don't assume it refers to the last change/fix mentioned in the conversation nor any other piece of chat context. List only the `{changesDir}/inProgress/` folders that already have `plan.md` (ready to implement) — their `xxxx` and, if it has one, its `description.md`'s name/summary — and explicitly ask the user which one they want to implement. If none has `plan.md` yet (even if there are unplanned entries in `inProgress`), tell them there's no change/fix ready to implement and that it needs to be planned with `pv-how` first.

```
These changes/fixes already have `plan.md` and are ready to implement:
- {xxxx} — {name/summary}
- ...

Which one do you want me to implement?
```

```
There's no change/fix with `plan.md` ready to implement. Use `pv-how` first to plan one of the pending ones in `{changesDir}/inProgress/`.
```

Once identified, that's `{xxxx}` and its folder `{changesDir}/inProgress/{xxxx}/` for the rest of the process.

## 2. Implement

Implement everything `plan.md` says. Its checklists (`(b)` and, if present, `(e)`) are the only reliable task list — don't trust what you remember from reading them earlier, go box by box:

- Go through section **(b) Technical solution** **one task at a time, in order**: implement that specific task (edit code, verify it compiles / tests pass if there are any) and, right after considering it done, edit `plan.md` marking that box as `- [x]` before moving to the next. Don't implement several tasks in a row and mark them all at the end — marking immediately is what avoids skipping one without noticing.
- If `plan.md` has section **(c) Architecture changes**, apply those changes to the `docs.tech.architectureDocDir` file(s) that section names, as part of this implementation.
- If `plan.md` has section **(e) Verification**, once every box in (b) is checked, go through each item in (e) **one at a time** and verify the described observable result truly holds (by reading the resulting code/DOM/styles, not assuming the (b) task that produces it went fine). Check its box `- [x]` only once you've verified it this way. If an item doesn't hold, fix it before checking it off — don't consider it done nor mention it to the user as pending.
- **Before moving to step 3**, reread the entire `plan.md` looking for unchecked `- [ ]` boxes in (b) or (e). If you find any, that task or check was left pending without you noticing: complete it now, don't ignore it or treat it as implicit.

If during implementation you discover the plan isn't viable as written, stop and tell the user instead of improvising a different solution without telling them.

## 2.1 Update documentation after implementing

Once the above is implemented in code, always update the following before moving the folder:

All three doc dirs are always configured. Before touching any of them, get each one's absolute path from `resolve-path.py` (see `pv-design.en.md`'s "Resolving paths"):

```
python .claude/skills/pv-init/scripts/resolve-path.py --what architectureDocDir
python .claude/skills/pv-init/scripts/resolve-path.py --what styleBibleDocDir
python .claude/skills/pv-init/scripts/resolve-path.py --what featuresDocPathDir
```

If any exits non-zero, stop here and send the user to `/pv-update` (see step 0) — don't implement the doc updates halfway. A folder that resolves fine but holds only its placeholder `INDEX.md` is fine; treat it as "nothing documented yet for the touched area" and add the first entry. (`featuresDocPathDir` may be a single `.md` file rather than a folder in unmigrated projects — `resolve-path.py` still resolves it; the folder-vs-file handling stays as described below.)

Below, wherever a sub-step passes `folder=architectureDocDir` / `folder=styleBibleDocDir` / `folder=featuresDocPathDir` to `pv-internal-doc-files`/`pv-internal-doc-features`, pass the **absolute path `resolve-path.py` just returned** for that key, not the literal key name.

- **`docs.tech.styleBibleDocDir` writing style baseline.** Before drafting or editing its content, invoke `pv-internal-doc-technical` (Skill tool, no parameters) to load its shared writing rules — see the `styleBibleDocDir` point below, which invokes `pv-internal-doc-style` for the content checklist and style-specific writing additions on top of this baseline. (For `architectureDocDir`, this invocation is folded into the next point instead, since `pv-internal-doc-technical` now also returns that field's content checklist.)
- **`docs.tech.architectureDocDir`** — first invoke `pv-internal-doc-files` (Skill tool) with `action=find`, `folder=architectureDocDir`, and a brief description of the touched topic, to know whether a file already covers it. Then invoke `pv-internal-doc-technical` (Skill tool) with a summary of what was implemented, the context already gathered (touched code, `plan.md`), and the existing `architectureDocDir` file(s) `find` returned for the touched area. It returns which content categories apply (components, contracts, data flows, decisions, dependencies, data model, configuration), which are already covered versus pending to document, and the writing rules to apply — these documents are read by AI (`pv-internal-tech-analysis`, future `pv-do`/`pv-how` cycles), not by a human, so they favor dense fact fragments over explanatory prose. For every category it reports as pending, review the existing file (if any) and make sure it faithfully reflects the resulting technical state; apply whatever section (c) of the plan says if it had one, or update it anyway if implementation turned out to touch something that folder describes even without the plan anticipating it. Draft the final `body` yourself (per the returned writing rules) and save it by invoking `pv-internal-doc-files` with `action=upsert`, `folder=architectureDocDir`, `area` (the technical topic this file groups under), `title`, `body`, and `existing_file` if `find` returned a match. **Write it in technical English**, never in `changes.language` — draft fresh in English, don't carry over `plan.md` sentences verbatim.
  - **Namespace upkeep.** If this change adds or renames a citable concept or assertion, update `{architectureDocDir}/00-namespace.md` (new path, or a moved `anchor:`); if a code symbol was renamed, update its `anchor:` line. Edit `00-namespace.md` with **Read/Edit directly — never via `pv-internal-doc-files`'s `upsert`** (the `00-` prefix is reserved infrastructure, excluded from `INDEX.md` and the `{NNN}` numbering; `upsert` is only for topic files). A renamed-away anchor whose new symbol you can't determine is left for `pv-update` to flag — don't guess it.
- **`docs.functional.featuresDocPathDir`** — it's **functional** documentation, not a changelog: it describes what the app can do today, organized by functional area/module, not a chronological list of changes/fixes. **Write it in `docs.functional.language`** (fallback `interaction.language`), never in `changes.language`.
  - **If `featuresDocPathDir` is a folder** (the recommended convention — `resolve-path.py` returned a directory, or the configured value doesn't end in `.md`): invoke the `pv-internal-doc-features` skill (Skill tool) with `action=find`, the resolved `featuresDocPathDir` path, and a brief description of the implemented feature, to know whether it already has its own file. Then invoke it with `action=upsert`, passing the resolved `featuresDocPathDir` path, `area`, `title`, a `summary` of what was implemented and where it's used, and the context already gathered (touched code, `plan.md`, this entry's functional Mermaid diagram if `description.md` has one, and any `design_navigation_*.md` files) plus `existing_file` if `find` returned a match. `pv-internal-doc-features` decides what the entry says and how it's written (in-place edit vs. new entry, which diagrams carry over, wording) — you only supply the summary and context, you don't draft the content yourself.
  - **If `featuresDocPathDir` is a single file** (projects that haven't migrated to a folder yet — `resolve-path.py` returned a path ending in `.md`): edit it yourself. If what was implemented extends or modifies a feature that already has its own entry, edit it in place so it keeps faithfully describing the current behavior (never add a new entry for the same thing), adding this entry's `xxxx` to its **Code** field; if it's a new feature, create an entry in the matching functional area (create the area if it doesn't exist yet) with this entry's `xxxx` in **Code**, using this skill's [`FEATURES.template.md`](FEATURES.template.md) as the template; create the file from that template if it doesn't exist yet. Carry over functional diagrams the same way described above for the folder case (as-is, joint-or-none rule for cross-referencing diagrams, never technical diagrams). Draft the body fresh in `docs.functional.language` rather than copying phrasing straight from `description.md`/`plan.md`.
- **`docs.tech.styleBibleDocDir`** — invoke `pv-internal-doc-style` (Skill tool) with a summary of what was implemented, the context already gathered (touched code, `plan.md`, any `design_*` mockups this entry has, whether the project has a presentation layer — web/desktop/mobile/CLI all count, see that skill for the full criterion), and the existing `styleBibleDocDir` file(s) matching the touched area (find them the same way as `architectureDocDir` above, via `pv-internal-doc-files`'s `action=find` with `folder=styleBibleDocDir`). It returns which style categories apply, what each must record, which are already covered versus pending to document, and the writing rules to apply on top of `pv-internal-doc-technical`'s baseline. For every category it reports as pending, draft the `body` yourself and save it via `pv-internal-doc-files`'s `action=upsert` (`folder=styleBibleDocDir`, `area`, `title`, `body`, `existing_file` if applicable) — same mechanics as `architectureDocDir` above, one file per category/topic that doesn't fit an existing one. If `pv-internal-doc-style` reports nothing pending (e.g. the project has no presentation layer), skip without asking anything — the folder legitimately stays at just its placeholder. **Write it in technical English**, same rule as `architectureDocDir` above. Style concepts that become citable go on the `ui.*` branch of `{architectureDocDir}/00-namespace.md` (Read/Edit directly, same as above) — `styleBibleDocDir` has no namespace file of its own.

## 3. Move the folder to `implemented`

Invoke the `pv-internal-workflow` skill (Skill tool) with `action=move`, `xxxx`, `from=inProgress` and `to=implemented` — don't move the folder yourself.

## 4. Confirm to the user

State what was implemented, which documentation was updated (`docs.tech.architectureDocDir`/`docs.functional.featuresDocPathDir`/`docs.tech.styleBibleDocDir`, whichever the change actually touched), and that the folder was moved to `{changesDir}/implemented/{xxxx}/`.
