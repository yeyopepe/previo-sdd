# TASKS — Annotation framework embedded into every HTML mockup

Lista de implementación derivada de [`PLAN.md`](PLAN.md). Orden pensado para avanzar por
fases; dentro de cada fase las tareas son mayormente secuenciales.

## Fase 1 — El asset (núcleo)

- [ ] **T1.** Crear `.claude/skills/pv-internal-mockups-html/assets/mockup-annotations.html`:
  marcador `<!-- mnote-framework v1 -->` + `<style id="mnote-styles">` +
  `<script id="mnote-runtime">` (IIFE, sin dependencias) +
  `<script type="application/json" id="mnote-data">[]</script>` + cuerpo de demo para abrirlo
  suelto. Referencia de diseño: `mockup_catalog.html` y `mockup_examples.html` de esta
  carpeta (definen ya los 3 componentes, los 2 colores `#f5a623` / `#2c7dd8`, el namespace
  `.mnote-*`, el mini-menú del `➕`, el contador ámbar, el panel de generales y el estado
  "desvinculada").
- [ ] **T2.** Implementar `#mnote-runtime`:
  - Barra `#mnote-bar` (`position:absolute`, solo iconos `➕ 👁 💾` + contador,
    `title`/`aria-label`, enfocable por teclado); se desplaza junto al cursor al seleccionar,
    vuelve a una esquina sin selección.
  - Selección por **clic simple** en cualquier nodo → `.mnote-sel` (contorno azul); cálculo
    de **selector robusto** (`#id`; si no, ruta `nth-of-type` desde `body`). **El recorrido
    del DOM ignora `#mnote-bar`, `#mnote-menu`, `#mnote-panel`, `.mnote-card` y `#mnote-data`**
    (ni seleccionables ni cuentan en la ruta). `Esc` / clic fuera deselecciona.
  - `➕`: sin selección → **nota general** directa; con selección → mini-menú `#mnote-menu`
    ("Nota en `<selector>`" / "Nota general").
  - Tarjeta `.mnote-card` (vinculada/general, lectura/edición con `<textarea>`, pie
    Editar/Guardar/Eliminar con **confirmación de borrado**, `‹ ›` entre notas del mismo
    elemento).
  - Contador ámbar `.mnote-count` en la esquina del elemento con notas vinculadas (**solo con
    anotaciones visibles**); al pulsar el elemento se abre su tarjeta al lado compartiendo el
    contorno ámbar `.mnote-linked`.
  - Panel `#mnote-panel` de notas generales acoplado a una esquina; estado **"desvinculada"**
    (borde rojo, conserva el texto) para notas vinculadas cuyo selector ya no resuelve.
  - `👁`: togglea `mnote-hidden` en `<html>`; estado en `localStorage` por
    `location.pathname`.
  - `💾`: serializa `[{id, kind:"linked"|"general", selector, text, createdAt}]`,
    escribe/actualiza `#mnote-data` en el DOM, descarga un Blob de
    `document.documentElement.outerHTML` con **el mismo nombre de archivo**.
  - Al cargar: lee `#mnote-data` si existe y rehidrata contadores, panel y estado.
  - Degradación sin JS: mockup intacto, sin anotaciones.
- [ ] **T3.** Verificación standalone del asset ([`PLAN.md`](PLAN.md) Verification §1): abrir
  en navegador — barra visible, nota general, editar/borrar, Save descarga, reabrir → la nota
  persiste vía `#mnote-data`.

## Fase 2 — `pv-internal-mockups-html/SKILL.md`

- [ ] **T4.** Añadir un inventario de ficheros (sección nueva o en el párrafo de intro —
  hoy no existe) mencionando `assets/mockup-annotations.html`.
- [ ] **T5.** Enmendar la regla "no JavaScript" (`SKILL.md` ~línea 52): excepción explícita y
  acotada — el único JS permitido es el framework de anotaciones copiado verbatim del asset;
  el mockup no contiene ningún otro JS.
- [ ] **T6.** Nueva regla **"Embed the annotation framework"** en "Rules for each mockup":
  tras escribir/editar el markup propio, copiar **verbatim** marcador +
  `<style id="mnote-styles">` antes de `</head>` y `<script id="mnote-runtime">` antes de
  `</body>`; añadir `#mnote-data` vacío si no existe. Redacción espejo de `pv-init/SKILL.md`
  línea ~141 ("copied as-is without modifying a single line of it"). Nunca
  reescribir/resumir/"mejorar".
- [ ] **T7.** Especificar el comportamiento de `action: edit` (step 1 de "Steps", hoy solo
  "preserve the rest of the file") con los 3 sub-casos de Flujo A:
  1. sin bloques framework → añadirlos, igual que `create`;
  2. con bloques y `vN` del asset **no más nuevo** que el del archivo → editar el markup
     propio sin tocar `mnote-*` ni `#mnote-data`;
  3. `vN` del asset **más nuevo** → reemplazar solo los 2 bloques framework, conservando
     `#mnote-data` verbatim.
