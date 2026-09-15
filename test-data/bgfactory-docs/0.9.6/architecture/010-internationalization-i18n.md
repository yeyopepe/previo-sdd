# 010 — Internationalization (i18n)

**Area**: Internationalization

Change 00244. UI chrome text is translatable; user-entered content is not.

## Components

| File | Responsibility |
|---|---|
| `src/core/i18n.js` | All i18n logic. Active language (in-memory), resolution on startup, `t()` string resolution with fallback chain + param interpolation + plural, `language:changed` emission. Imports only `./eventBus.js`, `./appTitle.js`, `../data/i18n.es.js`, `../data/i18n.en.js` — no `ui/*`/`modes/*` (respects layer direction). |
| `src/data/i18n.es.js` | `CATALOG_ES` — plain `key: string \| { one, other }` object. PURE DATA: no logic, no imports. Canonical reference: must be complete. |
| `src/data/i18n.en.js` | `CATALOG_EN` — same keys, English. May be temporarily incomplete (falls back to `CATALOG_ES`). |
| `src/ui/settingsModal.js` | Settings panel modal. Standard `.modal-overlay`/`.modal` pattern (ref `ui/helpIcon.js`). Content: language `<select>` (es/en, options are fixed literals not via `t()`) + "Texto en la mesa" `<textarea>` for `state.tableText` (keys `settings.tableText.label`/`.hint`, `input` → `setTableText`, 00250) + read-only version line `getVersionedProductName()` (fixed `BG Factory v.<NNNNN>`, no longer `getFullAppTitle(getAppTitle())`, 00250) with GitHub link (`t('appVersion.repoLink')`). Subscribes `on('language:changed', renderContent)` on open, `off()` on close (any close path). Opened by `createSettingsButton` in `ui/editModeToggle.js`. |

## Contracts (`src/core/i18n.js` exports)

```
SUPPORTED_LANGUAGES: string[] = ['es', 'en']
DEFAULT_LANGUAGE: string = 'es'
initI18n() -> void                       // once, from main.js, before first render and startup toasts
getLanguage() -> 'es' | 'en'
getLocale() -> 'es' | 'en'                // locale arg for localeCompare
setLanguage(code: string) -> void        // no-op if code not in SUPPORTED_LANGUAGES or code === active
t(key: string, params?: object) -> string
```

- `t(key, params)` resolution: `CATALOG[active][key]` → `CATALOG['es'][key]` → `key`. `console.warn` on miss only if module const `DEV_WARN === true` (default `false`).
- `t` plural: entry shaped `{ one, other }` + `params.count` present → `one` when `count === 1`, else `other`.
- `t` interpolation: each `{name}` in the resolved string replaced by `String(params[name])`. Plain text — result assigned via `textContent`. Exception: `batchUpload.*` entries carry static `<strong>` markup, assigned via `innerHTML` (trusted catalog markup, only `{count}` interpolated).
- Module-level `{value, label}` arrays that feed `<select>`/menus use `get label() { return t('key'); }` so labels follow the active language on each read (re-read on every modal open): `componentModal.js` (`MAZO_*`, plus `DEFAULT_MAZO_PROPERTIES.textoCartaRevelada` — getter resolved at spread time, stored as a concrete string on the new component), `componentTypeModal.js` (`COMPONENT_TYPES`, drives `getComponentTypeLabel`), `core/cardProportions.js` (`CARD_PROPORTIONS`), `core/interactions.js` (`TYPE_INTERACTIONS`), `ui/styleClipboardSelectionModal.js` (`ITEMS`).
- Module-level maps that only resolve at the consumption site are kept as `key → catalog-key` (not `key → text`) and passed through `t()` where used: `componentRenderer.js` `COMPONENT_IDENTIFIER_TYPE_KEY` (shorter type labels than `componentType.*` — `'Texto'` vs `'Cuadro de texto'`, `'Documento'` vs `'Visor de documentos'`), `importReportModal.js` `ERROR_LABEL_KEY`.
- `core/textSort.js` (`sortByName`, `compareValues`) and `core/resource.js` (`findResourceByName`) pass `getLocale()` as the `localeCompare` locale (was fixed `'es'`).
- `core/` consumers of `t()` (import `./i18n.js`, no cycle — `i18n.js` imports only `eventBus.js`, `appTitle.js`, the two catalogs): `textSort.js`, `resource.js`, `cardProportions.js`, `interactions.js`, `styleClipboard.js`, and (fix 00245) `importMerge.js` (import-report `solucion` strings), `persistence.js` (`parseImportedComponents` error `detail`). (`fichaMigration.js` was one until 00250 removed it.)

