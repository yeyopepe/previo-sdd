# Análisis: cómo cerrar el ~20-25% que falta en la documentación generada

**Fecha:** 2026-08-28
**Origen:** informe `test-data/bgfactory-docs/documentation-test-0.9.6b9-technical-full.md` (comparación doc generada por `pv-init` nivel `full` vs. baseline hecho a mano).
**Objeto:** ideas generalistas (no atadas a este proyecto) para mejorar el sistema de análisis en dos frentes: **(A)** que `pv-init` genere ese 20-25% de conceptos que hoy pierde, y **(B)** detectar sistemáticamente qué conceptos del código no llegaron a la doc (el bucle de control de A).

---

## Aclaración previa: dos métricas distintas

El informe reporta "cubre ~23% (arquitectura) / ~43% (estilo)". Eso es **volumen de prosa** (recuento de palabras), no cantidad de información. Por **conceptos del baseline efectivamente tratados**, la doc `full` está en ~75-85% (tabla §2.1/§3.1 del informe: de ~30 temas, la mayoría ✅ *Bien* o mejor, solo 2 ❌ ausentes, ~8 ⚠️ parciales). La diferencia se explica por densidad de escritura: `full` tabula y comprime en notación lo que el baseline desarrolla en prosa.

El "20-25% que falta" al que se refiere este documento es esa fracción de **conceptos/detalle** que queda ⚠️ parcial o ❌ ausente, no el 77% de "volumen que falta".

---

## Diagnóstico: por qué se pierde ese 20-25%

Lo que queda ⚠️/❌ en el informe no es aleatorio. Son **tres patrones repetidos**:

| Patrón de omisión | Ejemplos en el informe | Causa raíz probable |
|---|---|---|
| **Catálogo enumerable colapsado a muestra** | 8 tipos de componente → 1 tabla; ~20 patrones modal/menú → ~10; `renderComponentsOnTable` opts sin enumerar | El generador documenta *que existe la categoría* y da 1-2 ejemplos, en vez de iterar *cada miembro*. `pv-init` step 5.5.6 (features) sí exige exhaustividad por-miembro; 5.5.3 (arquitectura) y 5.5.5 (estilo) no. |
| **Detalle de nivel-campo perdido** | `numeroMaximoCaras` sin rango 2-100; migración `ficha→carta` sin mapeo campo a campo; "quién edita cada campo" | La info está en validaciones y constantes del código, pero el análisis sintetiza a nivel de "shape" y no baja a rangos/límites/reglas. |
| **Checklists de mantenimiento accionables** | "qué revisar al añadir un tipo" (§8 baseline); "Qué NO hacer" de CSS catalogado | No es contenido descriptivo del estado actual; es conocimiento *transversal* (qué N sitios hay que tocar juntos). El generador describe estado, no procedimientos. |

---

## Frente A — que `pv-init` genere ese 20-25%

Contexto: en `pv-init`, el contenido inicial se genera en **step 5.5.3** (arquitectura) y **5.5.5** (estilo), con contexto de `pv-internal-tech-analysis` (modo `bootstrap: true`) y las checklists de categorías de `pv-internal-doc-technical` / `pv-internal-doc-style`.

### A1. Exhaustividad por-miembro obligatoria en catálogos (no solo en features)

Hoy 5.5.6 (features) exige "exhaustivo: una entrada por capability, no una muestra". 5.5.3/5.5.5 no tienen esa exigencia.

**Generalizar el principio:** cuando el análisis detecta un **conjunto enumerable cerrado** (los N tipos de X, los N modos, los N estados de Y, las N variantes de modal), la doc debe tener **una fila/bloque por miembro**, no un ejemplo representativo.

Operativizar sin depender del criterio del modelo: que `pv-internal-tech-analysis` (bootstrap) devuelva explícitamente una lista de **"conjuntos enumerables detectados"** — cada uno con nombre, miembros (extraídos del código: enums, claves `DEFAULT_*`, `case` de switch, factory maps) y "dónde viven sus datos". Luego 5.5.3/5.5.5 llevan un checkbox: *por cada conjunto enumerable, tabla con una fila por miembro*. La ausencia de una fila es un fallo verificable, no cuestión de gusto.

### A2. Nivel "contrato" para toda interfaz que vaya a documentarse

`pv-internal-tech-analysis` ya tiene la regla: *"si el tema toca cualquier interfaz o estructura de datos, requiere su definición completa (firma, input, return, campos) antes de dar el contexto por reunido"*. En modo `bootstrap`/`full` parece aplicarse a las interfaces que el análisis "decide mirar", no a **todas** las que va a documentar.

**Idea:** en modo bootstrap, invertir la regla — **toda función / opts-object / constante que vaya a aparecer en la doc necesita su definición completa capturada primero**. `renderComponentsOnTable(worldEl, components, opts)` no entra en la doc sin las ~10 claves de `opts` y su semántica. Más caro en tokens, pero es lo que "full" promete al usuario ("better result from the start").

### A3. Extraer límites/rangos/defaults de las validaciones, como categoría propia

El detalle campo-a-campo que falta (`2-100`, "mínimo 2 valores", extensiones exactas) **está siempre en el mismo sitio**: funciones de validación, constantes `MIN_*`/`MAX_*`, allowlists, cláusulas `clamp`.

**Añadir a la checklist de categorías de `pv-internal-doc-technical`** una categoría **"constraints / validation rules"**: por cada estructura de datos documentada, barrer su(s) validador(es) y volcar rango + regla + qué cuenta como error. Contenido mecánicamente localizable.

