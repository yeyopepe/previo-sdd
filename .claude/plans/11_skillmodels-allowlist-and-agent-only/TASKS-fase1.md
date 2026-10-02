# Tareas — Fase 1: lista cerrada de skillModels + pv-internal-tech-risks y pv-internal-tech-analysis como agente

Ver [PLAN.md](PLAN.md) para el análisis y las decisiones de diseño. Esta es
la fase 1 de la implementación por fases de la Parte B (ver índice de
PLAN.md) — cubre la Parte A completa (aplica a las 22 skills) y, de la
Parte B, solo `pv-internal-tech-risks` y `pv-internal-tech-analysis`. Las
demás candidatas (incluida `pv-internal-tech-security`) quedan para fases
futuras, aún sin `TASKS-*.md` propio.

## Parte A — Rediseño de skillModels

- [ ] Crear `.claude/skills/pv-init/assets/allowed-skill-models.json` como
      mapa de nombre de skill → `model`/`effort` de arranque, con las 11
      user-invocable + las 15 `pv-internal-*` (incluida
      `pv-internal-mockups-html` aunque no vaya a ser agent-only — sigue
      participando en `skillModels`). Todas con `{ "model": null, "effort": null }`
      excepto:
      - `pv-internal-tech-risks`: `{ "model": "claude-haiku-4-5", "effort": "medium" }`
        (decidido en este plan como su default de arranque razonado).
      - `pv-internal-tech-security`: `{ "model": "claude-sonnet-5", "effort": "low" }`
        (decidido en este plan como su default de arranque razonado — ver
        PLAN.md, tabla de candidatas; su conversión a agent-only queda para
        una fase futura, pero su entrada en `skillModels` se fija ya en
        esta fase, como el resto del mapa completo).
- [ ] Editar `.claude/skills/pv-init/schema.json`: quitar `default` y
      `overrides` de la definición de `skillModels`, dejarlo como
      `additionalProperties: { "$ref": "#/$defs/modelConfig" }` (mapa plano).
      En `$defs.modelConfig`, permitir `null` en `model`/`effort` además de
      `string` (siguen siendo claves requeridas, pero su valor admite
      `null`). Mantener `_instructions`. Actualizar la `description` de
      `skillModels` (obligatoria una entrada por skill de la lista cerrada,
      aunque sea `null`/`null`; ninguna fuera de esa lista).
- [ ] Reescribir `.claude/skills/pv-init/scripts/collect-skill-models.py`:
      leer `allowed-skill-models.json`, para cada skill de la lista buscar
      su `model`/`effort` real en su `SKILL.md` (o el default de arranque
      del asset — `null`/`null` salvo excepción — si no lo tiene explícito),
      devolver mapa plano completo. Quitar la lógica de cálculo de `default`
      por frecuencia.
- [ ] Reescribir `.claude/skills/pv-init/scripts/sync-skill-models.py`:
      mantener sin cambios el comportamiento si `.claude/pv-context.json` no
      existe en absoluto (avisa por stdout, no hace nada más — no lo crea).
      Iterar sobre el asset `allowed-skill-models.json` (no sobre
      `glob("pv-*/SKILL.md")`). Para cada skill:
      - Si falta en `pv-context.json#skillModels`: avisar por stdout y
        **añadirla él mismo** con `{ "model": null, "effort": null }`
        (reescribe `pv-context.json`; no delega solo en `pv-update`).
      - Si su entrada tiene `model`/`effort` a `null`: **vaciar esas claves
        en el frontmatter** del `SKILL.md` si las tenía (borrarlas), no
        dejarlas como estaban.
      - Si tiene valores no vacíos: propagar al frontmatter como hoy.
- [ ] Editar `.claude/skills/pv-init/SKILL.md`: actualizar el paso de
      scaffolding para escribir `skillModels` como mapa plano completo,
      usando el `model`/`effort` de arranque de cada skill tal como venga en
      `allowed-skill-models.json` (`null`/`null` salvo
      `pv-internal-tech-risks` y `pv-internal-tech-security`) en vez de
      mirror vía `collect-skill-models.py`.
