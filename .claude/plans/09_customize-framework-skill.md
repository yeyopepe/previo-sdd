# Plan: skill `pv-customize` — punto de entrada único para personalizar el framework

## Problema

Hoy existen **dos mecanismos de personalización** del framework pv-*, y ninguno se descubre solo:

1. **Hooks de proyecto** (`{workFolder}/stuff/hooks/{skill}/NN-nombre.md`) — pasos inyectados en puntos fijos de `pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-version`. Sembrados desde plantillas `.template.md` en cada skill (`.claude/skills/pv-do/hooks/*.template.md`, etc.), nunca sobrescritos una vez existen.
2. **`pv-context.json`** — config estructural: idiomas, rutas (`workFolder`, `sourcecodeDir`, `docs.*`), `skillModels` (requiere además correr `sync-skill-models.py`), `framework.skills.mockups`/`diagrams`.

`pv-init` cubre el bootstrap inicial (todas las preguntas, una vez). `pv-update` cubre reparar/migrar un `pv-context.json` roto o desactualizado. Ninguna de las dos responde a "quiero que antes de implementar se corra el linter" o "quiero cambiar el modelo de pv-status a Haiku" a mitad de vida del proyecto — el usuario tiene que saber de memoria dónde vive cada cosa.

## Propuesta: `pv-customize`

Nueva skill cuyo único trabajo es **enrutar**, no ejecutar la personalización ella misma:

1. Entender en lenguaje natural qué quiere el usuario ("que antes de hacer pv-do se ejecute X", "quiero que el changelog salga en inglés", "usa mockups en ASCII en vez de HTML").
2. Clasificar la petición en una de las categorías conocidas (ver tabla abajo).
3. Delegar a quien ya sabe hacerlo — no reimplementar lógica de `pv-init`/`pv-update` ni de edición de hooks.

Trigger: `/pv-customize`, o lenguaje como "personalizar", "configurar el framework para que...", "añadir un hook", "cambiar pv-context.json".

### Tabla de enrutado

| Petición del usuario | Acción de `pv-customize` |
|---|---|
| Añadir/editar un paso que se ejecuta antes/después de `pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-version` | Editar directamente el `.md` correspondiente en `{workFolder}/stuff/hooks/{skill}/`. Si el hook aún no existe (proyecto viejo, o `scaffold-project.py` no llegó a sembrarlo), copiar la plantilla `.template.md` de la skill primero. |
| Cambiar idioma (interacción, changes, versions, docs funcionales) | Delegar a `pv-init` (ya tiene el flujo de preguntas de idioma) — invocar en modo "solo revisar/completar este campo", no reinit completo. |
| Cambiar rutas (`workFolder`, `sourcecodeDir`, `docs.tech.*`, `docs.functional.*`) | Delegar a `pv-update` si el cambio implica mover contenido existente; edición directa + aviso si es solo repuntar un path vacío. |
| Cambiar `skillModels` (modelo/effort por skill) | Editar `pv-context.json` directamente y recordar ejecutar `sync-skill-models.py` — mismo patrón que ya documenta `pv-init`. |
| Cambiar `framework.skills.mockups` / `framework.skills.diagrams` (swap de skill de mockups o diagramas) | Editar `pv-context.json` directamente, validando que la skill destino existe en `.claude/skills/`. |
| Petición ambigua o que no encaja en ninguna fila | Preguntar al usuario con `AskUserQuestion`, no adivinar. |
| `pv-context.json` no existe o está roto | Redirigir a `pv-init`/`pv-update` primero, igual que ya hacen otras skills pv-*. |

## Por qué no ampliar `pv-init` o `pv-update` en su lugar

- `pv-init` está diseñado para **una pasada completa** (bootstrap) — añadirle "modo parche puntual para una sola pregunta suelta en cualquier momento" le complica el flujo de `workflow.init.md` sin necesidad.
- `pv-update` está diseñado para **detectar y reparar drift/roturas**, no para "quiero esta funcionalidad nueva a propósito". Mezclar intención de reparación con intención de personalización deliberada confunde ambos flujos.
- Los hooks nunca han tenido dueño — ninguna skill existente los edita, solo los siembra (`scaffold-project.py`) y los lee (`pv-do` etc. en tiempo de ejecución). `pv-customize` les da un punto de entrada sin tocar quien ya los consume.

`pv-customize` es una capa fina de enrutado que reutiliza `pv-init`/`pv-update` como sub-skills cuando aplica, y edita directamente hooks/`pv-context.json` cuando el cambio es autocontenido.

## Qué necesita saber `pv-customize` para clasificar (research antes de implementar)

- Listado completo de hooks disponibles por skill (ya está: `pv-do`×2, `pv-fix`×1, `pv-how`×2, `pv-new`×1, `pv-version`×4) — sacarlo de `.claude/skills/*/hooks/*.template.md`, no hardcodearlo, para que siga funcionando si se añaden hooks nuevos a otras skills en el futuro.
- `schema.json` de `pv-init` como fuente de verdad de qué campos existen en `pv-context.json` y su descripción — reusar, no duplicar.

