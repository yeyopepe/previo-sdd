# `agents-status-tracking.md`: seguimiento de agentes en marcha sobre changes de Previo

## Context

Hoy no hay forma de saber, sin preguntar directamente en el chat de cada sesión, qué
agentes Claude Code están activos sobre este repo, sobre qué **change de Previo**
(`changes/{state}/{xxxx}/`) está trabajando cada uno, y en qué fase concreta de su
trabajo se encuentra (analizando, implementando, esperando algo...).

**Objetivo:** poder consultar en cualquier momento — desde `pv.py` y desde el chat — un
listado de agentes activos con: identificador de sesión, change de Previo sobre el que
trabaja (si alguno), fase actual tipificada, y desde cuándo está en esa fase. Una entrada
sin refrescar más allá de un timeout configurable se muestra como "caída / sin
respuesta" en vez de mentir indefinidamente.

## Descartado antes de llegar a este diseño

Dos enfoques se evaluaron y se descartaron, por razones que conviene dejar escritas para
no reabrirlas sin motivo nuevo:

1. **Un script periódico que pregunta activamente a cada agente.** `ListAgents` /
   `SendMessage` no son una API de sistema ni una librería invocable desde un script
   Python — solo existen dentro de una sesión de Claude Code. Un "script periódico" que
   preguntara tendría que ser en realidad otra sesión de Claude Code relanzada a
   intervalos (`claude -p "..."`), con el coste de latencia (segundos) y consumo de
   cuota que eso implica en cada tick. Además no elimina la fragilidad de fondo: sigue
   dependiendo de que un LLM interprete la pregunta y responda con precisión sobre su
   propio estado, solo que trasladada de "escribir proactivamente" a "responder cuando
   preguntan".
2. **Heartbeat continuo** (reporte cada pocos segundos mientras dura una fase). Permitiría
   timeouts de detección muy cortos (segundos), pero exige un mecanismo de fondo
   escribiendo sin parar durante toda la sesión — no hay nada en Claude Code que ofrezca
   eso hoy sin construir un proceso aparte.

**Enfoque elegido: reporte reactivo por transición de fase.** Cada skill `pv-*` escribe
una entrada cuando el agente entra en una fase nueva (no hay heartbeat, no hay "fin"
explícito por fase — la fase vigente es la última escrita). Es el único enfoque que no
depende de una sesión de Claude Code extra corriendo en bucle, al coste de que un agente
que se salte el marcado de una fase se queda "congelado" en la anterior hasta que expire
por timeout. Esa pérdida de precisión se acepta y se absorbe con el timeout, no se
intenta eliminar.

## Diseño propuesto

### 1. Registro único centralizado

Un solo fichero, `{workFolder}/.agents-status.json`, con una entrada por sesión activa:

```json
{
  "sessions": {
    "e3882b": {
      "sessionName": "previo-sdd-b5",
      "changeCode": "0042",
      "phase": "implementing",
      "updatedAt": "2026-09-19T14:32:10Z",
      "notes": null,
      "refHash": "a1b2c3d..."
    },
    "506b39": {
      "sessionName": "bgfactory-2a",
      "changeCode": null,
      "phase": "analyzing",
      "updatedAt": "2026-09-19T14:31:02Z",
      "notes": "Bloqueado por un test flaky en CI, reintentando"
    }
  }
}
```

Campos por entrada:

- `sessionName` (informativo): el nombre que `ListAgents` ya usa para esa sesión, para
  poder cruzar ambas fuentes visualmente sin que sea la clave primaria (la clave es el
  id corto de sesión, más estable).
- `changeCode`: el `xxxx` del change sobre el que trabaja, o `null` si el agente no está
  en ese momento sobre ningún change concreto (p. ej. dentro de `pv-todo` o de una
  conversación libre). **No se guarda el estado de carpeta (`changeState`)** — sería un
  dato derivado duplicado que puede desincronizarse del disco real (p. ej. si
  `move-change.py` mueve el change mientras el agente no ha vuelto a escribir). Quien lea
  el registro resuelve el estado buscando en qué subcarpeta de `changes/` vive
  `changeCode` en ese instante, igual que ya hace `list_implemented_entries()` en
  `pv.py` (L623) para una sola carpeta — aquí basta recorrer las cuatro.
- `phase`: uno de los 7 valores fijos (ver sección 2).
- `updatedAt`: timestamp ISO-8601 UTC de la última escritura — es lo único que el
  timeout evalúa.
- `notes` (opcional, `string | null`, default `null`): texto libre para que el agente
  anote algo que no cabe en `phase` (p. ej. por qué está bloqueado en `waiting_external`,
  o un detalle puntual de lo que está haciendo dentro de `implementing`). No estructurado
  ni validado — es la vía de escape para no forzar el catálogo fijo de fases a cubrir
  cada caso particular. No participa en el cálculo de `stale` (solo `updatedAt` lo hace).
- `refHash` (opcional, `string | null`): hash de referencia de los ficheros del change,
  usado solo por la verificación de conflicto de la sección 6. Se escribe únicamente al
  entrar en `planning` (ver sección 3) y no se toca en el resto de fases — ver el detalle
  completo en 6.1.
