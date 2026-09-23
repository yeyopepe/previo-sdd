# Reorganizar cómo se escribe/organiza la documentación funcional

> Estado: idea aparcada, sin definir. Anotado el 2026-09-24 para retomarlo más adelante — no
> empezar a implementar nada de esto sin antes discutir el enfoque con el usuario.

## Motivación

La forma actual en que `docs.functional.*` se organiza y escribe (ver `pv-internal-doc-features`,
`pv-internal-doc-files`) funciona pero el usuario quiere revisarla — sin haber concretado aún qué
le molesta ni qué alternativa prefiere. Este documento es solo el placeholder para no perder el
hilo.

## Preguntas a resolver cuando se retome

- ¿Qué concretamente no convence del esquema actual (un fichero por feature + `INDEX.md`)?
  ¿Es la granularidad, la organización por área, el formato del contenido, algo del proceso de
  escritura (`find`/`upsert`), o algo distinto?
- ¿El problema es de **organización** (cómo se agrupan/localizan las entradas) o de
  **redacción** (qué dice cada entrada y cómo está escrita)?
- ¿Afecta solo a `pv-internal-doc-features`, o también a `pv-internal-doc-style`
  (`styleBibleDocDir`) y su relación?
- ¿Hay un caso real reciente (una feature concreta, un `xxxx`) que haya sido incómodo de
  documentar y sirva de ejemplo concreto para arrancar el análisis?

## Puntos de partida para cuando se retome

- Skills involucradas: `pv-internal-doc-features`, `pv-internal-doc-files`,
  `pv-internal-doc-style`, `pv-internal-doc-technical` (comparten convenciones de escritura).
- Revisar primero con `/dev-analysis` o similar el estado real antes de proponer cambios —
  no asumir que el problema está donde parece a primera vista.

## Situación actual

Cómo y quién escribe `docs.functional.featuresDocPathDir` hoy, verificado contra el código real
(`pv-internal-doc-features/SKILL.md`, `pv-internal-doc-files/SKILL.md`,
`pv-internal-doc-features/FEATURE.template.md`):

- **Reparto de responsabilidades** (tres niveles, cada uno ciego a las decisiones del otro):
  - `pv-do` (caller) reúne el contexto (código tocado, `plan.md`, mockups) y decide *cuándo*
    documentar, pero no redacta nada él mismo para esta carpeta.
  - `pv-internal-doc-features` decide **qué dice** la entrada y **cómo se redacta**: aplica su
    propia checklist de contenido (descripción funcional, diagramas, `Available in`/`Code`/
    `Since`/`Last modified`, la regla de no duplicar entrada) y sus reglas de escritura, pero no
    sabe nada de numeración de ficheros ni de `INDEX.md`.
  - `pv-internal-doc-files` decide **dónde y cómo se guarda**: numeración estable, slug del
    nombre de fichero, regeneración de `INDEX.md` (agrupado por `**Area**:`) — nunca decide ni
    toca el contenido (`body` le llega ya redactado verbatim).
- **Estructura en disco**: un fichero `{NNN}-{slug}.md` por feature (nunca un documento
  monolítico), plano dentro de la carpeta (sin subcarpetas por área), más un `INDEX.md`
  autogenerado que agrupa por `Area` y nunca se edita a mano.
- **Forma de cada fichero** (`FEATURE.template.md`): título `# NNN — Nombre`, `**Area**:`,
  descripción funcional en prosa, diagrama Mermaid funcional opcional, y cuatro campos fijos al
  final (`Available in`, `Code`, `Since`, `Last modified`).
- **Tono de redacción** (explícito en las "Writing rules" de `pv-internal-doc-features`):
  prosa dirigida a un **humano**, no a una IA — a diferencia de `docs.tech.*`
  (`pv-internal-doc-technical`/`pv-internal-doc-style`), que es notación densa, tablas y
  fragmentos de hecho pensados para que una IA los lea. Reglas concretas: nunca mencionar
  detalles técnicos internos; nunca tono de changelog ("se añadió", "ahora permite"), siempre
  tiempo descriptivo del comportamiento actual; en una edición in-place, reescribir la
  descripción completa (no solo añadir el trocito nuevo); enlaces cruzados entre features vía
  ruta relativa (`[texto](NNN-slug.md)`), nunca anclas `#`.
- **Regla de no duplicar**: si lo que se documenta extiende una feature que ya tiene fichero
  propio, se edita in-place (nunca se crea una segunda entrada para la misma feature).
- **Ciclo de vida**: dos acciones, `find` (¿existe ya entrada para esto?) y `upsert` (redactar y
  escribir la versión final), ambas invocadas por `pv-do` a través de `pv-internal-doc-features`.
- **Migración legacy**: existe un script puntual
  (`pv-internal-doc-features/scripts/migrate-legacy-features-doc.py`) para partir un
  `FEATURES.md` monolítico antiguo (`## Area` / `### Feature`) en el esquema actual de un
  fichero por feature — indica que el sistema de un-fichero-por-feature ya es en sí mismo una
  evolución de un esquema anterior más simple.

## Ideas

Lista abierta, sin evaluar ni priorizar — puntos de partida para cuando se retome la discusión.

**Organización del texto**

- Permitir jerarquía dentro de una `Area` (subcarpetas o subgrupos en `INDEX.md`) cuando un área
  crece mucho, en vez de forzar todo a un único nivel plano de ficheros.
- Separar explícitamente "features activas/estables" de "features en beta/experimentales" en el
  índice, si el proyecto tiene ese concepto — hoy `Area` es la única dimensión de agrupación.
- Añadir una sección opcional de "casos límite / comportamiento cuando algo falla" al template,
  si se detecta que esa información se pierde o queda enterrada en prosa general.
- Un resumen de una línea por feature en `INDEX.md` (no solo número + nombre + área), para poder
  hojear el índice sin abrir cada fichero.
- Reconsiderar si `Available in` debería ser una lista estructurada (tabla `Modo | Pantalla`) en
  vez de prosa libre, cuando una feature aparece en muchos sitios distintos.

**Redacción**

- Definir una extensión objetivo (mínima/máxima) por entrada, para evitar tanto entradas
  telegráficas como descripciones que se alargan sin aportar.
- Dar 2-3 ejemplos de "buena" vs "mala" descripción funcional directamente en
  `pv-internal-doc-features/SKILL.md` o en el template, para calibrar el nivel de detalle
  esperado (hoy la regla es solo prosa + prohibiciones, sin ejemplo positivo).
- Explicitar cómo tratar features con múltiples variantes/modos (web vs CLI, plan free vs
  premium): ¿una entrada con subsecciones, o entradas separadas con cross-link?
- Regla para cuándo un diagrama Mermaid es preferible a prosa y cuándo estorba (hoy es "opcional"
  sin criterio de cuándo usarlo).

**Tono**

- Verificar que "prosa para humano" no derive en tono de marketing/producto (voz pasiva,
  adjetivos vacíos) — fijar un registro concreto: neutro, directo, sin vender la feature.
- Decidir si se tutea o no al usuario final dentro de la descripción funcional (afecta
  `docs.functional.language` en proyectos en español) y dejarlo como regla fija, no a criterio
  de quien redacta cada vez.
- Evaluar si conviene una regla explícita tipo `[gotcha]` (como ya existe en `docs.tech.*`) para
  señalar comportamiento contraintuitivo también en documentación funcional, sin romper el
  registro "para humano" de esta carpeta.

## Siguiente paso

Ninguno todavía. Retomar cuando el usuario quiera definir el problema con más detalle, usando
esta lista de ideas como punto de partida a filtrar, no como decisiones ya tomadas.
