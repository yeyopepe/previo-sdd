Orden pensado para avanzar por fases; dentro de cada fase las tareas son mayormente
secuenciales.

## Fase 1 — El asset (núcleo)

**Estado: completada** (2026-09-24), con varias mejoras sobre el diseño original surgidas
durante la verificación manual en el sandbox — ver notas en T1-T3:

- [x] **T1.** Crear `.claude/skills/pv-internal-mockups-html/assets/mockup-annotations.html`:
  marcador `<!-- mnoteqz7k-framework v1 -->` + `<style id="mnoteqz7k-styles">` +
  `<script id="mnoteqz7k-runtime">` (IIFE, sin dependencias) +
  `<script type="application/json" id="mnoteqz7k-data">[]</script>` + cuerpo de demo para abrirlo
  suelto. Referencia de diseño: `mockup_catalog.html` y `mockup_examples.html` de esta
  carpeta (definen ya los 3 componentes, los 2 colores `#f5a623` / `#2c7dd8`, el namespace
  `.mnoteqz7k-*`, el mini-menú del `➕`, el contador ámbar, el panel de generales y el estado
  "desvinculada").
- [x] **T2.** Implementar `#mnoteqz7k-runtime`:
  - Barra `#mnoteqz7k-bar` (`position:absolute`, solo iconos `➕ 👁 💾` + contador,
    `title`/`aria-label`, enfocable por teclado); se desplaza junto al cursor al seleccionar,
    vuelve a una esquina sin selección.
  - Selección por **clic simple** en cualquier nodo → `.mnoteqz7k-sel` (contorno azul); cálculo
    de **selector robusto** (`#id`; si no, ruta `nth-of-type` desde `body`). **El recorrido
    del DOM ignora `#mnoteqz7k-bar`, `#mnoteqz7k-menu`, `#mnoteqz7k-panel`, `.mnoteqz7k-card` y `#mnoteqz7k-data`**
    (ni seleccionables ni cuentan en la ruta). `Esc` / clic fuera deselecciona.
  - `➕`: sin selección → **nota general** directa; con selección → mini-menú `#mnoteqz7k-menu`
    ("Nota en `<selector>`" / "Nota general").
  - Tarjeta `.mnoteqz7k-card` (vinculada/general, lectura/edición con `<textarea>`, pie
    Editar/Guardar/Eliminar con **confirmación de borrado**, `‹ ›` entre notas del mismo
    elemento). **Sin ningún control para cerrar una nota** — cerrar es un juicio exclusivo de
    `pv-internal-mockups-html`, nunca del framework en el navegador.
  - Contador ámbar `.mnoteqz7k-count` en la esquina del elemento con notas vinculadas (**solo con
    anotaciones visibles**); al pulsar el elemento se abre su tarjeta al lado compartiendo el
    contorno ámbar `.mnoteqz7k-linked`.
  - Panel `#mnoteqz7k-panel` de notas generales acoplado a una esquina; estado **"desvinculada"**
    (borde rojo, conserva el texto) para notas vinculadas cuyo selector ya no resuelve.
  - **Estado `open`/`closed` de la nota**: toda nota nace `state: "open"` al crearse. El
    navegador nunca escribe `"closed"`. Una nota `closed` (escrita ahí solo por
    `pv-internal-mockups-html` vía `ensure-closed`) se muestra atenuada (gris/tachado/✓) y deja
    de contar en el contador ámbar del elemento y en el total de la barra, pero permanece en
    `#mnoteqz7k-data` hasta que el reviewer la borre explícitamente con 🗑.
  - `👁`: togglea `mnoteqz7k-hidden` en `<html>`; estado en `localStorage` por
    `location.pathname`.
  - `💾`: serializa `[{id, kind:"linked"|"general", selector, text, createdAt, state:"open"}]`
    (siempre `"open"` desde el navegador), escribe/actualiza `#mnoteqz7k-data` en el DOM, descarga
    un Blob de `document.documentElement.outerHTML` con **el mismo nombre de archivo**.
  - `#mnoteqz7k-toast`: barra fina fija abajo, se muestra al pulsar `💾` con
    "Guardado. Sustituye el original en: `<ruta completa>`" — ruta de `location.pathname`
    decodificado (coincide con el disco porque siempre se abre como `file://`), botón 📋 que
    copia la ruta con `navigator.clipboard.writeText` (no-op silencioso si la API no existe),
    autodesvanece ~6s o al clic (la descarga en `file://` nunca sobrescribe el original sola).
  - `💾` con `try/catch`: si falla la descarga, `#mnoteqz7k-toast.error` (fondo rojo, **sin
    autodesvanecer**) con "No se han guardado tus cambios. La descarga falló — copia el HTML
    manualmente o inténtalo con otro navegador."
  - Al cargar: lee `#mnoteqz7k-data` si existe y rehidrata contadores, panel y estado.
  - Degradación sin JS: mockup intacto, sin anotaciones.
