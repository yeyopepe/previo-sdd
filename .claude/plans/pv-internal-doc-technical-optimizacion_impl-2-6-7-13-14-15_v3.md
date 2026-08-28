# Plan de implementación — documentación técnica densa para lector-modelo

Plan completo y autocontenido. Lleva a `pv-internal-doc-technical` y a los artefactos que dependen de ella ocho bloques de cambio para la documentación técnica (`docs.tech.architectureDocDir` y `docs.tech.styleBibleDocDir`), partiendo de la premisa de que esos documentos los lee un modelo (`pv-internal-tech-analysis`, y desde ahí `pv-do`/`pv-how`), no una persona.

| # | Cambio | Ganancia |
|---|---|---|
| A | **Notación nativa por defecto**, prosa solo excepción tasada. Incluye notación compacta para datos estructurados e invariantes como asserts. | Alta |
| B | **Tag `[gotcha]`** para hechos que contradicen el patrón por defecto. | Alta |
| C | **Namespace jerárquico único**, vinculado al código. Da identidad canónica a cada concepto y afirmación. | Alta |
| D | **Prohibir anáforas** ("esto", "dicho campo"): repetir el nombre exacto. | Media |
| E | **Prohibir intensificadores sin cifra** ("muy rápido", "poco frecuente"). | Baja |
| F | **Inglés técnico fijo**; se elimina la opción `docs.tech.language`. | Baja |
| G | **Verificación**: `pv-update` detecta y repara lo que A-F introducen. | — |
| H | **Documentación del framework**: `pv-doc/` deja de describir un framework que ya no existe. | — |

---

## 0. Contexto y decisiones transversales

### 0.1. Artefactos que se tocan

| Artefacto | Rol actual | Qué cambia |
|---|---|---|
| `.claude/skills/pv-internal-doc-technical/SKILL.md` | Define **qué** contenido va en `architectureDocDir` + **cómo** se escribe (writing rules, para `architectureDocDir` y `styleBibleDocDir`) | Núcleo: writing rules nuevas (B, D, E), sección "Notation-first" (A), sección "Namespace" (C), idioma inglés fijo + inversión de 2 prohibiciones gramaticales (F) |
| `.claude/skills/pv-internal-doc-style/SKILL.md` | Extiende el writing baseline de `pv-internal-doc-technical` | Hereda A/B/D/E; conceptos de estilo entran en el árbol único (§0.4); eliminar menciones a `docs.tech.language` (F) |
| `.claude/skills/pv-internal-tech-analysis/SKILL.md` | **Lee** `docs.tech` en la fase de análisis | Leer notación como tal (A), elevar atención sobre `[gotcha]` (B), resolver rutas de namespace (C) |
| `.claude/skills/pv-do/SKILL.md` | Redacta el contenido y lo escribe a disco | Mantener `00-namespace.md` al documentar (A/C) — editándolo directamente, no vía `upsert` (§0.3); las 3 menciones a "write it in `docs.tech.language`" → "technical English" (F) |
| `.claude/skills/pv-internal-doc-files/SKILL.md` + `.claude/skills/pv-internal-doc-files/scripts/rebuild-index.py` + `.claude/skills/pv-internal-doc-files/scripts/next-feature-number.py` | Gestiona las tres carpetas de doc (numeración `{NNN}`, `INDEX.md`) | Excluir el prefijo `00-` del glob, igual que ya excluyen `INDEX.md` (§0.3) |
| `.claude/skills/pv-init/schema.json` | Esquema de `pv-context.json` | **Eliminar** la propiedad `docs.tech.language` y sus 4 menciones (§F.4) |
| `.claude/skills/pv-init/SKILL.md` | Flujo de `pv-init`, incluye las preguntas de idioma | Eliminar la pregunta 4 de idioma; nota "always technical English" (§F.4) |
| `.claude/skills/pv-init/scripts/scaffold-project.py` | Crea la estructura inicial de `docs.tech` | Crear semilla `00-namespace.md` en `architectureDocDir` (§C.7) |
| `.claude/skills/pv-update/scripts/audit-context.py` | Audita `pv-context.json` (**read-only, diagnóstico**) | Clave obsoleta `docs.tech.language` (§F.6) + chequeos de namespace (§G) |
| `.claude/skills/pv-update/SKILL.md` | Flujo de auditoría + fix loop | Entradas nuevas en el fix loop para los `id` nuevos (§F.6, §G) |
| `.claude/pv-doc/pv-design/pv-design.es.md` + `.claude/pv-doc/pv-guide.es.md` | Documentan el framework a un lector humano | Actualizar lo que A-G invalidan (§H). **Solo las versiones `.es.md`**; las `.en.md` se traducen después |
| `.claude/pv-context.json` (proyecto real) | Config viva | Eliminar `docs.tech.language` y ajustar `_comments` (§17) |

**Revisados, sin cambios** (constancia de la revisión): `.claude/skills/pv-init/scripts/check-context.py` solo referencia `framework.interaction.language`; `.claude/skills/pv-init/scripts/resolve-path.py` resuelve los tres doc dirs, no idiomas.

### 0.2. Orden de ejecución

```
1º  A  (notación nativa)      ─── base: define el catálogo de notación y la notación compacta
2º  B  (tag [gotcha])         ─── writing rule independiente, encaja en la regla 6 actual
3º  D  (anáfora prohibida)    ─── writing rule independiente → regla 9
4º  E  (intensificadores)     ─── writing rule independiente → regla 10
5º  C  (namespace)            ─── consume la notación que A introdujo; el más pesado
6º  F  (inglés fijo)          ─── toca schema, 4 skills y 2 scripts
7º  G  (verificación)         ─── al final: sus chequeos validan lo que A-F crean
8º  H  (doc del framework)    ─── el último: describe el estado final, ya implementado
```

Dentro de C, el cambio en `pv-internal-doc-files` (§0.3) va **primero**: sin él, la semilla que `.claude/skills/pv-init/scripts/scaffold-project.py` escribe rompe el `INDEX.md` del primer proyecto que se inicialice.

G va al final porque sus chequeos fallarían en cadena si se implementan antes de que exista lo que validan.

### 0.3. Dónde vive el namespace — [gotcha] `architectureDocDir` no es una carpeta libre

**Verificado en el código.** La carpeta la gobierna `pv-internal-doc-files`:

- `.claude/skills/pv-internal-doc-files/scripts/rebuild-index.py` (línea 38): `for path in sorted(folder.glob("*.md"))`, y solo salta `INDEX.md`. Cualquier otro `.md` entra en el índice generado como si fuera un fichero de tema.
- `.claude/skills/pv-internal-doc-files/scripts/next-feature-number.py`: mismo glob, y calcula el `NNN` siguiente leyendo el `# {NNN} — {title}` de la primera línea de cada fichero.
- `pv-do` **no escribe directamente** en `architectureDocDir`: invoca `pv-internal-doc-files` con `action=upsert`, que asigna el número y regenera el índice.

Un `00-namespace.md` colocado a mano, por tanto: (a) aparecería en `INDEX.md` mezclado con los temas, (b) no encaja en la convención `{NNN}-{slug}.md`, y (c) `pv-do` no tiene hoy ninguna vía para editarlo.

**Decisión: fichero especial excluido del índice.**