- [ ] **T8.** Nota: el marcador `vN` es independiente de `metadata.version`; los bumps de
  versión del framework los gestiona `/dev-generate-version`.

## Fase 3 — Cierre de ciclo

Párrafo común a anteponer en cada paso de validación visual: *"Si algún `design_*.html`
contiene `<script id="mnote-data">` con ≥ 1 nota, el usuario dejó anotaciones. Leerlas: por
cada nota, aplicar el cambio a ese `design_*.html` (skill de mockups con `action: edit` si no
es trivial; edición directa si es un retoque menor de texto), luego eliminar la nota resuelta
de `#mnote-data` (borrar el bloque si queda vacío). Resumir en la respuesta qué se cambió por
nota. Después presentar los mockups actualizados como de costumbre."* Una nota cuyo selector
ya no resuelve llega como **"desvinculada"** y se trata como una general más.

- [ ] **T9.** `pv-new/SKILL.md` step 4 (~línea 93): anteponer el párrafo antes de "present
  them to the user".
- [ ] **T10.** `pv-new/SKILL.md` nota final "who writes what" (~línea 102): leer/limpiar
  `#mnote-data` y aplicar sus cambios se hace vía la skill de mockups (`action: edit`) para lo
  no trivial, o edición directa para retoques menores.
- [ ] **T11.** `pv-fix/SKILL.md` step 5 (~línea 107): mismo párrafo anteponer.
- [ ] **T12.** `pv-fix/SKILL.md` nota final (~línea 113): mismo tweak que T10.
- [ ] **T13.** `pv-new/extend-entry.md` step 6 (~línea 10): mismo párrafo, acotado a los
  `design_*.html` tocados por la extensión + cualquiera con `#mnote-data`.
- [ ] **T14.** Revisar `pv-new/workflow.new.md` y `pv-fix/workflow.fix.md`: añadir la rama de
  escaneo `#mnote-data` al diagrama (`SCAN → APPLY → SUMMARY → PRESENT`, como Flujo B) o dejar
  constancia explícita de que es demasiado fina para diagramar. Ambos `SKILL.md` declaran que
  el diagrama manda sobre la prosa.

## Fase 4 — Verificación integral

- [ ] **T15.** Embebido en mockup real ([`PLAN.md`](PLAN.md) Verification §2): splice de los 2
  bloques en `sandbox-test1\previo-sdd\changes\inProgress\00196\design_bloc_notas_vista.html`
  y recorrer todos los sub-puntos: clic → contorno azul + barra al cursor, `➕` mini-menú,
  nota general directa, contador ámbar, tarjeta compartiendo contorno, `‹ ›`, toggle `👁` +
  recarga (localStorage), CSS del mockup intacto con anotaciones ocultas, Save + reabrir →
  rehidratan general + vinculada, y **clic en la barra/tarjeta/panel no selecciona nada del
  mockup ni entra en la ruta `nth-of-type`**.
- [ ] **T16.** Skill dry-run (§3): invocar `pv-internal-mockups-html` vía `pv-new` en un
  cambio visual de prueba en sandbox; confirmar que el `design_*.html` generado contiene
  `id="mnote-styles"`, `id="mnote-runtime"` y `<!-- mnote-framework v1 -->` **byte-idénticos**
  a los bloques del asset.
- [ ] **T17.** Edit round-trip (§4): añadir un `#mnote-data` falso con 2 notas, re-invocar con
  `action: edit`; confirmar que `#mnote-data` sobrevive y los bloques framework quedan
  intactos.
- [ ] **T18.** Cierre de ciclo (§5): `design_*.html` con `#mnote-data` (una nota vinculada
  "make this wider", una general); correr la ruta extend/validate de `pv-new`; confirmar que
  se leen, se edita el mockup, se vacía `#mnote-data` y se re-presenta.
- [ ] **T19.** Propagación en instalación (§6): correr `install.sh` / `install.ps1` a un dir
  scratch (o inspeccionar el bucle de copia, `install.ps1` ~línea 50) y confirmar que
  `.claude/skills/pv-internal-mockups-html/assets/mockup-annotations.html` aterriza en
  destino. Confirmar que `pv-update` no necesita cambios.
- [ ] **T20.** Consistencia prosa↔diagrama (§7): diff de `pv-new`/`pv-fix`/`extend-entry.md`
  contra `workflow.new.md` / `workflow.fix.md`; la rama `#mnote-data` debe estar en el
  diagrama o marcada como demasiado fina, sin desacuerdo silencioso.

## Fase 5 — Cierre

- [ ] **T21.** Ejecutar el flujo normal `/dev-generate-version`
  (`tools/set-skill-versions.py` sube todos los `SKILL.md`; `dev-changelog` regenera
  `.claude/pv-changelog.*.md` desde el git diff). Sin trabajo manual de changelog ni de
  versión.
