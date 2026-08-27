> **ESTADO: APLICADO** (2026-08-27). Decisiones finales tomadas con el usuario, distintas del borrador:
> - **`required` estricto SÍ** en `schema.json` (`framework.required:["docs"]`, `docs.required:["functional","tech"]`, y `featuresDocPathDir`/`architectureDocDir`/`styleBibleDocDir`). `check-context.py` los comprueba y los reporta en `missingRequired`; si no está vacío en un proyecto ya inicializado → rama `S1Broken` → `pv-update`.
> - **Sin flag `--only` en `scaffold-project.py`**: `pv-update` crea el dir + `INDEX.md` a mano con la plantilla de `*-missing-index`.
> - **Bump de versión: SÍ**, las 21 `pv-*/SKILL.md` a `0.9.6b5`.
> - **`sourcecodeDir`**: la cláusula "fallback cuando architectureDocDir no existe" se reescribió a redacción neutra (raíz de exploración de código de `pv-internal-tech-analysis` cuando la doc no basta).
> - El nuevo problema de `audit-context.py` es `docs-dir-unconfigured:<field>` (severity `required`).

# Plan: eliminar el "opcional" residual de la documentación técnica/funcional

## Objetivo

Reflejar en todo el framework la realidad de que `docs.tech.architectureDocDir`,
`docs.tech.styleBibleDocDir` y `docs.functional.featuresDocPathDir` **siempre están
configurados** (los crea `pv-init` en cada init, sin preguntar). El `OPTIONAL` del schema y
los ~8 *"if not configured, skip without asking"* repartidos por las skills son un residuo de
un diseño anterior. Si a un `pv-context.json` le falta uno (edición a mano, versión antigua
del framework), es un **estado roto** que `pv-update` repara — ninguna skill de flujo lo
tolera.

## Matiz importante

"Carpeta configurada pero **vacía**" ≠ "campo no configurado". `styleBibleDocDir` puede
quedar legítimamente sin contenido si el proyecto no tiene capa visual
(`pv-init/SKILL.md` ya lo contempla), pero el **campo y la carpeta con placeholder existen
igual**. Este plan no cambia eso: solo elimina la posibilidad de que el campo esté ausente.

## Decisiones tomadas (con el usuario)

- Los tres doc dirs pasan a ser **obligatorios de facto**.
- La obligatoriedad se **documenta** (schema, `pv-design.*`, SKILL.md) y la **impone
  `pv-update`** (recrea el dir ausente), **no** el validador de forma (`check-context.py` /
  JSON Schema `required`), para no reventar en proyectos a medio migrar antes de que
  `pv-update` pueda actuar.
- Se **elimina** el comportamiento de `pv-init` de "borrar el campo si el usuario dice que no
  quiere mantener esa doc" — se sustituye por "carpeta con placeholder, puede quedar vacía".

---

## Parte A — `schema.json`

`.claude/skills/pv-init/schema.json`

- **NO** añadir los tres campos a `required` (ver "Decisiones"). Mantener
  `additionalProperties: false` + descripciones.
- `docs` (objeto): `description` → *"Written by `pv-init` on every init; all three doc dirs
  are always present. A `pv-context.json` missing any of them is a broken state, repaired by
  `pv-update` — the other skills never tolerate a missing doc dir."*
- `functional` y `tech` (objetos): actualizar `description` en la misma línea.
- `featuresDocPathDir`, `architectureDocDir`, `styleBibleDocDir`: en cada `description`,
  quitar el `"OPTIONAL. "` inicial y sustituir *"If not configured, this step is skipped
  without asking anything"* por *"Always configured by `pv-init`. If absent from
  `pv-context.json`, run `/pv-update` — every skill requires it."*
- Conservar en las tres la nota *"relative to workFolder, not the repo root"* (ya está).
- Revisar `$defs` y ejemplos por menciones a "optional" de estos campos.

---

## Parte B — `pv-design.es.md` + `pv-design.en.md`

### B1. Sección "The `pv-context.json` file" → subsección "Documentation"

`.claude/pv-doc/pv-design/pv-design.en.md` (líneas ~411-419) y su equivalente ES.

- Quitar *"(object, optional)"* de `docs` y los *"(string, optional)"* de los tres paths.
  Reemplazar por *"Always written by `pv-init`. All three live under `workFolder`."*
