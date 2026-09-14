# Previo v0.9.7b4 changelog (from v0.9.6)

## Index

- ⭐[New](#new)
  - Project-specific hooks at fixed points of every flow
- ✏️[Changed](#changed)
  - `pv-version`'s custom pipeline replaced by the new hooks layout
  - `how-to-compile-version.md` renamed to `how-to-compile.md`
  - `pv-init`/`pv-update` now scaffold and audit the hooks layout

## ⭐New

- **Project-specific hooks at fixed points of every flow** — `pv-new`, `pv-how`, `pv-fix`, `pv-do` and `pv-version` each now expose one or more insertion points where a project can define its own steps (commands to run), stored one file per point under `{workFolder}/stuff/hooks/<flow>/`. Uses include registering a new change in an external tracker, loading context before analysis, running tests or a linter after implementation, or a precondition check before a release starts. A hook with no defined steps is skipped silently, so existing projects keep working exactly as before until they choose to add something; if a defined step fails, the flow stops and explains why instead of continuing.

## ✏️Changed

- **`pv-version`'s custom pipeline replaced by the new hooks layout** — the previous single file with three fixed sections (`custom-version-pipeline.md`) is replaced by four separate hook files (`stuff/hooks/version/`), giving the release flow two additional insertion points: one that runs before anything else (useful for aborting early, e.g. dirty git tree or wrong branch) and one right after the version code is resolved, on top of the previous after-build and after-changelog points.
- **`how-to-compile-version.md` renamed to `how-to-compile.md`** — same purpose (documenting the project's build/deliverable-generation procedure), only the file name changed; existing content is preserved and only needs renaming.
- **`pv-init`/`pv-update` now scaffold and audit the hooks layout** — a new project gets the full set of seed hook files created automatically, and `pv-update` on an existing project now detects a leftover legacy pipeline file (auto-deletes it if it's an untouched seed, or reports it for manual migration if it already holds project-authored steps) and any hook file with a non-canonical name (renamed automatically, keeping its content).
