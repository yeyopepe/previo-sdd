# Informe comparativo de documentación FUNCIONAL — Previo 0.9.6b9 (nivel `full`) vs. baseline

**Fecha:** 2026-08-28
**Objeto:** Comparar la documentación **funcional / de features** que Previo 0.9.6b9 genera en nivel `full` (solo mirando el código de la app) frente a la documentación de referencia (`_baseline`), creada y mantenida a mano a lo largo de la evolución del proyecto.

**Fuentes:**
- Referencia: `test-data/bgfactory-docs/_baseline/features/` (36 ficheros + INDEX)
- Bajo prueba: `test-data/bgfactory-docs/0.9.6b9/full/features/` (46 ficheros + INDEX)

> Cuarto informe de la serie. Hermanos: `documentation-test-0.9.6b9-technical-minimal.md`, `-functional-minimal.md`, `-technical-full.md`. Mismo método y formato.

---

## 1. Resumen ejecutivo

| Dimensión | Baseline | 0.9.6b9 / **full** | (recordatorio: `minimal`) |
|---|---|---|---|
| Nº de ficheros de feature | 36 (+ INDEX) | **46** (+ INDEX) | 27 |
| Palabras (sin INDEX) — **volumen** | ~23.900 | **~5.720** (~24 % del **volumen**) | ~2.170 (~9 %) |
| Features del baseline tratadas — **cobertura conceptual** | 100 % (referencia) | **~93 %** (~22 bien + ~18 parciales + 3 ausentes, de ~43 — ver §2.1) | ~60 % |
| Palabras medianas por feature | ~390 (rango 89–5.271) | **~120** (rango 79–220) | ~80 (rango 39–106) |
| Granularidad | mixta (atómica + agregada) | **muy atómica** (más features, cada una más acotada) | agregada (fusiona conceptos) |
| Diagramas (mermaid / stateDiagram) | presentes en varias | **0** | 0 |
| `Code:` con IDs de cambio reales | sí | `Code: init` en las 46 | `Code: init` |
| Fechas `Since` / `Last modified` reales | sí (jul–ago 2026) | `2026-08-28` en las 46 | `2026-08-28` |
| Enlaces cruzados entre features | densos | **escasos** (2-3 en todo el corpus) | ninguno |
| Comportamiento por modo | sistemático | **presente y explícito** en cada feature | colapsado |
| `**Available in**` con detalle de ubicación | sí | **sí, bastante preciso** | genérico |

> **Dos métricas distintas, no confundir.** El ratio de palabras (**~24 %**) mide **volumen de prosa**, no cuántas features del baseline están cubiertas. Por **features del baseline efectivamente tratadas**, `full` está en **~93 %** (§2.1: de ~43 features del baseline, ~22 bien cubiertas + ~18 parciales + solo 3 ausentes). La diferencia entre ambos números es **profundidad por entrada**: `full` da un párrafo de ~120 palabras donde el baseline dedica de 200 a 5.271. El volumen que falta **no está repartido de forma uniforme**: se concentra en las dos features más ricas (`carta` 5.271 pal. → 162; `mazo` 1.743 → 186) y en la ausencia de valores concretos (rangos, defaults) en casi todas. Cuando este informe dice "cubre ~24 %", se refiere **siempre a volumen**.

**Veredicto general:** el nivel `full` **duplica el número de features respecto a `minimal` (46 vs. 27) y casi triplica el volumen**, pero cada entrada sigue siendo **un párrafo corto (~120 palabras)**. La diferencia real con `minimal` no es tanto el tamaño por entrada como la **granularidad** (`full` separa lo que `minimal` fusiona: "lanzar el dado" es una feature propia, "voltear cartas" otra, "meter una carta en un mazo" otra) y la **precisión del comportamiento por modo** (cada feature dice explícitamente qué pasa en juego y qué en edición) y de la **ubicación** (`**Available in**` señala panel/menú/pestaña concretos).

Sigue **sin ser especificación funcional**: no hay valores concretos (rangos, mínimos, defaults numéricos), no hay diagramas de flujo/estado, y los metadatos de trazabilidad son de relleno (`Code: init`, fecha única). Los dos componentes más complejos —`carta` y `mazo`— reciben ~160 y ~186 palabras (baseline: 5.271 y 1.743).

Como **catálogo funcional navegable y fiable**, el nivel `full` es **notablemente bueno**: 46 features bien clasificadas en 6 áreas, cada una con su comportamiento por modo y su ubicación, sin errores materiales salvo la confusión heredada del cuadro de texto (§4.2). Para onboarding, revisión de alcance, o contexto de un agente, es suficiente y está bien hecho. Para implementar o testear una feature concreta, hay que ir al código.

