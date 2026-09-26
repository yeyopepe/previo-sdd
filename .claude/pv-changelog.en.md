# Previo v0.9.8rc1 changelog (from v0.9.7)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - New reviewer-annotation framework for HTML mockups
  - 📂Framework self-install (2 changes)
  - 📂`pv-update`'s self-healing audit (2 changes)
  - 📂New maintenance skills (2 changes)
- ✏️[Changed](#changed)
  - Mockups and their supporting files moved to a new folder layout
  - The framework's own guide moved into its own folder
  - No `pv-*` skill reads or edits a mockup file directly anymore
  - `pv.py` settings menu labels clarified
  - `pv.py` menus now exit with an "X" key

## ⭐New

- **New reviewer-annotation framework for HTML mockups** — every mockup now embeds a self-contained runtime that lets the reviewer pin a note to a specific element or leave a general note, without leaving the mockup itself. Before presenting the mockup again, the framework automatically resolves every open note: when it can confidently tell what change is being asked for, it applies it directly to the mockup and closes the note; when a note is ambiguous, or its linked element no longer exists in the mockup ("detached" note), it asks the reviewer before touching anything. No `pv-*` skill (`pv-new`, `pv-fix`, `pv-how`) reads or edits a mockup file directly anymore — they all go exclusively through the configured mockups skill's `describe` action (plain-text visual reference) and `ensure-closed` action (annotation resolution), which also means the built-in HTML mockups skill can be swapped for a custom one (Figma, a component library, etc.) without touching the rest of the framework.
- 📂**Framework self-install**:
  - **`pv-update` gained an explicit install mode (`/pv-update install`)** to install or update the `pv-*` framework itself (not just audit its configuration) to a version equal to or newer than what's installed, via a strict resolve-then-confirm-then-install protocol that never silently downgrades and always names the exact target version before touching anything; on success it automatically chains into the existing audit/repair mode to verify the newly installed version.
  - **`pv.py`'s settings menu gained an "Install new Previo version" option**, wired to the same install mechanism as `/pv-update install`, letting a user upgrade/reinstall the framework without going through Claude Code.
- 📂**`pv-update`'s self-healing audit**:
  - **`pv-update`'s audit now detects and fixes leftover template syntax** — if a generated `description.md`/`plan.md` still shows the raw `[[[Label]]]` template markup instead of the plain label, the audit strips the brackets automatically.
  - **`pv-update`'s audit now migrates old mockup/data files into the current folder/naming convention** — mockups left loose in an entry's root (predating the `mockups/` subfolder) are moved into `mockups/`, and `design_navigation_*.md`/`design_data_*.md` files still carrying the retired `design_` prefix are renamed to `navigation_*.md`/`data_*.md`, both automatically.
- 📂**New maintenance skills**:
  - **`pv-review-doc-tech`** rereads every configured `docs.tech` folder in full and reorganizes it — moving/merging content, fixing content filed under the wrong Area — without ever adding, deleting, or rewriting a fact.
  - **`pv-review-architecture`** reviews the project's real source code against a fixed structural checklist (separation of concerns, size, SOLID, DRY, KISS, coupling, naming) and produces a numbered list of pure reorganization proposals (move/split/merge/rename, never new or removed functionality); for each proposal the user accepts, it routes it into `pv-todo` or `pv-new` as chosen.

## ✏️Changed

- **Mockups and their supporting data/navigation files moved to a new folder layout** — `design_*.html`/`design_*.txt` mockups now live in a `mockups/` subfolder inside each change/fix entry instead of loose in its root, and `design_navigation_*.md`/`design_data_*.md` are renamed to `navigation_*.md`/`data_*.md` (still loose in the entry root). `pv-new`, `pv-fix`, `pv-how`, `pv-todo`, and `pv-status` were all updated to this convention. **Action required after updating**: run `/pv-update` — it detects and migrates any entry still on the old layout automatically.
- **The framework's own guide moved into its own folder** — `pv-guide.en.md`/`pv-guide.es.md` now live under `.claude/pv-doc/pv-guide/` instead of directly in `.claude/pv-doc/`. **Action required after updating**: re-run `/pv-update`/reinstall so any project reference to the old flat path is refreshed.
- **No `pv-*` skill reads or edits a mockup file directly anymore** — `pv-new`, `pv-fix`, and `pv-how` now go exclusively through the configured mockups skill's `describe` action to get a plain-text visual reference and its `ensure-closed` action to resolve pending reviewer annotations; a project supplying a custom `framework.skills.mockups` implementation must now support both actions (plus `style_context`/`language` inputs) to remain a drop-in replacement.
- **`pv.py`'s settings menu had two options relabeled for clarity** — "Change max character width" is now "Change terminal max character width", and "Check Previo versions" is now "Check product versions".
- **`pv.py`'s menus now exit with an "X" key instead of a trailing numbered option**, so the exit choice no longer shifts as menu items are added/removed.
