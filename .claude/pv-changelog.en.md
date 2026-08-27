# Previo v0.9.6b6 changelog (from v0.9.5)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - Skills now follow an explicit workflow diagram
  - Shared file-management engine for the documentation folders
  - Logical-key path resolution
- ✏️[Changed](#changed)
  - 📂The three documentation folders are now mandatory (5 changes)
  - 📂Documentation generation restructured (3 changes)
  - Trivial-fix fast track no longer depends on doc folders being configured
  - Plan and description templates protect more structural markers
  - Launcher reloads the closable-entry list after each closure

## ⭐New

- **Skills now follow an explicit workflow diagram** — `pv-fix`, `pv-how`, `pv-new` and `pv-version` each now read a dedicated Mermaid workflow diagram (`workflow.*.md` alongside the skill) as the authoritative source for their step sequence and branching; the prose steps are just per-node detail, and the diagram wins if the two ever disagree.
- **Shared file-management engine for the documentation folders** — introduced `pv-internal-doc-files`, a shared procedure that handles file numbering, `INDEX.md` regeneration, and locating/writing entries for all three documentation folders (features, architecture, style bible) with one consistent convention.
- **Logical-key path resolution** — added `resolve-path.py` (owned by `pv-init`), the single place that turns a logical key (`workFolder`, `sourcecodeDir`, `changesDir`, `versionsDir`, `stuffDir`, `architectureDocDir`, `styleBibleDocDir`, `featuresDocPathDir`) into an absolute path. Every flow skill now asks it for paths instead of parsing `pv-context.json` itself; on any failure the calling skill stops and sends the user to `/pv-update`.

## ✏️Changed

- 📂**The three documentation folders are now mandatory**:
  - **`docs.functional.featuresDocPathDir`, `docs.tech.architectureDocDir` and `docs.tech.styleBibleDocDir` are required** — `pv-init` always configures and scaffolds all three; `pv-context.json`'s schema now marks them required. A config missing any of them is a broken state, not a supported "documentation disabled" mode. **On update, run `/pv-update`** — it adds any absent doc dir with its default path and an empty placeholder `INDEX.md`.
  - **`pv-do` stops instead of silently skipping** — where it previously skipped a documentation update when the corresponding path wasn't configured, it now resolves all three up front and halts (directing the user to `/pv-update`) if any can't be resolved to a real folder. A folder that exists but holds only its placeholder is still fine.
  - **`pv-how` requires the doc dirs to resolve** — planning no longer "proceeds without them" when documentation paths are absent; an unresolvable doc dir stops the analysis and points the user to `/pv-update`.
  - **`pv-version` requires the doc dirs to resolve** — `copy-docs.py` no longer skips a documentation zip for an unconfigured path; a missing or non-existent doc dir now aborts the step, and the release always includes all three zipped docs.
  - **`pv-init` treats a missing doc dir as broken, not incomplete** — on an already-initialized project, a lost required doc dir routes `pv-init` to its repair branch (`pv-update`) rather than into the optional-fields questionnaire. Declining to *maintain* a doc area is still fine — the field and its empty folder stay.
- 📂**Documentation generation restructured**:
  - **File numbering unified across all three doc folders** — `architectureDocDir` and `styleBibleDocDir` files now use the same convention as `featuresDocPathDir`: a 3-digit prefix plus an `**Area**` field (e.g. `001-{slug}.md`), replacing the old 2-digit prefix, with `INDEX.md` always regenerated rather than hand-written. Existing files in those two folders should be renamed to the new convention when updating.
  - **Architecture documentation follows a content checklist** — updating `docs.tech.architectureDocDir` now checks the change against a fixed list of content categories (components, contracts, data flows, decisions, dependencies, data model, configuration) to decide what's already covered and what still needs writing, on top of the existing writing-style guidance.
  - **Feature documentation drafts itself from a summary** — `pv-internal-doc-features` now receives a summary of what was implemented plus the gathered context and drafts the feature entry itself (in-place edit vs. new entry, which diagrams carry over, wording), instead of being handed finished text to save; it delegates all file placement to `pv-internal-doc-files`.
- **Trivial-fix fast track no longer depends on doc folders being configured** — `pv-fix`'s criteria for the `fast` shortcut previously said "if `docs.tech.*` is configured"; since those folders are always configured now, that conditional is gone. The rules themselves (a value-only doc change stays `fast`; a meaningful architecture/style change does not) are unchanged.
- **Plan and description templates protect more structural markers** — `plan.md`'s always-present section headings (`## (a) Functional notes`, `## (b) Technical solution`, `## (e) Verification`) and `description.md`'s `## Full description` heading are now marked as fixed-English structural labels. `pv-update`'s marker check now also walks `plan.md` under `implemented/` and recognises translated headings from older framework versions as something to restore, in any language.
- **Launcher reloads the closable-entry list after each closure** — in `pv.py`, closing an implemented entry now re-lists the remaining ones so several can be closed in a row, instead of returning to the menu after a single closure.