- `changeStartedAt` (opcional, `string | null`, timestamp ISO-8601 UTC): momento en que la
  entrada quedó asociada al `changeCode` que tiene ahora. Solo alimenta el criterio de
  ordenación "Tiempo de trabajo" de la sección 5.1 — no participa en el cálculo de
  `stale` (eso solo lo hace `updatedAt`). Se recalcula cada vez que `changeCode` cambia de
  valor (incluido pasar de `null` a un código, ver sección 3); si una escritura repite el
  mismo `changeCode` que ya tenía la entrada, `changeStartedAt` no se toca.

Riesgo de escritura concurrente (dos agentes actualizando a la vez): se acepta
read-modify-write simple, igual que hace hoy `set-metadata.py` con `.metadata.json` — no
hay lock file ni escritura atómica en el resto del framework, así que no se introduce
aquí una garantía que no existe en ningún otro punto de pv-*.

### 2. Catálogo fijo de fases

Igual que `FLAG_VALUES` en `pv.py` (L156), un catálogo cerrado y compartido:

| Valor interno | Label | Significa |
|---|---|---|
| `analyzing` | Analizando | `pv-internal-tech-analysis` u otra fase de investigación/lectura de código y docs. |
| `planning` | Diseñando/planificando | Escribiendo `plan.md`, mockups, diagramas — antes de tocar código real. |
| `implementing` | Implementando | Editando ficheros de código o tests del change. |
| `documenting` | Documentando | Actualizando `docs.tech.*`, `description.md` o `changelog.md`. |
| `waiting_user` | Esperando confirmación del usuario | Bloqueado en un `AskUserQuestion` o `confirm()` pendiente. |
| `waiting_external` | Esperando algo externo | Bloqueado por un build, test, u otra skill/agente — no por el usuario. |
| `done` | Terminado | El agente considera su parte hecha. |
| `blocked_conflict` | Bloqueado por conflicto | Detectado un posible pisoteo (ver sección 6) antes de implementar: ficheros cambiados desde `planning`, u otro agente ya activo sobre el mismo change. Requiere autorización explícita del usuario para continuar. |

Sin heartbeat: la fase vigente es siempre la última escrita, no hay una escritura de
"salida" de fase — al entrar en la siguiente, la sobreescribe. `blocked_conflict` es la
única excepción con un flujo de salida propio: solo se abandona cuando el usuario
autoriza explícitamente continuar (pasa a `implementing`) o cancela.

### 3. Quién escribe, y dónde

**Nuevo script**, en el patrón ya establecido por `pv-internal-workflow`:
`.claude/skills/pv-internal-workflow/scripts/set-agent-status.py`, invocado así:

```
python3 set-agent-status.py --session-id <id> --phase implementing \
    [--xxxx 0042] [--notes "texto libre"] [--work-folder ...]
```

- Sin `--xxxx`: limpia el vínculo con un change (agente sin change activo). No se pasa
  ni se guarda ningún estado de carpeta — ver nota en la sección 1 sobre por qué
  `changeState` no forma parte del registro.
- Sin `--notes`: pone `notes` a `null` — cada escritura de fase reemplaza la nota
  anterior entera, no la acumula (mismo criterio "última escritura gana" que `phase`).
- `changeStartedAt`: el script compara el `--xxxx` recibido (o su ausencia) contra el
  `changeCode` que la entrada ya tenía antes de esta escritura. Si difieren — incluido el
  caso "no tenía ninguno y ahora sí" —, fija `changeStartedAt` al instante actual. Si
  coincide (mismo `changeCode` que ya tenía, o ambos `null`), deja `changeStartedAt` tal
  cual estaba. Al limpiar el vínculo con un change (sin `--xxxx`), `changeStartedAt` se
  pone a `null` igual que `changeCode`.
- Al escribir `--phase planning`, guarda además `refHash` (ver sección 6.1) calculado en
  ese instante — es el único caso en que el script guarda un campo aparte de los ya
  descritos en la sección 1; el resto de fases no lo tocan ni lo borran, así que
  `refHash` sigue siendo el de la última vez que alguien entró en `planning`, sea quien
  sea.
- Hace un read-modify-write de `.agents-status.json`, igual que `set-metadata.py` hace
  con `.metadata.json` — mismo patrón, mismo nivel de garantías.
- Acepta `--work-folder` para el test-harness, como el resto de scripts en
  `SCRIPTS_ACCEPTING_WORK_FOLDER`.

**Puntos de llamada — en el diagrama, no en prosa suelta.** Cada skill orquestadora del
grupo claro ya tiene su flujo documentado como un diagrama Mermaid en un fichero
`workflow.{nombre}.md` aparte (p. ej. `pv-fix/workflow.fix.md`, `pv-how/workflow.how.md`,
`pv-new/workflow.new.md`, `pv-do/workflow.do.md`), con una notación ya establecida
(`[Text]` paso interno, `[INFO: Text]` informa sin bloquear, `[ASK: Text]` bloquea
esperando al usuario, `{Text}` decisión). La instrumentación real es: añadir un nodo
`[REPORT: <fase>]` justo antes del nodo existente donde arranca cada fase, en ese mismo
diagrama — no prosa nueva en el `SKILL.md`. Ejemplo concreto sobre
`pv-fix/workflow.fix.md`:

- Antes de `S2Analysis` (`Invoke pv-internal-tech-analysis for context`) → `[REPORT: analyzing]`.
- Antes de `S3Doc`/`S4Mockup`/`S41Write` (documentar intención, diagramas, mockups, datos) → `[REPORT: planning]`.
- Antes de `FT2` (`Apply the change directly in code`) y en la rama que sigue
  `S6Chain → pv-how → pv-do` → `[REPORT: implementing]`.
- Los nodos `[ASK: ...]` que **ya existen** (`S1Ask`, `S5Ask`) son directamente
  `waiting_user` — no hace falta inventar un nodo nuevo, el propio vocabulario del
  diagrama ya distingue ese caso. Del mismo modo, un futuro nodo que espere un proceso
  externo (build/test) sería `waiting_external`.
- `FT4` (`move inProgress to implemented`) ya es el punto de `pv-internal-workflow` que
  marca `done` (ver más abajo) — no se toca `workflow.fix.md` para eso.
- `blocked_conflict` no es un nodo de esta lista — se reporta desde el nodo nuevo de la
  sección 6, antes de cualquier hook, no en una transición de fase "normal". Se detalla
  ahí, no aquí, para no duplicar la explicación.

El `xxxx` del change no necesita pasarse como parámetro nuevo a estas skills: en estos
diagramas ya está fijado desde que se crea `description.md`/`history.md` (nodo `S3Doc` en
`pv-fix`, equivalente en las demás), así que el agente ya lo tiene en contexto en
cualquier punto posterior del mismo flujo.

**Las `pv-internal-*` (skills-hoja invocadas por las orquestadoras) no se instrumentan
directamente.** Comprobado sobre `pv-fix`/`pv-how` (los dos casos con más subskills
invocadas): cada `pv-internal-*` cae siempre dentro de una fase que el diagrama del
*caller* ya distingue con sus propios nodos —

- `pv-internal-tech-analysis` (y, dentro de ella, `pv-internal-tech-security`, que ni
  siquiera aparece como nodo aparte en `workflow.fix.md`) → ambas caen bajo el mismo
  `[REPORT: analyzing]` puesto antes de `S2Analysis`.
- `pv-internal-mockups-ascii/-html` y `pv-internal-tech-mermaid` → los tres caen bajo el
  mismo `[REPORT: planning]` puesto antes de `S3Doc` (son nodos distintos dentro de la
  fase de diseño, pero la fase es una sola).
- `pv-internal-tech-risks` → invocada dentro de `pv-how`, ya cubierta por el
  `[REPORT: planning]`/`[REPORT: analyzing]` de ese diagrama.
- `pv-internal-doc-technical/-features/-files/-style` → invocadas dentro de `pv-do`, ya
  cubiertas por un único `[REPORT: documenting]` en `workflow.do.md`.

No hay ningún caso en el grupo claro donde una `pv-internal-*` represente una fase que el
diagrama de quien la invoca no distinga ya por sí mismo. Instrumentarlas aparte
duplicaría el reporte sin añadir granularidad real, así que quedan fuera de la
instrumentación directa — se benefician del reporte de su caller, no reportan ellas
mismas.

Tabla única (inventario completo de `.claude/skills/pv-*`, sin
duplicarla en otra parte del documento) que cruza cada skill del repo con las fases que
le tocaría reportar:

Columna **Orden** = orden de implementación sugerido dentro del "grupo a instrumentar"
(más abajo). Criterio: primero las orquestadoras más simples (menos fases, menos
dependencias), al final la más exigente (`pv-fix`, que recorre 3 fases) y el cierre en
`pv-internal-workflow`.

Columna **Cambios** = confirmado contra el disco real: las 4 orquestadoras tienen
diagrama Mermaid propio (`workflow.{nombre}.md`); `pv-internal-workflow` no, así que su
único cambio es prosa/script en su punto de mover a `implemented`.

| Skill | ¿Aplica? | Fase(s) que reportaría | Orden | Cambios | Notas |
|---|---|---|---|---|---|
| `pv-how` | Sí | `analyzing` → `planning` | 1 | Diagrama (`workflow.how.md`) | Orquesta 2 fases; cubre por sí sola `pv-internal-tech-analysis` (+ `-security` dentro) y `pv-internal-tech-risks`, que no se instrumentan aparte (ver más abajo). No pasa nunca por `pv-internal-workflow` — no crea ni mueve carpetas, solo lee el `description.md` que ya escribió `pv-new`/`pv-fix`, y al confirmar el usuario encadena a `pv-do` (que sí cierra). |
| `pv-new` | Sí | `planning` | 2 | Diagrama (`workflow.new.md`) | `description.md`, `plan.md`, mockups. Cubre `pv-internal-tech-analysis` y los mockups/mermaid invocados dentro de su propia fase `planning`. |
| `pv-do` | Sí | `implementing` → `documenting` | 3 | Diagrama (`workflow.do.md`) | Ejecuta el `plan.md` ya escrito y luego actualiza la documentación; cubre las 4 `pv-internal-doc-*` invocadas dentro de su propia fase `documenting`. |
| `pv-fix` | Sí | `analyzing` → `planning` → `implementing` | 4 | Diagrama (`workflow.fix.md`) | Recorre las 3 fases dentro de la misma skill — el caso más exigente, se deja para el final una vez validado el patrón en las demás. |
| `pv-internal-workflow` | Parcial | — (marca `done`) | 5 | Solo skill (sin diagrama propio) | Único punto de cierre real: el nodo `S3Move`/`FT4` (`Invoke pv-internal-workflow action=move, inProgress to implemented`) que ya existe en `workflow.do.md` y en el fast-track de `workflow.fix.md`. `pv-how` **no** pasa por aquí — nunca mueve carpetas, delega en `pv-do` para eso (ver nota de `pv-how` arriba). Solo tiene sentido una vez `pv-do`/`pv-fix` ya reportan fases que "cerrar". |
| `pv-todo` | No | — | — | — | Opera sobre `changes/todo/`, ideas sin analizar, sin agente "trabajando" en curso. |
| `pv-status` | No | — | — | — | Es la propia herramienta de lectura (`pv.py` delega en sus scripts) — no tiene sentido que reporte sobre sí misma. |
| `pv-update` | Dudoso | — | — | — | Actualiza el framework pv-* en sí, no un change de Previo — encajaría como `implementing`/`documenting` pero sobre el framework, no sobre `changes/`. |
| `pv-init` | No | — | — | — | Se ejecuta antes de que exista ningún change; no hay `changeCode` al que asociarlo. |
| `pv-version` | Dudoso | — | — | — | Opera sobre `changes/closed/` en bloque (varios changes a la vez) — el modelo "una entrada, un `changeCode`" no le encaja directamente. |
| `pv-internal-changelog` | Dudoso | — | — | — | Invocada por `pv-version`, mismo problema: trabaja sobre varios changes agregados, no uno. |

