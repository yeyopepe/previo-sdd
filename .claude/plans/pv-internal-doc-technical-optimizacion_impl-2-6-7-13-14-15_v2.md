# Plan de implementación v2 — puntos 2, 7, 13 (+6), 14, 15

Plan concreto para llevar a `pv-internal-doc-technical` (y a los artefactos que dependen de ella) los puntos aprobados **2, 6, 7, 13, 14 y 15** del documento de ideas `pv-internal-doc-technical-optimizacion_ideas.md`.

**Qué cambia respecto a v1** (`_impl-2-6-7-13-14-15.md`): mismo contenido técnico, menos estructura. El punto 6 se absorbe dentro del 13 (era un caso particular de su catálogo); la migración del corpus se reduce a una nota (no hay corpus en disco); se elimina el cotejo con `_v1.md` (ese fichero no existe); se corrige el supuesto sobre `audit-context.py` (no valida contra schema); glosario y namespace pasan a ser **un solo fichero**; los 8 bloques de verificación se colapsan en uno.

- **No cubre**: puntos 5 y 9 (aún `🔍 analizando`), ni 1/3/11 (descartados). Los puntos 4, 10 y 12 se implementan **dentro de** 15 y 13 respectivamente (absorbidos), no como trabajo aparte. El punto 6 se implementa dentro del 13 (§13.7).

---

## 0. Contexto y decisiones transversales

### 0.1. Artefactos que se tocan

| Artefacto | Rol actual | Qué cambia en este plan |
|---|---|---|
| `.claude/skills/pv-internal-doc-technical/SKILL.md` | Define **qué** contenido va en `architectureDocDir` + **cómo** se escribe (writing rules, para `architectureDocDir` y `styleBibleDocDir`) | Núcleo del plan: nuevas writing rules (2, 7), sección "Notation-first" (13, absorbe 6 y 12), sección "Namespace" (15, absorbe 4 y 10), idioma inglés fijo + inversión de 2 prohibiciones gramaticales (14) |
| `.claude/skills/pv-internal-doc-style/SKILL.md` | Extiende el writing baseline de `pv-internal-doc-technical` con reglas de estilo propias | Heredar 2/7/13; conceptos de estilo entran en el namespace (15); eliminar menciones a `docs.tech.language` (14) |
| `.claude/skills/pv-internal-tech-analysis/SKILL.md` | **Lee** `docs.tech` en la fase de análisis | Enseñarle a leer notación como tal (13), elevar atención sobre `[gotcha]` (2) y resolver rutas de namespace (15) |
| `.claude/skills/pv-do/SKILL.md` | Redacta el contenido y lo escribe a disco; invoca a `pv-internal-doc-technical` | Mantener `00-namespace.md` al documentar (13/15); las 3 menciones a "write it in `docs.tech.language`" → "technical English" (14) |
| `.claude/skills/pv-init/schema.json` | Esquema de `pv-context.json` | **Eliminar** la propiedad `docs.tech.language` y sus menciones (description de `interaction.language`, `_comments`, ejemplo) — §14 |
| `.claude/skills/pv-init/SKILL.md` | Flujo de `pv-init`, incluye las preguntas de idioma | Eliminar la pregunta de idioma de la doc técnica; nota "always technical English" — §14 |
| `.claude/skills/pv-init/scripts/scaffold-project.py` | Crea la estructura inicial de `docs.tech` | Crear semilla `00-namespace.md` (13/15). No cambia por 14. |
| `.claude/skills/pv-update/scripts/audit-context.py` | Audita `pv-context.json` (diagnóstico read-only) | Detectar la clave obsoleta `docs.tech.language` — requiere mecanismo nuevo, ver §14.6 |
| `.claude/skills/pv-update/SKILL.md` | Doc de lo que `pv-update` arregla | Añadir "removes the obsolete `docs.tech.language` key" — §14 |
| `.claude/pv-context.json` (proyecto real) | Config viva | Eliminar `docs.tech.language` y su `_comments` — §16 |

`pv-init/scripts/check-context.py` y `resolve-path.py`: **revisados, sin cambios**. `check-context.py` solo referencia `framework.interaction.language`; `resolve-path.py` resuelve los tres doc dirs, no idiomas. Se listan aquí solo para dejar constancia de la revisión.

### 0.2. Orden de ejecución

Los puntos tienen dependencias entre sí. Orden que minimiza retrabajo:

