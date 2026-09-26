---
name: pv-review-doc-tech
description: Reviews every technical documentation folder configured under `framework.docs.tech` (today `architectureDocDir` and `styleBibleDocDir`, but works generically for any key present there) and improves its structure and organization only — moving misplaced content to the right file/category, merging duplicates, fixing wrong `**Area**` grouping. Never deletes, rewrites, or adds content. Trigger: /pv-review-doc-tech, or when the user asks to reorganize/clean up/restructure the technical documentation.
model: claude-sonnet-5
effort: medium
metadata:
  author: Sergio José Martínez Primiani
  version: 0.9.8b15
  uses: [pv-internal-doc-technical, pv-internal-doc-style, pv-internal-doc-files]
---

# pv-review-doc-tech

Reorganizes the content already written in `framework.docs.tech`'s folders — **structure only**. It never deletes a fact, never rewrites a sentence, never adds new content. Every fact that exists before this skill runs must still exist, verbatim, after it runs; only its *location* (which file, which section, which `**Area**`) may change.

**Language.** Use `framework.interaction.language` (default English) for everything you say to the user in this conversation. The documentation itself stays in whatever language it's already written in (`docs.tech` is always fixed technical English per its schema) — this skill never translates.

**This skill writes/edits only files inside the `docs.tech` folders it reviews.** It never touches source code, `changes/**`, `stuff/**`, or any other part of the repo.

**Work silently, but stop and ask on anything odd.** Don't narrate progress file by file or move by move — apply the reorganization and give one final report (step 6). The one exception: if while reading (step 2) or deciding (step 3) you find an inconsistency or something that doesn't add up — a namespace collision, a fact that flatly contradicts another file, content that doesn't fit any category, anything that makes you unsure a move is safe — **stop and ask the user before changing anything**, instead of guessing, silently skipping it, or only mentioning it in the final report after having acted elsewhere. Keep applying the parts of the reorganization you're already sure about; only the doubtful item waits on the user's answer.

## Why reorganization needs its own pass

`docs.tech` isn't prose for a human to skim — it's the framework's own memory, read back by `pv-internal-tech-analysis` (and from there `pv-do`/`pv-how`) on every future change. Its structure directly determines how cheaply that future read finds the right fact:

- A fact filed under the wrong `**Area**`/category is invisible to a targeted read that trusts the grouping.
- The same fact stated in two files drifts the moment one of them is updated and the other isn't.
- A fact stranded in the wrong file's free-form body (instead of the category/section it actually belongs to) forces a full-file read instead of an index-guided jump.

Fixing these is a structural edit, not a content edit — which is exactly why this skill exists as a narrow, repeatable pass instead of being folded into `pv-do`'s per-change updates (which only ever touch the one topic just implemented, never the folder as a whole).

## How this documentation is created — read before reorganizing

This skill doesn't invent its own idea of "well organized". It reorganizes toward the same shape `pv-do` already builds *when it creates or updates content*, so review this pipeline before touching anything — every check in step 3 below is a check for whether a file already matches it or has drifted from it:

- **One file per topic, `find` before `upsert`.** `pv-do` never appends a second file for a topic that already has one: before drafting, it asks `pv-internal-doc-files`' `action=find` whether the topic already has an entry, and edits it in place if so. A folder that has drifted from this (two files covering the same topic, because two different changes each independently missed the existing one on `find`) is exactly the kind of duplicate step 3 must catch and consolidate.
- **Category checklists decide where content belongs, not free judgment.** `pv-do` doesn't file content wherever seems reasonable — it invokes `pv-internal-doc-technical` (for `architectureDocDir`: components, contracts, data flows, decisions, dependencies, data model, configuration) or `pv-internal-doc-style` (for `styleBibleDocDir`: writing/naming, visual tokens, layout, interaction, accessibility, components, microcopy) and follows what that checklist calls the content. Use the **same two checklists**, not your own reading of the topic, when judging in step 3 whether a file's `**Area**` and content actually match the category it claims.
- **Notation-first writing rules are what "internal disorder" means.** `pv-internal-doc-technical`'s writing rules (dense fact fragments, tables for parallel structures, fixed English tags like `[gotcha]`/`[motivación]`, no anaphora, no unquantified intensifiers, point at the source instead of duplicating it) are the target shape — not a generic prose cleanup. A file that has facts sitting in narrative prose where the catalog demands a table/notation block is disordered by this specific standard, not by generic writing taste.
- **The namespace tree is the cross-file skeleton.** `{architectureDocDir}/00-namespace.md` holds the single per-project tree of canonical paths (`area.aggregate.entity.field`), each citable exactly once project-wide; style concepts hang off its `ui.*` branch and `styleBibleDocDir` has no namespace file of its own. Two files both defining the same concept under different or ambiguous paths is a namespace violation, not just a content duplicate — flag it accordingly (see step 4, namespace changes are out of this skill's own edit scope).
- **`INDEX.md` is generated, `**Area**` groups it.** `pv-internal-doc-files`' `rebuild-index.py` builds the index purely from each file's `**Area**:` line — so correcting `**Area**` *is* correcting the index; there's no separate index-editing step.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root. If it doesn't exist, or is missing the `framework` section, stop and tell the user to run `pv-init` first.

```
This project doesn't have the `pv-*` framework initialized yet (or is missing configuration). Run `/pv-init` first before invoking me again.
```

Before continuing, check that `.claude/skills/pv-update/scripts/check-framework-status.py` exists. If it doesn't, tell the user the framework doesn't look correctly installed and that they must install the latest version (see `pv-update`'s "Install mode" — `/pv-update install`) — stop there, don't continue this skill's work.

If it exists, run it (`python .claude/skills/pv-update/scripts/check-framework-status.py`) and read its JSON. If `ok` is `false`, show `message` to the user and stop — no `pv-*` skill can continue its work without this step passing with `ok: true`.

## 1. Enumerate the folders to review

Read `framework.docs.tech` from `pv-context.json` directly — iterate over **every key present** under it (today `architectureDocDir` and `styleBibleDocDir`; treat any future key the same way, don't hardcode the two names in your reasoning). For each key, resolve its absolute path:

```
python .claude/skills/pv-init/scripts/resolve-path.py --what <key>
```

If resolution fails, stop for that key and send the user to `/pv-update` (same exit-code convention as every other `pv-*` skill) — don't skip it silently. A folder that resolves fine but holds only its placeholder `INDEX.md` has nothing to reorganize: skip it and mention it in the final summary, don't treat it as an error.

## 2. Read the whole folder before touching anything

For each resolved folder, **read everything before writing anything** — this is a whole-folder pass, not a file-by-file one:

1. Read `INDEX.md` to see the current grouping (`**Area**` categories and which files fall under each).
2. Read every `{NNN}-{slug}.md` file in full.
3. Read every `00-*.md` infrastructure file too (e.g. `00-namespace.md`) — you need it to know which paths/anchors exist, even though you never reorganize its content (see rule below).

Only after this full read, decide what (if anything) needs reorganizing. Acting on one file in isolation, without having read its siblings, is exactly how a duplicate goes unnoticed or a fact gets moved to a file that already covers it better elsewhere.

## 3. What to look for

Apply these checks across the whole folder, not per file in isolation:

- **Wrong `**Area**`**: a file's actual content doesn't match its declared `**Area**`, or overlaps more with another area's files than its own. Check against the category checklist the content actually belongs to — for `architectureDocDir` that's `pv-internal-doc-technical`'s categories (components, contracts, data flows, decisions, dependencies, data model, configuration); for `styleBibleDocDir`, `pv-internal-doc-style`'s (writing/naming, visual tokens, layout, interaction, accessibility, components, microcopy). Invoke the matching skill if you need to re-check which category a piece of content belongs to.
- **Duplicated or overlapping facts across files**: the same fact (same namespace path, same component/contract, same token) stated in more than one file — a sign two changes each ran `pv-do`'s `find` step and still landed in different files (near-duplicate topic naming, or `find` missing the existing match). Consolidate into the file whose topic/area it actually belongs to; the other occurrence becomes a cross-link (`[text](NNN-other-slug.md)`), never a second copy of the fact.
- **Same namespace path defined in two places, or a concept with no path that should have one**: cross-check moved/consolidated content against `00-namespace.md`'s tree. A concept documented under two different paths, or documented without ever being added to the tree, is a namespace violation — **ask the user** before consolidating it (see the silent-work rule above), don't silently pick one path yourself.
- **Content in the wrong file's body**: a paragraph/table/notation block that fits a *different existing file's* topic better than the one it's currently in (e.g. a data-model fact sitting inside a file about an unrelated component). Move it to the file it belongs to; leave a cross-link behind only if the original file's remaining content still needs to reference it.
- **Internal disorder within one file**: sections not following notation-first order (prose mixed in where a table/notation block would group facts of the same shape together — see `pv-internal-doc-technical`'s *Notation-first* catalog), or facts about the same sub-topic scattered non-contiguously through the file instead of grouped.
- **Stale or ambiguous cross-links**: a reference that pointed at content which itself moved during this same pass — fix the link's target as part of the move, don't leave it dangling.
- **`INDEX.md` grouping**: never edit it by hand — once file contents/`**Area**` are corrected, regenerate it (step 5).

## 4. Hard limits — what this skill must never do

- **Never delete a fact.** If a fact looks redundant, wrong, or outdated, that's a content judgment outside this skill's scope — leave it, and ask the user about it (silent-work rule above) rather than deciding on your own or silently leaving it for the final summary only.
- **Never rewrite a sentence's meaning**, reword for style, or "improve" phrasing. Moving a fact to a better-fitting notation (e.g. turning a stray prose sentence into the table row it should always have been, per `pv-internal-doc-technical` rule 3) is a structural fix and is in scope; changing what it *says* is not.
- **Never add new content**, including connective prose to make a moved fact "read better" in its new location, or a summary/introduction the file didn't have.
- **Never renumber a `{NNN}-{slug}.md` file or rename its filename.** The number is stable by design (`pv-internal-doc-files`) — other files' cross-links and, for `architectureDocDir`, `00-namespace.md`'s `anchor:` references may depend on the exact path. Moving content *out of* a file is fine; renumbering the file itself is not.
- **Never touch `00-*.md` files' content** (e.g. `00-namespace.md`). They're owned by `pv-do` directly, not by the per-file `upsert` convention this skill works within. If reorganization would require changing a namespace path or anchor, stop and ask the user (silent-work rule above) instead of editing it yourself.
- **Never hand-edit `INDEX.md`.** Only `rebuild-index.py` writes it.
- **Never touch a file outside the `docs.tech` folder being reviewed** — no source code, no `changes/**`.

## 5. Applying the reorganization

For each move/consolidation decided in step 3:

1. Edit the destination file to include the moved content, in the notation/section it belongs to (per `pv-internal-doc-technical`/`pv-internal-doc-style`'s writing rules — reorganizing is a chance to fix the notation shape, not the content).
2. Edit the source file to remove the content from its old location, replacing it with a cross-link only if the surrounding text still needs to point at it.
3. Keep each file's `# {NNN} — {title}` and `**Area**:` header lines as `pv-internal-doc-files`' convention requires — update `**Area**:` itself if that was the correction, but never touch the `{NNN}` number.
4. Once all edits to a folder are done, regenerate its index:
   ```
   python .claude/skills/pv-internal-doc-files/scripts/rebuild-index.py --folder <resolved-folder-path>
   ```

## 6. Final summary to the user

Once every folder from step 1 has been processed, close with a single final summary — not a running commentary during the pass (see the silent-work rule above). Structure it **one block per `docs.tech` folder reviewed**, in this order:

- The folder's resolved path and key (e.g. `docs/architecture` — `architectureDocDir`).
- If nothing needed reorganizing: say so in one line and move to the next folder.
- If it was skipped for being empty (only its placeholder `INDEX.md`): say so in one line and move to the next folder.
- Otherwise, the list of moves/consolidations applied in that folder, one line each (what moved, from where to where, why — e.g. "merged duplicate `SESSION_TTL` fact from `003-auth.md` into `005-sessions.md`, where it already lived under the right `**Area**`").
- Anything from that folder you stopped to ask about (step 3/4) and how it was resolved.

Don't repeat the full diff — the edits are already visible in the working tree. If every folder had nothing to reorganize, say that plainly instead of forcing the per-folder structure on an empty result.

Baseline shape (adapt the content and language if needed, keep the structure):

```
## docs/architecture (architectureDocDir)
- Merged duplicate `SESSION_TTL` fact from 003-auth.md into 005-sessions.md (already the right **Area**); left a cross-link in 003-auth.md.
- Moved the retry-policy table from 004-http-client.md's body into 002-resilience.md, whose **Area** it actually matches.
- Corrected 007-cache.md's **Area** from "Data model" to "Configuration" to match its content.
- Asked about: 006-billing.md and 009-invoicing.md both define `billing.recargo-equivalencia` under different namespace paths — resolved by [user's answer].

## docs/style (styleBibleDocDir)
- Nothing needed reorganizing.

## docs/<future-key> (<futureKey>)
- Skipped: folder only has its placeholder INDEX.md, nothing to reorganize yet.
```

If literally every folder had nothing to reorganize, skip the per-folder blocks and just say so in one line.