---

## 2. Cobertura de features

Mapeo feature-a-feature. `full` renumera y desagrega respecto al baseline.

| Feature (baseline) | Baseline | ¿En `full`? | Fichero(s) `full` | Profundidad relativa |
|---|---|---|---|---|
| Mesa infinita pan/zoom | `001` (222 pal.) | ✅ | `001-mesa-de-juego-infinita` (139) | **Buena.** Fondo de puntos, pan/zoom no afecta a posición real, misma mesa en ambos modos. Falta: rango 0,5–2,5×, "sin animación". |
| Ajustar zoom | (parte de `001`) | ✅ ➕ | `002-ajustar-zoom-para-ver-todos-los-elementos` (78) | `full` le da **feature propia**. Encuadra todo con margen; vista centrada si no hay componentes. Falta: botón solo-icono con aria-label, comportamiento con 1 componente / zoom máximo. |
| Alta/edición/borrado con modal de tabs | `002` (910 pal., **con mermaid**) | ✅ Desagregada | `005-crear-un-componente` (113) + `006-editar-y-eliminar` (129) | **Mejor que `minimal`.** `005`: elige tipo de lista, nace con defaults, aparece desplazado, si se cancela se descarta. `006`: pestañas (generales / específicas / ayuda al jugador), eliminar desde la ventana, confirmación simple vs. enumerada, cascada de copias. **Falta**: la pestaña "Visuales" (el baseline `002` la documenta en detalle tras el cambio 00210), la validación de `id` único/no vacío, los iconos de ayuda "?", el diagrama de estados de navegación entre pestañas. |
| Panel flotante de componentes | `003` (1.271 pal.) | ✅ **Buena** | `004-panel-de-componentes` (168) | Captura: tabla (id / orden / acciones editar-clonar-copiar-eliminar), arrastrable / colapsable / redimensionable, persistencia de posición/tamaño/colapso/ancho de columna, filtro de texto + limpiar, ordenar/filtrar por cabecera con indicador, miembros de grupo anidados, botón "+" al pie. **Buena densidad.** Falta: "traer al frente al interactuar", límites de resize (290–600px), doble manejador de esquina. |
| Ordenación/filtrado desde cabecera de columna | `004` (556 pal.) | ⚠️ Fusionada | dentro de `004` ("las cabeceras permiten ordenar y filtrar; el activo se indica") | **Reducida a 2 frases.** Falta: toggle A-Z/Z-A, `<select>` de valores distintos, AND con filtro de texto, "Orden" solo ordena. |
| Elementos "Copia" vinculados | `005` (785 pal.) | ✅ **Muy buena** | `011-elementos-copia-vinculados` (220 — la feature más larga de `full`) | Captura: qué se sincroniza (lista), qué no (`resultadoActual`/`caraActual`), posición/orden nunca, bloqueo/ocultación siguen al original mientras `sincronizado` y cambiarlos directamente rompe la sincronización, cascada de borrado, insignia roja (copia) vs. insignia con número (tiene copias), id `-COPY-NNN`. **Cobertura cercana al baseline.** Falta: la modal reducida, el menú contextual condicionado en modo juego. |
| Panel flotante de recursos con filtro | `006` (399 pal.) | ✅ ➕ | `028-panel-de-recursos` (92) | **Feature propia.** Tabla (nombre / nº de usos / acciones), mismo comportamiento de panel, filtro por nombre. |
| Edición de recurso Imagen con zoom/pan | `007` (241 pal.) | ✅ ➕ | `032-vista-previa-ampliada-de-recursos` (87) | **Feature propia.** Vista previa grande con zoom/pan, zoom numérico; tipografía → muestra de texto. Equivalente al baseline. |
| Etiquetas | `008` (1.443 pal.) | ✅ **Buena** | `013-etiquetas` (171) | Captura: organización por nombre, multi-etiqueta, panel con nº de elementos + editar/eliminar/crear, clic en etiqueta selecciona todos (incl. grupos y cartas en mazo que se sacan), asignación desde menú contextual o ventana de edición (que lista y permite quitar), borrado en uso enumera afectados. **Buen resumen.** Falta: alta al vuelo desde la modal de componente, orden alfabético, panel flotante como tal (arrastre/colapso). |
| Subida múltiple y por carpeta | `009` (449 pal.) | ✅ **Buena** | `029-subida-de-recursos` (122) | **Feature propia.** Un fichero / varios / carpeta; **formatos exactos** (PNG JPG GIF SVG WebP / TTF OTF WOFF WOFF2); solo primer nivel de carpeta, informa de omitidos en subcarpetas; resumen final (añadidos / reemplazados / omitidos). Muy buena. |
| Conversión automática a WebP | `010` (244 pal.) | ✅ ➕ | `030-conversion-automatica-a-webp` (79) | **Feature propia.** PNG/JPG → WebP sin pérdida perceptible; GIF/SVG/WebP tal cual. Falta: q=0.92, fallo silencioso. |
| Búsqueda de imagen en "Elegir imagen" | `011` (175 pal.) | ❌ **Ausente** | — | Sin feature propia. Se menciona "galería de imágenes con buscador" de pasada en `022-mazo` / `025`. |
| Orden de apilado en la mesa | `012` (265 pal.) | ✅ **Buena** | `009-orden-de-apilado-de-componentes` (132) | **Feature propia.** Nº de orden editable en la columna, resto se recoloca; grupos como bloque contiguo; subida automática al primer plano en juego. Falta: clamp `[1,n]`, `[1, n-k+1]` del bloque. |
| Subir al mover/interactuar | `013` (234 pal.) | ✅ Fusionada | `009` (último párrafo) + `041` | "configurado para subir al moverlo o interactuar pasa al primer plano". OK. |
| Interacciones programadas | `014` (537 pal.) | ✅ **Buena** | `019-interacciones-programadas-por-componente` (128) | **Feature propia.** Acción por tipo de click (izq / doble / arrastrar / derecho), pestaña de interacciones muestra qué hace cada una, los 3 tipos con click izq propio (lanzar / voltear / sacar) permiten desactivarlo, click derecho configurable (nada / menú). Buena. |
| Posición independiente, arrastre y redimensionado | `015` (1.201 pal.) | ⚠️ Disperso | `007-seleccion-multiple` + `017-bloqueo-de-movimiento` | El bloqueo de 3 niveles está en `017` con detalle. **Falta** el grueso: redimensionado libre vs. proporción fija por tipo, Shift = 1:1, qué tipos fuerzan cuadrado. |
| Componente oculto en modo juego | `016` (228 pal.) | ✅ ➕ | `018-ocultar-componentes-al-publico` (93) | **Feature propia.** No se muestra en juego, visible/editable en edición con indicador permanente, aplicable a selección múltiple o grupo desde menú contextual. Buena. |
| Componente "cuadro de texto" | `017` (89 pal.) | ⚠️ **Divergente** | `026-cuadro-de-texto` (89) | **Discrepancia (ver §4.2):** `full` dice "formato enriquecido escrito en Markdown o HTML". El baseline `017` describe texto plano (contenido / tamaño de fuente / color / color de fondo). Markdown/HTML es del **Visor de documentos**. **Misma confusión que `minimal`.** `full` añade correctamente "sin caja ni fondo, sombra sutil para legibilidad" y "se siembra uno de ejemplo en sesión nueva". |
| Componente "tablero simple" | `018` (391 pal.) | ✅ Parcial | `024-tablero-simple` (95) | Cuadrícula cuadrada/hexagonal (orientación V/H), color/grosor/filas/columnas, borde biselado/plano, sombra opcional. Falta: rangos (1–50, 1–20), migración `'tablero'`→`'tableroSimple'`, "sin recortar celdas". |
| Componente "tablero personalizado" | `019` (494 pal.) | ✅ Parcial | `025-tablero-personalizado` (91) | Mismo editor visual que cartas, una cara, imagen (posición/zoom/rotación) + formas + textos, píxel real, borde biselado + sombra como el simple. Correcto y algo más completo que `minimal`. |
| Componente "dado" | `020` (518 pal.) | ✅ Parcial | `023-dado` (122) + `041` | `023`: nº de caras (1..N) o lista de valores separados por comas (num/texto), color del cuerpo / del resultado / tipografía, resultado no sincronizado. `041`: click izq lanza con animación, doble click abre grande, sube al primer plano si configurado, desactivable. **Falta**: rango 2–100, mínimo 2 valores, siluetas por nº de resultados, temblor, clicks ignorados durante tirada. |
| Componente "Visor de documentos" | `021` (384 pal.) | ✅ **Buena** | `027-visor-de-documentos` (118) | Captura: texto/Markdown pegado o web externa embebida, Markdown → formato (encabezados, listas, **listas de tareas con casillas**, énfasis, enlaces), HTML limpiado de scripts + handlers, hoja blanca / borde fino / scroll propio. Buena. Falta: `<iframe sandbox>` (de hecho el técnico dice que **no** tiene sandbox), heurística de aviso a los 3s. |
| Componente "carta" | `022` (**5.271 pal.**) | ⚠️ Muy reducida | `021-carta` (162) + `042` (voltear) | `021`: rectángulo esquinas redondeadas, proporción (predefinidas + libre), dos caras independientes en editor visual (imagen con posición/zoom + formas + textos con fuente/color/bordes/alineación/rotación), píxel real, meter en mazo arrastrando o menú. `042`: click izq voltea con animación + efecto de elevación, voltear todas desde menú en edición, desactivable. **Buen titular desagregado.** Deja fuera el 95 %: las 11 proporciones nombradas, shapes `Forma`/`TextBox`, orden de apilado dentro de la cara, copiar/pegar elemento, `esquinasRedondeadas`, recorte hex/triángulo con borde interior, redimensionado por proporción. |
| Componente "mazo" | `023` (1.743 pal.) | ⚠️ Reducida | `022-mazo` (186) + `043` + `044` | `022`: pila barajable, orientación/forma/imagen de dorso/zona de revelado (lado/texto/cara), click izq saca la de arriba, menú (barajar / ver contenido), meter arrastrando o desde menú (arriba/abajo), cartas dentro no se dibujan sueltas, tooltip con nº de cartas. `043`/`044` desagregan las interacciones. **Buen resumen desagregado.** Falta: fallback al dorso de la carta de arriba, icono de vacío, transposición al cambiar orientación, forma circular recorta todo, `confirm()` en arrastre múltiple de edición. |
| Migración de fichas antiguas | `024` (326 pal.) | ✅ Fusionada | `039-migracion-automatica-de-formatos-antiguos` (121) | **Mejor que `minimal`.** `039` enumera qué se migra: tipos renombrados/retirados, campos de agrupación/etiqueta, bloqueo sí/no → 3 valores, cartas a píxel real; tolerante a fallos, nunca bloquea el arranque. **Falta** el mapeo específico `ficha`→`carta` (`forma`→`proporcion`) y la etiqueta "Carta/Ficha". |
| Identificación de componentes al pasar el ratón | `025` (294 pal.) | ✅ Desagregada | `015-titulo-de-componente-y-variables-de-texto` (131) + `016-tooltip-de-componente` (112) | **Mejor que `minimal`.** `015`: título propio en esquina, permanente en juego, texto/color/fondo/transparencia, variables `{...}` en tiempo real, `{cards_current}` para mazo, literal si no aplica. `016`: tooltip propio al pasar el ratón, sustituye al nativo, **mazos nacen con tooltip por defecto** ("cómo sacar la primera carta"), mismas variables. Falta: la etiqueta "Tipo: id" de modo edición (que sí está en el técnico), formato básico saneado. |
| Menú contextual en modo juego | `026` (503 pal.) | ✅ **Buena** | `045-menu-contextual-configurable-por-componente` (133) | **Feature propia.** Abre junto al cursor si configurado; "no hacer nada" no selecciona ni abre; muestra identificador + dato resumen (caras / dimensiones / cartas), bloquear/desbloquear (salvo copia sincronizada), acciones del tipo (barajar / ver contenido / meter en mazo), resumen de qué hace cada click. Buena, cercana al baseline. |
| Menú contextual en modo edición | `027` (553 pal.) | ⚠️ Disperso | mencionado en `007`, `008`, `012`, `013`, `018`, `042` | **No hay feature propia.** Las acciones (agrupar, ocultar, voltear, añadir a etiqueta, eliminar) aparecen repartidas por las features que las usan. Falta la vista de conjunto: que actúa sobre la selección completa, el `<select>` inline, deshabilitado sin etiquetas. |
| Atajos de teclado en modo edición | `028` (493 pal.) | ✅ **Buena** | `046-atajos-de-teclado-globales` (118) | **Feature propia.** Con ventana: Escape cancela, Intro acepta (salvo en textarea / deshabilitado), Suprimir borra la ventana. Sin ventana en edición: Suprimir borra selección, flechas 1px / 10px con Mayús; flechas inertes con ventana abierta. Cercana al baseline. Falta: `bloqueado:'todos'` no se mueve salvo en grupo, no disponible en juego. |
| Autoguardado en el navegador | `029` (330 pal.) | ✅ **Muy buena** | `036-autoguardado-local` (125) | Captura: guarda todo (componentes/recursos/etiquetas/grupos/título/paneles) tras cada cambio sin acción del usuario, recupera exacto al reabrir, una partida por navegador+perfil, fallo de cuota omitido sin interrumpir, estado corrupto → aviso + recursos de ejemplo. **Cobertura completa.** |
| Título de cabecera editable | `030` (206 pal.) | ✅ ➕ | `040-titulo-de-la-aplicacion-editable` (87) | **Feature propia.** Editable con clic en modo edición, versión siempre visible y no editable, default "BG Factory", forma parte del estado guardado/exportado. Equivalente al baseline. |
| Guardar a fichero | `031` (111 pal.) | ❌ **Ausente** | — | `full` **no tiene** el "Guardar" (descarga del HTML autocontenido con el estado embebido). Tiene `037-exportar-juego` (JSON) y `036-autoguardado`, pero no el guardado del `.html`. **Regresión respecto a `minimal`**, que sí tenía `023-guardar`. El técnico (`arch/005`) sí menciona el build del `.html` autocontenido, pero como feature de usuario no está. |
| Exportar/importar JSON con selección | `032` (862 pal.) | ✅ **Buena** — desagregada | `037-exportar-juego` (140) + `038-importar-juego` (172) | **Mejor que `minimal`.** `037`: JSON compartible, incluye componentes/recursos/etiquetas/grupos/título, no paneles; casillas de selección + nombre; grupos referenciados incluidos automáticamente; anuncia ZIP/CSV como "Próximamente". `038`: carga JSON (aunque sea de otra versión — caso de uso principal), selección por casillas, fusionar (añadir / sobrescribir todo), id duplicado (sobrescribir / mantener ambos), sobrescribir aplica título, conversión al vuelo con errores (continuar sin / abortar), ventana de operación en curso, informe si hubo avisos. **Muy buena cobertura.** Falta: `nextImportedId` (renombrado del que se conserva), la reparación fila a fila de refs rotas. |
| Modal de error común a toda la app | `033` (125 pal.) | ❌ **Ausente** | — | Sin feature propia. Es un patrón funcional transversal ("todo error se comunica igual"). Aparece solo como detalle en `036` ("se avisa"), `034`, `038`. |
| Agrupación: agrupar y desagrupar | `034` (1.507 pal.) | ✅ **Buena** | `012-agrupacion-de-componentes` (157) | Captura: agrupar selección sin grupos previos, propiedades propias del grupo (bloqueo/ocultación/tooltip/título/subir/etiquetas) que gobiernan a los miembros, selección/movimiento/edición como uno, miembros anidados en el panel, ventana de propiedades del grupo (editar comunes + renombrar), desagrupar devuelve propiedades, disolución automática ≤1 miembro. **Buen resumen.** Falta: no se redimensiona, tabla de habilitación Agrupar/Desagrupar según unidades, "Clonar"/"Copiar" deshabilitados en miembro agrupado, orden editable del bloque. |
| Título de componente | `035` (318 pal.) | ✅ | `015-titulo-de-componente-y-variables-de-texto` (fusionada con variables) | Captura: título propio en esquina, permanente en juego, texto/color/fondo/transparencia, variables. Bien. |
| Contenido de ejemplo al arrancar partida nueva | `036` (202 pal.) | ✅ ➕ | `033-recursos-de-ejemplo-por-defecto` (84) | **Feature propia.** Galería sembrada en primer arranque sin nada guardado; una sola vez (si se borran, no vuelven). **Falta**: "2 recursos, uno por tipo", el cuadro de texto de ejemplo (que sí se menciona en `026`), el backfill para guardados antiguos. |
| — | — | ➕ | `003-modo-edicion-y-modo-juego` (192) | `full` **añade** feature marco de los dos modos. Buena. |
| — | — | ➕ | `008-borrado-masivo-con-confirmacion` (96) | Desagrega el borrado múltiple de `002`/`003` baseline. Solapa con `006`. |
| — | — | ➕ | `010-clonar-un-componente` (96) | Desagrega "Clonar" (el baseline lo trata dentro de `005`/`003`). Correcto: copia independiente, id `(n)`, familia de id. |
| — | — | ➕ | `014-efecto-de-profundidad-y-extrusion-3d` (103) | **Feature propia** para `profundidad`/`colorExtrusion` — el baseline lo trata dentro de `002` (pestaña Visuales) y del Style Bible. Buen añadido: grosor + color, cálculo automático desde el color base. |
| — | — | ➕ | `020-portapapeles-de-estilos-entre-cartas` (103) | Desagrega el copiar/pegar estilo (baseline: dentro de `022-carta`). Captura: dos caras completas, solo en sesión, un estilo a la vez, nunca persistido/exportado. Mejor que `minimal` (que tenía 2 frases). |
| — | — | ➕ | `035-tipografias-personalizadas` (88) | Feature propia: subir fuentes, asignarlas a dado / textos de carta, registro automático al cargar. |
| — | — | ➕ | `041`, `042`, `043`, `044` | `full` **desagrega las interacciones de modo juego** en 4 features (lanzar dado / voltear / sacar-barajar-ver / meter en mazo). El baseline las tiene dentro de `020`/`022`/`023`. Para una doc funcional, esta desagregación **mejora** la localización. |
| — | — | ➕ | `031-deteccion-de-nombres-duplicados` (130) | Feature propia: reemplazar/cancelar, lote agrupa colisiones en una ventana, repetido dentro del lote cuenta desde el segundo. Mejor que el baseline (que lo tiene dentro de `009`). |
| — | — | ➕ | `034-aviso-al-borrar-un-recurso-en-uso` (101) | Feature propia: bloqueo + lista de componentes, comprobación recorre `properties` a cualquier nivel. Mejor localizada que en el baseline (dentro de `006`/`034` disperso). |