```
1º  Punto 13 (+6)  (notación nativa)   ─── base: define el catálogo de notación y la notación compacta
2º  Punto 2        (tag [gotcha])      ─── writing rule independiente, encaja en la regla 6 actual
3º  Punto 7        (anáfora prohibida) ─── writing rule independiente
4º  Punto 15       (namespace)         ─── consume la notación que 13 introdujo; el más pesado
5º  Punto 14       (inglés fijo)       ─── último: toca schema, 4 skills y 1 script; se apoya en que 15 ya fijó que los segmentos salen del código
```

### 0.3. Decisión: un solo fichero `00-namespace.md`

El árbol de nombres (punto 15) y la notación (punto 13) viven en **un único fichero** `docs.tech.architectureDocDir/00-namespace.md`, con dos secciones:

- `## Notation` — símbolos de contrato, convención compacta, formato de tablas de decisión, sintaxis de assert, y la frontera `= <escalar>` vs `:` + bloque.
- `## Tree` — el árbol de rutas con sus `anchor:`.

**Motivo**: están acoplados. La frontera `=` vs `:` que define la sección `Notation` es exactamente la que la sección `Tree` necesita para clasificar sus hojas (§15.4); el árbol no se puede leer sin la notación de sus hojas. Dos ficheros separados = dos semillas en `scaffold-project.py`, dos ficheros que `pv-do` debe recordar mantener y dos que `pv-internal-tech-analysis` debe leer, sin ganancia.

Descartado también el namespace **distribuido** (definir cada nodo inline en su doc temático): reintroduce el problema de "¿dónde está definido X?" que el punto 15 existe para matar. Como efecto colateral, esta decisión esquiva el conflicto 15 ↔ punto 9 (a qué nivel del `.md` se ancla una definición si el 9 impone secciones fijas): con fichero dedicado, no hay conflicto. Si el punto 9 se aprueba luego, revisar.

### 0.4. Versionado

Cada punto es un cambio en el framework mismo → al terminar, `/dev-generate-version` sube la versión de todos los `pv-*/SKILL.md` afectados de forma consistente. No versionar punto a punto; una sola release cuando el bloque completo esté implementado.

---

## Punto 13 — Notación lógico-matemática / formato nativo por defecto; prosa solo excepción

**Estado en ideas**: ✅ aprobado, REFACTORIZADO. Absorbe los puntos 12 (§13.5) y 6 (§13.7).

### 13.1. Qué se implementa

Reemplazar en `SKILL.md` la actual **regla 4** ("Don't restate what a signature or name already says. Reserve prose for...") y ampliar la **regla 3** (tablas) por una sección nueva **"Notation-first"** que:

1. Declara el principio: notación/formato nativo es el default para todo tipo de contenido; prosa es excepción rara.
2. Incluye el **catálogo contenido→notación** como tabla normativa.
3. Incluye la **regla de aprobación endurecida** (checklist obligatorio antes de escribir prosa).
4. Incluye la sub-regla de invariante ejecutable vs. declarativo (punto 12 absorbido).
5. Incluye la notación compacta para datos estructurados (punto 6 absorbido).
6. Marca la prosa superviviente con `[motivación]` y limita a una frase.

### 13.2. Cambios concretos en `SKILL.md`

| Ubicación | Acción |
|---|---|
| Regla 2 | Reescribir: "Signatures, types, values **and any structured datum (fields, defaults, optionality, ranges)** as code/compact notation, never prose. `field: type = default`, `?` for optional." (punto 6) |
| Regla 3 | Mantener; añadir referencia cruzada a "Notation-first" |
| Regla 4 | **Sustituir** por: "Prose is the exception. Every piece of content maps to a native notation (see *Notation-first* below); prose only for an idiosyncratic external constraint, one sentence, tagged `[motivación]`." |
| Nueva sección "## Notation-first" tras "Writing rules" | Añadir: principio + tabla catálogo (§13.3) + checklist de 4 pasos (§13.4) + sub-sección "Invariants: executable vs declarative" (§13.5) + notación compacta (§13.7) |
| Regla 6 (fixed English tags) | Añadir `[motivación]` a la lista de tags como marca de la prosa-excepción |

### 13.3. Tabla catálogo (a incrustar en `SKILL.md`, en inglés)

