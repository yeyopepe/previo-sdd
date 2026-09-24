# TASKS: Framework status gate

Ver [`PLAN.md`](./PLAN.md) para el análisis completo. Orden sugerido: piezas base
(scripts, diagramas) antes de instrumentar las skills que los consumen.

## 1. Script de verificación (`pv-update`)

- [ ] **`pv-update/scripts/check-framework-status.py`** (nuevo) — implementa el contrato
      de la sección 1 del plan: sin argumentos, imprime un único JSON (`ok`, `problem`,
      `message`, `expected?`, `actual?`) por stdout, comprobaciones en orden
      (`context-missing` → `context-invalid-json` → `blocked` → `version-mismatch` →
      `skill-count-mismatch`), parando en la primera que falle (`blocked` va antes que
      `version-mismatch` porque un `blocked=true` siempre implica también un mismatch de
      versión — comprobarlo después nunca se alcanzaría). Reutiliza (duplicándola, mismo
      patrón que `mark-verified.py`) la lógica de lectura de frontmatter
      `read_skill_version()` ya existente en `audit-context.py`/`mark-verified.py`.
      Declara `EXPECTED_SKILL_COUNT` como constante propia (sección 3 del plan; valor
      actual de referencia: 23 carpetas `pv-*` en este repo).

## 2. Conteo exacto de skills

- [ ] **`tools/set-skill-versions.py`** — ampliar para que, tras reescribir
      `metadata.version` en cada `pv-*/SKILL.md`, recalcule
      `len(glob("pv-*/SKILL.md"))` sobre el repo y reescriba
      `EXPECTED_SKILL_COUNT` en `pv-update/scripts/check-framework-status.py` para que
      coincida. Imprimir el nuevo valor junto al resto del resumen del script.

## 3. Capacidad de instalación (`pv-update`)

- [ ] **`pv-update/scripts/install-framework.py`** (nuevo) — wrapper de plataforma que
      invoca `install.sh`/`install.ps1` (raíz del repo) con el tag resuelto. Detecta el
      SO (`platform.system()`) y elige el script de esa plataforma, nunca por binarios
      disponibles en `PATH`. Antes de instalar, consulta la API de GitHub Releases
      (`GET /repos/{REPO}/releases/latest` y `GET /repos/{REPO}/releases?per_page=1`,
      con `REPO = "yeyopepe/previo-sdd"` como constante propia — tercera copia
      hardcodeada, mismo patrón que `install.sh`/`.ps1`) para imprimir siempre la última
      versión oficial y, si existe una pre-release más reciente que esa (`tag_name`
      distinto y `prerelease: true`), avisar de ella sin recomendarla. Implementa el
      rechazo duro de downgrade descrito en la sección 4 del plan (compara `--version`
      contra la versión real instalada vía `read_skill_version()`/`parse_version()`; sin
      flag de escape). Si `parse_version(tag)` devuelve `None` (el tag no tiene forma
      `X.Y.Z[sufijo]`), mismo rechazo duro que el downgrade — nunca delega la
      comparación al script de plataforma. Sin `--version`, delega en "latest" tal cual
      ya soportan `install.sh`/`.ps1` (nunca instala una pre-release por defecto).
- [ ] **`pv-update/workflow.install.md`** (nuevo) — diagrama fuente de verdad del modo
      `install`, mismo formato (`[Text]`/`[INFO: ...]`/`[ASK: ...]`/`{decisión}`) que
      `workflow.audit.md`: resolver versión objetivo → comparar con la instalada → si es
      inferior, informar y terminar → si no, invocar `install-framework.py` → informar
      resultado y recordar `/pv-update` (modo audit).

## 4. `pv-update/SKILL.md`

- [ ] Añadir una nueva sección (después del flujo de auditoría existente) documentando el
      modo `install`: cuándo se dispara (ver tabla de prompts, sección 5 del plan),
      remite a `workflow.install.md` como fuente de verdad del flujo (mismo patrón que ya
      usa la sección de auditoría con `workflow.audit.md`), y detalla qué texto mostrar
      en el caso de rechazo por downgrade y en el de éxito (recordatorio de ejecutar
      `/pv-update` después).
- [ ] Actualizar la `description` del frontmatter para mencionar también el modo
      `install` (instalar/actualizar el framework a una versión igual o superior), no
      solo auditoría/reparación.

## 5. Migración de las 9 skills públicas

Para cada una de las siguientes, reemplazar su párrafo actual de comprobación de versión
(la forma larga "Additionally, before continuing, check that the framework's installed
version is verified: read `metadata.version`..." en las 7 primeras, o la forma corta
"Check the framework version the same way every other `pv-*` skill does..." en las dos
últimas) por el texto de la sección 2 del plan (comprobar existencia de
`check-framework-status.py`, ejecutarlo, leer `ok`/`message`, parar si `ok` es `false`):

- [ ] **`pv-do/SKILL.md`** (paso "0. Load the project context")
- [ ] **`pv-fix/SKILL.md`** (paso "0. Check that the framework is initialized")
- [ ] **`pv-how/SKILL.md`** (paso "0. Load the project context")
- [ ] **`pv-new/SKILL.md`** (paso "0. Check that the framework is initialized")
- [ ] **`pv-status/SKILL.md`** (paso "0. Load the project context") — sin `workflow.*.md`
      propio; el cambio va solo en la prosa.
- [ ] **`pv-todo/SKILL.md`** (paso "0. Check that the framework is initialized") — sin
      `workflow.*.md` propio; el cambio va solo en la prosa.
