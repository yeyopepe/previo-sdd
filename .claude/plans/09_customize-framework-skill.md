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

### Step 0, antes de clasificar nada: auditar

Igual que cualquier skill pv-* que va a tocar `pv-context.json`, `pv-customize` corre primero `python .claude/skills/pv-update/scripts/audit-context.py`:
- Si el archivo no existe o es JSON inválido → redirigir a `pv-init`/`pv-update`, no continuar.
- Si `problems` no está vacío → avisar al usuario de que hay drift pendiente y redirigir a `/pv-update` primero. No se edita ningún campo sobre un estado que la propia auditoría ya marca como roto — evita que `pv-customize` escriba sobre un `pv-context.json` que `pv-update` habría cambiado de otra forma.
- Solo con `problems` vacío (o tras un `pv-update` limpio) se pasa a clasificar la petición.

### Tabla de enrutado

| Petición del usuario | Acción de `pv-customize` |
|---|---|
| Editar un paso en un hook point real **ya sembrado** en el proyecto | Editar directamente el `.md` de proyecto en `{workFolder}/stuff/hooks/{skill}/`. El `### Step` que se añada se escribe siempre en **inglés técnico**, igual que exige `pv-update` para cualquier contenido de hook (`stuff-<subdir>-hook-language`) — nunca en `interaction.language`. ⚠️ `pv-design.en.md`/`.es.md` ("Project hooks", línea ~543) dice hoy lo contrario ("`stuff/hooks/*` files follow `interaction.language`; there is no `stuff/*` language field") — desactualizado frente al comportamiento real que `pv-update`/`audit-context.py` ya audita y corrige. Antes de implementar `pv-customize`, corregir esa frase en ambos documentos para que coincida con `pv-update/SKILL.md` (inglés técnico fijo, misma categoría que `docs.tech.*`), así la fuente que `pv-customize` referencia para hooks no contradice la regla que aplica. |
| Editar un paso en un hook point real que **no está sembrado todavía** (proyecto viejo, o `scaffold-project.py` no llegó a crearlo) | Ejecutar `scaffold-project.py` para sembrar el archivo desde su `.template.md` (mismo mecanismo que usa `pv-update` para `stuff-<subdir>-hook-missing`, no una copia manual reimplementada) y editar después el `### Step` en inglés técnico, igual que la fila anterior. |
| Pedir un hook en un `<NN>` que **no corresponde a ningún hook point real** ("The ten points" de `pv-design.en.md`) | Rechazar y explicar — ver "Qué NO puede hacer nunca `pv-customize`". Remitir a `plans/07_future-hooks.md` como el sitio para proponerlo, nunca improvisarlo. |
| Cambiar idioma (interacción, changes, versions, docs funcionales) | `pv-customize` hace la pregunta él mismo (misma lógica que `pv-init` step 3, leyendo `schema.json` para los campos `interaction.language`/`changes.language`/`versions.language`/`docs.functional.language`) y escribe el campo con merge selectivo. **No invoca `pv-init` por `Skill` tool** — ninguna skill del framework invoca `pv-init` salvo el propio usuario vía `/pv-init`; si el proyecto no tiene `framework` en absoluto, se redirige a `/pv-init` como texto, no como invocación. |
| Cambiar rutas (`workFolder`, `sourcecodeDir`, `docs.tech.*`, `docs.functional.*`) | Delegar a `pv-update` si el cambio implica mover contenido existente; edición directa + aviso si es solo repuntar un path vacío. |
| Cambiar `skillModels` (modelo/effort por skill) | Editar `pv-context.json` directamente y **ejecutar `sync-skill-models.py` inmediatamente** (es determinista y gratis en tokens, mismo patrón que cualquier otro script del framework) — no dejarlo como recordatorio para que el usuario lo corra después. |
| Cambiar `framework.skills.mockups` / `framework.skills.diagrams` (swap de skill de mockups o diagramas) | Editar `pv-context.json` directamente, validando que la skill destino existe en `.claude/skills/`. |
| Petición ambigua o que no encaja en ninguna fila | Preguntar al usuario con `AskUserQuestion`, no adivinar. |
| `pv-context.json` no existe o está roto | Cubierto ya por el step 0 de arriba — redirigir a `pv-init`/`pv-update` primero, igual que ya hacen otras skills pv-*. |