| Content type | Native notation | Prose only when... |
|---|---|---|
| Boolean invariant / pre-post-condition | `assert <expr>` if runtime-checkable; else propositional logic (`pre:`, `post:`, `inv:`, `∧ ∨ ¬ → ⟹ ∀`) | Never (pure structure) |
| Data structure (fields, types, defaults, optionality) | Table or compact notation (`field: type = default`) — see §13.7 | Never |
| State machine / transitions | FSM or `(state, event) → state'` table | Never |
| Entity relationship / cardinality | ER diagram or `1---*`, `0..1` notation | Never |
| Temporal sequence / call flow | Sequence diagram (Mermaid) or ordered pseudocode | Never |
| Decision tree / nested conditionals | Boolean table or explicit tree | Never |
| Decision rationale | Rule/condition + comparison table | Only for an idiosyncratic external constraint (compliance, business) not reducible to a condition nor a general engineering principle |
| Side-effect flow | Numbered sequence / event→effect table | Only the single step whose ordering is externally-semantic (UX, business) |

**Notación anidada**: si una notación necesita referirse a otra, cítala por su ruta de namespace (punto 15), no la incrustes.

### 13.4. Checklist obligatorio antes de prosa (a incrustar, en inglés)

```
Before writing any prose sentence:
  1. Is it a condition/rule?            → decision table or propositional logic.
  2. Is it one more metric of a comparison already tabulated?  → add a column.
  3. Is it a general engineering principle the reader already infers?  → write nothing.
  4. None of the above  → one sentence of prose, tagged [motivación].
Never force prose for elegance, reading flow, or because "it sounds like a trade-off".
```

### 13.5. Sub-sección "Invariants: executable vs declarative" (punto 12 absorbido)

Criterio mecánico a incrustar:

| Question | Yes | No |
|---|---|---|
| Is there a program point where this condition can be checked with the values at hand? | `assert <expr>` | declarative `inv: …` |
| Does it quantify over an abstract set / talk about an FSM state / a non-observable global property? | — | declarative |

Reglas: forma preferente = assert siempre que el criterio dé "sí"; la declarativa es fallback, no estilo alternativo; si conviven, el assert manda y la declarativa se marca como enunciado; sintaxis exacta la fija la sección `## Notation` de `00-namespace.md`.

### 13.6. Ejemplos canónicos a incrustar en `SKILL.md`

```
MAL:  el método recibe un parámetro opcional que, si no se especifica, toma el valor por defecto de 30 segundos
BIEN: timeout?: Duration = 30s
```

### 13.7. Notación compacta para datos estructurados (punto 6 absorbido)

**Estado en ideas**: ✅ aprobado, ganancia **Alta**. Es la fila "Data structure" del catálogo (§13.3), explicitada aquí por su frecuencia de uso. Se materializa en la reescritura de la regla 2 (§13.2), el ejemplo de §13.6 y esta convención, que va a la sección `## Notation` de `00-namespace.md` (provisional en `SKILL.md` hasta que exista el fichero):

```
field: type                  required field
field?: type                 optional field
field: type = value          default value
field: type ∈ {a, b, c}      enum / allowed set
field: type [min..max]       range
```

---

## Punto 2 — Tag de anti-expectativa `[gotcha]`

**Estado en ideas**: ✅ aprobado. Ganancia **Alta**.

### 2.1. Qué se implementa

Añadir `[gotcha]` al vocabulario de **fixed English tags** (regla 6 de `SKILL.md`), con semántica específica: marca un hecho que **contradice el patrón por defecto** que un lector con conocimiento general de software asumiría.

### 2.2. Cambios concretos en `SKILL.md`

| Ubicación | Acción |
|---|---|
| Regla 6, lista de tags | Añadir `[gotcha]` junto a `[breaking]`, `[async]`, `[idempotent]`, `[deprecated]` |
| Regla 6, texto | Añadir: "`[gotcha]` marks a fact that contradicts the default assumption a reader would bring from general software patterns (a `delete` that soft-deletes, a `getX` that mutates, a sync-looking call that isn't). Reserve it for genuine anti-expectations, not for every noteworthy detail." |
| Nota bajo regla 6 | Criterio de uso + ejemplo canónico (§2.3) + nota de interacción con el punto 5 (§2.4) |

### 2.3. Ejemplo canónico (a incrustar)

```
BIEN: - [gotcha] deleteUser(id) does NOT remove the row — it sets active=false.
MAL:  - deleteUser(id) marks the user inactive.
```

### 2.4. Interacción con el punto 5 (no implementado aquí)

El punto 2 y el punto 5 son las dos caras: 5 dice "si sigue el default, no lo escribas"; 2 dice "si lo contradice, márcalo `[gotcha]`". Como el punto 5 no se implementa en este plan, dejar en `SKILL.md` una nota: "if a fact matches the default pattern, prefer omitting it (a future rule will make this explicit); if it breaks the pattern, tag it `[gotcha]`."