| Aspecto | Resolución |
|---|---|
| Ubicación | `{architectureDocDir}/00-namespace.md` |
| Convención | El prefijo `00-` queda **reservado** para ficheros de infraestructura de la carpeta, excluidos del índice y de la numeración. Se documenta en `.claude/skills/pv-internal-doc-files/SKILL.md` junto a la regla de `INDEX.md`. |
| `.claude/skills/pv-internal-doc-files/scripts/rebuild-index.py` | Ampliar el filtro: además de `INDEX.md`, saltar todo `path.name.startswith("00-")`. |
| `.claude/skills/pv-internal-doc-files/scripts/next-feature-number.py` | Mismo filtro, para que un `00-*` nunca influya en el número siguiente. |
| Escritura | `pv-do` edita `00-namespace.md` **directamente** (Read/Edit), no vía `upsert`. `upsert` sigue siendo la única vía para los ficheros de tema. |
| Coste | ~4 líneas en dos scripts + una regla en `.claude/skills/pv-internal-doc-files/SKILL.md`. |

### 0.4. Un solo árbol, en `architectureDocDir`

El namespace cubre `architectureDocDir` y `styleBibleDocDir`, que son dos carpetas distintas gestionadas por separado. **Decisión: un único árbol por proyecto**, en `{architectureDocDir}/00-namespace.md`.

- `styleBibleDocDir` **no** tiene semilla de namespace propia: sus conceptos (tokens de diseño, componentes) cuelgan de una rama del mismo árbol (`ui.grid.columns = 16`, `ui.color.primary` con ancla al design token).
- Motivo: el namespace existe para que cada concepto tenga **una** ruta canónica. Dos árboles reintroducen la pregunta "¿en cuál va este concepto fronterizo?", que es la clase de duda que el namespace elimina.
- Consecuencia operativa: `pv-internal-tech-analysis` y `pv-do` resuelven rutas siempre contra `{architectureDocDir}/00-namespace.md`, vengan de un doc de arquitectura o de uno de estilo.

### 0.5. El fichero `00-namespace.md`: dos secciones

Un único fichero con dos secciones, porque están acopladas — la frontera `=` vs `:` que define `## Notation` es la que `## Tree` necesita para clasificar sus hojas (§C.4); el árbol no se lee sin la notación de sus hojas.

- `## Notation` — símbolos de contrato, convención compacta (§A.7), formato de tablas de decisión, sintaxis de assert, y la frontera `= <escalar>` vs `:` + bloque.
- `## Tree` — el árbol de rutas con sus `anchor:`, más la regla de orden de segmentos (§C.3) y la excepción de slugs de dominio (§F.7).

Los nombres literales `## Notation` y `## Tree` son **normativos**: `pv-update` los comprueba (§G.2) y `pv-do` los localiza para insertar nodos.

### 0.6. Renumeración de las writing rules

A sustituye la **regla 4**; D añade la **regla 9** y E la **regla 10**. Las reglas 1-8 actuales conservan su número; la 4 cambia de contenido, no de posición. Antes de cerrar el bloque, verificar que ninguna referencia cruzada quedó apuntando al contenido viejo:

- `.claude/skills/pv-internal-doc-technical/SKILL.md` referencia "rule 6" en su sección "Language." → sigue siendo la 6 (tags), sin cambio.
- `.claude/skills/pv-internal-doc-style/SKILL.md` extiende el baseline: revisar si cita reglas por número y re-anclar si la 4 cambió de sentido bajo sus pies.
- La regla 5 ("Point at the source instead of duplicating its shape") y el namespace dicen cosas compatibles pero solapadas — la 5 dice "apunta al código", el namespace dice "cita por ruta canónica, cuyo nodo lleva `anchor:` al código". Añadir un cross-ref en la 5 hacia "Namespace" para que no se lean como dos mecanismos rivales.

### 0.7. Versionado

Cada cambio es un cambio en el framework mismo → al terminar, `/dev-generate-version` sube la versión de todos los `.claude/skills/pv-*/SKILL.md` afectados de forma consistente. No versionar cambio a cambio; una sola release cuando el bloque completo esté implementado. Skills afectadas: `doc-technical`, `doc-style`, `tech-analysis`, `do`, `doc-files`, `init`, `update`.

---

## A. Notación nativa por defecto; prosa solo excepción

Absorbe la notación compacta para datos estructurados (§A.7) y los invariantes como asserts (§A.5).

### A.1. Qué se implementa

Reemplazar la actual **regla 4** ("Don't restate what a signature or name already says. Reserve prose for...") y ampliar la **regla 3** (tablas) por una sección nueva **"Notation-first"** que:

1. Declara el principio: notación/formato nativo es el default para todo tipo de contenido; prosa es excepción rara.
2. Incluye el **catálogo contenido→notación** como tabla normativa (§A.3).
3. Incluye el **checklist obligatorio** antes de escribir prosa (§A.4).
4. Incluye la sub-regla de invariante ejecutable vs. declarativo (§A.5).
5. Incluye la notación compacta para datos estructurados (§A.7).
6. Marca la prosa superviviente con `[motivación]` y la limita a una frase.

### A.2. Cambios concretos en `.claude/skills/pv-internal-doc-technical/SKILL.md`

| Ubicación (por ancla textual) | Acción |
|---|---|
| Regla 2, "Signatures, types and values as code, never described in prose." | Reescribir: "Signatures, types, values **and any structured datum (fields, defaults, optionality, ranges)** as code/compact notation, never prose. `field: type = default`, `?` for optional." |
| Regla 3, "Tables for parallel structures." | Mantener; añadir cross-ref a "Notation-first" |
| Regla 4, "Don't restate what a signature or name already says." | **Sustituir** por: "Prose is the exception. Every piece of content maps to a native notation (see *Notation-first* below); prose only for an idiosyncratic external constraint, one sentence, tagged `[motivación]`." |
| Regla 5, "Point at the source instead of duplicating its shape." | Añadir cross-ref a "Namespace" (§0.6) |
| Nueva sección "## Notation-first", tras "Writing rules" | Principio + catálogo (§A.3) + checklist (§A.4) + "Invariants: executable vs declarative" (§A.5) + notación compacta (§A.7) |
| Regla 6, lista de tags | Añadir `[motivación]` como marca de la prosa-excepción |

### A.3. Tabla catálogo (a incrustar en `.claude/skills/pv-internal-doc-technical/SKILL.md`, en inglés)

| Content type | Native notation | Prose only when... |
|---|---|---|
| Boolean invariant / pre-post-condition | `assert <expr>` if runtime-checkable; else propositional logic (`pre:`, `post:`, `inv:`, `∧ ∨ ¬ → ⟹ ∀`) | Never (pure structure) |
| Data structure (fields, types, defaults, optionality) | Table or compact notation (`field: type = default`) — see §A.7 | Never |
| State machine / transitions | FSM or `(state, event) → state'` table | Never |
| Entity relationship / cardinality | ER diagram or `1---*`, `0..1` notation | Never |
| Temporal sequence / call flow | Sequence diagram (Mermaid) or ordered pseudocode | Never |
| Decision tree / nested conditionals | Boolean table or explicit tree | Never |
| Decision rationale | Rule/condition + comparison table | Only for an idiosyncratic external constraint (compliance, business) not reducible to a condition nor a general engineering principle |
| Side-effect flow | Numbered sequence / event→effect table | Only the single step whose ordering is externally-semantic (UX, business) |

**Notación anidada**: si una notación necesita referirse a otra, cítala por su ruta de namespace, no la incrustes.

**Diagramas**: las filas "Temporal sequence" y "Entity relationship" admiten Mermaid. El framework ya tiene `pv-internal-tech-mermaid` (configurable vía `framework.skills.diagrams`) para generarlos — `pv-do` la invoca como ya hace en otros flujos.

### A.4. Checklist obligatorio antes de prosa (a incrustar, en inglés)