## Formato: SKILL.md, como el resto del framework

`.claude/skills/pv-customize/SKILL.md` — es el único mecanismo por el que el harness descubre y dispara skills en este repo; no hay alternativa de formato a considerar.

Lo que sí decide si el disparo es fiable es la `description` del frontmatter, porque el enrutado a `pv-customize` ocurre **antes** de que corra ninguna lógica interna — Claude Code decide invocarla leyendo esa descripción. Tiene que:
- Nombrar explícitamente las categorías (hooks, idiomas, rutas, `skillModels`, mockups/diagramas), no quedarse en "personaliza el framework" genérico.
- Cubrir tanto intención de acción ("añade un hook que...", "cambia el modelo de...") como intención de consulta ("¿dónde configuro...?", "¿puedo cambiar...?") — el usuario también puede solo querer saber dónde mirar, no que se ejecute el cambio.

## Tabla de referencia determinista (dentro del propio SKILL.md)

En vez de fiarnos de que el modelo infiera bien el routing cada vez, `pv-customize` lleva una tabla fija "tipo de cambio → dónde vive y quién lo hace" (la de la sección "Tabla de enrutado" de este plan, ampliada). Fuentes que **no se duplican a mano** sino que se referencian, para no desincronizarse si el framework cambia:

- **Catálogo completo de hook points**: ya existe, completo y canónico, en [`pv-doc/pv-design/pv-design.en.md`](../pv-doc/pv-design/pv-design.en.md) (sección "The ten points", tabla `Skill | Hook | Runs`, líneas ~528-545) — los diez hooks actuales (`pv-how`×2, `pv-new`×1, `pv-fix`×1, `pv-do`×2, `pv-version`×4), su convención de nombre `<NN>-<before|after>-<object>` y las variables sustituibles. `pv-customize` lee esa tabla en vez de copiarla, así que si se añade un hook nuevo en el futuro (el propio doc referencia `plans/07_future-hooks.md` para propuestas no decididas) `pv-customize` queda al día automáticamente.
- **Catálogo de campos de `pv-context.json`**: `schema.json` de `pv-init`, igual que ya hace `pv-init`/`pv-update`.

## Qué NO puede hacer nunca `pv-customize`

Esto no existe hoy como documento único — es una convención implícita repartida por todo el framework (comentarios `_warning`, "never edited by hand" en `pv-internal-doc-files`, plantillas `.template.md` nunca sobrescritas una vez sembradas). `pv-customize` la consolida explícitamente en una sección propia de "límites", citando el patrón ya existente en vez de inventar reglas nuevas:

- **Nunca edita ningún `SKILL.md` ni script bajo `.claude/skills/*/`** (salvo, por supuesto, su propio archivo si en el futuro se le actualiza a mano fuera de esta skill) — eso es el core del framework, versionado y distribuido con el propio pv-*, no configuración de proyecto. Igual que ninguna otra skill pv-* se edita a sí misma ni a sus hermanas.
- **Nunca añade un hook point nuevo** (un `<NN>-<slug>` que no esté ya en la tabla de "The ten points") ni cambia dónde se ejecuta uno existente — eso requiere tocar el código de la skill dueña (`pv-do`, `pv-how`, etc.) y su `workflow.*.md`, es decisión de diseño del framework, no de un proyecto concreto. Si el usuario pide esto, `pv-customize` lo explica y remite a proponerlo en el repo del framework (`plans/07_future-hooks.md` es el sitio ya usado para eso), nunca lo improvisa localmente.
- **Nunca reescribe `INDEX.md` a mano** en ninguna carpeta de docs — siempre delegado a los scripts que ya lo regeneran (`pv-internal-doc-files`/`pv-internal-doc-technical`).
- **Nunca toca `pv.py`** directamente — es un artefacto generado, solo `scaffold-project.py` lo escribe.
- **Nunca sobrescribe una plantilla `.template.md`** de hooks ni un hook de proyecto ya sembrado con contenido previo — solo añade/edita `### Step` blocks dentro del archivo de proyecto en `stuff/hooks/`, nunca toca las `.template.md` fuente en `.claude/skills/*/hooks/`.
- **Nunca cambia campos fuera de lo declarado en `schema.json`** (`additionalProperties: false`) — cualquier campo nuevo necesario es, de nuevo, cambio de core, no de `pv-customize`.

Regla general que resume todas: `pv-customize` solo escribe dentro de `{workFolder}/stuff/**` y dentro de los campos ya existentes de `pv-context.json`. Cualquier petición que implique tocar algo bajo `.claude/skills/` (fuera de leer) se rechaza y se explica por qué, ofreciendo como alternativa documentarlo como propuesta para una futura versión del framework.

## Siguiente paso

Si esto encaja, redacto el `SKILL.md` de `pv-customize` siguiendo el patrón de las demás skills pv-* (frontmatter con `model`/`effort`/`metadata.uses`, sección de flujo con referencia a un `workflow.*.md` si la lógica de branching lo justifica — probablemente sí, dado que hay bifurcación real por tipo de petición), incluyendo la tabla determinista y la sección de límites de esta actualización del plan.
