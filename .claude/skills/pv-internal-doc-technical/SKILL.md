---
name: pv-internal-doc-technical
description: Shared, project-agnostic procedure defining what content docs.tech.architectureDocDir must hold (a checklist of technical content categories — components, contracts, data flows, decisions, dependencies, data model, configuration) plus the shared writing style for both docs.tech.architectureDocDir and styleBibleDocDir (dense fact fragments, tables, code spans, fixed English tags). Receives a summary of what's being documented and the context already gathered, and returns which architectureDocDir categories apply, what each must record, which are already covered versus pending, plus the writing rules to apply — without drafting content, deciding the document's structure, or writing anything itself. Internal use by pv-do.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b3
  uses: []
---

# pv-internal-doc-technical

A shared procedure covering both **what** `docs.tech.architectureDocDir` content must record and **how** to write it — plus, for `styleBibleDocDir`, the **how** only (the **what** for `styleBibleDocDir` belongs to `pv-internal-doc-style`, which extends this skill's writing baseline with its own checklist). Neither field gets a fixed template: each document's exact structure/sections stay free (unlike `pv-internal-doc-features`'s fixed fields) — this skill only fixes the catalog of content categories (for `architectureDocDir`) and the writing style (for both).

**This skill writes or edits nothing, nor does it draft any content.** For `architectureDocDir`, it states which content categories are relevant to what's being implemented, what each is expected to record, and which are already covered by the caller's context versus still pending to document. For both fields, it returns the writing rules to apply once the caller drafts the actual prose. Deciding each document's file/section structure, drafting the content, and writing it to disk is always the caller's job (`pv-do`).

**Language.** This skill doesn't talk to the user and doesn't read `.claude/pv-context.json` itself. Category names and guidance returned to the caller are in English, as internal framework vocabulary — the caller translates as needed when drafting into `docs.tech.language`. The fixed English tags in the writing rules (rule 6 below) stay in English regardless of `docs.tech.language`.

**Relationship with `pv-internal-doc-style`.** Complementary, not overlapping: this skill's checklist (below) only covers `architectureDocDir` — code-level architecture, not style/UI conventions. `pv-internal-doc-style` owns the **what** for `styleBibleDocDir` entirely and extends this skill's writing rules with its own style-specific additions; it still invokes this skill for the shared baseline.

## Audience: these documents are for me, not for a human

`docs.tech` exists to be read by `pv-internal-tech-analysis` and, from there, by `pv-do`/`pv-how` in future cycles — not by a person browsing the repo. That changes what "clear" means: dense and fact-first beats narrative and explanatory. Every sentence that could be a fragment, and every fragment that could be a table row, is wasted context.

## Expected input from the caller

- A brief summary of **what's being implemented/documented** (the specific change/fix, not the whole conversation).
- The **context already gathered** so far (touched code, `plan.md`, existing `architectureDocDir` files for the touched area) — to avoid repeating exploration already done, and to mark a category as already covered when the context makes that clear.

This input/checklist mechanic (below) applies only when the caller is drafting for `architectureDocDir`. If the caller is only invoking this skill for `styleBibleDocDir`'s shared writing baseline, skip straight to "Writing rules".

## 1. The category checklist

For each category, assess two things: (a) whether it's **applicable** to what's being documented (most changes only touch one or two categories, not all of them) and (b) if applicable, whether the caller's context already makes clear how it's resolved, or whether it's **pending to document**. All categories always apply to any project (no presentation-layer gate, unlike `pv-internal-doc-style`).

| Category | What to check |
|---|---|
| Components and responsibilities | Does the change add/modify a component, module or service with its own responsibility not already documented? |
| Contracts and public interfaces | Does it add/change a public signature, API, endpoint or extension point other code consumes? |
| Data flows between components | Does it change how information moves or transforms between two or more already-documented components? |
| Technical decisions and discarded alternatives | Is there a non-obvious design choice (why this and not the obvious option) that would be lost if not recorded? |
| External dependencies | Does it introduce/change a library, external service, or version the project now depends on? |
| Data model / persistence | Does it add/change an entity, schema, migration, or invariant of the persisted data? |
| Configuration and environment integration | Does it add/change an environment variable, flag, config file, or deployment requirement? |

Note: "Components and responsibilities" is about code-level architecture (modules, services), not UI. Reusable UI components / design system is `pv-internal-doc-style`'s category, not this one.

## 2. Check against the received context

For each category marked applicable in step 1:

- If the caller's context already makes clear how that category is addressed for this change — e.g. it reuses an already-documented component/contract, follows a pattern `architectureDocDir` already records — don't mark it as pending: flag it as **covered**, in one sentence, citing the specific existing convention that resolves it.
- If the context doesn't make it clear, or the change introduces something new with nothing already documented to follow, mark it as **pending to document**, with a sentence on what specifically needs recording.
- Don't over-explore code just to resolve this: if deciding needs more digging than the context already gathered, that itself is a sign the category stays pending — not a reason to launch additional exploration on your own.

## 3. Return the result to the caller

Don't draft any file nor show anything to the user directly. Return to the caller, in the same turn:

- **Applicable categories covered**: a list (can be empty) of `{category}: {why it's already resolved}`.
- **Categories pending to document**: a list (empty if none) of `{category}: {what needs recording}`.
- **Writing rules** below, for the caller to apply verbatim while drafting.
- Categories not applicable aren't even mentioned in the result.

The caller decides what to do with the pending items (document them now as part of this change, note them for later, or judge that they don't warrant documentation) — this skill doesn't intervene on that again, nor does it check back after the caller writes.

## Writing rules

Apply to both `docs.tech.architectureDocDir` and `styleBibleDocDir` content:

1. **One fact per line, no connective narrative.** Cut framing phrases ("this allows...", "in order to...", "it's worth noting that..."). State the fact directly.
2. **Signatures, types and values as code, never described in prose.** `funcName(param: type) -> type` in a fenced or inline code span — not "the function receives a parameter and returns...".
3. **Tables for parallel structures.** Any list of items sharing the same shape (fields, endpoints, states, layers) goes in a table, not repeated paragraphs — a table strips the connective tissue and its columns scan faster than sentences.
4. **Don't restate what a signature or name already says.** Reserve prose for what code doesn't show: invariants, side effects, rationale, edge cases, non-obvious decisions.
5. **Point at the source instead of duplicating its shape.** Reference `file:symbol` for exact structure. `pv-internal-tech-analysis` already falls back to the real code when a doc under-specifies something, so retyping a full class/schema here is redundant, not safer — and it's one more copy that can drift from the code.
6. **Fixed English tags for recurring properties, regardless of `docs.tech.language`.** `[breaking]`, `[async]`, `[idempotent]`, `[deprecated]`, etc. as literal prefixes: a closed, consistent vocabulary to pattern-match, instead of a sentence to re-parse every time — and immune to phrasing drift across edits or languages. Same convention `pv-internal-doc-features` already uses for its structural field labels (`**Area**`, `**Since**`...), which also stay English regardless of the doc's language.
7. **No introductions, summaries, or conclusions.** Skip "this document describes...", "in summary...". Start at the first fact, end at the last.
8. **Flat lists over nested paragraphs.** Prefer `-`/table structure over paragraph indentation — structure is cheap to parse, prose is not.

## Language-independence

These rules must hold no matter what `docs.tech.language` resolves to, so anything whose compression relies on a specific language's grammar was deliberately left out:

- **No telegraphic/headline compression** (dropping articles, prepositions, or verbs to shorten a sentence). That's an English-specific technique — English tolerates a headline like "user token expired"; the equivalent grammatical dropping in other languages (e.g. Spanish) produces broken or ambiguous text, not a compressed one. Compress by **removing whole sentences that add no fact**, never by mutilating the grammar of the ones you keep — rule 1 achieves the same context reduction without this risk.
- **No compound-noun stacking** ("user auth token expiry check") to save words. It's a valid English construction but doesn't shorten equivalently in languages that need prepositions for the same relationship, so it isn't a reliable density technique across `docs.tech.language` values. Use rule 2 (code/signatures) or rule 3 (tables) instead when a relationship needs to be dense.
- Everything else above (fragments over narrative, code over prose, tables, omission of the obvious, pointing at source, fixed English tags, no framing text, flat structure) is structural rather than grammatical, so it transfers unchanged to any `docs.tech.language`.
