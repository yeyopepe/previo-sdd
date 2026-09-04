---
name: pv-todo
description: Notes and develops loose ideas for later without putting them into the project's workflow — saves them at {changesDir}/todo/{code}/description.md, a separate folder no other pv-* skill uses or takes into account. Works for jotting down a new idea, continuing to develop/expand one already noted, and demoting an in-progress change into a noted idea (preserving everything it had). Trigger: /pv-todo [code] <idea>, /pv-todo change <xxxx> (or /pv-todo <xxxx>) to demote a change, or when the user asks to "note down"/"jot down" an idea for later, without asking for it to be documented as a change/fix.
argument-hint: "[code | change <xxxx>] <idea to note or develop>"
model: claude-haiku-4-5
effort: medium
metadata:
  version: 0.9.6b14
  uses: []
---

# pv-todo

The `pv-*` framework's idea notebook, but **outside** its workflow: it doesn't document a change/fix to implement, it just keeps a record of an idea to develop later, at a different pace from `pv-new`/`pv-fix`. There's no planning (`pv-how`/`pv-do`), no states (`inProgress`/`implemented`/`closed`), and no version: an idea noted here stays here until, if ever, someone decides to turn it into a real change/fix with `pv-new`/`pv-fix` (outside this skill already).

It also works the other way: an `inProgress` change/fix that's been deprioritized can be **demoted** here (`/pv-todo change <xxxx>`), keeping every file it had, so its analysis isn't lost while it waits — see [Demoting a change into a noted idea](#demoting-a-change-into-a-noted-idea).

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. `description.md` follows `framework.changes.language` (default `interaction.language`, English if neither is configured) — except the labels wrapped in `[[[...]]]` in `description.template.md` (the four markdown headings), which stay fixed in English always (see step 3, and the "Marker convention in templates" section of `pv-design.en.md`): write them without the brackets. If `language` is not configured anywhere, everything is English.

Lives at `{changesDir}/todo/`, a sibling subfolder to `inProgress`/`implemented`/`closed` but **entirely separate** from the rest of the framework: no other `pv-*` skill reads it, writes it, or counts its folders when numbering or looking up changes/fixes. The codes this skill uses have no relation to change/fix's numeric `xxxx` — they're just unique identifiers within `{changesDir}/todo/`. (The one crossover is the demote operation above, and it's one-way: this skill reads and deletes an `inProgress/{xxxx}/` folder, but the resulting idea still gets its own `pv-todo` code and stops counting for the workflow.)

## 0. Check that the framework is initialized

If `.claude/pv-context.json` doesn't exist at the repo root, or is missing the `framework` section, don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Additionally, before continuing, check that the framework's installed version is verified: read `metadata.version` from `.claude/skills/pv-init/SKILL.md`'s frontmatter (a handful of lines, not the whole file) and compare it against `framework.frameworkStatus.lastVerifiedVersion` in the `pv-context.json` you already loaded. If `frameworkStatus` is missing entirely, or `lastVerifiedVersion` doesn't match `pv-init/SKILL.md`'s real version, don't continue: tell the user the framework was updated (or has never been verified) and that they must run `pv-update` first — a stale `pv-context.json` can mean outdated templates, marker conventions, or other assumptions this skill relies on. Same stop if `framework.frameworkStatus.blocked` is already `true` (show `blockedReason` if present). This is a cheap, live comparison of two version strings already in hand — it doesn't require `pv-update` to have run before for the check itself to work, only for it to pass.

From here on, `changesDir` is shorthand for `{workFolder}/changes` (a fixed-name subfolder inside `framework.workFolder`, which defaults to `"/"`, the repo root).

## 1. Decide which of the four operations this is

Look at how the skill was invoked:

1. **Demote a change into a noted idea.** The user either wrote the literal keyword `change` followed by a code (`/pv-todo change 123`, `/pv-todo change 00123 ...`) **or** passed a single **purely numeric** argument with nothing else meaningful after it (`/pv-todo 123`) that does **not** match an existing `{changesDir}/todo/{arg}/` folder. Treat the number as a change/fix's numeric `xxxx` (`pv-todo` idea codes come from `[a-z0-9]`, so an all-digits one is possible but extremely unlikely — hence checking `todo/` first). Go to the [Demoting a change into a noted idea](#demoting-a-change-into-a-noted-idea) section.
2. **Expand an already-noted idea.** The user gave an idea code and `{changesDir}/todo/{code}/` exists **exactly** (this also covers the rare all-digits idea code). Go to the [Expanding an already-noted idea](#expanding-an-already-noted-idea) section.
3. **List noted ideas.** The user gave no content at all (e.g. "what ideas do I have noted", "list the todos"). Jump straight to [Listing noted ideas](#listing-noted-ideas) without creating or modifying anything.
4. **New idea.** Anything else (free-text idea, optionally with a not-yet-existing idea code). Continue to step 2.

If a numeric argument is given but you have real doubt about whether the user means a change code or something else, ask before doing anything — demoting a change deletes its workflow folder, so don't guess.

## 2. Generate a unique code

Generation and collision checking are handled deterministically and for free in tokens by the [`scripts/new-todo-code.py`](scripts/new-todo-code.py) script (standard Python, no external dependencies) — don't do it by hand. Run from the repo root:

```
python .claude/skills/pv-todo/scripts/new-todo-code.py
```

The script reads `workFolder` from `.claude/pv-context.json` (or uses `--work-folder` if you pass it), lists the subfolders already existing under `{changesDir}/todo/` (it doesn't need to exist yet — in that case there's nothing to collide with), generates a short alphanumeric code (`[a-z0-9]`, 5 characters by default, `--length` for a different size) that doesn't match any already there, and prints only that code on stdout. It doesn't check or take into account any other folder in the repo (not `inProgress`/`implemented`/`closed`, nor anything outside `{changesDir}/todo/`): the only uniqueness condition is not repeating within this subfolder. Use that value as-is for the code — don't recompute it by hand.

## 3. Note the idea

Without asking scope questions or proposing answers to functional gaps (that's what distinguishes this skill from `pv-new`/`pv-fix`: here the idea is noted as-is, even if incomplete or just a sketch), create:

```
{changesDir}/todo/{code}/description.md
```

**`description.md`** follows **exactly** the [`description.template.md`](description.template.md) template in this same folder: four markdown headings `## Idea`, `## Code`, `## Creation date` and `## Notes` (marked `[[[...]]]` in the template — write them without the brackets), in that order, without bold or a trailing `:` on the heading (neither `## Idea:` nor `**Idea:**`) — `pv-status`'s `list_todo.py`/`collect_status.py` parse these headings with a literal regular expression (`^##\s*Idea\s*\n+`) and any variation (bold heading, colon, a different title like "Ide", or a translated heading) makes the idea unreadable, showing up as "(no idea)" in `/pv-status todo`.

- **Idea** — short name summarizing the idea.
- **Code** — the code generated in step 2.
- **Creation date** — today's date (`YYYY-MM-DD` format) at the moment this `description.md` is created.
- **Notes** — the idea's content, as the user raised it. Can be a loose sentence, a list of possibilities, open unresolved questions, or any other form the user wants to note it in — don't force `pv-new`/`pv-fix`'s `description.md` structure onto it (there's no separate "Original prompt" or "Full description").

If the idea has a clear visual component and the user wants to record it, you can also create some `design_*.html`, same as `pv-new` does (self-contained mockup, no real functionality) — but it's not mandatory nor this skill's focus; only do it if the user asks or provides that material.

## 4. Confirm to the user

Report the assigned code and the created file's path, and remind them that this idea stays noted at `{changesDir}/todo/` outside the workflow — if it's ever turned into a real change/fix, it needs to be documented again with `pv-new`/`pv-fix` (this skill doesn't do that conversion automatically).

## Demoting a change into a noted idea

Triggered when step 1 reads the argument as a change/fix's numeric `xxxx` (`/pv-todo change 123` or `/pv-todo 123`). The goal: the change has been deprioritized, but nothing it accumulated (analysis, plan, prompt history, mockups, data tables…) should be lost — so its whole folder becomes a `pv-todo` idea and the change disappears from the workflow.

### D.1 Locate the change and validate its state

Normalize the given number to the project's `numberWidth` (the `framework.numberWidth` field in `.claude/pv-context.json`; zero-padded, same as the workflow uses — `123` → `00123` when `numberWidth` is 5) and look for that folder across **every** subtree of `{changesDir}` except `todo/`:

- **Only `{changesDir}/inProgress/{xxxx}/` is valid.** If it's there, continue to D.2.
- **If the folder exists but under any other state** (`implemented/`, `closed/`, or any other state folder that exists): stop. Tell the user the change can't be demoted because it's not `inProgress` (name the state it's actually in), and do nothing else.
- **If no folder with that number exists anywhere** under `{changesDir}` (again ignoring `todo/`): stop. Tell the user there's no change/fix with that code, and do nothing else.

Don't fall back to creating a new idea from a number that didn't resolve — a mistyped change code should fail loudly, not silently become a blank todo.

### D.2 Confirm with the user

Show the change's **Name** and **Type** (read from `{changesDir}/inProgress/{xxxx}/description.md`) and list the files the folder contains (`description.md`, `plan.md`, `history.md`, any `design_*`, `design_data_*`, etc.). State plainly what will happen: **all** of that content is copied into a new `pv-todo` idea and then `{changesDir}/inProgress/{xxxx}/` is deleted (the change leaves the workflow — no version, no changelog entry, it's as if it had never been opened, but its material is kept).

Ask for explicit confirmation. If the user doesn't confirm, stop and change nothing.

### D.3 Generate the idea code

Same as step 2: run [`scripts/new-todo-code.py`](scripts/new-todo-code.py) from the repo root and use the code it prints as `{code}`. This is a fresh `pv-todo` idea code with no relation to the change's `xxxx`.

### D.4 Copy every file across

Create `{changesDir}/todo/{code}/` and copy into it **every file** from `{changesDir}/inProgress/{xxxx}/`, contents unchanged, with two renames to avoid clobbering `pv-todo`'s own files and to keep `pv-status` parsing intact:

- the change's `description.md` → `original-change-description.md`
- the change's `history.md` (if present) → `original-change-history.md`

Everything else (`plan.md`, all `design_*` / `design_data_*` files, anything else that was there) keeps its original name.

### D.5 Write the idea's `description.md`

Create `{changesDir}/todo/{code}/description.md` following the [`description.template.md`](description.template.md) template exactly (same heading rules as step 3):

- **Idea** — the change's **Name**, verbatim.
- **Code** — the `{code}` from D.3.
- **Creation date** — today's date (`YYYY-MM-DD`).
- **Notes** — a short line stating this idea was demoted from change/fix `{xxxx}` (originally type `<type>`) on this date because it was deprioritized, then the **full functional description** copied verbatim from the change's `## Full description` section. After it, add a brief "Preserved material" list naming the other files now in this folder (`original-change-description.md` for the original entry with its Technical notes, `plan.md` for the technical plan if it was there, `original-change-history.md` for the prompt history, the `design_*` files, etc.) so whoever picks this up later knows the analysis wasn't thrown away.

### D.6 Delete the change

Delete the `{changesDir}/inProgress/{xxxx}/` folder entirely. Do **not** call `pv-internal-workflow` for this — that skill only moves between `inProgress`/`implemented`, and a demotion isn't a workflow transition. A plain recursive delete of that one folder is correct here.

### D.7 Confirm to the user

Report: the change/fix `{xxxx}` was removed from `{changesDir}/inProgress/` and its full content is now noted as idea `{code}` at `{changesDir}/todo/{code}/`. Remind them that, like any `pv-todo` idea, it's outside the workflow now — reviving it means documenting it again with `pv-new`/`pv-fix` (the preserved `plan.md` / `original-change-description.md` can be reused as input, but this skill doesn't convert it back automatically).

## Expanding an already-noted idea

When step 1 detects that the given code already exists at `{changesDir}/todo/{code}/`:

1. Open `{changesDir}/todo/{code}/description.md` to see what's already noted.
2. Add the new content to the **Notes** section, leaving what's there as-is (don't delete or rewrite it) and appending the new content after it — like a notebook you keep writing in, not a document rewritten each time.
3. Confirm to the user that idea `{code}` has been updated.

## Listing noted ideas

If the user asks to see what ideas are noted: list `{changesDir}/todo/`'s subfolders and, for each one, its code and its `description.md`'s **Idea** field. If the folder doesn't exist or is empty, say so — there are no ideas noted yet.

## What this skill does NOT do

- It doesn't plan or implement anything (there's no `pv-how`/`pv-do` equivalent here).
- It doesn't move ideas between states or "close" them — there's no flow for that; if an idea stops being interesting, it's up to the user to delete it or leave it as-is.
- It doesn't number with the framework's `xxxx` nor invoke `pv-internal-workflow` — its numbering is independent and local to `{changesDir}/todo/`. (Demoting a change deletes its `inProgress/{xxxx}/` folder with a plain recursive delete, not through `pv-internal-workflow`, which only handles `inProgress`↔`implemented` moves.)
- It doesn't count as a source of intent for `pv-how`, `pv-do`, or any other framework skill: `{changesDir}/todo/` is `pv-todo`'s exclusive territory.
- Demoting a change is **not** the reverse of `pv-new`/`pv-fix`: it doesn't produce a workflow entry and it can't turn an idea back into a change — reviving a demoted idea still goes through `pv-new`/`pv-fix` from scratch (reusing the preserved files as input).