- [x] **T3.** Verificación standalone del asset ([`PLAN.md`](PLAN.md) Verification §1): abrir
  en navegador — barra visible, nota general nace `state: "open"`, editar/borrar, Save
  descarga, reabrir → la nota persiste vía `#mnoteqz7k-data` con su estado intacto. Confirmar que
  la UI no ofrece ningún control para cerrar una nota.

  **Mejoras surgidas durante la verificación manual, no contempladas en el diseño original**:
  - **Namespace anti-colisión**: todo el namespace pasó de `mnote-*` a `mnoteqz7k-*` (sufijo
    corto y arbitrario) para hacer improbable una colisión accidental con el naming propio de
    un mockup real — importa porque el ID collision guard (Fase 2) depende de distinguir
    "framework ya incrustado" de "elemento sin relación que coincide de nombre por casualidad".
  - **Panel de notas vinculadas** (nuevo, no estaba en el diseño original): además del panel de
    generales (siempre visible, colapsable, expandido por defecto), un segundo panel análogo
    listando las notas vinculadas (colapsado por defecto); clicar un ítem abre esa nota en su
    posición real. Ambos paneles quedan siempre visibles — el toggle `👁` solo oculta
    badges/contornos/tarjetas sobre el propio mockup, nunca los paneles-lista.
  - **Badges fuera del árbol del mockup**: el contador ámbar dejó de insertarse dentro del
    elemento anotado (fallaba silenciosamente en elementos "replaced" como `<input>`/checkbox,
    que no admiten hijos visuales) — ahora es `position:fixed`, vive en `document.body`, y se
    reposiciona en un loop continuo de `requestAnimationFrame` (no solo en scroll/resize) para
    seguir a elementos que se mueven por drag-and-drop, animaciones CSS, o cualquier reposición
    ajena a eventos de ventana.
  - **Selección en fase de captura**: el listener de selección de `onDocumentClick` pasó a
    `capture:true` para poder seleccionar un elemento del mockup aunque su propio handler haga
    `stopPropagation()` en burbuja (p. ej. un dropdown decorativo) — antes ese caso bloqueaba
    la selección por completo.
  - **Guardado vía File System Access API** (`showSaveFilePicker`), con fallback automático a
    la descarga por Blob del diseño original si el navegador no la soporta o el usuario
    cancela: abre el diálogo nativo "Guardar como", permitiendo elegir/sobrescribir la ruta
    real en vez de caer siempre en Descargas. Un toast previo (anclado junto al botón 💾, con
    la carpeta a elegir copiable al portapapeles y el nombre exacto del archivo a confirmar)
    antecede el picker, ya que éste requiere un gesto de usuario directo.
  - **Serialización limpia al guardar**: `serializeClean()` clona el documento y retira toda la
    UI runtime (barra, menú, tarjetas, paneles, toast, badges, contornos, watermark) antes de
    generar el HTML a guardar — el diseño original serializaba `outerHTML` tal cual, lo que
    duplicaba la barra (fosilizada + recreada por `init()`) al reabrir un archivo ya guardado.
  - **Marca de agua** "Developed with Previo", fija en la esquina inferior derecha, enlazando
    al repo (`github.com/yeyopepe/previo-sdd`); se recrea en cada carga (nunca persistida en
    `#mnoteqz7k-data` ni en el HTML guardado) para evitar duplicados.