De los 7 valores del catálogo (sección 2), la tabla cubre `analyzing`, `planning`,
`implementing`, `documenting` y `done` con una fila fija por skill. Los otros dos —
`waiting_user` y `waiting_external` — no tienen fila propia **a propósito**: no son la
fase "normal" de ninguna skill concreta, son un estado transversal que cualquiera de las
5 puede tomar puntualmente en vez de su fase habitual (`waiting_user` en un nodo
`[ASK: ...]` ya existente en su diagrama; `waiting_external` esperando un proceso
externo — tests, build). Añadirles fila propia implicaría, incorrectamente, atarlos a
una sola skill.

**No instrumentadas directamente** (se benefician del reporte de quien las invoca, ver
justificación más arriba): `pv-internal-tech-analysis`, `pv-internal-tech-security`,
`pv-internal-mockups-ascii/-html`, `pv-internal-tech-mermaid`, `pv-internal-tech-risks`,
`pv-internal-doc-technical/-features/-files/-style`. Ninguna necesita fila propia con
Orden/Cambios porque no se les toca nada — quedan cubiertas por el `[REPORT: fase]` de su
caller.

**Grupo a instrumentar**: `pv-how`, `pv-new`, `pv-do`, `pv-fix` (diagrama, orden 1-4) y
`pv-internal-workflow` (cierre `done`, orden 5).

**Grupo fuera de alcance por ahora** (no operan sobre un `changeCode` único, o no tiene
sentido que reporten): `pv-todo`, `pv-status`, `pv-init`, `pv-update`, `pv-version`,
`pv-internal-changelog` — se revisita si en la práctica se echa en falta visibilidad
sobre ellas.

Esto es **fiabilidad limitada por diseño**: son instrucciones en markdown que un agente
ejecuta, no una garantía de runtime. Se acepta explícitamente que un agente puede
saltarse un marcado — el timeout (sección 4) es la red de seguridad para ese caso, no se
persigue el 100% de precisión.

Alcance de "agente" a efectos de este sistema: cualquier sesión que `ListAgents` pueda
ver (interactivas locales, subagentes lanzados con el tool `Agent`, sesiones cloud/
remote-control) — el registro no distingue el tipo de sesión, solo guarda lo que cada
una reporta.

### 4. Timeout configurable

Nuevo campo en `.claude/pv-context.json`, mismo patrón que `framework.onescript.width`:

```json
"framework": {
  "agents": {
    "staleTimeoutMinutes": 2
  }
}
```

- Default si el campo está ausente o es inválido: 2 minutos (valor elegido para probar
  en esta primera versión — se acepta reevaluarlo con uso real).
- **No hay proceso de fondo que purgue el fichero.** El timeout se evalúa en el momento
  de la lectura: cualquier consumidor (la opción nueva de `pv.py`, o el script que yo
  invoco desde el chat) compara `updatedAt` contra "ahora" y muestra la entrada como
  `stale` (caída / sin respuesta) si excede el límite, en vez de mostrarla con su última
  fase reportada como si siguiera vigente. El fichero en sí no se reescribe solo por
  efecto del timeout — una entrada `stale` puede "revivir" sola si esa sesión vuelve a
  escribir.

### 5. Lectura / presentación

**Nuevo script de lectura**, `.claude/skills/pv-status/scripts/read-agents-status.py`
(mismo patrón que `read-flags.py`: sin dependencias, acepta `--terminal`/`--color`/
`--no-color`/`--width`/`--work-folder`):

- Lee `.agents-status.json` (vacío/ausente → lista vacía, no error).
- Por cada entrada con `changeCode` no nulo, resuelve el estado de carpeta recorriendo
  `changes/{todo,inProgress,implemented,closed}/{changeCode}/` (igual que
  `list_implemented_entries()` en `pv.py`, pero mirando las cuatro carpetas) — si no lo
  encuentra en ninguna (se borró, o `changeCode` quedó obsoleto), lo muestra sin estado
  resuelto en vez de fallar.