### 2.5. Herencia y consumo

- `pv-internal-doc-style` hereda el tag: su contenido también puede tener gotchas de estilo ("el sistema de grid NO es de 12 columnas, es de 16").
- `pv-internal-tech-analysis` recibe instrucción de **elevar la atención** sobre líneas `[gotcha]`: son las que corrigen su modelo por defecto, no puede tratarlas como una fila más.

---

## Punto 7 — Prohibir referencias anafóricas

**Estado en ideas**: ✅ aprobado. Ganancia Media.

### 7.1. Qué se implementa

Nueva **writing rule 9** en `SKILL.md`: nunca pronombres ni referencias anafóricas ("esto", "dicho campo", "el mismo", "lo anterior") cuando se puede repetir el nombre exacto.

### 7.2. Cambios concretos en `SKILL.md`

| Ubicación | Acción |
|---|---|
| Sección "Writing rules" | Añadir **regla 9**: "No anaphora. Never 'this', 'that field', 'the former', 'the above' when the exact name can be repeated. Repeating the identifier is cheaper for the reader than resolving a referent — and never wrong when two candidates are nearby. Style cost of repetition is not a concern (see Audience)." |
| Misma regla, cross-ref | "When the referent has a namespace path (see *Namespace*), the repeated form is that canonical path." |

### 7.3. Ejemplo canónico (a incrustar)

```
MAL:  The token carries an expiry. This is checked on every request; if it has passed, the session ends.
BIEN: token.exp is checked on every request. If time > token.exp, the session ends.
```

### 7.4. Relación con el punto 15

El 15 provee el identificador canónico; el 7 obliga a usarlo en vez de una anáfora. El 7 **no** queda absorbido por el 15 (su alcance incluye anáforas sobre cosas sin ruta de namespace, p. ej. "el flujo anterior"), pero se subordina: "el identificador válido para citar es la ruta del namespace; nunca una anáfora ni un sinónimo".

---

## Punto 15 — Namespace jerárquico único, vinculado al código

**Estado en ideas**: ✅ aprobado. Absorbe puntos 4 y 10. Ganancia **Alta**. Es el punto más pesado.

### 15.1. Qué se implementa

Un **árbol de nombres único por proyecto**, con segmentos separados por puntos, de agregado a detalle. Cada elemento (concepto o afirmación) tiene una ruta canónica única. Los nodos con `anchor:` apuntan al código.

```
auth.token.session                       concepto.  anchor: src/auth/token.ts#SessionToken
auth.token.session.exp                   concepto.  anchor: SessionToken.exp
auth.token.session.ttl                   concepto.  anchor: SESSION_TTL_SECONDS
auth.token.session.ttl.value = 3600      afirmación (escalar)
auth.token.session.refresh.rule:         afirmación (no escalar → bloque de notación 13)
    pre:  state ∈ {AUTHENTICATED, EXPIRED} ∧ now - token.exp < 7d
    post: token'.exp = now + auth.token.session.ttl.value
auth.decision.circuit-breaker-over-retry decisión.  sin ancla de código
```

### 15.2. Reglas del árbol (a incrustar en `SKILL.md`, nueva sección "## Namespace")

| Element | Form | Rule |
|---|---|---|
| Node with code anchor | `path` + `anchor: file#symbol` | Canonical name **is** the path; definition lives in code. Uniqueness is structural. Absorbs Punto 10 (single term per concept). |
| Leaf `path = value` | terminal segment `= <scalar>` | The citable unit across docs: `see auth.token.session.ttl.value`. One citation syntax project-wide. Absorbs Punto 4 (stable citable IDs). |
| Leaf `path:` + notation block | terminal segment `:` then a notation block (§13.3) | For non-scalar assertions (a logic expression, a contract). Citable exactly like a `=value` leaf. |
| Branch `path.decision.<slug>` | reserved subtree | Assertion with no code anchor (a design choice). Citable like a leaf. |
| Node with no anchor and no `=` / `:` | — | **Suspicious**: missing anchor, or general knowledge that shouldn't be named. |

Frontera concepto/afirmación = **sintáctica**: ¿tiene `= valor`, `:` + bloque, o cuelga de `.decision.`? → afirmación. ¿No? → concepto. Sin juicio.

### 15.3. Convención de orden de segmentos

**Regla**: de **agregado a parte** y de **módulo a detalle**. `<área>.<agregado>.<entidad>.<campo-o-afirmación>`.