## Fase 2 — `pv-internal-mockups-html/SKILL.md`

**Estado: completada** (2026-09-24). `SKILL.md` reescrito: regla plugin-isolation (T3.1),
inputs `style_context`/`language` sustituyendo la resolución propia del style bible (T3.2),
inventario de ficheros (T4), excepción a "no JavaScript" para el framework embebido (T5),
regla "Embed the annotation framework" (T6), los tres sub-casos de `create`/`edit` con el ID
collision guard (T7/T7.3), las nuevas acciones `ensure-closed` (T7.1) y `describe` (T7.2), la
excepción de interacción directa con el usuario (T7.4), y la nota de versionado (T8).
`description` del frontmatter actualizada para reflejar las 4 acciones.

- [x] **T3.1.** Regla **plugin-isolation** (nueva, al principio de `SKILL.md`): la skill es un
  plugin autocontenido — copiar solo su carpeta a otro repo debe permitir crear/editar/gestionar
  `design_*.html` al 100%. Nunca resuelve su propio contexto desde disco ni desde
  `pv-context.json`; todo lo que necesite lo pide como input, y su ausencia degrada a un
  comportamiento por defecto en vez de ir a buscarlo.
- [x] **T3.2.** Reescribir la regla del style bible (líneas 35-56 del `SKILL.md` real):
  **eliminar** la llamada a
  `python .claude/skills/pv-init/scripts/resolve-path.py --what styleBibleDocDir` y la lectura
  directa de `INDEX.md`/ficheros de `styleBibleDocDir` — dependencia dura fuera de la propia
  carpeta de la skill. Nuevo input opcional `style_context` (texto plano, ya resuelto por el
  caller): si viene, reusar sus valores tal cual; si no viene (o vacío), estilo neutro +
  comentario `<!-- No documented visual identity for <element>; neutral placeholder styling. -->`
  como ya hace hoy para el caso "nada documentado". El manejo de exit codes de `resolve-path.py`
  (2→`/pv-init`, 3|4→`/pv-update`) deja de ser responsabilidad de esta skill.
- [x] **T4.** Añadir un inventario de ficheros (sección nueva o en el párrafo de intro —
  hoy no existe) mencionando `assets/mockup-annotations.html`.
- [x] **T5.** Enmendar la regla "no JavaScript" (`SKILL.md` línea 65 real, no 52/53 — la
  reescritura por subcarpetas desalineó de nuevo las referencias): excepción explícita y
  acotada — el único JS permitido es el framework de anotaciones copiado verbatim del asset;
  el mockup no contiene ningún otro JS.
- [x] **T6.** Nueva regla **"Embed the annotation framework"** en "Rules for each mockup":
  tras escribir/editar el markup propio, copiar **verbatim** marcador +
  `<style id="mnoteqz7k-styles">` antes de `</head>` y `<script id="mnoteqz7k-runtime">` antes de
  `</body>`; añadir `#mnoteqz7k-data` vacío si no existe. Redacción espejo de `pv-init/SKILL.md`
  línea 142 ("copied as-is without modifying a single line of it"). Nunca
  reescribir/resumir/"mejorar".
- [x] **T7.** Especificar el comportamiento de `action: edit` (step 1 de "Steps", hoy solo
  "preserve the rest of the file") con los 3 sub-casos de Flujo A:
  1. sin bloques framework → añadirlos, igual que `create`;
  2. con bloques (contenido reconocible, ver T7.3) y `vN` del asset **no más nuevo** que el del
     archivo → editar el markup propio sin tocar `mnoteqz7k-*` **ni `#mnoteqz7k-data`** — un `edit`
     plano nunca cambia el estado ni el contenido de ninguna nota, eso es solo cosa de
     `ensure-closed` (T7.1);
  3. `vN` del asset **más nuevo** → reemplazar solo los 2 bloques framework, conservando
     `#mnoteqz7k-data` verbatim.