## New event

`language:changed` on `core/eventBus.js`. Payload: the new language code.

| Subscriber | Effect |
|---|---|
| `src/main.js` | `renderAll()` — repaints header title, `#app-version` (now `renderAppVersion()`, was one-shot; also subscribed to `tableText:changed`, 00250), mode switcher, edit toolbar, active mode. |
| each open modal that can outlive a language switch | re-renders its own text content via `t()` without closing. `ui/settingsModal.js` implements this; other complex modals re-textualize on reopen. |

## Startup flow (`src/main.js`)

```
0. showSplashScreen()                    // ui/splashScreen.js — before initI18n(). NOT i18n-aware:
                                         // title "Board Game Factory" + "(2026)" is a fixed brand string, no t().
1. initI18n()                            // reads localStorage['bgfactory:lang']
2.   supported? -> active = stored
     else -> navigator.language startsWith 'es' ? 'es' : 'en'   // NOT written to localStorage
3.   applyDocumentLanguage(): documentElement.lang = active; document.title = t('app.documentTitle') + ' ' + formatVersion()
4. renderAppVersion / state resolution / seedDefaultResources (names via t()) / startup showToast (via t()) / first renderAll()
```

Language change: `setLanguage(code)` → `localStorage['bgfactory:lang'] = code` (try/catch) → active = code → `applyDocumentLanguage()` → `emit('language:changed', code)`.

## Persistence

`persistence.language.persist.key = 'bgfactory:lang'` — `localStorage` key separate from the state slot `bgfactory:state`.

- NOT in `persistence.serializedFields`; NOT in the export/import JSON (`buildComponentsExport`).
- Survives `CURRENT_VERSION` changes (unlike `bgfactory:state`, which `parseState` discards on version mismatch).
- Absent/unsupported value → autodetection. No migration.

## Decisions

- `i18n.catalog.decision.pure-data` — catalogs are plain `key → text` objects, no logic, no imports. `'es'` is canonical and always complete; `t()` falls back active → `'es'` → key.
  - [motivación] editing a translation cannot break behavior; adding a language = one catalog file + one `SUPPORTED_LANGUAGES` entry, no logic/component change.
- `i18n.language.persist.decision.separate-key` — language preference in its own `localStorage` key, not in `bgfactory:state`.
  - [motivación] `parseState` discards the whole state slot on `version !== CURRENT_VERSION`; the language preference must not be lost on every app version bump.
- `i18n.decision.no-external-lib` — hand-rolled `t()` + plain-object catalogs, no i18n library. Follows the project rule: no CDN at runtime, everything bundled by `src/scripts/build.py` (import graph from `main.js`).

## Bar-controls reorganization (`src/ui/editModeToggle.js`)

Bundled with i18n (same file). See [006 — UI layer: reusable modules](006-ui-layer.md).

- `createSettingsButton(className)` — new. Icon-only 36×36, class `mode-switcher__settings-btn`, opens `settingsModal`. NOT blue (`background: none; border: 1px solid var(--text-light)`), unlike `mode-switcher__fit-btn`.
- `createModeButton()` — new helper. Mode-switch button (`Modo Edición` in play, `Modo Juego` in edit), class `mode-switcher__mode-btn`, primary-action blue. Always mounted in the header corner row (`#mode-switcher`) in both modes.
- `renderModeSwitcher` runs in both modes now (was play-only early return): builds `#mode-switcher` with `[Importar] [Exportar] | (divider, play only) [Modo] [Ajustar zoom] [Configuración]`.
- `renderEditToolbar` no longer mounts the mode button nor `createFitButton` on `#edit-toolbar`; `.edit-toolbar` keeps only `[Importar] | [Exportar]`.
- `createImportControls` lost its `buttonClassName` param — `Importar`/`Exportar` use the same "ghost on dark" scheme in both modes.
- Text separated from inline SVG in the `innerHTML` template buttons (`Importar`, `Exportar`, mode button) via `iconTextButton(svg, text)` helper.