- `auth.token.session.exp` ✅ (área auth → agregado token → entidad session → campo exp)
- `auth.session.token.exp` ❌ (invierte agregado y entidad)

Autoridad que asigna rutas: `pv-do` al documentar, siguiendo esta regla; ante ambigüedad real, `pv-do` pregunta al usuario (igual que ya hace con dudas de interfaz en `pv-internal-tech-analysis`). La regla se escribe en `SKILL.md` y en la semilla de `00-namespace.md`.

### 15.4. Afirmaciones no escalares

Ya recogido en §15.2, fila "Leaf `path:` + notation block". La hoja **identifica** (nombre estable, citable); su **cuerpo** es un bloque de notación del punto 13. La sección `## Notation` de `00-namespace.md` define la frontera: `= <escalar>` para valores simples (número, enum, booleano); `:` + bloque para afirmaciones con estructura lógica.

### 15.5. Cambios concretos por artefacto

| Artefacto | Cambio |
|---|---|
| `pv-internal-doc-technical/SKILL.md` | Nueva sección "## Namespace" con las reglas de §15.2, la frontera sintáctica y el orden de segmentos (§15.3); regla "cite any concept or assertion by its canonical namespace path, never re-describe it"; cross-ref desde la regla 9 (anáfora) y desde la nota de notación anidada de §13.3 |
| `pv-internal-doc-style/SKILL.md` | Hereda: los conceptos de estilo (tokens de diseño, componentes) también entran en el namespace (`ui.grid.columns = 16`, `ui.color.primary` con ancla al design token) |
| `pv-internal-tech-analysis/SKILL.md` | Paso nuevo: "cuando el contenido cite una ruta de namespace, resuélvela contra `00-namespace.md`; si el nodo tiene `anchor:`, esa es la definición canónica y prevalece sobre cualquier redacción" — encaja con su regla actual de "code is source of truth". Añadir también: "el contenido técnico viene en notación (contratos `pre:/post:`, FSM, tablas, asserts); parséala como tal, no esperes prosa narrativa" (punto 13) |
| `pv-do/SKILL.md` | Paso nuevo al documentar: "si el cambio añade/renombra un concepto o afirmación citable, actualiza `00-namespace.md` (nueva ruta, o ancla movida); si el símbolo de código cambió de nombre, actualiza la `anchor:` correspondiente" |
| `pv-init/scripts/scaffold-project.py` | Crear semilla `00-namespace.md` (cabecera + sección `## Notation` con las convenciones de §13.7 y §13.5 + sección `## Tree` con la regla de orden de segmentos y un ejemplo comentado) |

### 15.6. Qué NO entra en este plan

**Coste de mantenimiento** al refactorizar código (renombrar símbolo → renombrar ruta): la reasignación de ruta es manual. Aceptado. Una validación automática de anclas (`anchor:` apunta a un `file#symbol` que existe; toda ruta citada existe en `00-namespace.md`) es candidata a una fase 2 en `audit-context.py`, fuera de este plan.

---

## Punto 14 — Inglés técnico fijo; se elimina `docs.tech.language`

**Estado en ideas**: ✅ aprobado, con la salvedad explícita de que **revierte una decisión de diseño ya implementada**: la sección "Language-independence" de `SKILL.md` y la opción de configuración `docs.tech.language`. Este plan lo implementa como **cambio no aditivo**: `docs.tech` pasa a estar **siempre en inglés técnico** y `docs.tech.language` **desaparece del framework**. Ganancia Baja (hipótesis de tokenización no medida), pero el punto se aprueba por coherencia con la premisa raíz del documento (optimizar para el lector-modelo, el idioma es una variable más). Se ejecuta el último por su coste de alcance.

### 14.1. Alcance: se elige 14-full (todo en inglés, sin opción de idioma)

Se descarta la variante "14-notation" (mantener `docs.tech.language` gobernando solo la prosa `[motivación]`). Razones para ir a **14-full**:

- El objetivo del punto 14 es que `docs.tech` sea **monolingüe de principio a fin**. Dejar la prosa `[motivación]` en otro idioma reintroduce la mezcla de idiomas dentro del mismo documento que el punto 14 quiere eliminar.
- Tras 13/15 la prosa `[motivación]` es marginal en volumen → `pv-do` la genera directamente en inglés.
- Mantener `docs.tech.language` "solo para una frase ocasional" es una opción de config que casi nunca hace nada: más superficie de configuración, error y drift que valor. Eliminarla simplifica `pv-init` y el schema.
- Es lo que el propio doc de ideas describe en "Implicación verificada: revierte esa decisión".

