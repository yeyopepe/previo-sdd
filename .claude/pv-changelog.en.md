# Previo v0.9.8b8 changelog (from v0.9.7)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - 📂Maintenance skills (2 changes)
  - 📂Installing and updating the framework itself (2 changes)
  - Mockups now fall back to real code, and flag documentation gaps
  - Mockup count shown in the status detail card
- ✏️[Changed](#changed)
  - 📂Entry folder layout (2 changes)
  - Framework version check is now a single shared script
  - `pv.py` menu wording and navigation tweaks

## ⭐New

- 📂**Maintenance skills**:
  - **`/pv-review-doc-tech` reorganizes the technical documentation** — a new opt-in periodic pass that rereads every folder under `docs.tech` (architecture and style bible) in full and reorganizes it — moving, grouping or consolidating content — without ever rewriting, deleting, or adding facts. It regenerates the documentation index automatically and flags anything it can't safely fix (like a needed namespace change) for the user to decide.
  - **`/pv-review-architecture` proposes code reorganizations** — a new opt-in pass that checks the real source code against a fixed checklist (separation of concerns, file/class size, SOLID, DRY, KISS, coupling, folder structure, naming) and returns a numbered list of reorganization proposals. It never changes behavior or writes code itself; for each proposal the user picks, it hands off to either the idea notebook or the standard change workflow.
- 📂**Installing and updating the framework itself**:
  - **`pv-update` can now install or update the framework** — a new `/pv-update install` mode resolves the requested version (latest official release, or a specific one), always shows the latest pre-release too, and only installs after the user explicitly confirms the exact resolved version by name. It refuses downgrades outright. On success it automatically re-verifies and repairs the project's configuration against the newly installed version.
  - **`pv.py` can install a new Previo version directly from its menu** — a new "Install new Previo version" option under Configuration lists the available versions (latest official, and pre-release if newer) and installs the chosen one after explicit confirmation, without needing Claude Code.
- **Mockups now fall back to real code, and flag documentation gaps** — when generating a visual mockup, if the style bible doesn't cover something needed, the mockup skill now looks for the real convention already used in the app's code before resorting to a neutral placeholder. Any such gap is reported back so it can be tracked as a pending documentation task instead of silently reused.
- **Mockup count shown in the status detail card** — `pv-status`'s terminal detail view now shows how many mockup files an entry has, separately from its other extra files.

## ✏️Changed

- 📂**Entry folder layout**:
  - **Mockups now live in their own `mockups/` subfolder** — visual mockup files (`design_*.html`/`design_*.txt`) for a change/fix entry are now kept under a dedicated `mockups/` subfolder instead of loose alongside the entry's other documents.
  - **Navigation and data files dropped their `design_` prefix** — `design_navigation_*.md` and `design_data_*.md` are now named `navigation_*.md` and `data_*.md`. Existing entries in an older layout are migrated automatically the next time `pv-update` runs.
- **Framework version check is now a single shared script** — every skill now verifies the framework is correctly installed and up to date through one shared check script instead of each doing its own inline comparison; if the framework isn't installed correctly, the user is now pointed to `pv-update`'s new install mode.
- **`pv.py` menu wording and navigation tweaks** — "Check Previo versions" is now "Check product versions" and "Change max character width" is now "Change terminal max character width"; every menu's exit option is now selected with `X` instead of a trailing number.