**Regla de escritura, válida para cualquier fila que edite `pv-context.json`:** siempre merge selectivo — leer el archivo, modificar solo las claves pedidas, escribir de vuelta preservando todo lo demás byte a byte. Nunca reescribir el archivo completo desde cero. Mismo patrón que `pv-init` step 4 ("update with a merge, without overwriting fields already present").

## Por qué no ampliar `pv-init` o `pv-update` en su lugar

- `pv-init` está diseñado para **una pasada completa** (bootstrap), invocable solo por el usuario (`/pv-init`) — ninguna otra skill del framework lo invoca hoy, ni siquiera `pv-update` (la relación es al revés: `pv-init` delega en `pv-update` cuando encuentra algo roto). Añadirle un modo "parche puntual para una sola pregunta suelta en cualquier momento" invocable desde otra skill rompería ese patrón sin necesidad — `pv-customize` reimplementa la pregunta de idioma él mismo en vez de forzar ese cambio en `pv-init`.
- `pv-update` está diseñado para **detectar y reparar drift/roturas**, no para "quiero esta funcionalidad nueva a propósito". Mezclar intención de reparación con intención de personalización deliberada confunde ambos flujos. Dicho esto, `pv-update` **sí es ya dueño de facto del sembrado/reparación de hooks** (`stuff-<subdir>-hook-missing`, `stuff-<subdir>-hook-badslug`, `stuff-<subdir>-hook-language`) y de campos como `skillModels`/`skill-ref-missing` — `pv-customize` reutiliza ese mecanismo (`scaffold-project.py` para sembrar un hook faltante) en vez de reimplementar la copia de plantillas por su cuenta.
- Los hooks nunca han tenido un dueño que los **edite con intención** (añadir/cambiar un `### Step` a petición del usuario) — `pv-update` los siembra/repara, `pv-do`/`pv-how`/etc. los leen en tiempo de ejecución, pero ninguna skill escribe contenido nuevo en ellos. `pv-customize` les da ese punto de entrada sin tocar quien ya los consume ni duplicar la lógica de sembrado que `pv-update` ya tiene.

`pv-customize` es una capa fina de enrutado: nunca invoca `pv-init` (nadie lo hace salvo el usuario), delega en `pv-update` cuando el cambio implica reparación/sembrado, y edita directamente hooks/`pv-context.json` (siempre con merge selectivo, nunca reescritura completa) cuando el cambio es autocontenido.

## Qué necesita saber `pv-customize` para clasificar (research antes de implementar)

- Listado completo de hooks disponibles por skill (ya está: `pv-do`×2, `pv-fix`×1, `pv-how`×2, `pv-new`×1, `pv-version`×4) — sacarlo de `.claude/skills/*/hooks/*.template.md`, no hardcodearlo, para que siga funcionando si se añaden hooks nuevos a otras skills en el futuro.
- `schema.json` de `pv-init` como fuente de verdad de qué campos existen en `pv-context.json` y su descripción — reusar, no duplicar.
- Regla de idioma del contenido de hooks: inglés técnico fijo, igual que `docs.tech.*` — confirmado en `pv-update/SKILL.md` y en la lógica real de `audit-context.py` (`stuff-<subdir>-hook-language`). **No** en `pv-design.en.md`/`.es.md` ("Project hooks"), que hoy dice lo contrario y está desactualizado — corregirlo ahí (ver tabla de enrutado arriba) antes de o junto con implementar esta skill, para no construir `pv-customize` sobre la fuente equivocada.

## Formato: SKILL.md, como el resto del framework

`.claude/skills/pv-customize/SKILL.md` — es el único mecanismo por el que el harness descubre y dispara skills en este repo; no hay alternativa de formato a considerar.

