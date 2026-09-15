# 008 — Code conventions

**Area**: Conventions

- ES modules (`import`/`export`) organized by layer/responsibility, one file per functional module.
- No external dependencies by default.
- A new library is only incorporated if its bundle can be embedded whole in the final HTML (no CDN at runtime, no additional installation).
- Graphic resources go in `/src/img`, organized by component type.
- Visual conventions (color tokens, typography, spacing, BEM naming, component patterns) documented in `../style/`.
- `src/test/` is the functional test framework (own runner + Playwright headless as a dev-only dependency, launched with `npm test`) — see [011 — Functional test framework](011-functional-test-framework.md). Its `src/test/fixtures/*.json` are games in the "Exportar" format (`core/persistence.js`: `buildComponentsExport` → `{ version, components, resources, tags, componentGroups, appTitle }`), loaded from tests via `loadFixture(...)`. Node/npm are **only** for tests: `src/scripts/build.py` and the deliverable do not depend on them, and nothing under `src/test/` enters the bundle (`build.py` walks imports from `src/main.js` only).
- Code comments: only the necessary ones. They explain the non-obvious why (hidden constraint, invariant, one-off workaround), never the what (the code already says it). No comment if removing it would not confuse a later reader.
- Comment style, when needed: same as the technical documentation — telegraphic. No superfluous articles, no filler adverbs, verbs in present, implicit subject. References (field name, type, file) always explicit, unambiguous.
- Exception: `src/vendor/` and `src/scripts/vendor/` are third-party code as-is (see `001-overview.md`, Layered architecture) — their comments are not touched.
