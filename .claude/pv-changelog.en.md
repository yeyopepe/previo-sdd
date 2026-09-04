# Previo v0.9.6b14 changelog (from v0.9.6b13)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - 📂Per-project custom steps in the release flow (4 changes)
- ✏️[Changed](#changed)
  - Changes are picked by id when toggling a flag

## ⭐New

- 📂**Per-project custom steps in the release flow**:
  - **The release flow runs the project's own steps at three fixed points** — `pv-version` now looks for `{workFolder}/stuff/custom-version-pipeline.md` and, if it exists, runs the steps it defines at three points of the release: before anything starts, in the middle (once the deliverable's artifacts are in place), and at the end (after the changelog is drafted, before the final summary). Each step is prose plus a command run from the repo root, with `{workFolder}`, `{XXXX}` and the `versions/{XXXX}/` paths substituted where they apply. A section with no steps is skipped silently, and a project that never created the file behaves exactly as before. If a custom step fails, the release stops and the problem is explained rather than worked around. This is the sanctioned way to extend the flow (e.g. publish a release, run a precondition check) — the skill files themselves are not meant to be hand-edited. The final summary now also reports which custom sections ran and what they produced.
  - **New projects are scaffolded with the custom-pipeline file** — `pv-init` now creates `{workFolder}/stuff/custom-version-pipeline.md` from the start, containing just its three fixed section headings and no steps, so the customization mechanism is discoverable. It is never overwritten, so a project that has already added steps keeps them.
  - **`pv-update` checks the custom-pipeline file is present** — for projects scaffolded before this file existed, `pv-update` now detects that `{workFolder}/stuff/` has no `custom-version-pipeline.md` and recreates the empty seed (three sections, zero steps). Only the file's presence is checked, never its contents, and an existing file is left untouched. Run `/pv-update` once to pick this up on an existing project.
  - **The guide documents the new customization point** — `pv-guide` now has a "Custom steps in the release pipeline" section under "More ways to customize Previo", describing the two `{workFolder}/stuff/` customization files, the three hook points and which variables each one can use.

## ✏️Changed

- **Changes are picked by id when toggling a flag** — in the "Toggle a flag on a change" flow (`pv-init`'s project console), the list of changes no longer shows a parallel row number alongside each entry. Changes are still grouped by state, but you now type a change's own id (code) to pick it, rather than cross-referencing a separate numbering. Typing an id that isn't in the list leaves the picker open with a short notice instead of failing.