- Sustituir el párrafo final (*"Any `docs` field left unconfigured means the corresponding
  step is skipped without asking anything — the framework works the same either way…"*) por:

  > `pv-init` always configures all three. A `pv-context.json` missing any of them
  > (hand-edited, or from a framework version before they became mandatory) is a broken
  > state: the skill that hits it stops and sends the user to `/pv-update`, which recreates
  > the missing dir with its placeholder. `styleBibleDocDir` may legitimately be **empty**
  > (a project with no visual layer) — that is not the same as unconfigured.

### B2. Sección "Responsibilities of each skill"

`.claude/pv-doc/pv-design/pv-design.en.md` (líneas ~75-315) + ES.

- Buscar menciones de "optional" / "if not configured" / "if configured" para los doc dirs
  en las entradas de `pv-init`, `pv-how`, `pv-do`, `pv-fix`, `pv-new` y actualizarlas al
  nuevo modelo. (Explorar en implementación; estimado 2-5 toques.)

---

## Parte C — Skills

Patrón: sustituir *"X is optional; if not configured, skip without asking"* por *"X is always
configured; if it can't be resolved, stop and tell the user to run `/pv-update`"*.
(El **cómo** se obtiene la ruta — `resolve-path.py` — es el otro plan; aquí solo el lenguaje
de obligatoriedad y el flujo de error.)

### C1. `pv-do` — `SKILL.md`

- Línea ~36: *"`docs.tech.architectureDocDir`, `docs.functional.featuresDocPathDir` and
  `docs.tech.styleBibleDocDir` are optional and used in step 2.1; if not configured, skip the
  corresponding updates without asking anything"* → *"…are always configured. In step 2.1
  resolve each; if any can't be resolved, stop before touching docs and tell the user to run
  `/pv-update`."*
- Línea ~81: *"If `docs.functional.featuresDocPathDir` isn't configured, skip this point
  without asking anything"* → flujo de error.
- Línea ~90 (reporte): sin cambio de fondo.
- Revisar paso 2.1 completo (líneas 66-82, varias truncadas en el grep).

### C2. `pv-how` — `SKILL.md`

- Línea ~36: quitar *"are optional and used as context in step 3; if not configured, proceed
  without them (use the repo in general as fallback context)"*. El fallback a "el repo en
  general" desaparece: los doc dirs siempre están; si no resuelven, es `/pv-update`.
  - **Ojo** con `sourcecodeDir`: ese sí conserva su rol de fallback context de `pv-how`
    cuando `architectureDocDir` "no existe como carpeta real" — pero con este plan
    `architectureDocDir` siempre existe, así que ese fallback pierde sentido. Revisar
    `pv-how` paso 3 y `schema.json` de `sourcecodeDir` (*"Used by pv-how as fallback context
    … only when docs.tech.architectureDocDir doesn't exist as a real folder"*) y decidir:
    o se elimina esa cláusula, o se reinterpreta como "cuando `architectureDocDir` está
    vacío/placeholder". **Punto abierto 1.**
- Líneas ~109-110, secciones (c)/(d) del plan: *"if `docs.tech.architectureDocDir` is
  configured and this solution modifies the project's core architecture"* → quitar
  *"is configured and"*; la condición real para incluir la sección es solo *"this solution
  modifies architecture"*. Idem (d) con `styleBibleDocDir`.
- Conservar el párrafo del paso 3.5 sobre no acusar a `pv-context.json` (ya añadido).
- `PLAN.template.md` líneas 20 y 24: *"Only if `docs.tech.architectureDocDir` is configured
  and this solution modifies…"* → *"Only if this solution modifies the project's core
  architecture."* Idem estilo.

### C3. `pv-fix` — `SKILL.md`

- Líneas ~63-65 (criterios `fast`): *"If the change affects `docs.tech.architectureDocDir` or
  `docs.tech.styleBibleDocDir` (if configured in `.claude/pv-context.json`) only in constant
  or parameter values, it's `fast`"* → quitar *"(if configured in `.claude/pv-context.json`)"*.
- Línea ~55: *"it reads the configured `framework.docs.tech` documentation first"* — ajustar
  redacción para no implicar opcionalidad.
- Revisar líneas 33, 87, 91, 114 (truncadas) por menciones a docs opcionales.

### C4. `pv-new` — `SKILL.md`

- Revisar línea ~30 y contexto. Si condiciona algo a "si `docs.*` está configurado",
  eliminarlo.

### C5. `pv-init` — `SKILL.md`

- Línea ~87: reforzar *"all three are always generated, without exception"* añadiendo:
  *"They are not optional in practice — the schema's wording is only about init-time merge
  behavior. A `pv-context.json` missing any is repaired by `pv-update`, never tolerated by
  the other skills."*
- **Línea ~93 — se elimina el comportamiento**: hoy dice *"If the user **explicitly decides
  they don't want one of the three** … delete what `scaffold-project.py` generated for that
  field … and leave the field undefined in `pv-context.json` — the rest of the skills treat
  it as optional and skip it"*. Reescribir a: *"If the user doesn't want to actively maintain
  one of the three (e.g. no interest in a style guide), keep the field and the scaffolded dir
  with its placeholder — they can simply leave it empty. Never delete the field: every other
  skill now requires all three to be configured."*
- Línea ~90 (carpeta fuera de `workFolder`, ofrecer moverla): **mantener**, es correcto.
- `check-context.py`: revisar su noción de "unconfigured optionals"
  (`pv-init/SKILL.md:55,61`). Si cuenta un doc dir ausente como "optional pendiente" que
  `pv-init` ofrece completar en `S1AskComplete`, ajustar para que un doc dir ausente sea
  tratado como problema que se delega a `pv-update` (rama `S1Broken`), no como optional
  normal. **Leer el script en implementación. Punto abierto 2.**

### C6. `pv-internal-doc-features` — `SKILL.md`

- Línea ~46: *"If `docs.functional.featuresDocPathDir` isn't configured in
  `.claude/pv-context.json`, say so and stop — it's up to the caller to decide what to do
  (normally, skip the step without asking anything)"* → *"…the doc dir is always configured;
  if it can't be resolved, stop and report to the caller that the framework config is broken
  and the user must run `/pv-update`."*

### C7. `pv-internal-doc-technical` / `pv-internal-doc-style` — `SKILL.md`

- Revisar por menciones a opcionalidad de `architectureDocDir` / `styleBibleDocDir`.
  Probablemente sin cambios (reciben contexto del caller), pero verificar.

---

## Parte D — `pv-update`: mecanismo de reparación

### D1. `audit-context.py`

`.claude/skills/pv-update/scripts/audit-context.py`

- Hoy: `if functional.get("featuresDocPathDir"):` / `if tech.get("architectureDocDir"):` /
  `if tech.get("styleBibleDocDir"):` (líneas ~363-371) — solo comprueba el dir **si** el
  campo está.
- **Añadir**: cuando el campo **no** está en `pv-context.json`, emitir un problema nuevo
  `docs-dir-unconfigured:<field>` con `severity: required`, `field` = ruta del campo,
  `message` explicando que `pv-init` siempre lo configura y que hay que recrearlo con el
  default del schema.
- Mantener `<field>-missing-dir` para el caso "campo configurado pero carpeta ausente".
- Comentario nuevo cerca de `check_docs_dir`: *"resolution logic kept in sync with
  `pv-init/scripts/resolve-path.py` — change both together."*

### D2. `pv-update` — `SKILL.md`

- Paso 3, lista de fixes — **añadir entrada** para `docs-dir-unconfigured:*`:

  > **`docs-dir-unconfigured:*`**: the field is missing from `pv-context.json` entirely.
  > Write it with the schema default (`docs/architecture` / `docs/style` / `docs/features`,
  > relative to `workFolder`) and run `scaffold-project.py` to create the empty dir with its
  > `INDEX.md` placeholder. Never leave a doc dir unconfigured — every other skill now
  > requires all three.

- Línea ~66 (`sourcecodedir-missing` / `framework.docs.*-missing-dir`): añadir el matiz de
  que ahora también puede llegar el caso "campo ausente" (→ escribir default + scaffold).
- Línea ~19 (*"It owns everything beyond 'which optional fields were never configured'"*):
  actualizar — los doc dirs ya no son "optional fields the user may skip"; un doc dir ausente
  es competencia de `pv-update`.
- Línea ~39 (explicación de `severity`): sin cambio (sigue siendo required/optional según
  campo configurado); `docs-dir-unconfigured` entra como `required`.

### D3. `scaffold-project.py`

`.claude/skills/pv-init/scripts/scaffold-project.py`

- Ya recibe rutas resueltas y crea placeholders (líneas 5-6, 164-170).
- Verificar/añadir soporte para recrear **solo un** doc dir concreto (invocación desde
  `pv-update` para un `docs-dir-unconfigured:*` aislado), sin rehacer todo el scaffold.
  Posible flag `--only <path>` o `--doc-dir <path>`. **Leer en implementación. Punto
  abierto 3.**

---

## Parte E — `pv-version` / `copy-docs.py`

`.claude/skills/pv-version/scripts/copy-docs.py`

- Hoy resuelve los tres dirs y tiene un `skipped` para los ausentes (líneas 17, 107-109).
- Con este plan los tres siempre existen. Cambiar: un doc dir que no resuelve deja de ser
  `skipped` silencioso y pasa a ser un **error a stderr** (`copy-docs.py` no debería
  encontrarse nunca un doc dir ausente si `pv-update` hizo su trabajo).
- Actualizar el docstring (líneas 5-9) y el ejemplo de salida (línea 17) para reflejarlo.
- `workflow.version.md` línea ~47 (nodo *"Run copy-docs.py: zip configured docs.tech/
  docs.functional"*): actualizar descripción si cambia el comportamiento observable.
- **No** migrar a `resolve-path.py` (es determinista, no adivina).

---

## Parte F — Verificación

### F1. Deterministas (comandos, en conversación)

- `audit-context.py` en este repo (tiene los tres configurados) → **no** debe aparecer
  `docs-dir-unconfigured`, ni falsos `*-missing-dir`.
- Test aislado en scratchpad: `pv-context.json` sin `docs.tech` → `audit-context.py` (vía
  import de funciones o copia temporal) debe reportar `docs-dir-unconfigured:framework.docs.
  tech.architectureDocDir` y `...styleBibleDocDir`.
- `scaffold-project.py --only <path>` (si se implementa) → crea solo ese dir + `INDEX.md`.

### F2. Consistencia cruzada (grep)

- `grep -rn "if not configured\|isn't configured\|is configured and\|are optional\|(if
  configured" .claude/skills/**/SKILL.md .claude/skills/**/*.template.md` → cero resultados
  relativos a doc dirs.
- `grep -rn "optional" .claude/pv-doc/pv-design/` → ninguna referencia a los tres doc dirs
  como opcionales.
- `grep -rn "fallback context\|repo in general" .claude/skills/pv-how/` → coherente con la
  decisión del punto abierto 1.

### F3. Flujos end-to-end

- `pv-how` sobre una entrada real → secciones (c)/(d) del plan se incluyen/omiten según
  "¿toca arquitectura/estilo?", nunca según "¿está configurado?".
- Proyecto sano (los tres dirs presentes) → ningún cambio de comportamiento observable salvo
  la desaparición del falso positivo original.

### F4. Versión del framework

- Todas las `pv-*/SKILL.md` a `0.9.6b4` hoy. Este plan + el otro tocan muchas skills.
  Opciones: (a) subir todas a `0.9.6b5` con edición manual de `metadata.version` en cada
  `SKILL.md` (tocadas y no tocadas, para no disparar `skill-version-mismatch` en
  `audit-context.py`); (b) seguir en `b4` por ser la misma beta en curso. **Punto abierto 4.**
- **No** ejecutar `dev-generate-version` ni regenerar `pv-changelog.*` — eso es un release
  formal, gesto del usuario.

---

## Puntos abiertos a confirmar durante la implementación

1. `sourcecodeDir` como fallback context de `pv-how` cuando `architectureDocDir` "no existe":
   con este plan siempre existe. ¿Se elimina la cláusula, o se reinterpreta como
   "`architectureDocDir` vacío/placeholder"?
2. `check-context.py`: ¿cómo clasifica hoy un doc dir ausente y qué hay que ajustar para que
   caiga en la rama `S1Broken` (→ `pv-update`) y no en `S1AskComplete`?
3. `scaffold-project.py`: ¿necesita flag `--only <path>` para recreación puntual?
4. Versión: ¿bump global a `b5` o seguir en `b4`?
5. `schema.json`: confirmado que **no** se usa `required` estricto — ¿de acuerdo?

---

## Orden de implementación

1. **Parte A** (schema) + **Parte B** (pv-design) — la doc canónica primero.
2. **Parte D** (`audit-context.py` + `pv-update` + `scaffold-project.py`) — el mecanismo de
   reparación debe existir antes de declarar los campos obligatorios en las skills.
3. **Parte C** (skills de flujo).
4. **Parte E** (`copy-docs.py`).
5. **Parte F** (verificación).

## Relación con el otro plan

`resolve-path-script.md` (el script `resolve-path.py`) depende de que este plan haya
declarado los doc dirs obligatorios y dado a `pv-update` el mecanismo de recreación, porque
su contrato de error es "exit 3 (campo ausente) → la skill va a `/pv-update`". Implementar
**Partes A, B y D de este plan primero**, luego el otro plan completo, luego Parte C y E de
este. (Parte C de ambos planes toca los mismos SKILL.md — hacerlas en una sola pasada por
fichero para no editar dos veces.)