### A4. Checklists de mantenimiento como categoría derivada

El "qué revisar al añadir un tipo" es regenerable; el informe lo dice (§5.2.2): *"si el generador detecta listas fijas de campos serializados/renderizados en varios sitios"*.

**Generalización:** cuando el análisis detecta que **un mismo concepto aparece en ≥3 sitios que hay que mantener sincronizados** (un tipo nuevo toca: enum, `DEFAULT_*_PROPERTIES`, render switch, validación, serialización, migración), eso *genera automáticamente* un checklist "al añadir un X, toca estos N sitios". Es la contrapartida procedural del mapa de módulos.

### A5. "full" con presupuesto de tamaño, no solo instrucción de profundidad

Hoy la diferencia minimal/full es prosa ("aim for the depth of a mature hand-written architecture doc"). Interpretable; el resultado fue ~23% del volumen.

**Idea:** que `pv-internal-tech-analysis` (bootstrap) devuelva una **estimación de tamaño esperado** por documento a partir de lo encontrado (nº de tipos × campos, nº de módulos, nº de patrones visuales) — objetivo aproximado tipo "el catálogo de tipos debería rondar N palabras / N filas". No para rellenar por rellenar, sino para que el modelo detecte *"he escrito 1 tabla donde el material da para 8"* y corrija.

---

## Frente B — detectar sistemáticamente qué falta (bucle de control)

Lo más valioso a largo plazo: hoy la detección de omisiones **depende de que exista un baseline hecho a mano** y de que un humano lo compare. Sin baseline (el caso normal de un proyecto nuevo) no hay red.

### B1. Inventario de conceptos desde el código, independiente de la doc

Un paso `pv-*` nuevo (o una acción de `pv-internal-tech-analysis`) que produzca un **índice de conceptos citables extraídos solo del código**: exports públicos, enums y sus valores, `DEFAULT_*`/`MIN_*`/`MAX_*`, opts-objects, eventos emitidos, claves de `localStorage`, cada `case` de los switch de tipo. Determinista y barato.

Luego: **diff entre ese índice y `00-namespace.md`**. Todo concepto del código sin ancla en el namespace es candidato a omisión. Es un test regenerable, no una revisión humana. El namespace ya está pensado como "un path por concepto citable" — cerrar el bucle es comparar contra la fuente.

### B2. Cobertura como métrica reportada, con los dos ejes separados

El fallo del informe de hoy (mezclar volumen y conceptos) es también una oportunidad. Definir **dos métricas que `pv-init`/`pv-do` calculen y reporten**:

- **Cobertura conceptual** = (conceptos del índice B1 con ancla en namespace) / (total del índice). Objetivo explícito por modo: minimal ≥ X%, full ≥ Y%.
- **Densidad de detalle** = por cada interfaz/estructura documentada, ¿tiene firma completa / campos / rango? Ratio de "documentadas a nivel contrato" vs. "solo mencionadas".

Reportarlas en el summary de step 6. Así "full generó documentación" pasa a "full alcanzó 82% cobertura conceptual, 60% densidad de contrato — pendientes: [lista]".

### B3. Detección de "muestra vs. catálogo" automatizable

Señal barata: si el código tiene un `switch(tipo)` con 8 `case` y la doc menciona 3 nombres de tipo, hay un catálogo colapsado. Si hay 12 clases `.modal-*` en el CSS y la doc describe 5, idem.

Un chequeo que cuenta miembros de conjuntos enumerables en el código y cuántos aparecen citados en la doc. Umbral: si citados/total < 0.8 para un conjunto cerrado → warning "catálogo incompleto: {conjunto}, {n} de {N} documentados".

### B4. El baseline como caso de test del generador

Generalizando el propio ejercicio: cualquier proyecto con doc hecha a mano *y* que adopte `pv-*` puede correr una comparación automatizada baseline↔generado una vez, y esa comparación alimenta mejoras del generador. Convertir este tipo de informe (hoy manual, prosa) en una **plantilla de comparación con salida estructurada**: tema, cubierto sí/no/parcial, eje (concepto/volumen/detalle), agregado. Reproducible y comparable entre versiones de `pv-init`.

### B5. Segunda pasada de auto-crítica antes de cerrar

Barato y efectivo: tras escribir cada documento en 5.5.3/5.5.5, una pasada explícita *"lee lo que acabas de escribir contra el índice de conceptos B1 y la checklist de categorías; lista lo que quedó fuera o a nivel-muestra"* — y o se completa, o se registra como carencia conocida en el summary. Es lo que hace un humano revisando; hoy no está en el flujo.

---

## Priorización

1. **B1 (índice de conceptos desde código) + B2 (métricas de cobertura)** — infraestructura que hace verificable todo lo demás, y no depende de baseline.
2. **A1 (exhaustividad por-miembro en catálogos)** — ataca el mayor bloque de volumen perdido (`02-component-types`, `03-modales-menus`), regla clara.
3. **B5 (auto-crítica pre-cierre)** — barato, encaja en el flujo actual (un checkbox más en 5.5.7).
4. **A3 (constraints desde validaciones)** — segundo bloque de detalle perdido, mecánicamente localizable.

A4 (checklists procedurales) y A5 (presupuesto de tamaño) son más especulativos; dejarlos para después de ver si 1-4 mueven la aguja.