- Cruza cada entrada con `ListAgents` **no** — ese cruce solo lo puede hacer una sesión
  de Claude Code (el script no tiene acceso a esa herramienta). El script solo sabe lo
  que hay escrito en disco. El cruce visual "esta entrada del fichero corresponde a este
  peer que veo en `ListAgents`" lo hace quien consulta desde el chat, no el script.
- Aplica el timeout de la sección 4 y marca cada entrada `active` / `stale`.
- En modo `--terminal`: listado agrupado por `changeCode` (o "Sin change asignado"),
  con el estado de carpeta resuelto, fase y tiempo transcurrido desde `updatedAt`.
- Acepta `--sort {priority,updated,worktime}` (default `priority`, ver criterios y
  desempate en la sección 5.1). El script ordena en memoria tras aplicar el timeout —
  `stale` es un estado calculado, no un campo del fichero, así que el ordenamiento por
  prioridad necesita que el timeout ya se haya evaluado antes de ordenar.

**En `pv.py`**: reestructuración del menú raíz para dar hueco a "Agents status" sin
mezclarlo con las opciones que ya operan sobre changes. El `MENU` raíz (pv.py L1197-1204)
pasa de:

```
1. General project status
2. Changes info
3. Ideas in todo/
4. Close an implemented entry (move to changes/closed/)
5. Configuration
6. Check Previo versions
```

a:

```
1. General project status
2. Changes info
3. Ideas in todo/
4. Close an implemented entry (move to changes/closed/)
5. Check versions          (antes "6. Check Previo versions", renombrada)
6. Framework status        (nueva)
   1. Agents status        (nueva — delega en read-agents-status.py)
   2. Configuration        (la actual show_settings_menu(), movida aquí desde la raíz)
```

- "Configuration" **deja de ser una opción de la raíz** — su único acceso pasa a ser a
  través de "Framework status". No queda un acceso duplicado.
- "Check Previo versions" se renombra a "Check versions" y baja de posición 6 a 5, sin
  cambios de contenido (`show_versions_menu()` sigue igual).
- Nuevo submenú `show_framework_status_menu()`, marcado `.is_submenu = True` igual que
  `show_settings_menu`/`show_versions_menu` (pv.py L755/825), con dos entradas:
  "Agents status" (pregunta primero el criterio de orden — Prioridad/Actualizados/Tiempo
  de trabajo, default Prioridad — y llama a
  `run_script(STATUS_SCRIPTS / "read-agents-status.py", "--terminal", "--sort", <valor>)`,
  mismo patrón que `show_general_status()` en L553) y "Configuration"
  (`show_settings_menu`, reutilizada tal cual, no duplicada).

**Desde el chat**: sigue funcionando como ya hemos probado — `ListAgents` para ver qué
sesiones existen y su `idle`/`busy`, y ahora además puedo leer `.agents-status.json` (vía
`read-agents-status.py` o directamente) para cruzarlo con el change y la fase que cada
una reportó, y con `SendMessage` si hace falta profundizar puntualmente en una sesión
concreta.

### 5.1 Mockup de la pantalla `--terminal`

Mismo estilo visual que ya usa `render_status.py` (`term.title`/`term.heading`/`term.hr`,
emoji si hay color, `[P]`/`[W]`-style ASCII si `--no-color`) — no se inventa un formato
nuevo, se reutiliza `terminal_output.py` tal cual.

**El registro es por sesión, no por change** (sección 1: una entrada de
`.agents-status.json` = una sesión), así que el listado es una lista de agentes primero
— cada bloque es una sesión, y el change al que está asociada (si tiene alguno) es un
dato dentro de ese bloque, no el encabezado que los agrupa.

**Tres criterios de ordenación** (`--sort`, sección 5), seleccionables tanto desde
`--terminal` como desde el submenú de `pv.py` (un `{Text}` de selección antes de listar,
mismo patrón que otros menús con opciones):

| `--sort` | Criterio | Desempate |
|---|---|---|
| `priority` (default) | Dos grupos: **activos** (`waiting_user`, `implementing`, `documenting`, `analyzing`, `planning`) primero, **resto** (`done`, `waiting_external`, `blocked_conflict`, `stale`) después. | Dentro de cada grupo, `updatedAt` descendente (más reciente primero). |
| `updated` | `updatedAt` ascendente — el que lleva más tiempo sin refrescar primero (los `stale` u olvidados suben arriba, útil para detectar agentes colgados de un vistazo). | — |
| `worktime` | `changeStartedAt` descendente — el que lleva más tiempo trabajando sobre su `changeCode` actual primero. Entradas sin `changeCode` (`changeStartedAt` a `null`) van al final, ordenadas entre sí por `updatedAt` descendente. | — |

`blocked_conflict` queda en el grupo "resto" de `priority` a propósito: no es que no
importe, pero ya destaca visualmente por su propio bloque `BLOQUEADO POR CONFLICTO` en
mayúsculas (ver mockup abajo) — agruparlo con los activos diluiría esa señal en vez de
reforzarla. `waiting_external` igual: es "algo está pasando" pero no requiere acción de
nadie ahora mismo, a diferencia de `waiting_user`.

