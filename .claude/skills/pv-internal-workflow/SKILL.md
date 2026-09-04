---
name: pv-internal-workflow
description: Shared, project-agnostic process with two internal pv-* framework actions — (1) create a new entry under {changesDir}/inProgress documenting the intent of a fix or change, and (2) move an existing entry between workflow substates (inProgress/implemented) when another framework skill produces that transition. Internal use by the pv-new, pv-fix and pv-do skills.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b11
  uses: []
---

# pv-internal-workflow

Generic process and single point where the `pv-*` framework knows how to create and move `{changesDir}` folders. Only invoked by other framework skills — not meant for direct invocation by the user.

**Language.** Use `framework.interaction.language` (default English) for the guardrail message to the user in the section below. `description.md`/`history.md` (action `create`) follow `framework.changes.language` (default `interaction.language`, English if neither is configured) — except everything wrapped in `[[[...]]]` in `description.template.md`, which stays fixed in English always (see the "Marker convention in templates" section of `pv-design.en.md`): that's the four field labels (**Name**, **Code**, **Type**, **Creation date**) *and* the `## Full description` section heading. Write them without the brackets, exactly as they appear once unwrapped — heading form included, never a translation. The `## Technical notes` heading is **not** marked (it's optional — omitted entirely when there's nothing technical to note, which a marker check can't tell apart from a translation); still write it in English for consistency, but it carries no marker. `pv-status`'s `filter_status.py` parses `## Full description` literally (`extract_description`) for the status report; translating that heading makes the entry's summary show up empty there, silently. If `language` is not configured anywhere, everything is English.

It has two independent actions, each invoked with an `action` parameter:

- **`action=create`** — invoked by `pv-new` and `pv-fix`, with `type` (`change`/`fix`/`fast`), the description of what's being asked, and the user's original prompt verbatim (`promptOriginal`). Sizes the functional scope and creates the entry under `{changesDir}/inProgress/`, with `description.md` (current information) and `history.md` (prompt history, see below) as separate files. For `type=fast` (a `pv-fix` shortcut for trivial changes), the caller typically chains an `action=move` to `implemented` in the same invocation, without going through `plan.md`.
- **`action=move`** — invoked by `pv-do`, with `xxxx`, `from` and `to` (subfolder names under `{changesDir}`: `inProgress` or `implemented`). Moves the `{xxxx}` folder between those substates.

Neither action implements or technically analyzes anything, nor decides **whether** the transition should happen or needs user confirmation — the calling skill has already resolved that before invoking `pv-internal-workflow`. This skill only executes the file mechanics (numbering+creating, or moving) consistently in a single place.

Beyond those two actions, this skill also **owns the `.metadata.json` contract** for a change/fix folder and the [`scripts/set-metadata.py`](scripts/set-metadata.py) script that is the single writer of it — see "The `.metadata.json` contract" below. `pv-status` reads it, `pv-update` audits it, `pv.py` toggles flags through `set-metadata.py`; none of them write the file directly.

## Invocation guardrail — read before anything else

This skill **does not run if invoked directly** (e.g. the user typed `/pv-internal-workflow`, or asked in plain text to "run/invoke pv-internal-workflow"). It should only run when the content of `pv-new`, `pv-fix` or `pv-do` itself has instructed you to invoke it as part of its process, with the `action` and corresponding parameters already resolved by that skill.