Lo que sí decide si el disparo es fiable es la `description` del frontmatter, porque el enrutado a `pv-customize` ocurre **antes** de que corra ninguna lógica interna — Claude Code decide invocarla leyendo esa descripción. Tiene que:
- Nombrar explícitamente las categorías (hooks, idiomas, rutas, `skillModels`, mockups/diagramas), no quedarse en "personaliza el framework" genérico.
- Cubrir tanto intención de acción ("añade un hook que...", "cambia el modelo de...") como intención de consulta ("¿dónde configuro...?", "¿puedo cambiar...?") — el usuario también puede solo querer saber dónde mirar, no que se ejecute el cambio.

## Tabla de referencia determinista (dentro del propio SKILL.md)

En vez de fiarnos de que el modelo infiera bien el routing cada vez, `pv-customize` lleva una tabla fija "tipo de cambio → dónde vive y quién lo hace" (la de la sección "Tabla de enrutado" de este plan, ampliada). Fuentes que **no se duplican a mano** sino que se referencian, para no desincronizarse si el framework cambia:

- **Catálogo completo de hook points**: ya existe, completo y canónico, en [`pv-doc/pv-design/pv-design.en.md`](../pv-doc/pv-design/pv-design.en.md), sección **"Project hooks" → "The ten points"** (referenciar por encabezado de sección, no por número de línea — el doc cambia con el tiempo) — los diez hooks actuales (`pv-how`×2, `pv-new`×1, `pv-fix`×1, `pv-do`×2, `pv-version`×4), su convención de nombre `<NN>-<before|after>-<object>` y las variables sustituibles. `pv-customize` lee esa tabla en vez de copiarla, así que si se añade un hook nuevo en el futuro (el propio doc referencia `plans/07_future-hooks.md` para propuestas no decididas) `pv-customize` queda al día automáticamente.
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

## Cambios en documentación

`pv-customize` es una skill nueva del framework, no un cambio interno de una skill existente: además del `SKILL.md`, hay documentación de framework —con pares en/es— que la introduce o la referencia. Nada de esto se reescribe a mano en `INDEX.md` (regla ya cubierta en "Qué NO puede hacer nunca `pv-customize`"); esto es sobre los `.md` de doc del propio framework, no del proyecto usuario.

