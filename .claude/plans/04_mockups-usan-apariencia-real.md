# Los mockups deben partir de la apariencia documentada de la app

## Context

Al generar mockups (`design_*.html` / `design_*.txt`) para un change/fix, el framework a
veces inventa estilos y colores que no tienen nada que ver con la app real, incluso cuando
el proyecto tiene una identidad visual asentada y documentada en
`framework.docs.tech.styleBibleDocDir` (por defecto `docs/style`).

Causa: `pv-internal-mockups-html` y `pv-internal-mockups-ascii` no tienen ninguna
instrucción de mirar el style bible antes de generar. Su sección "Rules for each mockup"
solo pide mostrar "the look that element would have".

Objetivo: **mínimo cambio** — que ambos skills, antes de generar, lean el style bible y
repliquen lo que allí esté documentado. Sin muestrear código fuente, sin tocar callers, sin
tocar el contrato de entrada, sin cambiar la tabla de responsabilidades de pv-design.

## Decisión de alcance (respuesta del usuario)

**Solo style bible.** Mockups pasa a ser un **lector más** de `docs.tech.styleBibleDocDir`
(solo lectura, nunca escribe ni decide su contenido) — mismo patrón que ya usa `pv-how` al
leer `docs.tech` vía `pv-internal-tech-analysis`. Si el style bible está vacío (solo su
`INDEX.md`), el mockup se genera con estilos sobrios y neutros y lo deja anotado. **No se
muestrea `sourcecodeDir`**: añadir a mockups la capacidad de explorar código sería una
responsabilidad nueva (hoy solo la tienen `pv-internal-tech-analysis` y
`pv-internal-tech-risks`) y se ha descartado.

Hueco conocido y aceptado: una app con el style bible sin poblar pero con identidad real en
su CSS/tema seguirá recibiendo un mockup neutro. La vía para cerrarlo es documentar el
style bible, no que el mockup lo deduzca del código.

## Cambio

### 1. `.claude/skills/pv-internal-mockups-html/SKILL.md`

Añadir una viñeta al principio de **"Rules for each mockup"** (no una sección nueva):

> - **It must replicate the app's documented visual identity when one exists.** Before
>   inventing any styling, read the project's style bible (read-only — this skill never
>   writes it or decides its content):
>   1. Resolve it with
>      `python .claude/skills/pv-init/scripts/resolve-path.py --what styleBibleDocDir`. On a
>      non-zero exit (exit 2 → `/pv-init`, exit 3 or 4 → `/pv-update`), return that to the
>      caller and generate nothing.
>   2. Read its `INDEX.md` and the files covering the visual categories relevant to the
>      elements being mocked (design tokens/colors, typography, spacing scale, layout,
>      reusable components, iconography, microcopy). Reuse the concrete values found there
>      (hex codes, `rem`/`px` values, token names) — don't approximate them from memory.
>   3. If that folder holds only its `INDEX.md` (nothing documented yet) or doesn't cover
>      what this mockup needs, use sober neutral styling for the gap and note it at the top
>      of the file: `<!-- No documented visual identity for <element>; neutral placeholder styling. -->`
>
>   The mockup stays self-contained (existing rule): copy the styling inline replicating the
>   documented appearance — never link the real stylesheet or a CDN.

### 2. `.claude/skills/pv-internal-mockups-ascii/SKILL.md`

Viñeta equivalente al principio de **"Rules for each mockup"**, acotada al medio (ASCII no
tiene color):

> - **It must follow the app's documented layout and copy conventions when they exist.**
>   Before inventing structure or sample text, read the project's style bible (read-only —
>   this skill never writes it or decides its content):
>   1. Resolve it with
>      `python .claude/skills/pv-init/scripts/resolve-path.py --what styleBibleDocDir`. On a
>      non-zero exit (exit 2 → `/pv-init`, exit 3 or 4 → `/pv-update`), return that to the
>      caller and generate nothing.
>   2. Read its `INDEX.md` and the files covering layout & composition, interaction patterns
>      (selected / highlighted / inactive states) and content & microcopy. Reuse the real
>      microcopy and conventions found there (button labels, status text, CLI flag naming)
>      instead of inventing them.
>   3. If that folder holds only its `INDEX.md`, or doesn't cover what's needed, use a
>      neutral placeholder layout for the gap and note it:
>      `-- No documented style conventions for <element>; neutral placeholder. --`

### 3. `.claude/pv-doc/pv-design/pv-design.en.md` y `.es.md`

