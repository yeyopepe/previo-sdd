# Previo v0.9.6b12 changelog (from v0.9.6b11)

Note: within a section, entries may be grouped under a theme when at least two entries share a topic. In the detail section, a theme is `- 📂**{Theme}**:` with its entries nested as indented sub-bullets beneath it (no heading, no link). In the Index, the same theme collapses to a single plain line `📂{Theme} (N changes)` with its member entries not listed. Ungrouped entries are listed as ordinary top-level bullets in both places (bare title in the Index, full bold-title-plus-summary bullet in the detail).

## Index

- ✏️[Changed](#changed)
  - 📂Mockups follow the project's documented style (2 changes)

## ✏️Changed

- 📂**Mockups follow the project's documented style**:
  - **ASCII mockups reuse the documented layout and copy** — before inventing structure or sample text, `pv-internal-mockups-ascii` now reads the project's style bible (read-only) and reuses its real conventions for layout, element states and microcopy (button labels, status text, flag naming). When no style bible is configured it points the user to `/pv-init` or `/pv-update` and generates nothing; when the style bible exists but doesn't cover a given element, it uses a neutral placeholder layout and marks that gap in the file.
  - **HTML mockups replicate the documented visual identity** — before inventing any styling, `pv-internal-mockups-html` now reads the project's style bible (read-only) and reuses its concrete values (colors, typography, spacing, token names, reusable components, iconography, microcopy) instead of approximating them. When no style bible is configured it points the user to `/pv-init` or `/pv-update` and generates nothing; when the style bible exists but doesn't cover what the mockup needs, it falls back to sober neutral styling and notes that gap at the top of the file. Mockups stay self-contained: the documented appearance is copied inline, never linked from the real stylesheet or a CDN.
