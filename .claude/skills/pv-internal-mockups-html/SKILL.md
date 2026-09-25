---
name: pv-internal-mockups-html
description: Shared, project-agnostic procedure to create or edit static visual mockups in HTML (`design_*.html`) for a change/fix, each embedding a standard review-annotation framework (floating toolbar, pin-to-element notes, general/linked notes panels, show/hide, save). Actions: `create`/`edit` (destination folder + list of visual elements + optional style_context/language as input; paths of the resulting files plus `style_gaps` as output), `ensure-closed` (resolves any pending annotation on given design_*.html paths, applying the requested change and asking the reviewer directly if a note is ambiguous, returning OK plus `style_gaps` once none are left open), and `describe` (read-only plain-text description of a mockup's visual content, for a caller that needs a reference without opening the file itself). `style_gaps` lists any explicit style value it had to apply (from the caller or a note) that wasn't already covered by `style_context`, so the caller can flag it as a possible style-bible gap or correction. Doesn't decide which elements need a mockup, doesn't resolve its own style-bible/language context (the caller supplies it), and doesn't validate anything with the user beyond `ensure-closed`'s own note-resolution questions. Internal use by the pv-new and pv-fix skills (directly or from extend-entry.md) and pv-how, invoked by the name configured in `.claude/pv-context.json`'s `framework.skills.mockups` (by default, this same skill).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  author: Sergio José Martínez Primiani
  version: 0.9.8b13
  uses: []
---

# pv-internal-mockups-html

A single, shared procedure to generate the visual mockup (`design_*.html`) of a new or modified UI element, as self-contained static HTML/CSS/SVG. Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**Plugin isolation.** This skill is a self-contained plugin: copying only its own folder to another repo must let it create/edit/manage `design_*.html` at 100%. It never resolves its own context from disk or from `.claude/pv-context.json` — everything it needs comes from the caller as input, and its absence degrades gracefully (neutral styling, English sample text) rather than triggering a resolution of its own.

**Language.** This skill doesn't talk to the user for its `create`/`edit` actions. The mockup's sample text/content follows the `language` the caller passes as input (plain text, e.g. `"English"` or `"Spanish"`); if omitted, it defaults to English. This skill never reads `framework.changes.language`/`interaction.language` or `.claude/pv-context.json` itself — resolving that is the caller's job, consistent with the plugin-isolation rule above. The one exception to "doesn't talk to the user" is `action: ensure-closed`, which can ask the reviewer directly when a note is ambiguous (see that action below) — always in whatever language the conversation is already in, since that's a live turn, not generated file content.

**This skill doesn't decide which elements need a mockup, nor validate anything with the user.** That's always decided by the caller (typically `pv-new`/`pv-fix`, upon detecting the change has a visual component): this skill is only invoked once it's already known that generating or editing at least one HTML mockup is needed, never "just in case". Presenting the result to the user for confirmation is also the caller's responsibility.

This skill is specifically for **HTML** mockups. If a project configures another skill in `framework.skills.mockups` to use a different technology (e.g. Figma, a component library, images), that alternative skill must fulfill the same input/output contract described here so it can replace this one without `pv-new`/`pv-fix` needing to change anything.

## File inventory

- [`assets/mockup-annotations.html`](assets/mockup-annotations.html) — the master copy of the embedded annotation framework (marker comment + `<style id="mnoteqz7k-styles">` + `<script id="mnoteqz7k-runtime">`, plus an empty `#mnoteqz7k-data`). This skill never retypes any of it — see "Embed the annotation framework" below for how it lands in a `design_*.html`, verbatim, via a script rather than by hand.
- [`scripts/scaffold-mockup.py`](scripts/scaffold-mockup.py) — copies the asset, as-is, to a new `design_<description>.html` (renaming only the `<title>` and swapping the asset's own dev-only comment for a placeholder marking where the mockup's markup goes). Used by `action: create`'s first write — see "Steps" below. Fails without writing anything if the target file already exists.

## Expected input from the caller

- **Destination folder**: the path where the files should live, normally `{changesDir}/inProgress/{xxxx}/mockups/`. Every mockup file lives under `{destination folder}/mockups/`, never loose in the entry root — the caller is responsible for passing that subfolder, this skill just writes where it's told. Required for `create`/`edit`/`ensure-closed`/`describe`.
- **Action**: `create`, `edit`, `ensure-closed`, or `describe` — see "Steps" below for each one's own contract. `create`/`edit` share the same "List of visual elements" input; `ensure-closed`/`describe` instead take a list of `design_*.html` paths (see their own sections).
- **List of visual elements** (only for `create`/`edit`), one per mockup to create or edit. For each element:
  - **Brief description** of the element (used for the filename: `design_<element-description>.html`, e.g. `design_deck-selection-modal.html`, `design_progress-bar.html`).
  - **What it should show**: look, layout, sample content relevant to illustrate the result (the caller doesn't need to give low-level detail — exact colors, measurements — if it doesn't have it yet).
  - **Sub-action**: `create` (new file) or `edit` (a `design_*.html` with that name already exists in the destination folder and needs modifying) — in this second case, what changes relative to what's already there.
- **`style_context`** (optional, only for `create`/`edit`): plain text — already-resolved excerpts of the project's style bible (tokens/colors, typography, spacing, relevant conventions) that the caller gathered itself, normally already in hand from its own `pv-internal-tech-analysis` call before reaching this skill. If given, this skill reuses those concrete values verbatim instead of inventing them. If omitted (or empty), this skill never tries to resolve a style bible on its own — see "Rules for each mockup" below.
- **`language`** (optional, only for `create`/`edit`): plain text naming the language for the mockup's sample text/content (e.g. `"English"`, `"Spanish"`). Defaults to English if omitted. **Caller note**: this skill never resolves the project's language itself (see "Language" above) — if the caller has one (e.g. `framework.changes.language`) but forgets to pass it here, the mockup silently falls back to English instead of the project's actual language. Pass it explicitly whenever the caller already knows it.

## Rules for each mockup

Every `design_*.html` file is only a visual mockup, not a functional prototype:

- **It must replicate the app's documented visual identity when the caller supplied one.**
  This skill never resolves the style bible itself (see "Plugin isolation" above) — it only
  reuses what the caller already gathered:
  - If the caller passed `style_context`, reuse its concrete values (hex codes, `rem`/`px`
    values, token names) verbatim — don't approximate or invent alternatives.
  - If it didn't (or passed it empty), use sober neutral styling and note it at the top of
    the file: `<!-- No documented visual identity for <element>; neutral placeholder styling. -->`.
  - If the caller (via the element's "what it should show") or a mockup annotation explicitly
    asks for a concrete style value — a hex code, a `rem`/`px` measurement, a named token —
    that isn't already covered by `style_context`, apply it as asked (it's the most specific
    instruction available), but record it — see "Reporting style-bible gaps" below. This is
    distinct from the generic neutral-styling case above: it's not "no style given", it's
    "a real value given, but it didn't come from the documented style bible".

  The mockup stays self-contained (existing rule): copy the styling inline replicating the
  documented appearance — never link the real stylesheet or a CDN.
- It must show only the look (layout, styles, iconography) that element would have — no need for real data or logic, static sample content illustrating the result is enough.
- It must have no real functionality: no JavaScript reacting to events, no network calls, no state — **the one exception is the standard annotation framework copied verbatim from `assets/mockup-annotations.html`** (see "Embed the annotation framework" below); beyond that, the mockup contains no other JS, at most purely decorative JS if needed for the visual look.
- It must be self-contained: only HTML, CSS and SVG, all embedded in the file itself (no external files, no CDNs, no imports).
- One file per distinct visual element in the proposal — don't group several different elements into the same `design_*.html` unless the caller asked for them as a single unit.
- **Embed the annotation framework — via the scaffold script, never by hand.** The framework blocks are **never retyped, summarized, or "improved"** (same rule as `pv-init/SKILL.md`'s `assets/pv.py`: *"copied as-is without modifying a single line of it"*) — and, unlike that precedent, this skill doesn't even read-then-rewrite them itself:
  - **On `create`**: run `scripts/scaffold-mockup.py --dest <destination folder> --description <element-description>` **first**, before writing a single line of markup. It copies the asset verbatim into `design_<description>.html` (renamed title, the asset's own dev-only comment swapped for a placeholder marking where the mockup's markup goes) — the marker, `#mnoteqz7k-styles`, `#mnoteqz7k-runtime`, and an empty `#mnoteqz7k-data` all land byte-identical, at zero token cost, without this skill ever holding their content in its own context. Then edit that same file, replacing only the placeholder comment with the mockup's own markup (`style_context` if given, else neutral styling) — the framework blocks and `#mnoteqz7k-data` are never touched again after the script wrote them.
  - **On `edit` needing the framework refreshed** (see "Steps" below): the two blocks are small enough that reading the current ones from the asset and replacing just those two in the target file (leaving `#mnoteqz7k-data` untouched) is the right granularity — running the scaffold script here would overwrite the mockup's own markup, so it's `create`-only.
  - The mockup stays self-contained either way — the framework is embedded inline, never linked externally.
  - See "Steps" below for the exact three sub-cases this follows on `edit` (new file, older framework, embedded-and-current).

## Reporting style-bible gaps

Whenever this skill applies a concrete style value that didn't come from `style_context` —
because the caller's element description or a mockup annotation asked for it explicitly (see
"Rules for each mockup" above) — it tracks that as a **style gap**: a plain-text entry saying
which element/note asked for it, what value was applied, and (if inferable) what it seems to be
missing or contradicting in the style bible (e.g. "no documented token for this shade of green;
applied `#2ecc71` as requested for the confirm button" or "requested `12px` radius on cards,
style_context's `--radius-card` documents `8px` — possible correction needed").

This never happens for the generic neutral-placeholder case (no value was given at all, so
there's nothing to reconcile against the style bible) — only when a real, specific value was
supplied outside of `style_context`.

`create`/`edit` return this list as `style_gaps` alongside the file paths (empty list if none).
`ensure-closed` returns it the same way alongside its OK summary, scoped to gaps introduced
while resolving notes in that call. This skill never edits the style bible itself, never asks
the user about it, and never decides whether a gap is worth fixing — it only surfaces what it
noticed so the caller (or whoever owns `docs.tech.styleBibleDocDir`) can act on it. **Caller
note**: a non-empty `style_gaps` is only useful if the caller actually does something with
it — surface it to the user or pass it along to whoever maintains the style bible. Silently
discarding it defeats the entire point of tracking gaps in the first place.

## Steps

### `action: create` / `action: edit`

1. For each element in the received list:
   - **`create`**: no ID collision guard needed here — `design_<description>.html` doesn't exist yet by definition (if it does, that's an `edit`). Run `scripts/scaffold-mockup.py` first (see "Embed the annotation framework" above) to get the file with the framework already in place, byte-identical, at no token cost — it fails on its own, without writing anything, if the file somehow already exists, which surfaces the same "this shouldn't be a `create`" problem without needing a separate check. Then edit that same file, replacing only its placeholder comment with the mockup's own markup (HTML + CSS + SVG inline, no JS of its own), following the rules above (`style_context` if given, else neutral styling) — never touch the framework blocks or `#mnoteqz7k-data` the script already wrote.
   - **ID collision guard** (`edit` only). Before deciding which of the three `edit` sub-cases below applies, check whether the existing file has any element with `id="mnoteqz7k-styles"`, `id="mnoteqz7k-runtime"`, or `id="mnoteqz7k-data"`. If one exists, verify its **content shape** — not just the id's presence — is recognizable as the asset (the style block starts with the same rule set, the script starts with a `/* mnoteqz7k-framework vN — self-contained review-annotation runtime. */`-shaped header, matching the marker comment). If an id exists with unrecognized content (a `design_*.html` predating this framework that happens to reuse the same namespace), **stop and return the conflict to the caller** (which id, and that it holds unrecognized content) **without writing anything** — never silently overwrite it, and never treat it as "no framework present".
   - **`edit` sub-cases**, once the collision guard has cleared — what to touch depends on whether a recognizable framework is present and, if so, whether the asset's version is newer:

     | Framework in target file | Asset marker vs. target's | Mockup markup | Framework blocks (`#mnoteqz7k-styles`/`#mnoteqz7k-runtime`) | `#mnoteqz7k-data` |
     |---|---|---|---|---|
     | Absent (older mockup, or guard found nothing) | — | Edit for the requested change | Splice in verbatim from the asset (scaffold script doesn't apply — `create`-only) | Left as-is / created empty |
     | Present | Not newer | Edit for the requested change | Untouched | Untouched |
     | Present | Newer | Edit for the requested change | Replaced verbatim with the asset's current blocks | Untouched, no exceptions |

     A plain `edit` from a caller never changes or removes a note — resolving annotations is the exclusive job of `action: ensure-closed` below, regardless of which row applies.
2. Return to the caller, in the same turn: the list of created/edited file paths, one per element, plus `style_gaps` (see "Reporting style-bible gaps" below). Don't present anything to the user or ask for confirmation — that's the caller's job.

### `action: ensure-closed`

Input: a list of `design_*.html` paths (the ones the caller is about to (re-)present, or — for `pv-how` — every `design_*.html` in the entry). This is the **only** way any caller learns about or resolves annotations — no caller ever opens `#mnoteqz7k-data`, knows the `mnoteqz7k-*` namespace, or sees an individual note's selector or `open`/`closed` state directly.

For each path:
1. If the file doesn't exist, or has no recognizable framework embedded (per the same content-shape check as the collision guard above), skip it — never an error, never blocks the other paths in the same call.
2. Otherwise, parse `#mnoteqz7k-data` internally. If every note is already `state: "closed"` (or there are none), this path is done.
3. For each note with `state: "open"`:
   - If a linked note's stored selector no longer resolves ("detached"), treat it as a general note for this purpose.
   - If the skill can confidently decide what change the note is asking for, apply it directly to the mockup's own markup (same mechanism as an internal `edit` — no round-trip to the caller for this), then set that note's `state` to `"closed"` in `#mnoteqz7k-data` (nothing else in that note, or in the rest of the block, changes).
   - If the note is ambiguous enough that the skill can't confidently decide, **ask the user directly** — see "Talking to the user" below — before applying anything for that note; once answered, apply the change and close the note the same way.
4. Once every given path has zero `open` notes left, return **OK** plus a plain-text summary of what was changed per resolved note — no selectors, no raw JSON, no mention of `mnoteqz7k-*` or note ids — plus `style_gaps` (see "Reporting style-bible gaps" below) for any note resolved in step 3 that asked for an explicit style value outside `style_context`.

### `action: describe`

Input: a list of `design_*.html` paths and, optionally, which elements/areas the caller wants described. Read-only — never touches `#mnoteqz7k-data` or any note's state. This is the **only** way any caller accesses a mockup's visual content — no caller ever `Read`s a `design_*.html` file itself.

For each path, read its own markup (something only this skill ever does directly) and return a plain-text description of the requested elements' layout, styling, and iconography — enough for a caller like `pv-how` (or `pv-do`, drafting a style-bible update) to use as visual reference, without exposing the raw HTML/CSS/SVG or the `mnoteqz7k-*` framework blocks (irrelevant to that purpose). `navigation_*.md`/`data_*.md` are out of scope for this action — they live outside `mockups/`, aren't this skill's responsibility, and the caller keeps reading them with a plain `Read`.

### Talking to the user (only `ensure-closed`)

Unlike every other `pv-internal-*` skill (which are mute — they only exchange input/output with their caller), `ensure-closed` can ask the reviewer a question directly, in the same turn, when it hits a note it can't resolve unambiguously on its own. This is a deliberate, scoped exception: delegating an ambiguous note's resolution back through the caller would mean the caller has to understand and relay something about the mockup's annotations, breaking the encapsulation this whole design exists to enforce. No other action, and no other `pv-internal-*` skill, gets this exception.

### Versioning note

The asset's `<!-- mnoteqz7k-framework vN -->` marker is independent of this skill's own `metadata.version` — framework-release version bumps are handled by `/dev-generate-version`, not by bumping the marker by hand.
