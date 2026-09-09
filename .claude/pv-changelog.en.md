# Previo v0.9.7b2 changelog (from v0.9.6)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - `pv-do` gained project hooks
- ✏️[Changed](#changed)
  - 📂Project hooks and release-pipeline customization (4 changes)

## ⭐New

- **`pv-do` gained project hooks** — `pv-do` now runs project-specific steps at two points of the implementation flow: before it starts editing code, and after the code and synced documentation are done but before the change moves to `implemented/`. The steps live in `{workFolder}/stuff/hooks/do/10-before-start.md` and `20-before-finish.md`; a file that's absent or defines no steps is skipped silently, and a hook step whose command fails stops the flow instead of being worked around.

## ✏️Changed

- 📂**Project hooks and release-pipeline customization**:
  - **Release-pipeline steps split into one file per insertion point** — `pv-version`'s single `{workFolder}/stuff/custom-version-pipeline.md` (one file with three `##` sections) is replaced by three separate files under `{workFolder}/stuff/hooks/version/`: `10-pre-release.md` (before the version code is resolved), `20-post-build.md` (after the deliverable's artifacts are copied), and `30-post-changelog.md` (after the changelog, before the summary). When updating a project, run `/pv-update` once to recreate the new layout; a project that still has the old single file with real steps in it is flagged with a section→file mapping so the steps can be moved by hand — it is not migrated automatically.
  - **Build-procedure file renamed** — `{workFolder}/stuff/how-to-compile-version.md` is now `how-to-compile.md`. `pv-version` only reads the new name, so when updating a project run `/pv-update`, which renames it in place; if both names already exist it asks which one is current.
  - **`pv-init` seeds the hook folders** — a freshly scaffolded project now gets `{workFolder}/stuff/hooks/` containing `hooks/version/` (the three `pv-version` files) and `hooks/do/` (the two `pv-do` files), each seeded with just a header and no steps and never overwritten, so the customization points are discoverable from the start.
  - **`pv-update` audits the hook files and any legacy pipeline** — the health check now verifies every `pv-version` and `pv-do` hook file is present with its canonical name, renames a misnamed one, deletes an untouched legacy single-file pipeline seed and reseeds the new layout, flags a legacy pipeline that still contains steps for manual migration, and detects the `how-to-compile-version.md` → `how-to-compile.md` rename.