### 2.1 Recuento

- **Cubiertas bien (resumen fiel + comportamiento por modo + ubicación):** ~22 (`004`, `009`, `011`, `013`, `019`, `023`+`041`, `027`, `029`, `036`, `037`+`038`, `045`, `046`, `012`, `031`, `034`…).
- **Cubiertas parcialmente (titular correcto, sin detalle accionable):** ~18.
- **Ausentes:** `011` baseline (búsqueda de imagen), `031` baseline (**Guardar a fichero** — regresión vs. `minimal`), `033` baseline (modal de error común).
- **Dispersas sin feature propia:** menú contextual de modo edición (`027` baseline), posición/redimensionado por tipo (`015` baseline).
- **Divergencia a verificar:** `026-cuadro-de-texto` (¿Markdown/HTML o texto plano? — misma confusión que `minimal`).

### 2.2 `full` vs. `minimal` (funcional)

| Eje | `minimal` (27 features, ~2.170 pal., ~60 % features baseline) | `full` (46 features, ~5.720 pal., ~93 % features baseline) |
|---|---|---|
| Granularidad | fusiona conceptos ("orden + profundidad + subida" en 1) | **desagrega** ("lanzar dado", "voltear", "meter en mazo" separadas) |
| Comportamiento por modo | colapsado a `Available in: edición y juego` | **explícito en cada feature** ("en modo juego X; en edición Y") |
| Ubicación (`Available in`) | genérica ("Modo edición") | **precisa** ("panel de recursos, menú de añadir"; "pestaña de ayuda al jugador") |
| Interacciones de juego | 1 feature (`010-menus-contextuales`) mezcla todo | **5 features** (`041`–`045`) + `046` atajos |
| Formatos/listas concretas | "PNG/JPG" | **lista completa** PNG JPG GIF SVG WebP / TTF OTF WOFF WOFF2 |
| Copiar/pegar estilo | 2 frases | **feature de 103 palabras** con "solo en sesión, nunca exportado" |
| Migración de fichas | media frase | **feature de 121 palabras** enumerando qué se migra |
| Regresiones | — | **pierde "Guardar a fichero"** que `minimal` sí tenía |

