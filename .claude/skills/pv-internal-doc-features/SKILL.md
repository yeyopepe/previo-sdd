---
name: pv-internal-doc-features
description: Shared, project-agnostic procedure defining what content a `docs.functional.featuresDocPathDir` entry must hold and how to write it, when that path is a folder (one file per feature, following `FEATURE.template.md`). Owns the domain rules — the content checklist for a feature entry (functional description, functional diagrams, `Available in`/`Code`/`Since`/`Last modified`, cross-links, the rule of never duplicating an entry, and the in-place-edit vs. new-entry criterion) plus its own writing rules — and delegates all file management (numbering, `INDEX.md`, `find`/`upsert`) to `pv-internal-doc-files`. Receives a summary of what was implemented and the context already gathered, and drafts the entry itself. Offers the same two actions to its caller: `find` (locate whether a feature already has its own entry) and `upsert` (draft and write a feature's final file). Internal use by the pv-do skill.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b2
  uses: [pv-internal-doc-files]
---

# pv-internal-doc-features

A single, shared procedure to organize `docs.functional.featuresDocPathDir` as a folder with one file per feature, instead of a single monolithic document — designed so that analyzing or updating one feature doesn't require reading the entire listing. Only invoked by `pv-do` (which writes this documentation after implementing a change/fix) — not meant for direct invocation by the user.

**Language.** This skill doesn't talk to the user directly. The content it writes to each feature file follows `docs.functional.language` (default `interaction.language`, English if neither is configured) — the caller (`pv-do`) tells it, since this skill doesn't read `.claude/pv-context.json` itself. The labels wrapped in `[[[...]]]` in `FEATURE.template.md` (`Area`, `Available in`, `Code`, `Since`, `Last modified`, and the `NNN` numeric prefix in the title) stay fixed in English always, regardless of `docs.functional.language` — write them without the brackets (see the "Marker convention in templates" section of `pv-design.en.md`). Only the free-text content following each label follows the configured language.

**This skill decides what the documentation says and how it's written.** Given a summary of what was implemented and the context already gathered (touched code, `plan.md`, functional diagrams/mockups available in the entry), it applies its own content checklist and writing rules (below) to draft the entry — including whether it's an in-place edit or a new entry, and which functional diagrams to carry over. It doesn't decide **where** or **how** it's stored on disk (numbering, `INDEX.md`, filename) — that's delegated to `pv-internal-doc-files`.

## Content checklist

Every feature entry must record:

- **Functional description** — one or more sentences/paragraphs describing the feature's current behavior: what it lets the user do and how it behaves. Never a changelog of what changed in this specific `xxxx` — always the full, faithful description of the resulting behavior, even on an in-place edit.
- **Functional diagrams (optional)** — carry over a diagram (as-is, never rewritten) when this entry's `description.md` has a functional Mermaid diagram (the kind `pv-new`/`extend-entry.md` generates), or the entry's folder has one or more `design_navigation_*.md`, and it represents a flow of the feature being documented. If two or more of those diagrams reference each other (one says "see diagram 1", or names a state/node defined in another), carry them over together, all or none — never leave a broken reference. Never carry over technical diagrams (internal flow, sequence between components) — those belong in `docs.tech.architectureDocDir`. If the feature already had its own diagrams from a previous version, keep them unless this change makes them outdated, in which case replace them instead of accumulating both.
- **`Available in`** — where it's seen/used (mode, screen, component...).
- **`Code`** — the complete list of `xxxx` codes that created or modified this entry, not just the new one.
- **`Since`** — date the entry was created (the first `xxxx`); never changes once assigned.
- **`Last modified`** — today's date, every time the entry goes through `upsert`.
- **Never duplicate an entry.** If what's being documented extends or modifies a feature that already has its own file, edit it in place so it keeps faithfully describing the current behavior — never create a second entry for the same feature.

## Writing rules

- Write for a **human**, functional reader — not for an AI, unlike `docs.tech.*` (`pv-internal-doc-technical`'s dense fact-fragment style doesn't apply here). Describe what the user can do, in plain descriptive prose.
- Never mention internal technical details (class/file names, architecture decisions, implementation choices) — that belongs in `docs.tech.architectureDocDir`, not here.
- Never write in changelog tone ("was added", "now allows"). Always present descriptive tense for the behavior as it stands today.
- Cross-links between features use the path relative to the destination file (`[text](NNN-other-slug.md)`), never `#` anchors — each feature lives in its own file.
- On an in-place edit, rewrite the description so it faithfully covers the full resulting behavior — don't just append the new bit to what was there before.

## Feature file shape

Given `docs.functional.featuresDocPathDir` (e.g. `docs/features/`), each `{NNN}-{slug}.md` file follows [`FEATURE.template.md`](FEATURE.template.md), with `# {NNN} — {Feature name}` and `**Area**: {Functional area}` written by `pv-internal-doc-files` (not by this skill) and the rest of the body assembled per the content checklist above, in the order the template lays out: functional description, functional diagrams (if any), `Available in`, `Code`, `Since`, `Last modified`.

## Expected input from the caller

The caller must give the `action` (`find` or `upsert`) and its own parameters (see below). If `docs.functional.featuresDocPathDir` isn't configured in `.claude/pv-context.json`, say so and stop — it's up to the caller to decide what to do (normally, skip the step without asking anything).

## Action `find`

Invoked by `pv-do` before drafting, to know whether the feature it's about to document already has its own entry.

Parameters: a brief description of the feature to look for (approximate name, area, or what it's about).

Delegate directly to `pv-internal-doc-files` (Skill tool) with `action=find`, `folder=featuresDocPathDir`, and the same description. Return its result to the caller as-is — this skill itself uses that result in `upsert` (below) to decide in-place edit vs. new entry, not the caller.

## Action `upsert`

Invoked by `pv-do` with a summary of what was implemented and the context already gathered — not with pre-drafted content. This skill drafts the entry itself.

Parameters:
- `summary` — brief description of what was implemented (the feature or behavior change) and where it's used/seen.
- `area` — functional area name (exactly as it should appear in `**Area**:` and group by in the index).
- `title` — feature name (exactly as it should appear as `# ...`); for an in-place edit, the existing title unless the change itself renames the feature.
- `context` — what's already gathered: the touched code, `plan.md`, and, if this entry's `description.md` has a functional Mermaid diagram or the entry's folder has `design_navigation_*.md` file(s), their content.
- `existing_file` — path returned by a previous call to `find`, if a matching entry was found; omitted if none was found.

Steps:

1. Apply the content checklist (above) to decide what this entry must say: read `existing_file`'s current content if present (this is an in-place edit — the description must end up covering the full resulting behavior, not just the new bit); decide which functional diagrams (if any) carry over, applying the joint-or-none rule for diagrams that reference each other, and never technical diagrams.
2. Draft the functional description and, if applicable, the `Available in` value, applying the writing rules (above).
3. **If there's an `existing_file`**: keep its original `- **Since**:` as-is (read it from the current content). Compute `- **Last modified**:` as today's date. Add this entry's `xxxx` (from `summary`/`context`) to the existing `- **Code**:` list if not already there.
4. **If there's no `existing_file`** (new feature): both `- **Since**:` and `- **Last modified**:` are today's date, and `- **Code**:` starts with this entry's `xxxx`.
5. Assemble `body` for `pv-internal-doc-files`, in order, per [`FEATURE.template.md`](FEATURE.template.md): the functional description, the functional diagrams (omit the section entirely if none), then `- **Available in**:`, `- **Code**:`, `- **Since**:`, `- **Last modified**:` with the values above.
6. Invoke `pv-internal-doc-files` (Skill tool) with `action=upsert`, `folder=featuresDocPathDir`, `area`, `title`, the assembled `body`, and `existing_file` if present.
7. Return the written file's path to the caller.

## Assets and scripts

- [`FEATURE.template.md`](FEATURE.template.md) — template for each feature file: number, area, functional description, optional Mermaid diagram, where it's used, associated `xxxx` code(s), and creation/last-modified dates.
- [`scripts/migrate-legacy-features-doc.py`](scripts/migrate-legacy-features-doc.py) — a one-off utility (not an invocable skill) that splits a monolithic `FEATURES.md` (`## Area` / `### Feature`) into one file per feature inside a folder, rewrites internal links, assigns sequential numbering, and regenerates `INDEX.md`; used to adopt the folder convention in a project that still had a single file.
