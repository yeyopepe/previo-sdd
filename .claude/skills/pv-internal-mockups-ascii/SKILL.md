---
name: pv-internal-mockups-ascii
description: Shared, project-agnostic procedure to create or edit static visual mockups in plain ASCII text (`design_*.txt`) for a change/fix. Actions: `create`/`edit` (destination folder + list of visual elements + optional style_context/language as input; paths of the resulting files plus `style_gaps` as output), `ensure-closed` (no-op — plain text carries no pending state of its own, so this always returns OK immediately with empty `style_gaps`), and `describe` (read-only plain-text description of a mockup's visual content, for a caller that needs a reference without opening the file itself). Doesn't decide which elements need a mockup, doesn't resolve its own style-bible/language context (the caller supplies it), and doesn't validate anything with the user. Internal use by the pv-new and pv-fix skills (directly or from extend-entry.md) and pv-how, invoked by the name configured in `.claude/pv-context.json`'s `framework.skills.mockups` when the project prefers ASCII mockups over HTML.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  author: Sergio José Martínez Primiani
  version: 0.9.8b11
  uses: []
---

# pv-internal-mockups-ascii

A single, shared procedure to generate the visual mockup (`design_*.txt`) of a new or modified UI element, as plain-text ASCII art. Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**Plugin isolation.** This skill is a self-contained plugin: copying only its own folder to another repo must let it create/edit/manage `design_*.txt` at 100%. It never resolves its own style-bible or language context from disk or from `.claude/pv-context.json` — everything it needs comes from the caller as input, and its absence degrades gracefully (neutral placeholder styling, English sample text) rather than triggering a resolution of its own. This is what keeps it swappable via `framework.skills.mockups` — any skill named there is a drop-in replacement as long as it honors the same input/output contract (see "Steps" below), regardless of what technology it uses internally.

**Language.** This skill doesn't talk to the user for its `create`/`edit` actions. The mockup's sample text/content follows the `language` the caller passes as input (plain text, e.g. `"English"` or `"Spanish"`); if omitted, it defaults to English. This skill never reads `framework.changes.language`/`interaction.language` or `.claude/pv-context.json` itself — resolving that is the caller's job, consistent with the plugin-isolation rule above.

**This skill doesn't decide which elements need a mockup, nor validate anything with the user.** That's always decided by the caller (typically `pv-new`/`pv-fix`, upon detecting the change has a visual component): this skill is only invoked once it's already known that generating or editing at least one ASCII mockup is needed, never "just in case". Presenting the result to the user for confirmation is also the caller's responsibility.

This skill is specifically for **ASCII text** mockups. If a project configures another skill in `framework.skills.mockups` to use a different technology (e.g. HTML, Figma, a component library, images), that alternative skill must fulfill the same input/output contract described here so it can replace this one without `pv-new`/`pv-fix`/`pv-how` needing to change anything.

## Expected input from the caller

- **Destination folder**: the path where the files should live, normally `{changesDir}/inProgress/{xxxx}/mockups/`. Every mockup file lives under `{destination folder}/mockups/`, never loose in the entry root — the caller is responsible for passing that subfolder, this skill just writes where it's told. Required for `create`/`edit`/`ensure-closed`/`describe`.
- **Action**: `create`, `edit`, `ensure-closed`, or `describe` — see "Steps" below for each one's own contract. `create`/`edit` share the same "List of visual elements" input; `ensure-closed`/`describe` instead take a list of `design_*.txt` paths (see their own sections).
- **List of visual elements** (only for `create`/`edit`), one per mockup to create or edit. For each element:
  - **Brief description** of the element (used for the filename: `design_<element-description>.txt`, e.g. `design_deck-selection-modal.txt`, `design_progress-bar.txt`).
  - **What it should show**: look, layout, sample content relevant to illustrate the result (the caller doesn't need to give low-level detail — exact colors, measurements — if it doesn't have it yet).
  - **Sub-action**: `create` (new file) or `edit` (a `design_*.txt` with that name already exists in the destination folder and needs modifying) — in this second case, what changes relative to what's already there.
- **`style_context`** (optional, only for `create`/`edit`): plain text — already-resolved excerpts of the project's style bible (layout/composition conventions, interaction-state conventions, content & microcopy) that the caller gathered itself. If given, this skill reuses it verbatim instead of resolving the style bible on its own — see "Rules for each mockup" below for what happens when it's omitted.
- **`language`** (optional, only for `create`/`edit`): plain text naming the language for the mockup's sample text/content (e.g. `"English"`, `"Spanish"`). Defaults to English if omitted. **Caller note**: this skill never resolves the project's language itself — if the caller has one (e.g. `framework.changes.language`) but forgets to pass it here, the mockup silently falls back to English instead of the project's actual language. Pass it explicitly whenever the caller already knows it.

## Rules for each mockup

Every `design_*.txt` file is only a visual mockup, not a functional prototype:

- **It must follow the app's documented layout and copy conventions when the caller supplied
  them.** This skill never resolves the style bible itself (see "Plugin isolation" above) —
  it only reuses what the caller already gathered:
  - If the caller passed `style_context`, reuse its concrete conventions (layout &
    composition, interaction-state conventions, real microcopy — button labels, status text,
    CLI flag naming) verbatim instead of inventing them.
  - If it didn't (or passed it empty), use a neutral placeholder layout and note it at the
    top of the file: `-- No documented style conventions for <element>; neutral placeholder. --`.
  - If the caller (via the element's "what it should show") or an explicit request names a
    concrete convention — exact button/label text, a CLI flag name, a status string — that
    isn't already covered by `style_context`, apply it as asked (it's the most specific
    instruction available), but record it — see "Reporting style-bible gaps" below. This is
    distinct from the generic neutral-placeholder case above: it's not "no style given", it's
    "a real value given, but it didn't come from the documented style bible".
- It's pure plain text: only ASCII characters (lines, corners and fills with `-`, `|`, `+`, `_`, `/`, `\`, `*`, `#`, `.`, spaces, etc.). No HTML, Markdown, emoji, or Unicode box-drawing characters (`─│┌┐└┘`) — the goal is that it looks equally good in any monospace text editor.
- Assumes a monospace font implicitly: align columns and borders with spaces, taking care that every line in a block has a consistent width so the boxes line up visually.
- It must show only the look (element layout, hierarchy, grouping, relative sizes) that element would have — no need for real data, static sample content illustrating the result is enough (button text, labels, example values).
- Represents controls and states with simple, explicit conventions when they add clarity, for example:
  - Button: `[ Save ]`
  - Text field: `[ group name____ ]`
  - Checked/unchecked checkbox: `[x]` / `[ ]`
  - Selected or highlighted element: `> Active option <` or surrounded by `*`
  - Icon or image: a bracketed marker describing what it is, e.g. `[trash-icon]`
- If the element has several relevant states (e.g. normal / hover / error) or the flow has several steps, represent them as separate blocks within the same file, each with a brief title on a comment line (e.g. `-- State: error --`) before the block.
- One file per distinct visual element in the proposal — don't group several different elements into the same `design_*.txt` unless the caller asked for them as a single unit.

## Reporting style-bible gaps

Whenever this skill applies a concrete convention that didn't come from `style_context` —
because the caller's element description explicitly asked for it (see "Rules for each
mockup" above) — it tracks that as a **style gap**: a plain-text entry saying which element
asked for it, what convention was applied, and (if inferable) what it seems to be missing or
contradicting in the style bible (e.g. "no documented label for this action; applied 'Discard
changes' as requested" or "requested status text differs from style_context's documented
wording for this state — possible correction needed").

This never happens for the generic neutral-placeholder case (no convention was given at all,
so there's nothing to reconcile against the style bible) — only when a real, specific
convention was supplied outside of `style_context`.

`create`/`edit` return this list as `style_gaps` alongside the file paths (empty list if
none). This skill never edits the style bible itself, never asks the user about it, and never
decides whether a gap is worth fixing — it only surfaces what it noticed so the caller (or
whoever owns `docs.tech.styleBibleDocDir`) can act on it. **Caller note**: a non-empty
`style_gaps` is only useful if the caller actually does something with it — surface it to the
user or pass it along to whoever maintains the style bible. Silently discarding it defeats
the entire point of tracking gaps in the first place.

## Steps

### `action: create` / `action: edit`

1. For each element in the received list, create (if the sub-action is `create`) or edit (if
   `edit`) the corresponding `design_<element-description>.txt` file in the destination
   folder, following the rules above (`style_context` if given, else neutral placeholder).
   When editing, preserve the rest of the file unrelated to the requested change.
2. Return to the caller, in the same turn: the list of created/edited file paths, one per
   element, plus `style_gaps` (see "Reporting style-bible gaps" above). Don't present
   anything to the user or ask for confirmation — that's the caller's job.

### `action: ensure-closed`

A `design_*.txt` file never carries any pending, unresolved state of its own — there's
nothing in this notation that stays "open" between edits. So this action is always a no-op:
every caller in this framework invokes it the same way regardless of which mockup skill is
configured, and this skill honors that same call without ever having anything to resolve.

Input: a list of `design_*.txt` paths (ignored beyond existence — nothing is read or parsed
from them). Immediately return **OK** with an empty change summary and an empty `style_gaps`,
for every path given, without touching any file. Never asks the user anything.

### `action: describe`

Input: a list of `design_*.txt` paths and, optionally, which elements/areas the caller wants
described. Read-only. This is the **only** way any caller accesses a mockup's visual content —
no caller ever `Read`s a `design_*.txt` file itself.

For each path, read its own content (something only this skill ever does directly) and return
a plain-text description of the requested elements' layout, structure, and represented states
— enough for a caller like `pv-how` (or `pv-do`, drafting a style-bible update) to use as
visual reference, without requiring the caller to parse ASCII art itself.