```
Before writing any prose sentence:
  1. Is it a condition/rule?            → decision table or propositional logic.
  2. Is it one more metric of a comparison already tabulated?  → add a column.
  3. Is it a general engineering principle the reader already infers?  → write nothing.
  4. None of the above  → one sentence of prose, tagged [motivación].
Never force prose for elegance, reading flow, or because "it sounds like a trade-off".
```

### A.5. Sub-sección "Invariants: executable vs declarative"

| Question | Yes | No |
|---|---|---|
| Is there a program point where this condition can be checked with the values at hand? | `assert <expr>` | declarative `inv: …` |
| Does it quantify over an abstract set / talk about an FSM state / a non-observable global property? | — | declarative |

Reglas: forma preferente = assert siempre que el criterio dé "sí"; la declarativa es fallback, no estilo alternativo; si conviven, el assert manda y la declarativa se marca como enunciado; sintaxis exacta la fija la sección `## Notation` de `00-namespace.md`.

### A.6. Ejemplo canónico a incrustar

```
MAL:  el método recibe un parámetro opcional que, si no se especifica, toma el valor por defecto de 30 segundos
BIEN: timeout?: Duration = 30s
```

### A.7. Notación compacta para datos estructurados

Es la fila "Data structure" del catálogo (§A.3), explicitada por su frecuencia de uso: aplica en casi toda tarea. Se materializa en la reescritura de la regla 2 (§A.2), el ejemplo de §A.6, y esta convención, que va a la sección `## Notation` de `00-namespace.md` (provisional en `.claude/skills/pv-internal-doc-technical/SKILL.md` hasta que exista el fichero):

```
field: type                  required field
field?: type                 optional field
field: type = value          default value
field: type ∈ {a, b, c}      enum / allowed set
field: type [min..max]       range
```

---

## B. Tag de anti-expectativa `[gotcha]`

### B.1. Qué se implementa

Añadir `[gotcha]` al vocabulario de **fixed English tags** (regla 6), con semántica específica: marca un hecho que **contradice el patrón por defecto** que un lector con conocimiento general de software asumiría.

### B.2. Cambios concretos en `.claude/skills/pv-internal-doc-technical/SKILL.md`

| Ubicación | Acción |
|---|---|
| Regla 6, lista de tags | Añadir `[gotcha]` junto a `[breaking]`, `[async]`, `[idempotent]`, `[deprecated]` |
| Regla 6, texto | Añadir: "`[gotcha]` marks a fact that contradicts the default assumption a reader would bring from general software patterns (a `delete` that soft-deletes, a `getX` that mutates, a sync-looking call that isn't). Reserve it for genuine anti-expectations, not for every noteworthy detail." |
| Nota bajo regla 6 | Criterio de uso + ejemplo canónico (§B.3) |

### B.3. Ejemplo canónico (a incrustar)

```
BIEN: - [gotcha] deleteUser(id) does NOT remove the row — it sets active=false.
MAL:  - deleteUser(id) marks the user inactive.
```

### B.4. Herencia y consumo

- `pv-internal-doc-style` hereda el tag: su contenido también puede tener gotchas de estilo ("el sistema de grid NO es de 12 columnas, es de 16").
- `pv-internal-tech-analysis` recibe instrucción de **elevar la atención** sobre líneas `[gotcha]`: son las que corrigen su modelo por defecto, no puede tratarlas como una fila más.

---

## C. Namespace jerárquico único, vinculado al código

Da identidad canónica única a cada concepto y afirmación, eliminando sinonimia y drift.

### C.1. Qué se implementa

Un **árbol de nombres único por proyecto** (§0.4), con segmentos separados por puntos, de agregado a detalle. Cada elemento (concepto o afirmación) tiene una ruta canónica única. Los nodos con `anchor:` apuntan al código.

```
auth.token.session                       concepto.  anchor: src/auth/token.ts#SessionToken
auth.token.session.exp                   concepto.  anchor: SessionToken.exp
auth.token.session.ttl                   concepto.  anchor: SESSION_TTL_SECONDS
auth.token.session.ttl.value = 3600      afirmación (escalar)
auth.token.session.refresh.rule:         afirmación (no escalar → bloque de notación)
    pre:  state ∈ {AUTHENTICATED, EXPIRED} ∧ now - token.exp < 7d
    post: token'.exp = now + auth.token.session.ttl.value
auth.decision.circuit-breaker-over-retry decisión.  sin ancla de código
ui.grid.columns = 16                     afirmación de estilo (mismo árbol, §0.4)
```

### C.2. Reglas del árbol (a incrustar en `.claude/skills/pv-internal-doc-technical/SKILL.md`, nueva sección "## Namespace")

| Element | Form | Rule |
|---|---|---|
| Node with code anchor | `path` + `anchor: file#symbol` | Canonical name **is** the path; definition lives in code. Uniqueness is structural: one term per concept, project-wide. |
| Leaf `path = value` | terminal segment `= <scalar>` | The citable unit across docs: `see auth.token.session.ttl.value`. One citation syntax project-wide, stable across edits. |
| Leaf `path:` + notation block | terminal segment `:` then a notation block (§A.3) | For non-scalar assertions (a logic expression, a contract). Citable exactly like a `=value` leaf. |
| Branch `path.decision.<slug>` | reserved subtree | Assertion with no code anchor (a design choice). Citable like a leaf. |
| Node with no anchor and no `=` / `:` | — | **Suspicious**: missing anchor, or general knowledge that shouldn't be named. |

Frontera concepto/afirmación = **sintáctica**: ¿tiene `= valor`, `:` + bloque, o cuelga de `.decision.`? → afirmación. ¿No? → concepto. Sin juicio.

### C.3. Convención de orden de segmentos

**Regla**: de **agregado a parte** y de **módulo a detalle**. `<área>.<agregado>.<entidad>.<campo-o-afirmación>`.

- `auth.token.session.exp` ✅ (área auth → agregado token → entidad session → campo exp)
- `auth.session.token.exp` ❌ (invierte agregado y entidad)

Autoridad que asigna rutas: `pv-do` al documentar, siguiendo esta regla; ante ambigüedad real, `pv-do` pregunta al usuario (igual que ya hace con dudas de interfaz en `pv-internal-tech-analysis`). La regla se escribe en `.claude/skills/pv-internal-doc-technical/SKILL.md` y en la semilla de `00-namespace.md`.

### C.4. Afirmaciones no escalares

La hoja **identifica** (nombre estable, citable); su **cuerpo** es un bloque de notación de §A.3. La sección `## Notation` de `00-namespace.md` define la frontera: `= <escalar>` para valores simples (número, enum, booleano); `:` + bloque para afirmaciones con estructura lógica.

### C.5. Cambios concretos por artefacto

