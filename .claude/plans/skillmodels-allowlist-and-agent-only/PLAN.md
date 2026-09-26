# Plan: lista cerrada de skillModels + piloto agent-only por fases

## Índice

- [Objetivo](#objetivo)
- [Skills candidatas a agente-only](#skills-candidatas-a-agente-only)
- [Contexto y hallazgo clave](#contexto-y-hallazgo-clave)
- [Decisiones de diseño ya tomadas](#decisiones-de-diseño-ya-tomadas)
- [Parte A — Rediseño de skillModels](#parte-a--rediseño-de-skillmodels)
- [Parte B — Piloto agent-only (por fases)](#parte-b--piloto-agent-only-por-fases)
- [Fuera de alcance](#fuera-de-alcance-para-iteraciones-futuras)
- Implementación por fases:
  - [Fase 1 — TASKS-fase1.md](TASKS-fase1.md) (`pv-internal-tech-risks` + `pv-internal-tech-analysis`)
  - Fases futuras — aún sin `TASKS-*.md`, ver "Fuera de alcance"
- [Reviews](#reviews)

## Objetivo

Hoy el frontmatter `model:`/`effort:` de una skill solo lo respeta el
harness cuando esa skill se lanza como agente (`Agent(subagent_type: ...)`),
nunca cuando se invoca inline con `Skill()`. Esto hace que
`pv-context.json#skillModels` — pensado para que el usuario controle qué
modelo usa cada skill del framework — no tenga efecto real sobre ninguna
skill invocada del modo en que se invocan hoy todas.

Este plan tiene dos objetivos, uno dependiente del otro:

1. **Cerrar `skillModels`** a una lista completa y explícita de skills
   permitidas (sin `default` implícito, sin skills fuera de esa lista), para
   que el usuario tenga control total y auditable de qué skills existen y
   qué modelo/effort usa cada una.
2. **Validar el mecanismo con un piloto real, por fases**: convertir
   progresivamente las `pv-internal-*` candidatas en skills que se invocan
   exclusivamente como agente foreground, de modo que su entrada en
   `skillModels` (ya parte de la lista cerrada de la Parte A) tenga efecto
   real. La Parte A se implementa entera de una vez (aplica a las 22 skills
   por igual); la Parte B se implementa **por fases**, cada una con su
   propio `TASKS-*.md` (ver "Implementación por fases" en el índice):
   - **Fase 1** (`TASKS-fase1.md`, este plan): `pv-internal-tech-risks` +
     `pv-internal-tech-analysis`.
   - **Fases futuras**: el resto de candidatas de la tabla siguiente,
     definidas más adelante con su propio `TASKS-*.md` cuando se acometan
     (cambios de diseño adicionales si hacen falta, más las skills que
     falten).

## Skills candidatas a agente-only

De las 15 `pv-internal-*` (subrutinas nunca invocadas directamente por el
usuario), estas son las identificadas como candidatas a pasar a invocarse
exclusivamente como agente foreground, y el estado de cada una en este plan:

| Skill | Caller(s) | Modelo/esfuerzo por defecto | Estado |
|---|---|---|---|
| `pv-internal-tech-risks` | `pv-how` | `claude-haiku-4-5` / `medium` | 🔵 En progreso — fase 1 (`TASKS-fase1.md`) |
| `pv-internal-tech-analysis` | `pv-new`, `pv-fix`, `pv-how` | *(sin definir — `null`/`null`)* | 🔵 En progreso — fase 1 (`TASKS-fase1.md`); resuelve en esta misma fase el bloqueo de diálogo con el usuario vía el contrato `pending_questions` (ver Parte B) |
| `pv-internal-doc-features` | `pv-do` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-doc-files` | `pv-internal-doc-features`, `pv-do` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-doc-style` | `pv-do` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-doc-technical` | `pv-do` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-mockups-ascii` | `pv-new`, `pv-fix`, `pv-how` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-tech-mermaid` | `pv-internal-workflow`, `pv-new`, `pv-fix`, `pv-how` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-tech-security` | `pv-internal-tech-analysis` | `claude-sonnet-5` / `low` | ⚪ Pendiente — fase futura, aún sin definir (default de arranque ya decidido: `claude-sonnet-5`/`low`, ver nota debajo). Su único caller real hoy es `pv-internal-tech-analysis` (no `pv-how` directamente — verificado por grep, corrige una lectura anterior de este plan) |
| `pv-internal-workflow` | `pv-new`, `pv-fix`, `pv-do` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-changelog` | `pv-version` | *(sin definir — `null`/`null`)* | ⚪ Pendiente — fase futura, aún sin definir |
| `pv-internal-mockups-html` | `pv-new`, `pv-fix`, `pv-how` | *(sin definir — `null`/`null`)* | 🔴 Descartada — su `ensure-closed` necesita diálogo iterativo nota-por-nota con el humano, incompatible con agente puro |

Todas las 12 (incluida la descartada) siguen participando en la lista
cerrada de `skillModels` de la Parte A — ser agente-only y estar en
`skillModels` son cosas independientes; `skillModels` fija modelo/effort
para cualquier skill del framework, se invoque como se invoque.

**Excepción de scaffolding**: por regla general el scaffolding inicial de
`pv-init` deja `model`/`effort` a `null` para todas las skills (ver
"Decisiones de diseño" más abajo — nadie arranca forzado). Dos excepciones
decididas hasta ahora:
- `pv-internal-tech-risks`: al ser piloto de la fase 1, su entrada de
  partida en `allowed-skill-models.json`/scaffolding lleva ya
  `claude-haiku-4-5`/`medium` en vez de `null`/`null`, porque ya se evaluó y
  decidió explícitamente que ese es su par razonable por defecto (una skill
  de scoring puramente mecánico — 9 factores con reglas fijas — no necesita
  un modelo más caro).
- `pv-internal-tech-security`: aunque su conversión a agent-only queda para
  una fase futura, su default de arranque ya se decide en este plan (se
  fija ya en el asset de A.1, independientemente de cuándo se implemente su
  parte de agent-only): `claude-sonnet-5`/`low` — checklist de categorías
  fijas, razonamiento moderado pero no trivial, no necesita `medium`/`high`.

El resto de la tabla queda en `null` hasta que se decida lo mismo caso por
caso.

## Contexto y hallazgo clave

El framework ya tiene un pipeline para fijar modelo/effort por skill:
`pv-context.json#skillModels` se sincroniza al frontmatter real de cada
`SKILL.md` mediante `.claude/skills/pv-init/scripts/sync-skill-models.py` —
es el único paso que hace que `skillModels` tenga efecto real, porque el
harness solo lee el frontmatter, nunca `pv-context.json` directamente.

Hoy `skillModels` acepta **cualquier** nombre de skill en `overrides` (el
schema solo exige la forma `{model, effort}`, sin restringir claves) y usa
`default` + `overrides` (solo las que difieren del default se listan
explícitamente). Este plan lo cambia de raíz: pasa a ser una **lista cerrada
y completa**, sin `default`.

## Decisiones de diseño ya tomadas

1. **`skillModels` deja de tener `default`/`overrides`.** Pasa a ser un
   objeto plano `{ "<skillName>": { "model": ..., "effort": ... }, ... }`
   con una **entrada siempre presente** por cada skill permitida — ninguna
   implícita, ninguna ausente. No hay fallback porque no puede faltar
   ninguna.

   **El override en sí es opcional; la entrada no.** `model`/`effort` de
   una skill pueden ir **vacíos** (`null`) — eso significa "no forzar nada
   para esta skill": su frontmatter no se toca y queda tal cual esté en
   disco. Lo que nunca puede faltar es la clave de la skill dentro de
   `skillModels`, aunque su valor sea `{ "model": null, "effort": null }`.
   El schema (`modelConfig`) deja de exigir `model`/`effort` no vacíos —
   siguen siendo claves requeridas, pero su valor admite `null`.

2. **"Skills permitidas" es una lista cerrada, hardcoded**, no derivada de
   qué exista en disco. Vive en **un único fichero de datos, asset de
   `pv-init`** (`.claude/skills/pv-init/assets/allowed-skill-models.json`),
   listando cada skill `pv-*` que el framework reconoce. Es la única fuente
   de verdad — evita que `sync-skill-models.py` (en `pv-init`) y
   `audit-context.py` (en `pv-update`) mantengan listas duplicadas que
   puedan divergir. `pv-update` referencia este asset cruzando la carpeta
   de `pv-init`, igual que `pv-how` ya reutiliza
   `pv-internal-workflow/scripts/set-metadata.py` — patrón ya existente en
   el framework, no rompe la convención de skills autocontenidas.

3. **`pv-init` hace scaffolding inicial con `skillModels` completo pero
   vacío**: al generar `pv-context.json` por primera vez, escribe una
   entrada por cada skill del asset, todas con `model`/`effort` a `null` —
   no como mirror del frontmatter real (que es lo que hace
   `collect-skill-models.py` hoy), y tampoco con un valor fijo tipo
   sonnet/medium. El punto de partida es "todas presentes, ninguna forzada"
   — el usuario decide qué overrides concretos quiere rellenar.

4. **`pv-update` valida la lista cerrada**: si `pv-context.json#skillModels`
   tiene una entrada para una skill que ya no está en el asset de permitidas
   (borrada, renombrada, o nunca debió estar ahí), la elimina directamente
   sin preguntar, avisando al usuario de qué quitó y por qué. Si falta una
   entrada para una skill permitida, la añade con `model`/`effort` a `null`
   — mismo patrón "converge sin preguntar" que ya usa hoy para
   `skillmodel-drift`.

5. **`sync-skill-models.py` también repara `pv-context.json`, no solo
   propaga hacia el frontmatter.** Si al recorrer el asset de permitidas
   encuentra que a `pv-context.json#skillModels` le falta una entrada, avisa
   del error por stdout **y** la añade él mismo con `model`/`effort` a
   `null` (no delega esa reparación solo a `pv-update` — `pv-update` sigue
   haciendo su propia auditoría más amplia por separado, pero
   `sync-skill-models.py` deja de asumir que `pv-context.json` ya está bien
   formado). Y en la propagación hacia el frontmatter: una entrada con
   `model`/`effort` a `null` hace que el script **vacíe también esas claves
   del `SKILL.md`** correspondiente (las borra del frontmatter si estaban),
   en vez de dejarlas como estaban — vacío en `pv-context.json` se propaga
   como "sin `model`/`effort` explícito" en el frontmatter, no como
   "ignora esta skill".

6. **`invocation: agent-only` es un campo nuevo e independiente de
   `user-invocable`, no un sustituto ni una fusión.** Las 12 `pv-internal-*`
   ya tienen hoy `user-invocable: false` en su frontmatter — ese campo
   contesta "¿puede el usuario invocar esta skill directamente?" (documentado
   en `pv-design.en.md`/`.es.md`, sección "User-invocable" vs "Internal and
   support"). `invocation: agent-only` contesta una pregunta distinta: "¿con
   qué tool debe invocarla su caller interno?" (`Agent(...)` en vez de
   `Skill()` inline). Ninguno de los dos campos es una barrera real a nivel
   de harness — igual que `user-invocable: false` hoy es una convención que
   las skills/el propio Claude Code respetan sin impedir técnicamente que el
   usuario escriba el nombre a mano, `invocation: agent-only` tampoco impide
   que alguien la invoque inline si quisiera; es una señal para quien
   escribe o mantiene los callers, no un candado. Las dos claves coexisten
   en el frontmatter de una skill agent-only: `pv-internal-tech-risks` sigue
   teniendo `user-invocable: false` (sin cambios) y gana además
   `invocation: agent-only`. Este punto debe quedar explícito en A.8 y B.2
   (ver más abajo), no implícito.

## Parte A — Rediseño de skillModels

Base necesaria antes de la Parte B: el piloto depende de que
`pv-internal-tech-risks` sea una entrada válida y reconocida en la lista
cerrada, y de que el usuario pueda fijarle modelo/effort de forma auditable.

### A.1. Asset `allowed-skill-models.json`

Nuevo fichero: `.claude/skills/pv-init/assets/allowed-skill-models.json`.

Lista todas las skills `pv-*` que participan en `skillModels` — hoy, todas
las `pv-*` existentes (`pv-do`, `pv-fix`, `pv-how`, `pv-init`, `pv-new`,
`pv-review-architecture`, `pv-review-doc-tech`, `pv-status`, `pv-todo`,
`pv-update`, `pv-version`, y las 15 `pv-internal-*`).

Cada entrada admite opcionalmente un `model`/`effort` de partida — por
regla general ausente (`null`/`null` al hacer scaffolding), salvo que se
haya evaluado y decidido explícitamente lo contrario para esa skill (hoy
solo `pv-internal-tech-risks`, ver "Skills candidatas a agente-only"). Ese
default de partida es distinto del override que el usuario pone luego en su
propio `pv-context.json` — es solo lo que `pv-init` escribe la primera vez.

Formato propuesto:
```json
{
  "_comment": "Lista cerrada de skills 'pv-*' reconocidas por skillModels, con el par model/effort de arranque que pv-init escribe en pv-context.json la primera vez (null/null salvo excepción explícitamente decidida). Mantenida a mano al añadir/quitar una skill del framework, o al decidir un default de arranque distinto para alguna. Única fuente de verdad, referenciada por pv-init/scripts/sync-skill-models.py, pv-init/scripts/collect-skill-models.py, y pv-update/scripts/audit-context.py.",
  "skills": {
    "pv-do": { "model": null, "effort": null },
    "pv-internal-tech-risks": { "model": "claude-haiku-4-5", "effort": "medium" }
  }
}
```

### A.2. `schema.json`

Cambiar la definición de `skillModels`:
- Eliminar `default` y `overrides`.
- Pasa a ser `additionalProperties: { "$ref": "#/$defs/modelConfig" }`
  directamente (un mapa plano nombre→config), manteniendo `_instructions`
  como única clave especial ignorada en runtime.
- `modelConfig` (`$defs`): `model`/`effort` siguen siendo claves requeridas,
  pero su tipo pasa a admitir `null` además de `string` (p. ej.
  `"type": ["string", "null"]`) — una entrada `{ "model": null, "effort": null }`
  es válida y es justamente el estado "sin override" de una skill permitida.
- Actualizar la `description` de `skillModels` para reflejar que ya no es
  "opcional, un default + overrides parciales" sino "obligatorio tener una
  entrada por cada skill de la lista cerrada (aunque su `model`/`effort`
  sean `null`), sin entradas fuera de esa lista".

### A.3. `collect-skill-models.py`

Reescribir: en vez de calcular un `default` por frecuencia + `overrides`
parciales, lee el asset `allowed-skill-models.json`, y para cada skill de
esa lista busca su `model`/`effort` real en su `SKILL.md` si existe en
disco; si no lo tiene explícito en el frontmatter, usa el `model`/`effort`
de arranque que traiga el asset para esa skill (`null`/`null` salvo
excepción, como `pv-internal-tech-risks`). Devuelve el mapa plano completo,
una entrada por cada skill permitida, nunca ausente.

### A.4. `sync-skill-models.py`

**Si `.claude/pv-context.json` no existe en absoluto**, el comportamiento no
cambia respecto a hoy: el script avisa por stdout ("No .claude/pv-context.json
-- nothing to sync.") y no hace nada más — no lo crea desde cero. Esta
reescritura solo cambia cómo resuelve cada skill una vez el fichero ya
existe.

Reescribir la resolución: en vez de `overrides.get(skill_name, default)`,
itera únicamente sobre las skills del asset `allowed-skill-models.json` (no
sobre `glob("pv-*/SKILL.md")` como hoy). Para cada skill del asset:

- Si `pv-context.json#skillModels` **no tiene** entrada para ella: es un
  error de configuración — avisa por stdout (mensaje claro de qué skill
  falta y por qué es un problema) **y la añade él mismo** a
  `pv-context.json#skillModels` con `{ "model": null, "effort": null }`,
  reescribiendo el JSON. No delega esta reparación solo a `pv-update`.
- Si la entrada existe con `model`/`effort` a `null`: **vacía también esas
  claves en el frontmatter** del `SKILL.md` correspondiente si las tenía
  (las borra), dejando la skill sin `model:`/`effort:` explícito — vacío en
  `pv-context.json` significa "no gestiono esto", y eso se propaga como
  ausencia de esas claves en el frontmatter, no como "no lo toco".
- Si la entrada existe con `model`/`effort` no vacíos: propaga esos valores
  al frontmatter como hoy.

### A.5. `pv-init/SKILL.md`

Actualizar el paso de scaffolding: al escribir `pv-context.json` por primera
vez, generar `skillModels` como mapa plano completo — todas las skills del
asset, cada una con el `model`/`effort` de arranque que traiga
`allowed-skill-models.json` (por regla general `null`/`null`; hoy
`claude-haiku-4-5`/`medium` solo para `pv-internal-tech-risks`) — no como
mirror vía `collect-skill-models.py` del frontmatter real. Todas presentes;
el usuario decide después qué overrides concretos rellenar o cambiar.
Mantener el resto del flujo (preguntar al usuario si quiere personalizar
algo, escribir, correr `sync-skill-models.py`).

### A.6. `pv-update/scripts/audit-context.py` + `pv-update/SKILL.md`

- Nueva categoría de problema: `skillmodel-not-allowed:<name>` — una entrada
  en `skillModels` cuyo nombre no está en el asset de permitidas.
- Nueva categoría: `skillmodel-missing:<name>` — falta una entrada para una
  skill que sí está en la lista de permitidas.
- Regla de reparación (converge sin preguntar, mismo patrón que
  `skillmodel-drift` ya documentado): elimina las `not-allowed` avisando al
  usuario qué quitó y por qué; añade las `missing` con
  `{ "model": null, "effort": null }` (salvo que el asset traiga un default
  de arranque distinto para esa skill).
- `audit-context.py` referencia el asset cruzando la carpeta de `pv-init`
  (ruta relativa `../../pv-init/assets/allowed-skill-models.json` desde
  `pv-update/scripts/`), documentando esa dependencia igual que `pv-how`
  documenta su dependencia de `pv-internal-workflow/scripts/set-metadata.py`.

### A.7. `pv-context.json` (este repo, dogfooding)

Regenerar su `skillModels` al nuevo formato plano y completo, corriendo el
nuevo `pv-init`/script de collect. Se hace como parte de la ejecución del
plan, no como cambio manual suelto.

### A.8. Documentación

Actualizar `.claude/pv-doc/pv-guide.en.md` / `.es.md` (sección "Model/effort
per skill: skillModels") para reflejar el mapa plano sin `default`/
`overrides`, y mencionar el asset de permitidas — ese doc es cara al usuario
final, así que basta con explicar el formato nuevo y qué pasa si edita algo
fuera de la lista cerrada (lo elimina `pv-update`).

`.claude/pv-doc/pv-design/pv-design.en.md` / `.es.md` es documentación
técnica interna del propio framework (para quien lo desarrolla, no para
quien lo usa) y requiere un cuidado especial: no basta con actualizar la
sección `### skillModels` al nuevo formato de JSON — hay que revisar y dejar
explícito **todo el mecanismo real**, con la misma precisión con la que hoy
documenta `sync-skill-models.py`:

- **Qué es la lista cerrada y por qué existe** — no solo "el formato cambió
  de default+overrides a mapa plano", sino la razón de diseño: control
  auditable total, ninguna skill fuera de una lista conocida.
  `allowed-skill-models.json` como única fuente de verdad, y qué scripts lo
  leen (`collect-skill-models.py`, `sync-skill-models.py`,
  `audit-context.py`) — igual de explícito que como `pv-design.en.md:88` ya
  documenta hoy que `sync-skill-models.py` "es el único paso que hace X
  real" para la propagación de `skillModels` al frontmatter (ese es el
  precedente a seguir; no es una referencia cruzada `pv-how`↔
  `set-metadata.py`, que vive en otra parte del documento).
- **El ciclo de vida completo de una entrada de `skillModels`**: creada por
  `pv-init` al hacer scaffolding (sonnet/medium fijo, no mirror), corregida
  por `pv-update` si sobra o falta (con qué criterio, sin preguntar),
  propagada al frontmatter real por `sync-skill-models.py`. Sin esto, quien
  lea `pv-design` no entiende que las tres skills cooperan sobre el mismo
  fichero con roles distintos.
- **Que `skillModels` y "agente-only" son ejes independientes** — la tabla
  de candidatas de este plan lo dice, pero `pv-design` es donde debe quedar
  documentado de forma permanente: toda skill de la lista cerrada tiene una
  entrada de modelo/effort, se invoque como se invoque; ser agente-only
  (frontmatter §`invocation: agent-only`) es una propiedad aparte que decide
  *cómo* la invoca su caller, no si participa en `skillModels`. Documentar
  ambos conceptos sin que se lean como la misma cosa es explícitamente el
  objetivo de este ítem — es el punto donde más fácil es dejar el documento
  ambiguo o incompleto si se actualiza deprisa.
- **El nuevo campo `invocation: agent-only`** del frontmatter (introducido
  en la Parte B) — documentarlo junto a `model`/`effort` como otro campo de
  frontmatter con significado especial para el harness/los callers, ya que
  `pv-design` es hoy la referencia técnica de cómo se comporta el frontmatter
  de una skill.
- **Su relación explícita con `user-invocable`** (ya documentado hoy en la
  sección "User-invocable" vs "Internal and support" de `pv-design`):
  `invocation: agent-only` no sustituye ni fusiona `user-invocable: false` —
  son dos campos independientes que coexisten en el frontmatter de la misma
  skill. `user-invocable: false` contesta "¿puede el usuario invocarla
  directamente?"; `invocation: agent-only` contesta "¿con qué tool debe
  invocarla su caller interno (`Agent()` vs `Skill()`)?". Ninguno de los dos
  es una restricción real a nivel de harness, ambos son convenciones que
  las skills/callers respetan. Dejar esto explícito evita que quien lea el
  frontmatter de `pv-internal-tech-risks` (con ambas claves a la vez) piense
  que son lo mismo o que una sobra.

Antes de dar este ítem por cerrado, releer `pv-design.en.md`/`.es.md` de
punta a punta en busca de cualquier otra mención residual a `default`/
`overrides` (ejemplos de JSON, prosa, índice) que quedara desalineada con el
nuevo mecanismo — un ejemplo de código desactualizado en un documento de
referencia técnica es peor que no tener el ejemplo.

## Parte B — Piloto agent-only (por fases)

Asume que la Parte A ya está implementada y que toda skill de esta parte es
una entrada reconocida en `allowed-skill-models.json`.

La implementación de la Parte B está dividida en fases (ver índice) — este
documento describe **el diseño completo** de la fase 1, que cubre dos
skills: `pv-internal-tech-risks` (piloto original, sin cambios de diseño
respecto a antes) y `pv-internal-tech-analysis` (nueva incorporación a esta
fase, que requiere resolver primero su bloqueo de diálogo con el usuario —
ver B.0).

### B.0. `pv-internal-tech-analysis`: contrato `pending_questions`

**Bloqueo identificado**: el paso 3 de `pv-internal-tech-analysis/SKILL.md`
("Doubts neither documentation nor code resolve", línea 74) hoy dice que si
queda una duda de definición que ni la documentación ni el código resuelven,
la skill "confirma con el usuario" antes de considerar el contexto reunido.
Eso funciona invocada inline (`Skill()`, corre en el turno principal, puede
usar `AskUserQuestion` con normalidad) pero es incompatible con
`Agent(run_in_background: false)`: un agente corre en un contexto aislado,
sin canal para preguntar al humano y bloquear el turno del caller a
esperar respuesta.

**Contrato nuevo, decidido en esta fase** (sustituye la redacción actual del
paso 3's "Doubts..." subsección):

1. El agente **nunca pregunta directamente**. Si queda una duda de
   definición bloqueante tras los pasos 1-3, sigue formulando "la solución
   que le parece más razonable" (como ya hace hoy) pero la marca como
   *asumida, no confirmada*.
2. Añade un nuevo campo al resultado devuelto en el paso 6:
   **`pending_questions`** — lista (vacía si no hay ninguna duda) de
   objetos `{doubt, assumed_answer}` (la duda formulada + la respuesta
   asumida).
3. El **caller** (`pv-new`, `pv-fix`, o `pv-how` — los tres corren en el
   turno principal, con acceso a `AskUserQuestion`) es responsable de: si
   `pending_questions` no está vacío, mostrar cada duda al usuario vía
   `AskUserQuestion` (usando `assumed_answer` como opción recomendada). Si
   el usuario confirma la respuesta asumida, no hay nada más que hacer. Si
   da una respuesta distinta, el caller usa la respuesta real (no la
   asumida) al escribir su propio documento (`description.md`/`plan.md`) —
   **no hace falta reinvocar el agente** en el caso normal, porque la duda
   es puntual y su resolución no cambia el resto del contexto ya reunido.
4. Solo si el caller juzga que la respuesta real cambia algo más profundo
   del análisis ya devuelto (caso raro), puede reinvocar el agente pasándole
   la respuesta como contexto adicional en un nuevo prompt.

Este contrato reemplaza, en el cuerpo de `pv-internal-tech-analysis/SKILL.md`,
la frase actual "confirms it with the user before considering the context
gathered" (paso 3) y añade `pending_questions` a la lista de lo que el paso
6 devuelve al caller.

### B.1. Restricción de diseño: invocación síncrona en el mismo turno

Ambas skills de esta fase se invocan hoy de forma síncrona por su(s)
caller(s), que necesitan su resultado en el mismo turno para continuar:

- `pv-how` invoca a `pv-internal-tech-risks`: necesita su resultado (9
  factores + mediana) en el mismo turno para escribirlo acto seguido en
  `.metadata.json` vía `set-metadata.py --set-risk`, y no puede considerar
  `plan.md` cerrado sin ese valor (`pv-how/SKILL.md` línea 155, check
  explícito).
- `pv-new` (línea 31), `pv-fix` (líneas 36 y 60), y `pv-how` (línea 135)
  invocan a `pv-internal-tech-analysis`: los tres necesitan su resultado
  (contexto reunido, inconsistencias, `pending_questions`) en el mismo
  turno para continuar con su propio flujo (escribir `description.md`,
  decidir si el fix es `fast`, escribir `plan.md`).

Por tanto, en ambos casos: `Agent(..., run_in_background: false)` —
foreground, nunca background. Un agente en background rompería el flujo
síncrono de los tres callers.

### B.2. Frontmatter de `pv-internal-tech-risks/SKILL.md`

Añadir `invocation: agent-only`, más una línea en el cuerpo (junto a "Not
meant for direct invocation by the user") aclarando que se invoca como
agente foreground, nunca inline vía `Skill()`, y por qué: es lo que permite
que su `model`/`effort` —ya sincronizado desde `pv-context.json#skillModels`
por `sync-skill-models.py`— tenga efecto real.

`user-invocable: false` (ya presente en esta skill) **no se toca, no se
quita, no se fusiona**: sigue significando "el usuario no la invoca
directamente", exactamente como hoy. `invocation: agent-only` se añade como
clave nueva e independiente, coexistiendo con `user-invocable: false` en el
mismo frontmatter — cada una contesta una pregunta distinta (ver Decisión de
diseño 6).

### B.3. `pv-how/SKILL.md`, paso 3.1 (línea ~145)

Cambiar de `Skill()` inline a `Agent(run_in_background: false)`, con un
prompt autocontenido que incluya el contenido ya leído de `plan.md` y
`description.md` — el agente no hereda memoria de conversación, así que todo
lo que hoy llegaba por contexto compartido debe ir explícito en el prompt.

**Manejo de fallo del agente** (modo de fallo nuevo, inexistente con
`Skill()` inline): si el agente falla, hace timeout, o devuelve un resultado
que no puede parsearse como los 9 factores + mediana esperados, `pv-how`
**siempre avisa al usuario** (qué pasó, en términos simples) **y relanza el
agente** con el mismo prompt — nunca se salta el paso ni escribe un valor
placeholder en `.metadata.json`. No hay límite de reintentos definido en
este plan: reintenta cada vez que falla, avisando cada vez.

Sin cambios: escritura en `.metadata.json`, el check de la línea 155, y el
reúso de resultado de la línea 157 (si el usuario pide el detalle más tarde
en la misma conversación y el resultado sigue en contexto, no relanzar el
agente).

### B.4. `workflow.how.md`

Verificado: el nodo `S31Risk` (línea 59) dice "Invoke pv-internal-tech-risks
on plan.md/description.md" — agnóstico a `Skill` vs `Agent`, no menciona
ningún tool concreto. **No requiere cambio.**

### B.5. Frontmatter de `pv-internal-tech-analysis/SKILL.md`

Añadir `invocation: agent-only`, sin tocar `user-invocable: false` (ya
presente — mismo criterio de independencia que B.2/Decisión de diseño 6).
Añadir una línea en el cuerpo (junto a "Only invoked by other `pv-*`
framework skills — not meant for direct invocation by the user") aclarando
que se invoca como agente foreground desde sus tres callers, nunca inline
vía `Skill()`.

Reescribir el paso 3's subsección "Doubts neither documentation nor code
resolve" (línea 74) y el paso 6 (línea 90) siguiendo el contrato
`pending_questions` de B.0.

### B.6. Los tres callers de `pv-internal-tech-analysis`: `pv-new`, `pv-fix`, `pv-how`

Cambiar de `Skill()` inline a `Agent(run_in_background: false)` en cada uno
de los tres puntos de invocación, con un prompt autocontenido (el agente no
hereda memoria de conversación — todo lo que hoy llegaba por contexto
compartido, como el resumen de lo analizado o `bootstrap: true` cuando
aplica, debe ir explícito en el prompt):

- **`pv-new/SKILL.md`** (línea 31, dentro de "Source of truth").
- **`pv-fix/SKILL.md`** (línea 36 "Source of truth", y línea 60, paso 2
  "Assess whether the change is `fast`" — es la misma invocación descrita
  dos veces en el documento; un solo cambio de mecanismo, aplicado en el
  punto real de invocación del paso 2).
- **`pv-how/SKILL.md`** (línea 135, paso 3, punto 5).

**Manejo de `pending_questions`** en los tres: tras recibir el resultado del
agente, si `pending_questions` no está vacío, usar `AskUserQuestion` con
cada `{doubt, assumed_answer}` (la respuesta asumida como opción
recomendada) antes de continuar el propio flujo; usar la respuesta real del
usuario en el documento que se esté escribiendo (`description.md` en
`pv-new`/`pv-fix`, `plan.md` en `pv-how`) sin reinvocar el agente, salvo que
el caller juzgue que la respuesta cambia algo más profundo del análisis (ver
B.0, punto 4).

**Manejo de fallo del agente** en los tres (mismo criterio que B.3): si
falla, hace timeout, o devuelve un resultado no parseable, avisar siempre al
usuario y relanzar el agente con el mismo prompt — nunca continuar el propio
flujo sin un resultado válido. Sin límite de reintentos definido.

### B.7. Diagramas (`workflow.new.md`, `workflow.fix.md`, `workflow.how.md`)

Revisar, en cada uno de los tres, el nodo que representa la invocación a
`pv-internal-tech-analysis` — mismo criterio que B.4: actualizar solo si el
diagrama detalla explícitamente el tool de invocación (`Skill` vs `Agent`);
si es agnóstico, no requiere cambio. `pv-how/workflow.how.md` ya se
verificó como agnóstico para el nodo de `pv-internal-tech-risks` (B.4); su
nodo de `pv-internal-tech-analysis` (paso 3, punto 5) queda por verificar
en la ejecución, igual que los nodos equivalentes de `workflow.new.md` y
`workflow.fix.md`.

### B.8. Versión

Subir el patch de `metadata.version` en `pv-internal-tech-risks/SKILL.md`,
`pv-internal-tech-analysis/SKILL.md`, `pv-how/SKILL.md`, `pv-new/SKILL.md`,
`pv-fix/SKILL.md`, `pv-init/SKILL.md`, `pv-update/SKILL.md` (todos
modificados).

## Fuera de alcance (para iteraciones futuras)

- Migrar las otras 9 `pv-internal-*` candidatas a agente-only, en fases
  futuras aún sin definir (`TASKS-*.md` propio para cada una cuando se
  acometa): `pv-internal-doc-features`, `pv-internal-doc-files`,
  `pv-internal-doc-style`, `pv-internal-doc-technical`,
  `pv-internal-mockups-ascii`, `pv-internal-tech-mermaid`,
  `pv-internal-tech-security` (su default de arranque `claude-sonnet-5`/
  `low` ya queda fijado en la Parte A de este plan — ver tabla de
  candidatas; solo su conversión a agent-only queda para una fase futura),
  `pv-internal-workflow`, `pv-internal-changelog`.
- Resolver el `ensure-closed` iterativo de `pv-internal-mockups-html` (queda
  descartada de la conversión a agente-only por ese motivo).

## Reviews

### 2026-09-26 — Análisis crítico

#### Estructura

| Finding | Explanation | Proposed improvement |
|---|---|---|
| Estructura OK | `PLAN.md` tiene Título, Índice completo (con enlace a `TASKS.md` en vez de "Implementation plan" inline), Objetivo, contenido propio, y `Reviews` como última sección. `TASKS.md` existe como fichero hermano y desglosa en tareas concretas cada elemento identificado en el análisis (asset, schema, cada script, cada `SKILL.md`, cada doc, cada traducción gemela). No se detectan desviaciones estructurales. | — |

#### Skills candidatas a agente-only

| Finding | Explanation | Proposed improvement |
|---|---|---|
| Campo `invocation: agent-only` posiblemente redundante con `user-invocable: false` ya existente | Las 12 `pv-internal-*` (incluida `pv-internal-tech-risks`) ya tienen hoy `user-invocable: false` en su frontmatter (confirmado en `pv-internal-tech-risks/SKILL.md:4` y en las otras 11 vía grep), y `pv-design.en.md` ya documenta una sección "User-invocable" vs "Internal and support" basada en ese campo. El plan introduce un segundo campo (`invocation: agent-only`) sin decir en ningún punto de PLAN.md qué relación tiene con `user-invocable` — son ejes conceptualmente distintos (uno dice "quién puede invocarla", el otro diría "cómo se invoca técnicamente"), pero el plan no lo aclara, y el ítem A.8 pide documentar que "`skillModels` y agente-only son ejes independientes" sin mencionar siquiera la existencia de `user-invocable`. Riesgo real de que quien lea el frontmatter final vea dos campos aparentemente solapados (`user-invocable: false` + `invocation: agent-only`) sin entender por qué no es uno solo. | Se mantienen como dos campos independientes (decisión del usuario, ninguno de los dos es una restricción real a nivel de harness, son convenciones distintas). Añadida Decisión de diseño 6 en PLAN.md explicando la relación; A.8/B.2 en PLAN.md y las tareas correspondientes de A.8/B.1 en TASKS.md ahora dicen explícitamente que `user-invocable: false` no se toca ni se fusiona. |
| Excepción de `pv-internal-mockups-html` no propagada a A.1/TASKS.md de forma explícita | La tabla dice que `pv-internal-mockups-html` queda descartada de agent-only por su `ensure-closed` iterativo, y TASKS.md sí la incluye correctamente en el asset de A.1. Pero el ítem A.1 en `TASKS.md` describe el asset como si todas las entradas fueran `null`/`null` "excepto `pv-internal-tech-risks`" — no aclara que esa exclusión de agent-only es independiente de su valor en el asset (que sigue siendo `null`/`null` como cualquier otra pendiente). No es un error de contenido, pero es un punto donde el redactor de TASKS.md podría, al ejecutar, dudar si `pv-internal-mockups-html` necesita algún tratamiento especial en el asset — no lo necesita, solo en la tabla de candidatas. | Descartado — el usuario considera que la tabla de candidatas en PLAN.md ya lo deja suficientemente claro; no se toca TASKS.md. |

#### Contexto y hallazgo clave / Decisiones de diseño

| Finding | Explanation | Proposed improvement |
|---|---|---|
| — | Verificado contra el repo: `schema.json` hoy exige `default`+`overrides` (`schema.json:23-32`), `sync-skill-models.py` resuelve con `overrides.get(skill_name, default)` (`sync-skill-models.py:118`) e itera `glob("pv-*/SKILL.md")` en vez de una lista cerrada (`sync-skill-models.py:116`), y `collect-skill-models.py` calcula el `default` por frecuencia (`collect-skill-models.py:77-89`). Todo coincide exactamente con lo que el plan describe como estado actual — sin hallazgos aquí. | — |

#### Parte A — Rediseño de skillModels

| Finding | Explanation | Proposed improvement |
|---|---|---|
| A.6 y A.8 citan una ruta de doc técnica incorrecta | El plan y `TASKS.md` referencian `pv-doc/pv-design/pv-design.en.md` y `pv-doc/pv-guide.en.md`, pero la ruta real en este repo es `.claude/pv-doc/pv-design/pv-design.en.md` y `.claude/pv-doc/pv-guide.en.md` (confirmado con Glob). Falta el prefijo `.claude/` en ambas menciones de PLAN.md (§A.8) y en las tareas correspondientes de `TASKS.md`. | Corregido — añadido el prefijo `.claude/` en PLAN.md §A.8 y en las tareas de A.8 de TASKS.md (ambos idiomas, PLAN.md y guide). |
| A.8 cita mal el precedente de "línea 88" | PLAN.md decía que "`pv-design.en.md:88` ya sienta el precedente de nombrar qué script hace qué y por qué es 'el único paso que hace X real'", enlazándolo implícitamente a la relación `pv-how`↔`set-metadata.py`. En realidad la línea 88 real de `pv-design.en.md` no menciona `pv-how` ni `set-metadata.py` — describe la propagación de `skillModels` vía `sync-skill-models.py` hacia el frontmatter. El precedente en sí (explicitar qué script hace qué) era válido, pero la atribución concreta estaba mal identificada. | Corregido — reescrita la frase en PLAN.md §A.8 para que cite correctamente que la línea 88 documenta la propagación de `skillModels` por `sync-skill-models.py`, sin mencionar una referencia cruzada `pv-how`↔`set-metadata.py` que no está ahí. |
| A.4 no dice qué pasa si `pv-context.json` no existe en absoluto | El script actual (`sync-skill-models.py:100-103`) sale con un mensaje si `.claude/pv-context.json` no existe. El plan (A.4) describía el nuevo comportamiento de "entrada faltante para una skill" pero no decía explícitamente si ese caso (fichero entero ausente) se mantenía igual o si el script debía crear `pv-context.json` desde cero. | Resuelto — se mantiene el comportamiento actual (avisa por stdout, no crea el fichero). Explicitado en PLAN.md §A.4 y en la tarea de A.4 en TASKS.md. |
| A.6 no especificaba el valor exacto que usan las categorías nuevas al reparar `missing` | PLAN.md §Decisiones 4 y A.6 decían que `pv-update` "añade las `missing` con `{ "model": null, "effort": null }`", pero en la sección A.6 la frase literal era "añade las `missing` con sonnet/medium por defecto", contradiciendo tanto la Decisión 4 como el propio `TASKS.md`. | Corregido — reescrita la frase en PLAN.md §A.6 para usar `{ "model": null, "effort": null }` (salvo excepción del asset), coherente con Decisión 4, A.4 y `TASKS.md` (que ya estaba correcto y no necesitó cambio). |

#### Parte B — Piloto pv-internal-tech-risks como agente foreground

| Finding | Explanation | Proposed improvement |
|---|---|---|
| B.2 pide añadir `invocation: agent-only` pero no dice si `user-invocable: false` se mantiene, se quita, o se fusiona | Ligado al hallazgo de la tabla de candidatas (ya resuelto arriba): B.2 solo decía "añadir `invocation: agent-only` al frontmatter", dejando implícito que `user-invocable: false` se queda igual. | Resuelto junto al finding equivalente de la tabla de candidatas — `user-invocable: false` se mantiene sin cambios; ambos campos son independientes. PLAN.md §B.2 y la tarea de B.2 (`pv-internal-tech-risks/SKILL.md`) en TASKS.md ahora lo dicen explícitamente. |
| B.3 no cubría qué pasa si el agente falla o devuelve un resultado no parseable | El paso 3.1 de `pv-how` hoy asume que la invocación `Skill()` devuelve el resultado en el mismo turno de forma fiable. Al pasar a `Agent(run_in_background: false)`, se introduce una superficie de fallo que no existía antes (el agente puede fallar, devolver un formato inesperado, o timeout) sin que el plan dijera qué hacer. | Resuelto — decisión del usuario: siempre avisar al usuario y relanzar el agente con el mismo prompt, sin límite de reintentos, nunca saltar el paso ni escribir un placeholder. Añadido a PLAN.md §B.3 y a la tarea de B.3 (`pv-how/SKILL.md`) en TASKS.md. |
| B.4 no verificaba si el nodo del diagrama es realmente agnóstico | El criterio de B.4 era correcto pero no se había verificado si `workflow.how.md:59` (`S31Risk`) menciona `Skill`/`Agent` explícitamente. | Resuelto — verificado: el nodo es agnóstico ("Invoke pv-internal-tech-risks on plan.md/description.md", sin tool concreto). No requiere cambio. Actualizado PLAN.md §B.4 y marcada como hecha en TASKS.md. |

#### Fuera de alcance

| Finding | Explanation | Proposed improvement |
|---|---|---|
| — | Sección coherente con el resto del plan; lista exactamente las 10 candidatas restantes de la tabla más los dos temas ya mencionados en el cuerpo (pending_questions, ensure-closed de mockups-html). Sin hallazgos. | — |

### 2026-09-26 (continuación) — Ampliación de alcance: fase 1 pasa a incluir `pv-internal-tech-analysis`

Decisiones tomadas con el usuario, no bugs encontrados en revisión — se
documentan aquí para conservar el historial de por qué el plan cambió de
forma:

- **La implementación de la Parte B pasa a ser por fases.** En vez de un
  único `TASKS.md`, cada fase tiene su propio `TASKS-*.md` (este plan
  documenta el diseño completo, pero solo implementa la fase 1). `TASKS.md`
  se renombró a `TASKS-fase1.md`; el índice de `PLAN.md` ahora enlaza a
  cada fase en vez de a un único fichero.
- **Fase 1 pasa de una skill a dos**: se añade `pv-internal-tech-analysis`
  junto a `pv-internal-tech-risks`. Se descartó incluir
  `pv-internal-tech-security` en la fase 1 (su único caller real es
  `pv-internal-tech-analysis`, no `pv-how` como se pensó al principio —
  corregido en la tabla de candidatas) porque exigía un patrón nuevo sin
  resolver (agente lanzado desde dentro de una skill inline); en su lugar
  se decidió mover `pv-internal-tech-analysis` misma a agent-only, lo que
  de paso resuelve por completo ese problema (ya no hay skill inline en
  medio — el árbol de invocación pasa a ser agente→agente, patrón normal).
  El default de arranque de `pv-internal-tech-security`
  (`claude-sonnet-5`/`low`) se fija ya en esta fase (es solo un valor en el
  asset de la Parte A, que se implementa entera), aunque su conversión a
  agent-only queda para una fase futura.
- **Se resuelve el bloqueo de `pending_questions`** que el plan tenía
  aparcado como "fuera de alcance": nuevo contrato explícito en PLAN.md §
  B.0 — el agente nunca pregunta directamente, devuelve
  `{doubt, assumed_answer}` por cada duda sin resolver, y el caller (que sí
  corre en el turno principal) decide si usar `AskUserQuestion` y si
  reinvocar el agente con la respuesta real. Aplica a los tres callers de
  `pv-internal-tech-analysis` (`pv-new`, `pv-fix`, `pv-how`).
- Cambios aplicados: `PLAN.md` (objetivo, tabla de candidatas, título,
  índice, nueva sección B.0, B.1/B.5/B.6/B.7/B.8 ampliados, "Fuera de
  alcance" reducido a 9 candidatas); `TASKS-fase1.md` (renombrado desde
  `TASKS.md`, A.1 con el default de `pv-internal-tech-security`, nueva
  sección de tareas para `pv-internal-tech-analysis` y sus tres callers,
  verificación ampliada).
