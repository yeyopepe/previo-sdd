# Previo v0.9.7b1 changelog (from v0.9.6)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ✏️[Changed](#changed)
  - 📂pv-version project customization (2 changes)

## ✏️Changed

- 📂**pv-version project customization**:
  - **Release pipeline customization moved from one file to per-point hook files** — the single `{workFolder}/stuff/custom-version-pipeline.md` (with its three `## Before starting` / `## In the middle` / `## At the end` sections) is retired. `pv-version` now runs project-specific steps from one file per insertion point under `{workFolder}/stuff/hooks/version/`: `10-pre-release.md` (before the version code is resolved), `20-post-build.md` (after the deliverable's artifacts are in `versions/{XXXX}/files/`), and `30-post-changelog.md` (after the changelog, before the final summary). `pv-init` seeds the three files (header, no steps); a file with no steps is skipped silently, so a project that never touches them behaves as before. **On update:** run `/pv-update` once to create `stuff/hooks/version/` and its seed files. A project that already has `custom-version-pipeline.md` with its own steps is flagged by `/pv-update` with a section→file mapping (`## Before starting` → `10-pre-release.md`, `## In the middle` → `20-post-build.md`, `## At the end` → `30-post-changelog.md`); the steps must be moved into the matching hook files by hand and the old file deleted — `pv-version` no longer reads it.
  - **Build-procedure file renamed to `how-to-compile.md`** — `pv-version` reads the deliverable-build procedure from `{workFolder}/stuff/how-to-compile.md` instead of the previous `how-to-compile-version.md`, and only recognizes the new name. **On update:** `/pv-update` renames the file in place when only the old name is present. If both `how-to-compile-version.md` and `how-to-compile.md` exist, `/pv-update` reports both and leaves them untouched for the user to reconcile (keep whichever is current, delete the other).
