# Previo v0.9.8b8 changelog (from v0.9.7)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ⭐[New](#new)
  - 📂Maintenance skills (2 changes)
- ✏️[Changed](#changed)
  - Framework-installation check replaced with a single status-gate script
  - `pv-update` can now install or update the framework itself
  - Mockups and flow/data files reorganized into a dedicated `mockups/` subfolder
  - Mockup generation now falls back to real code conventions when the style bible has gaps
  - `pv-status` now shows the mockup count in the entry detail card
- 🛠️[Fixed](#fixed)
  - Template bracket markers no longer risk leaking into generated documents

## ⭐New

- 📂**Maintenance skills**:
  - **`/pv-review-doc-tech` reorganizes the technical documentation** — a new opt-in skill that rereads every folder under `docs.tech` in full and reorganizes it (moving, grouping, consolidating duplicate or misplaced content) without ever deleting a fact, rewriting a sentence, or adding new content.
  - **`/pv-review-architecture` proposes code reorganizations** — a new opt-in skill that reviews the real source code against a fixed, language-agnostic checklist (separation of concerns, SOLID, DRY, KISS, coupling, naming) and produces a numbered list of structural reorganization proposals, which the user can turn into a noted idea (`pv-todo`) or a documented change (`pv-new`).

## ✏️Changed

- **Framework-installation check replaced with a single status-gate script** — every `pv-*` skill's startup check now runs one shared script (`check-framework-status.py`) instead of comparing version fields itself. **Action needed when updating:** if that script is missing after updating, the framework must be reinstalled via `/pv-update install` before any skill will run.
- **`pv-update` can now install or update the framework itself** — a new explicit `/pv-update install` mode resolves and installs a target version (latest by default), separate from its existing audit-only mode, which still never touches the network.
- **Mockups and flow/data files reorganized into a dedicated `mockups/` subfolder** — `design_*.html`/`design_*.txt` mockups now live under each entry's `mockups/` subfolder instead of loose in its root, and `design_navigation_*.md`/`design_data_*.md` are renamed to `navigation_*.md`/`data_*.md`. **Action needed when updating:** run `/pv-update`, which detects and migrates any entry still using the old layout.
- **Mockup generation now falls back to real code conventions when the style bible has gaps** — when `docs.tech.styleBibleDocDir` doesn't cover an element being mocked up, the mockup skills now look for the real convention in the source code instead of defaulting straight to a neutral placeholder, and report any such gap back to the caller as a documentation debt to track.
- **`pv-status` now shows the mockup count in the entry detail card** — the terminal detail view reports how many files an entry's `mockups/` subfolder holds, alongside its existing extra-files count.

## 🛠️Fixed

- **Template bracket markers no longer risk leaking into generated documents** — every skill that fills in a `[[[...]]]`-marked template field now explicitly drops the triple brackets when writing the real file, and `pv-update`'s audit gained a dedicated check (`marker-literal:*`) to catch and repair any document where the raw brackets survived.