| Artefacto | Cambio |
|---|---|
| `.claude/skills/pv-internal-doc-technical/SKILL.md` | Nueva sección "## Namespace" con las reglas de §C.2, la frontera sintáctica y el orden de segmentos (§C.3); regla "cite any concept or assertion by its canonical namespace path, never re-describe it"; cross-ref desde la regla 9 (anáfora), desde la regla 5 (§0.6) y desde la nota de notación anidada de §A.3. Indicar que el árbol vive en `{architectureDocDir}/00-namespace.md`, uno solo por proyecto. |
| `.claude/skills/pv-internal-doc-style/SKILL.md` | Hereda: los conceptos de estilo (tokens de diseño, componentes) entran en **ese mismo** árbol, rama `ui.*`. `styleBibleDocDir` no tiene fichero de namespace propio. |
| `.claude/skills/pv-internal-tech-analysis/SKILL.md` | Paso nuevo: "cuando el contenido cite una ruta de namespace, resuélvela contra `{architectureDocDir}/00-namespace.md`; si el nodo tiene `anchor:`, esa es la definición canónica y prevalece sobre cualquier redacción" — encaja con su regla actual de "code is source of truth". Añadir: "el contenido técnico viene en notación (contratos `pre:/post:`, FSM, tablas, asserts); parséala como tal, no esperes prosa narrativa". Nota: al leer `styleBibleDocDir`, las rutas se resuelven contra el mismo fichero de `architectureDocDir`. |
| `.claude/skills/pv-do/SKILL.md` | Paso nuevo al documentar: "si el cambio añade/renombra un concepto o afirmación citable, actualiza `{architectureDocDir}/00-namespace.md` (nueva ruta, o ancla movida); si el símbolo de código cambió de nombre, actualiza la `anchor:` correspondiente". **Editarlo con Read/Edit directamente — no vía `upsert`** (§0.3, §C.6). |
| `pv-internal-doc-files` | §C.6 |
| `.claude/skills/pv-init/scripts/scaffold-project.py` | Semilla `00-namespace.md` (§C.7) |

### C.6. Cambios en `pv-internal-doc-files`

| Artefacto | Cambio |
|---|---|
| `.claude/skills/pv-internal-doc-files/scripts/rebuild-index.py` | En el bucle `for path in sorted(folder.glob("*.md"))`, ampliar el `continue` de `INDEX.md` para saltar también `path.name.startswith("00-")`. |
| `.claude/skills/pv-internal-doc-files/scripts/next-feature-number.py` | Mismo filtro en su glob, para que un `00-*` nunca influya en el número siguiente ni pueda "robar" un `NNN`. |
| `.claude/skills/pv-internal-doc-files/SKILL.md`, estructura de carpeta | Documentar el prefijo reservado, junto a la regla de `INDEX.md`: "`00-*.md` — infrastructure files for the folder (e.g. `00-namespace.md`), excluded from `INDEX.md` and from the `{NNN}` numbering. Written directly by their owning skill, never through `upsert`." |
| `.claude/skills/pv-internal-doc-files/SKILL.md`, acción `upsert` | Nota: `upsert` nunca crea ni toca un `00-*`; si el caller pide escribir uno, es un error de uso. |

Este cambio va **antes** que la semilla de `.claude/skills/pv-init/scripts/scaffold-project.py`: sin él, el primer proyecto inicializado saldría con un `INDEX.md` que lista el namespace como si fuera un tema.

### C.7. Semilla de `00-namespace.md`

`.claude/skills/pv-init/scripts/scaffold-project.py` la crea en `architectureDocDir` (no en `styleBibleDocDir`, §0.4), con:

- Cabecera de una línea diciendo qué es el fichero y que es el único árbol del proyecto.
- `## Notation` — convenciones de §A.7 y §A.5, y la frontera `= <escalar>` vs `:` + bloque.
- `## Tree` — la regla de orden de segmentos (§C.3), la excepción de slugs de dominio (§F.7), y un ejemplo comentado. Árbol vacío: `pv-do` lo puebla.

Comprobar que `.claude/skills/pv-init/scripts/scaffold-project.py` sigue siendo idempotente con el fichero nuevo (su patrón actual es `status: created/skipped` por ruta): si `00-namespace.md` ya existe, **no** sobrescribirlo.

### C.8. Coste asumido

Al refactorizar código (renombrar símbolo → renombrar ruta), la reasignación de ruta es manual. `pv-update` detecta el ancla rota (§G.3) pero no la repara sola: no puede saber a qué símbolo nuevo corresponde.

---

## D. Prohibir referencias anafóricas

### D.1. Qué se implementa

Nueva **writing rule 9**: nunca pronombres ni referencias anafóricas ("esto", "dicho campo", "el mismo", "lo anterior") cuando se puede repetir el nombre exacto.

### D.2. Cambios concretos en `.claude/skills/pv-internal-doc-technical/SKILL.md`

| Ubicación | Acción |
|---|---|
| Sección "Writing rules", tras la regla 8 | Añadir **regla 9**: "No anaphora. Never 'this', 'that field', 'the former', 'the above' when the exact name can be repeated. Repeating the identifier is cheaper for the reader than resolving a referent — and never wrong when two candidates are nearby. Style cost of repetition is not a concern (see Audience)." |
| Misma regla, cross-ref | "When the referent has a namespace path (see *Namespace*), the repeated form is that canonical path." |

### D.3. Ejemplo canónico (a incrustar)

```
MAL:  The token carries an expiry. This is checked on every request; if it has passed, the session ends.
BIEN: token.exp is checked on every request. If time > token.exp, the session ends.
```

### D.4. Relación con el namespace

El namespace provee el identificador canónico; esta regla obliga a usarlo en vez de una anáfora. No queda absorbida por el namespace: su alcance incluye anáforas sobre cosas sin ruta canónica (p. ej. "el flujo anterior"). Se subordina: "el identificador válido para citar es la ruta del namespace; nunca una anáfora ni un sinónimo".

---

## E. Prohibir adjetivos/adverbios de intensidad sin cifra

### E.1. Qué se implementa

Nueva **writing rule 10**: prohibir intensificadores sin cuantificar ("muy rápido", "bastante grande", "poco frecuente"). O se cuantifica, o no se escribe. Conecta con el espíritu de "hechos verificables" de las reglas actuales, pero como regla explícita de redacción, no de contenido.

Un intensificador sin cifra ya se descarta como no-información al leerlo: la regla evita el coste de escribirlo y descartarlo. Cuando la cifra existe, forzarla es la ganancia real; cuando no existe, la frase entera sobra.

### E.2. Cambios concretos en `.claude/skills/pv-internal-doc-technical/SKILL.md`

| Ubicación | Acción |
|---|---|
| Sección "Writing rules", tras la regla 9 | Añadir **regla 10**: "No unquantified intensifiers. Never 'very fast', 'fairly large', 'rarely called', 'significant overhead'. Either give the figure (`p95 = 12ms`, `~400 rows`, `< 1 call/day`) or drop the claim entirely — an intensifier without a number is discarded as non-information on read, so writing it only costs tokens. This includes comparatives with no baseline ('slower', 'heavier') unless the baseline is named." |
| Ejemplo canónico | §E.3 |

### E.3. Ejemplo canónico (a incrustar)

```
MAL:  This endpoint is very slow and is rarely called.
BIEN: p95 = 2.4s. Called < 10 times/day.
BIEN: (si no hay cifra) — omit the sentence.
```

### E.4. Interacción con el resto

- Con A: una comparativa cuantificada casi siempre es una tabla, no una frase. Si aparecen dos o más métricas, el checklist de §A.4 la manda a tabla antes de que esta regla intervenga.
- Con `[motivación]`: la única prosa que sobrevive también está sujeta a esta regla — una frase de motivación no puede apoyarse en "muy costoso" sin cifra.

---

## F. Inglés técnico fijo; se elimina `docs.tech.language`

**Cambio no aditivo**: revierte una decisión de diseño ya implementada (la sección "Language-independence" de `.claude/skills/pv-internal-doc-technical/SKILL.md` y la opción de configuración `docs.tech.language`). `docs.tech` pasa a estar **siempre en inglés técnico** y `docs.tech.language` **desaparece del framework**, incluida cualquier `pv-context.json` ya existente (§F.6).

### F.1. Alcance: todo en inglés, sin opción de idioma

- El objetivo es que `docs.tech` sea **monolingüe de principio a fin**. Dejar la prosa `[motivación]` en otro idioma reintroduciría la mezcla de idiomas dentro del mismo documento.
- Tras A y C, la prosa `[motivación]` es marginal en volumen → `pv-do` la genera directamente en inglés.
- Una opción de config que gobierne "solo una frase ocasional" es más superficie de configuración, error y drift que valor.