Media frase en la entrada en prosa de cada skill de mockups, **sin tocar la tabla de
responsabilidades** (líneas 278-284) ni ninguna otra parte:

- `pv-design.en.md` línea 233 (`pv-internal-mockups-html`): tras "…the list of elements the
  caller needs to mock up", añadir algo como: "reading the project's style bible
  (`docs.tech.styleBibleDocDir`, read-only) first so the mockup replicates the documented
  visual identity rather than an invented one".
- `pv-design.en.md` línea 237 (`pv-internal-mockups-ascii`): como comparte contrato, basta
  "same style-bible read as `pv-internal-mockups-html`, applied to layout and microcopy".
- `pv-design.es.md`: las dos frases equivalentes en su redacción en español.

No se toca la línea 148 (resumen de grupo) porque mockups **no** pasa a explorar código;
sigue siendo válida tal cual.

## Ficheros

| Fichero | Cambio |
|---|---|
| `.claude/skills/pv-internal-mockups-html/SKILL.md` | 1 viñeta al inicio de "Rules for each mockup" |
| `.claude/skills/pv-internal-mockups-ascii/SKILL.md` | 1 viñeta equivalente, acotada a layout/microcopy |
| `.claude/pv-doc/pv-design/pv-design.en.md` | Media frase en líneas 233 y 237 |
| `.claude/pv-doc/pv-design/pv-design.es.md` | Media frase en las 2 entradas equivalentes |

**No se toca:**
- La tabla de responsabilidades de `pv-design.en.md` (278-284): queda byte a byte igual —
  es solo sobre las 4 skills de documentación y mockups no entra en ella.
- "Expected input from the caller" en ambos `SKILL.md`: sin parámetros nuevos.
- `pv-new` / `pv-fix` / `pv-how` / `extend-entry.md` / `workflow.*.md`: sin cambios.
- `pv-changelog.*.md`: el framework sella versión con `/dev-generate-version`, que regenera
  su propio changelog; no se edita a mano aquí.
- `metadata.version` en frontmatter: lo sella `/dev-generate-version`.

## Responsabilidad que cambia (y por qué no requiere discusión adicional)

**Única:** `pv-internal-mockups-html` / `-ascii` pasan a **leer** `docs.tech.styleBibleDocDir`
(solo lectura). No deciden su contenido, no lo escriben, no gestionan sus ficheros — eso
sigue siendo de `pv-internal-doc-style` (qué) y `pv-internal-doc-files` / `pv-do` (dónde y
escribir), exactamente como en la tabla de responsabilidades. Es el mismo tipo de acceso
que `pv-how` ya tiene sobre `docs.tech` a través de `pv-internal-tech-analysis` (pv-design
línea 217). No se añade capacidad de explorar `sourcecodeDir`.

## Reutilización

- `resolve-path.py` (`.claude/skills/pv-init/scripts/`, `--what styleBibleDocDir`) — el
  mecanismo estándar del framework para resolver rutas de `docs.tech`; mismos códigos de
  salida y mismo tratamiento de fallo (exit 2 → `/pv-init`, exit 3/4 → `/pv-update`) que ya
  usan los demás skills.
- Cascada "style bible poblado → si no, placeholder" — mismo patrón que ya aplica
  `pv-internal-doc-style` ("a folder that holds only its `INDEX.md` means nothing
  documented yet").

## Verificación

1. Releer ambos `SKILL.md` completos: confirmar que la viñeta nueva no contradice las reglas
   existentes (self-contained, sin JS funcional, un fichero por elemento) ni cambia
   "Expected input from the caller".
2. `git diff` de `pv-design.en.md`: confirmar que el cambio se limita a las líneas 233 y 237
   y que las líneas 278-284 (tabla de responsabilidades) no aparecen en el diff.
3. Ejecutar desde la raíz del repo:
   `python .claude/skills/pv-init/scripts/resolve-path.py --what styleBibleDocDir` — debe
   imprimir `.../previo-sdd/docs/style` con exit 0.
4. End-to-end: invocar `/pv-fix` con un cambio visual pequeño en un proyecto con `docs/style`
   poblado y verificar que el `design_*.html` usa los tokens/colores documentados; repetir
   con `docs/style` vacío (solo `INDEX.md`) y verificar que el fichero incluye el comentario
   de placeholder neutro y no invoca ni lee código fuente.
5. `/pv-update`: confirmar que no reporta incoherencias nuevas por la edición de los skills.
