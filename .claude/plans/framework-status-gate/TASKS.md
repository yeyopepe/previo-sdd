# TASKS: Framework status gate

Ver [`PLAN.md`](./PLAN.md) para el análisis completo. Orden sugerido: piezas base
(scripts, diagramas) antes de instrumentar las skills que los consumen.

## 1. Script de verificación (`pv-update`)

- [ ] **`pv-update/scripts/check-framework-status.py`** (nuevo) — implementa el contrato
      de la sección 1 del plan: sin argumentos, imprime un único JSON (`ok`, `problem`,
      `message`, `expected?`, `actual?`) por stdout, comprobaciones en orden
      (`context-missing` → `context-invalid-json` → `version-mismatch` → `blocked` →
      `skill-count-mismatch`), parando en la primera que falle. Reutiliza (duplicándola,
      mismo patrón que `mark-verified.py`) la lógica de lectura de frontmatter
      `read_skill_version()` ya existente en `audit-context.py`/`mark-verified.py`.
      Declara `EXPECTED_SKILL_COUNT = 22` como constante propia (sección 3 del plan).

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
      flag de escape). Sin `--version`, delega en "latest" tal cual ya soportan
      `install.sh`/`.ps1` (nunca instala una pre-release por defecto).
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

## 5. Migración de las 7 skills públicas

Para cada una de las siguientes, reemplazar el párrafo "Additionally, before continuing,
check that the framework's installed version is verified: read `metadata.version`..."
por el texto de la sección 2 del plan (comprobar existencia de
`check-framework-status.py`, ejecutarlo, leer `ok`/`message`, parar si `ok` es `false`):

- [ ] **`pv-do/SKILL.md`** (paso "0. Load the project context")
- [ ] **`pv-fix/SKILL.md`** (paso "0. Check that the framework is initialized")
- [ ] **`pv-how/SKILL.md`** (paso "0. Load the project context")
- [ ] **`pv-new/SKILL.md`** (paso "0. Check that the framework is initialized")
- [ ] **`pv-status/SKILL.md`** (paso "0. Load the project context")
- [ ] **`pv-todo/SKILL.md`** (paso "0. Check that the framework is initialized")
- [ ] **`pv-version/SKILL.md`** (paso "0. Framework initialized")

## 6. Documentación del framework

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
- [ ] Ejecutar `/pv-update` (modo audit) tras una instalación exitosa y confirmar que
      `mark-verified.py --clear` dejó `frameworkStatus` consistente con la nueva versión.