**Consecuencia**: `docs.tech.language` se elimina. `docs.functional.language`, `changes.language`, `versions.language` e `interaction.language` **no se tocan** — el proyecto puede seguir en español en todo lo demás; `docs.tech` queda como isla en inglés, que es el resultado buscado.

### 14.2. Cambios en `pv-internal-doc-technical/SKILL.md`

| Ubicación | Acción |
|---|---|
| **Frontmatter `description`** | Quitar la mención a que el estilo aplica "regardless of ... configured `docs.tech.language`"; sustituir por "written in fixed technical English". |
| **Sección "Language."** | Reescribir: "This skill's output and all `docs.tech` content is fixed technical English. There is no `docs.tech.language` option — architecture and style-bible documents are always English, regardless of `interaction.language` or the project's language elsewhere. The caller does not translate; it drafts in English." |
| **Regla 6** | Quitar "regardless of `docs.tech.language`" (ya no existe la opción); dejar "Fixed English tags for recurring properties" a secas. Añadir `[gotcha]` y `[motivación]` a la lista (puntos 2 y 13). |
| **Sección "## Language-independence"** | **Renombrar a "## Fixed language: technical English"** y reescribir el cuerpo: ya no es "estas reglas valen para cualquier idioma", es "el documento es inglés técnico; por tanto se permiten técnicas de densidad que dependen de la gramática inglesa". |
| Viñeta "No telegraphic/headline compression" | **Invertir**: ahora se **permite** la compresión telegráfica del inglés (`user token expired`) porque el idioma es fijo. Mantener solo la advertencia de no volverla ilegible. |
| Viñeta "No compound-noun stacking" | **Invertir**: se **permite** el compound-noun stacking (`user auth token expiry check`) como técnica de densidad válida, al ser el idioma fijo inglés. |
| Última viñeta ("Everything else ... transfers unchanged to any `docs.tech.language`") | Eliminar (ya no hay "any language" al que transferir). |

> Nota: esto es exactamente lo que la sección actual dice que se dejó fuera **a propósito**. Al fijar el idioma, esas dos técnicas dejan de ser un riesgo de portabilidad y pasan a ser herramientas de densidad recomendadas. El punto 14 no solo cambia el idioma: **desbloquea compresión que hoy está prohibida por portabilidad**.

### 14.3. Cambios en `pv-internal-doc-style/SKILL.md`

| Ubicación (sección "Language.") | Acción |
|---|---|
| "the caller translates as needed when drafting into `docs.tech.language`" | Sustituir por "all `styleBibleDocDir` content is fixed technical English, same as `pv-internal-doc-technical`; there is no `docs.tech.language`." |
| "stay in English regardless of `docs.tech.language`" | Simplificar a "stay in English" (ya es redundante: todo es inglés). |

### 14.4. Cambios en `pv-init`

| Artefacto | Acción |
|---|---|
| `schema.json`, objeto `docs.tech` (líneas ~186-190) | **Eliminar** la propiedad `language` completa (tipo, default, description, examples). El objeto `docs.tech` mantiene `required: ["architectureDocDir", "styleBibleDocDir"]` sin cambios. |
| `schema.json`, línea 54 (description de `interaction.language`) | Quitar "any docs.*.language block" → dejar "changes.language, versions.language, and docs.functional.language". |
| `schema.json`, líneas ~255-259 (`_comments` de ejemplo) | Eliminar la línea `"docs.tech.language": "Architecture and style bible in English, ..."`. |
| `schema.json`, ejemplo de config (línea ~246) | Quitar `"language": "en"` del bloque `docs.tech` del ejemplo. |
| `SKILL.md`, línea ~80 (flujo de preguntas de idioma) | Quitar `docs.tech.language` de la frase "set `changes.language`, `versions.language`, `docs.functional.language` and `docs.tech.language` to the interaction language". |
| `SKILL.md`, línea ~84 (pregunta 4, "Language of the technical documentation") | **Eliminar la pregunta 4 entera**. Renumerar: quedan 3 preguntas por área (changes, versions, functional). Añadir: "Technical documentation (`docs.tech`) has no language option — it is always technical English." |
| `scripts/scaffold-project.py` | Sin cambios por 14 (no referencia idioma); su cambio es la semilla `00-namespace.md` de §15.5. |

### 14.5. Cambios en `pv-do/SKILL.md`

