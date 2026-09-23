---
name: pv-review-architecture
description: Analyzes the project's real source code architecture (`framework.sourcecodeDir`) against a fixed checklist of language-agnostic software design principles (separation of concerns, file/class size, SOLID, KISS, DRY, coupling/cohesion, naming, layering) and produces a numbered list of reorganization proposals — pure structural moves (splitting/merging/relocating/renaming files or classes), never adding or removing functional code. For each proposal the user confirms, asks whether to turn it into a noted idea (`pv-todo`) or directly into a documented change (`pv-new`) and creates it accordingly. Trigger: /pv-review-architecture, or when the user asks to review/audit the project's architecture or code organization.
model: claude-sonnet-5
effort: high
metadata:
  author: Sergio José Martínez Primiani
  version: 0.9.8b6
  uses: [pv-todo, pv-new]
---

# pv-review-architecture

Reviews the project's **code architecture** — how responsibilities are split across files/classes/modules, not the functional behavior of the code and not `docs.tech` (that's `pv-review-doc-tech`'s job). Produces a numbered list of concrete, scoped **reorganization proposals**: moving/splitting/merging/renaming/relocating code so responsibilities land where they belong. It never proposes (and, downstream, `pv-todo`/`pv-new` must never be asked to implement) adding new functionality, removing functionality, or changing behavior — every proposal must be achievable by moving existing code around, unchanged in what it does.

**Language.** Use `framework.interaction.language` (default English) for everything said to the user in this conversation.

**This skill edits nothing itself.** It only reads code and writes nothing to `{sourcecodeDir}`. Its only writes, if the user asks for them, are through `pv-todo`/`pv-new` (steps 4-5) — never a direct code edit, never a direct `changes/**` write of its own.

**Before any other step**, read [`workflow.review-architecture.md`](workflow.review-architecture.md) — it's the source of truth for this flow's sequence and branches (see `pv-design.en.md`'s "Workflow diagrams" section for the notation). If it doesn't exist or can't be followed, stop and report that instead of improvising the flow from the prose below. The numbered steps that follow are each node's detail (what exact text to use, which checklist to apply) — the diagram governs sequence and branching; if the two ever disagree, the diagram wins and this prose gets corrected to match.

## 0. Check that the framework is initialized

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, stop and tell the user to run `pv-init` first.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Check the framework version the same way every other `pv-*` skill does: compare `metadata.version` in `.claude/skills/pv-init/SKILL.md`'s frontmatter against `framework.frameworkStatus.lastVerifiedVersion`. If they don't match, or `frameworkStatus` is missing, or `framework.frameworkStatus.blocked` is `true`, stop and send the user to `/pv-update`.

Resolve the source folder to review:

```
python .claude/skills/pv-init/scripts/resolve-path.py --what sourcecodeDir
```

If resolution fails, stop and send the user to `/pv-update` — don't guess a folder.

## 1. Read the codebase before judging anything

Read the whole resolved source tree structurally before forming any opinion — file/folder layout first (so you see the project's real module boundaries, not an assumed convention), then the content of each file. For a large codebase, prioritize breadth (every file's size, name, and top-level responsibilities) over depth (reading every line of every file); go deep only into files/areas that step 2's checklist flags as suspect (very long files, files mixing unrelated concerns, folders with unclear boundaries).

Don't read `changes/**`, `docs/**`, or any other `pv-*` workflow folder as input here — this review judges the **real code as it stands today**, not what any change/fix or documentation says about it. If documentation and code disagree, that's out of this skill's scope (flag it in passing if you notice it, but don't chase it — `pv-review-doc-tech`/`pv-internal-tech-analysis` own that concern).

## 2. Checklist — what to look for

Apply these checks across the whole codebase, project-agnostic (language/framework-independent). Each is a **lens for finding candidate reorganizations**, not a rule to report violations of in the abstract — every finding must resolve to a concrete "move/split/merge/rename X" proposal, not a generic observation.

