---
name: dev-analysis
description: Critically reviews a plan or any document handed to it, verifying every claim against the actual repo state rather than trusting what it's told, to surface bugs, inconsistencies, gaps, missing coverage, and unhandled edge cases — then, if the user wants, collaborates through the findings to bring the plan itself up to a quality bar, editing the plan document directly. Trigger: /dev-analysis, or when the user asks to critically review/audit a plan or document.
argument-hint: "[path to the plan/document to analyze]"
model: claude-sonnet-5
effort: high
metadata:
  author: Sergio José Martínez Primiani
  version: 0.7.0
  uses: [dev-onescript]
---

# dev-analysis

Critically reviews a plan or any document handed to it — **never modifies code, and never writes a plan from scratch**. It only ever works against a document that already exists. Surfacing causes is always the first job; if the user then wants to raise the plan's quality, this skill can also collaborate through the findings and edit the plan document itself (never the code it describes) — see step 8.

**Trust nothing the document or the user claims. Verify everything against the repo.** A plan saying "function X already validates Y" is a claim, not a fact — read `X` and confirm it actually does. A plan saying "this won't affect Z" is a claim — grep for every caller of what it touches and check. If the document and the repo disagree, the repo wins, and that disagreement is itself a finding.

## 1. Get the target document

- If the user passed a path (`argument-hint`) or pasted the plan directly, use that as the target.
- If the target isn't clear, **ask the user which document to analyze** — don't guess, don't pick the most recently modified file in `.claude/plans/`, don't assume.

Read the full target document before doing anything else.

## 2. Build ground truth from the repo, not from the document

For every claim, assumption, or reference in the document, verify it independently:

- **File/symbol references** — for every file, function, class, config key, or script the document names, open it and confirm it exists, exists where claimed, and behaves as described. A stale reference (renamed, moved, deleted, signature changed) is a finding.
- **Callers and dependents** — for anything the plan proposes to change, grep for every current caller/consumer across the repo (not just the ones the document mentions). An unlisted caller the plan would break is a finding.
- **Assumptions about current behavior** — anything the document asserts about how the system currently works ("X always does Y", "this is the only place Z happens") gets checked against the actual code, not accepted at face value.
- **External claims** — if the document cites a library's behavior, a framework convention, or documentation, verify against the vendored/installed source or the project's own docs in this repo where possible, rather than trusting the citation.

Do not ask the user to confirm facts that are verifiable by reading the repo. Only ask when the repo itself is ambiguous or silent on the question.

If verifying a claim requires actually running something rather than just reading code, `sandbox-test1/` is a disposable test environment — use it freely for that, never the real project.

## 3. Check the plan's required structure

Every plan document must carry this minimum set of sections, in this order:

1. **Title** — a top-level heading naming the plan.
2. **Index** — a table of contents with a link to each of the plan's own section headings. It it's not existent or stale, this skill will generate/update it automatically before doing anything else in this step.
3. **Objective** (or "Plan objective"/"Goal" if the document is in English — match the document's own language) — states what the plan achieves and why, up front.
4. *(the plan's own content — analysis, scope, technical sections, whatever the plan needs; not fixed by this rule)*
5. **Implementation plan** (or "Implementation plan" in English) — as the **last** section of the document, a concrete, ordered, checkable breakdown of what to actually do to execute the plan. It must go down to task-level detail and cover every element the plan's own analysis raised, not just a high-level summary — in particular, a task per document that needs changing (each `SKILL.md`, each workflow/hook/template file, each design/architecture doc, each translation twin) naming that exact file, plus a task for every other concrete element the analysis section(s) identified (scripts, config keys, data migrations, etc.). If the plan's analysis names a file or element as affected and "Plan de implementación" doesn't turn it into its own task, that's a gap, not an acceptable summary.
6. **Reviews** — history of reviews with the date and brief list of findings with brief descriptions. Findings will disappear from this section as they are resolved, but the date of each review remains for history. It must always be the last section of the plan — if it isn't, move it yourself.

Check the target document against this list before anything else. A missing section, a section present but not linked from the index, "Plan de implementación" not being the last section, or "Plan de implementación" omitting a task for something the analysis identified, is each its own finding — report them under a dedicated "Structure" heading in step 5's report, separate from the section-by-section findings. Don't let a structurally incomplete plan stop the rest of the analysis — keep going through steps 2/4/5 regardless, but the structural findings still get reported.


Note the distinction from step 7's own "Implementation detail" report section: that one is this skill's own post-walkthrough checklist of framework files touched, added to the *report*. "Plan de implementación" here is a section the *target plan itself* must already contain (or gets flagged for lacking), independent of whether a walkthrough ever happens.

## 4. When the document is a framework change plan

If the document plans a change to the `pv-*` framework itself, its technical section must be checked against every part of the framework it touches, not just the pieces it names:

- **Skills** — for every skill the plan mentions or implies (added, changed, removed), check whether the change belongs in `SKILL.md`, in its workflow file(s) (`workflow.*.md`, hooks, templates), or both. A plan that only mentions "update the skill" without saying which is an underspecified plan — flag it as a gap, don't guess on its behalf. Also check the skill's `assets/` folder (scripts, templates) for anything the plan's described behavior would require changing but doesn't mention.
- **Documentation** — check impact on any documentation the change touches: technical docs (`docs.tech.architectureDocDir`, `styleBibleDocDir`), the framework's own design docs (e.g. `pv-doc/pv-design-onescript/`), README/changelog files, or any other doc category present in the repo. A plan that changes behavior without a corresponding doc-update step is a gap.
- **`pv.py`** — if the plan touches `.claude/skills/pv-init/assets/pv.py` (or describes new/changed menu options, screens, or interactive behavior that would require touching it), that portion of the plan must be validated against the `dev-onescript` skill's rules (single-file constraint, the four screen helpers, single-extension-point rule, propagation to `test/pv-test.py`, and the requirement to update both `pv-design-onescript.en.md`/`.es.md`). Read `.claude/skills/dev-onescript/SKILL.md` and check the plan's `pv.py`-related steps against it; a `pv.py` change that skips propagation, doc updates, or violates the single-extension-point rule is a finding, not something to silently accept.

## 5. Hunt systematically

Go through the document section by section and actively look for, specifically:

- **Bugs** — logic that's wrong, off-by-one conditions, incorrect assumptions about data shape or control flow, race conditions, state that isn't reset/cleaned up.
- **Inconsistencies** — the document contradicting itself across sections, or contradicting the repo's actual current behavior/conventions/naming.
- **Gaps** — steps or pieces implied as necessary (by the goal stated) but never actually specified: missing error paths, missing rollback/undo, missing tests, missing doc updates, missing config wiring.
- **Missing coverage** — callers, consumers, platforms (e.g. both OS variants if the project ships `install.sh`/`install.ps1`), languages (e.g. both `.en.md`/`.es.md` if the project keeps parallel translations), or scenarios the change should account for but the plan never mentions.
- **Unhandled edge cases** — empty/null input, first-run/no-prior-state, concurrent access, partial failure mid-operation, very large or malformed input, backward compatibility with existing data/files.

Don't stop at the first pass per section — a document can look complete on a skim and still be missing an entire dimension (e.g. it plans the code change but never the test, or plans one platform but not the other).

## 6. Write the report

Decide the destination first:

- **Target was a file** (an existing file the user handed you or referenced) → append the report as a new section directly onto that same file, don't create a separate report file. Use a clear heading such as `## Critical analysis` (or `## Análisis crítico` if the plan itself is in Spanish — match the document's own language), dated if the plan file already uses dates elsewhere. If the file already has a prior "Critical analysis" section from an earlier run, add a new dated section rather than overwriting the old one, so review history isn't lost.
- **Target wasn't a file** (pasted text, or the user is unsure where it should live) → **ask the user where to write the report** before writing anything — don't invent a location or default to a scratch file silently.

Report the structural findings from step 3 first, under their own "Structure" heading. Then structure the rest of the report by section, mirroring the target document's own sections (or, if it has none, group findings by area/topic identified in step 5). Under each section heading, list its findings as a table with three columns:

| Finding | Explanation | Proposed improvement |
|---|---|---|
| short name | what's wrong + concrete repo evidence (file/line or exact repo state contradicting the document) | `—` |

**Leave "Proposed improvement" as `—` for every row at this stage.** This first pass's output is causes only — never invent fixes here; the "Proposed improvement" column only gets filled later, and only for rows the user actually works through in step 8. Order rows within a section by severity (things that would break something first, omissions last). If a section turns up no findings, say so plainly under its heading instead of an empty table. If the whole analysis turns up nothing, say that plainly instead of manufacturing findings.

## 7. Report the location

Tell the user exactly where the report landed — the file path, and the section/heading if it was appended to an existing document.

## 8. Offer a point-by-point walkthrough to raise the plan's quality

Ask the user (❓ prefix, bold question) whether they want to go through the findings one by one together to bring the plan up to a quality bar.

- **No** → stop here. The report stands as written, "Proposed improvement" columns untouched, and the plan document itself is untouched.
- **Yes** → walk the report's findings in order, section by section, row by row, one at a time. This is a genuine collaboration, not a rubber-stamp pass — bring your own judgment on what a good fix looks like, disagree with the user's first instinct when the repo evidence says otherwise, and don't settle for a fix that papers over the finding without resolving it:
  1. Present the finding's explanation (and its proposed improvement, if by some later run one was already filled in).
  2. Discuss it with the user — they may accept it as-is, reject it, refine the explanation, or work out a proposed improvement with you. Push back if a proposed fix is vague, contradicts something verified in step 2, or only partially addresses the finding — the goal is a plan that would actually survive execution, not just a shorter findings list. If the finding is a structural one from step 3 (missing/misplaced section), the "fix" is adding or moving that section in the plan document, following the required order.
  3. Once a fix is agreed, **apply it to the plan document itself** — edit the relevant section of the target document so the plan reads correctly going forward, not just a description of what to do. This is the one case where this skill writes outside the report; it still never touches code, only the plan document. If the target wasn't a file (step 1 was pasted text), there's no document to edit — keep the agreed fix in the report's "Proposed improvement" column only, and tell the user the updated plan text lives there since no source file exists to hold it.
  4. Fill in the **Proposed improvement** column for that row in the report too, describing what was changed and where, then update the row's status (resolved/dismissed/refined) before moving to the next finding.
  5. Don't jump ahead or batch multiple findings together — sequential, one at a time, until every row has been through this. If two findings turn out to be entangled (fixing one changes how another should be read), say so, resolve them together, and note both rows accordingly rather than forcing a strict sequence.

  Once every row has been through the walkthrough, if the target document is a framework change plan (see step 4) and at least one finding was accepted with a proposed improvement, add a final `## Implementation detail` section (`## Detalle de implementación` if the document is in Spanish) at the end of the report (not the plan document). List, as a plain checklist, every concrete file this implies touching, derived strictly from the accepted proposed improvements — e.g. `- [ ] .claude/skills/<skill>/SKILL.md`, `- [ ] .claude/skills/<skill>/workflow.<x>.md`, `- [ ] .claude/skills/pv-init/assets/pv.py (validate via dev-onescript)`, `- [ ] pv-doc/pv-design-onescript/pv-design-onescript.en.md` + `.es.md`. Don't add a file that no accepted finding actually implies changing, and don't add this section at all if no findings were accepted or the document isn't a framework change plan.

  When finished, tell the user plainly that the plan document itself was edited (not just the report) and summarize what changed, so they aren't surprised by a diff they didn't expect.
