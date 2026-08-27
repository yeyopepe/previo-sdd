# Optimización de pv-internal-doc-technical

Ideas para mejorar la skill `pv-internal-doc-technical` optimizando exclusivamente para el lector-modelo (yo), no para lectores humanos. Documento de trabajo — se va discutiendo y actualizando el estado de cada propuesta a medida que avanzamos.

## Índice

| # | Propuesta | Estado | Ganancia | Razón de la ganancia (fase de análisis) | Incompatible con... |
|---|-----------|--------|----------|------------------------------------------|------------------|
| [1](#1-metadata-de-verificación-contra-código--descartado) | Metadata de verificación contra código (`[verified: ...]` / `[source: ...]`) | ❌ descartado | — | — | — |
| [2](#2-tag-de-anti-expectativa--aprobado) | Tag de anti-expectativa para hechos que contradicen el prior por defecto | ✅ aprobado | **Alta** | Marca justo la línea donde el análisis se equivoca: la excepción al patrón común, que si no se pierde entre hechos que solo confirman lo obvio. | — |
| [3](#3-orden-por-frecuencia-de-consulta--descartado) | Orden por frecuencia de consulta en vez de jerarquía lógica humana | ❌ descartado | — | — | — |
| [4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) | IDs estables y citables entre documentos `docs.tech` | 🔀 absorbido por [15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) | Media | Evita reconciliar dos redacciones de la misma regla al cruzar varios docs; menos drift que resolver durante el análisis. | via [15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado): [9](#inc-151-punto-15--punto-9-nombres-de-sección-fijos), [13](#inc-152-punto-15--punto-13-afirmaciones-no-escalares) |
| [5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo) | Excluir explícitamente lo ya-inferible por conocimiento general del modelo | 🔍 analizando | Media | Menos texto que leer y descartar; lo genérico no tapa lo específico del proyecto. Acelera, no cambia lo que se entiende. | — |
| [6](#6-notación-compacta-en-vez-de-prosa-para-datos-estructurados--aprobado) | Notación compacta en vez de prosa para datos estructurados (tipos, defaults, opcionalidad) | ✅ aprobado | **Alta** | El análisis exige la definición completa de cada estructura tocada; `campo: tipo = default (opc)` se extrae sin ambigüedad, la misma info en prosa hay que parsearla y es donde se cuela el error. | — |
| [7](#7-prohibir-referencias-anafóricas--aprobado) | Prohibir referencias anafóricas ("esto", "dicho campo") — repetir el nombre exacto | ✅ aprobado | Media | Elimina la pasada extra de desambiguación de "esto"/"dicho campo", que a veces se resuelve mal con dos candidatos cerca. Ambigüedad puntual, no reestructura. | — |
| [8](#8-prohibir-adjetivosadverbios-de-intensidad-sin-cifra--aprobado) | Prohibir adjetivos/adverbios de intensidad sin cifra ("muy rápido", "poco frecuente") | ✅ aprobado | Baja | Un intensificador sin cifra ya se descarta como no-información; forzar la cifra solo aporta cuando existe. Higiene de redacción. | — |
| [9](#9-nombres-de-sección-fijos-entre-documentos) | Nombres de sección fijos y repetidos entre todos los docs `docs.tech` (indexación por convención) | 🔍 analizando | Media | *Jump-to-section* por convención: se localiza "Contracts"/"Invariants" en cualquier doc sin leer su índice. Acelera localizar, no comprender. | — |
| [10](#10-un-único-término-por-concepto--absorbido-por-el-15) | Un único término por concepto, prohibida la variación sinonímica dentro del proyecto | 🔀 absorbido por [15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) | Media | Elimina la resolución de sinonimia (¿"endpoint", "ruta" y "handler" son lo mismo aquí?), que puede fallar y partir un concepto en dos. Subconjunto de lo que el 15 hace estructural. | — |
| [11](#11-grafo-de-dependencias-explícito-entre-secciones--descartado) | Grafo de dependencias explícito entre secciones (`requires:` / `assumes:` / `narrows:`) en vez de orden narrativo | ❌ descartado | Baja | Ahorra leer secciones de más en consultas puntuales, pero eso es menos que el error de entender mal las que sí se leen (lo ataca el 13). Depende de infraestructura de otras 3 propuestas. | [3](#111-punto-11--punto-3-orden-por-frecuencia-de-consulta), [9](#112-punto-11--punto-9-nombres-de-sección-fijos), [13](#113-punto-11--punto-13-notación-nativa--índice-inverso-de-narrows) |
| [12](#12-invariantes-como-asserts-ejecutables--absorbido-por-el-13) | Invariantes como asserts ejecutables/testables en vez de (o además de) prosa | 🔀 absorbido por [13](#136-invariante-forma-ejecutable-vs-declarativa-absorbe-el-12) | Media | Un `assert token.exp - token.iat <= 3600` se lee sin ambigüedad y, con test, se sabe vivo sin verificar contra el código. Acotado a invariantes evaluables en runtime. | — |
| [13](#13-notación-nativa-por-tipo-de-contenido-prosa-solo-donde-no-hay-forma-mejor--aprobado) | Notación nativa por tipo de contenido (tablas, contratos, diagramas...); prosa solo donde no hay forma mejor | ✅ aprobado | **Alta** | Convierte cada contrato/FSM/tabla/flujo de prosa-a-parsear en estructura que se lee directa. Reduce a la vez coste (menos parsing) y error (menos relleno con el patrón), en cada documento. | — |
| [14](#14-inglés-técnico-como-idioma-del-documento--aprobado) | Inglés técnico como idioma del documento en vez de español | ✅ aprobado | Baja | Hipótesis de mejor tokenización y doc monolingüe, no medida (regla 8). Sin cifra no se puede afirmar ganancia real de análisis. | — |
| [15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) | Namespace jerárquico único (segmentos separados por puntos), vinculado al código, para conceptos y afirmaciones — absorbe 4 y 10 | ✅ aprobado | **Alta** | Cada concepto y afirmación tiene ruta canónica única vinculada al código por `ancla:`. Elimina de golpe sinonimia, drift y la duda "¿esto es lo mismo que aquello?", y da un punto de verificación contra el código por nodo. | [9](#inc-151-punto-15--punto-9-nombres-de-sección-fijos), [13](#inc-152-punto-15--punto-13-afirmaciones-no-escalares) |

Leyenda de estado: ✅ aprobado · ❌ descartado · 🔍 analizando · 🔀 absorbido (su contenido sigue vivo dentro de otra propuesta que lo generaliza).

Columna **Ganancia**: cuánto acelera o hace más fiable la **fase de análisis** de una tarea cualquiera (`pv-internal-tech-analysis`: leer `docs.tech`, reconstruir interfaces y estructuras, no rellenar huecos con el patrón por defecto) si ese punto —y solo ese— estuviera implementado en la documentación. **Alta**: golpea el núcleo del análisis (extraer estructura, no equivocarse en la excepción). **Media**: reduce coste o ambigüedad puntual sin cambiar lo que se entiende. **Baja**: higiene, efecto marginal o no verificable. Ver [Ganancia en la fase de análisis](#ganancia-en-la-fase-de-análisis) para el detalle punto por punto.

## 1. Metadata de verificación contra código — DESCARTADO

Descartado: la premisa asume que la doc puede desincronizarse del código, pero eso es justo lo que el framework garantiza que no pase (`pv-do` mantiene la doc actualizada junto con cada cambio). Un tag de "esto podría estar desactualizado" resolvería un problema inexistente en este framework y solo añadiría mantenimiento sin beneficio real.

<details>
<summary>Idea original (descartada)</summary>

Distinguir, dentro de un mismo doc, entre hechos arquitectónicos/estables (decisiones de diseño que no dependen del estado exacto del código) y hechos que son snapshot del código (listas de campos, firmas, valores concretos). Hoy la regla 5 ("apunta a la fuente en vez de duplicar forma") mitiga la duplicación, pero no marca qué afirmaciones son más propensas a quedar desactualizadas.

Idea: un tag fijo tipo `[snapshot: file:symbol]` para hechos derivados directamente del código en un momento dado, dejando sin marcar (o con otro tag `[stable]`) las decisiones de diseño que no cambian con cada refactor. Esto me permitiría, al leer, ponderar cuánta confianza dar a una afirmación sin tener que ir siempre a verificar contra el código real — sabiendo cuáles sí necesitan esa verificación con más frecuencia.

</details>

## 2. Tag de anti-expectativa — APROBADO

Como lector-modelo, no parto de cero: tengo priors fuertes sobre patrones comunes de software (nombres de métodos, convenciones REST, ciclos de vida típicos). Un hecho que confirma mi prior aporta poco valor real aunque ocupe una línea; un hecho que lo contradice es donde el doc realmente me corrige, y es también donde más me equivoco si no está señalado — porque tiendo a rellenar huecos con el patrón común en vez de con la excepción real del proyecto.

La regla 1 actual ("un hecho por línea") trata todas las líneas como intercambiables en peso, sin distinguir la anti-expectativa del hecho confirmatorio. Un tag fijo (mismo mecanismo que la regla 6 ya usa para `[breaking]`, `[async]`, etc.) — por ejemplo `[gotcha]` — marcaría específicamente los hechos que contradicen el patrón por defecto esperable, para que no se pierdan entre filas de tabla que solo confirman lo obvio.

Ejemplo:
```
- [gotcha] `deleteUser(id)` NO borra el registro, solo marca `active=false`.
```
en vez de
```
- `deleteUser(id)` marca el usuario como inactivo.
```
porque "delete" sugiriendo borrado físico es exactamente el prior que traería y que aquí es falso.

## 3. Orden por frecuencia de consulta — DESCARTADO

Descartado: sin telemetría real, la única señal disponible sería una heurística indirecta (qué se referencia desde otros docs/entries) — demasiado débil y fácil de sesgar al escribir como para sostener un mecanismo de orden.

<details>
<summary>Idea original (descartada)</summary>

Los docs humanos suelen ordenarse de general a específico, o siguiendo una jerarquía conceptual. Para mí no es necesariamente relevante esa jerarquía — mi lectura no siempre es secuencial completa (a veces extraigo por patrón-matching o consulta puntual). Sería más eficiente que las secciones más consultadas por `pv-internal-tech-analysis`/`pv-how` en ciclos anteriores estuvieran al principio del documento, independientemente de su lugar "lógico" en una jerarquía humana — front-loading lo de alta frecuencia reduce el caso típico de lectura parcial.

Abierto: cómo determinar "frecuencia de consulta" sin telemetría real — quizás una heurística simple (qué se referencia más desde otros docs/entries) o dejarlo como sugerencia flexible más que regla dura.

Ejemplo: en un doc de arquitectura de auth, la jerarquía humana típica empezaría por "Visión general del módulo" → "Diagrama de componentes" → "Flujo de login" → ... → "Expiración y renovación de tokens" al final, como detalle. Pero si en ciclos anteriores `pv-how`/`pv-internal-tech-analysis` han consultado ese doc sobre todo para resolver dudas puntuales de expiración de tokens (porque es lo que más cambia o lo que más genera fixes), esa sección debería ir cerca del principio — aunque conceptualmente sea "un detalle" dentro de la jerarquía lógica del documento.

</details>

## 4. IDs estables y citables entre documentos — ABSORBIDO POR EL 15

El [punto 15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) generaliza esta propuesta: las hojas del namespace jerárquico (las que tienen `=valor` o cuelgan de `.decision.*`) **son** los IDs estables citables que pedía este punto, y la ruta con puntos (`auth.token.session.ttl.value`) es su forma canónica de cita — una sola sintaxis, sin `ver docs.tech#id` vs `[ver id]`. El contenido de este punto sigue vivo dentro del 15; no está descartado.

Las incompatibilidades que se registraron para el punto 4 se trasladan al bloque de incompatibilidades del punto 15:
- 4 ↔ 9 → [Incompat. 15.1](#inc-151-punto-15--punto-9-nombres-de-sección-fijos) (fricción, sigue abierta).
- 4 ↔ 13 (sintaxis de cita) → **resuelta por construcción**; lo que queda abierto es otra cosa (afirmaciones no escalares), en [Incompat. 15.2](#inc-152-punto-15--punto-13-afirmaciones-no-escalares).
- 4 ↔ 10 → **resuelta por construcción** ([Incompat. 15.3](#inc-153-punto-15--punto-10-un-único-término-por-concepto--resuelta-por-construcción)).
- 4 ↔ 1 → guía de implementación del 15 ([Incompat. 15.4](#inc-154-punto-15--punto-1-metadata-de-verificación--histórico)).

<details>
<summary>Idea original (absorbida por el 15)</summary>

La regla 5 cubre "apunta al código en vez de duplicar su forma", pero no cubre la duplicación entre distintos documentos `docs.tech` que comparten una misma invariante o decisión. Hoy, si dos docs de arquitectura mencionan la misma regla, probablemente cada uno la redacta con su propia prosa, lo que introduce el mismo riesgo de drift que la regla 5 ya evita para el código.

Idea: anchors o IDs estables (`<!-- id: auth-token-expiry -->` o similar) que permitan a un doc referenciar a otro (`ver docs.tech#auth-token-expiry`) sin reescribir el hecho. Reduce duplicación y mantiene una única fuente de verdad también a nivel de documentación, no solo entre documentación y código.

</details>

## 5. Excluir lo ya-inferible por conocimiento general del modelo

La regla 4 actual dice "no repitas lo que ya dice la firma o el nombre" — es decir, no dupliques lo que el código ya muestra. Propuesta de ampliar ese principio: tampoco vale la pena documentar lo que yo, como modelo con conocimiento general de patrones de software, ya asumiría por defecto sin necesidad de que el código o el doc lo diga (p.ej. "sigue REST", "usa MVC" sin más detalle, "las contraseñas se hashean" sin especificar el algoritmo o una decisión no estándar).

Esto es distinto de la regla 4: la regla 4 habla de redundancia código↔doc; esto habla de redundancia conocimiento-general↔doc. Solo justifica una línea la desviación del patrón esperado — lo cual conecta directamente con la propuesta 2 (anti-expectativa): si algo sigue el default, no hace falta escribirlo; si lo contradice, se marca con `[gotcha]`.

Riesgo a discutir: esto depende de que el escritor (`pv-do`) sepa estimar qué es "obvio para un modelo" — criterio más difuso que las reglas actuales, que son mecánicas y verificables.

## 6. Notación compacta en vez de prosa para datos estructurados — APROBADO

En vez de "el método recibe un parámetro opcional que, si no se especifica, toma el valor por defecto de 30 segundos", usar directamente notación tipo `timeout: number = 30s (opcional)`. Como lector-modelo parseo notación mucho más rápido y con menos ambigüedad que prosa — la prosa está optimizada para lectura humana fluida, no para extracción de datos estructurados.

## 7. Prohibir referencias anafóricas — APROBADO

Nunca usar pronombres/referencias anafóricas ("esto", "dicho campo", "el mismo") cuando se puede repetir el nombre exacto. En texto humano repetir el nombre se ve pesado; para el lector-modelo, resolver un "esto" cuesta una pasada extra de desambiguación y a veces se resuelve mal si hay dos candidatos cerca.

## 8. Prohibir adjetivos/adverbios de intensidad sin cifra — APROBADO

Prohibir intensificadores sin cuantificar ("muy rápido", "bastante grande", "poco frecuente") — o se cuantifica o no se escribe. Conecta con el espíritu de "hechos verificables" de las reglas actuales, pero como regla explícita de redacción, no de contenido.

## 9. Nombres de sección fijos entre documentos

Una sola convención de nombrado de secciones fija y repetida en todos los docs `docs.tech` (mismos headers literales: "Contratos", "Invariantes", "Decisiones descartadas", etc.) en vez de dejar que cada doc titule libremente. Permite *jump-to-section* por nombre exacto sin tener que leer el índice cada vez — indexación por convención en vez de por contenido.

## 10. Un único término por concepto — ABSORBIDO POR EL 15

El [punto 15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) generaliza esta propuesta: los **nodos** del namespace jerárquico (los segmentos con ancla de código, `auth.token.session`) son el término único por concepto que pedía este punto, y su unicidad es estructural — no hay dos rutas para el mismo nodo. La prohibición de sinónimos deja de ser una regla de estilo a vigilar y pasa a ser una propiedad del árbol de nombres. El contenido de este punto sigue vivo dentro del 15; no está descartado.

<details>
<summary>Idea original (absorbida por el 15)</summary>

Evitar sinónimos variados para el mismo concepto dentro del proyecto (a veces "endpoint", a veces "ruta", a veces "handler" para la misma cosa) — fijar un término único por concepto y prohibir variarlo por elegancia de estilo. La variación estilística que un humano agradece (para no sonar repetitivo) al lector-modelo le cuesta una resolución de sinonimia que puede fallar.

Criterio de aprobación: no importa la repetición del término — el estilo no es un objetivo del doc, solo la efectividad de lectura para el modelo. Lenguaje único e inequívoco por encima de variedad estilística.

</details>

## 11. Grafo de dependencias explícito entre secciones — DESCARTADO

Descartado al compararlo cabeza a cabeza con el [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado): si solo se implementa uno de los dos, el 13 aporta mucho más y el 11 no compensa su coste de infraestructura.

Razones:

- **Cobertura.** El 13 toca cada línea de cada documento (cómo se escribe un invariante, un contrato, una FSM, una tabla de decisión, una alternativa descartada). El 11 solo añade metadatos de navegación en la cabecera de cada sección — cambia el bloque de aristas, no el contenido.
- **El coste que elimina es secundario.** Parsear prosa para extraer estructura (default, opcionalidad, transición faltante) es el trabajo más caro y más propenso a error de relleno con el patrón común — eso lo resuelve el 13. El 11 solo ahorra *leer secciones irrelevantes*, un ahorro menor frente a *entender mal las relevantes*.
- **El 13 funciona solo; el 11 casi no.** El 11 rinde solo si además existen los IDs estables ([punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15)), los nombres de sección resueltos ([punto 9](#9-nombres-de-sección-fijos-entre-documentos)) y un índice inverso de `narrows` generado al escribir. Es infraestructura dependiente de otras tres propuestas. El 13 se aplica documento a documento sin nada más.
- **Degradación.** Un doc con 13 y sin 11 sigue siendo denso y rápido de leer, solo que se navega linealmente. Un doc con 11 y sin 13 es prosa humana con un grafo encima: se sabe qué cargar, pero cada sección cargada cuesta lo mismo de parsear.

Lo que se pierde al descartar el 11: en documentos grandes (>15-20 secciones) el lector-modelo carga de más o de menos en consultas puntuales, y se pierde la validación de ciclos que forzaba a fusionar secciones mal separadas. Mitigación parcial: buen uso de los IDs citables del [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) y referencias explícitas entre secciones donde la dependencia sea crítica.

Las incompatibilidades registradas para el punto 11 ([11.1](#111-punto-11--punto-3-orden-por-frecuencia-de-consulta), [11.2](#112-punto-11--punto-9-nombres-de-sección-fijos), [11.3](#113-punto-11--punto-13-notación-nativa--índice-inverso-de-narrows)) quedan como histórico — ninguna aplica ya, pero documentan por qué el grafo chocaba con 9 y 13.

<details>
<summary>Desarrollo original (descartado)</summary>

En vez de orden narrativo (Sección A seguida de Sección B, con la jerarquía implícita en el orden), un bloque de aristas al principio de cada sección. Permite al lector-modelo decidir algorítmicamente qué otras secciones necesita cargar en contexto antes de confiar en esta, en vez de inferirlo leyendo todo el documento en orden.

El orden narrativo humano codifica dependencias, pero lo hace de forma implícita, unidireccional (solo "lo anterior") y no verificable. Un grafo explícito las hace legibles sin lectura secuencial, permite dependencias hacia adelante, y es validable (detección de ciclos).

### 11.1. Taxonomía de aristas

`depends_on` genérico mezcla dos relaciones que el lector-modelo trata distinto. Se separan en tres aristas, cada una con un nombre fijo:

| Arista | Significado | Qué obliga al lector-modelo |
|---|---|---|
| `requires: [ID, ...]` | No se puede **entender** esta sección sin la otra: usa un término, ID, contrato o estado definido allí. Dependencia de **comprensión**. | Cargar la(s) sección(es) **antes** de leer esta. Cierre transitivo obligatorio. |
| `assumes: [ID, ...]` | Esta sección solo es **válida** si se cumple lo que afirma la otra. Dependencia de **verdad**: si la otra cambia, las conclusiones de esta pueden dejar de valer. | Cargar la(s) sección(es) y **verificar que siguen diciendo lo que esta asume** antes de concluir. Sin cierre transitivo. |
| `narrows: [ID, ...]` | Esta sección **restringe / estrecha** un caso que la otra dejaba abierto o más general. No la contradice: acota. | Al leer la sección `narrows`-target, saber que existe una restricción adicional aquí. Arista informativa, no de carga previa. |

Notas:
- Se elimina `invalidates` del planteamiento original. Una sección no invalida otra de forma estática dentro de un mismo doc coherente; el caso real ("aquí la regla general no aplica") es siempre un `narrows` (acota) o, si de verdad contradice, es un bug del doc que hay que resolver, no documentar.
- `requires` es para **comprensión**, `assumes` es para **validez**. Regla práctica: si al quitar la otra sección esta se vuelve *incomprensible* → `requires`; si se vuelve *comprensible pero potencialmente falsa* → `assumes`.

### 11.2. Dirección de la arista

**Siempre la declara la sección dependiente, apuntando "hacia arriba"** (hacia aquello de lo que depende). Nunca una sección declara quién depende de ella.

Motivo: es local. Se escribe o edita una sección sin tocar ninguna otra. Es el mismo modelo que `import` en código: el módulo que necesita algo lo importa; el módulo importado no lista a sus consumidores.

### 11.3. Formato del bloque

Bloque al inicio de la sección, inmediatamente bajo el header, antes de cualquier contenido. Aristas ausentes se omiten (no se escribe `requires: []`). Los IDs son los IDs estables del [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15).

```
## auth-token-refresh
requires: [auth-token-model, auth-session-fsm]
assumes:  [auth-clock-source]
narrows:  [config-timeouts]
```

### 11.4. Algoritmo de carga (lo que hace el lector-modelo)

```
Para responder una pregunta cuyo anclaje es la sección S:

1. cargar S
2. R := cierre transitivo de `requires` empezando en S
   cargar todo R  (obligatorio en contexto — sin esto, S es incomprensible)
3. A := unión de `assumes` de S y de cada sección de R
   cargar todo A
   para cada sección de A: verificar que su contenido actual sigue
   satisfaciendo lo que S (o la sección de R) asume
   NO cerrar transitivamente A
     (una sección que S asume puede tener sus propios `assumes`;
      esos no entran salvo que también sean asumidos por S directamente —
      la cadena de validez no se propaga sola)
4. `narrows` NO se carga en este sentido. Solo es relevante al revés:
   si S es target de un `narrows` de otra sección N, y la pregunta
   toca el caso acotado, cargar N.
   → requiere un índice inverso de `narrows` a nivel de documento
     (lo genera pv-internal-doc-technical al escribir, no el lector).
```

Consecuencia práctica: para una consulta puntual el lector-modelo carga `S ∪ R ∪ A` (más algún `narrows`-inverso si aplica), no el documento entero. `R` es típicamente pequeño y estable; `A` es donde está el riesgo de desactualización y por eso se verifica, no solo se lee.

### 11.5. Validación (la ejecuta pv-internal-doc-technical, no el lector)

| Regla | Acción si falla |
|---|---|
| El grafo de `requires` es un DAG (sin ciclos). | Ciclo en `requires` ⟹ las secciones del ciclo se necesitan mutuamente para entenderse ⟹ **son una sola sección**: fusionarlas. El ciclo no se documenta, se elimina fusionando. |
| Ciclos en `assumes` sí se permiten. | Dos secciones pueden asumir cosas la una de la otra sin ser incomprensibles por separado. No es error. |
| Todo ID citado en `requires` / `assumes` / `narrows` existe. | ID colgante ⟹ error de doc, se corrige la cita o se crea la sección. |
| `narrows` no forma ciclo con otro `narrows`. | A `narrows` B y B `narrows` A ⟹ una de las dos acota mal; revisar cuál es la general. |

### 11.6. Ejemplo completo — documento de arquitectura de autenticación

IDs estables entre `< >`. Solo se muestran los bloques de aristas y una línea de contenido por sección para ver el grafo; el contenido real seguiría las demás reglas del documento.

```
## <auth-token-model>
   (sin aristas — sección raíz)
   token = { sub: string, iat: int, exp: int, scope: string[] }

## <auth-clock-source>
   (sin aristas — sección raíz)
   inv: todas las comparaciones de tiempo usan NTP-synced server clock, no client time

## <auth-session-fsm>
requires: [auth-token-model]
   estados: { ANONYMOUS, AUTHENTICATED, EXPIRED, REVOKED }
   (AUTHENTICATED, time > token.exp) → EXPIRED

## <auth-login-flow>
requires: [auth-token-model, auth-session-fsm]
   POST /login {user,pass} → 200 { token } ; estado: ANONYMOUS → AUTHENTICATED

## <auth-token-refresh>
requires: [auth-token-model, auth-session-fsm]
assumes:  [auth-clock-source]
narrows:  [config-session-ttl]
   POST /refresh (estado ∈ {AUTHENTICATED, EXPIRED}, dentro de refresh-window) → 200 { token' }
   [gotcha] refresh permitido en estado EXPIRED si (now - token.exp) < 7d

## <config-session-ttl>
requires: [auth-token-model]
   token.exp - token.iat = 3600  (configurable vía SESSION_TTL_SECONDS)

## <auth-logout>
requires: [auth-session-fsm]
   POST /logout → estado: * → REVOKED ; token añadido a denylist hasta su exp original
```

Lecturas que habilita el grafo, sin leer el doc entero:

| Pregunta | Anclaje S | Carga en contexto (S ∪ R ∪ A) |
|---|---|---|
| "¿Cómo se renueva un token?" | `auth-token-refresh` | `auth-token-refresh`, `auth-token-model`, `auth-session-fsm` (R), `auth-clock-source` (A, a verificar), + `config-session-ttl` por el `narrows` inverso |
| "¿Qué contiene un token?" | `auth-token-model` | solo `auth-token-model` (sección raíz, sin aristas) |
| "¿Qué pasa al hacer logout?" | `auth-logout` | `auth-logout`, `auth-session-fsm`, `auth-token-model` (R transitivo) |

Sin el grafo, cada una de esas preguntas obligaría a leer las 7 secciones para descubrir cuáles son relevantes. Con el grafo, la tercera columna se calcula sin leer contenido — solo los bloques de aristas.

### Nota pendiente: aristas entre secciones de documentos distintos

El ejemplo asume todas las secciones en un mismo fichero. Si `requires`/`assumes` apunta a un ID de otro fichero `docs.tech`, el algoritmo de carga 11.4 no cambia (los IDs del [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) ya son globales al proyecto), pero el índice inverso de `narrows` (paso 3 de 11.5) pasa a ser de proyecto, no de documento. Pendiente de decidir si ese índice inverso vive en el `00-glossary.md` (nota del [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado)) o en un artefacto propio generado por `pv-internal-doc-technical`.

</details>

## 12. Invariantes como asserts ejecutables — ABSORBIDO POR EL 13

El [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado) ya obliga a que los invariantes vayan en notación, nunca en prosa (fila "Invariante booleana / pre-post-condición" de su tabla). Este punto es una **restricción adicional sobre esa misma fila**, no una categoría nueva: cuando el invariante sea evaluable en runtime, la forma preferente es el assert ejecutable (`assert <expr>`), para fusionar doc + verificación. Se traslada al 13 como parte de la regla de esa fila (ver [13, fila "Invariante"](#tabla-contenido--notación--excepciones-a-prosa) y [13.6](#136-invariante-forma-ejecutable-vs-declarativa-absorbe-el-12)). El contenido sigue vivo dentro del 13; no está descartado. No queda incompatibilidad: el 13 pasa a ser la única fuente sobre cómo se escribe un invariante.

<details>
<summary>Idea original (absorbida por el 13)</summary>

En vez de (o además de) prosa, documentar invariantes como asserts en pseudo-código o código real testable (`assert token.expiry <= 3600`). Fusiona documentación y verificación en el mismo artefacto: si la regla cambia, el assert falla, en vez de depender de que alguien recuerde actualizar el texto.

</details>

## 13. Notación lógico-matemática o formato nativo para TODO; prosa SOLO excepción — REFACTORIZADO

Principio: **notación lógico-matemática o formato nativo es el default para todo tipo de contenido. Prosa es una excepción rara, solo donde la estructura lógica es insuficiente para capturar la semántica del argumento.**

No es optimización de forma — es reconocer que casi toda la estructura de software es captura de lógica, y la lógica ya tiene notación óptima. Prosa entra solo cuando hay semántica pura (motivación irreducible, causalidad narrativa) que la notación no puede llevar.

### Tabla: contenido → notación | excepciones a prosa

| Tipo de contenido | Notación óptima | Prosa se usa en... |
|---|---|---|
| Invariante booleana / pre-post-condición | Assert ejecutable (`assert <expr>`) si es evaluable en runtime; lógica proposicional declarativa (`pre:`, `post:`, `inv:`, `∧`, `∨`, `¬`, `→`, `⟹`, `∀`) si no. Ver [13.6](#136-invariante-forma-ejecutable-vs-declarativa-absorbe-el-12) | Nunca (estructura pura) |
| Estructura de datos (campos, tipos, defaults, opcionalidad) | Tabla o BNF compacto (`campo: tipo = default`) | Nunca (cartesiano, no narrativa) |
| Máquina de estados / transiciones | FSM o tabla `(estado, evento) → estado'` | Nunca (grafo de transiciones, no narrativa) |
| Relación/cardinalidad entre entidades | Diagrama ER o notación cardinalidad (`1---*`, `0..1`) | Nunca (relaciones, no narrativa) |
| Secuencia temporal / flujo de llamadas | Diagrama de secuencia (Mermaid) o pseudocódigo ordenado | Nunca (timeline, no narrativa) |
| Árbol de decisión / condicionales anidados | Tabla booleana o árbol explícito | Nunca (lógica pura) |
| Justificación/motivación de decisión | Regla/condición + tabla comparativa (ver Caso 1: casi siempre reducible; el principio general detrás ni se escribe, por [punto 5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo)) | Solo cuando la razón es una restricción externa idiosincrática (compliance, negocio) no generalizable ni reducible a condición |
| Descripción de flujo con efectos secundarios | Secuencia numerada / diagrama evento→efecto (ver Caso 2: raramente necesita prosa, "tiene efectos secundarios" no es motivo suficiente) | Solo la pieza puntual donde el efecto se explica por semántica externa (UX, negocio), no la secuencia completa |

### Ejemplos: NO entra prosa (parecía necesitarla, se redujo a notación)

#### Caso 1: decisión con regla generalizable

**Ejemplo:** "¿Por qué se eligió un circuit breaker en vez de reintentos exponenciales?"

Parece requerir prosa, pero se descompone en dos partes:

1. **La regla de decisión del proyecto** — expresable como tabla/condición, no prosa:
```
decision(dependency_recovery_time):
  < 5s  → circuit_breaker
  > 30s → exponential_retry
```
2. **El principio general detrás de la regla** ("fail-fast evita saturación en cascada cuando la recuperación es rápida") — esto es conocimiento general de ingeniería, no un hecho del proyecto. Por [punto 5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo), ni siquiera hace falta escribirlo — ya es inferible.

**"Es un trade-off" no es señal suficiente de que haga falta prosa.** Si el trade-off se puede reducir a una condición + un principio de ingeniería estándar, va todo a notación (o se omite, si es puro conocimiento general).

---

#### Caso 2: flujo de error con efectos secundarios

**Ejemplo:** "¿Qué pasa cuando un usuario intenta acceder a un recurso después de que la sesión expiró?"

Se podría pensar que esto necesita prosa porque hay efectos secundarios ("el 401 dispara un redirect, el JS limpia localStorage pero conserva un flag..."), pero **es una secuencia causal — sigue siendo lógica, solo con más pasos**. Se expresa completa en diagrama de secuencia o tabla evento→efecto, sin perder nada:

```
1. estado: AUTENTICADO, evento: time > session.expiry → estado: EXPIRADO
2. evento: GET /resource (estado=EXPIRADO) → respuesta: 401
3. efecto(401): redirect(login)
4. efecto(redirect capturado por cliente): localStorage.clear(EXCEPT lastAuth)
5. inv: lastAuth PERSISTE ⟹ modal("sesión perdida") == false
```

**"Hay efectos secundarios" no es señal de que haga falta prosa** — solo lo es cuando la razón del orden/efecto es semántica externa (UX, negocio, trade-off), no la secuencia en sí. El resto es notación pura.

---

#### Caso 3: alternativas descartadas

**MAL (prosa innecesaria):**
> "Consideramos usar polling cada 5 segundos, pero eso era ineficiente en conexiones lentas. Tampoco usamos long-polling porque en un contexto móvil mantener conexiones HTTP abiertas vacía la batería más rápido que la alternativa."

**BIEN (tabla comparativa, batería como columna más — no semántica irreducible):**
```
| Opción | Latencia | Carga (CPU) | Carga (red) | Consumo batería (móvil) | Costo |
|--------|----------|-------------|------------|--------------------------|-------|
| Polling 5s | ~5s | Alto | Alto (picos) | Medio | $ |
| WebSocket | ~100ms | Bajo | Bajo (continuo) | Bajo | $$ |
| SSE | ~500ms | Bajo | Bajo (stream) | Bajo | $ |
| ❌ DESCARTADO: Long-polling | ~1s | Muy alto | Muy alto | Alto (conexión persistente) | $$$ |
```

**Patrón que se repite en los tres casos:** lo que parece "semántica irreducible" casi siempre es una dimensión más del mismo espacio de comparación — solo hacía falta ampliar la tabla/regla, no huir a prosa.

---

### Ejemplos: SÍ entra prosa (excepción real, sobrevive el escrutinio)

#### Restricción externa idiosincrática (compliance, sobre el Caso 1)

> "Se descartó el circuit breaker automático porque el equipo de compliance exige que cada apertura del breaker quede registrada con aprobación manual, algo que la librería estándar no soporta sin un wrapper custom."

Prosa aquí porque: no reduce a condición booleana del sistema ni es principio de ingeniería generalizable — es una restricción de negocio específica de este proyecto, impuesta por un actor externo (compliance).

#### Comentario semántico puntual sobre un invariante (sobre el Caso 2)

```
5. inv: lastAuth PERSISTE ⟹ modal("sesión perdida") == false
   [motivación] Evita falso positivo cuando el usuario solo cerró pestaña, no expiró por inactividad.
```

Prosa aquí porque: el invariante en sí ya es notación; solo la razón de *por qué existe* esa regla (UX, no lógica del sistema) necesita una frase — y se marca `[motivación]`, no un párrafo.

---

### Regla de aprobación (endurecida)

- **Default:** notación lógico-matemática o formato nativo, sin excepción de tipo de contenido — toda fila de la tabla original cae aquí, incluidas justificación y narrativa de flujo (ver Casos 1–3: ninguno sobrevivió como excepción real).
- **Prosa:** reservada exclusivamente para una restricción externa idiosincrática del proyecto (legal, compliance, contractual, organizacional) que no es una métrica comparable ni un principio de ingeniería generalizable — y aun así, en una frase corta, no un párrafo.
- **Antes de escribir prosa, checklist obligatorio:**
  1. ¿Es esto una condición/regla? → tabla de decisión o lógica proposicional.
  2. ¿Es esto una métrica más de una comparación ya tabulada? → agregar columna.
  3. ¿Es esto un principio general de ingeniería inferible por el modelo? → no escribir nada ([punto 5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo)).
  4. Si ninguna de las tres aplica → prosa, marcada `[motivación]`, una frase.
- **Nunca:** forzar prosa por elegancia, fluidez de lectura, o porque "suena a trade-off". Un trade-off casi siempre es una tabla con más columnas.

### 13.6. Invariante: forma ejecutable vs. declarativa (absorbe el 12)

El [punto 12](#12-invariantes-como-asserts-ejecutables--absorbido-por-el-13) queda absorbido aquí: no era una categoría de contenido nueva, era una regla sobre *cómo* se escribe la fila "Invariante" de la tabla. La fila ya prohíbe prosa; el 12 añade que, **cuando el invariante sea evaluable en un punto concreto del programa, se escriba como assert ejecutable** — así doc y test son el mismo artefacto y un cambio en la regla rompe el test.

Criterio de elección (mecánico, no de juicio):

| Pregunta | Sí | No |
|---|---|---|
| ¿Existe un punto del programa (entrada de función, transición, fin de operación) donde esta condición se puede comprobar con los valores en mano? | **Assert ejecutable**: `assert token.exp - token.iat <= 3600` | **Lógica declarativa**: `inv: ∀ s ∈ sessions · s.exp > s.iat` |
| ¿La condición habla de un estado observable en runtime (campos, variables, retorno)? | Assert ejecutable | — |
| ¿La condición cuantifica sobre un conjunto abstracto, habla de un estado de una FSM, o de una propiedad global no observable en un solo punto? | — | Lógica declarativa |

Reglas:
- **Forma preferente = assert ejecutable siempre que el criterio dé "sí".** La lógica declarativa no es un estilo alternativo libre: es el fallback para lo que no se puede evaluar en runtime.
- Un mismo invariante puede tener **las dos formas** si aporta: el assert como forma normativa verificable, la declarativa como enunciado general. En ese caso el assert manda; la declarativa va marcada como enunciado, no se duplican como si fueran hechos distintos.
- La sintaxis exacta del assert (lenguaje real del proyecto vs. pseudocódigo) y de la lógica declarativa (juego de símbolos) las fija el `00-glossary.md` (nota siguiente), una sola vez para todo `docs.tech`.
- El `[motivación]` de una frase sobre *por qué existe* el invariante (ver [Caso 2 / comentario semántico](#comentario-semántico-puntual-sobre-un-invariante-sobre-el-caso-2)) aplica igual a las dos formas.

No queda incompatibilidad entre 12 y 13: **el 13 es la única fuente sobre cómo se escribe un invariante**, y la regla ejecutable-vs-declarativa está integrada en su tabla y en esta subsección.

### Nota pendiente: glosario de notación único por proyecto

Riesgo detectado: "notación con precedente amplio" (contratos, FSM, tablas, etc.) puede variar de doc a doc dentro del mismo proyecto si cada uno la reinventa a su manera (uno usa `pre:/post:`, otro `requires:/ensures:`) — mismo problema que resuelven el [punto 9](#9-nombres-de-sección-fijos-entre-documentos) (secciones) y el [punto 10](#10-un-único-término-por-concepto--absorbido-por-el-15) (vocabulario), pero sin cubrir aún a nivel de notación.

Acción: `pv-internal-doc-technical` debe crear siempre un fichero `00-glossary.md` donde se documente toda la notación (símbolos, convenciones de contrato, formato de tablas de decisión, notación de FSM/cardinalidad, etc.) que aplicará de forma consistente a toda la documentación `docs.tech` del proyecto — una sola fuente de verdad para la notación, igual que el punto 4 lo es para IDs citables.

Pendiente de detallar: contenido exacto del glosario, si se genera una vez o se actualiza incrementalmente, y su relación con la implementación ya definida en `pv-internal-doc-technical-optimizacion_v1.md` (que no se toca en esta discusión).

### Nota pendiente: notación anidada/híbrida entre tipos de contenido

Riesgo detectado: la tabla del punto 13 asigna una notación nativa por tipo de contenido asumiendo que cada pieza de información cae limpiamente en una sola fila, pero en la práctica un tipo de contenido frecuentemente depende de otro:

- Un invariante booleano que referencia un estado de una máquina de estados: `pre: state == AUTHENTICATED`.
- Una tabla de decisión donde una celda no es un valor simple sino que requiere, a su vez, un contrato completo (`pre:`/`post:`) para esa combinación de condiciones.
- Un diagrama de secuencia donde un paso individual dispara una transición de FSM documentada en otra sección.

Sin una regla para este caso, quien escriba el doc tiene dos escapes problemáticos: (a) anidar la segunda notación inline dentro de la primera, generando una notación híbrida ad-hoc no cubierta por ningún estándar de precedente amplio (exactamente el problema que el punto 13 quiere evitar), o (b) recurrir a prosa "para no anidar", que es el escape que el punto 13 entero busca cerrar.

Opciones a evaluar (sin decidir aún):
1. **Referencia por ID en vez de anidar** — conectando con el [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15): la celda/condición no repite la notación ajena, solo la cita (`pre: state == AUTHENTICATED [ver fsm-auth#AUTHENTICATED]`).
2. **Notación compuesta explícita** — el `00-glossary.md` (nota anterior) define cómo se combinan dos notaciones nativas cuando aparecen juntas (p. ej. cómo se escribe una celda de tabla de decisión que a su vez es un contrato), en vez de dejarlo a criterio de quien escribe cada doc.

Pendiente de decidir cuál de las dos (o ambas, según el caso) adopta `pv-internal-doc-technical`; probablemente ligado a la implementación del glosario de notación, no un mecanismo aparte.

## 14. Inglés técnico como idioma del documento — APROBADO

Encaja con la premisa raíz del documento: se optimiza exclusivamente para el lector-modelo, no para lectores humanos — por lo tanto el idioma también es una variable de optimización, no una convención fija a respetar por legibilidad humana.

Hipótesis (razonada, no medida): el inglés técnico tokeniza mejor que el español para este dominio, por dos motivos estructurales:

1. **Los identificadores de código ya están en inglés** (nombres de campos, métodos, tipos, clases). Un doc en español mezcla constantemente dos idiomas dentro de la misma frase ("el campo `sessionExpiry` determina..."), lo cual no reduce tokens — el identificador no cambia, y la prosa alrededor sigue en español. Un doc en inglés técnico es monolingüe de principio a fin.
2. **El vocabulario técnico en inglés (`state`, `invariant`, `token`, `session`, `expiry`) tiene, con alta probabilidad, mayor frecuencia en el corpus de entrenamiento técnico específico** (código, RFCs, specs, papers de CS, docs de APIs) que sus traducciones al español ("estado", "invariante", "token", "sesión", "caducidad"). Mayor frecuencia en corpus técnico generalmente correlaciona con mejor tokenización (más probable que sea un token único o casi-único) — mismo argumento que ya usamos en el punto 13 para preferir notación con precedente amplio sobre notación inventada.

Lo que NO se puede sostener sin medir (por la regla 8 del propio documento — nada de cifras sin verificar):
- Cuánto ahorro real de tokens hay — no tengo acceso a mi propia tabla de frecuencias de tokenización, es una hipótesis razonada, no un hecho medido.
- Que el ahorro por idioma sea comparable o mayor al ahorro ya logrado por el punto 13 (notación vs. prosa) — mi sospecha es que es menor, pero no está verificado.

Riesgo/costo a considerar (no de legibilidad humana, sino de alcance de la migración):
- Implica traducir todo el corpus `docs.tech` existente y ajustar `pv-do`/`pv-internal-doc-technical` para que generen en inglés por defecto — cambio de alcance mayor que una regla de estilo, es un cambio de política de idioma para toda la skill.
- Si el proyecto base (nombres de negocio, dominio, requisitos funcionales en `docs.features` u otros) está en español, hay que decidir si `docs.tech` queda como única isla en inglés dentro del proyecto, y cómo se resuelve la terminología de dominio que no tiene traducción técnica estándar (nombres de conceptos de negocio específicos del cliente).

Pendiente de detallar (no de aprobación): si aplica a todo `docs.tech` o solo a la notación/vocabulario técnico (dejando prosa de motivación en español) — este último enfoque sería coherente con el punto 13, que ya trata notación y prosa como capas separables. La terminología de dominio/negocio sin traducción técnica estándar (ver riesgo arriba) también queda por resolver.

### Implicación verificada: revierte una decisión de diseño ya implementada

`pv-internal-doc-technical/SKILL.md` (líneas 14, 18, 35-41) implementa hoy lo contrario de esta propuesta: **independencia de idioma deliberada**. El doc declara explícitamente una sección "Language-independence" que:
- Aplica el writing style "regardless of topic or configured `docs.tech.language`" (línea 14).
- Descarta técnicas de compresión que dependen de gramática inglesa específica (compound-noun stacking, línea 40) precisamente para que las reglas transfieran sin cambios a cualquier `docs.tech.language`.
- Confirma que existe hoy una opción de configuración `docs.tech.language` (default `interaction.language`) que el usuario puede elegir.

Aprobar el punto 14 no es "agregar una regla más" — es **revertir esa decisión**: pasar de "las reglas son agnósticas de idioma, el usuario elige" a "el idioma se fija en inglés técnico, se elimina `docs.tech.language` como opción". Eso afecta tanto a la doc de arquitectura como a la de diseño (`architectureDocDir`/`styleBibleDocDir`, ambas cubiertas por esta skill).

Este documento de ideas no decide si se aprueba — solo deja constancia de que, si se aprueba, el cambio no es aditivo: requiere reescribir la sección "Language-independence" de `SKILL.md` (pasaría a ser una sección de "fixed language" en su lugar) y eliminar la opción `docs.tech.language` de la configuración del framework. Ese trabajo de implementación, si se decide seguir adelante, corresponde a `_v1.md` u otro plan de implementación — no a este documento.

## 15. Namespace jerárquico único, vinculado al código — APROBADO

Absorbe el [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) (IDs citables entre docs) y el [punto 10](#10-un-único-término-por-concepto--absorbido-por-el-15) (término único por concepto). Los puntos 4, 7, 9 y 10 comparten el espíritu "lenguaje preciso e inequívoco", pero operan sobre objetos distintos; de ellos, **solo 4 y 10 nombran un elemento** y se pueden unificar en un único sistema de nombres. El 7 es regla de redacción (prohíbe anáfora, no aporta identificador) y el 9 es organización física del `.md` (ortogonal). Ver [15.3](#153-relación-con-los-puntos-7-y-9) para por qué 7 y 9 quedan fuera.

### 15.1. El esquema

Un árbol de nombres único por proyecto. Cada elemento —concepto o afirmación— tiene **una sola ruta canónica**, con segmentos separados por puntos, de agregado a detalle.

```
auth.token.session                       → concepto. ancla: src/auth/token.ts#SessionToken
auth.token.session.exp                   → concepto (campo). ancla: SessionToken.exp
auth.token.session.ttl                   → concepto. ancla: SESSION_TTL_SECONDS
auth.token.session.ttl.value = 3600      → afirmación. "el TTL de sesión es 3600 s"
auth.token.session.refresh.grace = 7d    → afirmación. "refresh permitido hasta exp + 7d"
auth.decision.circuit-breaker-over-retry → decisión. sin ancla de código (es una elección)
```

### 15.2. Reglas del árbol

| Elemento | Forma | Qué era antes | Regla |
|---|---|---|---|
| **Nodo con ancla de código** | segmento sin `=`, con `ancla: file#symbol` | término único del [punto 10](#10-un-único-término-por-concepto--absorbido-por-el-15) | El nombre canónico **es** la ruta; la definición vive en el código, no en la doc. La unicidad es estructural: no hay dos rutas para el mismo nodo. |
| **Hoja `ruta = valor`** | segmento terminal con `= <escalar>` | ID citable del [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) | Es lo citable entre docs: `ver auth.token.session.ttl.value`. Una sola sintaxis de cita en todo el proyecto. |
| **Rama `ruta.decision.<slug>`** | subárbol reservado bajo `decision.` | decisión del [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) | Afirmación sin ancla de código (una elección de diseño). Citable igual que una hoja `=valor`. |
| **Nodo sin ancla y sin `=`** | — | — | **Sospechoso**: o falta el ancla, o es conocimiento general ([punto 5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo)) y no debería estar nombrado. Lo marca la validación. |

Frontera concepto/afirmación (lo que en la antigua [4.3](#inc-153-punto-15--punto-10-un-único-término-por-concepto--resuelta-por-construcción) era criterio difuso, aquí es sintáctico): **¿tiene `= valor` o cuelga de `.decision.`?** → afirmación. **¿no?** → concepto. No hay juicio: la forma lo decide.

### 15.3. Relación con los puntos 7 y 9

| Punto | Objeto | ¿Entra en el namespace? |
|---|---|---|
| [7](#7-prohibir-referencias-anafóricas--aprobado) — prohibir anáfora | El referente de un pronombre ("esto", "dicho campo") dentro de una frase | **No.** El 7 no crea identificadores: prohíbe *dejar de repetir* el nombre que ya existe. Con el 15 se reformula como corolario: "el identificador válido para citar es la ruta del namespace; nunca una anáfora ni un sinónimo". |
| [9](#9-nombres-de-sección-fijos-entre-documentos) — headers fijos | La sección del documento como contenedor estructural | **No.** El 9 organiza el `.md` en ficheros y títulos; el 15 nombra elementos del sistema. Son capas distintas: se puede tener un namespace perfecto y aun así discutir cómo se titula cada `.md`. Choque residual en [Incompat. 15.1](#inc-151-punto-15--punto-9-nombres-de-sección-fijos). |

### 15.4. Qué resuelve respecto a 4 y 10 por separado

- **Un solo mecanismo** da vocabulario único (nodos) y afirmaciones citables (hojas). Desaparecen las antiguas incompatibilidades 4.2 y 4.3 (ver [Incompat. 15.2](#inc-152-punto-15--punto-13-afirmaciones-no-escalares) y [15.3](#inc-153-punto-15--punto-10-un-único-término-por-concepto--resuelta-por-construcción)): la frontera concepto/hecho es sintáctica y la sintaxis de cita es una sola (`ruta.punteada`).
- **Vínculo al código verificable**: cada nodo-concepto tiene `ancla`. `pv-internal-doc-technical` comprueba que la ancla existe; ancla rota = error de validación. El drift que el [punto 1](#1-metadata-de-verificación-contra-código--descartado) (descartado) no supo atacar aquí es detectable.
- **Cita entre docs con una sintaxis**: `auth.token.session.ttl.value`. Se acaba `ver docs.tech#id` vs `[ver id]` del [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado).

### 15.5. Pendiente de decidir

1. **Orden de segmentos.** `auth.token.session` vs `auth.session.token`. Necesita una convención fija (de módulo a detalle / de agregado a parte) y una autoridad que asigne rutas — probablemente el `00-glossary.md` del [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado).
2. **Afirmaciones no escalares.** "refresh permitido en estado `EXPIRED` si `now - exp < 7d`" no es `clave = valor`. ¿Se fuerza a `auth.token.session.refresh.grace = 7d` asumiendo el resto, o la hoja apunta a un bloque de notación? Es la nota de notación anidada del [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado). Desarrollado en [Incompat. 15.2](#inc-152-punto-15--punto-13-afirmaciones-no-escalares).
3. **Coste de mantenimiento del árbol** al refactorizar el código: renombrar `SessionToken` obliga a renombrar `auth.token.session` y todas sus hojas. Mitigable si la validación detecta la ancla rota, pero la re-asignación de ruta es manual.
4. **Relación con `docs.tech.language` ([punto 14](#14-inglés-técnico-como-idioma-del-documento--aprobado))**: los segmentos del namespace salen de nombres de código (inglés), coherente con el 14; queda por decidir si un concepto de dominio sin símbolo de código usa slug en inglés o en el idioma del proyecto.

## Ganancia en la fase de análisis

Detalle de la columna **Ganancia** del índice. Criterio único: valor para la **fase de análisis de una tarea cualquiera** — el trabajo de `pv-internal-tech-analysis` (leer `docs.tech`, reconstruir la definición completa de cada interfaz/estructura tocada, detectar dónde el proyecto se desvía del patrón esperable, no concluir en falso rellenando huecos con el default). No se valora aquí el coste de implementar el punto ni su efecto sobre otras fases (redacción, revisión, versión).

Escala:
- **Alta** — golpea el núcleo del análisis: o convierte contenido que había que *parsear* en contenido que se *lee directo* (estructura), o marca justo el punto donde el análisis se equivoca (la excepción al patrón). Efecto en casi toda tarea.
- **Media** — reduce coste o ambigüedad puntual (una pasada extra de desambiguación, una reconciliación entre dos redacciones, localizar dónde está lo que se busca) sin cambiar lo que se entiende una vez localizado. Efecto acotado a las tareas donde aplica.
- **Baja** — higiene de redacción, efecto marginal sobre la comprensión, o ganancia no verificable sin medición.

| # | Ganancia | Qué se gana en análisis (punto implementado en solitario) | Qué la limita |
|---|----------|-----------------------------------------------------------|---------------|
| [2](#2-tag-de-anti-expectativa--aprobado) `[gotcha]` | **Alta** | El error más caro del análisis es asumir el patrón común (`delete` borra, `getX` no muta, la sesión expira sola) donde el proyecto hace la excepción. `[gotcha]` marca exactamente esas líneas, que si no se pierden entre filas que solo confirman lo obvio. Ataca la fuente directa de conclusiones erróneas. | Depende de que quien escribe identifique bien la anti-expectativa; un `[gotcha]` omitido no deja rastro. |
| [4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) | Media | Menos drift entre documentos: una regla compartida se cita, no se re-redacta, así que no hay que reconciliar dos versiones de la misma afirmación durante el análisis. | Solo aparece cuando la tarea toca varios docs que comparten una invariante. Absorbido por el [15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado), que lo hace mejor. |
| [5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo) | Media | Menos texto que leer y descartar: lo que ya se infiere por conocimiento general (sigue REST, hashea contraseñas) no ocupa líneas ni distrae de lo específico del proyecto. | Acelera, no cambia lo que se entiende. Y depende de un criterio difuso ("¿esto es obvio para el modelo?") más frágil que las reglas mecánicas. |
| [6](#6-notación-compacta-en-vez-de-prosa-para-datos-estructurados--aprobado) | **Alta** | El análisis exige la definición completa de cada estructura tocada (tipo, default, opcionalidad de cada campo). `timeout: number = 30s (opcional)` se extrae sin ambigüedad; la misma información en prosa hay que parsearla y es donde se cuela el error ("¿el default era 30 o el mínimo?"). Golpea el núcleo del trabajo, en casi toda tarea. | Ninguna relevante para análisis; es ganancia casi pura. |
| [7](#7-prohibir-referencias-anafóricas--aprobado) | Media | Resolver "esto" / "dicho campo" / "el mismo" cuesta una pasada extra de desambiguación y a veces se resuelve mal si hay dos candidatos cerca. Repetir el nombre exacto elimina ese coste. | Ambigüedad puntual, no reestructura el contenido. El efecto agregado es real pero pequeño frente a 6 o 13. |
| [8](#8-prohibir-adjetivosadverbios-de-intensidad-sin-cifra--aprobado) | Baja | Un "muy rápido" / "poco frecuente" sin cifra se descarta como no-información igualmente; forzar la cifra da un dato usable cuando existe. | Sobre todo higiene de redacción. Cuando no hay cifra, el punto solo suprime ruido que ya se ignoraba. |
| [9](#9-nombres-de-sección-fijos-entre-documentos) | Media | *Jump-to-section* por convención: se localiza "Contracts" / "Invariants" / "Decisions" en cualquier doc sin leer su índice. Acelera la localización dentro de un corpus grande. | No cambia la comprensión del contenido una vez localizado. Y su propia viabilidad (catálogo de secciones universal) está sin cerrar. |
| [10](#10-un-único-término-por-concepto--absorbido-por-el-15) | Media | Un término único por concepto elimina la resolución de sinonimia (¿"endpoint", "ruta" y "handler" son lo mismo aquí?), que puede fallar y llevar a tratar dos menciones como cosas distintas. | Subconjunto de lo que el [15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) hace de forma estructural. Aislado, es solo disciplina léxica. |
| [11](#11-grafo-de-dependencias-explícito-entre-secciones--descartado) | Baja | En documentos grandes, saber qué otras secciones cargar antes de confiar en una evita leer el doc entero para una consulta puntual. | El coste que ahorra (leer secciones de más) es menor que el que ataca el 13 (entender mal las que sí se leen). Depende de infraestructura (IDs, secciones, índice inverso). Descartado. |
| [12](#12-invariantes-como-asserts-ejecutables--absorbido-por-el-13) | Media | Un invariante como `assert token.exp - token.iat <= 3600` se lee sin ambigüedad y, si el test existe, se sabe que sigue vivo — no hay que verificarlo contra el código. | Acotado a invariantes evaluables en runtime. Absorbido por el [13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado). |
| [13](#13-notación-nativa-por-tipo-de-contenido-prosa-solo-donde-no-hay-forma-mejor--aprobado) | **Alta** | Convierte cada contrato, FSM, tabla de decisión, relación y flujo de prosa-a-parsear en estructura que se lee directa. Es el punto que más reduce a la vez el coste (menos parsing) y el error (menos relleno con el patrón) del análisis, y aplica en cada documento, no solo cuando la tarea cruza varios. | Ninguna relevante para análisis. Zona gris solo en la motivación irreducible, que es marginal en volumen. |
| [14](#14-inglés-técnico-como-idioma-del-documento--aprobado) | Baja | Hipótesis de mejor tokenización del vocabulario técnico en inglés y de un doc monolingüe (sin mezcla español + identificadores en inglés). | No medida (regla 8 del propio documento). Sin cifra que respalde el ahorro, no se puede afirmar ganancia real de análisis. |
| [15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) | **Alta** | Cada concepto y cada afirmación tiene una ruta canónica única (`auth.token.session.ttl.value`) vinculada al código por `ancla:`. Elimina de golpe la sinonimia, el drift entre docs y la duda "¿esto es lo mismo que aquello?", y da un punto de verificación contra el código para cada nodo. Cubre lo de 4 y 10 y añade el anclaje verificable. | La ganancia plena depende de resolver las notas pendientes (afirmaciones no escalares, orden de segmentos); el esqueleto ya rinde. |

## Incompatibilidades

Sección de trabajo. Registra pares de propuestas que se pisan, se estorban, o cuya combinación genera un problema que ninguna de las dos tiene por separado. Se analizan aquí las propuestas que estén o hayan estado en estado ✅ aprobado (la contraparte puede estar en cualquier estado). La columna "Incompatible With" del índice enlaza a la subsección correspondiente. Una subsección se mantiene aunque una de las dos propuestas pase luego a descartada — queda como registro de por qué chocaban (ver [punto 11](#11-grafo-de-dependencias-explícito-entre-secciones--descartado), descartado tras el análisis 11.3).

Nomenclatura de severidad:
- **Bloqueante** — las dos no pueden coexistir sin resolver antes una decisión de diseño; aprobar ambas tal cual produce contradicción.
- **Fricción** — coexisten, pero una encarece o degrada a la otra; conviene un ajuste explícito.
- **Solapamiento** — hacen parcialmente lo mismo; riesgo de redundancia o de divergencia entre las dos implementaciones.

### INC-15.1. Punto 15 ↔ Punto 9 (nombres de sección fijos)

**Severidad: fricción.** (Heredada de la antigua 4.1; sigue abierta.)

El [punto 15](#15-namespace-jerárquico-único-vinculado-al-código--aprobado) cuelga la **definición** de cada nodo/hoja del namespace en algún punto de un `.md`. El [punto 9](#9-nombres-de-sección-fijos-entre-documentos) (en análisis) fija un conjunto cerrado de headers de categoría repetidos en todos los docs. El choque es a qué nivel del documento vive esa definición.

| Aspecto | Punto 9 pide | Punto 15 necesita |
|---|---|---|
| Unidad con identidad en el `.md` | La sección de categoría (`## Invariants`), compartida entre docs | El nodo/hoja concreto (`auth.token.session.ttl.value = 3600`) |
| Nº de anclas por doc | Fijo (uno por header del conjunto cerrado) | Variable (uno por nodo/hoja definido en ese doc) |
| Reutilización del identificador | El mismo header se repite en todos los docs | Cada ruta del namespace es única y global |

Si el punto 9 se aprueba con **secciones atómicas** (una sola "Invariants" con N invariantes dentro), el lector que llega desde una cita `ver auth.token.session.ttl.value` aterriza en la sección "Config" entera y tiene que buscar la hoja. El namespace da el identificador exacto; el 9, tal cual, no da un ancla física igual de exacta.

Resolución candidata (pendiente, ligada a cerrar el punto 9): **dos niveles**. El punto 9 fija los headers de nivel 1; cada nodo/hoja del punto 15 se define en un **bloque identificable dentro de esos headers**, anclado por su ruta del namespace. `jump-to-section` por header sigue funcionando; la cita del namespace apunta al bloque. Requiere que el punto 9, al aprobarse, declare sus secciones como contenedores de bloques identificables, no unidades atómicas. Misma resolución que se había propuesto para la antigua 11.2.

### INC-15.2. Punto 15 ↔ Punto 13 (afirmaciones no escalares)

**Severidad: fricción.** (Sustituye a la antigua 4.2, que era "solapamiento de sintaxis de cita" — ese solapamiento **ya está resuelto por construcción** en el 15: ver más abajo. Lo que queda abierto es otra cosa.)

**Lo que el 15 resolvió y ya no es incompatibilidad:** la antigua 4.2 registraba dos sintaxis de cita compitiendo (`ver docs.tech#id` del punto 4 vs `[ver id]` inline del punto 13). Con el 15 hay **una sola**: la ruta punteada (`auth.token.session.ttl.value`). El `00-glossary.md` del [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado) documenta esa sintaxis, no inventa otra. La frontera concepto/afirmación que la antigua 4.3 marcaba como criterio difuso es ahora **sintáctica** (¿tiene `= valor` o cuelga de `.decision.`?), no de juicio. Ninguna de las dos sobrevive como incompatibilidad.

**Lo que sigue abierto:** el [punto 15.1 (esquema)](#151-el-esquema) modela las afirmaciones como `ruta = <escalar>`. Pero muchas afirmaciones de arquitectura **no son escalares**:

```
"refresh permitido en estado EXPIRED si  now - token.exp < 7d"
"el breaker abre tras 5 fallos consecutivos en menos de 10s"
```

Eso no es `clave = valor`; es una expresión lógica — justo el territorio del [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado) (lógica proposicional, contratos, tablas de decisión). Choque: el 15 quiere una hoja citable con nombre estable; el 13 quiere que el contenido de esa hoja sea notación, no un escalar. Dos escapes malos:

- **(a)** Forzar todo a escalar (`auth.token.session.refresh.grace = 7d`) y perder la condición completa (`estado EXPIRED`, `consecutivos`, la ventana de 10s) — el nombre miente por omisión.
- **(b)** Meter notación multilínea como "valor" de la hoja, y entonces la hoja deja de ser un identificador citable limpio y pasa a ser un bloque — que es la nota de **notación anidada/híbrida** del punto 13, sin resolver.

Resolución candidata (pendiente, ligada al `00-glossary.md`): la hoja del namespace **identifica** la afirmación (nombre estable, citable) pero su **cuerpo es un bloque de notación del 13**, no un escalar. Es decir:

```
auth.token.session.refresh.rule:
    pre:  state ∈ {AUTHENTICATED, EXPIRED} ∧ now - token.exp < 7d
    post: token'.iat = now ∧ token'.exp = now + auth.token.session.ttl.value
```

`auth.token.session.refresh.rule` se cita como cualquier hoja; su contenido es notación proposicional, no `= valor`. El `00-glossary.md` define la frontera: **hoja `= <escalar>`** para valores simples (un número, un enum, un booleano); **hoja `:` + bloque de notación** para afirmaciones con estructura lógica. Ambas son citables por ruta; la forma del cuerpo la decide si el hecho es un escalar o una expresión.

### INC-15.3. Punto 15 ↔ Punto 10 (un único término por concepto) — resuelta por construcción

**Sin incompatibilidad.** El [punto 10](#10-un-único-término-por-concepto--absorbido-por-el-15) está **absorbido** por el 15: los nodos del namespace *son* los términos únicos por concepto. La frontera concepto/afirmación que la antigua 4.3 marcaba como criterio difuso ("¿esto es concepto o hecho?") pasa a ser sintáctica en el 15 (`= valor` / `.decision.` → afirmación; en otro caso → concepto). No queda nada que registrar como choque; se deja esta entrada solo como puntero desde la columna del índice.

### INC-15.4. Punto 15 ↔ Punto 1 (metadata de verificación) — histórico

**Sin incompatibilidad activa** ([punto 1](#1-metadata-de-verificación-contra-código--descartado) descartado). Se conserva como **guía de implementación del 15**: el 15 sirve bien a afirmaciones estables (decisiones, invariantes de diseño) y mal a "snapshots del código" (listados de campos, firmas). Un nodo del namespace sobre una firma concreta hereda el drift silencioso que el punto 1 no supo atacar. Guía: dar ruta de namespace a decisiones e invariantes; **no** dar ruta a listados de campos/firmas — esos apuntan al código por la regla 5 (`ancla:`), no se les crea una hoja `=valor` propia.

### 11.1. Punto 11 ↔ Punto 3 (orden por frecuencia de consulta)

**Severidad: solapamiento (histórico — punto 3 descartado).**

El [punto 3](#3-orden-por-frecuencia-de-consulta--descartado) (descartado) buscaba front-loading de las secciones más consultadas para mitigar la lectura parcial. El punto 11 ataca el mismo problema — lectura no secuencial, carga parcial del documento — pero por otra vía: en vez de reordenar por una heurística de frecuencia no medible, hace explícito el grafo de dependencias para que el lector-modelo calcule `S ∪ R ∪ A` sin leer el resto.

No es incompatibilidad activa (el punto 3 está descartado), pero se deja constancia de que **el punto 11 es la razón adicional para mantener el punto 3 descartado**: el problema que el punto 3 intentaba resolver queda cubierto por el grafo, sin depender de telemetría ni de heurísticas de orden. Si en el futuro se reabriera el punto 3, chocaría de frente: reordenar secciones por frecuencia y a la vez declarar dependencias explícitas mete dos criterios de orden en el mismo documento.

### 11.2. Punto 11 ↔ Punto 9 (nombres de sección fijos)

**Severidad: fricción.**

El [punto 9](#9-nombres-de-sección-fijos-entre-documentos) (en análisis) propone un conjunto cerrado de headers literales repetidos en todos los docs `docs.tech` ("Contratos", "Invariantes", "Decisiones descartadas", ...) para permitir *jump-to-section* por nombre. El punto 11 asume secciones con **IDs propios y granulares** (`<auth-token-refresh>`, `<config-session-ttl>`) sobre los que se declaran las aristas `requires` / `assumes` / `narrows`.

Los dos modelos de sección no encajan sin decidir a qué nivel vive cada cosa:

| Aspecto | Punto 9 pide | Punto 11 pide |
|---|---|---|
| Nº de secciones por doc | Fijo y pequeño (el conjunto cerrado de headers) | Variable, una por unidad de dependencia (puede haber 3 "Contratos" distintos con aristas distintas) |
| Identificador | El header literal, compartido entre docs | ID único global, no reutilizable |
| Granularidad | De categoría ("todos los invariantes juntos") | De hecho ("este invariante concreto que asume el reloj NTP") |

Si un doc tiene una sola sección "Invariantes" (punto 9) pero dentro hay tres invariantes con `assumes` distintos, el grafo del punto 11 no puede anclar a nivel de sección — necesitaría anclar a nivel de sub-item, que el punto 9 no contempla.

Resolución candidata (pendiente, ligada a cerrar el punto 9): **dos niveles**. El punto 9 fija los headers de nivel 1 (`## Contracts`, `## Invariants`, ...); el punto 11 opera sobre **bloques con ID dentro de esos headers**, cada uno con su propio bloque de aristas. El `jump-to-section` del punto 9 sigue funcionando para la categoría; el grafo del punto 11 funciona para el bloque. Requiere que el punto 9, al aprobarse, defina explícitamente que sus secciones son contenedores de bloques-con-ID, no unidades atómicas.

### 11.3. Punto 11 ↔ Punto 13 (notación nativa — índice inverso de `narrows`)

**Severidad: fricción.**

El paso 3 de [11.5](#115-validación-la-ejecuta-pv-internal-doc-technical-no-el-lector) y la nota final del punto 11 introducen un **índice inverso de `narrows`** a nivel de documento (y potencialmente de proyecto) que el lector-modelo necesita para saber, al anclar en la sección general, que existe una sección que la acota. Ese índice es un artefacto nuevo.

El [punto 13](#13-notación-lógico-matemática-o-formato-nativo-para-todo-prosa-solo-excepción--refactorizado) ya arrastra dos notas pendientes que crean artefactos transversales:
- El `00-glossary.md` (notación única por proyecto).
- La regla de notación anidada/híbrida, cuya opción 1 es "referencia por ID en vez de anidar" — es decir, **el mismo mecanismo de citar-por-ID que usan las aristas del punto 11**.

Riesgo de divergencia: si el punto 11 genera su índice inverso de `narrows` por un lado y el punto 13 define su tabla de notación anidada por otro, se acaban con **dos convenciones distintas para "una sección/celda hace referencia a otra por ID"** dentro del mismo proyecto — exactamente el tipo de duplicación que el [punto 4](#4-ids-estables-y-citables-entre-documentos--absorbido-por-el-15) y el [punto 10](#10-un-único-término-por-concepto--absorbido-por-el-15) quieren evitar, un nivel más arriba.

Resolución candidata (pendiente): el índice inverso de `narrows` del punto 11 **no es un artefacto propio** — es una vista derivada que `pv-internal-doc-technical` genera junto al `00-glossary.md` del punto 13, o dentro de él. Una sola pieza de "grafo de referencias entre bloques del proyecto" que sirve a las aristas del punto 11 y a la notación-por-referencia del punto 13. Pendiente de confirmar al detallar el glosario.

#### Ejemplo del conflicto y su resolución

Escenario: doc de arquitectura con un bloque de estructura de datos y un contrato que lo usa en un caso acotado.

```
## <auth-token-model>
   token = { sub: string, iat: int, exp: int, scope: string[] }

## <auth-token-refresh>
requires: [auth-token-model]
narrows:  [config-session-ttl]
   pre:  state ∈ {AUTHENTICATED, EXPIRED} ∧ now - token.exp < 7d
   post: token'.iat = now ∧ token'.exp = now + SESSION_TTL_SECONDS
```

En este contrato, `token` en `pre:`/`post:` es la estructura definida en `<auth-token-model>`. Aquí aparece la fricción entre los dos puntos, porque cada uno tiene su propia forma de resolver "esto se define en otro sitio":

- **Camino del punto 13** (nota de notación anidada, opción 1): el `pre:` referencia una estructura ajena, así que escribe `pre: ... token [ver auth-token-model] ...` — una cita inline con su propia sintaxis `[ver ID]`.
- **Camino del punto 11**: esa misma dependencia ya está declarada arriba como `requires: [auth-token-model]`. El bloque de aristas *es* la lista de "de qué depende este bloque para entenderse".

Sin resolución, el doc acaba con **la misma dependencia expresada dos veces y con dos sintaxis distintas**: una vez en el bloque de aristas (`requires:`) y otra inline en la notación (`[ver auth-token-model]`). Un lector-modelo que confíe en el bloque de aristas para calcular `R` no necesita la cita inline; uno que lea la notación linealmente encuentra una `[ver ...]` que no aparece en ningún glosario si el glosario solo documentó la sintaxis de aristas. Divergencia garantizada en cuanto un doc use una y otro doc la otra.

**Resolución:**

1. **La dependencia de comprensión se declara una sola vez, en el bloque de aristas** (`requires:`). La notación dentro del bloque **no repite la cita**: usa el nombre del tipo a secas (`token`), y se da por entendido que todo identificador no-local está resuelto por el cierre de `requires`.
2. **La cita inline `[ver ID]` del punto 13 se reserva para el caso que el bloque de aristas no cubre**: una referencia puntual dentro de una celda o expresión que apunta a un bloque del que la sección *no* depende globalmente — p. ej. una nota "este valor coincide con el de `<config-session-ttl>` por diseño" que es informativa, no una dependencia de comprensión de todo el bloque.
3. **El `00-glossary.md` documenta ambas y su frontera**: `requires:` / `assumes:` / `narrows:` para dependencias a nivel de bloque; `[ver ID]` inline solo para referencias sub-bloque que no son dependencia. Regla mecánica: si la referencia aplica a todo el bloque → arista; si aplica a un token concreto dentro de una expresión y no es dependencia de comprensión → `[ver ID]`.
4. **El índice inverso de `narrows`** (necesario para que, al anclar en `<config-session-ttl>`, el lector sepa que `<auth-token-refresh>` lo acota) se genera como parte del mismo artefacto de glosario, no aparte.

Resultado sobre el ejemplo: el contrato de `<auth-token-refresh>` queda exactamente como está arriba — `requires:` declara la dependencia de `<auth-token-model>`, el `pre:`/`post:` usa `token` sin cita, y no hay `[ver ...]` inline porque no hay ninguna referencia sub-bloque que no sea ya una arista.