---

## 3. Análisis cualitativo

### 3.1 Lo que el nivel `full` hace bien

1. **Desagregación orientada a la localización.** Separar "lanzar el dado" (`041`) de la definición del dado (`023`), o "voltear cartas" (`042`) de la carta (`021`), hace que quien busca "¿cómo funciona robar del mazo?" encuentre `043` directamente en el área "Interacción en modo juego". El baseline mete todo eso dentro del doc del tipo.
2. **Comportamiento por modo explícito y sistemático.** Cada feature relevante dice qué pasa en juego y qué en edición. `full` no colapsa esto (`minimal` sí).
3. **`**Available in**` preciso.** No "Modo edición" a secas, sino "menú de añadir del panel de recursos", "pestaña de ayuda al jugador", "sección de estilo de la carta en su ventana de propiedades". Ayuda a encontrar la feature en la app.
4. **Listas concretas donde el código las tiene explícitas.** Formatos de fichero completos (`029`, `035`), qué se sincroniza en una copia (`011`), qué elementos Markdown se renderizan (`027`: "listas de tareas con casillas").
5. **Features transversales rescatadas como propias.** `014` (extrusión 3D), `031` (nombres duplicados), `034` (recurso en uso), `020` (portapapeles de estilo) — el baseline las tiene enterradas en otras; `full` les da entrada localizable.
6. **Clasificación en 6 áreas** coherente (Gestión de componentes / Tipos de componente / Interacción en modo juego / Mesa y navegación / Recursos e imágenes / Persistencia e intercambio). Más navegable que la lista plana del baseline.
7. **Marco de los dos modos** (`003`) que el baseline da por sabido.
8. **Precisión sin errores** (salvo `026`): lo que afirma es fiable y conservador.