- [x] **T7.1.** Nueva acción **`action: ensure-closed`** (sustituye por completo al diseño
  anterior de `read-annotations` + `edit`-por-nota): recibe una lista de rutas `design_*.html`
  bajo `mockups/` (las que el caller va a (re-)presentar, o — para `pv-how` — todas las de la
  entrada). Por cada ruta con framework reconocible:
  - parsea `#mnoteqz7k-data` internamente;
  - si no hay ninguna nota `state: "open"` (o no hay notas), no hace nada en esa ruta;
  - por cada nota `open`: si puede aplicar el cambio pedido sin ambigüedad, lo aplica
    directamente al markup propio del mockup (mismo mecanismo que un `edit` interno, decidido
    por la propia skill — sin ida y vuelta al caller) y marca esa nota `state: "closed"` en
    `#mnoteqz7k-data` (nada más del bloque cambia);
  - si una nota es ambigua, **la skill pregunta al usuario directamente** (T7.4) antes de
    aplicar nada para esa nota concreta; con la respuesta, aplica y cierra igual;
  - una nota "desvinculada" (selector que ya no resuelve) se trata como nota general a estos
    efectos;
  - una ruta sin framework incrustado se salta sin más (nunca error, nunca bloquea las demás).
  - Devuelve **OK** + resumen en texto plano de qué se cambió por nota (sin selectores ni JSON
    crudo) solo cuando cada ruta dada queda sin ninguna nota `open`. **Es la única vía por la
    que cualquier caller se entera de o resuelve anotaciones** — ningún otro skill abre
    `#mnoteqz7k-data` ni conoce el estado `open`/`closed` de una nota.
- [x] **T7.2.** Nueva acción **`action: describe`** (solo lectura, nunca toca `#mnoteqz7k-data` ni
  el estado de ninguna nota): recibe una lista de rutas `design_*.html` bajo `mockups/` y,
  opcionalmente, qué elementos/áreas interesan; lee el markup propio (algo que solo esta skill
  hace directamente) y devuelve una descripción en texto plano del layout/estilo/iconografía
  pedido — suficiente para que un caller como `pv-how` la use como referencia visual, sin
  exponer HTML/CSS/SVG crudo ni los bloques `mnoteqz7k-*`. **Es la única vía por la que cualquier
  caller accede al contenido visual de un `design_*.html`** — ningún caller hace `Read` sobre
  uno de ellos. `navigation_*.md`/`data_*.md` quedan fuera de esta acción: viven fuera de
  `mockups/`, no son responsabilidad de esta skill, y siguen leyéndose con `Read` directo.
- [x] **T7.3.** ID collision guard: el check "¿el archivo ya tiene el framework?" debe verificar
  que el contenido del `id="mnoteqz7k-runtime"` (o `-styles`/`-data`) es reconocible como el asset
  (marcador/cabecera), no solo que el id exista. Si hay un id `mnoteqz7k-*` con contenido distinto
  (mockup viejo previo a este plan que coincide por casualidad), **detener y devolver el
  conflicto al caller sin escribir nada** — nunca pisarlo ni tratarlo como "sin framework".
- [x] **T7.4.** Capacidad de interacción directa con el usuario (excepción única en todo el
  framework `pv-internal-*`, que hoy son todos mudos): documentar explícitamente en `SKILL.md`
  que `ensure-closed` puede preguntar al usuario en el mismo turno cuando una nota es ambigua,
  justificado por el objetivo de plugin-isolation (delegar la pregunta al caller rompería la
  encapsulación que motiva todo este rediseño).
- [x] **T8.** Nota: el marcador `vN` es independiente de `metadata.version`; los bumps de
  versión del framework los gestiona `/dev-generate-version`.

