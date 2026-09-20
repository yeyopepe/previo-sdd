# Previo v0.9.8b2 changelog (from v0.9.7)

## Index

- ⭐[New](#new)
  - Optional progress checklist during a flow
- ✏️[Changed](#changed)
  - `pv-update` now catches leftover template bracket syntax in generated docs

## ⭐New

- **Optional progress checklist during a flow** — if `framework.skills.progress` is configured (e.g. to the new `pv-internal-progress-todowrite`), `pv-new`, `pv-fix`, `pv-how` and `pv-do` now publish a visible checklist of their major steps in the interface as they run, so you can see where the flow is without asking in chat. It's off by default: leaving `skills.progress` unset keeps the previous behavior exactly, with no checklist shown.

## ✏️Changed

- **`pv-update` now catches leftover template bracket syntax in generated docs** — a new check flags a `description.md`/`plan.md` that still carries the raw `[[[...]]]` marker syntax around a label (e.g. `**[[[Name]]]**` instead of `**Name**`), which happened when the model copied the template's internal notation verbatim instead of writing just the label it wraps. `pv-update` fixes it automatically by stripping the brackets.
