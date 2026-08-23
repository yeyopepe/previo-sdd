---
name: pv-internal-doc-features
description: Shared, project-agnostic procedure to keep `docs.functional.featuresDocPathDir` up to date when that path is a folder (one file per feature, following `FEATURE.template.md`). Owns the domain rules — the fields specific to a feature entry (`Available in`/`Code`/`Since`/`Last modified`), functional diagrams, cross-links, and the rule of never duplicating an entry — and delegates all file management (numbering, `INDEX.md`, `find`/`upsert`) to `pv-internal-doc-files`. Offers the same two actions to its caller: `find` (locate whether a feature already has its own entry) and `upsert` (write a feature's final file, already drafted by the caller). Internal use by the pv-do skill.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b1
  uses: [pv-internal-doc-files]
---

# pv-internal-doc-features

A single, shared procedure to organize `docs.functional.featuresDocPathDir` as a folder with one file per feature, instead of a single monolithic document — designed so that analyzing or updating one feature doesn't require reading the entire listing. Only invoked by `pv-do` (which writes this documentation after implementing a change/fix) — not meant for direct invocation by the user.

**Language.** This skill doesn't talk to the user directly. The content it writes to each feature file follows `docs.functional.language` (default `interaction.language`, English if neither is configured) — the caller (`pv-do`) tells it, since this skill doesn't read `.claude/pv-context.json` itself. The labels wrapped in `[[[...]]]` in `FEATURE.template.md` (`Area`, `Available in`, `Code`, `Since`, `Last modified`, and the `NNN` numeric prefix in the title) stay fixed in English always, regardless of `docs.functional.language` — write them without the brackets (see the "Marker convention in templates" section of `pv-design.en.md`). Only the free-text content following each label follows the configured language.

**This skill doesn't decide what the documentation says.** It doesn't draft functional descriptions nor decide whether an existing feature's behavior changed — that's always `pv-do`'s job, which already knows the implemented change. This skill knows the **domain shape** a feature entry must have (which fields, in what format) and builds the `body` accordingly, but delegates **where** and **how** it's stored on disk (numbering, `INDEX.md`, filename) to `pv-internal-doc-files`.

## Feature file shape

Given `docs.functional.featuresDocPathDir` (e.g. `docs/features/`), each `{NNN}-{slug}.md` file follows [`FEATURE.template.md`](FEATURE.template.md):

- `# {NNN} — {Feature name}` and `**Area**: {Functional area}` — written by `pv-internal-doc-files`, not by this skill (see below).
- Functional body (one or more sentences/paragraphs).
- Functional diagrams (optional) — zero or more ```mermaid``` blocks, each representing a flow/use case for this feature from the user's point of view. Never technical diagrams (internal flow, sequence between components): those live in the technical documentation, not here.
- `- **Available in**: ...`
- `- **Code**: {xxxx}, {xxxx}, ...` — all the change/fix codes that created or modified this entry, not just the last one.
- `- **Since**: {YYYY-MM-DD}` — date this entry was created (the first `xxxx` in **Code**). Never changes once assigned.
- `- **Last modified**: {YYYY-MM-DD}` — date this entry was last edited (today, every time it goes through `upsert`).

Cross-links between features use the path relative to the destination file (`[text](NNN-other-slug.md)`), never `#` anchors — each feature lives in its own file.

## Expected input from the caller

The caller must give the `action` (`find` or `upsert`) and its own parameters (see below). If `docs.functional.featuresDocPathDir` isn't configured in `.claude/pv-context.json`, say so and stop — it's up to the caller to decide what to do (normally, skip the step without asking anything).

## Action `find`

Invoked by `pv-do` before drafting, to know whether the feature it's about to document already has its own entry (so it can edit it in place) or is new.

Parameters: a brief description of the feature to look for (approximate name, area, or what it's about).

Delegate directly to `pv-internal-doc-files` (Skill tool) with `action=find`, `folder=featuresDocPathDir`, and the same description. Return its result to the caller as-is.

## Action `upsert`

Invoked by `pv-do` with the content already fully drafted (this skill doesn't rephrase anything).

Parameters:
- `area` — functional area name (exactly as it should appear in `**Area**:` and group by in the index).
- `title` — feature name (exactly as it should appear as `# ...`).
- `body` — full functional description already drafted (one or more sentences/paragraphs, with cross-links already in `[text](other-slug.md)` format if applicable).
- `diagrams` — optional; the complete list of functional diagrams that should end up in the final file, each already as a complete ```mermaid``` block (if it's an in-place edit, the resulting list after adding/updating/removing as applicable, not just the new ones). Omitted or empty list if the feature has no functional diagram.
- `available_in` — content of the `- **Available in**:` line.
- `codes` — the complete list of `xxxx` codes that should end up in `- **Code**:` (if it's an in-place edit, the full resulting list after adding the new one, not just the new one).
- `existing_file` — path returned by a previous call to `find`, if this is an in-place edit; omitted if it's a new feature.

Steps:

1. **If there's an `existing_file`**: keep its original `- **Since**:` as-is (read it from the current content). Compute `- **Last modified**:` as today's date.
2. **If there's no `existing_file`** (new feature): both `- **Since**:` and `- **Last modified**:` are today's date.
3. Build `body` for `pv-internal-doc-files` by assembling, in order, per [`FEATURE.template.md`](FEATURE.template.md): the functional body, the functional diagrams (if `diagrams` is non-empty — omit the diagrams section entirely if empty or omitted), then `- **Available in**:`, `- **Code**:`, `- **Since**:`, `- **Last modified**:` with the values above.
4. Invoke `pv-internal-doc-files` (Skill tool) with `action=upsert`, `folder=featuresDocPathDir`, `area`, `title`, the assembled `body`, and `existing_file` if present.
5. Return the written file's path to the caller.

## Assets and scripts

- [`FEATURE.template.md`](FEATURE.template.md) — template for each feature file: number, area, functional description, optional Mermaid diagram, where it's used, associated `xxxx` code(s), and creation/last-modified dates.
- [`scripts/migrate-legacy-features-doc.py`](scripts/migrate-legacy-features-doc.py) — a one-off utility (not an invocable skill) that splits a monolithic `FEATURES.md` (`## Area` / `### Feature`) into one file per feature inside a folder, rewrites internal links, assigns sequential numbering, and regenerates `INDEX.md`; used to adopt the folder convention in a project that still had a single file.