### 3.2 Carencias críticas

Ordenadas por impacto:

1. **Sigue sin haber valores concretos: ni rangos, ni mínimos, ni defaults numéricos.**
   `023-dado` dice "un número de caras que genera 1..N" — no "2 a 100". `024-tablero-simple` dice "número de filas y columnas" — no "1–50". `007` dice "un píxel (diez con Mayús)" — eso sí. Pero en general **no se puede implementar ni testear** una feature: no se sabe qué es válido. El baseline sí lo especifica.

2. **Cero diagramas.**
   El baseline usa `stateDiagram-v2` para la navegación de pestañas de la modal (`002`), y flujos para importación. Features con estados o secuencias (importación en `038`, modal de tabs en `006`, voltear en `042`) se benefician de un diagrama; `full` no tiene ninguno.

3. **`carta` y `mazo` siguen en un párrafo cada uno.**
   `021` (162 pal.) y `022` (186 pal.) para los dos componentes más ricos del producto (baseline: 5.271 y 1.743). La desagregación de interacciones (`041`–`044`) ayuda, pero la definición del tipo —proporciones, shapes de elemento, recortes, reglas de redimensionado— queda en el titular.

4. **Regresión: se pierde "Guardar a fichero".**
   `minimal` tenía `023-guardar` (descarga del `.html` autocontenido con el estado embebido — la forma canónica de compartir un juego jugable). `full` tiene exportación a JSON (`037`) y autoguardado (`036`), pero **no** el guardado del HTML. Es una feature de usuario real y visible (botón "Guardar" en la barra de edición).

