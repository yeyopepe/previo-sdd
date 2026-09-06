# Previo v0.9.6b15 changelog (from v0.9.5)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - 📂Focus flags on changes (3 changes)
  - 📂Relationships between changes (2 changes)
  - 📂Custom steps in the release pipeline (4 changes)
  - Demote a change back to a noted idea
  - The `pv.py` console gains a "Changes info" menu and a width setting
  - Mockups now follow the project's documented style
  - First-time documentation is generated in depth from existing code
- ✏️[Changed](#changed)
  - 📂Required documentation folders (3 changes)
  - 📂Technical documentation is always English (2 changes)
  - Change risk moved out of `plan.md` into per-change metadata
  - Skill flows are now driven by a diagram
  - `pv-version` is framework-managed and no longer edited per project
  - `pv-update` audits more of the project

## ⭐New

- 📂**Focus flags on changes**:
  - **A change can be flagged as a priority or as work in progress** — every change/fix can now carry one or more focus flags, orthogonal to its lifecycle state: `priority` (⭐, moves up the queue) and `workinprogress` (⚙️, actively being worked on). Flags live in a hidden `.metadata.json` next to the change's other files, travel with the folder as it moves between states, and never apply to `todo/` ideas. A change with no flags has no such file — existing projects need no migration.
  - **Flags are toggled and listed from the `pv.py` console** — under the new "Changes info" menu, "Toggle a flag on a change" shows the changes grouped the same way as the overall status (closed changes excluded), and picking one lets you switch its flags on/off instantly, with no confirmation prompt. "Show changes by flag" lists everything carrying a given flag.
  - **`pv-status` shows the flag icons** — every change listing in `/pv-status` (both the chat report and the terminal output) now shows the ⭐/⚙️ icons for each change, via a new `Flags` column in chat and an icon prefix in the terminal.

- 📂**Relationships between changes**:
  - **A change can record which other changes it relates to** — when documenting a change with `/pv-new` or a non-trivial fix with `/pv-fix`, the skill now notices when the work looks connected to another existing change/fix (because you mentioned it, or because the analysis found a clear link) and asks you to confirm the relation. Confirmed ids are stored in the change's `.metadata.json`. Trivial fast-tracked fixes never record relations.
  - **Relations are always reciprocal** — relating change A to change B updates both sides in the same operation, so a relationship is never known to only one of the two changes. Each related id must point at a real change in a non-`todo` state, and a change can never relate to itself.

- 📂**Custom steps in the release pipeline**:
  - **The release flow runs the project's own steps at three fixed points** — `pv-version` now looks for `{workFolder}/stuff/custom-version-pipeline.md` and, if it exists, runs the steps it defines at three points of the release: before anything starts, in the middle (once the deliverable's artifacts are in place), and at the end (after the changelog is drafted, before the final summary). Each step is prose plus a command run from the repo root, with `{workFolder}`, `{XXXX}` and the `versions/{XXXX}/` paths substituted where they apply. A section with no steps is skipped silently, and a project that never created the file behaves exactly as before. If a custom step fails, the release stops and the problem is explained rather than worked around. The final summary now also reports which custom sections ran and what they produced.
  - **New projects are scaffolded with the custom-pipeline file** — `pv-init` now creates `{workFolder}/stuff/custom-version-pipeline.md` from the start, containing just its three fixed section headings and no steps, so the customization mechanism is discoverable. It is never overwritten, so a project that has already added steps keeps them.
  - **`pv-update` checks the custom-pipeline file is present** — for projects scaffolded before this file existed, `pv-update` now detects that `{workFolder}/stuff/` has no `custom-version-pipeline.md` and recreates the empty seed (three sections, zero steps). Only the file's presence is checked, never its contents, and an existing file is left untouched. Run `/pv-update` once to pick this up on an existing project.
  - **The guide documents the new customization point** — `pv-guide` now has a "Custom steps in the release pipeline" section under "More ways to customize Previo", describing the two `{workFolder}/stuff/` customization files, the three hook points and which variables each one can use.

- **Demote a change back to a noted idea** — `/pv-todo change <xxxx>` (or just `/pv-todo <xxxx>`) takes an `inProgress` change that has been deprioritized and turns its whole folder into a `pv-todo` idea: all of its content (analysis, plan, prompt history, mockups, data tables) is preserved under a new idea code, and the change is removed from the workflow. Only `inProgress` changes can be demoted; the operation always asks for explicit confirmation first. Reviving a demoted idea still means re-documenting it with `/pv-new` or `/pv-fix` (reusing the preserved files as input).

- **The `pv.py` console gains a "Changes info" menu and a width setting** — `pv.py`'s main menu now has a "Changes info" submenu with five options: search by id, search by content, list by state, toggle a flag on a change, and list changes by flag. Its Configuration submenu also gains a "Change max character width" option that persists a preferred line width for the console's menus and reports (default 80).

