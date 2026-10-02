# Previo v0.9.8 changelog (from v0.9.7)

## Index

- ⭐[New](#new)
  - 📂Framework self-update (2 changes)
  - 📂Architecture and documentation maintenance (2 changes)
  - User guide
  - Mockup review-annotation framework
- ✏️[Changed](#changed)
  - Mockup lifecycle now has explicit close and describe actions
  - Every skill now verifies the framework installation before running
  - Maximum characters for change descriptions is now configurable

## ⭐New

- 📂**Framework self-update**:
  - **`/pv-update install` installs or updates the framework itself** — a new explicit mode that resolves the latest (or a requested) official release from GitHub, warns about pre-releases and same-version reinstalls, refuses to downgrade, and only installs after the user confirms the exact resolved version by name. On success it automatically runs the usual configuration audit against the newly installed version.
  - **`pv.py` can install a new Previo version from its own menu** — a new "Install new Previo version" option mirrors the same resolve-confirm-install flow as `/pv-update install`, without needing to open Claude Code.
- 📂**Architecture and documentation maintenance**:
  - **New skill: `/pv-review-architecture`** — analyzes the project's real source code against a checklist of language-agnostic design principles (separation of concerns, SOLID, file size, naming, layering, DRY/KISS) and produces a numbered list of pure reorganization proposals (splitting, merging, relocating, renaming), never adding or removing functionality. For each proposal accepted, it can turn it into a noted idea (`pv-todo`) or a documented change (`pv-new`).
  - **New skill: `/pv-review-doc-tech`** — reorganizes the project's technical documentation folders (`architectureDocDir`, `styleBibleDocDir`) for structure only: moving misplaced content to the right file/category, merging duplicates, and fixing wrong groupings, without ever deleting, rewriting, or adding content.
- **New user guide** — a full onboarding document (`pv-guide`) walking through setup, the natural change-definition-planning-implementation flow, release preparation, and the maintenance skills, aimed at someone new to the framework.
- **Mockup review-annotation framework** — HTML mockups (`design_*.html`) now embed a standard, self-contained review-annotation toolbar (pin notes to elements, general notes, show/hide, save), letting a reviewer leave feedback directly on the mockup instead of only in chat.

## ✏️Changed

- **Mockup lifecycle now has explicit close and describe actions** — both the HTML and ASCII mockup skills gained an `ensure-closed` action (resolving any pending annotation on a mockup before it's treated as final) and a `describe` action (a plain-text summary of a mockup's visual content for another skill to use as reference, without reading the raw file). `pv-new`, `pv-fix` and `pv-how` now go through these actions at the right points of their flow instead of reading mockup files directly.
- **Every skill now verifies the framework installation before running** — `pv-fix`, `pv-how`, `pv-do`, `pv-new`, `pv-todo`, `pv-status` and the other `pv-*` skills now check the framework's installation status as their first step and stop with a clear message pointing to `/pv-update install` if something is wrong, instead of surfacing a less clear failure deeper into their own flow.
- **Maximum characters for change descriptions is now configurable** — `pv.py`'s details view has a new setting to change how many characters of a change's description are shown, alongside the existing terminal width setting.