- **Separation of concerns / cohesion.** A file or class mixing unrelated responsibilities (e.g. data access + business rules + presentation formatting in one place) — candidate to split along those seams.
- **Single Responsibility (SRP).** A class/module with more than one reason to change (touched for unrelated purposes across the project's real change history/naming) — candidate to split by responsibility.
- **File/class size and length.** Files or classes conspicuously larger than their siblings in the same layer, or that read as "doing everything" — candidate to break into smaller, named units. Judge relative to the codebase's own norm, not a fixed line-count threshold picked in isolation.
- **Open/Closed.** Logic that branches repeatedly on type/kind (long if/switch chains over a discriminator) where the codebase already has a polymorphism/strategy seam it isn't using — candidate to relocate the branch's cases to where that seam already lives.
- **Liskov substitution.** A subtype/implementation that special-cases or contradicts its supertype/interface's contract — flag as a design smell; propose only the structural fix (e.g. relocate the special-cased behavior out of the hierarchy), not a behavior change.
- **Interface segregation.** A single wide interface/module that different callers use only slivers of — candidate to split into smaller, caller-specific interfaces/modules.
- **Dependency inversion.** High-level logic directly coupled to a low-level/concrete detail that the codebase already abstracts elsewhere (a pattern already used in sibling code, just not here) — candidate to relocate/realign to the existing abstraction seam.
- **DRY — duplicated logic.** The same logic (not just similar-looking code) repeated across files instead of shared — candidate to consolidate into one place and have callers reference it. (Where consolidating would require writing new shared code rather than moving what already exists verbatim, it's out of this skill's reorg-only scope — say so instead of proposing it.)
- **KISS — accidental complexity.** Structure more layered/indirect than the responsibility needs (e.g. a pass-through wrapper doing nothing, an abstraction with exactly one implementation and no foreseeable second one) — candidate to flatten/relocate, never to redesign.
- **Coupling and layering.** Violations of the project's own layering convention (e.g. a UI file importing directly from a data-access layer, skipping the domain/service layer the rest of the codebase goes through) — candidate to relocate the call through the existing layer.
- **Folder/module structure vs. responsibility.** Files whose folder placement doesn't match what they actually do (e.g. a utility used by one feature sitting in a shared "utils" catch-all instead of that feature's own folder, or the reverse — something genuinely shared stranded inside one feature's folder) — candidate to relocate.
- **Naming as a structure signal.** A file/class/function name that no longer matches its actual responsibility (grew past its original scope, or was never renamed after a refactor) — candidate to rename, or a signal that it should first be split (apply together with the SRP/cohesion checks above, don't treat renaming alone as sufficient when the content itself is mixed).
- **Dead structural weight.** Empty or near-empty pass-through files/folders/index barrels that exist only to route to one real file — candidate to collapse, only when doing so is a pure move with no behavior change.

Do **not** flag, since they're out of this skill's reorg-only scope: missing tests, missing error handling, missing validation, performance, security, naming *style* (formatting/casing conventions), or anything whose fix would require writing new logic rather than moving existing code.

## 3. Build the numbered proposal list

Consolidate step 2's findings into a single numbered list, one proposal per item, each self-contained and independently actionable (not "fix all the god classes" as one item — one per class/area). For each proposal, state:

1. **What** moves/splits/merges/renames (concrete files/classes/paths).
2. **Why** (which checklist principle it resolves, one line).
3. **Where it ends up** (destination file(s)/structure), concrete enough that `pv-new`/`pv-todo` downstream doesn't need to re-derive it.

Order the list by impact (proposals touching widely-shared or foundational code first), not by discovery order. Present the full list to the user before asking anything else — this is a report, not an action yet.

**Hard constraint, restated:** every proposal must be achievable as a pure reorganization — no new functional code, no removed functional code, no behavior change. If a genuinely valuable improvement would require writing new code (introducing an interface that doesn't exist yet, adding a missing abstraction), do not list it as a proposal here — mention it separately, clearly labeled as **out of this skill's scope**, so the user can raise it through `pv-new` directly as a real change if they want it.

## 4. Ask what to do with the proposals

Ask the user which proposals (if any) they want turned into workflow entries — all of them, a subset by number, or none.

```
Do you want me to create workflow entries for all of these proposals, only some (tell me the numbers), or none?
```

If none, stop here — the numbered list itself is the deliverable.

## 5. For each accepted proposal, confirm how to create it

For **every** proposal the user accepted in step 4, ask individually (or in one batched question covering all of them, if that's clearer given the count) whether it should become:

- **A noted idea** (`pv-todo`) — for a proposal the user wants recorded but not committed to the active workflow yet.
- **A documented change** (`pv-new`) — for a proposal the user wants to move into `{changesDir}/inProgress` now, ready to plan with `pv-how`.

```
For proposal #<n> ("<short title>"): do you want it as a noted idea (pv-todo) or as a documented change (pv-new) right away?
```

Don't assume a default — every proposal's destination must be explicitly confirmed by the user, one by one or as an explicit batched choice, never inferred.

## 6. Create each confirmed entry

For each proposal confirmed in step 5, invoke the corresponding skill (Skill tool) with the proposal's **what/why/where** (step 3) as its input content — don't write to `changes/**` directly yourself:

- **`pv-todo`**: invoke it with the proposal's text as the idea to note (`/pv-todo <idea text>`). Let it generate its own code and file as it normally does.
- **`pv-new`**: invoke it with the proposal's text as the change description (`/pv-new <description>`), **appending an explicit note that the technical documentation (`docs.tech.architectureDocDir`/`styleBibleDocDir`) must be updated in full detail once the reorganization is implemented** — every moved/split/merged/renamed file, class, or module needs its existing documentation references (paths, namespace entries, cross-links) updated to match the new location/shape, not left pointing at the pre-refactor structure. This matters more here than for an ordinary change: a pure structural refactor changes *where* things live without changing *what* they do, so documentation drift is easy to miss (nothing behaves differently, but every reference to the old location is now stale) and correspondingly easy for `pv-how`/`pv-do` to under-scope if not flagged up front. Let `pv-new` run its own full process otherwise (doubt-anticipation, `pv-internal-workflow` documentation, visual proposal if applicable — a pure code reorganization typically has no UI/visual dimension, so it will likely skip mockups on its own judgment). Don't pre-empt or shortcut its steps.

If a later proposal in the same batch references an earlier one's destination (e.g. proposal #3 moves a file that proposal #1 already relocated), pass that context along when invoking `pv-new`/`pv-todo` for #3, so it documents the *current* expected location, not the pre-review one.

## 7. Final summary

Once every confirmed proposal has been created, report a single list: proposal number, short title, and what it became (`pv-todo` idea `<code>` or `pv-new` change `<xxxx>`). Proposals declined in step 4 or step 5 aren't repeated here — they were already visible in step 3's list.