- [ ] Editar `.claude/skills/pv-update/scripts/audit-context.py`:
      - Referenciar el asset `allowed-skill-models.json` cruzando la carpeta
        de `pv-init` (ruta relativa desde `pv-update/scripts/`).
      - Añadir detección `skillmodel-not-allowed:<name>` (entrada en
        `skillModels` fuera de la lista permitida).
      - Añadir detección `skillmodel-missing:<name>` (falta entrada para una
        skill permitida).
      - Quitar/ajustar cualquier lógica existente que asuma `default`/
        `overrides` (revisar línea ~1040-1063 y `KNOWN_TOP_LEVEL`).
- [ ] Editar `.claude/skills/pv-update/SKILL.md`: documentar las dos nuevas
      categorías de problema y su regla de reparación (elimina `not-allowed`
      avisando; añade `missing` con `{ "model": null, "effort": null }`),
      junto a la entrada existente de `skillmodel-drift`.
- [ ] Regenerar `.claude/pv-context.json` de este mismo repo (dogfooding) al
      nuevo formato plano y completo de `skillModels`, corriendo el
      `collect-skill-models.py` reescrito y confirmando que
      `sync-skill-models.py` no reporta drift tras la migración.
- [ ] Editar `.claude/pv-doc/pv-guide.en.md` (sección "3. Model/effort per
      skill: skillModels", ~línea 388-409): reflejar el mapa plano sin
      `default`/`overrides`, mencionar el asset de permitidas y que la lista
      es cerrada (no se pueden añadir skills arbitrarias).
- [ ] Editar `.claude/pv-doc/pv-guide.es.md` (mismo apartado, ~línea
      388-409): traducción gemela del cambio anterior.
- [ ] Editar `.claude/pv-doc/pv-design/pv-design.en.md` (~líneas 356-409,
      sección `### skillModels`, más línea 88 sobre `sync-skill-models.py`)
      con el nivel de detalle que exige PLAN.md § A.8 — no solo cambiar el
      ejemplo de JSON a mapa plano, sino documentar explícitamente:
      - `allowed-skill-models.json` como única fuente de verdad y qué tres
        scripts la leen (`collect-skill-models.py`, `sync-skill-models.py`,
        `audit-context.py`), con la misma precisión que ya usa la línea 88
        para `sync-skill-models.py`.
      - El ciclo de vida completo de una entrada de `skillModels`: creada
        por `pv-init` (scaffolding, sonnet/medium fijo), corregida por
        `pv-update` (criterio de qué añade/quita), propagada al frontmatter
        por `sync-skill-models.py`.
      - Que "estar en `skillModels`" y "ser agente-only" son ejes
        independientes — toda skill de la lista cerrada tiene entrada de
        modelo/effort se invoque como se invoque; `invocation: agent-only`
        decide solo cómo la invoca su caller. Nota: en esta fase 1,
        `pv-internal-tech-security` es el ejemplo vivo de esa independencia
        — tiene entrada en `skillModels` (con su default ya fijado) pero
        aún no es agent-only.
      - El nuevo campo de frontmatter `invocation: agent-only`, documentado
        junto a `model`/`effort` como otro campo con significado especial.
      - **Su relación explícita con `user-invocable`** (ya documentado en la
        sección "User-invocable" vs "Internal and support"): son dos campos
        independientes que coexisten en el frontmatter de la misma skill —
        `user-invocable: false` no se toca ni se fusiona; `invocation:
        agent-only` contesta una pregunta distinta ("con qué tool la invoca
        su caller"), no "quién puede invocarla".
      - Barrido final de todo el documento buscando cualquier mención
        residual a `default`/`overrides` (prosa, índice, otros ejemplos de
        JSON) que quede desalineada tras el cambio.
- [ ] Editar `.claude/pv-doc/pv-design/pv-design.es.md`: traducción gemela
      del ítem anterior, con el mismo nivel de detalle (fuente de verdad,
      ciclo de vida, independencia skillModels/agent-only, relación con
      `user-invocable`, campo `invocation`, barrido de residuos
      `default`/`overrides`).

## Parte B (fase 1) — pv-internal-tech-risks y pv-internal-tech-analysis como agente

### pv-internal-tech-analysis: contrato pending_questions (base de todo lo demás)

- [ ] Editar `.claude/skills/pv-internal-tech-analysis/SKILL.md`:
      - Paso 3, subsección "Doubts neither documentation nor code resolve"
        (línea 74): reemplazar "confirms it with the user before
        considering the context gathered" por el contrato nuevo — la skill
        nunca pregunta directamente; formula la solución que le parece más
        razonable, la marca como asumida (no confirmada), y la añade al
        resultado (ver PLAN.md § B.0).
      - Paso 6 (línea 90): añadir **`pending_questions`** a la lista de lo
        que se devuelve al caller — lista (vacía si no hay dudas) de
        objetos `{doubt, assumed_answer}`.
      - Añadir `invocation: agent-only` al frontmatter, **sin tocar**
        `user-invocable: false` (campos independientes — ver PLAN.md,
        Decisión de diseño 6).
      - Añadir nota en el cuerpo (junto a "Only invoked by other `pv-*`
        framework skills — not meant for direct invocation by the user")
        explicando que se invoca como agente foreground desde sus tres
        callers, nunca inline vía `Skill()`, y por qué.
      - Subir patch de `metadata.version`.

### pv-internal-tech-risks (piloto original, sin cambios de diseño)

- [ ] Editar `.claude/skills/pv-internal-tech-risks/SKILL.md`:
      - Añadir `invocation: agent-only` al frontmatter, **sin tocar** la
        clave `user-invocable: false` ya presente (son campos
        independientes — ver PLAN.md, Decisión de diseño 6).
      - Añadir nota en el cuerpo (junto a "Not meant for direct invocation
        by the user") explicando que se invoca como agente foreground desde
        `pv-how`, nunca vía `Skill()` inline, y por qué (para que su
        `model`/`effort` sincronizado desde `skillModels` tenga efecto
        real).
      - Subir patch de `metadata.version`.
- [ ] Editar `.claude/skills/pv-how/SKILL.md`, paso 3.1 (~línea 145):
      cambiar la invocación de `Skill()` a `Agent(run_in_background: false)`,
      con un prompt autocontenido (contenido de `plan.md` y `description.md`
      ya leído, pasado explícitamente — el agente no hereda contexto de
      conversación). Mantener sin cambios la escritura en `.metadata.json`
      (línea ~147-153), el check de la línea 155, y el reúso de resultado de
      la línea 157.
      - Añadir manejo de fallo del agente: si falla, hace timeout, o
        devuelve un resultado no parseable (9 factores + mediana), avisar
        siempre al usuario de qué pasó y relanzar el agente con el mismo
        prompt — nunca saltar el paso ni escribir un valor placeholder en
        `.metadata.json`. Sin límite de reintentos definido.
      - Subir patch de `metadata.version`.
- [x] Verificado `.claude/skills/pv-how/workflow.how.md` (línea 59, nodo
      `S31Risk`): agnóstico a `Skill` vs `Agent` ("Invoke
      pv-internal-tech-risks on plan.md/description.md"). No requiere
      cambio.

### Los tres callers de pv-internal-tech-analysis

- [ ] Editar `.claude/skills/pv-new/SKILL.md` (línea 31, "Source of truth"):
      cambiar la invocación de `Skill()` a `Agent(run_in_background: false)`,
      con prompt autocontenido (resumen de lo analizado explícito). Añadir
      manejo de `pending_questions` (usar `AskUserQuestion` con cada
      `{doubt, assumed_answer}` antes de continuar, usar la respuesta real
      al escribir `description.md`, sin reinvocar el agente salvo caso
      raro — ver PLAN.md § B.0/B.6). Añadir manejo de fallo del agente
      (avisar y relanzar, mismo criterio que pv-how/B.3). Subir patch de
      `metadata.version`.
- [ ] Editar `.claude/skills/pv-fix/SKILL.md` (línea 36 "Source of truth" y
      línea 60, paso 2 "Assess whether the change is `fast`" — es la misma
      invocación, el cambio real va en el punto de invocación del paso 2):
      mismo cambio de mecanismo, manejo de `pending_questions` (usar la
      respuesta real al decidir si el fix es `fast` o al escribir
      `description.md`, según corresponda) y manejo de fallo del agente que
      en `pv-new`. Subir patch de `metadata.version`.
- [ ] Editar `.claude/skills/pv-how/SKILL.md` (línea 135, paso 3, punto 5):
      mismo cambio de mecanismo, manejo de `pending_questions` (usar la
      respuesta real al escribir `plan.md`) y manejo de fallo del agente que
      en `pv-new`/`pv-fix`. Ya se está editando este mismo fichero para el
      paso 3.1 de `pv-internal-tech-risks` — un solo patch de
      `metadata.version` cubre ambos cambios.
- [ ] Revisar `.claude/skills/pv-new/workflow.new.md`: el nodo que
      representa la invocación a `pv-internal-tech-analysis` — actualizar
      solo si detalla explícitamente el tool; si es agnóstico, sin cambios.
- [ ] Revisar `.claude/skills/pv-fix/workflow.fix.md`: mismo criterio, nodo
      equivalente.
- [ ] Revisar `.claude/skills/pv-how/workflow.how.md`: nodo del paso 3,
      punto 5 (distinto del `S31Risk` ya verificado) — mismo criterio.

### Verificación de la fase 1

- [ ] Ejercitar `pv-how` de punta a punta sobre una entrada real de
      `{changesDir}/inProgress` (o una de prueba) para confirmar:
      - El paso 3.1 lanza el agente `pv-internal-tech-risks` en foreground,
        no `Skill()`.
      - El resultado (9 factores + mediana) vuelve al turno de `pv-how` y se
        escribe en `.metadata.json` vía `set-metadata.py`.
      - El reúso de resultado en la misma conversación (línea 157) sigue
        funcionando sin relanzar el agente.
- [ ] Ejercitar `pv-new`, `pv-fix` y `pv-how` de punta a punta (una entrada
      real o de prueba cada uno) para confirmar:
      - Cada uno lanza `pv-internal-tech-analysis` en foreground, no
        `Skill()`.
      - Un caso con `pending_questions` no vacío dispara `AskUserQuestion`
        correctamente y la respuesta real (no la asumida) queda reflejada
        en el documento escrito.
      - Un caso sin dudas pendientes no muestra ninguna pregunta de más.
- [ ] Provocar un fallo simulado del agente (timeout o resultado no
      parseable) en al menos uno de los cuatro puntos de invocación
      (`pv-how`→risks, o cualquiera de los tres callers→analysis) y
      confirmar que el caller avisa al usuario y relanza, sin continuar con
      un valor placeholder.
- [ ] Correr `pv-update` sobre el repo y confirmar que no reporta
      `skillmodel-drift` ni `skillmodel-not-allowed`/`skillmodel-missing`
      para `pv-internal-tech-risks` ni `pv-internal-tech-analysis` tras el
      cambio.

## Verificación final (Parte A completa + Parte B fase 1)

- [ ] Simular en `pv-context.json` una skill inventada dentro de
      `skillModels` y confirmar que `pv-update` la elimina avisando al
      usuario.
- [ ] Simular en `pv-context.json` la ausencia de una skill permitida dentro
      de `skillModels` y confirmar que tanto `sync-skill-models.py` como
      `pv-update` la añaden con `{ "model": null, "effort": null }` (salvo
      que el asset traiga un default de arranque distinto para esa skill).
- [ ] Correr `pv-init` desde cero (proyecto de prueba) y confirmar que
      `skillModels` sale completo, con todas las skills del asset en
      `null`/`null` excepto `pv-internal-tech-risks`
      (`claude-haiku-4-5`/`medium`) y `pv-internal-tech-security`
      (`claude-sonnet-5`/`low`).
- [ ] Simular en `pv-context.json` una entrada con `model`/`effort` a `null`
      para una skill que hoy tiene `model:`/`effort:` en su frontmatter, y
      confirmar que `sync-skill-models.py` se los borra del `SKILL.md`.
- [ ] Correr `sync-skill-models.py` y confirmar que el frontmatter de todas
      las skills de la lista (incluidas `pv-internal-tech-risks` y
      `pv-internal-tech-analysis`) queda en sync con `pv-context.json`.
