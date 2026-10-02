# `.agents-status.json`: registro de estado de agentes

Fichero central del diseño descrito en `PLAN.md`. Este documento define su estructura,
campos, catálogo de fases, quién lo escribe y con qué garantías, y el timeout que rige su
lectura. La lectura/presentación (sección 5 de `PLAN.md`) y la verificación de conflicto
(sección 6 de `PLAN.md`) son consumidores de este fichero, no parte de su definición —
están documentados aparte.

## 1. Registro único centralizado

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
  usado solo por la verificación de conflicto de la sección 6.1 de `PLAN.md`. Se escribe
  únicamente al entrar en `planning` (ver sección 3) y no se toca en el resto de fases.
- `changeStartedAt` (opcional, `string | null`, timestamp ISO-8601 UTC): momento en que la
  entrada quedó asociada al `changeCode` que tiene ahora. Solo alimenta el criterio de
  ordenación "Tiempo de trabajo" (sección 5.1 de `PLAN.md`) — no participa en el cálculo
  de `stale` (eso solo lo hace `updatedAt`). Se recalcula cada vez que `changeCode` cambia
  de valor (incluido pasar de `null` a un código, ver sección 3); si una escritura repite
  el mismo `changeCode` que ya tenía la entrada, `changeStartedAt` no se toca.

Riesgo de escritura concurrente (dos agentes actualizando a la vez): se acepta
read-modify-write simple, igual que hace hoy `set-metadata.py` con `.metadata.json` — no
hay lock file ni escritura atómica en el resto del framework, así que no se introduce
aquí una garantía que no existe en ningún otro punto de pv-*.

## 2. Catálogo fijo de fases

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
| `blocked_conflict` | Bloqueado por conflicto | Detectado, solo antes de `implementing` (ver sección 6.1 de `PLAN.md`), que los ficheros del change cambiaron desde `planning` sin pasar por este mecanismo. Requiere autorización explícita del usuario para continuar. **No cubre** el caso "otro agente ya activo sobre el mismo change" — ver sección 6.2 de `PLAN.md`, que no usa este estado: ahí el agente para y termina, no se queda en ningún valor del catálogo. |

Sin heartbeat: la fase vigente es siempre la última escrita, no hay una escritura de
"salida" de fase — al entrar en la siguiente, la sobreescribe. `blocked_conflict` es la
única excepción con un flujo de salida propio: solo se abandona cuando el usuario
autoriza explícitamente continuar (pasa a `implementing`) o cancela.

## 3. Quién escribe, y dónde

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
- Al escribir `--phase planning`, guarda además `refHash` (ver sección 6.1 de `PLAN.md`)
  calculado en ese instante — es el único caso en que el script guarda un campo aparte de
  los ya descritos en la sección 1; el resto de fases no lo tocan ni lo borran, así que
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
- `blocked_conflict` no es un nodo de esta lista — se reporta desde el nodo de la sección
  6.1 de `PLAN.md`, antes de cualquier hook, no en una transición de fase "normal". El
  nodo de la sección 6.2 (otro agente activo) tampoco es un nodo de esta lista: va al
  inicio del diagrama, antes del primer `[REPORT: ...]`, y no escribe ningún valor del
  catálogo — el agente simplemente termina si detecta colisión. Ambos se detallan en
  `PLAN.md`, no aquí, para no duplicar la explicación.

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

## 4. Timeout configurable

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