5. **Metadatos de trazabilidad de relleno.**
   `Code: init` y `2026-08-28` en las 46. Se pierde qué cambio introdujo cada feature y cuándo se tocó por última vez (el baseline tiene IDs `00xxx` reales y fechas distintas jul–ago 2026).

6. **Enlaces cruzados casi inexistentes.**
   El baseline teje las 36 features entre sí. `full` tiene 2-3 enlaces en 46 ficheros, pese a haber desagregado features que se referencian obviamente (`041` dado ↔ `023` dado; `042` voltear ↔ `021` carta ↔ `044` meter en mazo). El lector no puede navegar el grafo.

7. **Menú contextual de modo edición sin feature propia.**
   El baseline le dedica `027` (553 pal.). En `full` sus acciones están repartidas por 6 features. Falta la vista de conjunto (actúa sobre la selección, `<select>` inline, deshabilitado sin etiquetas).

8. **Features transversales de UX perdidas.**
   `033-modal-de-error-comun` ("todo error se comunica con el mismo elemento") es una decisión de producto; `full` la disuelve en cláusulas.

---

## 4. Diagnóstico transversal

### 4.1 Qué tipo de conocimiento se pierde

Mismo patrón que en los tres informes previos:

- **`full` captura bien el "qué" y el "dónde y cuándo":** qué features existen, en qué área, qué hacen a grandes rasgos, **en qué modo**, **en qué panel/menú**. Como catálogo funcional navegable, es fiable y está mejor calibrado que `minimal` (más granular, con comportamiento por modo).
- **`full` no captura el "cómo se comporta exactamente":** rangos válidos, defaults numéricos, casos límite, secuencias paso a paso, estados. Sigue viviendo repartido por el código y no se condensa al resumir.
- **Y sigue sin capturar lo histórico:** qué cambio introdujo la feature, cuándo, qué la modificó, cómo se relaciona con otras.

