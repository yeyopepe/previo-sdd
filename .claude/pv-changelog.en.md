# Previo v0.9.7b3 changelog (from v0.9.6)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - 📂Project hooks for the implementation flow (2 changes)
- ✏️[Changed](#changed)
  - 📂Release-pipeline customization moved to hook files (4 changes)
- ❌[Deleted](#deleted)
  - Legacy single-file release-pipeline template removed

## ⭐New

- 📂**Project hooks for the implementation flow**:
  - **`pv-do` runs project steps before and after implementing** — `pv-do` now looks for two optional hook files in `{workFolder}/stuff/hooks/do/` (`10-before-start.md`, run before any code is edited; `20-before-finish.md`, run after the code and docs are updated and before the change/fix folder moves to `implemented/`). Each holds project-defined steps to run at that point; an absent or step-less file is skipped silently, so projects that don't use them are unaffected. If a step fails, `pv-do` stops and explains instead of working around it.
  - **`pv-fix`'s fast track runs the same hooks** — a trivially-fast fix edits code directly without going through `pv-do`, and now runs the same `10-before-start` / `20-before-finish` hooks around that edit. There is no separate `fix/` hook set — the fast track shares `pv-do`'s.

## ✏️Changed

- 📂**Release-pipeline customization moved to hook files**:
  - **`pv-version` custom steps are now one file per insertion point** — the single `{workFolder}/stuff/custom-version-pipeline.md` (with its `## Before starting` / `## In the middle` / `## At the end` sections) is replaced by three files in `{workFolder}/stuff/hooks/version/`: `10-pre-release.md`, `20-post-build.md`, `30-post-changelog.md`. Each runs at the same point in the flow as the section it replaces. Projects that added custom pipeline steps must move each section's steps into the matching hook file (see below).
  - **`pv-update` migrates or flags the old pipeline file** — running `pv-update` now detects a pre-hooks `custom-version-pipeline.md`: an untouched seed (no steps) is deleted and the new hook layout is reseeded automatically; one that contains project-authored steps is reported as a pending manual migration with the exact section→file mapping, and is not auto-fixed. Until migrated, those steps no longer run.
  - **The build-procedure file was renamed to `how-to-compile.md`** — `{workFolder}/stuff/how-to-compile-version.md` is now `how-to-compile.md`. `pv-version` reads only the new name. `pv-update` renames an existing file in place; if both names exist it asks which one is current instead of guessing.
  - **`pv-init` scaffolds the new `stuff/hooks/` layout** — a freshly initialized project now gets `stuff/hooks/` with one subfolder per hook-exposing skill (`version/`, `do/`) pre-seeded with header-only hook files (no steps). Existing files are never overwritten, so steps a project already added survive re-initialization and `pv-update`.

## ❌Deleted

- **Legacy single-file release-pipeline template removed** — the `custom-version-pipeline.md` template shipped with `pv-version` is gone, replaced by the per-insertion-point hook templates. See the migration handled by `pv-update` above.