- [ ] **`pv-version/SKILL.md`** (paso "0. Framework initialized")
- [ ] **`pv-review-architecture/SKILL.md`** (línea 30, antes de "Resolve the source folder to review")
- [ ] **`pv-review-doc-tech/SKILL.md`** (línea 50, antes de "## 1. Enumerate the folders to review") —
      sin `workflow.*.md` propio; el cambio va solo en la prosa.

No basta con tocar el `SKILL.md` de las skills que además tienen `workflow.*.md`: la
convención del framework (`pv-design.en.md`, "Relationship with the SKILL.md") dice que
el diagrama manda sobre la secuencia y la prosa se corrige para igualarlo — nunca al
revés. Cinco de las nueve ya representan este chequeo como nodo (`S0Check[Check framework
initialized and version verified]` → `S0Ok{Initialized, verified, not blocked?}`):

- [ ] **`pv-do/workflow.do.md`** (líneas 5-6) — el texto del nodo no cambia (sigue
      cubriendo "inicializado, versión verificada, no bloqueado"), solo revisar que sigue
      siendo fiel a la nueva secuencia interna (script ausente → mismo `S0Ok` "No"
      genérico, sin desglosar sub-casos en el diagrama — el detalle de cada mensaje vive
      en el `SKILL.md`).
- [ ] **`pv-fix/workflow.fix.md`** (mismo par de nodos, misma revisión).
- [ ] **`pv-how/workflow.how.md`** (mismo par de nodos, misma revisión).
- [ ] **`pv-new/workflow.new.md`** (mismo par de nodos, misma revisión).
- [ ] **`pv-review-architecture/workflow.review-architecture.md`** (mismo par de nodos,
      misma revisión).

**`pv-version` es un caso aparte**: su `workflow.version.md` **no tiene, hoy, ningún nodo**
de chequeo de versión (el flujo empieza directo en `S02Intent`), pese a que su `SKILL.md`
(línea 33) sí tiene la prosa completa — un desajuste preexistente, anterior a este plan,
que incumple la regla de que el diagrama es la fuente de verdad de la secuencia.

- [ ] **`pv-version/workflow.version.md`** — añadir el par de nodos `S0Check`/`S0Ok`
      (mismo patrón que las otras 5) antes de `S02Intent`, corrigiendo de paso el
      desajuste preexistente en vez de heredarlo.

## 6. Documentación del framework

- [ ] **`.claude/pv-doc/pv-design/pv-design.en.md`** y **`pv-design.es.md`** —
      `pv-update` es hoy la única skill pública **sin entrada propia** en este documento
      (a diferencia de `pv-todo`, `pv-version`, etc., que sí la tienen con el formato
      `- **nombre** — resumen. *Uses:* ...` seguido de su bloque "Assets and scripts").
      Crear esa entrada completa desde cero, en orden alfabético entre `pv-todo` y
      `pv-version` (línea ~141/~147 en la versión inglesa actual): resumen de qué hace
      `pv-update` (audita/repara `pv-context.json`, más el nuevo modo `install`), su
      `*Uses:*`, y el bloque "Assets and scripts" listando los cinco assets que tendrá
      tras este plan: `workflow.audit.md`, `scripts/audit-context.py`,
      `scripts/mark-verified.py` (los tres ya existentes, sin documentar hasta ahora) más
      `scripts/check-framework-status.py`, `scripts/install-framework.py` y
      `workflow.install.md` (los tres nuevos de este plan) — mismo nivel de detalle por
      asset que el resto de skills documentadas. Añadir también `workflow.install.md`
      junto a `workflow.audit.md` donde el doc ya explica la convención `workflow.*.md`
      (su sección "Reading rule", ~línea 527 en la versión inglesa).
- [ ] Revisar `pv-doc/pv-design-onescript/` (u otro doc de diseño interno del framework
      que describa el paso 0 compartido de las skills, si existe) por si documenta el
      patrón anterior (comparación manual de versión) y necesita actualizarse para
      reflejar el nuevo script único.
- [ ] Revisar si `.claude/pv-doc/pv-guide.en.md` / `pv-guide.es.md` mencionan cómo
      `pv-update` opera hoy (solo auditoría) y actualizar para incluir el nuevo modo
      `install`.

## 7. Verificación manual

- [ ] En un proyecto de prueba con el framework instalado: borrar/renombrar
      `check-framework-status.py` y confirmar que `pv-do` (o cualquiera de las 7)
      informa del mensaje de "framework no parece bien instalado" y no continúa.
- [ ] Restaurar el script, forzar `frameworkStatus.blocked = true` a mano en
      `pv-context.json` y confirmar que las 7 skills paran con el mensaje correcto.
- [ ] Borrar una carpeta `pv-*` cualquiera (simulando instalación incompleta) y
      confirmar que `check-framework-status.py` reporta `skill-count-mismatch` y que las
      7 skills paran citando ese motivo.
- [ ] Ejecutar `/pv-update install` sin argumentos en un proyecto con una versión antigua
      instalada y confirmar que actualiza a la última release real (verificar contra
      GitHub Releases).
- [ ] Ejecutar `/pv-update install <tag inferior a la instalada>` y confirmar el rechazo
      duro, sin cambios en disco.
- [ ] Ejecutar `/pv-update install <tag no parseable, p. ej. "main" o "v1">` y confirmar
      el mismo rechazo duro (no delega en `install.sh`/`.ps1`), sin cambios en disco.
- [ ] Ejecutar `/pv-update` (modo audit) tras una instalación exitosa y confirmar que
      `mark-verified.py --clear` dejó `frameworkStatus` consistente con la nueva versión.