| Ubicación | Acción |
|---|---|
| Línea ~16, "Language." | "When updating `docs.tech.architectureDocDir`/`styleBibleDocDir` yourself, use `docs.tech.language` (fallback `interaction.language`)" → "always write `docs.tech.architectureDocDir`/`styleBibleDocDir` in technical English — there is no `docs.tech.language`. The source (`plan.md`) may be in `changes.language`; translating to English when writing the reference document is your responsibility." |
| Línea ~89 (bloque `architectureDocDir`) | "**Write it in `docs.tech.language`** (fallback `interaction.language`), never in `changes.language`" → "**Write it in technical English**, never in `changes.language` — draft fresh in English, don't carry over `plan.md` sentences verbatim." |
| Línea ~93 (bloque `styleBibleDocDir`) | "**Write it in `docs.tech.language`** ... same rule as `architectureDocDir`" → "**Write it in technical English**, same rule as `architectureDocDir` above." |

### 14.6. Detección de la clave obsoleta en `pv-update` — [gotcha] el mecanismo asumido no existe

**Verificado en el código**: `audit-context.py` **no valida contra `schema.json`**. Sus chequeos son ad-hoc, y su detección de claves desconocidas (`unknown-top-level-field`, `unknown-framework-field`, líneas 288-304) solo recorre **dos niveles**: las claves de `context` y las de `framework`. **No baja a `framework.docs.tech`**. Además, `schemaOk` se deriva de esos mismos `id` (línea 486), no de una validación de schema real.

Consecuencia: quitar `docs.tech.language` del `schema.json` **no basta** — sin trabajo adicional, un `pv-context.json` que conserve la clave pasaría silencioso indefinidamente, y `pv-update` reportaría el fichero como correcto.

| Artefacto | Acción |
|---|---|
| `scripts/audit-context.py` | Añadir una constante `OBSOLETE_KEYS` con la ruta `framework.docs.tech.language` y un chequeo que emita un problema propio (`obsolete-field:framework.docs.tech.language`, severidad `required`) cuando la clave exista. ~6 líneas; no exige generalizar el recorrido de claves desconocidas a `docs.*`. |
| `SKILL.md` de `pv-update` | Documentar la reparación en la lista de cosas que arregla: "removes the obsolete `docs.tech.language` key". |

**Alternativa descartada** (fuera de alcance de este plan): extender el recorrido de `unknown-*-field` a los subobjetos de `docs.*`. Es más correcto en general y detectaría futuras claves obsoletas sin listarlas una a una, pero es alcance nuevo que el punto 14 no pide. Candidata a fase 2 junto con la validación de anclas de §15.6.

### 14.7. Terminología de dominio sin traducción técnica estándar

`docs.tech` es inglés, pero un concepto de negocio del proyecto puede no tener término inglés estándar (p. ej. dominio fiscal español: "recargo de equivalencia"). Regla:

- Si el concepto **tiene símbolo de código**, su ruta de namespace usa el nombre del símbolo (que ya está en el idioma en que se programó — normalmente inglés, y si no, es lo que hay).
- Si **no tiene símbolo de código**, se permite el slug en el idioma del proyecto para ese nodo concreto (`billing.recargo-equivalencia`), documentado como **excepción explícita** en `00-namespace.md` con una nota de una línea de qué es en inglés aproximado.
- La prosa `[motivación]` que acompañe a ese concepto sigue siendo inglés (puede nombrar el término español entre comillas: `[motivación] "recargo de equivalencia" is a Spanish tax surcharge; no standard English term.`).

Esta regla se escribe en la semilla de `00-namespace.md`.

---

## 16. Migración

**Verificado en el repo**: `docs.tech.architectureDocDir` (`docs/architecture`) y `styleBibleDocDir` (`docs/style`) **no existen en disco**. No hay corpus que migrar — la §16 del plan v1 describía una pasada sobre cero ficheros.

Lo único que procede hoy:

1. Eliminar `"language": "es"` del bloque `framework.docs.tech` de `.claude/pv-context.json`.
2. Eliminar la línea `"docs.tech.language"` de `framework._comments` del mismo fichero.
3. Ajustar la línea `"interaction.language"` de `_comments`, que menciona "cualquier docs.*.language".
4. Ejecutar `/pv-update` y comprobar que reporta limpio (con el chequeo de §14.6 ya implementado, debe detectar la clave si se olvida el paso 1).

