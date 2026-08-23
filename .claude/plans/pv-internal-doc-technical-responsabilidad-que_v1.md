# Plan de implementación — `pv-internal-doc-technical` gana la responsabilidad del "qué" (fila 1 de la tabla)

Contexto: en [pv-design.es.md](../pv-doc/pv-design/pv-design.es.md), la "Tabla de responsabilidades comparadas" (sección Documentación) tiene una fila `Decide **qué** dice el contenido`. Hoy solo `pv-internal-doc-style` responde **Sí** ahí (checklist de categorías de estilo para `styleBibleDocDir`); `pv-internal-doc-technical` responde **No** — decide solo cómo redactar (estilo de escritura), dejando tema/estructura completamente libres para `architectureDocDir`.

Objetivo: dar a `pv-internal-doc-technical` una checklist de categorías de contenido técnico, propia de `architectureDocDir`, simétrica a la que ya tiene `pv-internal-doc-style` para `styleBibleDocDir` — sin invadir el territorio de `doc-style` (decisión ya tomada con el usuario: alcance limitado a `architectureDocDir`, sin checklist base compartida entre ambas skills).

Lo que **no** cambia: `pv-internal-doc-technical` sigue sin decidir la estructura de fichero/secciones de cada documento concreto (eso sigue libre, igual que hoy), sigue sin escribir nada en disco, y sigue aplicando a `architectureDocDir` **y** `styleBibleDocDir` para el "cómo redactar" (Writing rules ya existentes) — el cambio de esta fila es únicamente el "qué", y únicamente para `architectureDocDir`.

## Archivos a modificar

1. [.claude/skills/pv-internal-doc-technical/SKILL.md](../skills/pv-internal-doc-technical/SKILL.md)
2. [.claude/skills/pv-do/SKILL.md](../skills/pv-do/SKILL.md)
3. [.claude/pv-doc/pv-design/pv-design.es.md](../pv-doc/pv-design/pv-design.es.md)

## Fase 1 — `pv-internal-doc-technical/SKILL.md`: checklist de categorías + contrato entrada/salida

Modelo a replicar: la estructura que ya usa `pv-internal-doc-style` en sus secciones "Expected input from the caller", "1. The category checklist", "2. Check against the received context" y "4. Return the result to the caller".

### 1.1 Categorías propuestas (arquitectura, solo `architectureDocDir`)

| Categoría | Qué revisar |
|---|---|
| Componentes y responsabilidades | ¿El cambio añade/modifica un componente, módulo o servicio con una responsabilidad propia que no está ya documentada? |
| Contratos e interfaces públicas | ¿Añade/cambia una firma pública, API, endpoint o punto de extensión que otro código consume? |
| Flujos de datos entre componentes | ¿Cambia cómo se mueve o transforma la información entre dos o más componentes ya documentados? |
| Decisiones técnicas y alternativas descartadas | ¿Hay una elección de diseño no obvia (por qué esto y no lo evidente) que se perdería si no se registra? |
| Dependencias externas | ¿Introduce/cambia una librería, servicio externo o versión de la que el proyecto pasa a depender? |
| Modelo de datos / persistencia | ¿Añade/cambia una entidad, esquema, migración o invariante de los datos persistidos? |
| Configuración e integración con el entorno | ¿Añade/cambia una variable de entorno, flag, fichero de config o requisito de despliegue? |

Nota: ajustar nombres/columnas exactos al redactar, siguiendo el mismo tono en inglés que usa `doc-style` (vocabulario interno del framework — el caller traduce al redactar en `docs.tech.language`).

### 1.2 Estructura nueva a insertar en el SKILL.md

- Nueva sección **"Expected input from the caller"** (antes de la checklist): resumen de qué se implementa/documenta + contexto ya reunido (código tocado, `plan.md`, ficheros existentes de `architectureDocDir` para el área tocada) — mismo shape que ya recibe `doc-style`.
- Nueva sección **"1. The category checklist"**: la tabla de 1.1, con la misma mecánica de `doc-style` — aplicable si/no, y si aplica, cubierta (con la razón) o pendiente (con qué falta registrar). A diferencia de `doc-style`, aquí no hay condición de "solo si hay capa de presentación": las 7 categorías aplican siempre que sean relevantes al cambio (no todas aplican a la vez — la mayoría de cambios tocan 1-2).
- Nueva sección **"2. Check against the received context"**: mismo criterio que `doc-style` — no explorar código de más para resolver esto; si el contexto ya recibido no basta para decidir, la categoría queda pendiente.
- Nueva sección **"3. Return the result to the caller"**: categorías aplicables cubiertas / pendientes de documentar, sin drafting ni decisión de estructura de fichero. Las Writing rules existentes (renumeradas si hace falta) se devuelven igual que hoy, para aplicar sobre lo que quede pendiente.
- Las Writing rules actuales (1-8) y la sección "Language-independence" no cambian de contenido, solo de posición si el nuevo orden de secciones lo requiere.

