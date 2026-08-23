# Previo v0.9.6b3 changelog (from v0.9.5)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - Skills now follow an explicit workflow diagram
  - Documentation folders share one file-management engine
- ✏️[Changed](#changed)
  - Architecture documentation now follows a content checklist
  - Feature documentation drafts itself from a summary, not pre-written content
  - Documentation file naming is now consistent across all three doc folders

## ⭐New

- **Skills now follow an explicit workflow diagram** — `pv-fix`, `pv-how`, `pv-new` and `pv-version` each now read a dedicated Mermaid workflow diagram as the authoritative source for their step sequence and branching, instead of relying only on prose instructions.
- **Documentation folders share one file-management engine** — introduced `pv-internal-doc-files`, a shared procedure that now handles file numbering, indexing, and locating/writing entries for all three documentation folders (features, architecture, style bible) consistently.

## ✏️Changed

- **Architecture documentation now follows a content checklist** — when updating `docs.tech.architectureDocDir`, the framework now checks the change against a fixed list of content categories (components, contracts, data flows, decisions, dependencies, data model, configuration) to decide what's already covered and what still needs documenting, instead of relying only on writing-style guidance.
- **Feature documentation drafts itself from a summary, not pre-written content** — when updating `docs.functional.featuresDocPathDir`, the framework now receives a summary of what was implemented and drafts the feature entry itself (deciding in-place edit vs. new entry, which diagrams carry over, and the wording), rather than being handed the finished text to save as-is.
- **Documentation file naming is now consistent across all three doc folders** — `architectureDocDir` and `styleBibleDocDir` files now use the same numbering and area-labeling convention as `featuresDocPathDir` (a 3-digit prefix plus an `Area` field, e.g. `001-{slug}.md`), replacing the previous 2-digit prefix. Existing files in those two folders should be renamed to the new convention when updating.