**Si en el futuro existe corpus** en `docs.tech`, aplicar en una sola pasada por fichero: extraer conceptos y afirmaciones a `00-namespace.md` con su `anchor:` (15); convertir prosa estructural a notación según el catálogo (13); sustituir anáforas por el nombre exacto o la ruta (7); marcar `[gotcha]` los hechos que contradicen el patrón por defecto (2); dejar en prosa `[motivación]` en inglés solo lo que pase el checklist de 4 pasos (13/14).

---

## 17. Checklist de cierre

Un solo bloque de verificación para todo el plan.

**Punto 13 (+6)**
- [ ] `SKILL.md` no contiene ya ninguna instrucción que permita prosa "para explicar" fuera del checklist de 4 pasos.
- [ ] La regla 4 vieja ya no existe con su redacción permisiva.
- [ ] La regla 2 cubre explícitamente defaults y opcionalidad, no solo firmas; hay ejemplo MAL/BIEN de dato estructurado.
- [ ] La convención `?` / `=` / `∈` / `[..]` está escrita en un solo sitio (semilla de `00-namespace.md`, sección `## Notation`).
- [ ] `pv-internal-doc-style/SKILL.md` sigue siendo coherente (su checklist de estilo no pide prosa donde 13 la prohíbe).
- [ ] `pv-internal-tech-analysis` sabe que el contenido viene en notación y debe parsearla como tal.

**Punto 2**
- [ ] `[gotcha]` está en la lista de tags fijos, con criterio explícito de cuándo NO usarlo (no es "dato interesante", es "contradice el prior").
- [ ] `pv-internal-tech-analysis` eleva la atención sobre líneas `[gotcha]`.
- [ ] `pv-internal-doc-style` hereda el tag.

**Punto 7**
- [ ] La regla 9 existe, menciona que el coste de estilo de repetir no cuenta, y tiene ejemplo MAL/BIEN.
- [ ] Cross-ref a "Namespace" para el caso "el referente tiene ruta canónica".

**Punto 15**
- [ ] `SKILL.md` tiene la sección "## Namespace" con las 5 filas de reglas, la frontera sintáctica concepto/afirmación y el orden de segmentos.
- [ ] Semilla `00-namespace.md` creada en `scaffold-project.py`, con sus dos secciones (`## Notation`, `## Tree`), la regla de orden de segmentos y la excepción de §14.7.
- [ ] `pv-internal-tech-analysis` resuelve rutas contra `00-namespace.md` y respeta `anchor:` como fuente de verdad.
- [ ] `pv-do` actualiza `00-namespace.md` al documentar conceptos/afirmaciones nuevos.

**Punto 14**
- [ ] `docs.tech.language` eliminada del schema; description de `interaction.language`, `_comments` de ejemplo y bloque de ejemplo ya no la mencionan.
- [ ] `pv-init/SKILL.md`: pregunta 4 eliminada y renumerada; flujo "same for everything" ya no la setea; nota "always technical English" añadida.
- [ ] `pv-do/SKILL.md`: las 3 menciones sustituidas por "technical English".
- [ ] `pv-internal-doc-technical/SKILL.md`: sección renombrada a "Fixed language: technical English"; las dos prohibiciones gramaticales **invertidas a permitidas**; `description` de frontmatter actualizada y fiel (ya no promete independencia de idioma).
- [ ] `pv-internal-doc-style/SKILL.md`: menciones eliminadas.
- [ ] `audit-context.py`: chequeo `obsolete-field` implementado y probado contra un `pv-context.json` que aún tenga la clave; documentado en `pv-update/SKILL.md`.

**Global**
- [ ] `grep -rn "docs.tech.language" .claude/skills/ .claude/pv-context.json` = 0 resultados (salvo changelog histórico).
- [ ] `.claude/pv-context.json` migrado (§16) y `/pv-update` reporta limpio.
- [ ] `pv-internal-doc-technical/SKILL.md` sin contradicción interna.
- [ ] Doc de ideas actualizado: puntos 2/6/7/13/14/15 marcados como implementados, con nota "implementado en `_impl-2-6-7-13-14-15_v2.md`"; el punto 14 deja constancia de que `docs.tech.language` se eliminó.
- [ ] Una tarea de prueba (`pv-fix` trivial que toque un contrato documentado) recorre `pv-internal-tech-analysis` → `pv-do` sin fricción con el formato nuevo.
- [ ] `/dev-generate-version` ejecutado: versión consistente en todos los `pv-*/SKILL.md` afectados (doc-technical, doc-style, tech-analysis, do, init, update).
