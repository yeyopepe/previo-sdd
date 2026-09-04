# Previo v0.9.6b11 changelog (from v0.9.5)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - 📂Change flags (3 changes)
  - Demote a change back into a noted idea
  - Per-project namespace tree
  - Workflow diagrams as the source of truth for each skill's flow
  - `pv.py` maximum line width is now configurable
- ✏️[Changed](#changed)
  - 📂Documentation folders are now mandatory (4 changes)
  - 📂Existing-code documentation on init is now a full checklist (2 changes)
  - Risk lives in the change's metadata, not in `plan.md`
  - `pv-update` gained several new health checks
  - `pv.py`'s "Changes info" menu was reorganised
- ❌[Deleted](#deleted)
  - Per-area language for the technical documentation

## ⭐New

- 📂**Change flags**:
  - **Flags on a change (priority, work in progress)** — a change/fix can now carry status labels that are independent of its lifecycle state: `priority` (⭐) to move it up the queue and `workinprogress` (⚙️) to mark it as actively being worked on. A change can have both, one or none; `todo/` ideas never carry flags. Flags are stored in a hidden `.metadata.json` file inside the change folder that travels with it as it moves between states, and are versioned by git.
  - **Manage and filter by flag from `pv.py`** — `pv.py`'s *Changes info* submenu can toggle a flag on a change (the change list comes out grouped the same way as the overall status; `closed/` entries are excluded) and list every change carrying a given flag. Toggling applies instantly with no confirmation prompt.
  - **Flags shown across `pv-status`** — every `pv-status` change listing now shows the ⭐/⚙️ icons: a dedicated `Flags` column in the chat report and an icon prefix on each entry in the terminal output. `pv-status` also accepts a new `--flag` filter to list, across every state, the changes carrying one or more given flags.
- **Demote a change back into a noted idea** — `/pv-todo change <xxxx>` (or just `/pv-todo <xxxx>`) takes an `inProgress` change/fix that's been deprioritised and turns it back into a `pv-todo` idea, preserving every file it had accumulated (analysis, plan, prompt history, mockups, data tables). The change leaves the workflow entirely — no version, no changelog entry — but its material is kept so the analysis isn't lost while it waits. Reviving it later still goes through `pv-new`/`pv-fix` from scratch, reusing the preserved files as input.
- **Per-project namespace tree** — `docs.tech.architectureDocDir` now carries a `00-namespace.md` file: a single canonical name tree where every architecture and style concept or assertion has exactly one path, with code-backed nodes pointing at their symbol. `pv-init` seeds it, `pv-do` populates it over time, and both architecture and style documentation cite concepts by their canonical path instead of re-describing them. `pv-update` checks the seed is present and well-formed.
- **Workflow diagrams as the source of truth for each skill's flow** — `pv-new`, `pv-fix`, `pv-how`, `pv-version` and (already before) `pv-init`/`pv-update` now each ship a `workflow.*.md` Mermaid diagram that is the authoritative description of that skill's step sequence and branching. The skill reads it before doing anything else; if the prose and the diagram ever disagree, the diagram wins.
- **`pv.py` maximum line width is now configurable** — a new optional `framework.onescript.width` setting controls the maximum line width `pv.py` uses for its menus, framed info and the detail cards it delegates to `pv-status`. It's written through `pv.py`'s own *Configuration → Change max character width* option; `pv-init` never asks about it, and an out-of-spec value falls back to 80.

## ✏️Changed

- 📂**Documentation folders are now mandatory**:
  - **The three documentation folders are always configured** — `docs.tech.architectureDocDir`, `docs.tech.styleBibleDocDir` and `docs.functional.featuresDocPathDir` are no longer optional: `pv-init` always writes and scaffolds all three, and every other skill refuses to run against a config missing any of them. **Action on update:** run `/pv-update` — it adds any missing dir with its default path (`docs/architecture`, `docs/style`, `docs/features` under `workFolder`) and scaffolds the empty folder.
  - **A folder that holds only its placeholder is a valid state** — an existing documentation folder with just its `INDEX.md` and nothing else now means "nothing documented here yet", never a problem. Skills that need detail fall back to reading the source code. Declining to actively maintain the style bible no longer deletes the folder or the config field — the placeholder simply stays.
  - **Skills resolve documentation paths through a script** — no skill parses `pv-context.json`'s path fields directly any more; they call a `resolve-path.py` helper by logical key. A resolution failure is a broken-config signal that sends the user to `/pv-update` and stops the current skill, instead of the skill silently treating the path as unconfigured.
  - **Documentation file numbering is now three digits** — new files in the documentation folders are named `001-`, `002-`… (previously `01-`, `02-`), and each carries an `**Area**:` field so the generated `INDEX.md` groups by topic. Existing two-digit files keep working; the change only affects newly created ones.
- 📂**Existing-code documentation on init is now a full checklist**:
  - **`pv-init` generates initial documentation as a seven-step checklist** — when `pv-init` finds existing code and the user picks a documentation level, it now works through an explicit checklist (gather code context once, load the writing rules, write the architecture docs, decide whether there's a presentation layer, write the style bible, write an *exhaustive* feature list, report the outcome). Each step must be genuinely completed and reported in the final summary; the minimal/full choice changes only the depth of the architecture and feature content, not which steps run.
  - **The documentation skills own more of the decision** — `pv-internal-doc-technical` now also returns a content checklist for the architecture documentation (components, contracts, data flows, decisions, dependencies, data model, configuration) and which categories are already covered versus pending, alongside its writing rules. `pv-internal-doc-features` now decides itself what a feature entry says and how it's written (in-place edit vs. new entry, which diagrams carry over), receiving a summary and context rather than pre-drafted content, and delegates all file mechanics to the new `pv-internal-doc-files` procedure. The technical writing style moved to notation-first (prose is a tagged exception) and gained the `[gotcha]` and `[motivación]` tags.
- **Risk lives in the change's metadata, not in `plan.md`** — the risk median produced by `pv-how` is now written to the change's `.metadata.json` (`risk` field, integer 0-10) instead of a `**Risk**` line in `plan.md`'s header. `pv-status` reads it from there. **Action on update:** run `/pv-update` — it performs a one-shot migration, moving the value from any `plan.md` header into `.metadata.json` and removing the dead header line (except in `closed/`, which is left as frozen history).
- **`pv-update` gained several new health checks** — the audit now also detects and repairs: a `.metadata.json` that violates its contract (bad JSON, unknown keys, invalid flags, out-of-range risk, or one appearing under `todo/`); a `plan.md` still carrying the retired `**Risk**` header; a required documentation dir missing from the config; an obsolete config key left over from a framework upgrade (e.g. `docs.tech.language`); and the `00-namespace.md` seed being absent, missing its normative headings, or carrying an anchor to a file that no longer exists. A broken namespace anchor joins broken JSON and a version downgrade as the cases `pv-update` reports for the user to resolve rather than fixing unilaterally.
- **`pv.py`'s "Changes info" menu was reorganised** — the second `pv.py` menu entry is now a *Changes info* submenu grouping five operations: search by id, search by content, list by state, toggle a flag, and list changes by flag. The standalone "list filtered by state" option folded into it.

## ❌Deleted

- **Per-area language for the technical documentation** — the `docs.tech.language` setting is gone. Architecture and style-bible documentation is now always written in technical English, regardless of `interaction.language` or any other language configured, because it's optimised to be read by the `pv-*` skills themselves rather than by a person. The interaction, in-progress-change, changelog and feature-documentation languages are unaffected and still configurable. **Action on update:** run `/pv-update` — it removes the obsolete key (and its `_comments` entry) from `pv-context.json`.