`full` mejora sobre `minimal` en granularidad y en precisión de modo/ubicación, pero **no cambia la naturaleza del artefacto**: sigue siendo un catálogo de resúmenes, no una especificación. La brecha con el baseline es del mismo tipo que en `minimal`, solo algo más estrecha. Y conviene medirla con el eje correcto: **en volumen de prosa** es ~24 % (vs. ~9 % de `minimal`); **en features cubiertas** es ~93 % (vs. ~60 %). Lo que falta no son features enteras —solo 3— sino la profundidad dentro de cada una: valores, casos límite, secuencias.

### 4.2 Precisión — discrepancia a verificar (persiste desde `minimal`)

**`026-cuadro-de-texto`.**

| | Contenido |
|---|---|
| **`full`** (`026`) | "Admite formato enriquecido escrito en **Markdown o en HTML**." |
| **`minimal`** (`017-texto`) | Idéntico: "Markdown o en HTML". |
| **Baseline** (`017-componente-cuadro-de-texto`, 89 pal.) | Texto simple: `contenido`, `tamañoFuente`, `colorTexto`, `colorFondo`. Sin Markdown/HTML. |
| **Baseline** (`021-componente-visor-de-documentos`) | *Este* interpreta Markdown/HTML. |
| **Técnico `full`** (`arch/003`) | `documento: { ..., formato ∈ {'markdown','html'}, ... }` — el `documento`, no el `texto`. `texto` no aparece con `properties` de formato. |

