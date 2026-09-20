---
name: pv-internal-progress-todowrite
description: Shared, project-agnostic procedure to publish and update a visible progress checklist for a pv-* orchestrator's own flow (pv-new/pv-fix/pv-how/pv-do), using the harness's native TodoWrite tool. Receives an action (init/update/close) plus the item list or the item/status being changed, and returns nothing the caller needs to act on. Internal use by pv-new, pv-fix, pv-how and pv-do, invoked by the name configured in `.claude/pv-context.json`'s `framework.skills.progress` (by default, this same skill), only when that field is configured.
user-invocable: false
model: claude-sonnet-5
effort: low
metadata:
  author: Sergio José Martínez Primiani
  version: 0.9.8b4
  uses: []
---

# pv-internal-progress-todowrite

A single, shared procedure to publish a visible progress checklist for the major steps of a `pv-*` orchestrator's own flow, so the user can see in the interface where the flow is without asking in chat. Only invoked by other `pv-*` framework skills — not meant for direct invocation by the user.

**This skill doesn't decide which steps exist, how many, or when they change status.** That's always decided by the caller (the orchestrator), exactly as it already knows its own `workflow.*.md` — this skill only renders whatever list and status it's given.

If a project configures another skill in `framework.skills.progress` to report progress a different way (e.g. a host without `TodoWrite`), that alternative skill must fulfill the same input contract described here so it can replace this one without `pv-new`/`pv-fix`/`pv-how`/`pv-do` needing to change anything.

## Expected input from the caller

One `action`, plus the fields that action needs:

- **`init`** — `items`: the ordered, complete list of major steps of the flow (or branch) about to run, each a short text in the caller's `framework.interaction.language`. Replaces any previous list in full (a second `init` mid-flow, e.g. because a conditional step turned out to apply, replaces the list the same way — last list wins).
- **`update`** — `itemId`: which of the current items changes. `status`: `in_progress` or `completed`.
- **`close`** — no fields. Marks every remaining item `completed` (flow finished normally). If the caller is stopping early instead, it does not call `close` with that meaning — see "Steps" below.

## Output

Nothing the caller needs to read or branch on — fire-and-forget, like logging. Never present anything to the user directly; the checklist rendering is entirely the harness's own UI for `TodoWrite`.

## Steps

1. Keep the current item list and each item's status in this conversation's own memory (not written to disk) — this skill's whole state lives only as long as the session does.
2. On `action: init`: replace the in-memory list with `items`, each starting as `pending` except the first, which starts `in_progress` (a flow's first major step begins running as soon as it's announced). Call `TodoWrite` with the full list and these statuses.
3. On `action: update`: set `itemId`'s status to `status` in the in-memory list, leaving every other item's status untouched. Call `TodoWrite` with the full list (the tool requires the entire list on every call, never a delta).
4. On `action: close`: set every item still `pending` or `in_progress` to `completed`. Call `TodoWrite` with the full list.
5. If the caller never called `init` in this conversation (e.g. `framework.skills.progress` isn't actually configured but something invoked this skill anyway), do nothing and return — there is no list to update.