## Fase 3 — Cierre de ciclo en `pv-new` / `pv-fix` / `extend-entry.md`

**Estado: completada** (2026-09-24). `pv-new/SKILL.md` (step 3 pasa `style_context`, step 4
invoca `ensure-closed` antes de presentar, nota final actualizada), `pv-fix/SKILL.md` (mismos
tres puntos), `pv-new/extend-entry.md` (step 4 pasa `style_context`, step 6 invoca
`ensure-closed` sobre lo tocado por la extensión + el resto de `mockups/` de la entrada),
`workflow.new.md`/`workflow.fix.md` (rama `ensure-closed` añadida a ambos diagramas), y
`pv-do/SKILL.md` (tercer caller, sustituida la mención directa de `design_*` por `action:
describe`).

**Regla de encapsulación**: ningún caller lee, parsea o escribe `#mnoteqz7k-data`, ni menciona
`mnoteqz7k-*`/selectores/JSON/estado `open`/`closed` en su propia prosa o lógica — eso es concern
exclusivo de `pv-internal-mockups-html` (T7.1/T7.2). El caller solo invoca `ensure-closed` y
espera su OK/resumen.

Párrafo común a anteponer en cada paso de validación visual: *"Invocar la acción
`ensure-closed` de la skill de mockups configurada sobre los `design_*.html` a presentar. La
skill resuelve internamente cualquier anotación pendiente (`open`) — aplicando el cambio
directamente y preguntando ella misma al reviewer si una nota es ambigua — y devuelve cuando ya
no queda ninguna anotación `open` en esos archivos. Resumir en la respuesta lo que la skill
reporta haber cambiado, si algo. Después presentar los mockups actualizados como de
costumbre."*

- [x] **T8.1.** `pv-new/SKILL.md` step 3 (invocación de la skill de mockups): pasar
  `style_context` extraído del contexto que step 1 ya obtuvo de `pv-internal-tech-analysis` —
  si no hay nada de estilo relevante, no pasar nada (la skill ya asume neutro por su cuenta).
- [x] **T8.2.** `pv-fix/SKILL.md` step 4 (invocación de la skill de mockups): mismo tweak que
  T8.1.
- [x] **T8.3.** `pv-new/extend-entry.md` step 4 (invocación de la skill de mockups): mismo
  tweak que T8.1.
- [x] **T9.** `pv-new/SKILL.md` step 4 (línea 112): anteponer el párrafo antes de "present
  them to the user".
- [x] **T10.** `pv-new/SKILL.md` nota final "who writes what" (línea 125): resolver anotaciones
  pendientes se hace exclusivamente vía `action: ensure-closed` de la skill de mockups.
- [x] **T11.** `pv-fix/SKILL.md` step 5 (línea 106): mismo párrafo anteponer.
- [x] **T12.** `pv-fix/SKILL.md` nota final (línea 114): mismo tweak que T10.
- [x] **T13.** `pv-new/extend-entry.md` step 6 (línea 10): mismo párrafo, acotado a los
  `design_*.html` tocados por la extensión + el resto de `design_*.html` ya en `mockups/` de
  la entrada (una anotación pendiente en un archivo no tocado por esta vuelta debe seguir
  resolviéndose).
- [x] **T14.** Revisar `pv-new/workflow.new.md` y `pv-fix/workflow.fix.md`: añadir la rama
  `ensure-closed` al diagrama (Flujo B) redactada en términos de las acciones de la skill,
  nunca `#mnoteqz7k-data`/estado, o dejar constancia explícita de que es demasiado fina para
  diagramar. Ambos `SKILL.md` declaran que el diagrama manda sobre la prosa.
