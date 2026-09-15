# 005 — Text links and external links

**Area**: Layout & components

First user-facing hyperlink (`<a>`) in `/src`: change 00243, the repository link in the version footer (`#app-version`, see `002-componentes-layout.md`, "Version footer"). No `<a>` existed anywhere in `/src` before it.

## Visual

| Property | Value | Note |
|---|---|---|
| `color` | `inherit` | Link takes the surrounding text color — no dedicated link token, no `--accent-blue` |
| `text-decoration` | `underline` | The only thing distinguishing a link from adjacent text |
| `:visited` / `:hover` / `:active` | not styled | No state variants; browser default pointer cursor from `<a href>` |

- [gotcha] a text link is NOT `--accent-blue`. Accent blue means "interactive control / selected" across the app (buttons, active tab, selection outline); a text link is distinguished by the underline alone, in the color of its context.
- Reference rules: `#app-version a` and `.settings-modal__repo a` in `src/styles/main.css` — same treatment, two sites.
  - `.settings-modal__repo` (00250): the GitHub external link repeated inside the settings panel's version block (`006-ui-layer.md`, `ui/settingsModal.js`). Container `font-size: 0.875rem` (default UI text, `001-tokens-visual.md`), `color: var(--text-muted)`, `margin-top: 0.15rem`; the `<a>` inherits `color` and adds `text-decoration: underline`, identical to `#app-version a`.

## Markup

- Built with `document.createElement('a')` + property assignment (`href`, `textContent`, `target`, `rel`), never interpolated `innerHTML` — same DOM convention as the rest of the app (`004-naming-and-patterns.md`, Component patterns).
- Visible text is a readable label, never the raw URL. The `href` never changes.
- Label language: `#app-version a` and `.settings-modal__repo a` use `t('appVersion.repoLink')` (→ `Ver en Github` / `View on GitHub`, 00244). `.splash-window__link` (00247) uses a **fixed literal `"View on Github"`, NOT `t()`** — coherent with the splash title, also not translated (see `../architecture/006-ui-layer.md`, `ui/splashScreen.js`).
- `#app-version` is (re)built by `renderAppVersion()` on every `renderAll()` (00244, was one-shot at module load) so the label updates on language change. `.splash-window__link` is built once, does not re-render.

## External links

`external` — opens a destination outside the app:

- `target="_blank"` always paired with `rel="noopener"`.
- Opens in a new browser tab; the app tab keeps its state.
- Reference: the repository link (`https://github.com/yeyopepe/bgfactory`), in 3 sites, all built `createElement` + property assignment, `href` fixed:

  | Site | Class | Label |
  |---|---|---|
  | Version footer | `#app-version a` (00243) | `t('appVersion.repoLink')` |
  | Settings panel version block | `.settings-modal__repo a` (00250) | `t('appVersion.repoLink')` |
  | Startup splash | `.splash-window__link` (00247) | fixed literal `"View on Github"` — [gotcha] not `t()` |

- The URL string is a hardcoded literal in all 3 sites (`main.js#renderAppVersion`, `settingsModal.js`, `splashScreen.js`) — not centralized.
