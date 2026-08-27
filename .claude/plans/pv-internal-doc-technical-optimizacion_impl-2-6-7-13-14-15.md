# Plan de implementación — puntos 2, 6, 7, 13, 14, 15

Plan concreto para llevar a `pv-internal-doc-technical` (y a los artefactos que dependen de ella) los puntos aprobados **2, 6, 7, 13, 14 y 15** del documento de ideas `pv-internal-doc-technical-optimizacion_ideas.md`.

- **No cubre**: puntos 5 y 9 (aún `🔍 analizando`), ni 1/3/11 (descartados). Los puntos 4, 10 y 12 se implementan **dentro de** 15 y 13 respectivamente (están absorbidos), no como trabajo aparte.
- **Fuera de alcance de este plan**: la implementación ya existente en `pv-internal-doc-technical-optimizacion_v1.md` (según la nota del documento de ideas, no se toca). Este plan asume que `_v1.md` es un plan hermano y que, si hay solape, se reconcilian antes de ejecutar — ver [§0.3](#03-relación-con-_v1md).

---

## 0. Contexto y decisiones transversales

### 0.1. Artefactos que se tocan

| Artefacto | Rol actual | Qué cambia en este plan |
|---|---|---|
| `.claude/skills/pv-internal-doc-technical/SKILL.md` | Define **qué** contenido va en `architectureDocDir` + **cómo** se escribe (writing rules, para `architectureDocDir` y `styleBibleDocDir`) | Núcleo del plan: nuevas writing rules (2, 6, 7), reescritura de la regla de notación (13), fijar idioma inglés + invertir 2 prohibiciones gramaticales (14), nueva sección de namespace (15) |
| `.claude/skills/pv-internal-doc-style/SKILL.md` | Extiende el writing baseline de `pv-internal-doc-technical` con reglas de estilo propias | Heredar 2/6/7/13; conceptos de estilo entran en el namespace (15); eliminar menciones a `docs.tech.language` (14) |
| `.claude/skills/pv-internal-tech-analysis/SKILL.md` | **Lee** `docs.tech` en la fase de análisis | Enseñarle a resolver rutas de namespace (15), tags `[gotcha]` (2) y la notación del glosario (13) |
| `.claude/skills/pv-do/SKILL.md` | Redacta el contenido y lo escribe a disco; invoca a `pv-internal-doc-technical` | Mantener `00-glossary.md` y las anclas de namespace al documentar (13/15); las 3 menciones a "write it in `docs.tech.language`" → "technical English" (14) |
| `.claude/skills/pv-init/schema.json` | Esquema de `pv-context.json` | **Eliminar** la propiedad `docs.tech.language` y sus menciones (description de `interaction.language`, `_comments`, ejemplo) — §14 |
| `.claude/skills/pv-init/SKILL.md` | Flujo de `pv-init`, incluye las preguntas de idioma | Eliminar la pregunta de idioma de la doc técnica; nota "always technical English" — §14 |
| `.claude/skills/pv-init/scripts/scaffold-project.py` | Crea la estructura inicial de `docs.tech` | Crear semillas `00-glossary.md` (13) y `00-namespace.md` (15). No cambia por 14. |
| `.claude/skills/pv-init/scripts/check-context.py`, `resolve-path.py` | Validan/resuelven `pv-context.json` | Solo **revisión**: confirmar que no referencian `docs.tech.language` (confirmado — sin cambios) — §14 |
| `.claude/skills/pv-update/scripts/audit-context.py` | Audita y repara `pv-context.json` | Reparación automática: eliminar la clave obsoleta `docs.tech.language` (14). Opcional fase 2: validar anclas/rutas de namespace (15) |
| `.claude/skills/pv-update/SKILL.md` | Doc de lo que `pv-update` arregla | Añadir "removes the obsolete `docs.tech.language` key" — §14 |
| `.claude/pv-context.json` (proyecto real) | Config viva | Eliminar `docs.tech.language` (vía `pv-update` o a mano) — §14 |
| `docs.tech.architectureDocDir` / `styleBibleDocDir` del proyecto real | Corpus existente | Migración del contenido ya escrito, incluida la traducción a inglés de la prosa `[motivación]` (§16) |

### 0.2. Orden de ejecución recomendado

Los puntos tienen dependencias entre sí. Orden que minimiza retrabajo:

```
1º  Punto 13  (notación nativa)  ─── es la base: define el catálogo de notación
2º  Punto 6   (notación compacta) ── se integra como una fila del catálogo de 13
3º  Punto 2   (tag [gotcha])      ── writing rule independiente, encaja en la regla 6 actual
4º  Punto 7   (anáfora prohibida) ── writing rule independiente
5º  Punto 15  (namespace)         ── consume el glosario que 13 introdujo; el más pesado
6º  Punto 14  (inglés fijo + quitar docs.tech.language) ── último: toca schema, 4 skills y 2 scripts; se apoya en que 15 ya fijó que los segmentos salen del código
7º  Migración del corpus real     ── una sola pasada aplicando todo
```

### 0.3. Relación con `_v1.md`

Antes de ejecutar: abrir `pv-internal-doc-technical-optimizacion_v1.md` y cotejar. Si `_v1.md` ya reescribió la sección "Writing rules" o "Language-independence" de `SKILL.md`, este plan **parte de esa versión**, no de la actual. Los números de regla ("regla 6", "regla 8") usados aquí son los del `SKILL.md` actual (§ arriba); si `_v1.md` los renumeró, re-anclar.

### 0.4. Versionado

Cada punto es un cambio en el framework mismo → al terminar, `/dev-generate-version` sube la versión de todos los `pv-*/SKILL.md` afectados de forma consistente. No versionar punto a punto; una sola release cuando el bloque 2/6/7/13/14/15 esté completo y migrado.

### 0.5. Criterio de "hecho" para todo el plan

- `SKILL.md` de `pv-internal-doc-technical` contiene las reglas nuevas, sin contradicción interna, y su `description` de frontmatter sigue siendo fiel.
- `pv-internal-tech-analysis` sabe leer todo lo que las reglas nuevas producen.
- Existe `00-glossary.md` (semilla en `scaffold-project.py` + real en el proyecto).
- El corpus `docs.tech` real está migrado y no mezcla estilo viejo y nuevo.
- Una tarea de prueba (`pv-fix` trivial que toque un contrato documentado) recorre análisis→doc sin fricción con el formato nuevo.

---

## Punto 13 — Notación lógico-matemática / formato nativo por defecto; prosa solo excepción

**Estado en ideas**: ✅ aprobado, REFACTORIZADO. Absorbe el punto 12.

### 13.1. Qué se implementa

Reemplazar en `SKILL.md` la actual **regla 4** ("Don't restate what a signature or name already says. Reserve prose for...") y ampliar la **regla 3** (tablas) por una sección nueva **"Notation-first"** que:

1. Declara el principio: notación/formato nativo es el default para todo tipo de contenido; prosa es excepción rara.
2. Incluye el **catálogo contenido→notación** (la tabla del punto 13 del doc de ideas), como tabla normativa en el `SKILL.md`.
3. Incluye la **regla de aprobación endurecida** (checklist obligatorio antes de escribir prosa) del doc de ideas.
4. Incluye la sub-regla **13.6** (invariante ejecutable vs. declarativo — el punto 12 absorbido).
5. Marca la prosa superviviente con `[motivación]` y limita a una frase.

### 13.2. Cambios concretos en `SKILL.md`

| Ubicación | Acción |
|---|---|
| Sección "Writing rules", regla 3 | Mantener; añadir referencia cruzada a "Notation-first" |
| Sección "Writing rules", regla 4 | **Sustituir** por: "Prose is the exception. Every piece of content maps to a native notation (see *Notation-first* below); prose only for an idiosyncratic external constraint, one sentence, tagged `[motivación]`." |
| Nueva sección "## Notation-first" tras "Writing rules" | Añadir: principio + tabla catálogo + checklist de 4 pasos + sub-sección "Invariants: executable vs declarative" |
| Regla 6 (fixed English tags) | Añadir `[motivación]` a la lista de tags como marca de la prosa-excepción |

### 13.3. Contenido de la tabla catálogo (a incrustar en `SKILL.md`, en inglés)

| Content type | Native notation | Prose only when... |
|---|---|---|
| Boolean invariant / pre-post-condition | `assert <expr>` if runtime-checkable; else propositional logic (`pre:`, `post:`, `inv:`, `∧ ∨ ¬ → ⟹ ∀`) | Never (pure structure) |
| Data structure (fields, types, defaults, optionality) | Table or compact BNF (`field: type = default`) — see Punto 6 | Never |
| State machine / transitions | FSM or `(state, event) → state'` table | Never |
| Entity relationship / cardinality | ER diagram or `1---*`, `0..1` notation | Never |
| Temporal sequence / call flow | Sequence diagram (Mermaid) or ordered pseudocode | Never |
| Decision tree / nested conditionals | Boolean table or explicit tree | Never |
| Decision rationale | Rule/condition + comparison table | Only for an idiosyncratic external constraint (compliance, business) not reducible to a condition nor a general engineering principle |
| Side-effect flow | Numbered sequence / event→effect table | Only the single step whose ordering is externally-semantic (UX, business) |

### 13.4. Checklist obligatorio antes de prosa (a incrustar, en inglés)

```
Before writing any prose sentence:
  1. Is it a condition/rule?            → decision table or propositional logic.
  2. Is it one more metric of a comparison already tabulated?  → add a column.
  3. Is it a general engineering principle the reader already infers?  → write nothing (punto 5).
  4. None of the above  → one sentence of prose, tagged [motivación].
Never force prose for elegance, reading flow, or because "it sounds like a trade-off".
```

### 13.5. Sub-sección "Invariants: executable vs declarative" (punto 12 absorbido)

Criterio mecánico a incrustar:

| Question | Yes | No |
|---|---|---|
| Is there a program point where this condition can be checked with the values at hand? | `assert <expr>` | declarative `inv: …` |
| Does it quantify over an abstract set / talk about an FSM state / a non-observable global property? | — | declarative |

Reglas: forma preferente = assert siempre que el criterio dé "sí"; la declarativa es fallback, no estilo alternativo; si conviven, el assert manda y la declarativa se marca como enunciado; sintaxis exacta la fija `00-glossary.md`.

### 13.6. Notas pendientes que este plan NO cierra (quedan como TODO en el glosario)

- **Notación anidada/híbrida** entre tipos de contenido → se resuelve con "referencia por ruta de namespace" una vez el punto 15 esté implementado (ver Punto 15). Hasta entonces: regla provisional "si una notación necesita referirse a otra, cítala por su ancla, no la incrustes".
- **Contenido exacto del `00-glossary.md`** y si se genera una vez o incrementalmente → lo aborda el Punto 15 (§15.5), que es quien crea el glosario de verdad.

### 13.7. Verificación del punto 13

- [ ] `SKILL.md` no contiene ya ninguna instrucción que permita prosa "para explicar" fuera del checklist de 4 pasos.
- [ ] La regla 4 vieja ya no existe con su redacción permisiva.
- [ ] `pv-internal-doc-style/SKILL.md` sigue siendo coherente (su checklist de estilo no pide prosa donde 13 la prohíbe).
- [ ] `pv-internal-tech-analysis` tiene una línea que le dice: "el contenido técnico viene en notación (contratos `pre:/post:`, FSM, tablas, asserts); parséala como tal, no esperes prosa narrativa".

---

## Punto 6 — Notación compacta para datos estructurados

**Estado en ideas**: ✅ aprobado. Es un caso particular de 13 (fila "Data structure" del catálogo).

### 6.1. Qué se implementa

No es una regla aparte de 13, pero merece explicitud porque es de las de ganancia **Alta** y aplica en casi toda tarea. Se implementa como:

1. **Refuerzo de la regla 2 actual** de `SKILL.md` ("Signatures, types and values as code") — ampliarla para cubrir no solo firmas sino cualquier dato estructurado con default/opcionalidad.
2. **Fila explícita en el catálogo de 13** (ya incluida en §13.3): `field: type = default` / marcar opcionalidad con `?` o `(opc)`.
3. **Ejemplo canónico en `SKILL.md`**:
   - MAL: "el método recibe un parámetro opcional que, si no se especifica, toma el valor por defecto de 30 segundos"
   - BIEN: `timeout?: Duration = 30s`

### 6.2. Cambios concretos en `SKILL.md`

| Ubicación | Acción |
|---|---|
| Regla 2 | Reescribir: "Signatures, types, values **and any structured datum (fields, defaults, optionality, ranges)** as code/compact notation, never prose. `field: type = default`, `?` for optional." |
| "Notation-first" tabla | Fila "Data structure" ya lo recoge (§13.3) |
| Ejemplos de `SKILL.md` | Añadir el par MAL/BIEN de arriba |

### 6.3. Convención de notación compacta (a fijar en `00-glossary.md` cuando exista; provisional en `SKILL.md`)

```
field: type                  required field
field?: type                 optional field
field: type = value          default value
field: type ∈ {a, b, c}      enum / allowed set
field: type [min..max]       range
```

### 6.4. Verificación del punto 6

- [ ] La regla 2 cubre explícitamente defaults y opcionalidad, no solo firmas.
- [ ] Hay un ejemplo MAL/BIEN de dato estructurado en prosa vs. notación compacta.
- [ ] La convención `?` / `=` / `∈` / `[..]` está escrita en un solo sitio (glosario provisional o real).

---

## Punto 2 — Tag de anti-expectativa `[gotcha]`

**Estado en ideas**: ✅ aprobado. Ganancia **Alta**.

### 2.1. Qué se implementa

Añadir `[gotcha]` al vocabulario de **fixed English tags** (regla 6 de `SKILL.md`), con semántica específica: marca un hecho que **contradice el patrón por defecto** que un lector con conocimiento general de software asumiría.

### 2.2. Cambios concretos en `SKILL.md`

| Ubicación | Acción |
|---|---|
| Regla 6, lista de tags | Añadir `[gotcha]` junto a `[breaking]`, `[async]`, `[idempotent]`, `[deprecated]` |
| Regla 6, texto | Añadir una frase: "`[gotcha]` marks a fact that contradicts the default assumption a reader would bring from general software patterns (a `delete` that soft-deletes, a `getX` that mutates, a sync-looking call that isn't). Reserve it for genuine anti-expectations, not for every noteworthy detail." |
| Nueva mini-sección o nota bajo regla 6 | Criterio de uso + ejemplo canónico |

### 2.3. Ejemplo canónico (a incrustar)

```
- [gotcha] deleteUser(id) does NOT remove the row — it sets active=false.
```
en vez de
```
- deleteUser(id) marks the user inactive.
```

### 2.4. Interacción con el punto 5 (no implementado aquí)

El punto 2 y el punto 5 son las dos caras: 5 dice "si sigue el default, no lo escribas"; 2 dice "si lo contradice, márcalo `[gotcha]`". Como el punto 5 no se implementa en este plan, dejar en `SKILL.md` una nota: "if a fact matches the default pattern, prefer omitting it (a future rule will make this explicit); if it breaks the pattern, tag it `[gotcha]`."

### 2.5. Verificación del punto 2

- [ ] `[gotcha]` está en la lista de tags fijos, en inglés, marcado como independiente de `docs.tech.language`.
- [ ] Hay criterio explícito de cuándo NO usarlo (no es "dato interesante", es "contradice el prior").
- [ ] `pv-internal-tech-analysis` tiene instrucción de **elevar la atención** sobre líneas `[gotcha]`: son las que corrigen su modelo por defecto, no puede tratarlas como una fila más.
- [ ] `pv-internal-doc-style` hereda el tag (su contenido también puede tener gotchas de estilo: "el sistema de grid NO es de 12 columnas, es de 16").

---

## Punto 7 — Prohibir referencias anafóricas

**Estado en ideas**: ✅ aprobado. Ganancia Media.

### 7.1. Qué se implementa

Nueva **writing rule** en `SKILL.md`: nunca pronombres ni referencias anafóricas ("esto", "dicho campo", "el mismo", "lo anterior") cuando se puede repetir el nombre exacto.

### 7.2. Cambios concretos en `SKILL.md`

| Ubicación | Acción |
|---|---|
| Sección "Writing rules" | Añadir **regla 9**: "No anaphora. Never 'this', 'that field', 'the former', 'the above' when the exact name can be repeated. Repeating the identifier is cheaper for the reader than resolving a referent — and never wrong when two candidates are nearby. Style cost of repetition is not a concern (see Audience)." |
| Interacción con punto 15 | Nota: "when the referent has a namespace path (Punto 15), the repeated form is that canonical path." |

### 7.3. Ejemplo canónico (a incrustar)

```
MAL:  The token carries an expiry. This is checked on every request; if it has passed, the session ends.
BIEN: token.exp is checked on every request. If time > token.exp, the session ends.
```

### 7.4. Relación con el punto 15

El 15 provee el identificador canónico; el 7 obliga a usarlo en vez de una anáfora. El 7 NO queda absorbido por el 15 (su alcance incluye anáforas sobre cosas sin ruta de namespace, p. ej. "el flujo anterior"), pero se subordina: "el identificador válido para citar es la ruta del namespace; nunca una anáfora ni un sinónimo".

### 7.5. Verificación del punto 7

- [ ] La regla 9 existe y menciona explícitamente que el coste de estilo de repetir no cuenta.
- [ ] Hay ejemplo MAL/BIEN.
- [ ] Cross-ref al punto 15 para el caso "el referente tiene ruta canónica".

---

## Punto 15 — Namespace jerárquico único, vinculado al código

**Estado en ideas**: ✅ aprobado. Absorbe puntos 4 y 10. Ganancia **Alta**. Es el punto más pesado.

### 15.1. Qué se implementa

Un **árbol de nombres único por proyecto**, con segmentos separados por puntos, de agregado a detalle. Cada elemento (concepto o afirmación) tiene una ruta canónica única. Los nodos con `ancla:` apuntan al código.

```
auth.token.session                       concepto.  ancla: src/auth/token.ts#SessionToken
auth.token.session.exp                   concepto.  ancla: SessionToken.exp
auth.token.session.ttl                   concepto.  ancla: SESSION_TTL_SECONDS
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
| Leaf `path:` + notation block | terminal segment `:` then a Punto 13 notation block | For non-scalar assertions (a logic expression, a contract). Citable exactly like a `=value` leaf. |
| Branch `path.decision.<slug>` | reserved subtree | Assertion with no code anchor (a design choice). Citable like a leaf. |
| Node with no anchor and no `=` / `:` | — | **Suspicious**: missing anchor, or general knowledge (Punto 5) that shouldn't be named. Validation flags it. |

Frontera concepto/afirmación = **sintáctica**: ¿tiene `= valor`, `:` + bloque, o cuelga de `.decision.`? → afirmación. ¿No? → concepto. Sin juicio.

### 15.3. Dónde vive el namespace

**Decisión a tomar antes de ejecutar** (una de estas):

| Opción | Descripción | Recomendación |
|---|---|---|
| A. Fichero dedicado | `docs.tech/00-namespace.md` con el árbol completo; cada doc cita por ruta | **Recomendada**. Un solo sitio, validable de una pasada, no obliga a tocar cada doc para ver el árbol. |
| B. Distribuido | Cada nodo/hoja se define inline en el doc donde se documenta ese tema; el árbol es la unión | Más local pero re-introduce el problema de "¿dónde está definido X?" que el 15 quiere matar. |
| C. Híbrido | El árbol (rutas + anclas) en `00-namespace.md`; el **cuerpo** de las hojas no escalares en el doc temático, citado por ruta | Compromiso; más piezas que mantener. |

Este plan asume **Opción A** salvo decisión contraria. `00-namespace.md` y `00-glossary.md` (del punto 13) pueden ser el mismo fichero o dos; recomendación: **dos ficheros**, `00-glossary.md` (notación) y `00-namespace.md` (árbol de nombres), ambos semilla en `scaffold-project.py`.

### 15.4. Cambios concretos por artefacto

| Artefacto | Cambio |
|---|---|
| `pv-internal-doc-technical/SKILL.md` | Nueva sección "## Namespace" con las reglas de §15.2; regla en "Writing rules" o en esa sección: "cite any concept or assertion by its canonical namespace path, never re-describe it"; cross-ref desde regla 7 (anáfora) y desde la nota de notación anidada de 13 |
| `pv-internal-doc-style/SKILL.md` | Hereda: los conceptos de estilo (tokens de diseño, componentes) también entran en el namespace (`ui.grid.columns = 16`, `ui.color.primary` con ancla al design token) |
| `pv-internal-tech-analysis/SKILL.md` | Paso nuevo: "cuando el contenido cite una ruta de namespace, resuélvela contra `00-namespace.md`; si el nodo tiene `ancla:`, esa es la definición canónica y prevalece sobre cualquier redacción" — encaja con su regla actual de "code is source of truth" |
| `pv-do/SKILL.md` | Paso nuevo al documentar: "si el cambio añade/renombra un concepto o afirmación citable, actualiza `00-namespace.md` (nueva ruta, o ancla movida); si el símbolo de código cambió de nombre, actualiza la `ancla:` correspondiente" |
| `pv-init/scripts/scaffold-project.py` | Crear `00-namespace.md` semilla (cabecera + convención de orden de segmentos + ejemplo comentado) |
| `pv-update/scripts/audit-context.py` | (Opcional, fase 2) validación: toda `ancla:` de `00-namespace.md` apunta a un `file#symbol` que existe; toda ruta citada en un doc existe en `00-namespace.md` |

### 15.5. Convención de orden de segmentos (nota pendiente del doc de ideas — se decide aquí)

**Regla**: de **agregado a parte** y de **módulo a detalle**. `<área>.<agregado>.<entidad>.<campo-o-afirmación>`.
- `auth.token.session.exp` ✅ (área auth → agregado token → entidad session → campo exp)
- `auth.session.token.exp` ❌ (invierte agregado y entidad)

Autoridad que asigna rutas: `pv-do` al documentar, siguiendo esta regla; ante ambigüedad real, `pv-do` pregunta al usuario (igual que ya hace con dudas de interfaz en `pv-internal-tech-analysis`).

### 15.6. Afirmaciones no escalares (nota pendiente del doc de ideas — se resuelve aquí)

Ya recogido en §15.2, fila "Leaf `path:` + notation block". La hoja **identifica** (nombre estable, citable); su **cuerpo** es un bloque de notación del punto 13. El `00-glossary.md` define la frontera: `= <escalar>` para valores simples (número, enum, booleano); `:` + bloque para afirmaciones con estructura lógica.

### 15.7. Qué NO entra en este plan sobre el 15

- **Incompat. 15.1 (15 ↔ 9)**: a qué nivel del `.md` se ancla la definición cuando el punto 9 imponga secciones fijas. El punto 9 no está aprobado → se deja la Opción A de §15.3 (fichero dedicado), que esquiva el problema. Si el 9 se aprueba luego, revisar.
- **Coste de mantenimiento** al refactorizar código (renombrar símbolo → renombrar ruta): mitigado por la validación opcional de `audit-context.py` (§15.4), pero la reasignación de ruta sigue siendo manual. Aceptado.

### 15.8. Verificación del punto 15

- [ ] `SKILL.md` tiene la sección "## Namespace" con las 5 filas de reglas y la frontera sintáctica concepto/afirmación.
- [ ] Existe decisión registrada sobre §15.3 (Opción A por defecto).
- [ ] `00-namespace.md` semilla creado en `scaffold-project.py`.
- [ ] `pv-internal-tech-analysis` resuelve rutas contra `00-namespace.md` y respeta `ancla:` como fuente de verdad.
- [ ] `pv-do` actualiza `00-namespace.md` al documentar conceptos/afirmaciones nuevos.
- [ ] Regla de orden de segmentos (§15.5) escrita en `00-namespace.md` y en `SKILL.md`.
- [ ] Puntos 4 y 10 marcados en el doc de ideas como cubiertos por esta implementación (ya están `🔀 absorbido`).

---

## Punto 14 — Inglés técnico fijo; se elimina `docs.tech.language`

**Estado en ideas**: ✅ aprobado, con la salvedad explícita de que **revierte una decisión de diseño ya implementada**: la sección "Language-independence" de `SKILL.md` y la opción de configuración `docs.tech.language`. Este plan lo implementa como **cambio no aditivo**: `docs.tech` pasa a estar **siempre en inglés técnico** y `docs.tech.language` **desaparece del framework**. Ganancia Baja (hipótesis de tokenización no medida), pero el punto se aprueba por coherencia con la premisa raíz del documento (optimizar para el lector-modelo, el idioma es una variable más). Se ejecuta el último por su coste de alcance (schema + scripts + skills + migración).

### 14.1. Alcance: se elige 14-full (todo en inglés, sin opción de idioma)

Se descarta la variante "14-notation" (mantener `docs.tech.language` gobernando solo la prosa `[motivación]`). Razones para ir a **14-full**:

- El objetivo del punto 14 es que `docs.tech` sea **monolingüe de principio a fin**. Dejar la prosa `[motivación]` en otro idioma reintroduce la mezcla de idiomas dentro del mismo documento que el punto 14 quiere eliminar.
- Tras 13/6/15 la prosa `[motivación]` es marginal en volumen → traducirla a inglés en la migración es coste bajo, y a partir de ahí `pv-do` la genera directamente en inglés.
- Mantener `docs.tech.language` "solo para una frase ocasional" es una opción de config que casi nunca hace nada: más superficie de configuración, error y drift que valor. Eliminarla simplifica `pv-init`, el schema y cuatro scripts.
- Es lo que el propio doc de ideas describe en "Implicación verificada: revierte esa decisión".

**Consecuencia**: `docs.tech.language` se elimina. `docs.functional.language`, `changes.language`, `versions.language` e `interaction.language` **no se tocan** — el proyecto puede seguir en español en todo lo demás; `docs.tech` queda como isla en inglés, que es el resultado buscado.

### 14.2. Cambios concretos en `pv-internal-doc-technical/SKILL.md`

| Ubicación (líneas actuales) | Acción |
|---|---|
| **Frontmatter `description`** | Quitar la mención a que el estilo aplica "regardless of ... configured `docs.tech.language`"; sustituir por "written in fixed technical English". |
| **Sección "Language."** (línea 18) | Reescribir: "This skill's output and all `docs.tech` content is fixed technical English. There is no `docs.tech.language` option — architecture and style-bible documents are always English, regardless of `interaction.language` or the project's language elsewhere. The caller does not translate; it drafts in English." |
| **Regla 6** (línea 77) | Quitar "regardless of `docs.tech.language`" (ya no existe la opción); dejar "Fixed English tags for recurring properties" a secas. Añadir `[gotcha]` y `[motivación]` a la lista (ver puntos 2 y 13). |
| **Sección "## Language-independence"** (líneas 81-87) | **Renombrar a "## Fixed language: technical English"** y reescribir el cuerpo: ya no es "estas reglas valen para cualquier idioma", es "el documento es inglés técnico; por tanto se permiten técnicas de densidad que dependen de la gramática inglesa". |
| Mismo bloque, viñeta "No telegraphic/headline compression" | **Invertir**: ahora se **permite** la compresión telegráfica del inglés (`user token expired`) porque el idioma es fijo. Mantener solo la advertencia de no volverla ilegible. |
| Mismo bloque, viñeta "No compound-noun stacking" | **Invertir**: se **permite** el compound-noun stacking (`user auth token expiry check`) como técnica de densidad válida, al ser el idioma fijo inglés. |
| Última viñeta ("Everything else ... transfers unchanged to any `docs.tech.language`") | Eliminar (ya no hay "any language" al que transferir). |

> Nota: esto es exactamente lo que la sección actual dice que se dejó fuera **a propósito**. Al fijar el idioma, esas dos técnicas dejan de ser un riesgo de portabilidad y pasan a ser herramientas de densidad recomendadas. El punto 14 no solo cambia el idioma: **desbloquea compresión que hoy está prohibida por portabilidad**.

### 14.3. Cambios en `pv-internal-doc-style/SKILL.md`

| Ubicación (línea 18, "Language.") | Acción |
|---|---|
| Frase "the caller translates as needed when drafting into `docs.tech.language`" | Sustituir por "all `styleBibleDocDir` content is fixed technical English, same as `pv-internal-doc-technical`; there is no `docs.tech.language`." |
| Frase "stay in English regardless of `docs.tech.language`" | Simplificar a "stay in English" (ya es redundante: todo es inglés). |

### 14.4. Cambios en `pv-init`

| Artefacto | Acción |
|---|---|
| `schema.json`, objeto `docs.tech` (líneas ~186-190) | **Eliminar** la propiedad `language` completa (tipo, default `"en"`, description, examples). El objeto `docs.tech` mantiene `required: ["architectureDocDir", "styleBibleDocDir"]` sin cambios. |
| `schema.json`, línea 54 (description de `interaction.language`) | Quitar "docs.tech.language" de la lista "Also the fallback value for changes.language, versions.language, and any docs.*.language block" → dejar "changes.language, versions.language, and docs.functional.language". |
| `schema.json`, líneas ~255-259 (`_comments` de ejemplo) | Eliminar la línea `"docs.tech.language": "Architecture and style bible in English, ..."`. |
| `schema.json`, ejemplo de config (líneas ~244-246) | Quitar `"language": "en"` del bloque `docs.tech` del ejemplo. |
| `SKILL.md`, línea 80 (flujo de preguntas de idioma) | Quitar `docs.tech.language` de la frase "set `changes.language`, `versions.language`, `docs.functional.language` and `docs.tech.language` to the interaction language". |
| `SKILL.md`, línea 84 (pregunta 4, "Language of the technical documentation") | **Eliminar la pregunta 4 entera**. Renumerar: quedan 3 preguntas por área (changes, versions, functional). Añadir una frase: "Technical documentation (`docs.tech`) has no language option — it is always technical English." |
| `scripts/check-context.py` | Revisar: solo referencia `framework.interaction.language` (línea 97) → **sin cambios**. Confirmar que no valida `docs.tech.language` en ningún sitio. |
| `scripts/resolve-path.py` | Resuelve los tres doc dirs (no idioma) → **sin cambios** salvo comprobación. |
| `scripts/scaffold-project.py` | Ya crea la estructura de `docs.tech` (líneas ~172-175) → **sin cambios de idioma**; el cambio de este script es por 13/15 (semillas `00-glossary.md` / `00-namespace.md`), no por 14. |

### 14.5. Cambios en `pv-do/SKILL.md`

| Ubicación (línea 16, "Language.") | Acción |
|---|---|
| "When updating `docs.tech.architectureDocDir`/`styleBibleDocDir` yourself, use `docs.tech.language` (fallback `interaction.language`)" | Sustituir por "always write `docs.tech.architectureDocDir`/`styleBibleDocDir` in technical English — there is no `docs.tech.language`. The source (`plan.md`) may be in `changes.language`; translating to English when writing the reference document is your responsibility." |
| Línea 89 (bloque `architectureDocDir`), "**Write it in `docs.tech.language`** (fallback `interaction.language`), never in `changes.language`" | Sustituir por "**Write it in technical English**, never in `changes.language` — draft fresh in English, don't carry over `plan.md` sentences verbatim." |
| Línea 93 (bloque `styleBibleDocDir`), "**Write it in `docs.tech.language`** ... same rule as `architectureDocDir`" | Igual: "**Write it in technical English**, same rule as `architectureDocDir` above." |

### 14.6. Cambios en `pv-update` (migración de `pv-context.json` existentes)

`pv-update` audita y repara `pv-context.json` contra el schema. Con `docs.tech.language` fuera del schema (`additionalProperties: false` en `docs.tech`), un `pv-context.json` que aún la tenga se vuelve **inválido**.

| Artefacto | Acción |
|---|---|
| `scripts/audit-context.py` | Añadir regla de migración: si `docs.tech.language` existe → **eliminarla** del `pv-context.json` (reparación automática, no destructiva: no cambia paths ni comportamiento, solo quita una clave que ya no se usa). Registrar en el reporte de cambios. |
| `SKILL.md` de `pv-update` | Documentar esa reparación en la lista de cosas que arregla ("removes the obsolete `docs.tech.language` key"). |
| Comportamiento ante `additionalProperties: false` | Confirmar que el validador de schema de `audit-context.py` trata `docs.tech.language` sobrante como "clave obsoleta a eliminar", no como "JSON roto que requiere intervención del usuario" (esa categoría se reserva, según la description de `pv-update`, para JSON no parseable o downgrade de versión). |

### 14.7. Terminología de dominio sin traducción técnica estándar

`docs.tech` es inglés, pero un concepto de negocio del proyecto puede no tener término inglés estándar (p. ej. dominio fiscal español: "recargo de equivalencia"). Regla:

- Si el concepto **tiene símbolo de código**, su ruta de namespace usa el nombre del símbolo (que ya está en el idioma en que se programó — normalmente inglés, y si no, es lo que hay).
- Si **no tiene símbolo de código**, se permite el slug en el idioma del proyecto para ese nodo concreto (`billing.recargo-equivalencia`), documentado como **excepción explícita** en `00-namespace.md` con una nota de una línea de qué es en inglés aproximado.
- La prosa `[motivación]` que acompañe a ese concepto sigue siendo inglés (puede nombrar el término español entre comillas: `[motivación] "recargo de equivalencia" is a Spanish tax surcharge; no standard English term.`).

### 14.8. Verificación del punto 14

- [ ] `docs.tech.language` **eliminada** del schema (`docs.tech` con `additionalProperties: false` la rechaza).
- [ ] `pv-init/SKILL.md`: pregunta 4 de idioma eliminada; flujo "same for everything" ya no setea `docs.tech.language`; nota "technical documentation is always English" añadida.
- [ ] `schema.json`: description de `interaction.language`, `_comments` de ejemplo y bloque de ejemplo ya no mencionan `docs.tech.language`.
- [ ] `pv-do/SKILL.md`: las tres menciones a "write it in `docs.tech.language`" sustituidas por "technical English".
- [ ] `pv-internal-doc-technical/SKILL.md`: sección "Language-independence" renombrada a "Fixed language: technical English"; las dos prohibiciones gramaticales (telegraphic, compound-noun) **invertidas a permitidas**; `description` de frontmatter actualizada.
- [ ] `pv-internal-doc-style/SKILL.md`: menciones a `docs.tech.language` eliminadas.
- [ ] `pv-update/audit-context.py`: elimina `docs.tech.language` de `pv-context.json` existentes como reparación automática; documentado en su `SKILL.md`.
- [ ] `check-context.py` / `resolve-path.py` / `scaffold-project.py` revisados: no referencian `docs.tech.language` (confirmado, sin cambios por el punto 14).
- [ ] Regla de excepción para slugs de dominio sin término inglés (§14.7) escrita en `00-namespace.md`.
- [ ] `pv-context.json` del proyecto real: `docs.tech.language` eliminada.

---

## 16. Migración del corpus `docs.tech` existente

Una sola pasada, tras implementar 13/6/2/7/15/14 en las skills.

### 16.1. Procedimiento

1. **Inventario**: listar todos los ficheros de `docs.tech.architectureDocDir` y `styleBibleDocDir` del proyecto real.
2. **Por fichero, en orden de dependencia** (los que definen conceptos base primero):
   - Extraer conceptos y afirmaciones → alta en `00-namespace.md` con su `ancla:` (punto 15).
   - Convertir prosa estructural a notación según el catálogo de 13 (contratos→`pre:/post:`, listas de campos→notación compacta de 6, flujos→secuencia/tabla, decisiones→tabla comparativa).
   - Sustituir toda anáfora por el nombre exacto o la ruta de namespace (punto 7).
   - Marcar con `[gotcha]` los hechos que hoy están redactados como normales pero contradicen el patrón por defecto (punto 2).
   - Dejar en prosa `[motivación]` (una frase) solo lo que pase el checklist de 4 pasos de 13; **traducida a inglés** (punto 14 — ya no hay `docs.tech.language`).
3. **Crear `00-glossary.md`** con la notación efectivamente usada (símbolos de contrato, convención de notación compacta, formato de tablas de decisión, sintaxis de assert) y `00-namespace.md` con el árbol completo.
4. **Eliminar `docs.tech.language`** de `.claude/pv-context.json` (o ejecutar `/pv-update`, que ahora lo repara automáticamente — §14.6).
5. **Validación final**: ejecutar `/pv-update` — schema OK sin `docs.tech.language`, anclas de namespace resuelven, rutas citadas existen, ningún fichero mezcla estilo viejo y nuevo.

### 16.2. Verificación de la migración

- [ ] Ningún fichero de `docs.tech` contiene prosa narrativa fuera de frases `[motivación]` de una línea, y esas están en inglés.
- [ ] `00-glossary.md` y `00-namespace.md` existen y son consistentes con lo que los docs citan.
- [ ] Toda estructura de datos está en notación compacta; todo contrato en `pre:/post:`; toda FSM en tabla/diagrama.
- [ ] `.claude/pv-context.json` ya no tiene `docs.tech.language`; `/pv-update` no reporta nada pendiente.
- [ ] Una tarea de prueba (`pv-fix` trivial sobre un contrato documentado) recorre `pv-internal-tech-analysis` → `pv-do` sin ambigüedad con el formato nuevo.

---

## 17. Resumen de cambios por fichero

| Fichero | Puntos que lo tocan | Naturaleza del cambio |
|---|---|---|
| `pv-internal-doc-technical/SKILL.md` | 2, 6, 7, 13, 14, 15 | Reglas nuevas (2/6/7), sección "Notation-first" (13, absorbe 12), sección "Namespace" (15, absorbe 4/10), "Language-independence" → "Fixed language: technical English" con las dos prohibiciones gramaticales **invertidas a permitidas** (14), `description` de frontmatter |
| `pv-internal-doc-style/SKILL.md` | 2, 6, 7, 13, 14, 15 | Herencia de 2/6/7/13; conceptos de estilo entran en el namespace (15); eliminar menciones a `docs.tech.language` (14) |
| `pv-internal-tech-analysis/SKILL.md` | 2, 13, 15 | Leer notación como tal; elevar atención en `[gotcha]`; resolver rutas de namespace contra `00-namespace.md` |
| `pv-do/SKILL.md` | 13, 14, 15 | Mantener `00-glossary.md` y `00-namespace.md` al documentar (13/15); las 3 menciones a "write it in `docs.tech.language`" → "technical English" (14) |
| `pv-init/schema.json` | 14 | **Eliminar** la propiedad `docs.tech.language` (tipo, default, description, examples); limpiar su mención en la description de `interaction.language`, en `_comments` y en el ejemplo de config |
| `pv-init/SKILL.md` | 14 | Eliminar la pregunta 4 de idioma (technical doc); el flujo "same for everything" ya no setea `docs.tech.language`; nota "technical documentation is always English" |
| `pv-init/scripts/scaffold-project.py` | 13, 15 | Semillas `00-glossary.md` y `00-namespace.md`. (No cambia por 14 — no referencia idioma.) |
| `pv-init/scripts/check-context.py`, `resolve-path.py` | 14 (verificación) | Revisar que no referencian `docs.tech.language` — confirmado, sin cambios; se listan para dejar constancia de la revisión |
| `pv-update/scripts/audit-context.py` | 14, 15 | 14: eliminar la clave obsoleta `docs.tech.language` de `pv-context.json` existentes como reparación automática. 15 (opcional): validar anclas y rutas de namespace |
| `pv-update/SKILL.md` | 14 | Documentar la reparación "removes the obsolete `docs.tech.language` key" en la lista de lo que `pv-update` arregla |
| `.claude/pv-context.json` (proyecto real) | 14 | Eliminar `docs.tech.language` (lo hará `pv-update`, o a mano) |
| Corpus `docs.tech` real | todos | Migración §16 (incluye traducir a inglés la prosa `[motivación]` superviviente) |

## 18. Checklist global de cierre

- [ ] §0.3 hecho: `_v1.md` cotejado, sin solapes sin reconciliar.
- [ ] Puntos 13 → 6 → 2 → 7 → 15 → 14 implementados en ese orden.
- [ ] Los 6 bloques de verificación por punto (§13.7, §6.4, §2.5, §7.5, §15.8, §14.8) pasados.
- [ ] Punto 14: `docs.tech.language` no aparece en **ningún** artefacto del framework (grep en `.claude/skills/` y `schema.json` = 0 resultados salvo, si acaso, en changelog histórico).
- [ ] Migración §16 completada y su verificación (§16.2) pasada; `/pv-update` limpio.
- [ ] `pv-internal-doc-technical/SKILL.md` sin contradicción interna; `description` de frontmatter revisada y fiel (ya no promete independencia de idioma).
- [ ] Doc de ideas actualizado: puntos 2/6/7/13/14/15 marcados como implementados (nota "implementado en `_impl-2-6-7-13-14-15.md`"); el punto 14 además deja constancia de que `docs.tech.language` se eliminó.
- [ ] `/dev-generate-version` ejecutado: versión consistente en todos los `pv-*/SKILL.md` afectados (doc-technical, doc-style, tech-analysis, do, init, update).