### 1.3 Frontmatter

- Actualizar `description`: añadir que ahora también decide el **qué** de `architectureDocDir` (checklist de categorías de contenido técnico), dejando claro que `styleBibleDocDir` sigue sin checklist propia aquí (esa la tiene `doc-style`) y que la estructura del documento sigue libre.
- Bump de `metadata.version` (patch).

## Fase 2 — `pv-do/SKILL.md`: actualizar la invocación (líneas 76-77 actuales)

- Cambiar la invocación de `pv-internal-doc-technical` de "sin parámetros, solo carga estilo" a pasarle el mismo tipo de input que ya recibe `doc-style`: resumen del cambio + contexto reunido + ficheros existentes de `architectureDocDir` para el área tocada.
- Esto obliga a adelantar el `pv-internal-doc-files action=find` de `architectureDocDir` (hoy ocurre después, en el punto de "docs.tech.architectureDocDir" de la línea 77) a **antes** de invocar `doc-technical`, o pasarlo como contexto ya disponible si `pv-how`/`plan.md` ya lo trae.
- Tras la invocación, usar las categorías "pendientes" devueltas por `doc-technical` para decidir qué redactar en `architectureDocDir` (igual que ya hace hoy con lo que devuelve `doc-style` para `styleBibleDocDir`), en vez de decidir sin guía qué actualizar.
- El resto del punto (invocar `pv-internal-doc-files action=upsert` con el `body` redactado) no cambia.
- Bump de `metadata.version` (patch) si el cambio de contrato de invocación lo justifica.

## Fase 3 — `pv-design.es.md`: tabla y prosa

### 3.1 Tabla de responsabilidades comparadas (líneas ~268-276)

Cómo queda la fila 1 tras el cambio:

| | `pv-internal-doc-files` | `pv-internal-doc-features` | `pv-internal-doc-technical` | `pv-internal-doc-style` |
|---|---|---|---|---|
| Decide **qué** dice el contenido | No | No — lo hace `pv-do` | **Sí, para `architectureDocDir`** — checklist de categorías técnicas (componentes, contratos, flujos de datos, decisiones, dependencias, modelo de datos, configuración); estructura del documento sigue libre. No decide el qué de `styleBibleDocDir` (eso es `doc-style`) | **Sí** — checklist de categorías + qué debe registrar cada una |

El resto de filas de la tabla no cambia (cómo redactarlo, gestión de fichero, escribe en disco, a qué campo aplica siguen igual: `doc-technical` sigue sin gestionar fichero, sin escribir nada, y sigue aplicando a ambos campos tech para el "cómo").

### 3.2 Prosa a ajustar

- Párrafo bajo la tabla (línea ~276): matizar "`pv-internal-doc-technical`/`pv-internal-doc-style` no gestionan fichero ni deciden dónde se guarda" para dejar claro que eso sigue siendo cierto (gestión de fichero) pero que `doc-technical` ahora sí decide el catálogo de categorías de contenido para `architectureDocDir`.
- Leyenda del diagrama Mermaid de la sección Documentación (línea ~264): "`pv-internal-doc-technical`/`pv-internal-doc-style` nunca invocan a `pv-internal-doc-files` ni a la inversa: las dos primeras solo deciden qué/cómo redactar, la última solo decide dónde/cómo guardarlo" — corregir, porque hoy es inexacto (decía que ninguna decidía "qué"; ahora sí es cierto para ambas pero con alcance distinto cada una). Redacción propuesta: "las dos primeras deciden qué documentar (cada una en su campo: `doc-technical` en `architectureDocDir`, `doc-style` en `styleBibleDocDir`) y cómo redactarlo; la última solo decide dónde/cómo guardarlo".
- Entrada de responsabilidades de `pv-internal-doc-technical` (línea ~292): reescribir para incluir la checklist de categorías, manteniendo intacta la frase sobre que sigue sin decidir estructura de fichero ni escribir nada. Ejemplo de redacción:

  > **pv-internal-doc-technical** — Qué y cómo escribir `docs.tech.architectureDocDir` (checklist de categorías de contenido técnico — componentes, contratos, flujos de datos, decisiones, dependencias, modelo de datos, configuración) y estilo de escritura compartido con `styleBibleDocDir` (fragmentos densos, tablas, código, tags fijos en inglés). No decide el qué de `styleBibleDocDir` (lo hace `pv-internal-doc-style`) ni la estructura/tema concretos de cada documento, ni escribe nada por sí misma: solo carga la checklist y las reglas antes de que quien invoca redacte. La usa `pv-do`. *Usa:* ninguna otra skill.

