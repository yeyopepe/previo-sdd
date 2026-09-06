# 004 — Build pipeline

**Area**: Architecture

## Entry point

`python src/scripts/build.py` — no arguments. Pure Python 3, standard library only (`base64`, `re`, `pathlib`). No Node, no `package.json`.

## Output

`src/_output/versions/index-v{XXXX}.html` — one self-contained file: HTML + inlined `<style>` + inlined `<script>` + all image/font assets as `data:` URIs.

## Pipeline

```
1. visit_module('main.js')          -> DFS over ES `import` graph; `order` = post-order list (deps first)
2. bump version:
     read src/data/version.js CURRENT_VERSION 'vNNNN'
     new = zfill(int(NNNN) + 1, len(NNNN))
     write back to src/data/version.js               [gotcha] build.py MUTATES a source file
3. per module in `order`:
     strip `export function`/`export const` -> collect names
     `import { a, b } from 'x'`  ->  `const { a, b } = require('<resolved rel path>');`
     wrap: __modules['<rel>'] = function(module, exports, require) { <body>; module.exports.a = a; ... }
4. bundle_js = RUNTIME + wrapped modules + `require('main.js');`
     RUNTIME = ~8-line CommonJS shim (__modules registry, __cache, require())
5. css = read styles/main.css; embed_css_asset_urls  -> url(...) non-data/non-http -> url("data:...")
6. html = read index.html
     remove <link rel=stylesheet> and <script type=module>
     embed_html_asset_refs   -> <img|link|source src|href="..."> local -> data URI
     inject <style> after </title>, <script>bundle_js</script> before </body>
     replace {VERSION} in <title> with 'v.{version}'         (fails build if marker absent)
7. write index-v{version}.html
```

## Import transform — supported subset

| Handled | Not handled |
|---|---|
| `import { named, list } from 'rel/path.js'` | default imports, namespace imports (`* as`), dynamic `import()` |
| `export function f` / `export async function f` | `export default`, `export { x }`, re-exports |
| `export const C` | `export let`/`export var`, destructured `export const { a }` |

`IMPORT_PATTERN` / `EXPORT_FUNCTION_PATTERN` / `EXPORT_CONST_PATTERN` are regexes — the codebase must stay within this subset for the build to work.

- [motivación] `vendor/marked.js` is `require`-loaded by `core/markdown.js` via the same ES `import { parse }` form, so it goes through the transform like any other module.

## Asset embedding rules

`CSS_URL_PATTERN` / `HTML_ASSET_PATTERN` skip `data:`, `http(s)://`, `//`, and (HTML) `#`. Missing file → reference left untouched (no build failure). MIME from `MIME_TYPES` map, else `application/octet-stream`.

## Optional obfuscation

`node src/scripts/obfuscate_bundle.js <input.js> <output.js>` — separate, optional step. Uses vendored `src/scripts/vendor/javascript-obfuscator.browser.js` (UMD browser build; script sets `global.self = global`). Requires Node; not part of `build.py`.

## Version semantics

`CURRENT_VERSION` (`src/data/version.js`) is an auto-incrementing deliverable counter, independent of any pv-* change/fix `{xxxx}` code. `build.py` increments it on every run before packaging, so the bundle embeds the already-incremented value.