**Consecuencia**: `docs.tech.language` se elimina. `docs.functional.language`, `changes.language`, `versions.language` e `interaction.language` **no se tocan** — el proyecto puede seguir en español en todo lo demás; `docs.tech` queda como isla en inglés, que es el resultado buscado.

**Beneficio secundario**: al fijar el idioma, dos técnicas de compresión hoy prohibidas por portabilidad pasan a ser recomendadas (§F.2). El cambio no solo fija idioma: **desbloquea densidad**.

### F.2. Cambios en `.claude/skills/pv-internal-doc-technical/SKILL.md`

| Ubicación (por ancla textual) | Acción |
|---|---|
| Frontmatter `description` | Ninguna acción por F: **verificado**, la `description` actual no menciona `docs.tech.language`. Sí hay que revisarla al final por A y C, que añaden secciones nuevas que la `description` debería reflejar. |
| Sección "**Language.**" ("the caller translates as needed when drafting into `docs.tech.language`" ... "stay in English regardless of `docs.tech.language`") | Reescribir: "This skill's output and all `docs.tech` content is fixed technical English. There is no `docs.tech.language` option — architecture and style-bible documents are always English, regardless of `interaction.language` or the project's language elsewhere. The caller does not translate; it drafts in English." |
| Regla 6, "Fixed English tags for recurring properties, regardless of `docs.tech.language`." | Quitar "regardless of `docs.tech.language`". Ojo a la frase final de esa misma regla, que dice "which also stay English regardless of the doc's language" refiriéndose a `pv-internal-doc-features` — **esa se mantiene**: `docs.functional.language` sigue existiendo. |
| Sección "## Language-independence", encabezado | **Renombrar a "## Fixed language: technical English"** y reescribir el cuerpo: ya no es "estas reglas valen para cualquier idioma", es "el documento es inglés técnico; por tanto se permiten técnicas de densidad que dependen de la gramática inglesa". |
| Viñeta "**No telegraphic/headline compression**" | **Invertir**: se **permite** la compresión telegráfica (`user token expired`) porque el idioma es fijo. Mantener solo la advertencia de no volverla ilegible. |
| Viñeta "**No compound-noun stacking**" | **Invertir**: se **permite** el compound-noun stacking (`user auth token expiry check`) como técnica de densidad válida. |
| Última viñeta ("...transfers unchanged to any `docs.tech.language`") | Eliminar (ya no hay "any language" al que transferir). |

### F.3. Cambios en `.claude/skills/pv-internal-doc-style/SKILL.md`

Una sola línea (sección "**Language.**"), con dos menciones:

| Fragmento | Acción |
|---|---|
| "the caller translates as needed when drafting into `docs.tech.language`" | → "all `styleBibleDocDir` content is fixed technical English, same as `pv-internal-doc-technical`; there is no `docs.tech.language`." |
| "stay in English regardless of `docs.tech.language`, same convention `pv-internal-doc-technical` already uses" | → "stay in English, same convention `pv-internal-doc-technical` already uses." |

### F.4. Cambios en `pv-init`

`.claude/skills/pv-init/schema.json` — **verificadas 4 menciones**:

| Ubicación | Acción |
|---|---|
| `docs.tech.language` (propiedad, con `description: "OPTIONAL. Language shared by architectureDocDir and styleBibleDocDir..."`) | **Eliminar** la propiedad completa. `docs.tech` mantiene su `required` sin cambios. |
| `description` de `interaction.language`: "...fallback value for changes.language, versions.language, and any docs.\*.language block without its own language" | → "...fallback value for changes.language, versions.language, and docs.functional.language." |
| Bloque de ejemplo, `docs.tech: { ..., "language": "en" }` | Quitar `"language": "en"` de ese bloque. Ojo: el ejemplo tiene varios `"language"`; solo se toca el de `docs.tech`. |
| `_comments` del ejemplo: `"docs.tech.language": "Architecture and style bible in English, to share with external collaborators."` | **Eliminar** la línea. |

`.claude/skills/pv-init/SKILL.md`:

| Ubicación | Acción |
|---|---|
| Flujo "same language for everything": "set `changes.language`, `versions.language`, `docs.functional.language` and `docs.tech.language` to the interaction language" | Quitar `docs.tech.language` de la enumeración. |
| Pregunta 4, "**Language of the technical documentation** (`framework.docs.tech.language`)" | **Eliminar la pregunta entera.** Quedan 3 preguntas por área (changes, versions, functional) — renumerar. Añadir: "Technical documentation (`docs.tech`) has no language option — it is always technical English." |
| Frase sobre `hasLanguage`: "`changes.language`/`versions.language`/`docs.*.language` are optional refinements" | Ajustar `docs.*.language` → `docs.functional.language`. |
| Paso final, resumen al usuario: "the resolved language configuration (`interaction.language`/`changes.language`/`versions.language`/`docs.*.language`...)" | Mismo ajuste. |
| `.claude/skills/pv-init/scripts/scaffold-project.py` | Sin cambios por F; su cambio es la semilla de §C.7. |

### F.5. Cambios en `.claude/skills/pv-do/SKILL.md`

**Verificadas 3 menciones**:

| Ubicación | Acción |
|---|---|
| Sección "**Language.**" | "When updating `docs.tech.architectureDocDir`/`styleBibleDocDir` yourself, use `docs.tech.language` (fallback `interaction.language`) — **not** `changes.language`..." → "always write `docs.tech.architectureDocDir`/`styleBibleDocDir` in technical English — there is no `docs.tech.language`. The source (`plan.md`) may be in `changes.language`; translating to English when writing the reference document is your responsibility." Mantener intacto lo que esa misma sección dice de `docs.functional.language`. |
| Bloque `docs.tech.architectureDocDir` | "**Write it in `docs.tech.language`** (fallback `interaction.language`), never in `changes.language`" → "**Write it in technical English**, never in `changes.language` — draft fresh in English, don't carry over `plan.md` sentences verbatim." |
| Bloque `docs.tech.styleBibleDocDir` | "**Write it in `docs.tech.language`** ... same rule as `architectureDocDir`" → "**Write it in technical English**, same rule as `architectureDocDir` above." |

### F.6. Erradicar la clave de los `pv-context.json` ya existentes

Quitar `docs.tech.language` de `.claude/skills/pv-init/schema.json` no la borra de los ficheros que ya la tienen en disco — y `pv-update` no la detectaría.

**Verificado en el código**: `.claude/skills/pv-update/scripts/audit-context.py` **no valida contra `.claude/skills/pv-init/schema.json`**. Sus chequeos son ad-hoc, y su detección de claves desconocidas (`unknown-top-level-field`, `unknown-framework-field`) recorre **solo dos niveles**: las claves de `context` y las de `framework`. **No baja a `framework.docs.tech`**. Además `schemaOk` se deriva de esos mismos `id`, no de una validación real. Y el script es **read-only** (solo escribe JSON a stdout): la reparación la aplica siempre `.claude/skills/pv-update/SKILL.md` en su fix loop.

Consecuencia sin trabajo adicional: un `pv-context.json` que conserve la clave pasaría silencioso indefinidamente y `pv-update` reportaría el fichero como sano — lo contrario de "la configuración desaparece del framework".

