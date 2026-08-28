# Previo v0.9.6b7 changelog (from v0.9.5)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - 📂Project documentation is now mandatory (2 changes)
  - New internal skill for documentation file management
  - Every flow skill now has a workflow diagram
- ✏️[Changed](#changed)
  - 📂Documentation folder layout and index (2 changes)
  - Framework health check covers more of the change history
  - Planning template no longer branches on whether documentation is configured
  - Closing implemented entries no longer drops you out after each one

## ⭐New

- 📂**Project documentation is now mandatory**:
  - **Technical, style and features documentation are always set up** — `pv-init` now always creates and scaffolds the architecture doc folder, the style bible folder and the features doc folder on every project. It never asks whether you want them and never lets you remove them; a project that isn't interested in maintaining one keeps the empty folder rather than deleting it. Existing projects that predate this are treated as needing repair and are sent to `pv-update`.
  - **Every skill refuses to run against a project missing any of the three doc folders** — `pv-new`, `pv-fix`, `pv-how`, `pv-do` and `pv-version` now stop and tell you to run `/pv-update` if the architecture, style or features documentation folder is missing from the configuration or absent on disk, instead of silently skipping that part of their work. An empty folder holding only its placeholder is fine and does not trigger this.
- **New internal skill for documentation file management** — a new `pv-internal-doc-files` skill centralizes how every documentation folder stores its files (one numbered file per topic, an auto-generated index, locating an existing entry before writing a new one). `pv-internal-doc-features` now focuses only on deciding what a feature entry says, delegating the file handling to the new skill. This is internal plumbing with no change to how you invoke anything.
- **Every flow skill now has a workflow diagram** — `pv-new`, `pv-fix`, `pv-how` and `pv-version` each ship a diagram of their own step sequence and branches, which the skill now treats as the authoritative description of its flow (matching what `pv-update` already did). Behavior is unchanged; the flows are just pinned down explicitly.

## ✏️Changed

- 📂**Documentation folder layout and index**:
  - **Documentation files are numbered with three digits and grouped by area** — files in every documentation folder now use a 3-digit prefix (`001-`, `002-`…) instead of two, and each file carries an area label used to group it in the folder's index. Existing folders keep working; new files follow the new convention.
  - **The documentation index is always regenerated, never hand-written** — every documentation folder's `INDEX.md` is now produced deterministically from the folder's files (the features documentation already worked this way; the architecture and style folders now do too).
- **Framework health check covers more of the change history** — `pv-update`'s audit now also checks the plans of already-implemented entries, and flags translated section headings (not just field labels) in change/fix documents, restoring them to their canonical form. Documents created by an older framework version whose templates were still translated are the common case this repairs.
- **Planning template no longer branches on whether documentation is configured** — the plan's "Architecture changes" and "Style changes" sections are now simply included when the change actually touches architecture or style, without the earlier "only if that documentation is configured" condition (since it always is now). Several plan and change-description section headings are also now fixed in English regardless of the configured language, so status reporting keeps working.
- **Closing implemented entries no longer drops you out after each one** — closing entries from the `pv.py` helper now re-lists the remaining pending entries after each closure, so you can close several in a row without re-launching it.
