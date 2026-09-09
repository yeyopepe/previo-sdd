# 001 — Overview

**Area**: Overview

## Goal and constraints

- Digital prototype runs in any modern browser.
- Deliverable: a single self-contained HTML file (JS and CSS embedded, any external library embedded in the file itself).
- Opens with a double click (`file://`), no server or installation.
- Build does not depend on Node.js or complex build tools: uses Python.
- Source code organized in separate files/layers inside `/src`.
- `src/scripts/build.py` transforms the source code into a single versioned file under `src/_output/versions/`.
- Functional tests live in `src/test/` (dev-only, Node + headless Chromium via Playwright); they never enter the deliverable. See [011 — Functional test framework](011-functional-test-framework.md).

## Test coverage rule

Every change that **adds** a feature must add its functional tests; every change that **modifies** a feature must update them; every change that **removes** a feature must delete the tests (and fixtures) that validated it. A change is not complete until `npm test` passes and `src/test/TRACEABILITY.md` is regenerated with no anomalies. Details in [011 — Functional test framework](011-functional-test-framework.md).

## Layered architecture

```
core/    → application state, data model (components and resources), event bus, persistence and file export
modes/   → play mode and edit mode, each in its own folder
ui/      → interface elements reused across modes
data/    → app version data and default gallery resources
main.js  → bootstrap: wires the previous layers
```

Dependencies between layers (arrow = "depends on"):

```
modes/* ──▶ ui/* ──▶ core/*
modes/* ──────────▶ core/*
main.js ──▶ data/*, ui/*, modes/*, core/*
```

- `core` depends on no other layer.
- `ui` depends only on `core` (reads/writes state).
- `modes` composes `ui` and `core` to build each screen.
- `main.js` is the only point that knows and wires all layers.
- State (`core/state.js`) is the single source of truth.
- Changes are notified via a simple event bus (`core/eventBus.js`, `emit`/`on`) so the UI re-renders without coupling modules to each other.
