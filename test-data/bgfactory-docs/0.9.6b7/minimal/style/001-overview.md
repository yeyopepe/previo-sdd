# 001 — Overview

**Area**: Style bible

## Scope

BG Factory has a presentation layer: infinite pan/zoom game table, floating
edit-mode panels (components / resources / tags), a shared modal system, cursor
context menus, toasts. All style tokens live in `src/styles/main.css` `:root`.

## Language / naming

| Rule | Value |
|---|---|
| User-facing copy, in-repo prose docs | Spanish |
| Technical docs (`architecture/`, `style/`) | technical English |
| CSS class naming | BEM — `.block`, `.block__element`, `.block--modifier` |
| JS identifiers | camelCase; domain terms kept in Spanish where they are the code symbol (`carta`, `mazo`, `dado`, `etiqueta`, `bloqueado`, `oculto`) |
| Doc files | `NNN-slug.md` + generated `INDEX.md` |

[gotcha] Four footer buttons are a documented BEM exception: `.btn-cancel`,
`.btn-duplicate`, `.btn-accept`, `.btn-eliminar` are standalone classes, not
`block__element`. `src/ui/globalShortcuts.js` matches them literally.

## Files

| File | Area | Covers |
|---|---|---|
| [002 — Design tokens](002-design-tokens.md) | Visual design tokens | Full `:root` token set: color, radius, shadow, transition. |
| [003 — Modals & menus](003-modals-menus.md) | Reusable components / Interaction patterns | Shared modal DOM pattern, footer button variants + states, overlay, context menu, toast, progress modal. |
