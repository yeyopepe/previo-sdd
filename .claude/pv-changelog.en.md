# Previo v0.9.6 changelog (from v0.9.5)

## Index

- ⭐[New](#new)
  - Per-change focus flags
  - Related change/fix links
  - Custom steps in the release pipeline
  - Demote an in-progress change back to a noted idea
  - Configurable terminal width for `pv.py`
  - 📂Documentation internals (2 changes)
- ✏️[Changed](#changed)
  - 📂Documentation folders are now mandatory (3 changes)
  - The risk score moved out of `plan.md`
  - Mockups now follow the project's documented style
  - Skill flows are now driven by an explicit diagram
  - The release flow can no longer be patched locally
  - `pv.py` "Changes info" gained lookup and flag options

## ⭐New

- **Per-change focus flags** — `pv-internal-workflow`, `pv-status`, `pv.py`, `pv-update`: each change/fix can now carry one or more status flags — `priority` (⭐) and `workinprogress` (⚙️) — a layer of personal focus that's independent of the `inProgress`/`implemented`/`closed` lifecycle. Flags are toggled from `pv.py` ("Changes info" → "Toggle a flag on a change") or by a framework skill, shown as a new column/prefix in every `pv-status` listing, and can be listed on their own ("Show changes by flag"). `todo/` ideas never carry flags. `pv-update` validates the stored flag data.
- **Related change/fix links** — `pv-new`, `pv-fix`: when documenting a change or a non-trivial fix, the skill now notices when the request looks related to an existing entry (because the user said so, or because the analysis found a clear connection), asks the user to confirm it, and records the link. Relations are reciprocal — both entries end up pointing at each other. Trivial fast-tracked fixes don't record relations.
- **Custom steps in the release pipeline** — `pv-version`, `pv-init`: a project can now insert its own steps at three fixed points of the release flow — before it starts, after the deliverable is built, and after the changelog is drafted — by filling in `{workFolder}/stuff/custom-version-pipeline.md` (created empty by `pv-init`, with three fixed section headings). Each step is a command plus a note of what it produces; a failing step stops the release instead of being worked around. A project that never touches the file behaves exactly as before; running `/pv-update` once creates the empty seed in an older project.
- **Demote an in-progress change back to a noted idea** — `pv-todo`: `/pv-todo change <xxxx>` (or just `/pv-todo <xxxx>`) takes a deprioritized `inProgress` change and turns its whole folder into a `pv-todo` idea — the plan, the prompt history, the mockups and data tables are all preserved — then removes it from the workflow. Only `inProgress` entries can be demoted, and it always asks for confirmation first since it deletes the change's workflow folder. Reviving the idea later still goes through `pv-new`/`pv-fix` from scratch.
- **Configurable terminal width for `pv.py`** — `pv-init`, `pv.py`: `pv.py` now reads a maximum line width from a new optional `framework.onescript.width` setting and uses it for its menus, framed output and the width it forwards to the `pv-status` terminal scripts. It's set from `pv.py` itself ("Configuration" → "Change max character width") — the only place `pv.py` writes to `pv-context.json` — and falls back to 80 if unset or out of range.
- 📂**Documentation internals**:
  - **Project namespace tree** — `pv-init`, `pv-do`, `pv-update`: the architecture documentation folder now gets a `00-namespace.md` file holding a single canonical name tree for the project — one path per citable concept or assertion, with anchors pointing at the code. `pv-init` seeds it, `pv-do` populates and maintains it as it documents changes, and `pv-update` checks it's present, has its required sections, and that its anchors still resolve to real files.
  - **Shared file-management skill for all documentation folders** — `pv-internal-doc-files`: a new internal skill now owns the mechanics common to the features, architecture and style-bible folders (one numbered file per topic, a generated `INDEX.md`, locating an existing entry). `pv-internal-doc-features` keeps deciding what a feature entry says and how it reads, and delegates the file handling here.

## ✏️Changed

- 📂**Documentation folders are now mandatory**:
  - **Architecture, style-bible and features folders are always configured** — `pv-init`, `pv-do`, `pv-how`, `pv-fix`, `pv-new`, `pv-version`, `pv-update`: the three documentation folders are no longer optional — `pv-init` always writes and scaffolds all three, the schema marks them required, and every other skill refuses to run against a configuration missing any of them and sends the user to `/pv-update`. A folder that exists but holds only its placeholder `INDEX.md` is a normal "nothing documented yet" state, not a broken one. Projects initialized before this change that are missing a folder need to run `/pv-update`.
  - **Technical documentation has no language option** — `pv-init`, `pv-do`, `pv-how`, `pv-internal-doc-technical`, `pv-internal-doc-style`, `pv-internal-tech-mermaid`: the architecture documentation and the style bible are now always written in technical English. The `docs.tech.language` setting was removed; `pv-init` no longer asks about it, and `/pv-update` deletes it from an existing configuration. The changelog, the feature documentation and in-progress change documents keep their own language settings unchanged.
  - **Documentation paths are resolved through a shared helper** — `pv-do`, `pv-how`, `pv-fix`, `pv-new`, `pv-internal-tech-analysis`: skills no longer read the documentation-folder paths straight out of `pv-context.json`; they resolve each one through a shared path resolver, and treat any resolution failure as a broken configuration that must be repaired with `/pv-update` before continuing.
- **The risk score moved out of `plan.md`** — `pv-how`, `pv-status`, `pv-update`: the risk median assessed while planning is now stored in the change's `.metadata.json` instead of a `**Risk**` field in `plan.md`'s header. `pv-status` reads it from there, and `plan.md`'s optional risk-detail section is unchanged. `/pv-update` performs a one-shot migration of existing plans: it moves the value into `.metadata.json` and removes the dead header line (leaving `closed/` plans as frozen history).
- **Mockups now follow the project's documented style** — `pv-internal-mockups-html`, `pv-internal-mockups-ascii`: before inventing any styling or sample text, the mockup skills now read the project's style bible and reuse the concrete values and conventions found there (colors, spacing, component names, microcopy), falling back to neutral placeholder styling only for what isn't documented yet.
- **Skill flows are now driven by an explicit diagram** — `pv-new`, `pv-fix`, `pv-how`, `pv-version`: each of these skills now reads a companion `workflow.*.md` file describing its sequence and branches, and follows that as the source of truth for the flow (the prose steps remain as per-node detail). If the diagram file is missing or unusable, the skill stops rather than improvising.
- **The release flow can no longer be patched locally** — `pv-version`: the skill now states plainly that it's installed framework and must not be edited from a consuming project. Requests to change how the release flow works are directed to the two supported customization files in `{workFolder}/stuff/` (`how-to-compile.md` and the new `custom-version-pipeline.md`), or to opening a change in the framework repo.
- **`pv.py` "Changes info" gained lookup and flag options** — `pv.py`: the "Changes info" submenu now offers five options — search by id, search by content, list by state, toggle a flag on a change, and list changes by flag — replacing the previous top-level "listing filtered by state" entry.