If you were invoked without that context (the user typed the command directly, or you didn't come from one of those three skills), **stop here** and tell the user that `pv-internal-workflow` is for internal framework use: to document or implement a change/fix they should use the corresponding skill. Do nothing else in that case.

```
`/pv-internal-workflow` is for internal use by the `pv-*` framework and isn't invoked directly. To document a change/fix use `pv-new`/`pv-fix`, and to implement it `/pv-how`/`/pv-do`.
```

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section (or fields this action needs), don't continue: tell the user they must first run the `pv-init` skill to initialize/complete the framework in this project, and stop there — don't reimplement the bootstrap here. The full schema is at [`../pv-init/schema.json`](../pv-init/schema.json) (read it first if you haven't already this session, to know which fields to check).

From here on, `changesDir` is shorthand for `{workFolder}/changes` (a fixed-name subfolder inside `framework.workFolder`, which defaults to `"/"`, the repo root — not its own field in `pv-context.json`), and `numberWidth` refers to that field's value under `framework` in that file.

Continue with whichever section below matches the received `action`.

**Documentation format:** when writing `description.md` (action `create`), if the caller passed you one or more already-generated Mermaid diagrams (obtained from the skill configured in `framework.skills.diagrams`, see `pv-new`/`pv-fix`), insert them along with the essential notes at the corresponding point, instead of repeating in prose what the diagram already makes clear. This skill doesn't generate diagrams itself nor decide whether they're needed — the caller already resolved that before calling you.

## Action `create`

### create.1 Compute the change code `xxxx`

Every change/fix lives in a numbered subfolder under one of `{changesDir}`'s subtrees (`inProgress/`, `implemented/`, or any other that exists): the same `xxxx` cannot repeat in any of them. The exception is `{changesDir}/todo/`, used by the `pv-todo` skill for loose ideas outside this flow: its folders never count here, even if they had a numeric name. To compute it without errors, run the [`scripts/next-change-number.py`](scripts/next-change-number.py) script (requires Python 3) from the repo root:

```
python .claude/skills/pv-internal-workflow/scripts/next-change-number.py
```

The script reads `workFolder` and `numberWidth` from `.claude/pv-context.json`, walks **all** subfolders of `{changesDir}` (not just `inProgress`/`implemented`, but always ignoring `todo/`) looking for purely numeric names, and prints on stdout the next `xxxx` already formatted with `numberWidth` digits and leading zeros (e.g. `0002`, or `1` if there's no numbered folder yet). Use that value as-is for `xxxx` — don't recompute it by hand nor look only at `inProgress`/`implemented`.

### create.2 Generate the change/fix intent document

If there are relevant doubts about the scope of what's being asked that can't be resolved with what you already know, ask them before writing the document — they don't need to be technical implementation doubts (that's `pv-how`'s job later), just functional scope ones. Keep those questions along with the user's answers: they go into the document (see below).

Create (creating `{changesDir}/inProgress/` if it doesn't exist) two separate files:

```
{changesDir}/inProgress/{xxxx}/description.md
{changesDir}/inProgress/{xxxx}/history.md
```

**`description.md`** follows exactly the [`description.template.md`](description.template.md) template in this same folder, with these rules per section:

- **Name** — short, descriptive name for the change/fix.
- **Code** — the `xxxx` computed in the previous step.
- **Type** — `fix`, `change` or `fast`, as applicable.
- **Creation date** — today's date (`YYYY-MM-DD` format) at the moment this `description.md` is created.
- **Full description** — functional summary of what's been analyzed as requested, understandable by anyone non-technical, without going into technical solution or mentioning files, functions, classes or data structures:
  - For a `fix`: what behavior is broken, how to reproduce or identify it, and what should happen instead.
  - For a `change`: what's being asked to add or modify, why, and how the result should behave.
  - Also include here, if there were any, the scope questions asked of the user along with their answers.
- **Technical notes** — any technical detail seen during analysis (files, functions, classes, existing code patterns relevant to this entry, detected technical constraints) worth noting for when `pv-how` designs the solution. Optional section: if the functional analysis didn't touch code or find anything technically relevant, omit it entirely instead of leaving it empty.

This separation is strict: any mention of files, functions, CSS classes or other implementation details always goes in **Technical notes**, never in **Full description**, even if it came up naturally during analysis. The in-depth technical analysis and the solution itself are still `plan.md`'s job, generated by `pv-how`.

**`history.md`** follows exactly the [`history.template.md`](history.template.md) template: a single `## {today's date} — initial session` heading followed by the received `promptOriginal`, verbatim, without rephrasing. It's historical information, for the exclusive use of `pv-new`/`pv-fix` (see the template itself) — never mix its content into `description.md`.

### create.3 Confirm to the caller

Report the created files (`{changesDir}/inProgress/{xxxx}/description.md` and `.../history.md`) and the resolved `xxxx`, so the calling skill (`pv-new`/`pv-fix`) can continue its own process.

## Action `move`

Received with `xxxx`, `from` and `to` already resolved by the caller (`pv-do`: `inProgress`→`implemented`).

The file mechanics (check source, create destination if missing, move) are done deterministically and for free in tokens by the [`scripts/move-change.py`](scripts/move-change.py) script (standard Python, no external dependencies) — don't reimplement it by hand. Run from the repo root:

```
python .claude/skills/pv-internal-workflow/scripts/move-change.py --xxxx <xxxx> --from <from> --to <to>
```

- If `{changesDir}/{from}/{xxxx}/` doesn't exist, or something already exists at `{changesDir}/{to}/{xxxx}/`, the script exits with an error and moves nothing — this is an error on the caller's part (that skill should have already identified and verified the folder before calling `pv-internal-workflow`). Report it back to the caller as-is, without improvising a fix.
- If it succeeds, the script prints the destination path on stdout, relative to the repo root (e.g. `changes/implemented/0002`).

Confirm that destination path to the caller, so the calling skill can continue its own process (message to the user, next steps like generating a version or updating the graph, etc. — that's handled by it, not `pv-internal-workflow`).

## The `.metadata.json` contract

Every change/fix folder under `{changesDir}/` *may* carry a dotfile `.metadata.json` next to `description.md` / `plan.md` / `history.md`, holding **mutable per-change state** — state that changes without re-documenting the change. Today that's the change's **flags**. Its shape is defined by [`metadata.schema.json`](metadata.schema.json) in this skill's folder (referenced by `pv-status` when reading it and by `pv-update` when auditing it):

```json
{
  "flags": ["priority", "workinprogress"],
  "flagsLastModified": "2026-09-03"
}
```

- **`flags`** — array of strings, no duplicates. Valid values are the `metadata.schema.json` enum, today `"priority"` (⭐, marked as a priority) and `"workinprogress"` (⚙️, actively being worked on right now). A change can have 0, 1 or several. Order in the array isn't significant — consumers paint them in a fixed order (⭐ before ⚙️). **Adding a future flag** = one value in the schema enum + its icon/label entry in `pv-status`'s `FLAG_*` maps; nothing else changes.
- **`flagsLastModified`** — ISO date (`YYYY-MM-DD`), optional. A single global timestamp for the last add/remove of any flag. Written on every effective mutation; no consumer reads it yet (reserved for future use).
- **`risk`** is declared in `metadata.schema.json` but **not written by this flow** — it's the hook for a later plan that moves `risk` out of `plan.md`'s header. `set-metadata.py` preserves it untouched if another writer added it.

**Rules:**

- **No file = `flags: []`.** A missing `.metadata.json`, a missing `flags` field, or `flags: []` all mean "no flags". The file only appears once a change gets its first flag. Existing folders need **no migration**.
- **`todo/` entries NEVER carry `.metadata.json`.** A todo is a loose idea outside the flow — nothing to mark as prioritised or in progress. `set-metadata.py` rejects any operation that resolves under `todo/`; `pv-update` reports a `.metadata.json` that appears there.
- **The code, the workflow state, `type` and `name` do NOT go in this file** — the code is the folder name, the state is the parent folder, `type`/`name` come from `description.md`.
- **`move-change.py` carries it automatically** — it does `shutil.move()` on the whole directory, so `.metadata.json` travels with the folder on every `inProgress → implemented → closed` move. No code change was needed there. Any *future* recursive copy of a change folder must include dotfiles.
- **`.metadata.json` is versioned by `git`** like any other file in the folder. Make sure a `workFolder` `.gitignore` doesn't exclude it (a dotfile can be caught by `*` + `!*.md`).

### `set-metadata.py` — the single writer

[`scripts/set-metadata.py`](scripts/set-metadata.py) (standard Python, no dependencies) is the only thing that writes `.metadata.json`. Run from the repo root:

```
python .claude/skills/pv-internal-workflow/scripts/set-metadata.py --xxxx <code> --toggle-flag <name>
```

- **`--xxxx <code>`** + state resolution: the script searches every state folder under `changes/` (skipping `todo/`) for `<code>`. Pass **`--state <state>`** to target one directly. Ambiguous (`<code>` in more than one state) → error, pass `--state`.
- **Flag ops (repeatable):** `--add-flag <name>`, `--remove-flag <name>`, `--toggle-flag <name>`. `<name>` is validated against the schema enum — a clear error otherwise. An op that changes nothing (adding a set flag, removing an unset one) is reported as a no-op and writes nothing new.
- **`--work-folder <path>`** override (same pattern as `move-change.py`) so `pv.py --testconfig` can point it at fixtures.
- **`--print`** also emits the resulting `.metadata.json` as JSON on stdout after the confirmation line, so callers don't re-read it.
- Rejects any operation resolving under `todo/`. Takes an **exclusive file lock** on an adjacent `.metadata.json.lock` for the read-modify-write cycle, so a toggle from `pv.py` and one from a Claude Code session in parallel don't clobber each other. Creates `.metadata.json` if absent; **never deletes it** (even when `flags` becomes `[]`). Preserves unknown fields (e.g. a future `risk`). Refreshes `flagsLastModified` to today on every effective mutation.
- Output: one plain-text confirmation line (no ANSI), like `delete-todo.py`.
