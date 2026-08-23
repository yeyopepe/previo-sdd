# Plan — `pv-internal-doc-features` pasa a decidir el qué y el cómo

## Objetivo

Alinear `pv-internal-doc-features` con el mismo patrón de responsabilidad que ya tienen `pv-internal-doc-technical`/`pv-internal-doc-style` para sus respectivos campos (ver tabla comparada de [pv-design.es.md](../pv-doc/pv-design/pv-design.es.md#documentación), sección "Documentación"). Hoy la tabla dice explícitamente, para `pv-internal-doc-features`:

- "Decide **qué** dice el contenido" → **No — lo hace `pv-do`**
- "Decide **cómo** redactarlo" → **No** — construye el `body` con las reglas de dominio (campos, diagramas, cross-links) pero no decide el estilo de prosa

El resto de la fila (gestión de fichero delegada en `pv-internal-doc-files`, no escribe en disco) ya está bien y no cambia. El objetivo de este plan es que `pv-internal-doc-features` pase a tener la responsabilidad única de **qué contenido lleva una entrada de funcionalidad y cómo redactarlo**, dejando a `pv-do` solo el papel de aportar el resumen del cambio implementado y el contexto ya reunido — exactamente el contrato que `pv-do` ya usa hoy con `pv-internal-doc-technical` (`SKILL.md` de `pv-do`, paso 2.1, punto `architectureDocDir`).

## Por qué ahora es distinto de `doc-technical`/`doc-style`

`doc-technical`/`doc-style` no redactan tampoco (nunca escriben nada), solo devuelven checklist + reglas y dejan que `pv-do` redacte. `pv-internal-doc-features` en cambio **sí** ensambla hoy el `body` final (paso 3 de la acción `upsert` actual). Para mantener runtime real (no solo apariencia) hay dos formas de resolver la única responsabilidad "qué + cómo": que seguir redactando ella misma (rol distinto: redactora, no solo asesora) o que pase también a ser solo asesora como sus hermanas. Ver decisión más abajo — se opta por la primera, manteniendo el patrón `find`/`upsert` que ya usa (más cercano a su forma actual, menor blast radius, y coherente con que `doc-features` seguirá siendo la única con `body` estructurado por campos fijos, no prosa libre como architecture/style).

## Cambios en `.claude/skills/pv-internal-doc-features/SKILL.md`

### 1. Nueva sección "Content checklist" (el qué)

Antes de "Feature file shape", añadir una sección que enumere qué debe registrar una entrada de funcionalidad, a partir de lo que hoy solo describe implícitamente `FEATURE.template.md` y el paso 2.1 de `pv-do`:

- Descripción funcional del comportamiento actual (no un changelog de lo que cambió).
- Diagramas funcionales (Mermaid), cuándo incluirlos: si `description.md` de la entrada tiene uno, o hay `design_navigation_*.md`, y representan un flujo de la funcionalidad — con la regla de arrastre conjunto de diagramas que se referencian entre sí (hoy vive en `pv-do` paso 2.1, debe migrar aquí).
- `Available in`.
- `Code` — lista completa de `xxxx`.
- `Since`/`Last modified`.
- Regla de no duplicar entrada (editar in-place) — ya existe, se mantiene.

Esta sección sustituye la frase actual "This skill doesn't decide what the documentation says" (línea 18) por su contraria: la skill sí decide el catálogo de campos/categorías que debe llevar cada entrada.

### 2. Nueva sección "Writing rules" (el cómo)

Añadir reglas de redacción propias del dominio funcional — hoy no existen en ningún sitio de forma explícita, `pv-do` las infiere sobre la marcha. Como mínimo:

- Prosa dirigida a un lector humano/funcional (a diferencia de `doc-technical`, que es para IA) — describe qué puede hacer el usuario, no cómo está implementado.
- Nunca mencionar detalles técnicos internos (nombres de clase, ficheros, decisiones de arquitectura) — eso vive en `architectureDocDir`.
- Nunca redactar en tono changelog ("se añadió...", "ahora permite...") — siempre presente descriptivo del comportamiento vigente, igual que ya impone `pv-internal-changelog` para su propio documento pero aplicado aquí a nivel de frase.
- Cross-links usan ruta relativa `[text](NNN-slug.md)`, nunca anclas `#` (ya existe, se mantiene, pasa a esta sección).
- Al editar in place una entrada existente, la reescritura debe seguir describiendo fielmente el comportamiento resultante completo, no solo apendizar la novedad.

### 3. Cambiar el contrato de la acción `upsert`

Sustituir los parámetros actuales (`body`, `diagrams`, `available_in`, `codes` ya pre-ensamblados por el caller) por lo que ya usa `pv-internal-doc-technical`/`pv-internal-doc-style` como entrada: un resumen de lo implementado + contexto ya reunido (código tocado, `plan.md`, diagramas funcionales/mockups disponibles en la entrada) + fichero existente (si `find` ya devolvió uno). `pv-internal-doc-features` pasa a:

1. Aplicar su propia checklist (sección 1) para decidir qué campos/contenido corresponde a esta entrada.
2. Redactar el `body` ella misma siguiendo sus propias writing rules (sección 2).
3. Ensamblar y delegar en `pv-internal-doc-files` (`action=upsert`) igual que hoy — este paso final no cambia.

Esto implica mover a `pv-internal-doc-features` la lógica que hoy vive en `pv-do` (SKILL.md líneas 78-81): el criterio de "editar in place vs. nueva entrada", el criterio de qué diagramas arrastrar (y la regla de arrastre conjunto), y la redacción del body — `pv-do` deja de redactar y de decidir esos criterios, solo entrega el resumen + contexto.

### 4. Actualizar la acción `find`

Sin cambios de contrato (sigue delegando en `pv-internal-doc-files`), pero aclarar en su prosa que ahora es la propia skill, no `pv-do`, quien usa el resultado de `find` para decidir in-place vs. nueva entrada al ejecutar `upsert`.

### 5. Actualizar `metadata.uses` / versión

Sin cambios en `uses` (sigue siendo solo `pv-internal-doc-files`). Subir `metadata.version` (patch/minor según convención del framework — revisar `pv-internal-doc-technical`/`pv-internal-doc-style` como precedente de versión al recibir esta misma responsabilidad, si la tuvieron en su propio historial).

## Cambios en `.claude/skills/pv-do/SKILL.md`

Paso 2.1, punto `docs.functional.featuresDocPathDir` (líneas 78-82):

- Eliminar los criterios de redacción que migran a `doc-features`: qué es "editar in place" vs. nueva entrada, la lógica de arrastre de diagramas funcionales (párrafo completo "Functional diagrams"), y "Draft the final content... yourself with the criteria above".
- Sustituir por: invocar `pv-internal-doc-features` con `action=find` (igual que hoy) y luego `action=upsert` pasando un resumen de lo implementado + el contexto ya reunido (`plan.md`, código tocado, diagramas/mockups de la entrada) + `existing_file` si `find` encontró coincidencia — sin redactar nada `pv-do` mismo.
- El caso "`featuresDocPathDir` es un único fichero" (legado, línea 81) no tiene skill de dominio equivalente: mantenerlo igual que hoy (pv-do sigue redactando directamente con `FEATURES.template.md`) — fuera de alcance de este plan, se anota como deuda conocida si se quiere unificar más adelante.
- Revisar la frase de idioma en la cabecera de `pv-do` (línea 16, "When updating docs.functional.featuresDocPathDir (via pv-internal-doc-features), use docs.functional.language") — sigue siendo correcta (el idioma lo sigue indicando `pv-do`, igual que ya hace con `architectureDocDir`/`styleBibleDocDir` vía `doc-technical`/`doc-style`), no requiere cambio de fondo, solo confirmar que la redacción no contradice el nuevo contrato.

## Cambios en `pv-design.es.md` (y su par `pv-design.en.md`)

Sección "Responsabilidades de cada skill" → "Documentación":

- Tabla comparada (líneas 268-276 en `.es.md`): actualizar fila "Decide **qué** dice el contenido" para `pv-internal-doc-features` de "No — lo hace `pv-do`" a algo como "**Sí, para `featuresDocPathDir`** — checklist de campos funcionales (descripción, diagramas, Available in, Code, Since, Last modified) y criterio de in-place vs. nueva entrada".
- Actualizar fila "Decide **cómo** redactarlo" de "No — construye el `body`..." a "**Sí** — reglas de redacción funcional propias (tono descriptivo no-changelog, sin detalle técnico, cross-links relativos)".
- Párrafo explicativo bajo la tabla (línea 278): quitar la frase "`pv-internal-doc-features` conserva su responsabilidad de dominio (plantilla, campos..., diagramas funcionales, regla de no duplicar entrada) pero delega en `doc-files`..." — reformular para que quede simétrica con la explicación de `doc-technical`/`doc-style`: decide qué y cómo, delega dónde/cómo se guarda.
- Entrada de responsabilidades de `pv-internal-doc-features` (líneas 288-292): reescribir la primera frase para que dependa de resumen+contexto en vez de contenido pre-ensamblado, igual que ya describe `pv-internal-doc-technical` (línea 294) y `pv-internal-doc-style` (línea 298).
- Entrada de `pv-do` (línea 106): la frase "Si `docs.functional.featuresDocPathDir` es una carpeta, delega su lectura/escritura en `pv-internal-doc-features` en vez de tocarla directamente" ya es compatible sin cambios; revisar si conviene añadir "(qué escribir y cómo redactarlo lo decide `doc-features`)" para que quede explícito, en paralelo a como ya describe la delegación en `doc-technical`/`doc-style` en la misma entrada.
- Diagrama Mermaid de "Documentación" (líneas 237-260) y su leyenda (262-266): no cambia la topología de flechas (`pv-do --> pv-doc-features` sigue existiendo con la misma etiqueta), pero la leyenda línea 265 dice "las dos primeras deciden qué documentar... y cómo redactarlo; la última [`doc-files`] solo decide dónde/cómo guardarlo" refiriéndose solo a `doc-technical`/`doc-style` — hay que incluir explícitamente a `doc-features` en ese "las que deciden qué/cómo", ya que hoy la frase la excluye a propósito.

Aplicar el mismo conjunto de cambios en `pv-design.en.md` (par en inglés) para no desincronizar ambos documentos — localizar las líneas equivalentes por búsqueda de las mismas cabeceras de sección antes de editar.

## Fuera de alcance

- El caso legado de `featuresDocPathDir` como fichero único (`pv-do` sigue redactando directamente) — no tiene skill de dominio, no se toca.
- Cambios en `pv-internal-doc-files` — su contrato (`find`/`upsert` de fichero) no cambia.
- Cualquier cambio de `metadata.version`/changelog global del framework — se resuelve en la fase de implementación siguiendo la convención ya usada por `dev-generate-version`/`pv-version`, no forma parte del diseño de este plan.

## Orden de implementación sugerido

1. `pv-internal-doc-features/SKILL.md` — nuevas secciones (checklist + writing rules) y nuevo contrato de `upsert`.
2. `pv-do/SKILL.md` — simplificar paso 2.1 para el caso carpeta, delegando qué/cómo en `doc-features`.
3. `pv-design.es.md` y `pv-design.en.md` — sincronizar tabla, prosa y leyenda del diagrama de "Documentación".
4. Verificación cruzada: releer las tres skills tocadas (`doc-features`, `pv-do`, `pv-design.*`) para confirmar que ninguna sigue describiendo a `pv-do` como quien decide contenido/redacción funcional.