**Un emoji por fase** (no un semáforo genérico — cada valor del catálogo de la sección 2
tiene su propio icono, más uno para `stale`, que no es una fase sino un estado
transversal calculado al leer):

| Fase / estado | Emoji |
|---|---|
| `analyzing` | 🔍 |
| `planning` | 📐 |
| `implementing` | ⚙️ |
| `documenting` | 📝 |
| `waiting_user` | ❓ |
| `waiting_external` | ⏳ |
| `done` | ✅ |
| `blocked_conflict` | ⛔ |
| `stale` (timeout, sección 4 — sustituye al emoji de fase, no se combinan) | 💀 |

**Caso con las 9 variantes** (una sesión por fila del catálogo, para ver todos los
emojis juntos — en la práctica normalmente habrá muchas menos entradas activas a la
vez):

```
════════════════════════════════════════════════════════════════
  AGENTS STATUS                        Generated: 2026-09-20 14:35
════════════════════════════════════════════════════════════════

🔍 e3882b (previo-sdd-b5)
   Analizando                                           hace 40 s
   Change: 0060 — Exportación batch de facturas          [inProgress]

📐 9f10ab (previo-sdd-a2)
   Diseñando/planificando                                hace 1 min
   Change: 0059 — Panel de auditoría de accesos          [inProgress]

⚙️ c72e19 (previo-sdd-c1)
   Implementando                                        hace 3 min
   Change: 0042 — Refactor de autenticación de sesión    [inProgress]
   "Aplicando plan.md, paso 2/4"

📝 a91f4c (previo-sdd-d7)
   Documentando                                          hace 1 min
   Change: 0038 — Exportación de informes a PDF          [implemented]

❓ f10cde (previo-sdd-e3)
   Esperando confirmación del usuario                   hace 45 s
   Change: 0051 — Migración de caché de sesión           [inProgress]
   (bloqueado en AskUserQuestion)

⏳ 7b2a91 (previo-sdd-f9)
   Esperando algo externo                                hace 2 min
   Change: 0055 — Job de sincronización nocturna          [inProgress]
   "Esperando a que termine el build de CI"

✅ d4e8f2 (previo-sdd-g4)
   Terminado                                            hace 30 s
   Change: 0037 — Filtro avanzado en listado de changes  [implemented]

⛔ b6019c (previo-sdd-h1)                    BLOQUEADO POR CONFLICTO
   hace 10 s
   Change: 0042 — Refactor de autenticación de sesión    [inProgress]
   "Otro agente (c72e19) ya está en 'implementing' sobre este mismo change"

💀 506b39 (bgfactory-2a)                                       STALE
   Analizando (última fase reportada — hace 14 min, sin refrescar)
   Change: — (sin change asignado)
   "Bloqueado por un test flaky en CI, reintentando"

------------------------------------------------------------------
🔍 analizando · 📐 planificando · ⚙️ implementando · 📝 documentando
❓ esperando usuario · ⏳ esperando externo · ✅ terminado
⛔ conflicto · 💀 stale (sin respuesta > 2 min)
[changeState] resuelto desde disco, no desde el registro.
------------------------------------------------------------------
```

**Caso vacío** (`.agents-status.json` ausente o sin entradas — no es un error):

```
════════════════════════════════════════════════════════════════
  AGENTS STATUS                        Generated: 2026-09-20 14:35
════════════════════════════════════════════════════════════════

(No hay agentes con actividad registrada.)

------------------------------------------------------------------
```

**Modo `--no-color`** (mismo contenido, con etiqueta de fase entre corchetes en vez de
emoji, mismo patrón que `flags_prefix()`):

```
[IMPLEMENTING] c72e19 (previo-sdd-c1)
   Implementando                                        hace 3 min
   Change: 0042 - Refactor de autenticacion de sesion    [inProgress]
```

Estos son bocetos de formato, no el layout final pixel-a-pixel — la implementación real
decide columnas exactas, truncado de nombres largos, y wrapping (`term.wrap`) igual que
ya hace `render_status.py` con `--width`.

### 6. Verificación previa a implementar (detección de conflicto)

**Debe ir antes de cualquier hook del proyecto, no solo antes del propio código.**
`pv-do` y `pv-fix` ejecutan hooks de `stuff/hooks/{do,fix}/*.md` (pasos escritos por el
propio proyecto, no por el framework) **antes** de llegar al nodo que aplica el cambio
(`S20Hook`/`S20Run` en `workflow.do.md`, `FTHookEntry`/`FTHookStart` en
`workflow.fix.md`). Si el nodo de verificación se pusiera solo "justo antes de aplicar
el cambio" (como en un borrador anterior de esta sección), un hook —que puede tocar
ficheros del change, o directamente adelantar trabajo de implementación— se ejecutaría
**sin pasar por esta comprobación**, dejando la protección con un hueco explotable. Por
eso el nodo de verificación va **antes del primer hook de la skill**, no entre el hook y
el código:

- En `pv-do`: antes de `S15Load` (que es lo que dispara `S20Hook`).
- En `pv-fix` (fast-track): antes de `FTLoad` (que dispara `FTHookEntry`).

