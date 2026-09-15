# Previo v0.9.7 changelog (from v0.9.6)

## Index

- ⭐[New](#new)
  - 📂Project hook system (6 changes)
- ✏️[Changed](#changed)
  - 📂Project hook system (4 changes)
  - `pv-init`'s scaffolding now seeds the hooks folder
- ❌[Deleted](#deleted)
  - `pv-version`'s old single-file custom pipeline removed

## ⭐New

- 📂**Project hook system**:
  - **Per-flow hook insertion points added across the framework** — `pv-do`, `pv-how`, `pv-new`, `pv-fix`, and `pv-version` each now expose fixed customization points as individual files under `{workFolder}/stuff/hooks/<flow>/<NN>-<slug>.md`, one file per insertion point, holding zero or more steps (command, expected output, notes). A hook with no steps is skipped silently; a step that fails stops the flow and explains why. `stuff/` gains a `hooks/` subfolder with one subdirectory per hook-exposing skill — running `pv-init` on a new project or `pv-update` on an existing one seeds the new files automatically, without overwriting any existing project-authored content.
  - **`pv-how` gains two hook points** — one before technical analysis starts, to load or refresh context such as generated types, a DB schema dump, or external docs (skipped when the user chooses to implement an existing `plan.md` instead of re-analyzing), and one after `plan.md` and its risk score are written, before the user is asked to implement, to validate or publish the plan (e.g. open a ticket).
  - **`pv-new` gains one hook point** — after the entry (and any mockups) are finished, right before handoff to `pv-how`, for registering the entry externally (e.g. a tracker issue, a channel post, an index row). In todo mode it runs after the originating idea is deleted.
  - **`pv-fix` gains a hook point for the fast-track (trivial-change) path** — right after the entry is documented, before any code is touched, the only customization point available before a fast-tracked change lands since fast-track skips `plan.md`/`pv-how` entirely. The fast-track now also runs `pv-do`'s two hooks below, since it edits code the same way `pv-do` does.
  - **`pv-version` gains a fifth, earliest hook point** — before even checking that `implemented/` is empty, for cheap abort checks (clean git tree, correct branch, CI green, release tag not already taken). Its three former "custom pipeline" sections become three separate hook files instead of sections in one shared file (see Changed, below).
  - **`pv-do` gains two hook points** — before any code is edited, and after code/docs are done but before the folder moves to `implemented/`. Both also run from `pv-fix`'s fast-track.

## ✏️Changed

- 📂**Project hook system**:
  - **`pv-version`'s old single-file, three-section custom pipeline is replaced by the new per-point hook files** — the former fixed sections ("Before starting" / "In the middle" / "At the end") are now three independent files, plus the new earliest guardrail hook. **Action required:** `pv-update` detects the legacy single file — if it's an untouched empty seed it's deleted and reseeded automatically; if it holds project-authored steps, it is **not** migrated automatically, and is reported with the section→file mapping so the user can move the steps by hand.
  - **`pv-version`'s build-procedure file renamed from `how-to-compile-version.md` to `how-to-compile.md`** — same role and format, name only. **Action required:** `pv-update` renames the file automatically when only the old name is found; if both names exist, neither is touched and the user is asked to reconcile them manually.
  - **`pv-update`'s audit/repair scope extended to the new hooks system** — it checks each hook file's presence, renames any file using an old/non-canonical name while preserving its content, and, since hook files are fixed technical English with no language option, automatically translates any project-authored step content found in another language in place, leaving commands and file paths untouched.
  - **`pv-do`, `pv-how`, `pv-new`, `pv-fix`, and `pv-version` now explicitly document themselves as non-editable installed framework** — a request to change how one of these flows behaves is now answered by pointing to the relevant hook file instead of hand-editing the skill, since a hand-edited skill falls out of sync with `pv-update`'s version tracking. Each of these skills also gained an explicit workflow diagram file (`workflow.do.md`, alongside existing ones for the others) documenting the flow's full sequence including hook branch points.
- **`pv-init`'s scaffolding now seeds the hooks folder** — project scaffolding now seeds `stuff/hooks/` and its per-skill subfolders/seed files instead of the old single custom-pipeline seed, as part of initializing a new project.

## ❌Deleted

- **`pv-version`'s old single-file custom pipeline removed** — the three-section, zero-step seed file is gone, superseded by the separate per-point hook template files described above.