**Tanto `minimal` como `full` atribuyen al "cuadro de texto" (`'texto'`) una capacidad que es del "visor de documentos" (`'documento'`).** Ambos tienen `027`/`018-documento` correcto. Es una confusión persistente entre los dos tipos en la feature del cuadro de texto. **Verificar en `src/ui/componentModal.js` / la definición de `'texto'` en 0.9.6b9** — si `'texto'` solo lleva contenido/tamaño/color, la feature del cuadro de texto está mal en las dos generaciones.

(No se han encontrado otras afirmaciones incorrectas en `full`. El resto es conservador y fiable.)

### 4.3 Organización

`full` **organiza mejor el catálogo funcional** que `minimal` y que el baseline:
- 6 áreas temáticas coherentes vs. lista plana de 36 (baseline) o 7 áreas de `minimal`.
- Desagregación por localización (interacciones de juego separadas del tipo).
- `**Available in**` preciso.
- Metadatos uniformes.

Si se le pidiera **más profundidad por entrada** (valores, casos límite, un diagrama donde haga falta) manteniendo esta taxonomía y granularidad, `full` sería una buena documentación funcional de referencia.

---

## 5. Conclusiones y recomendaciones

### 5.1 Sobre el nivel `full` como tal

**Es un buen catálogo funcional navegable.** 46 features en 6 áreas, cada una con su comportamiento por modo y su ubicación en la app, sin errores materiales salvo `026`. Para onboarding, revisión de alcance de producto, o contexto de un agente, es suficiente y está mejor hecho que `minimal` (más granular, más preciso en modo/ubicación).

**No es especificación funcional** — pero la brecha es de **profundidad**, no de features ausentes. En **volumen de prosa** es ~24 % del baseline; en **features cubiertas**, ~93 % (solo 3 ausentes: búsqueda de imagen, Guardar a fichero, modal de error común). Lo que falta dentro de cada entrada: valores concretos, diagramas, y la trazabilidad a cambios. `carta` y `mazo` siguen en un párrafo. Un desarrollador no puede implementar ni un QA testear a partir de estas entradas sin ir al código.

**Regresión puntual:** pierde "Guardar a fichero" (`.html` autocontenido), que `minimal` sí documentaba.

### 5.2 Prioridades si se quiere subir de nivel

Por orden de retorno:

1. **Recuperar "Guardar a fichero"** como feature propia (regresión clara respecto a `minimal`).
2. **Añadir valores concretos** a cada feature: rangos, mínimos, defaults numéricos (2–100 caras, 1–50 filas, 290–600px de panel, q=0.92…). Barato de regenerar (están en las validaciones).
3. **Expandir `carta` y `mazo`** a documentos de varias secciones (proporciones, shapes de elemento, recortes, redimensionado).
4. **Recuperar `011` (búsqueda de imagen)** y **`033` (modal de error común)** como entradas propias, y **dar feature propia al menú contextual de modo edición**.
5. **Casos límite explícitos** por feature: 0 componentes, lista de valores vacía, referencia rota al importar, cuota excedida (algunos ya están; sistematizarlo).
6. **Diagramas de estado/flujo**: navegación de pestañas de la modal, flujo de importación, voltear carta, sacar carta de mazo.
7. **Enlaces cruzados** entre las features desagregadas (`041`↔`023`, `042`↔`021`↔`044`, `013`↔`012`).
8. **Trazabilidad**: si el generador puede leer git, poblar `Code:` y fechas reales en vez de `init` / `2026-08-28`.

### 5.3 Verificación pendiente

- **`026-cuadro-de-texto`**: confirmar en el código de 0.9.6b9 si el "cuadro de texto" (`'texto'`) interpreta Markdown/HTML o es texto plano con contenido/tamaño/color. Confusión persistente en `minimal` y `full`; el propio técnico apunta a que Markdown/HTML es solo del `'documento'`.
- Confirmar que "Guardar a fichero" (botón "Guardar" de la barra de edición, descarga del `.html` con estado embebido) sigue existiendo en 0.9.6b9 — si sí, es una omisión de `full`.
- Confirmar que no falta ninguna otra capacidad viva más allá de las señaladas (`011`, `033`, guardar).
