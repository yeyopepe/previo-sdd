---
name: pv-internal-doc-technical
description: Shared, project-agnostic procedure defining what content docs.tech.architectureDocDir must hold (a checklist of technical content categories — components, contracts, data flows, decisions, dependencies, data model, configuration) plus the shared writing style for both docs.tech.architectureDocDir and styleBibleDocDir — notation-first by default (prose is a tagged exception), fixed English tags including [gotcha] and [motivación], a single per-project namespace tree in {architectureDocDir}/00-namespace.md, and fixed technical English with no language option. Receives a summary of what's being documented and the context already gathered, and returns which architectureDocDir categories apply, what each must record, which are already covered versus pending, plus the writing rules to apply — without drafting content, deciding the document's structure, or writing anything itself. Internal use by pv-do.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b12
  uses: []
---

# pv-internal-doc-technical

A shared procedure covering both **what** `docs.tech.architectureDocDir` content must record and **how** to write it — plus, for `styleBibleDocDir`, the **how** only (the **what** for `styleBibleDocDir` belongs to `pv-internal-doc-style`, which extends this skill's writing baseline with its own checklist). Neither field gets a fixed template: each document's exact structure/sections stay free (unlike `pv-internal-doc-features`'s fixed fields) — this skill only fixes the catalog of content categories (for `architectureDocDir`) and the writing style (for both).

**This skill writes or edits nothing, nor does it draft any content.** For `architectureDocDir`, it states which content categories are relevant to what's being implemented, what each is expected to record, and which are already covered by the caller's context versus still pending to document. For both fields, it returns the writing rules to apply once the caller drafts the actual prose. Deciding each document's file/section structure, drafting the content, and writing it to disk is always the caller's job (`pv-do`).

**Language.** This skill's output and all `docs.tech` content is fixed technical English. There is no `docs.tech.language` option — architecture and style-bible documents are always English, regardless of `interaction.language` or the project's language elsewhere. The caller does not translate; it drafts in English. This skill doesn't talk to the user and doesn't read `.claude/pv-context.json` itself; category names and guidance returned to the caller are English internal framework vocabulary.

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
2. **Signatures, types, values and any structured datum (fields, defaults, optionality, ranges) as code/compact notation, never prose.** `field: type = default`, `?` for optional. `funcName(param: type) -> type` in a fenced or inline code span — not "the function receives a parameter and returns...", not "an optional parameter that defaults to 30 seconds".
3. **Tables for parallel structures.** Any list of items sharing the same shape (fields, endpoints, states, layers) goes in a table, not repeated paragraphs — a table strips the connective tissue and its columns scan faster than sentences. See *Notation-first* below for the full content→notation catalog.
4. **Prose is the exception.** Every piece of content maps to a native notation (see *Notation-first* below); prose is reserved only for an idiosyncratic external constraint that reduces to neither a condition nor a general engineering principle — one sentence, tagged `[motivación]`.
5. **Point at the source instead of duplicating its shape.** Reference `file:symbol` for exact structure. `pv-internal-tech-analysis` already falls back to the real code when a doc under-specifies something, so retyping a full class/schema here is redundant, not safer — and it's one more copy that can drift from the code. This rule and *Namespace* below are the same mechanism, not rivals: *Namespace* is how you cite ("by canonical path, whose node carries `anchor:` to the code"), this rule is why (the code, not the doc, holds the shape).
6. **Fixed English tags for recurring properties.** `[breaking]`, `[async]`, `[idempotent]`, `[deprecated]`, `[gotcha]`, `[motivación]`, etc. as literal prefixes: a closed, consistent vocabulary to pattern-match, instead of a sentence to re-parse every time — and immune to phrasing drift across edits. Same convention `pv-internal-doc-features` already uses for its structural field labels (`**Area**`, `**Since**`...), which also stay English regardless of the doc's language.
   - `[gotcha]` marks a fact that contradicts the default assumption a reader would bring from general software patterns (a `delete` that soft-deletes, a `getX` that mutates, a sync-looking call that isn't). Reserve it for genuine anti-expectations, not for every noteworthy detail. `pv-internal-tech-analysis` raises its attention on `[gotcha]` lines — they correct its default model, so it must not treat them as one more row.
     ```
     BIEN: - [gotcha] deleteUser(id) does NOT remove the row — it sets active=false.
     MAL:  - deleteUser(id) marks the user inactive.
     ```
   - `[motivación]` marks the one surviving prose sentence when *Notation-first*'s checklist allows it (§ *Notation-first*, checklist step 4). One sentence, and still bound by rule 10 (no unquantified intensifier inside it).
7. **No introductions, summaries, or conclusions.** Skip "this document describes...", "in summary...". Start at the first fact, end at the last.
8. **Flat lists over nested paragraphs.** Prefer `-`/table structure over paragraph indentation — structure is cheap to parse, prose is not.
9. **No anaphora.** Never "this", "that field", "the former", "the above" when the exact name can be repeated. Repeating the identifier is cheaper for the reader than resolving a referent — and never wrong when two candidates are nearby. Style cost of repetition is not a concern (see *Audience*). When the referent has a namespace path (see *Namespace*), the repeated form is that canonical path; never an anaphora, never a synonym.
   ```
   BAD:  The token carries an expiry. This is checked on every request; if it has passed, the session ends.
   GOOD: token.exp is checked on every request. If time > token.exp, the session ends.
   ```
10. **No unquantified intensifiers.** Never "very fast", "fairly large", "rarely called", "significant overhead". Either give the figure (`p95 = 12ms`, `~400 rows`, `< 1 call/day`) or drop the claim entirely — an intensifier without a number is discarded as non-information on read, so writing it only costs tokens. This includes comparatives with no baseline ("slower", "heavier") unless the baseline is named. Without a figure the sentence is omitted whole, not softened.
    ```
    BAD:  This endpoint is very slow and is rarely called.
    GOOD: p95 = 2.4s. Called < 10 times/day.
    GOOD: (si no hay cifra) — omit the sentence.
    ```

## Notation-first

Native notation/format is the default for every kind of content. Prose is a rare exception.

Every piece of content maps to a native notation. Pick it from this catalog before writing a sentence:

| Content type | Native notation | Prose only when... |
|---|---|---|
| Boolean invariant / pre-post-condition | `assert <expr>` if runtime-checkable; else propositional logic (`pre:`, `post:`, `inv:`, `∧ ∨ ¬ → ⟹ ∀`) | Never (pure structure) |
| Data structure (fields, types, defaults, optionality) | Table or compact notation (`field: type = default`) — see below | Never |
| State machine / transitions | FSM or `(state, event) → state'` table | Never |
| Entity relationship / cardinality | ER diagram or `1---*`, `0..1` notation | Never |
| Temporal sequence / call flow | Sequence diagram (Mermaid) or ordered pseudocode | Never |
| Decision tree / nested conditionals | Boolean table or explicit tree | Never |
| Decision rationale | Rule/condition + comparison table | Only for an idiosyncratic external constraint (compliance, business) not reducible to a condition nor a general engineering principle |
| Side-effect flow | Numbered sequence / event→effect table | Only the single step whose ordering is externally-semantic (UX, business) |

**Nested notation**: if a notation needs to refer to another, cite it by its namespace path — never embed it inline.

**Diagrams**: the "Temporal sequence" and "Entity relationship" rows accept Mermaid. The framework has `pv-internal-tech-mermaid` (configurable via `framework.skills.diagrams`) to generate them — `pv-do` invokes it as it already does in other flows.

### Checklist before any prose sentence

```
Before writing any prose sentence:
  1. Is it a condition/rule?            → decision table or propositional logic.
  2. Is it one more metric of a comparison already tabulated?  → add a column.
  3. Is it a general engineering principle the reader already infers?  → write nothing.
  4. None of the above  → one sentence of prose, tagged [motivación].
Never force prose for elegance, reading flow, or because "it sounds like a trade-off".
```

### Invariants: executable vs declarative

| Question | Yes | No |
|---|---|---|
| Is there a program point where this condition can be checked with the values at hand? | `assert <expr>` | declarative `inv: …` |
| Does it quantify over an abstract set / talk about an FSM state / a non-observable global property? | — | declarative |

- Preferred form = `assert` whenever the criterion answers "yes"; the declarative form is a fallback, not an alternative style.
- If both coexist, the `assert` governs and the declarative one is marked as a restatement.
- Exact syntax is fixed by the `## Notation` section of `{architectureDocDir}/00-namespace.md`.

### Compact notation for structured data

The "Data structure" row of the catalog, made explicit because it applies in almost every task. This convention lives in the `## Notation` section of `00-namespace.md` (kept here provisionally until that file exists):

```
field: type                  required field
field?: type                 optional field
field: type = value          default value
field: type ∈ {a, b, c}      enum / allowed set
field: type [min..max]       range
```

Canonical example:

```
MAL:  el método recibe un parámetro opcional que, si no se especifica, toma el valor por defecto de 30 segundos
BIEN: timeout?: Duration = 30s
```

## Namespace

One name tree per project (§ single tree), segments separated by dots, aggregate to detail. Every element (concept or assertion) has one canonical path. Nodes with `anchor:` point at the code. The tree lives in `{architectureDocDir}/00-namespace.md`, one per project — style concepts (design tokens, components) hang off the `ui.*` branch of that same tree, `styleBibleDocDir` has no namespace file of its own.

```
auth.token.session                       concepto.  anchor: src/auth/token.ts#SessionToken
auth.token.session.exp                   concepto.  anchor: SessionToken.exp
auth.token.session.ttl                   concepto.  anchor: SESSION_TTL_SECONDS
auth.token.session.ttl.value = 3600      afirmación (escalar)
auth.token.session.refresh.rule:         afirmación (no escalar → bloque de notación)
    pre:  state ∈ {AUTHENTICATED, EXPIRED} ∧ now - token.exp < 7d
    post: token'.exp = now + auth.token.session.ttl.value
auth.decision.circuit-breaker-over-retry decisión.  sin ancla de código
ui.grid.columns = 16                     afirmación de estilo (mismo árbol)
```

| Element | Form | Rule |
|---|---|---|
| Node with code anchor | `path` + `anchor: file#symbol` | Canonical name **is** the path; definition lives in code. Uniqueness is structural: one term per concept, project-wide. |
| Leaf `path = value` | terminal segment `= <scalar>` | The citable unit across docs: `see auth.token.session.ttl.value`. One citation syntax project-wide, stable across edits. |
| Leaf `path:` + notation block | terminal segment `:` then a notation block (see *Notation-first* catalog) | For non-scalar assertions (a logic expression, a contract). Citable exactly like a `=value` leaf. |
| Branch `path.decision.<slug>` | reserved subtree | Assertion with no code anchor (a design choice). Citable like a leaf. Rationale goes as a `[motivación]` line or a comparison table under the node — never bare prose next to the `decision.` marker. |
| Node with no anchor and no `=` / `:` | — | **Suspicious**: missing anchor, or general knowledge that shouldn't be named. |

Concept/assertion boundary is **syntactic**: has `= value`, `:` + block, or hangs off `.decision.`? → assertion. Otherwise → concept. No judgment.

**Segment order**: aggregate to part, module to detail. `<área>.<agregado>.<entidad>.<campo-o-afirmación>`.

- `auth.token.session.exp` ✅ (área auth → agregado token → entidad session → campo exp)
- `auth.session.token.exp` ❌ (inverts aggregate and entity)

`pv-do` assigns paths when documenting, following this order; on real ambiguity `pv-do` asks the user (same as it already does for interface doubts in `pv-internal-tech-analysis`).

**Cite any concept or assertion by its canonical namespace path, never re-describe it.**

Refactoring code (rename symbol → rename path) is a manual path reassignment. `pv-update` detects a broken anchor (`namespace-anchor-broken:*`) but does not repair it: it cannot know which new symbol replaced the old one.

## Fixed language: technical English

`docs.tech` is technical English, with no language option. Because the language is fixed, density techniques that rely on English grammar are permitted here — techniques that would be forbidden in a portable, any-language document:

- **Telegraphic/headline compression is allowed** (`user token expired`). English tolerates dropping articles/prepositions/verbs in a headline; the language being fixed, that compression is a valid technique. Only keep it legible — don't compress to the point of ambiguity.
- **Compound-noun stacking is allowed** (`user auth token expiry check`) as a valid density technique.
- Everything else in the writing rules (fragments over narrative, code over prose, tables, omission of the obvious, pointing at source, fixed English tags, no framing text, flat structure, no anaphora, no unquantified intensifiers) is structural, and applies as written.

## Domain terms with no standard English translation

`docs.tech` is English, but a business concept may have no standard English term (e.g. Spanish tax domain: "recargo de equivalencia"):

- If the concept **has a code symbol**, its namespace path uses the symbol name (already in the language it was coded in).
- If it **has no code symbol**, the slug may stay in the project's language for that one node (`billing.recargo-equivalencia`), documented as an **explicit exception** in `00-namespace.md` with a one-line note of the approximate English.
- Any `[motivación]` prose alongside it stays English (may name the term in quotes: `[motivación] "recargo de equivalencia" is a Spanish tax surcharge; no standard English term.`).