- [x] **T14.5.** `pv-do/SKILL.md` línea 121 (paso de actualización de
  `docs.tech.styleBibleDocDir`): hoy pasa "any `design_*` mockups this entry has" como parte
  del contexto que entrega a `pv-internal-doc-style` — un tercer caller de mockups no cubierto
  por el diseño original de este plan (hallazgo de `dev-analysis`, 2026-09-24). Sustituir esa
  referencia por una invocación a `action: describe` de la skill de mockups configurada, pidiendo
  la descripción de los elementos relevantes al área de estilo tocada, en vez de mencionar o
  pasar los ficheros `design_*` directamente. `pv-do` no invoca `ensure-closed` (no valida
  visualmente con el usuario ni presenta mockups) — solo `describe`, que es de solo lectura.

## Fase 3.5 — Gate de entrada de `pv-how`

**Estado: completada** (2026-09-24). Nuevo step 1.05 en `pv-how/SKILL.md` (gate `ensure-closed`
antes de 1.1), step 1.1 reescrito (visuales de `mockups/` vía `describe`, `navigation_*.md`/
`data_*.md` sin cambios), el punto 2 de step 3 reescrito (referencia visual vía `describe` en
vez de `Read` directo), y `workflow.how.md` con el nuevo nodo de gate (`S105Check`/
`S105Ensure`) entre encontrar la entrada y el chequeo de consistencia.

`pv-how` no puede analizar una entrada sin el OK de la skill de mockups — precondición dura,
no una optimización. Se aplica siempre, invoque quien invoque a `pv-how` y haya pasado o no por
`pv-new`/`pv-fix` en esta misma sesión.

