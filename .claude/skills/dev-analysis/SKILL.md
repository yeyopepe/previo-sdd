---
name: dev-analysis
description: Critically reviews a plan or any document handed to it, verifying every claim against the actual repo state rather than trusting what it's told, to surface bugs, inconsistencies, gaps, missing coverage, and unhandled edge cases. Trigger: /dev-analysis, or when the user asks to critically review/audit a plan or document.
argument-hint: "[path to the plan/document to analyze]"
model: claude-sonnet-5
effort: high
metadata:
  author: Sergio José Martínez Primiani
  version: 0.2.0
  uses: []
---

# dev-analysis

Critically reviews a plan or any document handed to it — **never modifies code**, and never writes anywhere except the report itself. Its job ends at surfacing causes; fixing them is always someone else's call, applied through a different skill.

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

## 3. Hunt systematically

Go through the document section by section and actively look for, specifically:

- **Bugs** — logic that's wrong, off-by-one conditions, incorrect assumptions about data shape or control flow, race conditions, state that isn't reset/cleaned up.
- **Inconsistencies** — the document contradicting itself across sections, or contradicting the repo's actual current behavior/conventions/naming.
- **Gaps** — steps or pieces implied as necessary (by the goal stated) but never actually specified: missing error paths, missing rollback/undo, missing tests, missing doc updates, missing config wiring.
- **Missing coverage** — callers, consumers, platforms (e.g. both OS variants if the project ships `install.sh`/`install.ps1`), languages (e.g. both `.en.md`/`.es.md` if the project keeps parallel translations), or scenarios the change should account for but the plan never mentions.
- **Unhandled edge cases** — empty/null input, first-run/no-prior-state, concurrent access, partial failure mid-operation, very large or malformed input, backward compatibility with existing data/files.

Don't stop at the first pass per section — a document can look complete on a skim and still be missing an entire dimension (e.g. it plans the code change but never the test, or plans one platform but not the other).

## 4. Write the report

Decide the destination first:

- **Target was a file** (an existing file the user handed you or referenced) → append the report as a new section directly onto that same file, don't create a separate report file. Use a clear heading such as `## Critical analysis` (or `## Análisis crítico` if the plan itself is in Spanish — match the document's own language), dated if the plan file already uses dates elsewhere. If the file already has a prior "Critical analysis" section from an earlier run, add a new dated section rather than overwriting the old one, so review history isn't lost.
- **Target wasn't a file** (pasted text, or the user is unsure where it should live) → **ask the user where to write the report** before writing anything — don't invent a location or default to a scratch file silently.

Then structure the report by section, mirroring the target document's own sections (or, if it has none, group findings by area/topic identified in step 3). Under each section heading, list its findings as a table with three columns:

| Finding | Explanation | Proposed improvement |
|---|---|---|
| short name | what's wrong + concrete repo evidence (file/line or exact repo state contradicting the document) | `—` |

**Leave "Proposed improvement" as `—` for every row.** This skill's core output is causes only — never invent fixes here. Order rows within a section by severity (things that would break something first, omissions last). If a section turns up no findings, say so plainly under its heading instead of an empty table. If the whole analysis turns up nothing, say that plainly instead of manufacturing findings.

## 5. Report the location

Tell the user exactly where the report landed — the file path, and the section/heading if it was appended to an existing document.

## 6. Offer a point-by-point walkthrough

Ask the user (❓ prefix, bold question) whether they want to go through the findings one by one together.

- **No** → stop here. The report stands as written, "Proposed improvement" columns untouched.
- **Yes** → walk the report's findings in order, section by section, row by row, one at a time:
  1. Present the finding's explanation (and its proposed improvement, if by some later run one was already filled in).
  2. Discuss it with the user — they may accept it as-is, reject it, refine the explanation, or work out a proposed improvement with you.
  3. If a fix is agreed, this is the only point where this skill fills in a **Proposed improvement**, and only for the row under discussion — still described as a proposal to evaluate, never applied to any code.
  4. Update that row in the report file to reflect the outcome (resolved/dismissed/refined, and any agreed proposed improvement) before moving to the next finding.
  5. Don't jump ahead or batch multiple findings together — sequential, one at a time, until every row has been through this.
