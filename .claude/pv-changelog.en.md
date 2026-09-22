# Previo v0.9.8b5 changelog (from v0.9.7)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - New skill to reorganize technical documentation: `/pv-review-doc-tech`
- ✏️[Changed](#changed)
  - Template marker brackets no longer leak into generated files

## ⭐New

- **New skill to reorganize technical documentation: `/pv-review-doc-tech`** — a new periodic-maintenance skill that rereads every folder configured under `docs.tech` (architecture and style bible) in full and reorganizes it — moving, grouping, or consolidating misplaced or duplicated content — without ever deleting a fact, rewriting a sentence, or adding new content. It regenerates each folder's `INDEX.md` automatically and flags anything it's unsure about (such as a needed namespace change) for the user to decide instead of guessing.

## ✏️Changed

- **Template marker brackets no longer leak into generated files** — when filling a template, the framework now correctly drops the `[[[...]]]` wrapper around fixed-English labels (e.g. `**[[[Name]]]**:` becomes `**Name**:`) instead of only skipping their translation, which could previously leave the raw brackets in a generated `description.md`/`plan.md`. `pv-update` also now detects and repairs any file where this happened (`marker-literal:*`).