- Revisar si el diagrama Mermaid en sí (nodos/flechas) necesita cambios: no — la relación de invocación (`pv-do --> pv-doc-technical`) no cambia, solo lo que hace `doc-technical` internamente.

## Fase 4 — Verificación

- Releer `pv-internal-doc-technical/SKILL.md` completo: la checklist nueva no debe solapar categorías con `pv-internal-doc-style` (p.ej. "Componentes reutilizables / design system" es de `doc-style`; "Componentes y responsabilidades" de `doc-technical` es sobre arquitectura de código, no UI — dejar la distinción explícita si hay riesgo de confusión).
- Releer `pv-do/SKILL.md` punto 2.1 completo tras el cambio, confirmando que el orden de invocación (`doc-files find` → `doc-technical` con ese contexto → redactar pendientes → `doc-files upsert`) queda sin ambigüedad.
- Confirmar que la tabla y las tres menciones de prosa en `pv-design.es.md` quedan consistentes entre sí (misma frase para describir el alcance del "qué" de `doc-technical" en los tres sitios donde aparece).

## Orden de ejecución sugerido

1. Fase 1 (`pv-internal-doc-technical`) — define el contrato nuevo primero.
2. Fase 2 (`pv-do`) — consume el contrato ya definido.
3. Fase 3 (`pv-design.es.md`) — documenta el resultado final.
4. Fase 4 (verificación) antes de dar el plan por cerrado.

## Anexo — Qué implicaría que `pv-internal-doc-technical` dejara de intervenir en `styleBibleDocDir`

Esto es un cambio **más profundo** que el de las Fases 1-4 (que no tocan el alcance actual de aplicación de `doc-technical`, solo le añaden la checklist del "qué" para `architectureDocDir`). Sacarla por completo de `styleBibleDocDir` afecta al "cómo redactar" compartido, no solo al "qué", y toca la relación entre `doc-technical` y `doc-style`. Se documenta aquí como análisis de impacto, sin incluirlo en el orden de ejecución anterior — es una decisión de alcance separada.

### Estado actual (por qué hoy sí interviene)

- `pv-internal-doc-technical` es, según su propio frontmatter, "*Shared, project-agnostic writing style for `docs.tech.architectureDocDir` **and** `styleBibleDocDir`*" — el baseline de redacción (fragmentos densos, tablas, código, tags fijos en inglés) es explícitamente el mismo para los dos campos, no una casualidad de implementación.
- `pv-internal-doc-style` no sustituye ese baseline, lo **extiende**: su propio SKILL.md dice literalmente "*The two are complementary, not redundant*" y en la sección "3. Writing rules" — "*These extend `pv-internal-doc-technical`'s baseline (**still invoke that skill too** — this doesn't replace it)*". Es decir, hoy `doc-style` depende de que `doc-technical` siga interviniendo; no tiene sus propias reglas base de "una tabla por estructura paralela", "código para valores", "tags fijos", etc. — las hereda por invocación directa.
- `pv-do` (línea 76 de su SKILL.md) invoca `doc-technical` **una sola vez** antes de tocar cualquiera de los dos campos, precisamente porque hoy es la base común: "*Before drafting or editing any content for either of the two points below, invoke `pv-internal-doc-technical`... Skip this invocation only if neither `architectureDocDir` nor `styleBibleDocDir` is configured.*"

### Qué habría que hacer para separarlas

1. **Duplicar o mover el baseline de redacción a `doc-style`.** Las 8 reglas de "Writing rules" (fragmentos densos, código/tipos, tablas, no restatear lo obvio, apuntar a la fuente, tags fijos en inglés, sin intro/resumen, listas planas sobre párrafos) y la sección "Language-independence" (garantías de que las reglas no dependen del idioma) tendrían que copiarse dentro de `pv-internal-doc-style`, porque dejarían de estar disponibles vía invocación a `doc-technical`. Esto rompe el principio DRY que el diseño actual explota deliberadamente (una sola fuente de verdad para el "cómo" común a ambos campos tech).
2. **Mantenimiento duplicado a partir de ahí.** Cualquier ajuste futuro al estilo base (como los que ya se hicieron en `pv-internal-doc-technical-optimizacion_v1.md`: reglas anti-anafóricas, anti-intensificadores, tags nuevos como `[gotcha]`, notación de contrato) tendría que aplicarse en dos sitios a la vez y mantenerse sincronizado a mano — el propio plan de optimización ya identificó este riesgo en su Fase 5 ("confirmar que `pv-internal-doc-style` no duplica ninguna de estas reglas... evitar que quede una regla contradictoria en dos sitios"); separar del todo lo convierte en una duplicación intencionada, no accidental.
3. **Reescribir `pv-do`.** El punto 2.1 de `pv-do/SKILL.md` (línea 76) tendría que dejar de invocar `doc-technical` como paso común previo a los dos campos, y en su lugar: invocar `doc-technical` solo antes de tocar `architectureDocDir`, e invocar `doc-style` (ahora autosuficiente, sin depender de `doc-technical`) antes de tocar `styleBibleDocDir`. Dos rutas de invocación en vez de una compartida.
4. **Actualizar frontmatter y prosa de ambas skills.** `doc-technical` dejaría de decir "for `docs.tech.architectureDocDir`/`styleBibleDocDir`" en su `description` y en el cuerpo (título de la sección "Audience", frase "how to write `docs.tech.architectureDocDir`/`styleBibleDocDir` content"), pasando a ser exclusivamente sobre `architectureDocDir`. `doc-style` dejaría de decir "The two are complementary... still invoke that skill too" y pasaría a documentarse como autocontenida.
5. **Actualizar `pv-design.es.md` en varios puntos**, no solo la tabla: el diagrama Mermaid de la sección Documentación (línea ~248-251) tiene la flecha `pv_do -->|"docs.tech.architectureDocDir / styleBibleDocDir"| pv_doc_technical`, que pasaría a ser solo `architectureDocDir`; la fila "A qué campo aplica" de la tabla cambiaría de "`architectureDocDir` **y** `docs.tech.styleBibleDocDir`" a solo `architectureDocDir`; la fila "Decide **cómo redactarlo**" también cambiaría, porque hoy dice que `doc-style` tiene "reglas de escritura propias, **encima de** las de `doc-technical`" — dejaría de ser "encima de", pasaría a ser autosuficiente.

### Problemas / riesgos de hacerlo

- **Pérdida de garantía de consistencia entre `architectureDocDir` y `styleBibleDocDir`.** Hoy, que ambos compartan el mismo baseline vía una sola skill es lo que garantiza que un lector-IA (`pv-internal-tech-analysis`) encuentre el mismo formato (fragmentos, tablas, tags) en los dos. Separarlas del todo abre la puerta a que diverjan con el tiempo si alguien edita una sin replicar en la otra — justo el riesgo que la Fase 5 del plan de optimización ya marcó como algo a vigilar, y que hoy se evita por construcción (una sola skill, invocada dos veces).
- **No hay ninguna necesidad funcional que lo empuje.** El único cambio pedido en este plan (Fases 1-4) es que `doc-technical` sume una checklist de "qué" para `architectureDocDir` — eso no requiere dejar de aplicar su "cómo" a `styleBibleDocDir`. Separar el "cómo" compartido sería un cambio de alcance no solicitado por el objetivo original (fila 1 de la tabla), que además contradice el propio diseño documentado en `pv-design.es.md` línea ~264 ("no se necesitan entre sí" se refiere a `doc-files`, no a esto — pero el diseño sí declara expresamente el baseline compartido como algo intencional, no incidental).
- **Recomendación:** no ejecutar este anexo salvo que surja una razón concreta (p.ej. que `architectureDocDir` y `styleBibleDocDir` necesiten estilos de redacción realmente distintos, no solo categorías de contenido distintas — que no es el caso hoy). Si en el futuro se decide hacerlo, tratarlo como un plan aparte, no como extensión de este.
