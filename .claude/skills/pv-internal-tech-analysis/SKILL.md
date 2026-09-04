---
name: pv-internal-tech-analysis
description: Shared, project-agnostic procedure to gather technical context before analyzing a change/fix or assessing whether a change is trivial. First reads the technical documentation configured in framework.docs.tech (architecture, style bible), and only explores the real code if more information is needed. If the topic touches any interface or data structure, requires having its complete definition (signature, input, return, fields) before considering the context gathered, and confirms with the user any definition doubt not resolved by documentation or code. If it detects that code and documentation don't match, flags the code as the source of truth and returns the inconsistency as part of the analysis. When done, checks the change against pv-internal-tech-security's security checklist and adds its pending items to the result. Edits nothing. Internal use by the pv-new, pv-fix and pv-how skills.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.6b14
  uses: [pv-internal-tech-security]
---

# pv-internal-tech-analysis

A single, shared procedure to obtain reliable technical context before making any decision about a change/fix (designing a solution, assessing root cause, or judging whether a change is trivial enough for `pv-fix`'s `fast` shortcut). Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**This skill writes or edits nothing.** It's purely analysis/reading: it gathers context and, if any, reports inconsistencies between documentation and code to the caller. What to do with those inconsistencies (update the document right away, note it for later, or use it as a reason to rule out a fast path) is always decided by the calling skill, per its own rules. The only exception to not interacting on its own is a specific one (see step 3): if a definition doubt remains that blocks having complete context, it confirms it directly with the user before returning the result.

**Language.** This skill writes nothing and doesn't normally talk to the user, so `language` doesn't apply to most of it — except step 3's user confirmation, which follows `framework.interaction.language` (default English; the caller has already resolved it before invoking this skill).

## Expected input from the caller

The caller must pass a brief summary of **what's being analyzed** (the specific change/fix/doubt, not the whole conversation) — used to scope step 2's code exploration, instead of exploring the entire repo aimlessly.

The caller may also pass `bootstrap: true`. `pv-init` passes it when it invokes this skill during its own scaffold (step 5.5), while `docs.tech` has just been created and holds only placeholder `INDEX.md` files. In that mode, **skip resolving `docs.tech` via `resolve-path.py`** (it would exit 4 — folder present but empty of real content, or scaffold still settling) and go straight to step 2, exploring `sourcecodeDir`. Nobody else passes it.

## 0. Load the project context

Read `.claude/pv-context.json` at the repo root (if you haven't already this session). Don't validate here that the framework is initialized — the calling skill has already checked that before invoking this one.

## 1. Read the existing technical documentation first

Before touching code, get the absolute paths of `architectureDocDir` and `styleBibleDocDir`. **Don't parse `pv-context.json` yourself** — call `resolve-path.py` for each (see pv-design's "Resolving paths"):

```
python .claude/skills/pv-init/scripts/resolve-path.py --what architectureDocDir
python .claude/skills/pv-init/scripts/resolve-path.py --what styleBibleDocDir
```

Each prints the absolute path on success. If either exits non-zero, **stop this analysis** and tell the caller the framework config is broken and the user must run `/pv-update` — do not try to locate the docs yourself, and never report this as a doc-vs-code inconsistency. (In `bootstrap: true` mode, skip these calls entirely — see "Expected input from the caller" — and go to step 2.)

- **If you already read a specific file earlier this session** and it hasn't changed since, don't reread it — reuse what you already have in context. This rule applies per individual file, not the whole directory: `architectureDocDir`/`styleBibleDocDir`'s documents are several small files, so in a typical cycle (invoked from `pv-new`/`pv-fix`, then again from `pv-how`) only `INDEX.md` needs rereading the second time, checking whether the already-read sibling files are still the relevant ones — reread only the missing ones, never the whole directory again. This is strictly more efficient than rereading a full monolithic file twice per cycle.
- For each of `architectureDocDir` and `styleBibleDocDir` (resolved above):
  1. Always read `{dir}/INDEX.md` first (if you don't already have it from this session).
  2. With the summary of what's being analyzed (received as input) and `INDEX.md`'s index table (what each sibling file covers), decide which sibling files are relevant and read only those.
  3. When in reasonable doubt about whether a file is relevant, read it — better to overshoot than fall short.
- A folder that `resolve-path.py` resolved successfully but that holds only its placeholder `INDEX.md` (no `{NNN}-*.md`) is fine: it just means nothing is documented for the touched area yet — note it and move on to step 2, where `sourcecodeDir` fills the gap. A resolution failure (any non-zero exit from `resolve-path.py`) is the broken-config case — stop and send the caller to `/pv-update`.

Return to the caller the list of documents configured in `.claude/pv-context.json` and which you found populated versus empty.

With this, build preliminary context (architecture/layers, style conventions, file and symbol map) before reading a single line of source code.

**How `docs.tech` content is written now** (applies while reading it in this step):

- The content comes in notation — `pre:`/`post:` contracts, FSMs, decision tables, `assert` expressions, compact `field: type = default` — not narrative prose. Parse it as such; don't expect explanatory sentences.
- When the content cites a **namespace path** (e.g. `auth.token.session.ttl.value`), resolve it against `{architectureDocDir}/00-namespace.md` (the single per-project tree, resolved the same way even when the citing document is under `styleBibleDocDir`). If the resolved node has an `anchor:`, that anchored code is the canonical definition and prevails over any wording — consistent with "code is the source of truth" (step 4).
- Raise attention on `[gotcha]` lines: each one corrects a default assumption from general software patterns, so it can't be skimmed as one more fact.

## 2. Fill in with real code only if needed

If step 1's context already resolves what the caller needs to know, don't explore any more code. If information is missing (the docs are still just placeholders, what's there doesn't cover the topic, or the caller needs to confirm a specific implementation detail), explore **only the part of the code relevant to the given topic** — starting from `sourcecodeDir` (get its absolute path with `python .claude/skills/pv-init/scripts/resolve-path.py --what sourcecodeDir`; if that exits non-zero, stop and send the caller to `/pv-update`).

## 3. Completeness of interfaces and data structures

If the analyzed topic involves any **interface** (HTTP endpoint, public function/method, event, message between components, contract between layers) or **data structure** (model, schema, table, DTO, type), the context isn't complete with a generic summary — the exact definition is needed:

- **Interface**: exact path/name, verb or invocation form, every input parameter (name, type, whether required/optional), the complete shape of the output/return (fields and types), and relevant error codes or failure cases if any.
- **Data structure**: all its fields, each one's type, constraints (nullability, keys, defaults) and relation to other structures, to the extent relevant to the analyzed topic.

This is the only exception to step 2's "don't over-explore": if what was read in steps 1-2 leaves a relevant interface or structure half-defined, go back and explore the code (or the documentation, if it has one) specifically until you have the complete definition — an approximate description isn't enough context to design against.

### Doubts neither documentation nor code resolve

If after this a genuine definition doubt remains (e.g. what an ambiguous field represents, what exact format a parameter expects, why an interface has a shape that's neither documented nor evident from the code) that neither `framework.docs.tech` nor the code clarify, don't accept it with a silent assumption: formulate the solution that seems most reasonable to you and confirm it with the user before considering the context gathered. This applies only to specific definition doubts blocking complete context — not to design decisions about the solution itself, which remain the responsibility of whoever invokes this skill.

## 4. Detecting inconsistencies: the code rules

While reading code during step 2, compare what you find against what step 1's documentation said (if any). If something doesn't match (a layer that no longer works as some `architectureDocDir` file describes, or a `styleBibleDocDir` convention the code no longer follows):

- The real code is always the source of truth, never what the document says.
- **Scope: an "inconsistency" here is strictly documentation *content* vs. code behaviour.** It is never a remark about how `pv-context.json` is *written*: `resolve-path.py` already returned the docs' absolute paths in step 1, so the paths are fine by definition — don't return "the `docs.*` paths look misconfigured" as an inconsistency. The one `pv-context.json`-related thing you *do* surface is handled in step 1, not here: a non-zero exit from `resolve-path.py` → stop and send the caller to `/pv-update`. Auditing `pv-context.json`'s full shape is `pv-update`'s job (`audit-context.py`), not this skill's.
- Don't fix the document yourself here. Add the inconsistency to the result you return to the caller (see below) as a pending documentation change, so that skill decides how and when to apply it (e.g. `pv-how` integrates it into its `plan.md`'s sections (c)/(d), which `pv-do` will apply in its documentation-update step; `pv-new`/`pv-fix` can note it in **Technical notes**; `pv-fix` can take it as a reason not to qualify as trivial for its `fast` shortcut).

## 5. Check against the security checklist

Before returning the result, invoke the `pv-internal-tech-security` skill (Skill tool) passing it the summary of what's being analyzed (the same input received) and the context already gathered in steps 1-4. That skill explores nothing on its own nor decides design: it only checks the change against its security category checklist and returns which ones apply and, of those, which are still pending review.

This step always runs, not only when the analyzed topic "sounds" security-related — apparently unrelated changes (UI, text, configuration) can incidentally touch a checklist category (e.g. a new form that does imply input validation). It's `pv-internal-tech-security` itself that decides which categories apply, not this skill.

## 6. Return the result to the caller

Don't draft any file. Return to the calling skill, in the same turn:

- **Gathered context** — the relevant summary for the given topic, already synthesized (don't paste the entire documents or the raw code), including the complete definition of any relevant interface or data structure from step 3.
- **Detected inconsistencies** — a list (empty if none) with, for each one: which document contains it, what it said, what the code actually shows, and the suggested documentation change.
- **Pending security points** — the "Categories pending review" list returned by `pv-internal-tech-security` in step 5 (empty if none). Don't include here the categories that skill marked as already covered — those need no action from the caller.

The caller decides what to do with each inconsistency and each pending security point (resolve it with the user, note it in `plan.md`, use it as a reason not to qualify as trivial); this skill doesn't intervene on that again.
