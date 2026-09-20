# `10_todo-progress-tracking.md`: lista de tareas visible en el chat durante un flujo pv-*

## Context

Hoy, mientras `pv-fix`/`pv-how`/`pv-do`/`pv-new` ejecutan su flujo (varios pasos, algunos
largos: análisis, mockups, implementación...), el usuario no tiene forma de ver en la
interfaz por dónde va la skill sin preguntar en el chat. No es el mismo problema que
`08_agents-status-tracking.md` (ese es visibilidad *entre* sesiones/agentes, persistida en
disco); este es visibilidad *dentro* de la sesión actual, en tiempo real, usando el
mecanismo nativo del harness (`TodoWrite`): una checklist que se renderiza en la UI y se
va marcando `pending` → `in_progress` → `completed` a medida que la skill avanza.

**Objetivo:** que cada skill orquestadora (`pv-fix`, `pv-how`, `pv-do`, `pv-new`) publique
y actualice una checklist de sus pasos mayores en la interfaz, sin acoplar ese mecanismo a
`TodoWrite` de forma que migrar el framework a otro agente (p. ej. Copilot, que no tiene
`TodoWrite`) obligue a reescribir las 4 orquestadoras. El acoplamiento va todo detrás de
una única skill-hoja sustituible, igual que ya se hace con mockups y diagramas.

## Precedente ya existente en el framework: `framework.skills.*`

El framework ya resuelve exactamente este problema de aislamiento dos veces:

- `framework.skills.mockups` (default `pv-internal-mockups-html`) — mockups HTML.
- `framework.skills.diagrams` (default `pv-internal-tech-mermaid`) — diagramas Mermaid.

Ambas son skills-hoja con **contrato de entrada/salida explícito y documentado en su
propio `SKILL.md`**, invocadas siempre por nombre configurable, nunca hardcodeadas en las
orquestadoras. `pv-internal-tech-mermaid/SKILL.md` lo dice explícitamente: *"If a project
configures another skill in `framework.skills.diagrams` to generate diagrams a different
way [...], that alternative skill must fulfill the same input/output contract described
here so it can replace this one without pv-*  needing to change anything."*

Este plan aplica el mismo patrón, nada nuevo: una tercera entrada,
`framework.skills.progress`, con una skill-hoja por defecto que usa `TodoWrite`.

## Diseño propuesto

### 1. Nueva skill-hoja: `pv-internal-progress-todowrite`

`.claude/skills/pv-internal-progress-todowrite/SKILL.md`, mismo perfil que
`pv-internal-tech-mermaid` (`user-invocable: false`, sin `uses`, sin diálogo con el
usuario).

**Contrato de entrada** (lo que recibe del caller, en cada invocación):