| Artefacto | Acción |
|---|---|
| `.claude/skills/pv-update/scripts/audit-context.py` | Añadir una constante `OBSOLETE_KEYS` con la ruta `framework.docs.tech.language` y un chequeo que emita `obsolete-field:framework.docs.tech.language` (severidad `required`) cuando la clave exista. ~6 líneas. |
| `.claude/skills/pv-update/scripts/audit-context.py`, cálculo de `schemaOk` | Incluir el prefijo `obsolete-` en la tupla de `p["id"].startswith((...))`, para que la presencia de la clave marque el fichero como no conforme. |
| `.claude/skills/pv-update/SKILL.md`, fix loop | **Entrada nueva**: "**`obsolete-field:*`** — delete the key at the reported path from `pv-context.json`, and remove its matching entry from `framework._comments` if one exists. Non-destructive: it changes no path and no behavior, only removes a key no skill reads any more." Sin esta entrada, el script diagnostica pero la skill no sabe qué hacer. |
| `.claude/skills/pv-update/SKILL.md`, `description` y cobertura del paso 2 | Añadir "obsolete keys left over from a framework upgrade". |

### F.7. Terminología de dominio sin traducción técnica estándar

`docs.tech` es inglés, pero un concepto de negocio puede no tener término inglés estándar (p. ej. dominio fiscal español: "recargo de equivalencia"). Regla:

- Si el concepto **tiene símbolo de código**, su ruta de namespace usa el nombre del símbolo (que ya está en el idioma en que se programó).
- Si **no tiene símbolo de código**, se permite el slug en el idioma del proyecto para ese nodo concreto (`billing.recargo-equivalencia`), documentado como **excepción explícita** en `00-namespace.md` con una nota de una línea de qué es en inglés aproximado.
- La prosa `[motivación]` que lo acompañe sigue siendo inglés (puede nombrar el término español entre comillas: `[motivación] "recargo de equivalencia" is a Spanish tax surcharge; no standard English term.`).

Esta regla se escribe en la semilla de `00-namespace.md` (§C.7).

---

## G. Verificación por `pv-update`

**Verificado en el código**: hoy `.claude/skills/pv-update/scripts/audit-context.py` comprueba de las carpetas de doc **solo dos cosas** (`check_docs_dir`): que la carpeta existe y que tiene `INDEX.md`. Nada de lo que este plan introduce está cubierto. Sin §G, un proyecto puede perder el `00-namespace.md`, tenerlo sin sus secciones, o acumular anclas rotas, y `pv-update` lo reportaría como sano.

Los chequeos siguen el patrón ya existente en el script: detectar y describir, con la reparación en el fix loop de `.claude/skills/pv-update/SKILL.md`. El script sigue siendo **read-only**.

### G.1. Semilla presente

| Artefacto | Acción |
|---|---|
| `.claude/skills/pv-update/scripts/audit-context.py`, dentro de `check_docs_dir` (solo para `framework.docs.tech.architectureDocDir`) | Emitir `namespace-missing` (severidad `optional`) si la carpeta existe pero no contiene `00-namespace.md`. No aplicar a `styleBibleDocDir` ni a `featuresDocPathDir`: por §0.4 solo `architectureDocDir` tiene árbol. |
| `.claude/skills/pv-update/SKILL.md`, fix loop | "**`namespace-missing`** — recreate the seed by re-running `.claude/skills/pv-init/scripts/scaffold-project.py`, same as the `*-missing-index` fix. Never invent tree content: an empty `## Tree` with its conventions is the correct repaired state; `pv-do` fills it over time." |

### G.2. Secciones normativas presentes

| Artefacto | Acción |
|---|---|
| `.claude/skills/pv-update/scripts/audit-context.py` | Si `00-namespace.md` existe, comprobar que contiene los headings literales `## Notation` y `## Tree`. Si falta alguno, emitir `namespace-section-missing` (`optional`), con `expected` = los dos headings y `actual` = los encontrados. Mismo espíritu que el chequeo de marcadores estructurales que el script ya hace sobre los documentos derivados de plantilla: son nombres que otras skills localizan literalmente. |
| `.claude/skills/pv-update/SKILL.md`, fix loop | "**`namespace-section-missing`** — add the missing `## Notation` / `## Tree` heading in its canonical order, without touching the content already under the other one. If the section exists translated or reworded, rewrite just the heading back to its English literal, leaving the body as-is." |

### G.3. Anclas que resuelven

| Artefacto | Acción |
|---|---|
| `.claude/skills/pv-update/scripts/audit-context.py` | Por cada `anchor: <file>#<symbol>` del `## Tree`, comprobar que `<file>` existe (resuelto desde la raíz del repo, como `sourcecodeDir`). Emitir `namespace-anchor-broken:<path>` (`optional`) por cada ancla cuyo fichero no exista. **Solo se valida el fichero, no el símbolo**: buscar el símbolo exigiría parsear cada lenguaje, y un falso positivo aquí sería peor que no avisar. |
| `.claude/skills/pv-update/SKILL.md`, fix loop | "**`namespace-anchor-broken:*`** — the anchored file no longer exists (renamed, moved, or deleted). **This is not auto-fixable**: only the code's history says which symbol replaced it. Report it to the user with the path and the namespace route, and offer to look for the symbol in git history — don't guess a new anchor, and don't delete the node." |

Esta es la tercera excepción del fix loop de `.claude/skills/pv-update/SKILL.md`: se resuelve preguntando, no unilateralmente, por la misma razón que las dos ya existentes (adivinar sería inseguro). Documentarlo junto a ellas en la sección de la skill que enumera las excepciones, para que no contradiga su afirmación de que solo hay dos.

### G.4. Rutas citadas que existen — **fuera de alcance**

Validar que toda ruta de namespace citada en un doc existe en el `## Tree` exigiría distinguir una cita real de un identificador de código cualquiera con puntos (`token.exp` aparece en ambos). Sin una sintaxis de cita explícita, el ratio de falsos positivos lo haría inservible. Queda anotado como límite conocido de §G, no como trabajo pendiente de este plan.

---

## H. Documentación del framework (`pv-doc/`)

Los ficheros de `.claude/pv-doc/` describen el framework a un lector humano. **Verificado**: A-G invalidan pasajes concretos. Sin §H, la documentación del framework queda describiendo un framework que ya no existe.

**Alcance: solo los ficheros `.es.md`.** Se actualizan `.claude/pv-doc/pv-design/pv-design.es.md` y `.claude/pv-doc/pv-guide.es.md`. Las versiones `.en.md` **no se tocan** en este plan: se traducirán después, a partir de las `.es.md` ya actualizadas. Consecuencia asumida y temporal: al terminar este plan los pares en/es quedan **desincronizados**, y el `.en.md` sigue documentando `docs.tech.language` como si existiera. No es un olvido — es trabajo diferido; anotarlo al cerrar para que la traducción posterior sepa qué pares revisar.

`.claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md`: **revisado, sin cambios** — no menciona `docs.tech.language`, ni `pv-internal-doc-technical`, ni la numeración de `pv-internal-doc-files`.

### H.1. `.claude/pv-doc/pv-design/pv-design.es.md`