- [x] **T14.1.** `pv-how/SKILL.md` — nuevo **step 1.05**, entre step 1 ("Identify the
  change/fix", que resuelve `{xxxx}`) y step 1.1 ("Validate the change's documents before
  analyzing"): *"Si la entrada tiene algún `design_*.html` bajo `mockups/`, invocar
  `action: ensure-closed` de la skill de mockups configurada sobre todos ellos. Esperar su OK
  antes de continuar — no leer, describir ni usar de ningún modo ningún `design_*.html` de esta
  entrada (incluido el propio chequeo de consistencia del step 1.1) hasta que devuelva OK."* La
  posición importa: **step 1.1 ya hace hoy `Read` directo sobre `mockups/` y sobre
  `navigation_*.md`/`data_*.md`** (para el chequeo de consistencia contra `description.md`),
  antes incluso de llegar a step 2 — así que el gate tiene que ir antes de 1.1, no solo antes
  de 2. El gate solo cubre `mockups/`: `navigation_*.md`/`data_*.md` no pasan por
  `ensure-closed` ni `describe`, siguen con `Read` directo como hoy.
- [x] **T14.2.** Reescribir `pv-how/SKILL.md` step 1.1 (el chequeo de consistencia, línea 80
  real): sustituir la lectura de `design_*.html` bajo `mockups/` por una invocación a
  `action: describe` de la skill de mockups para los elementos/áreas relevantes al chequeo —
  la lectura de `navigation_*.md`/`data_*.md` sueltos en la raíz de la entrada no cambia, sigue
  siendo `Read` directo; la lógica del chequeo (comparar contra `description.md`) tampoco
  cambia, solo la fuente de los hechos visuales de `mockups/`.
- [x] **T14.3.** Reescribir `pv-how/SKILL.md` step 2 (hoy: *"open them, but treat them only as
  visual reference"*, `Read` directo sobre `mockups/`): invocar `action: describe` para los
  elementos que necesita como referencia visual, y construir su entendimiento a partir de esa
  descripción en vez de abrir el archivo.
- [x] **T14.4.** Revisar `pv-how/workflow.how.md`: añadir el nuevo nodo de gate (`ensure-closed`
  antes de 1.1) al diagrama (Flujo C), redactado en términos de la acción de la skill, nunca
  `#mnoteqz7k-data`/estado, o dejar constancia explícita de que es demasiado fino para diagramar.
  `pv-how/SKILL.md` también declara que el diagrama manda sobre la prosa.

## Fase 4 — Verificación integral

**Estado: completada** (2026-09-24). T15-T17.3 corridos sobre `sandbox-test1/previo-sdd/changes/
inProgress/00196/` (splice real en `design_bloc_notas_vista.html`, dry-run de la skill en
`design_verify-t16-widget.html` — borrado tras las pruebas, contrato `ensure-closed`/`describe`
verificado con notas reales incluyendo el caso de ambigüedad, que preguntó al usuario en el
propio turno). T18-T18.2 corridos sobre una copia desechable `00197` (para no ensuciar `00196`):
ciclo `pv-new`→`ensure-closed`, gate de `pv-how` en step 1.05 (confirmado que bloquea ante una
re-anotación posterior a `pv-new` y no confía en la validación anterior), y `pv-do` sin fugas de
`design_*`/`mnoteqz7k-*` en su propia prosa hacia `pv-internal-doc-style`. T19 confirmado con una
instalación real a un directorio scratch. T20: los tres `workflow.*.md` ya reflejan las nuevas
ramas; el único punto sin nodo propio (referencia visual dentro del step 3 de `pv-how`) ya era
demasiado fino para diagramar antes de este plan, sin cambio de criterio. `00197` queda en el
sandbox como registro de la prueba; bórrala si prefieres no conservarla.

- [x] **T15.** Embebido en mockup real ([`PLAN.md`](PLAN.md) Verification §2): splice de los 2
  bloques en `sandbox-test1\previo-sdd\changes\inProgress\00196\mockups\design_bloc_notas_vista.html`
  y recorrer todos los sub-puntos: clic → contorno azul + barra al cursor, `➕` mini-menú,
  nota general directa, contador ámbar, tarjeta compartiendo contorno, `‹ ›`, toggle `👁` +
  recarga (localStorage), CSS del mockup intacto con anotaciones ocultas, Save + reabrir →
  rehidratan general + vinculada (ambas `state: "open"`), y **clic en la barra/tarjeta/panel no
  selecciona nada del mockup ni entra en la ruta `nth-of-type`**. Confirmar que no hay ningún
  control de UI para cerrar una nota.
- [x] **T16.** Skill dry-run (§3): invocar `pv-internal-mockups-html` vía `pv-new` en un
  cambio visual de prueba en sandbox; confirmar que el `design_*.html` generado contiene
  `id="mnoteqz7k-styles"`, `id="mnoteqz7k-runtime"` y `<!-- mnoteqz7k-framework v1 -->` **byte-idénticos**
  a los bloques del asset.
- [x] **T16.1.** Aislamiento de plugin (§3.1): grep de `pv-internal-mockups-html/SKILL.md` por
  `resolve-path.py` y `pv-context.json` — ninguno debe aparecer tras la reescritura. Invocar la
  skill directamente con `action: create` sin `style_context`; confirmar estilo neutro +
  comentario placeholder, sin tocar disco fuera de `assets/` y la carpeta destino. Reinvocar con
  `style_context` y confirmar que reusa esos valores en vez del neutro.
- [x] **T17.** Edit plano no toca notas (§4): añadir un `#mnoteqz7k-data` falso con 2 notas `open`,
  re-invocar con `action: edit` (no `ensure-closed`); confirmar que `#mnoteqz7k-data` y el `state`
  de cada nota sobreviven completamente intactos, y los bloques framework quedan intactos.
- [x] **T17.1.** Contrato `ensure-closed` — resolución (§4.1): con ese mismo `#mnoteqz7k-data` (2
  notas `open`, ambas resolubles sin ambigüedad), invocar `action: ensure-closed`; confirmar que
  aplica ambos cambios al markup propio, pone `state: "closed"` en ambas notas (nada más del
  bloque cambia), y devuelve OK con resumen en texto plano sin selectores ni JSON crudo.
  Reinvocar `ensure-closed` sobre el archivo ya cerrado; confirmar que es no-op (OK inmediato).
  Confirmar que una ruta sin framework se salta sin error.
- [x] **T17.2.** Contrato `ensure-closed` — ambigüedad (§4.2): añadir una nota `open` con texto
  genuinamente ambiguo ("arregla esto"); invocar `ensure-closed` y confirmar que la skill
  pregunta directamente al usuario (no al caller) antes de aplicar nada para esa nota, y la
  cierra tras la respuesta.
- [x] **T17.3.** Contrato `describe` (§4.3): invocar `action: describe` sobre un `design_*.html`
  real preguntando por un par de elementos; confirmar que la respuesta es texto plano
  describiendo layout/estilo/iconografía, sin HTML/CSS/SVG crudo ni internals `mnoteqz7k-*`, y que
  nunca toca `#mnoteqz7k-data` ni el estado de ninguna nota.
- [x] **T18.** Cierre de ciclo — check de encapsulación en `pv-new` (§5): `design_*.html` con
  `#mnoteqz7k-data` (una nota vinculada `open` "make this wider", una general `open`); correr la
  ruta extend/validate de `pv-new`; confirmar que Claude solo invoca `ensure-closed` — grepear
  las tool calls y la propia prosa del turno por `#mnoteqz7k-data`/`mnoteqz7k-`/`open`/`closed` para
  confirmar que `pv-new` nunca los menciona — y que ambas notas quedan `closed` internamente.
- [x] **T18.1.** Gate de `pv-how` (§5.1): sobre esa misma entrada ya cerrada, invocar `pv-how`;
  confirmar que llama a `ensure-closed` de nuevo como su propio step 1.05 antes de 1.1 (no
  asume que la llamada anterior de `pv-new` siga siendo válida), recibe OK inmediato, y que ni
  el step 1.1 ni el step 2 hacen `Read` sobre ningún `design_*.html` de `mockups/` — ambos pasan
  por `describe`. Después añadir una nota `open` nueva directamente a `#mnoteqz7k-data` (simulando
  que el usuario volvió a anotar entre que `pv-new` terminó y `pv-how` corrió) y reinvocar
  `pv-how`; confirmar que se bloquea en 1.05 hasta que `ensure-closed` la resuelve, y nunca
  llega a step 1.1/2/3 antes de eso.
- [x] **T18.2.** `pv-do` no referencia `design_*` directamente (hallazgo `dev-analysis`
  2026-09-24, resuelto en T14.5): confirmar que `pv-do/SKILL.md` línea 121 invoca
  `action: describe` de la skill de mockups en vez de mencionar/pasar ficheros `design_*`
  como contexto a `pv-internal-doc-style`; correr el paso de actualización de
  `docs.tech.styleBibleDocDir` de `pv-do` sobre una entrada con mockups y grepear la respuesta
  del turno por `design_*`/`mnoteqz7k-`/`#mnoteqz7k-data` para confirmar que `pv-do` nunca los
  menciona directamente.
- [ ] **T19.** Propagación en instalación (§6): correr `install.sh` / `install.ps1` a un dir
  scratch (o inspeccionar el bucle de copia, `install.ps1` ~línea 50) y confirmar que
  `.claude/skills/pv-internal-mockups-html/assets/mockup-annotations.html` aterriza en
  destino. Confirmar que `pv-update` no necesita cambios.
- [x] **T20.** Consistencia prosa↔diagrama (§7): diff de `pv-new`/`pv-fix`/`extend-entry.md`/
  `pv-how` contra `workflow.new.md` / `workflow.fix.md` / `workflow.how.md` (los tres ya
  reflejan la convención `mockups/design_*.html` — partir de ese estado real, no de una versión
  sin subcarpeta); las ramas `ensure-closed`/`describe` (redactadas en términos de las acciones
  de la skill, nunca `#mnoteqz7k-data`/estado) deben estar en cada diagrama o marcadas como
  demasiado finas, sin desacuerdo silencioso.

## Fase 5 — Cierre

- [ ] **T21.** Ejecutar el flujo normal `/dev-generate-version`
  (`tools/set-skill-versions.py` sube todos los `SKILL.md`; `dev-changelog` regenera
  `.claude/pv-changelog.*.md` desde el git diff). Sin trabajo manual de changelog ni de
  versión.