- `action`: `init` | `update` | `close`.
- `items` (solo en `init`): lista ordenada de pasos mayores del flujo, cada uno con un
  texto breve en el idioma de `framework.interaction.language` (p. ej. "Analizar causa
  raíz", "Escribir plan.md", "Implementar cambios"). Es la lista *completa* del flujo tal
  y como el caller la conoce en el momento de arrancar — no hace falta que cubra ramas que
  aún no se sabe si se van a tomar (ver punto 3, listas dinámicas).
- `itemId` (en `update`/`close`): cuál de los items de `init` cambia de estado.
- `status` (en `update`): `in_progress` | `completed`. `close` marca todo lo que quede
  como `completed` de golpe (fin del flujo, éxito) o no marca nada (el caller ya dejó dicho
  qué pasó; `close` solo es la señal de "ya no hay más pasos que reportar").

**Contrato de salida**: ninguno relevante para el caller — esta skill no devuelve nada que
el flujo use para decidir. Es "fire and forget" desde el punto de vista de la orquestadora,
igual que loguear.

**Implementación por defecto (`pv-internal-progress-todowrite`):** en cada `action`,
traduce directamente a una llamada `TodoWrite` con la lista completa de items y sus
estados actuales (el propio harness exige mandar la lista entera en cada llamada, no un
delta) — mantiene el estado en memoria de la conversación, no en fichero: no necesita
leer/escribir nada en disco, la lista vive mientras dura la sesión, que es exactamente el
alcance que se busca (ver "Fuera de alcance").

**Qué NO hace esta skill:**

- No decide qué pasos existen ni cuántos — eso lo decide el caller (la orquestadora),
  igual que `pv-internal-tech-mermaid` no decide qué diagramas hacen falta.
- No persiste nada en disco ni sobrevive a la sesión — si se quiere eso, es el problema ya
  cubierto (para otro fin) por `08_agents-status-tracking.md`, no este.
- No es user-facing por narrativa: no reemplaza los `[INFO: ...]`/`[ASK: ...]` que ya
  existen en los diagramas — la checklist es un complemento visual pasivo, no un canal de
  comunicación con el usuario.

### 2. Configuración: `framework.skills.progress`

En `.claude/pv-context.json`, junto a `mockups`/`diagrams`. Estado por defecto tras
`pv-init` (campo ausente — sin checklist, ver más abajo):

```json
"framework": {
  "skills": {
    "mockups": "pv-internal-mockups-html",
    "diagrams": "pv-internal-tech-mermaid"
  },
  "_comments": {
    "skills.progress": "Opcional. Si se configura con un nombre de skill (p. ej. pv-internal-progress-todowrite), las skills pv-fix/pv-how/pv-do/pv-new publican una checklist de su avance en la interfaz durante el flujo. Ausente o vacio: comportamiento actual, sin checklist."
  }
}
```

Si el usuario activa la funcionalidad, queda así:

```json
"framework": {
  "skills": {
    "mockups": "pv-internal-mockups-html",
    "diagrams": "pv-internal-tech-mermaid",
    "progress": "pv-internal-progress-todowrite"
  }
}
```

**Default si el campo está ausente: sin checklist, comportamiento idéntico al actual.**
A diferencia de `mockups`/`diagrams` (piezas necesarias del flujo, con default activo),
`progress` es una mejora puramente cosmética y opcional — no genera contenido, no afecta
al resultado de ningún change. Por eso aquí se invierte el criterio: **ausencia o campo
vacío (`""`/`null`) = las orquestadoras no instancian ningún nodo `[PROGRESS: ...]` ni
invocan ninguna skill de progreso**, cero coste, cero diferencia respecto a como funciona
el framework hoy. Solo cuando el usuario configura explícitamente un nombre de skill en
`framework.skills.progress` se activa la instrumentación.

Esto es intencionadamente la única entrada de `framework.skills.*` con este criterio —
`mockups`/`diagrams` producen algo que el change necesita y por eso tienen un default
activo; `progress` no produce nada que el flujo dependa de tener, así que activarlo es un
opt-in, no un opt-out.

**Migración a Copilot**: se escribe `pv-internal-progress-copilot` implementando el mismo
contrato de entrada (sección 1) y se apunta `framework.skills.progress` a ella — cero
cambios en las 4 orquestadoras. Si no interesa la funcionalidad en el nuevo host, no hay
nada que hacer: simplemente no se configura el campo.

Añadir el campo también donde `pv-init` genera la plantilla inicial de `pv-context.json`
y, si existe, al schema JSON que valida el fichero (mismo punto abierto que ya deja sin
verificar `08_agents-status-tracking.md` para `staleTimeoutMinutes` — comprobar en
implementación, no asumir).

### 3. Puntos de invocación — en el diagrama, no en prosa suelta

Mismo criterio que ya fijó `08_agents-status-tracking.md` para sus nodos `[REPORT: fase]`:
la instrumentación real vive en los `workflow.*.md` (notación ya establecida:
`[Text]`/`[INFO: Text]`/`[ASK: Text]`/`{Text}`), no como prosa nueva en el `SKILL.md`. Se
añade un nodo `[PROGRESS: init]` al arrancar el flujo (justo después del check de
inicialización, `S0Ok -->|Yes|`) y un nodo `[PROGRESS: <id> in_progress]` /
`[PROGRESS: <id> completed]` alrededor de cada paso mayor ya existente en el diagrama —
sin crear pasos nuevos que no existieran, solo marcando los que ya hay.

**Listas dinámicas (ramas condicionales):** varios diagramas bifurcan pronto (fast-track
vs. no-trivial en `pv-fix`; extend-entry/todo-mode vs. flujo normal en `pv-new`). El
`init` se emite **una vez se sabe qué rama se sigue**, no antes — con la lista de pasos de
esa rama únicamente. No se listan por adelantado pasos de una rama que no se va a tomar.
Si a mitad de flujo aparece un paso condicional que sí aplica (p. ej. `pv-fix` paso 4.1
"definir datos", solo si el fix tiene datos estructurados), el caller puede añadirlo con
un segundo `init` que sustituye la lista (misma semántica "última lista gana" que ya usa
`TodoWrite` internamente) — no hace falta una `action` nueva para "añadir item".

**Inventario de nodos por skill** (mismo criterio de alcance que la tabla de
`08_agents-status-tracking.md` — orquestadoras con diagrama propio, no las
`pv-internal-*` hoja, que quedan cubiertas por el paso de su caller):

| Skill | Diagrama | Items sugeridos del `init` (rama principal) |
|---|---|---|
| `pv-fix` | `workflow.fix.md` | No-trivial: Analizar la petición, Documentar la intención, Generar representación visual, Validar con el usuario, Planificar (`pv-how`). Fast-track: Documentar, Aplicar hooks previos, Aplicar el cambio, Documentar lo aplicado, Mover a implemented. |
| `pv-how` | `workflow.how.md` | Validar consistencia de la entrada, Analizar causa técnica, Escribir plan.md, Evaluar riesgo, Confirmar implementación. |
| `pv-do` | `workflow.do.md` | Cargar hooks del proyecto, Implementar plan.md, Verificar, Actualizar documentación técnica, Mover a implemented. |
| `pv-new` | `workflow.new.md` | Entender la petición, Documentar la intención, Generar representación visual, Validar con el usuario, Encadenar pv-how (opcional). |

Estos son los pasos "mayores" (los que ya son nodos de primer nivel en cada diagrama), no
cada subpaso interno de un hook o de una `pv-internal-*` — mismo criterio de granularidad
que ya usó `08_agents-status-tracking.md` para no duplicar reporte a nivel de skill-hoja.

**`pv-internal-workflow`, `pv-internal-tech-analysis` y demás `pv-internal-*`:** no se
instrumentan aparte, por la misma razón exacta que en `08_agents-status-tracking.md`
sección 3 — cada una cae ya bajo un paso mayor que su caller marca `in_progress`.

**Cierre:** el nodo final de cada rama (`EndOK`, `End0`, etc.) dispara
`[PROGRESS: close]`. Un flujo que termina en un `[End: stopped]` temprano (p. ej. falta
`pv-init`) también cierra — no deja una checklist a medias colgada en pantalla sin
explicación; el propio `[INFO: ...]` que ya existe en ese nodo es la explicación.

### 4. Migrar a otro host (p. ej. Copilot)

Copilot (agent mode, VS Code) tiene su propio mecanismo nativo de todo-list en la UI,
equivalente en concepto a `TodoWrite` aunque con su propia forma de invocarlo. Migrar es
escribir `pv-internal-progress-copilot` traduciendo el mismo contrato de entrada
(sección 1: `action`/`items`/`itemId`/`status`) a lo que ese mecanismo nativo espere, y
apuntar `framework.skills.progress` a ella. Cero cambios en
`pv-fix`/`pv-how`/`pv-do`/`pv-new`: ya solo hablan con `[PROGRESS: ...]` a través de la
skill configurada, nunca con `TodoWrite` directamente.

## Fuera de alcance de esta primera versión

- Persistencia entre sesiones o cruce con otros agentes — eso es
  `08_agents-status-tracking.md`, un problema distinto y ya diseñado aparte.
- Progreso a nivel de subpaso dentro de un hook del proyecto (`stuff/hooks/**`) — son
  pasos del proyecto, no del framework; instrumentar eso es responsabilidad de quien
  escriba el hook, no de este plan.
- Cualquier UI propia fuera de lo que el harness ya renderiza para `TodoWrite` — no se
  construye un dashboard ni un fichero de estado.
- Instrumentar skills que no orquestan un flujo multi-paso (`pv-todo`, `pv-status`,
  `pv-init`, `pv-update`, `pv-version`) — mismo criterio de exclusión que ya aplicó
  `08_agents-status-tracking.md` a su propio catálogo de fases.

## Lista de tareas para la implementación

1. **Skill-hoja**: crear `.claude/skills/pv-internal-progress-todowrite/SKILL.md` con el
   contrato de entrada de la sección 1 (`action`/`items`/`itemId`/`status`), siguiendo el
   mismo formato de frontmatter y estructura que `pv-internal-tech-mermaid/SKILL.md`.
2. **Schema**: en `.claude/skills/pv-init/schema.json`, añadir `progress` dentro de
   `framework.skills.properties` (junto a `mockups`/`diagrams`, L96-113), **sin**
   `"default"` — a diferencia de esas dos, para que su ausencia no dispare ningún valor
   implícito. Descripción en el mismo estilo (`"OPTIONAL. Name of the skill that
   pv-new/pv-fix/pv-how/pv-do invoke, at each major step of their own flow, to report
   progress on a visible checklist. Not asked by pv-init, no default: if absent, no
   checklist is shown and the flow behaves exactly as without this field. The skill named
   here must fulfill the same input/output contract documented in
   pv-internal-progress-todowrite/SKILL.md (init/update/close actions) so it can be
   swapped for another mechanism (e.g. on a non-Claude-Code host) without touching
   pv-new/pv-fix/pv-how/pv-do."`).
3. **`pv-context.json`**: no se añade a la plantilla que genera `pv-init`
   (`scripts/scaffold-project.py`) ni se pregunta en `workflow.init.md` — sigue ausente
   tras un `pv-init` normal, coherente con "opt-in, no default". Sí se documenta como
   ejemplo comentado en `_comments` de los ficheros de ejemplo del propio schema (bloque
   `"examples"` L254-262) para que quien mire el schema sepa que existe sin que aparezca
   activado.
4. **Skill-hoja**: crear `.claude/skills/pv-internal-progress-todowrite/SKILL.md` con el
   contrato de entrada de la sección 1 (`action`/`items`/`itemId`/`status`), siguiendo el
   mismo formato de frontmatter y estructura que `pv-internal-tech-mermaid/SKILL.md`.
5. **Notación de diagramas** (`pv-doc/pv-design/pv-design.es.md` y `.en.md`): documentar
   `[PROGRESS: init]` / `[PROGRESS: <id> in_progress|completed]` / `[PROGRESS: close]`
   como una variante del nodo "paso interno" existente (`ID[Texto]`, sección "Cuatro tipos
   de nodo", L497-502) — no un quinto tipo de nodo nuevo, ya que sigue siendo la skill
   actuando sin hablar con el usuario. Aclarar que estos nodos solo se incluyen en el
   diagrama de una orquestadora si el proyecto tiene `framework.skills.progress`
   configurado; si no, el `workflow.*.md` no los lleva y el flujo no cambia. No toca la
   plantilla fija de leyenda (L504-512): esos nodos siguen siendo `[Texto]` a efectos de
   leyenda, solo con un prefijo `PROGRESS:` reconocible dentro del propio texto.
6. **Guía de usuario** (`pv-doc/pv-guide.es.md` y `.en.md`): añadir una mención breve,
   junto a donde ya se describe `framework.skills.mockups` (L210) y el resto de
   `framework.skills.*`, explicando que `framework.skills.progress` es opcional y, si se
   configura, hace que `pv-new`/`pv-fix`/`pv-how`/`pv-do` muestren una checklist de avance
   en la interfaz durante su ejecución — sin entrar en el detalle de implementación (eso
   vive en el `SKILL.md` de la skill-hoja).
7. **Instrumentar `pv-how`** (`workflow.how.md`): nodos `[PROGRESS: init]` tras `S0Ok`,
   más `in_progress`/`completed` en los 5 pasos mayores de la tabla de la sección 3, y
   `[PROGRESS: close]` en cada nodo `End*`. Actualizar también la prosa numerada de
   `pv-how/SKILL.md` si en algún punto describe el flujo de forma que quede inconsistente
   con los nodos nuevos (regla ya fijada en `pv-design.*.md`: el diagrama manda, la prosa
   se corrige para cuadrar).
8. **Instrumentar `pv-new`** (`workflow.new.md` + `SKILL.md` si aplica): mismo patrón, con
   `init` emitido después de resolver qué rama se sigue (`extend-entry`/`todo-mode`/flujo
   normal — tres listas distintas, una por rama).
9. **Instrumentar `pv-do`** (`workflow.do.md` + `SKILL.md` si aplica): mismo patrón, 5
   pasos mayores.
10. **Instrumentar `pv-fix`** (`workflow.fix.md` + `SKILL.md` si aplica): mismo patrón,
    dos listas distintas (no-trivial vs. fast-track) según la rama que tome el paso 2 del
    diagrama.
11. **Prueba manual de extremo a extremo**: con `framework.skills.progress` configurado,
    correr un `pv-fix` no-trivial y un fast-track, comprobando en la interfaz que la
    checklist aparece al arrancar, cada item pasa por `in_progress`→`completed` en el
    orden correcto, y se cierra limpia al terminar (o al parar temprano por falta de
    `pv-init`). Repetir sin el campo configurado y comprobar que no aparece checklist ni
    cambia nada más del comportamiento.

## Decisiones ya confirmadas en el diseño

- Se reutiliza el patrón `framework.skills.*` ya existente (mockups/diagramas) en vez de
  inventar un mecanismo de aislamiento nuevo — es el patrón que el propio framework ya usa
  para este problema exacto (sustituibilidad).
- La lista es por sesión/conversación, no persistida — cualquier necesidad de
  persistencia entre sesiones es un problema distinto, ya cubierto por
  `08_agents-status-tracking.md`.
- Granularidad: solo pasos mayores de cada diagrama (nodos de primer nivel), nunca
  subpasos de hooks del proyecto ni de `pv-internal-*` invocadas dentro de un paso ya
  cubierto.
