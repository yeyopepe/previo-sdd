# Previo v0.9.8b4 changelog (from v0.9.7)

## Index

- ✏️[Changed](#changed)
  - `pv-update` now catches leftover template bracket syntax in generated docs

## ✏️Changed

- **`pv-update` now catches leftover template bracket syntax in generated docs** — a new check flags a `description.md`/`plan.md` that still carries the raw `[[[...]]]` marker syntax around a label (e.g. `**[[[Name]]]**` instead of `**Name**`), which happened when the model copied the template's internal notation verbatim instead of writing just the label it wraps. `pv-update` fixes it automatically by stripping the brackets.