| Ubicación (por ancla textual) | Acción |
|---|---|
| Ficha de `pv-internal-doc-technical` (`- **pv-internal-doc-technical** — Qué y cómo escribir...`) | Actualizar la descripción del estilo: hoy dice "fragmentos densos, tablas, código, tags fijos en inglés". Añadir notación-first como default y prosa como excepción tasada (A), el tag `[gotcha]` (B), y la sección de namespace (C). |
| Ficha de `pv-internal-doc-technical`, idioma | Añadir que su salida y todo `docs.tech` es inglés técnico fijo, sin opción de idioma (F). |
| Ficha de `pv-internal-doc-files` (`- **pv-internal-doc-files** — ...`) | Documentar el prefijo reservado `00-`: excluido de `INDEX.md` y de la numeración, escrito directamente por la skill dueña, nunca vía `upsert` (§0.3). |
| Viñeta de `scripts/rebuild-index.py` ("regenera `INDEX.md` a partir de todos los ficheros de la carpeta") | Corregir: ya no es "todos" — excluye `INDEX.md` y `00-*.md`. |
| Viñeta de `scripts/next-feature-number.py` (calcula el siguiente número libre buscando el más alto ya usado) | Corregir igual: los `00-*` no cuentan. |
| Viñeta `- **docs.tech.language** (string, opcional, default interaction.language): idioma compartido por...` | **Eliminar la viñeta entera** (F). |
| Viñeta "El idioma compartido por ambos campos `tech.*` se configura en `tech.language`" | Sustituir por: `docs.tech` no tiene campo de idioma — su contenido es siempre inglés técnico. |
| Bloque de ejemplo de `pv-context.json`, línea `"docs.tech.language": "Arquitectura y biblia de estilo en inglés..."` (dentro de `_comments`) | Eliminar la línea del ejemplo. |
| Sección "Configuración de idioma" | Quitar `docs.tech` de la enumeración de áreas configurables; añadir que `docs.tech` es la excepción: inglés fijo, no configurable. |
| Ficha de `tech.architectureDocDir` ("un fichero `{NNN}-{slug}.md` por tema") | Añadir el `00-namespace.md` como fichero de infraestructura de esa carpeta, y que es el único árbol del proyecto (§0.4). |
| Árbol de carpetas (`├── architecture/  # docs.tech.architectureDocDir`) | Añadir la línea de `00-namespace.md` bajo `architecture/`, con su comentario. **No** añadirla bajo `style/` (§0.4). |
| Sección de marcadores estructurales y su párrafo sobre `audit-context.py` | Añadir que `audit-context.py` también valida los headings normativos `## Notation` / `## Tree` del `00-namespace.md` (§G.2) — misma familia de chequeo, distinta fuente (aquí los literales los fija este plan, no una plantilla `[[[...]]]`). |

### H.2. `.claude/pv-doc/pv-guide.es.md`

**Verificado**: hay **dos** bloques de ejemplo de `pv-context.json` con `docs.tech.language`, no uno. Ambos hay que tocarlos.

| Ubicación (por ancla textual) | Acción |
|---|---|
| **Ejemplo 1** (~línea 75), bloque `"tech": { "architectureDocDir": ..., "styleBibleDocDir": ..., "language": "en" }` | Quitar la línea `"language": "en"` del objeto `tech`. Ojo: el mismo ejemplo tiene otros `"language"` (`interaction`, `changes`, `versions`, `functional`) que **se quedan**. |
| **Ejemplo 1**, `_comments` (~línea 88), línea `"docs.tech.language": "Arquitectura y biblia de estilo en inglés, para compartir con colaboradores externos."` | Eliminar la línea. |
| Sección "2. Configuración de idiomas", viñeta `- **docs.tech.language**: idioma compartido por la documentación de arquitectura...` | **Eliminar la viñeta** de la lista de puntos configurables. |
| Sección "2. Configuración de idiomas", frase que introduce el ejemplo 2: *"Esto te permite, por ejemplo, hablar con Previo en español mientras la documentación técnica queda en inglés para compartirla con colaboradores externos"* | **[gotcha] El ejemplo entero está construido sobre la opción que se elimina.** Reescribir el gancho: el caso de uso que ilustra ya no es una elección del usuario, es el comportamiento fijo. Pasa a ser algo como "hablar con Previo en español mientras el changelog y las funcionalidades salen en español — la documentación técnica va siempre en inglés, no se configura". |
| **Ejemplo 2** (~línea 337), bloque `"docs": { "functional": { "language": "es" }, "tech": { "language": "en" } }` | Quitar la entrada `"tech": { "language": "en" }` del ejemplo. Si al quitarla el objeto `docs` queda con un solo campo, reformatear el JSON para que siga leyéndose bien. |
| Párrafo final "**Dos** cosas se quedan siempre en inglés, se configure lo que se configure..." | **Ampliar a tres**, y que la nueva sea explícita: además de la tabla de `pv-status` y de las etiquetas markdown, **toda la documentación técnica** (`architectureDocDir` + `styleBibleDocDir`) está siempre en inglés técnico y no se puede configurar. Decir el porqué en una frase (está optimizada para que la lean las propias skills, no una persona). Este párrafo es el único sitio de cara al usuario que responde a "¿por qué mi documentación técnica sale en inglés si configuré español?" — sin esto, el cambio parece un bug. |
| Párrafo de `pv-init` ("siempre pregunta por el idioma en una inicialización desde cero... ofreciendo reutilizar el mismo valor para el resto") | Ajustar: "el resto" ya no incluye la documentación técnica. Coherente con la eliminación de la pregunta 4 (§F.4). |

### H.3. Regla de consistencia

Las skills son la fuente de verdad; `pv-doc/` las describe. Al aplicar §H, verificar contra el `SKILL.md` real de cada skill ya modificada, no contra este plan — si algo se implementó distinto a lo aquí escrito, manda la implementación y lo que se corrige es la documentación, no al revés.

---

## 17. Estado del proyecto real

**Verificado en el repo**: `docs.tech.architectureDocDir` (`docs/architecture`) y `styleBibleDocDir` (`docs/style`) **no existen en disco** — ni bajo la raíz ni bajo `workFolder` (`/previo-sdd`, que tampoco existe todavía). No hay corpus que migrar.

Lo único que procede, sobre `.claude/pv-context.json`:

1. Eliminar `"language": "es"` del bloque `framework.docs.tech`.
2. Eliminar la línea `"docs.tech.language"` de `framework._comments`.
3. Ajustar la línea `"interaction.language"` de `_comments`, que dice "y cualquier docs.\*.language que no se configure aparte" → dejar solo `changes.language`, `versions.language` y `docs.functional.language`.
4. Ejecutar `/pv-update` y comprobar que reporta limpio. Con §F.6 implementado, si se olvida el paso 1 el propio `pv-update` lo detecta y lo repara — que es la prueba de que §F.6 funciona.

**Cuando exista corpus** en `docs.tech`, aplicar en una sola pasada por fichero: extraer conceptos y afirmaciones a `00-namespace.md` con su `anchor:` (C); convertir prosa estructural a notación según el catálogo (A); sustituir anáforas por el nombre exacto o la ruta (D); cuantificar o eliminar intensificadores (E); marcar `[gotcha]` los hechos que contradicen el patrón por defecto (B); dejar en prosa `[motivación]` en inglés solo lo que pase el checklist de 4 pasos (A/F).

---

## 18. Checklist de cierre

**A — Notación nativa**
- [ ] `.claude/skills/pv-internal-doc-technical/SKILL.md` no contiene ya ninguna instrucción que permita prosa "para explicar" fuera del checklist de 4 pasos.
- [ ] La regla 4 vieja ya no existe con su redacción permisiva.
- [ ] La regla 2 cubre explícitamente defaults y opcionalidad; hay ejemplo MAL/BIEN de dato estructurado.
- [ ] La convención `?` / `=` / `∈` / `[..]` está escrita en un solo sitio (semilla de `00-namespace.md`, sección `## Notation`).
- [ ] La regla 5 tiene cross-ref a "Namespace" y no se lee como mecanismo rival.
- [ ] `.claude/skills/pv-internal-doc-style/SKILL.md` sigue coherente: su checklist de estilo no pide prosa donde A la prohíbe, y ninguna referencia suya a una regla por número quedó desanclada.
- [ ] `.claude/skills/pv-internal-tech-analysis/SKILL.md` sabe que el contenido viene en notación y debe parsearla como tal.