- **Mockups now follow the project's documented style** — before inventing any visual styling or sample copy, the HTML and ASCII mockup skills now read the project's style bible and reuse its concrete values (colors, spacing, token names, button labels, status text). Where the style bible doesn't cover something, a neutral placeholder is used and noted in the file. Mockups stay self-contained (styling copied inline, never linked).

- **First-time documentation is generated in depth from existing code** — when `/pv-init` runs on a project that already has code and you pick a documentation level, it now follows a checklist to genuinely populate all three documentation folders: an architecture doc (file/symbol map at minimal level, full layer/flow/contract treatment at full level), a style bible (full depth in both levels, when the project has a presentation layer), an exhaustive feature listing, and the project namespace tree. Step 6's summary reports the outcome of each, including anything it could not complete.

## ✏️Changed

- 📂**Required documentation folders**:
  - **The architecture, style-bible and feature folders are now mandatory** — `docs.tech.architectureDocDir`, `docs.tech.styleBibleDocDir` and `docs.functional.featuresDocPathDir` are no longer optional. `pv-init` always writes and scaffolds all three, and every other skill refuses to run against a `pv-context.json` missing any of them, sending you to `/pv-update`. A folder that exists but holds only its placeholder `INDEX.md` is a valid "nothing documented yet" state, not a problem — the folder and its config entry must never be deleted, even for documentation you don't intend to maintain.
  - **`pv-update` repairs a missing documentation folder** — if any of the three doc dirs is absent from `pv-context.json`, `pv-update` now adds it back with its default path (`docs/features`, `docs/architecture`, `docs/style` under `{workFolder}/`) and creates the folder with a minimal `INDEX.md`. Existing projects that were configured before these became required should run `/pv-update` once.
  - **Skills resolve documentation paths through a script, not by reading the config** — `pv-new`, `pv-fix`, `pv-how`, `pv-do` and `pv-internal-tech-analysis` no longer parse `pv-context.json`'s path fields directly; they resolve each documentation folder via a shared `resolve-path.py` helper. If resolution fails, the skill stops and sends you to `/pv-update` instead of guessing. This is internal, but a broken config now surfaces consistently as "run `/pv-update`" across every skill.

- 📂**Technical documentation is always English**:
  - **The `docs.tech.language` setting has been removed** — architecture and style-bible documentation is now always written in fixed technical English, regardless of `interaction.language` or any other language setting (it is optimized to be read by the skills themselves, not by a person). `pv-init` no longer asks about it, and "reuse the same language for everything" no longer includes the technical docs. The changelog and feature documentation still follow their own language settings. If you configured Spanish and your technical docs come out in English, that is now intended behavior.
  - **`pv-update` removes the obsolete language key** — a `docs.tech.language` key left over from before this change is now detected and deleted from `pv-context.json` (along with its `_comments` entry). It changes no path and no behavior; run `/pv-update` once to clean it up.

- **Change risk moved out of `plan.md` into per-change metadata** — the risk median that `pv-how` computes is no longer written as a `**Risk**` field in `plan.md`'s header; it is stored as an integer in the change's `.metadata.json`. `pv-status` derives the textual meaning ("Moderate risk", etc.) from that integer when it needs it. `pv-update` performs a one-shot migration of existing plans: it moves the value into `.metadata.json` and removes the dead header line (for `closed/` plans the header line is left in place but the value is still migrated). The full 9-factor breakdown, when requested, is still added to `plan.md` as an optional section.

- **Skill flows are now driven by a diagram** — `pv-new`, `pv-fix`, `pv-how` and `pv-version` each now ship a `workflow.*.md` file with a Mermaid diagram that is the authoritative description of that skill's step sequence and branching. The skill reads it before doing anything else; the prose steps remain as per-node detail, and if the two ever disagree the diagram wins. If the file is missing or unusable, the skill stops rather than improvising its flow.

- **`pv-version` is framework-managed and no longer edited per project** — `pv-version`'s `SKILL.md` and workflow files are installed framework kept in sync by `pv-update`, and are not meant to be hand-edited. To make the release flow do something project-specific there are now exactly two customization points, both in `{workFolder}/stuff/`: `how-to-compile-version.md` (how to build the deliverable) and `custom-version-pipeline.md` (the project's own steps). If a request fits neither, `pv-version` will say so and suggest opening a change in the framework repo rather than patching the skill locally.

- **`pv-update` audits more of the project** — beyond its previous checks, `pv-update` now validates each change's `.metadata.json` against its schema (valid JSON, known flags, risk in range, none present under `todo/`), checks the architecture namespace seed (`00-namespace.md` present, with its required headings and resolving anchors), detects obsolete config keys left by a framework upgrade, and checks the custom-pipeline seed. A broken namespace anchor (its file no longer exists) is reported for you to resolve rather than auto-fixed.