Con el nodo ahí, ningún hook puede ejecutarse sin que la verificación ya haya corrido
primero — "hackear" un hook para saltarse el check dejaría de ser posible porque el
check ya pasó (o bloqueó) antes de que el hook exista como paso alcanzable.

Aparte de esto, se ejecutan dos comprobaciones. Si cualquiera de las dos detecta un
posible conflicto, la skill reporta `blocked_conflict` (en vez de `implementing`) e
informa al usuario con el motivo exacto — **no ejecuta ningún hook ni edita ningún
fichero de código hasta que el usuario autorice explícitamente continuar**.

**6.1. Ficheros del change modificados desde `planning`**

- Al entrar en `planning` (no en `implementing` — ver sección 3, es el único momento en
  que `set-agent-status.py` toca este campo), guarda además un campo `refHash`: el
  resultado de
  `git rev-parse HEAD:{ruta del change}` (o, si hay cambios sin commitear bajo esa ruta,
  un hash de contenido equivalente — a definir en la implementación) para
  `changes/inProgress/{xxxx}/` en ese instante. Cubre así todo el ciclo previo
  (análisis + planificación), no solo el instante justo antes de implementar — fijar el
  hash ya en `implementing` no protegería nada la primera vez, al comparar contra sí
  mismo.
- **Caso `pv-do` encadenado desde `pv-how`**: `pv-how` también orquesta la fase
  `planning` (sección 3), así que también fija su propio `refHash` al hacerlo — mismo
  criterio "última escritura gana" que ya rige `phase`. No hace falta lógica especial
  para este caso: si `pv-how` re-planifica un change ya creado por `pv-new`/`pv-fix`, su
  `refHash` sustituye al anterior sin más, y `pv-do` compara siempre contra el más
  reciente, sea de quien sea.
- Justo antes de pasar a `implementing`, se recalcula el mismo hash y se compara contra
  `refHash`. Si difieren, alguien (otro agente sin pasar por este mecanismo, o el propio
  usuario) tocó los ficheros del change entre medias.

**6.2. Otro agente activo sobre el mismo change**

- Es una lectura de `.agents-status.json` (sección 1), no un mecanismo nuevo: se busca si
  existe **otra** entrada (`sessionId` distinto) con el mismo `changeCode` y una fase
  activa (cualquiera salvo `done` y salvo `stale` por timeout — sección 4). Si la hay, es
  el mismo caso que "punto 2" de la petición original: no es una comprobación de
  ficheros, es la misma verificación de concurrencia ya cubierta por el registro.

**Nuevo script**, en el patrón ya establecido: `check-agent-conflict.py`
(`pv-internal-workflow/scripts/`), invocado antes de entrar en `implementing`:

```
python3 check-agent-conflict.py --session-id <id> --xxxx 0042 [--work-folder ...]
```

Devuelve sin conflicto (exit 0, sin output) o con el motivo (exit 1, una línea por cada
comprobación que falló: `files_changed` y/o `other_agent:<sessionId>:<phase>`). La skill
que invoca decide qué hacer con la salida — el script no bloquea nada por sí mismo, solo
informa.

**Puntos de inserción**: solo en las skills que de verdad llegan a `implementing` —
`pv-do` y `pv-fix`. `pv-how` nunca implementa directamente (ver sección 3), así que no
aparece en la tabla ni necesita este punto.

| Skill | Cambio | Nodo/punto de inserción |
|---|---|---|
| `pv-do` | Diagrama (`workflow.do.md`) | Nodo nuevo **antes de `S15Load`** (antes del primer hook, `10-before-implementation`): invoca `check-agent-conflict.py`; si hay conflicto, reporta `blocked_conflict` y pregunta al usuario antes de que corra ningún hook ni se toque código. |
| `pv-fix` | Diagrama (`workflow.fix.md`) | Mismo nodo nuevo, **antes de `FTLoad`** (antes de `fix/10-before-entry`, el primer hook del fast-track). |

## Fuera de alcance de esta primera versión

- Cualquier forma de heartbeat o consulta activa periódica (ver "Descartado" arriba).
- Limpieza/purga física de entradas `stale` del fichero — se quedan ahí, marcadas como
  caídas en la lectura, hasta que la sesión vuelva a escribir o alguien borre el fichero
  a mano. Si en la práctica el fichero crece sin control, se revisita.
- Instrumentar `pv-todo`, `pv-status`, `pv-init`, `pv-update`, `pv-version`,
  `pv-internal-changelog` (grupo fuera de alcance, sección 3) — se revisita si en la
  práctica se echa en falta visibilidad sobre ellas.

## Decisiones ya confirmadas en revisión

- Nodo de configuración `framework.agents.staleTimeoutMinutes` en `pv-context.json`:
  confirmado tal cual, no se agrupa bajo `framework.onescript`.
- El registro no guarda `changeState`: se resuelve siempre al leer, recorriendo
  `changes/` (ver secciones 1 y 5). No hay riesgo de que ambos campos se desincronicen
  porque solo hay un campo (`changeCode`).
- Sin piloto: se instrumentan las 5 skills del grupo (`pv-how`, `pv-new`, `pv-do`,
  `pv-fix`, `pv-internal-workflow`) más el mecanismo de conflicto de la sección 6, todo
  en la misma tanda de implementación.

## Lista de tareas para la implementación

Orden sugerido: de abajo hacia arriba (piezas base primero, instrumentación de skills al
final, porque estas últimas dependen de que los scripts ya existan).