**B — `[gotcha]`**
- [ ] `[gotcha]` está en la lista de tags fijos, con criterio explícito de cuándo NO usarlo (no es "dato interesante", es "contradice el prior").
- [ ] `.claude/skills/pv-internal-tech-analysis/SKILL.md` eleva la atención sobre líneas `[gotcha]`.
- [ ] `.claude/skills/pv-internal-doc-style/SKILL.md` hereda el tag.

**C — Namespace**
- [ ] `.claude/skills/pv-internal-doc-technical/SKILL.md` tiene la sección "## Namespace" con las 5 filas de reglas, la frontera sintáctica y el orden de segmentos.
- [ ] `.claude/skills/pv-internal-doc-files/scripts/rebuild-index.py` y `.claude/skills/pv-internal-doc-files/scripts/next-feature-number.py` ignoran `00-*.md`; el prefijo reservado está documentado en `.claude/skills/pv-internal-doc-files/SKILL.md`.
- [ ] **Probado**: con un `00-namespace.md` en la carpeta, `.claude/skills/pv-internal-doc-files/scripts/rebuild-index.py` genera un `INDEX.md` que no lo lista, y `.claude/skills/pv-internal-doc-files/scripts/next-feature-number.py` devuelve el mismo número que devolvería sin él.
- [ ] Semilla creada por `.claude/skills/pv-init/scripts/scaffold-project.py` en `architectureDocDir`, con sus dos secciones, la regla de orden de segmentos y la excepción de §F.7; el script sigue siendo idempotente (no sobrescribe si ya existe).
- [ ] Hay **un solo** árbol: `styleBibleDocDir` no tiene semilla propia y sus conceptos cuelgan de `ui.*`.
- [ ] `.claude/skills/pv-internal-tech-analysis/SKILL.md` resuelve rutas contra `{architectureDocDir}/00-namespace.md` (también al leer `styleBibleDocDir`) y respeta `anchor:` como fuente de verdad.
- [ ] `.claude/skills/pv-do/SKILL.md` actualiza `00-namespace.md` con Read/Edit directo, y en ningún sitio se le dice de pasarlo por `upsert`.

**D — Anáforas**
- [ ] La regla 9 existe, menciona que el coste de estilo de repetir no cuenta, y tiene ejemplo MAL/BIEN.
- [ ] Cross-ref a "Namespace" para el caso "el referente tiene ruta canónica".

**E — Intensificadores**
- [ ] La regla 10 existe, cubre también comparativas sin baseline, y tiene ejemplo MAL/BIEN.
- [ ] La regla deja explícito que sin cifra la frase se omite entera, no se suaviza.

**F — Inglés fijo**
- [ ] `docs.tech.language` eliminada del schema, y sus otras 3 menciones (description de `interaction.language`, `_comments` del ejemplo, bloque de ejemplo) limpiadas.
- [ ] `.claude/skills/pv-init/SKILL.md`: pregunta 4 eliminada y las 3 restantes renumeradas; flujo "same for everything" ya no la setea; menciones a `docs.*.language` acotadas a `docs.functional`; nota "always technical English" añadida.
- [ ] `.claude/skills/pv-do/SKILL.md`: las 3 menciones sustituidas por "technical English", sin tocar lo que dice de `docs.functional.language`.
- [ ] `.claude/skills/pv-internal-doc-technical/SKILL.md`: sección renombrada a "Fixed language: technical English"; las dos prohibiciones gramaticales **invertidas a permitidas**; en la regla 6 se quitó "regardless of `docs.tech.language`" **pero se conservó** la frase sobre `pv-internal-doc-features`.
- [ ] `.claude/skills/pv-internal-doc-style/SKILL.md`: sus 2 menciones eliminadas.

**G — Verificación**
- [ ] `.claude/skills/pv-update/scripts/audit-context.py`: `OBSOLETE_KEYS` + `obsolete-field:*` implementado, incluido en el cálculo de `schemaOk`, y **probado** contra un `pv-context.json` que aún tenga la clave.
- [ ] `.claude/skills/pv-update/scripts/audit-context.py`: `namespace-missing`, `namespace-section-missing` y `namespace-anchor-broken:*` implementados, y **probados** cada uno contra un caso real (carpeta sin semilla; semilla sin `## Tree`; ancla a un fichero borrado).
- [ ] `.claude/skills/pv-update/SKILL.md`: entradas del fix loop para los cuatro `id` nuevos.
- [ ] `.claude/skills/pv-update/SKILL.md`: `namespace-anchor-broken` documentado como **tercera excepción** no auto-reparable, junto a las dos ya existentes, para que la skill no siga afirmando que solo hay dos.
- [ ] `.claude/skills/pv-update/SKILL.md`: `description` y cobertura del paso 2 mencionan las claves obsoletas y los chequeos de namespace.
- [ ] El script sigue siendo read-only: ningún chequeo nuevo escribe en disco.

**H — Documentación del framework** (solo `.es.md`)
- [ ] `.claude/pv-doc/pv-design/pv-design.es.md`: fichas de `pv-internal-doc-technical` y `pv-internal-doc-files` actualizadas; viñetas de los dos scripts corregidas; `docs.tech.language` eliminada de la viñeta de definición, del `_comments` del ejemplo y de la sección de idioma; `00-namespace.md` en el árbol de carpetas (solo bajo `architecture/`).
- [ ] `.claude/pv-doc/pv-guide.es.md`: los **dos** bloques de ejemplo de `pv-context.json` sin `docs.tech.language` (incluido el `_comments` del primero); viñeta de `docs.tech.language` eliminada de la lista de puntos configurables.
- [ ] `.claude/pv-doc/pv-guide.es.md`: el ejemplo 2 ya no se presenta como "documentación técnica en inglés **porque la configuras**"; su frase de entrada refleja que es fijo.
- [ ] `.claude/pv-doc/pv-guide.es.md`: el párrafo de "dos cosas se quedan siempre en inglés" dice **tres**, y la tercera es explícitamente toda la documentación técnica (`architectureDocDir` + `styleBibleDocDir`), con el porqué en una frase.
- [ ] `grep -n "docs.tech.language" .claude/pv-doc/pv-design/pv-design.es.md .claude/pv-doc/pv-guide.es.md` = 0 resultados.
- [ ] `.claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md`: revisado, sin cambios necesarios.
- [ ] **Pendiente registrado**: los `.en.md` (`pv-design.en.md`, `pv-guide.en.md`) siguen sin actualizar y contradicen a sus pares `.es.md`. Anotado como trabajo de traducción posterior, no como parte de este plan.

**Global**
- [ ] `grep -rn "docs.tech.language" .claude/skills/ .claude/pv-context.json` = 0 resultados. (En `.claude/pv-doc/` solo los `.es.md`; los `.en.md` la conservan hasta que se traduzcan.)
- [ ] `.claude/pv-context.json` migrado (§17) y `/pv-update` reporta limpio.
- [ ] `.claude/skills/pv-internal-doc-technical/SKILL.md` sin contradicción interna; su `description` de frontmatter revisada tras A/C y fiel a lo que la skill hace ahora.
- [ ] Una tarea de prueba (`pv-fix` trivial que toque un contrato documentado) recorre `pv-internal-tech-analysis` → `pv-do` sin fricción con el formato nuevo, y `00-namespace.md` sale actualizado y fuera del `INDEX.md`.
- [ ] `/dev-generate-version` ejecutado: versión consistente en `doc-technical`, `doc-style`, `tech-analysis`, `do`, `doc-files`, `init`, `update`.
