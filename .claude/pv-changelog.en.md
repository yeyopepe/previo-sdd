# Previo v0.9.5 changelog (from v0.9.21)

## Index

- ⭐[New](#new)
  - Framework health audit and self-repair
  - 📂Framework documentation (3 changes)
  - Codebase analysis on first initialization
  - Multi-language support
  - Framework version verification gate
  - Todo entry deletion
  - Isolated changelog staging
- ✏️[Changed](#changed)
  - 📂`workFolder` structure and paths (4 changes)
  - 📂`pv-status` reports (2 changes)
  - Trivial-fix risk tolerance loosened slightly
  - Technical/style documentation now written using shared style rules
  - Sequential code padding default increased
  - Skill model/effort baseline always recorded
  - Broken or drifted configuration now delegated to `pv-update`
  - Translated framework prose to English

## ⭐New

- **Framework health audit and self-repair** — `pv-update`: added a new skill that audits `.claude/pv-context.json` and the installed framework files for drift — broken configuration, missing folders, duplicate change codes, mismatched skill versions, stale `pv.py`, corrupted document labels — and automatically fixes everything it can determine safely, asking the user only when the fix would be a guess (invalid JSON, or a suspected downgrade).
- 📂**Framework documentation**:
  - **User guide documentation** — `pv-doc`: added a bilingual (English/Spanish) end-user guide describing how to use the `pv-*` framework, previously undocumented outside the skills themselves.
  - **Style-bible writing guidance** — `pv-internal-doc-style`: added a new shared skill that tells `pv-do` which style categories (writing, visual design, interaction, accessibility, reusable components) apply to a given change and what each must record, used when keeping the project's style bible in sync.
  - **Shared technical-documentation writing rules** — `pv-internal-doc-technical`: added a new shared skill defining the dense, AI-oriented writing conventions (fixed tags, tables, code blocks) that architecture and style-bible documentation must follow, invoked by `pv-do` and `pv-init` before drafting that content.
- **Codebase analysis on first initialization** — `pv-init`: when initializing on a project that already has source code, the skill now offers a choice between a minimal or complete analysis pass and generates real architecture, style, and feature documentation from the existing codebase, instead of only scaffolding empty placeholders.
- **Multi-language support** — `pv-init` and the framework at large: added configuration for the language the framework speaks to the user in chat, plus separate optional languages for in-progress change documents, the release changelog, feature documentation, and technical documentation, each falling back to the chat language if unset.
- **Framework version verification gate** — `pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-status`, `pv-todo`, `pv-version`: every user-invocable skill now checks, before doing anything else, that the installed framework's version matches what was last verified by `pv-update`, and refuses to continue (pointing the user to `pv-update`) if the configuration looks stale or blocked.
- **Todo entry deletion** — `pv-internal-workflow`: added a capability to delete a todo entry, exposed internally for cleanup after conversion.
- **Isolated changelog staging** — `pv-internal-changelog`: entries pending inclusion in a release are now staged into an isolated `closed/temp/` copy before drafting, so change/fix entries closed while the changelog is being written no longer interfere with that run; deletion of folded-in entries afterward no longer requires user confirmation, since the staged copy is provably safe to remove.

## ✏️Changed

- 📂**`workFolder` structure and paths**:
  - **`workFolder` default and configuration behavior changed** — `pv-init`: the framework's working folder now defaults to a fixed `/previo-sdd` path instead of the repo root, and is written silently without asking the user to confirm it (previously it was always asked/confirmed); a new `stuff/` fixed subfolder was added alongside `changes/`/`versions/`. Projects previously initialized at the repo root should re-run `pv-init`/`pv-update` to review the new layout.
  - **Technical/functional documentation paths now relative to `workFolder`** — `pv-init`: architecture, style-bible, and features documentation folders are now placed relative to `workFolder` instead of the repo root, aligning them with `changes/`/`versions/`. Existing configurations pointing outside `workFolder` need review via `pv-update`.
  - **Release build procedure file relocated** — `pv-version`: the project's build/compile procedure document moved from `{workFolder}/framework/how-to-compile-version.md` to `{workFolder}/stuff/how-to-compile-version.md`. Existing projects need to re-run `pv-update` (or manually relocate the file) after updating.
  - **Path resolution made consistent regardless of leading-slash formatting** — `pv-internal-workflow`, `pv-how`: `workFolder` values are now resolved the same way whether or not they carry a leading slash, avoiding inconsistent change-code collision checks (internal fix with no visible behavior change for correctly configured projects).
- 📂**`pv-status` reports**:
  - **Status report gained risk and version data** — `pv-status`: the general and filtered status reports now show each entry's assessed risk level and a running count of prepared versions; the general report also splits "in progress" entries into a distinct "ready to close" bucket alongside "planned, pending implementation" and "pending technical analysis." The report's own text (headings, labels) is now always rendered in English regardless of the user's configured chat language, since it's produced by deterministic scripts, not drafted prose.
  - **Terminal report width configurable** — `pv-status`: the plain-text terminal output used by `pv.py` now accepts a caller-specified column width instead of a fixed value.
- **Trivial-fix risk tolerance loosened slightly** — `pv-fix`: the "fast" (trivial) classification now tolerates a small amount of risk to the rest of the application instead of requiring exactly zero risk.
- **Technical/style documentation now written using shared style rules** — `pv-do`: when updating architecture or style-bible documentation after implementing a change, it now loads the shared writing conventions from `pv-internal-doc-technical` and, for the style bible specifically, consults `pv-internal-doc-style` for which categories apply, instead of drafting that content with no shared baseline.
- **Sequential code padding default increased** — `pv-init`: the default zero-padding width for change/fix codes increased, and the field is now always written explicitly to configuration instead of being left to an implicit default.
- **Skill model/effort baseline always recorded** — `pv-init`: the mapping of which Claude model/effort each `pv-*` skill runs with is now always written to `pv-context.json` (mirrored from each skill's actual frontmatter), even when the user customizes nothing, instead of being omitted when unused.
- **Broken or drifted configuration now delegated to `pv-update`** — `pv-init`: when it detects a problem beyond an unconfigured optional field (invalid JSON, a dangling reference, a stale `pv.py`), it now hands off diagnosis and repair to the new `pv-update` skill instead of attempting to fix it inline.
- **Translated framework prose to English** — nearly every `pv-*` skill: all skill instructions, message templates, and document templates (previously written in Spanish) were translated to English as the framework's baseline language, with document field labels using a new fixed-marker convention so they stay parseable regardless of the configured content language.
