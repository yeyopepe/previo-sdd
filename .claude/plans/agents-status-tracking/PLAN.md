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

### 1-4. Registro `.agents-status.json`

Todo lo relativo a la definición del fichero de estado — estructura, campos, catálogo
fijo de fases, quién escribe en él y con qué garantías, y el timeout de caducidad — está
documentado por separado en [`agent-status-file.md`](./agent-status-file.md). Las
secciones 5 y 6 de este documento son consumidoras de ese fichero, no parte de su
definición.

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
- Aplica el timeout de la sección 4 de `agent-status-file.md` y marca cada entrada `active` / `stale`.
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

**El registro es por sesión, no por change** (sección 1 de `agent-status-file.md`: una entrada de
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
| `stale` (timeout, sección 4 de `agent-status-file.md` — sustituye al emoji de fase, no se combinan) | 💀 |

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

### 6. Verificación de conflicto

Dos mecanismos independientes, con severidad distinta porque cubren riesgos distintos:
**6.2 es un corte duro** (dos agentes trabajando a la vez sobre el mismo change — no hay
nada que autorizar, autorizar sería aceptar el pisotón en curso) y **6.1 es un aviso con
autorización** (el contenido del change cambió respecto a lo planificado, lo cual puede
ser perfectamente intencional — un ajuste manual del usuario — y solo él tiene contexto
para decidir si invalida el plan).

**6.1. Ficheros del change modificados desde `planning`** (sin cambios respecto al
diseño original de esta sección)

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

- Al entrar en `planning` (no en `implementing` — ver sección 3 de `agent-status-file.md`, es el único momento en
  que `set-agent-status.py` toca este campo), guarda además un campo `refHash`: el
  resultado de
  `git rev-parse HEAD:{ruta del change}` (o, si hay cambios sin commitear bajo esa ruta,
  un hash de contenido equivalente — a definir en la implementación) para
  `changes/inProgress/{xxxx}/` en ese instante. Cubre así todo el ciclo previo
  (análisis + planificación), no solo el instante justo antes de implementar — fijar el
  hash ya en `implementing` no protegería nada la primera vez, al comparar contra sí
  mismo.
- **Caso `pv-do` encadenado desde `pv-how`**: `pv-how` también orquesta la fase
  `planning` (sección 3 de `agent-status-file.md`), así que también fija su propio `refHash` al hacerlo — mismo
  criterio "última escritura gana" que ya rige `phase`. No hace falta lógica especial
  para este caso: si `pv-how` re-planifica un change ya creado por `pv-new`/`pv-fix`, su
  `refHash` sustituye al anterior sin más, y `pv-do` compara siempre contra el más
  reciente, sea de quien sea.
- Justo antes de pasar a `implementing`, se recalcula el mismo hash y se compara contra
  `refHash`. Si difieren, alguien (otro agente sin pasar por este mecanismo, o el propio
  usuario) tocó los ficheros del change entre medias.

**Nuevo script**, en el patrón ya establecido: `check-agent-conflict.py`
(`pv-internal-workflow/scripts/`), invocado antes de entrar en `implementing`:

```
python3 check-agent-conflict.py --session-id <id> --xxxx 0042 [--work-folder ...]
```

Devuelve sin conflicto (exit 0, sin output) o con el motivo (exit 1: `files_changed`). Si
detecta conflicto, la skill reporta `blocked_conflict` (en vez de `implementing`) e
informa al usuario con el motivo exacto — **no ejecuta ningún hook ni edita ningún
fichero de código hasta que el usuario autorice explícitamente continuar**. La skill que
invoca decide qué hacer con la salida — el script no bloquea nada por sí mismo, solo
informa.

**Puntos de inserción**: solo en las skills que de verdad llegan a `implementing` —
`pv-do` y `pv-fix`. `pv-how` nunca implementa directamente (ver sección 3 de `agent-status-file.md`), así que no
aparece en la tabla ni necesita este punto.

| Skill | Cambio | Nodo/punto de inserción |
|---|---|---|
| `pv-do` | Diagrama (`workflow.do.md`) | Nodo nuevo **antes de `S15Load`** (antes del primer hook, `10-before-implementation`): invoca `check-agent-conflict.py`; si hay conflicto, reporta `blocked_conflict` y pregunta al usuario antes de que corra ningún hook ni se toque código. |
| `pv-fix` | Diagrama (`workflow.fix.md`) | Mismo nodo nuevo, **antes de `FTLoad`** (antes de `fix/10-before-entry`, el primer hook del fast-track). |

**6.2. Otro agente activo sobre el mismo change** (generalizado: como mucho un agente
activo por `changeCode`, en cualquier fase, no solo antes de implementar)

- Es una lectura de `.agents-status.json` (sección 1 de `agent-status-file.md`), no un mecanismo nuevo: se busca si
  existe **otra** entrada (`sessionId` distinto) con el mismo `changeCode` y una fase
  activa (cualquiera salvo `done` y salvo `stale` por timeout — sección 4 de `agent-status-file.md`).
- A diferencia de 6.1, esto **no depende de en qué fase esté la skill que arranca**: se
  comprueba nada más entrar, antes de hacer nada más — analizar, planificar, implementar,
  documentar o cerrar el change son todos "trabajar sobre el change", y el registro solo
  permite una sesión activa a la vez sobre el mismo `changeCode`, sea cual sea la fase de
  esa sesión y la fase a la que quiere entrar la que llega.
- **Salida: corte duro, sin autorización posible.** Si hay colisión, el agente **para y
  termina la ejecución ahí mismo**, informando al usuario qué sesión tiene el change
  tomado y en qué fase. No se reporta `blocked_conflict` ni ningún otro valor del
  catálogo de fases (sección 2 de `agent-status-file.md`) — la propia sesión termina, así que no hay una fase
  "vigente" que mostrar aparte de la que ya tenía antes de este intento (o ninguna, si es
  su primer contacto con el change). No hay camino para que el usuario autorice seguir
  desde aquí: autorizarlo sería aceptar la escritura concurrente que este mecanismo
  existe para evitar. Quien quiera desbloquearlo tiene que resolver el conflicto por
  fuera del framework (esperar a que la otra sesión termine, hablar con ella, etc.) y
  relanzar la skill.

**Nuevo script**, mismo patrón que el de 6.1 pero independiente (motivo y severidad
distintos no deben compartir script): `check-agent-active.py`
(`pv-internal-workflow/scripts/`), invocado al entrar en cualquiera de las 5 skills:

```
python3 check-agent-active.py --session-id <id> --xxxx 0042 [--work-folder ...]
```

Devuelve sin conflicto (exit 0, sin output) o con el motivo (exit 1:
`other_agent:<sessionId>:<phase>`). La skill que invoca es la que corta la ejecución e
informa al usuario — el script solo informa, igual que `check-agent-conflict.py`.

**Puntos de inserción**: al arrancar, en las 5 skills que trabajan sobre un `changeCode`
— antes de cualquier otro paso, incluida su propia primera escritura de fase (sección 3 de `agent-status-file.md`).

| Skill | Cambio | Nodo/punto de inserción |
|---|---|---|
| `pv-how` | Diagrama (`workflow.how.md`) | Nodo nuevo al inicio, antes del primer `[REPORT: analyzing]`. |
| `pv-new` | Diagrama (`workflow.new.md`) | Nodo nuevo al inicio, antes del `[REPORT: planning]`. |
| `pv-do` | Diagrama (`workflow.do.md`) | Nodo nuevo al inicio, antes del primer `[REPORT: implementing]` — independiente del nodo de 6.1, que sigue estando más adelante, justo antes de `S15Load`. |
| `pv-fix` | Diagrama (`workflow.fix.md`) | Nodo nuevo al inicio, antes del primer `[REPORT: analyzing]` — independiente del nodo de 6.1 en el fast-track. |
| Cierre (`pv-internal-workflow`, acción `move`) | Solo skill (sin diagrama propio) | Antes de mover la carpeta a `implemented`/`closed`. |

## Fuera de alcance de esta primera versión

- Cualquier forma de heartbeat o consulta activa periódica (ver "Descartado" arriba).
- Limpieza/purga física de entradas `stale` del fichero — se quedan ahí, marcadas como
  caídas en la lectura, hasta que la sesión vuelva a escribir o alguien borre el fichero
  a mano. Si en la práctica el fichero crece sin control, se revisita.
- Instrumentar `pv-todo`, `pv-status`, `pv-init`, `pv-update`, `pv-version`,
  `pv-internal-changelog` (grupo fuera de alcance, sección 3 de `agent-status-file.md`) — se revisita si en la
  práctica se echa en falta visibilidad sobre ellas.

## Decisiones ya confirmadas en revisión

- Nodo de configuración `framework.agents.staleTimeoutMinutes` en `pv-context.json`:
  confirmado tal cual, no se agrupa bajo `framework.onescript`.
- El registro no guarda `changeState`: se resuelve siempre al leer, recorriendo
  `changes/` (ver secciones 1 y 5). No hay riesgo de que ambos campos se desincronicen
  porque solo hay un campo (`changeCode`).
- Sin piloto: se instrumentan las 5 skills del grupo (`pv-how`, `pv-new`, `pv-do`,
  `pv-fix`, `pv-internal-workflow`) más los dos mecanismos de conflicto de la sección 6
  (6.1 solo en `pv-do`/`pv-fix`, 6.2 en las 5), todo en la misma tanda de implementación.
- Generalización de 6.2 (revisión posterior al primer diseño): "otro agente activo sobre
  el mismo change" deja de comprobarse solo antes de `implementing` y pasa a comprobarse
  al entrar en cualquiera de las 5 skills — como mucho una sesión activa por
  `changeCode`, en cualquier fase. Y su salida deja de ser "avisa y el usuario autoriza"
  (eso lo sigue siendo 6.1) para ser un corte duro sin apelación: el agente que llega
  tarde para y termina, no hay forma de autorizar la escritura concurrente que este
  mecanismo existe para evitar.

## Lista de tareas para la implementación

Orden sugerido: de abajo hacia arriba (piezas base primero, instrumentación de skills al
final, porque estas últimas dependen de que los scripts ya existan).

1. **Config**: añadir `framework.agents.staleTimeoutMinutes` (default `2`) a
   `.claude/pv-context.json` y a su esquema/documentación si `pv-context.json` tiene uno
   validado en otro sitio del framework (comprobarlo antes de asumir que no).
2. **Script de escritura**: `pv-internal-workflow/scripts/set-agent-status.py` —
   `--session-id`, `--phase`, `--xxxx` opcional, `--notes` opcional, `--work-folder`;
   calcula y guarda `refHash` solo cuando `--phase planning`; recalcula `changeStartedAt`
   cuando `--xxxx` difiere del `changeCode` previo de la entrada (sección 3 de `agent-status-file.md`);
   read-modify-write de `{workFolder}/.agents-status.json` (crear el fichero si no
   existe).
3. **Scripts de verificación** (dos, severidad distinta — ver sección 6):
   - `pv-internal-workflow/scripts/check-agent-conflict.py` — `--session-id`, `--xxxx`,
     `--work-folder`; hace 6.1 (recalcular hash vs. `refHash`); exit 0/1 con motivo
     (`files_changed`).
   - `pv-internal-workflow/scripts/check-agent-active.py` — `--session-id`, `--xxxx`,
     `--work-folder`; hace 6.2 (buscar otra entrada activa con el mismo `changeCode`);
     exit 0/1 con motivo (`other_agent:<sessionId>:<phase>`).
4. **Script de lectura**: `pv-status/scripts/read-agents-status.py` — lee
   `.agents-status.json`, resuelve estado de carpeta por `changeCode`, aplica el timeout
   de la sección 4 de `agent-status-file.md`, soporta `--terminal`/`--color`/`--no-color`/`--width`/`--work-folder`/
   `--sort {priority,updated,worktime}` (default `priority`, criterios en 5.1).
5. **`pv.py`**: reestructurar el `MENU` raíz (sección 5) — nuevo submenú
   `show_framework_status_menu()` con "Agents status" (pregunta el criterio de orden,
   delega en el script del punto 4 con `--sort`) y "Configuration" (reutiliza
   `show_settings_menu` existente); renombrar "Check Previo versions" a "Check versions"
   y reordenar.
6. **Instrumentar `pv-how`** (`workflow.how.md`): nodo de `check-agent-active.py`
   (sección 6.2) al inicio, antes del primer `[REPORT: ...]`; luego nodos
   `[REPORT: analyzing]` / `[REPORT: planning]` en los puntos que correspondan de su
   diagrama.
7. **Instrumentar `pv-new`** (`workflow.new.md`): nodo de `check-agent-active.py` al
   inicio; nodo `[REPORT: planning]`.
8. **Instrumentar `pv-do`** (`workflow.do.md`): nodo de `check-agent-active.py` al
   inicio; nodos `[REPORT: implementing]` / `[REPORT: documenting]`; más el nodo de
   `check-agent-conflict.py` (sección 6.1) **antes de `S15Load`**, independiente del
   anterior.
9. **Instrumentar `pv-fix`** (`workflow.fix.md`): nodo de `check-agent-active.py` al
   inicio del fast-track; nodos `[REPORT: analyzing]` / `[REPORT: planning]` /
   `[REPORT: implementing]` en las ramas correspondientes; más el nodo de
   `check-agent-conflict.py` **antes de `FTLoad`**, independiente del anterior.
10. **Cierre en `pv-internal-workflow`**: nodo de `check-agent-active.py` antes de
    empezar la acción `move`; en el punto que ya invoca `move-change.py` (`S3Move`/`FT4`
    de los diagramas de `pv-do`/`pv-fix`), añadir la llamada a
    `set-agent-status.py --phase done` y la limpieza de `changeCode` (sección 3 de `agent-status-file.md`).
11. **Prueba manual de extremo a extremo**: recorrer un change real con `pv-new` →
    `pv-how` → `pv-do`, comprobando en cada paso que `.agents-status.json` refleja la
    fase correcta y que `pv.py` → "Framework status" → "Agents status" la muestra bien;
    forzar un conflicto de contenido a mano (editar un fichero del change entre
    `planning` e `implementing`) para comprobar que `blocked_conflict` se dispara y
    bloquea antes de cualquier hook; y por separado, lanzar dos sesiones sobre el mismo
    `changeCode` para comprobar que la segunda corta su ejecución de inmediato sin pedir
    autorización.

## Revisión final del plan

- **Consistencia de campos**: `refHash` ya está documentado en las secciones 1 (campo
  del registro) y 3 (cuándo se escribe), no solo en 6.1 — dejaba de estar duplicado o
  colgado sin definición previa.
- **Consistencia de catálogo**: las 8 fases (7 + `blocked_conflict`) están todas
  justificadas: 5 con fila fija en la tabla de la sección 3 de `agent-status-file.md`, 2 transversales explicadas
  aparte, y `blocked_conflict` con su propio flujo de entrada/salida en la sección 2 de `agent-status-file.md` y
  su nodo de disparo en la sección 6.1 — ninguna quedó mencionada en el catálogo sin
  decir dónde se dispara o se abandona. El motivo de la sección 6.2 (otro agente activo)
  no usa el catálogo en absoluto — el corte es a nivel de ejecución, no de estado, y así
  queda dicho explícitamente en la sección 2 de `agent-status-file.md` para que no se lea como un descuido.
- **Sin cabos sueltos de "piloto"**: al ir con todo, se retiraron las referencias a
  instrumentar "una sola skill primero" tanto en "Fuera de alcance" como en las
  preguntas abiertas — ya no queda una decisión pendiente que contradiga esa premisa.
- **Riesgo que el plan acepta explícitamente, no que ignora**: la fiabilidad del reporte
  depende de que cada skill ejecute correctamente una instrucción en markdown (sección
  3 de `agent-status-file.md`) — no hay garantía de runtime. El timeout (sección 4 de
  `agent-status-file.md`) y la verificación de conflicto (sección 6) son las dos redes de
  seguridad diseñadas para ese límite, no un intento de eliminarlo del todo.
- **Punto que sigue sin verificar contra el disco real** (a comprobar durante la
  implementación, no asumido aquí): si `pv-context.json` tiene algún esquema JSON
  validado en otro sitio del framework (p. ej. algo análogo a
  `metadata.schema.json` de `pv-internal-workflow`) al que también haya que añadir
  `framework.agents.staleTimeoutMinutes` — el plan asume que no, por analogía con
  `framework.onescript.width`, que tampoco parece tener uno, pero no se ha comprobado
  explícitamente.
