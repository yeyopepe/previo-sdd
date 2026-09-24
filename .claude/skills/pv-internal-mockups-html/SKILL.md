---
name: pv-internal-mockups-html
description: Shared, project-agnostic procedure to create or edit static visual mockups in HTML (`design_*.html`) for a change/fix, each embedding a standard review-annotation framework (floating toolbar, pin-to-element notes, general/linked notes panels, show/hide, save). Actions: `create`/`edit` (destination folder + list of visual elements + optional style_context/language as input; paths of the resulting files as output), `ensure-closed` (resolves any pending annotation on given design_*.html paths, applying the requested change and asking the reviewer directly if a note is ambiguous, returning OK once none are left open), and `describe` (read-only plain-text description of a mockup's visual content, for a caller that needs a reference without opening the file itself). Doesn't decide which elements need a mockup, doesn't resolve its own style-bible/language context (the caller supplies it), and doesn't validate anything with the user beyond `ensure-closed`'s own note-resolution questions. Internal use by the pv-new and pv-fix skills (directly or from extend-entry.md) and pv-how, invoked by the name configured in `.claude/pv-context.json`'s `framework.skills.mockups` (by default, this same skill).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  author: Sergio José Martínez Primiani
  version: 0.9.8b8
  uses: []
---

# pv-internal-mockups-html

A single, shared procedure to generate the visual mockup (`design_*.html`) of a new or modified UI element, as self-contained static HTML/CSS/SVG. Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**Plugin isolation.** This skill is a self-contained plugin: copying only its own folder to another repo must let it create/edit/manage `design_*.html` at 100%. It never resolves its own context from disk or from `.claude/pv-context.json` — everything it needs comes from the caller as input, and its absence degrades gracefully (neutral styling, English sample text) rather than triggering a resolution of its own.

**Language.** This skill doesn't talk to the user for its `create`/`edit` actions. The mockup's sample text/content follows the `language` the caller passes as input (plain text, e.g. `"English"` or `"Spanish"`); if omitted, it defaults to English. This skill never reads `framework.changes.language`/`interaction.language` or `.claude/pv-context.json` itself — resolving that is the caller's job, consistent with the plugin-isolation rule above. The one exception to "doesn't talk to the user" is `action: ensure-closed`, which can ask the reviewer directly when a note is ambiguous (see that action below) — always in whatever language the conversation is already in, since that's a live turn, not generated file content.

**This skill doesn't decide which elements need a mockup, nor validate anything with the user.** That's always decided by the caller (typically `pv-new`/`pv-fix`, upon detecting the change has a visual component): this skill is only invoked once it's already known that generating or editing at least one HTML mockup is needed, never "just in case". Presenting the result to the user for confirmation is also the caller's responsibility.

This skill is specifically for **HTML** mockups. If a project configures another skill in `framework.skills.mockups` to use a different technology (e.g. Figma, a component library, images), that alternative skill must fulfill the same input/output contract described here so it can replace this one without `pv-new`/`pv-fix` needing to change anything.

## File inventory

- [`assets/mockup-annotations.html`](assets/mockup-annotations.html) — the master copy of the embedded annotation framework (marker comment + `<style id="mnoteqz7k-styles">` + `<script id="mnoteqz7k-runtime">`, plus a standalone demo shell so the file can be opened on its own). This skill splices only those two blocks (and the marker) verbatim into every `design_*.html` it creates or edits — see "Embed the annotation framework" below. Never re-typed, summarized, or edited to "improve" it.

## Expected input from the caller

- **Destination folder**: the path where the files should live, normally `{changesDir}/inProgress/{xxxx}/mockups/`. Every mockup file lives under `{destination folder}/mockups/`, never loose in the entry root — the caller is responsible for passing that subfolder, this skill just writes where it's told. Required for `create`/`edit`/`ensure-closed`/`describe`.
- **Action**: `create`, `edit`, `ensure-closed`, or `describe` — see "Steps" below for each one's own contract. `create`/`edit` share the same "List of visual elements" input; `ensure-closed`/`describe` instead take a list of `design_*.html` paths (see their own sections).
- **List of visual elements** (only for `create`/`edit`), one per mockup to create or edit. For each element:
  - **Brief description** of the element (used for the filename: `design_<element-description>.html`, e.g. `design_deck-selection-modal.html`, `design_progress-bar.html`).
  - **What it should show**: look, layout, sample content relevant to illustrate the result (the caller doesn't need to give low-level detail — exact colors, measurements — if it doesn't have it yet).
  - **Sub-action**: `create` (new file) or `edit` (a `design_*.html` with that name already exists in the destination folder and needs modifying) — in this second case, what changes relative to what's already there.
- **`style_context`** (optional, only for `create`/`edit`): plain text — already-resolved excerpts of the project's style bible (tokens/colors, typography, spacing, relevant conventions) that the caller gathered itself, normally already in hand from its own `pv-internal-tech-analysis` call before reaching this skill. If given, this skill reuses those concrete values verbatim instead of inventing them. If omitted (or empty), this skill never tries to resolve a style bible on its own — see "Rules for each mockup" below.
- **`language`** (optional, only for `create`/`edit`): plain text naming the language for the mockup's sample text/content (e.g. `"English"`, `"Spanish"`). Defaults to English if omitted.

## Rules for each mockup

Every `design_*.html` file is only a visual mockup, not a functional prototype:

- **It must replicate the app's documented visual identity when the caller supplied one.**
  This skill never resolves the style bible itself (see "Plugin isolation" above) — it only
  reuses what the caller already gathered:
  - If the caller passed `style_context`, reuse its concrete values (hex codes, `rem`/`px`
    values, token names) verbatim — don't approximate or invent alternatives.
  - If it didn't (or passed it empty), use sober neutral styling and note it at the top of
    the file: `<!-- No documented visual identity for <element>; neutral placeholder styling. -->`.

  The mockup stays self-contained (existing rule): copy the styling inline replicating the
  documented appearance — never link the real stylesheet or a CDN.
- It must show only the look (layout, styles, iconography) that element would have — no need for real data or logic, static sample content illustrating the result is enough.
- It must have no real functionality: no JavaScript reacting to events, no network calls, no state — **the one exception is the standard annotation framework copied verbatim from `assets/mockup-annotations.html`** (see "Embed the annotation framework" below); beyond that, the mockup contains no other JS, at most purely decorative JS if needed for the visual look.
- It must be self-contained: only HTML, CSS and SVG, all embedded in the file itself (no external files, no CDNs, no imports).
- One file per distinct visual element in the proposal — don't group several different elements into the same `design_*.html` unless the caller asked for them as a single unit.
- **Embed the annotation framework.** After writing or editing the mockup's own markup (`create` or `edit`), splice in the asset's blocks:
  - Copy, **verbatim — never re-type, summarize, or "improve" it** (same rule as `pv-init/SKILL.md`'s `assets/pv.py`: *"copied as-is without modifying a single line of it"*), from `assets/mockup-annotations.html`:
    - the `<!-- mnoteqz7k-framework vN -->` marker comment and `<style id="mnoteqz7k-styles">…</style>` right before `</head>`;
    - `<script id="mnoteqz7k-runtime">…</script>` right before `</body>`.
  - Add an empty `<script type="application/json" id="mnoteqz7k-data">[]</script>` if the file doesn't already have one.
  - The mockup stays self-contained even with this — the framework is embedded inline, never linked externally.
  - See "Steps" below for the exact three sub-cases this splicing follows on `edit` (new file, older framework, embedded-and-current).

## Steps

### `action: create` / `action: edit`

1. For each element in the received list:
   - **ID collision guard.** Before deciding whether the file already has the framework embedded, check whether it has any element with `id="mnoteqz7k-styles"`, `id="mnoteqz7k-runtime"`, or `id="mnoteqz7k-data"`. If one exists, verify its **content shape** — not just the id's presence — is recognizable as the asset (the style block starts with the same rule set, the script starts with a `/* mnoteqz7k-framework vN — self-contained review-annotation runtime. */`-shaped header, matching the marker comment). If an id exists with unrecognized content (a `design_*.html` predating this framework that happens to reuse the same namespace), **stop and return the conflict to the caller** (which id, and that it holds unrecognized content) **without writing anything** — never silently overwrite it, and never treat it as "no framework present".
   - **`create`**: write the mockup's own markup (HTML + CSS + SVG inline, no JS of its own) in `design_<description>.html`, following the rules above (`style_context` if given, else neutral styling). Then embed the framework (see "Embed the annotation framework" above).
   - **`edit`** with no recognizable framework blocks present (older mockup, or one that just failed the collision guard with no conflict — i.e. genuinely absent): edit the mockup's own markup for the requested change, then embed the framework exactly as `create` does.
   - **`edit`** with a recognizable framework already present, and the asset's `<!-- mnoteqz7k-framework vN -->` marker is **not newer** than the file's: edit only the mockup's own markup for the requested change, preserving the rest of the file unrelated to it. **Never touch `mnoteqz7k-*` or `#mnoteqz7k-data` in this case** — not the framework blocks, not any note's state or content. A plain `edit` from a caller never changes or removes a note; resolving annotations is the exclusive job of `action: ensure-closed` below.
   - **`edit`** with a recognizable framework already present, and the asset's marker **is newer**: edit the mockup's own markup for the requested change, **and** replace only the `<style id="mnoteqz7k-styles">` and `<script id="mnoteqz7k-runtime">` blocks with the asset's current ones (same verbatim-copy rule) — keep `#mnoteqz7k-data` exactly as it was, with no exceptions.
2. Return to the caller, in the same turn: the list of created/edited file paths, one per element. Don't present anything to the user or ask for confirmation — that's the caller's job.

### `action: ensure-closed`

Input: a list of `design_*.html` paths (the ones the caller is about to (re-)present, or — for `pv-how` — every `design_*.html` in the entry). This is the **only** way any caller learns about or resolves annotations — no caller ever opens `#mnoteqz7k-data`, knows the `mnoteqz7k-*` namespace, or sees an individual note's selector or `open`/`closed` state directly.

For each path:
1. If the file doesn't exist, or has no recognizable framework embedded (per the same content-shape check as the collision guard above), skip it — never an error, never blocks the other paths in the same call.
2. Otherwise, parse `#mnoteqz7k-data` internally. If every note is already `state: "closed"` (or there are none), this path is done.
3. For each note with `state: "open"`:
   - If a linked note's stored selector no longer resolves ("detached"), treat it as a general note for this purpose.
   - If the skill can confidently decide what change the note is asking for, apply it directly to the mockup's own markup (same mechanism as an internal `edit` — no round-trip to the caller for this), then set that note's `state` to `"closed"` in `#mnoteqz7k-data` (nothing else in that note, or in the rest of the block, changes).
   - If the note is ambiguous enough that the skill can't confidently decide, **ask the user directly** — see "Talking to the user" below — before applying anything for that note; once answered, apply the change and close the note the same way.
4. Once every given path has zero `open` notes left, return **OK** plus a plain-text summary of what was changed per resolved note — no selectors, no raw JSON, no mention of `mnoteqz7k-*` or note ids.

### `action: describe`

Input: a list of `design_*.html` paths and, optionally, which elements/areas the caller wants described. Read-only — never touches `#mnoteqz7k-data` or any note's state. This is the **only** way any caller accesses a mockup's visual content — no caller ever `Read`s a `design_*.html` file itself.

For each path, read its own markup (something only this skill ever does directly) and return a plain-text description of the requested elements' layout, styling, and iconography — enough for a caller like `pv-how` (or `pv-do`, drafting a style-bible update) to use as visual reference, without exposing the raw HTML/CSS/SVG or the `mnoteqz7k-*` framework blocks (irrelevant to that purpose). `navigation_*.md`/`data_*.md` are out of scope for this action — they live outside `mockups/`, aren't this skill's responsibility, and the caller keeps reading them with a plain `Read`.

### Talking to the user (only `ensure-closed`)

Unlike every other `pv-internal-*` skill (which are mute — they only exchange input/output with their caller), `ensure-closed` can ask the reviewer a question directly, in the same turn, when it hits a note it can't resolve unambiguously on its own. This is a deliberate, scoped exception: delegating an ambiguous note's resolution back through the caller would mean the caller has to understand and relay something about the mockup's annotations, breaking the encapsulation this whole design exists to enforce. No other action, and no other `pv-internal-*` skill, gets this exception.

### Versioning note

The asset's `<!-- mnoteqz7k-framework vN -->` marker is independent of this skill's own `metadata.version` — framework-release version bumps are handled by `/dev-generate-version`, not by bumping the marker by hand.