1. **Config**: añadir `framework.agents.staleTimeoutMinutes` (default `2`) a
   `.claude/pv-context.json` y a su esquema/documentación si `pv-context.json` tiene uno
   validado en otro sitio del framework (comprobarlo antes de asumir que no).
2. **Script de escritura**: `pv-internal-workflow/scripts/set-agent-status.py` —
   `--session-id`, `--phase`, `--xxxx` opcional, `--notes` opcional, `--work-folder`;
   calcula y guarda `refHash` solo cuando `--phase planning`; recalcula `changeStartedAt`
   cuando `--xxxx` difiere del `changeCode` previo de la entrada (sección 3);
   read-modify-write de `{workFolder}/.agents-status.json` (crear el fichero si no
   existe).
3. **Script de verificación**: `pv-internal-workflow/scripts/check-agent-conflict.py` —
   `--session-id`, `--xxxx`, `--work-folder`; hace 6.1 (recalcular hash vs. `refHash`) y
   6.2 (buscar otra entrada activa con el mismo `changeCode`); exit 0/1 con motivo.
4. **Script de lectura**: `pv-status/scripts/read-agents-status.py` — lee
   `.agents-status.json`, resuelve estado de carpeta por `changeCode`, aplica el timeout
   de la sección 4, soporta `--terminal`/`--color`/`--no-color`/`--width`/`--work-folder`/
   `--sort {priority,updated,worktime}` (default `priority`, criterios en 5.1).
5. **`pv.py`**: reestructurar el `MENU` raíz (sección 5) — nuevo submenú
   `show_framework_status_menu()` con "Agents status" (pregunta el criterio de orden,
   delega en el script del punto 4 con `--sort`) y "Configuration" (reutiliza
   `show_settings_menu` existente); renombrar "Check Previo versions" a "Check versions"
   y reordenar.
6. **Instrumentar `pv-how`** (`workflow.how.md`): nodos `[REPORT: analyzing]` /
   `[REPORT: planning]` en los puntos que correspondan de su diagrama.
7. **Instrumentar `pv-new`** (`workflow.new.md`): nodo `[REPORT: planning]`.
8. **Instrumentar `pv-do`** (`workflow.do.md`): nodos `[REPORT: implementing]` /
   `[REPORT: documenting]`, más el nodo de verificación de conflicto (sección 6) **antes
   de `S15Load`**.
9. **Instrumentar `pv-fix`** (`workflow.fix.md`): nodos `[REPORT: analyzing]` /
   `[REPORT: planning]` / `[REPORT: implementing]` en las ramas correspondientes, más el
   nodo de verificación de conflicto **antes de `FTLoad`** en el fast-track.
10. **Cierre en `pv-internal-workflow`**: en el punto que ya invoca `move-change.py`
    (`S3Move`/`FT4` de los diagramas de `pv-do`/`pv-fix`), añadir la llamada a
    `set-agent-status.py --phase done` y la limpieza de `changeCode` (sección 3).
11. **Prueba manual de extremo a extremo**: recorrer un change real con `pv-new` →
    `pv-how` → `pv-do`, comprobando en cada paso que `.agents-status.json` refleja la
    fase correcta y que `pv.py` → "Framework status" → "Agents status" la muestra bien;
    forzar un conflicto a mano (editar un fichero del change entre `planning` e
    `implementing`) para comprobar que `blocked_conflict` se dispara y bloquea antes de
    cualquier hook.

## Revisión final del plan

- **Consistencia de campos**: `refHash` ya está documentado en las secciones 1 (campo
  del registro) y 3 (cuándo se escribe), no solo en 6.1 — dejaba de estar duplicado o
  colgado sin definición previa.
- **Consistencia de catálogo**: las 8 fases (7 + `blocked_conflict`) están todas
  justificadas: 5 con fila fija en la tabla de la sección 3, 2 transversales explicadas
  aparte, y `blocked_conflict` con su propio flujo de entrada/salida en la sección 2 y
  su nodo de disparo en la sección 6 — ninguna quedó mencionada en el catálogo sin decir
  dónde se dispara o se abandona.
- **Sin cabos sueltos de "piloto"**: al ir con todo, se retiraron las referencias a
  instrumentar "una sola skill primero" tanto en "Fuera de alcance" como en las
  preguntas abiertas — ya no queda una decisión pendiente que contradiga esa premisa.
- **Riesgo que el plan acepta explícitamente, no que ignora**: la fiabilidad del reporte
  depende de que cada skill ejecute correctamente una instrucción en markdown (sección
  3) — no hay garantía de runtime. El timeout (sección 4) y la verificación de conflicto
  (sección 6) son las dos redes de seguridad diseñadas para ese límite, no un intento de
  eliminarlo del todo.
- **Punto que sigue sin verificar contra el disco real** (a comprobar durante la
  implementación, no asumido aquí): si `pv-context.json` tiene algún esquema JSON
  validado en otro sitio del framework (p. ej. algo análogo a
  `metadata.schema.json` de `pv-internal-workflow`) al que también haya que añadir
  `framework.agents.staleTimeoutMinutes` — el plan asume que no, por analogía con
  `framework.onescript.width`, que tampoco parece tener uno, pero no se ha comprobado
  explícitamente.