- **`pv-doc/pv-guide.en.md` / `pv-guide.es.md`** (mantener ambos en paridad, no solo el inglés):
  - Añadir `pv-customize` al árbol de skills (línea ~104, junto a `pv-init/`, con su comentario de una línea de qué hace).
  - Nueva subsección en la guía de uso (junto a "2. Initialize the framework: `/pv-init`") explicando cuándo usar `/pv-customize` en vez de `/pv-init`/`/pv-update` — el criterio ya está en el plan ("Por qué no ampliar pv-init o pv-update"), aquí se traduce a guía de usuario.
  - En ["More ways to customize Previo"](#more-ways-to-customize-previo) (secciones ~93, ~375, ~449 sobre `skillModels`, hooks, `sync-skill-models.py`): añadir una nota de que `/pv-customize` es ahora el punto de entrada conversacional para estos cambios, sin quitar la documentación de cómo editarlos a mano (sigue siendo válida, `pv-customize` no es obligatorio).
- **`pv-doc/pv-design/pv-design.en.md` / `pv-design.es.md`**:
  - La sección "The ten points" (líneas ~520-547) es la fuente canónica que `pv-customize` **lee, no duplica** (ya lo dice el plan) — no necesita cambios de contenido, pero si se documenta el árbol de skills del repo (patrón de las líneas ~569-634, un bloque `hooks/` comentado por skill) añadir `pv-customize/` a ese árbol como skill sin hooks propios (es enrutador, no dueño de ningún hook point).
  - Confirmar que la nueva skill no necesita entrada en la tabla `Skill | Hook | Runs` — no define hooks propios, solo los edita cuando ya existen.
- **`schema.json` de `pv-init`**: no requiere cambios de campos (ya lo dice el plan, `pv-customize` no añade propiedades nuevas), pero si el schema o `pv-guide` documentan alguna vez "qué skill toca cada campo" habría que sumar `pv-customize` como editor adicional de `skillModels`/`framework.skills.*` junto a `pv-init`.
- **`README.md` raíz del framework** (si existe listado de skills disponibles fuera de `pv-doc/`): verificar si hay un listado plano de comandos `/pv-*` a actualizar con `/pv-customize`.

Regla general: cualquier doc que hoy mencione "para cambiar `skillModels`/hooks/rutas, edita X a mano o corre `pv-init`/`pv-update`" gana una frase adicional "o pide a `/pv-customize` que lo haga por ti", sin eliminar la instrucción manual existente (sigue siendo el mecanismo subyacente).

## Siguiente paso

Si esto encaja, redacto el `SKILL.md` de `pv-customize` siguiendo el patrón de las demás skills pv-* (frontmatter con `model`/`effort` según el baseline mirroreado del proyecto, `metadata.uses: [pv-update]` — no `pv-init`, por la regla de arriba —, sección de flujo con referencia a un `workflow.customize.md` dado que hay bifurcación real por tipo de petición: step 0 de audit, idioma, rutas, `skillModels`, mockups/diagramas, hooks en sus tres variantes, ambigua/rechazo), incluyendo la tabla determinista, la sección de límites, y los cambios de documentación de esta actualización del plan.

## Análisis crítico (2026-09-21)

Cada afirmación factual del plan se verificó contra el repo (`audit-context.py`, `pv-update/SKILL.md`, `pv-init/SKILL.md`, `schema.json`, `scaffold-project.py`, `pv-design.en.md`/`.es.md`, `pv-guide.en.md`). La mayoría se sostiene tal cual está escrita — el número de hooks (10 puntos en 5 skills), la contradicción de idioma en `stuff/hooks/*` en `pv-design.en.md:543`/`pv-design.es.md:543`, la ubicación real de `sync-skill-models.py` (`pv-init/scripts/`, no `pv-update/`), y el patrón "`pv-init` nunca es invocado por otra skill" (`uses: [pv-update]` en el propio frontmatter de `pv-init/SKILL.md`, nunca al revés) quedan confirmados exactamente como los describe el plan.

### Bug de repo (base sobre la que se apoya el plan, sin detectarlo)

| Hallazgo | Explicación | Mejora propuesta |
|---|---|---|
| `pv-update/SKILL.md` infracuenta los hooks que su propio script audita — falta `pv-fix` en la línea 49 | El diccionario `HOOK_SETS` de `.claude/skills/pv-update/scripts/audit-context.py` (líneas 286–307) **sí** incluye `"fix": ("pv-fix", {"10": "10-before-entry.md"})`, y tanto el docstring de módulo como el de `check_version_hooks_seed` (línea 387, línea 400) ya listan `fix` correctamente — el script está bien y bien documentado en su propio fichero. El único texto desactualizado es `pv-update/SKILL.md` línea 49, que enumera `<subdir> = version \| do \| how \| new` sin `fix` y no incluye la entrada `fix: 10-before-entry.md (owned by pv-fix)` en la lista por-skill de esa misma línea. `pv-update/SKILL.md` es el fichero que el plan cita dos veces (§"Tabla de enrutado" fila 2, §"Qué necesita saber pv-customize") como fuente de verdad confirmada — si quien implemente `pv-customize` se fía de esa línea 49 en vez de mirar el `HOOK_SETS` real, concluirá erróneamente que el hook de `pv-fix` no está cubierto por el mecanismo de `pv-update` y podría reimplementar ese camino — justo la duplicación que el plan dice evitar (§"Por qué no ampliar pv-init o pv-update"). | Añadir `\| fix` a la enumeración de `<subdir>` y `fix: 10-before-entry.md (owned by pv-fix)` a la lista por-skill, ambos en `pv-update/SKILL.md:49`. Cambio de una línea, sin tocar código — el script ya es correcto. |

### Huecos

| Hallazgo | Explicación | Mejora propuesta |
|---|---|---|
| Fila "Cambiar rutas" infraespecificada frente al resto de la tabla | Cada otra fila indica un mecanismo concreto (script, fichero, regla merge-only). La fila de rutas solo dice "Delegar a `pv-update` si implica mover contenido existente; edición directa + aviso si es repuntar un path vacío" — pero `pv-update/SKILL.md` (línea 84) muestra que su arreglo para un docs dir ausente es "buscar dónde se movió el contenido", es decir, espera un problema *preexistente* (drift), no una petición deliberada de reubicación sin drift. El plan nunca resuelve quién ejecuta el movimiento cuando el usuario pide mover `docs.tech.architectureDocDir` en un proyecto sano — no es caso de drift (el audit no reportaría nada) ni "repuntar path vacío" (hay contenido real que trasladar). | — |
| Sin mención de `framework._comments` al cambiar idioma vía `pv-customize` | `pv-init` (paso 3 — `SKILL.md` línea 88) escribe una entrada explicativa en `framework._comments` por cada campo de idioma fijado, y `schema.json` (líneas 91-95) documenta `_comments` como metadata mantenida junto con `language`. La fila de idioma del plan nunca dice si `pv-customize` también actualiza `_comments` como hace `pv-init`, pese a posicionarse como reimplementación de esa misma lógica — omitirlo en silencio crearía una inconsistencia entre `/pv-init` y `/pv-customize`. | — |
| `docs.tech.*` englobado en la fila genérica "Cambiar rutas" sin cubrir que son campos requeridos | `schema.json` (línea 197) ya refleja correctamente en el plan que `docs.tech.*` no tiene opción de idioma. Pero la fila de rutas trata `docs.tech.*` igual que `workFolder`/`sourcecodeDir` para mover-vs-repuntar, sin abordar que `architectureDocDir`/`styleBibleDocDir` son **requeridos** (`schema.json` líneas 163, 188). Una petición de vaciar/desconfigurar uno de los tres docs dirs no está cubierta ni por la tabla ni por "Qué NO puede hacer nunca" — el propio arreglo de `pv-update` para `docs-dir-unconfigured:*` (SKILL.md línea 85) es reintroducir el campo con el default, nunca eliminarlo. El plan debería rechazar esa petición explícitamente, igual que ya rechaza hook points fuera de catálogo. | — |
| Sin caso de borde para idioma de hook fuera de bloques `### Step` | El check `HOOK_STEP_RE`/`stuff-<subdir>-hook-language` de `audit-context.py` (líneas 311, 374-381) solo se dispara si existe un bloque `### Step`. Un fichero de hook editado por `pv-customize` con prosa *fuera* de un `### Step` (p. ej. un comentario de cabecera) nunca sería detectado por el audit de idioma posterior. Menor, pero relevante dado el peso que el plan pone en "siempre inglés, misma exigencia que `pv-update`". | — |

### Lo que ya se sostiene (sin hallazgo, listado para no volver a revisarlo)

- Número/catálogo de hooks (10 puntos, 5 skills) y la convención de nombrado — verificado contra `pv-design.en.md` líneas 518–545 y el `HOOK_SETS` de `audit-context.py`.
- Contradicción de idioma en la línea ~543 de `pv-design.en.md`/`.es.md` — verificada textualmente en ambos ficheros, coincide exactamente con la cita del plan.
- Ruta de `sync-skill-models.py` y el patrón "ejecútalo de inmediato, es gratis" — coincide con `pv-init/SKILL.md` línea 117 y la descripción de `skillModels` en `schema.json`.
- "`pv-init` solo lo invoca el usuario, nunca otra skill" — confirmado: ninguna otra `SKILL.md` `pv-*` que nombra `pv-update` en `uses:` nombra jamás `pv-init`; el propio `pv-init/SKILL.md` declara `uses: [pv-update]`, confirmando la relación unidireccional en la que se apoya el plan.
- `additionalProperties: false` de `schema.json` en cada nivel, citado como la razón por la que `pv-customize` nunca puede añadir campos nuevos — confirmado en las líneas 8, 17, 37, 99, 125, 139, 168, 187, 210.
