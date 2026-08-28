# Informe comparativo de documentación FUNCIONAL — Previo 0.9.6b9 (nivel `minimal`) vs. baseline

**Fecha:** 2026-08-28
**Objeto:** Comparar la documentación **funcional / de features** que Previo 0.9.6b9 genera en nivel `minimal` (solo mirando el código de la app) frente a la documentación de referencia (`_baseline`), creada y mantenida a mano a lo largo de la evolución del proyecto.

**Fuentes:**
- Referencia: `test-data/bgfactory-docs/_baseline/features/` (36 ficheros + INDEX)
- Bajo prueba: `test-data/bgfactory-docs/0.9.6b9/minimal/features/` (27 ficheros + INDEX)

> Informe hermano del análisis de arquitectura y estilo (`documentation-test-0.9.6b9-minimal.md`). Mismo método, mismo formato.

---

## 1. Resumen ejecutivo

| Dimensión | Baseline | 0.9.6b9 / minimal | Ratio |
|---|---|---|---|
| Nº de ficheros de feature | 36 (+ INDEX) | 27 (+ INDEX) | 75 % |
| Palabras (sin INDEX) | ~23.900 | ~2.170 | **~9 %** |
| Palabras medianas por feature | ~390 (rango 89–5.271) | ~80 (rango 39–106) | — |
| Diagramas (mermaid / stateDiagram / flowchart) | Presentes en varias features | **0** | — |
| Trazabilidad a cambios (`Code:` con IDs `00xxx`) | Sí, lista real por feature | `Code: init` en las 27 | — |
| Fechas `Since` / `Last modified` reales | Sí (jul–ago 2026, distintas) | `2026-08-28` en las 27 | — |
| Enlaces cruzados entre features | Densos (`[feature](fichero.md)`) | Ninguno | — |

**Veredicto general:** el nivel `minimal` produce un **catálogo de features correcto, bien clasificado y sin errores detectados**, pero cada entrada es **un único párrafo de resumen** (~80 palabras). Funciona como **índice de "qué sabe hacer la app"** — útil para un product manager, un onboarding rápido o un LLM que necesite orientarse — pero **no como especificación**. El baseline, en cambio, es una especificación funcional completa: casos límite, valores concretos (rangos, defaults), comportamiento por modo, migraciones, historia de cambios y diagramas de estado.

Para el propósito declarado del nivel `minimal` (visión general compacta), el resultado es **adecuado y limpio**. Como documentación funcional única del proyecto, sería **claramente insuficiente**: falta el ~90 % del contenido, y lo que falta es justo el detalle accionable (qué pasa en el borde, con qué valor exacto, en qué modo).

---

## 2. Cobertura de features

Mapeo feature-a-feature. La numeración difiere entre ambas colecciones (el `minimal` reorganiza y fusiona).

| Feature (baseline) | Baseline | ¿En minimal? | Fichero minimal | Profundidad relativa |
|---|---|---|---|---|
| Mesa infinita pan/zoom | `001` (222 pal.) | ✅ | `001-mesa-infinita` (95) | **Buena.** Captura rango 0,5–2,5×, "Ajustar zoom", cámara persiste entre modos pero no entre recargas. Falta: botón solo-icono con aria-label, comportamiento con 0 / 1 componente, "sin animación". |
| Alta/edición/borrado con modal de tabs | `002` (910 pal., **con mermaid**) | ⚠️ Parcial | `003-panel-componentes` + `002-modos` | **Superficial.** El minimal menciona "editar desde su fila" pero **no documenta la modal de 3 pestañas** (Generales / Visuales / Específicas), ni la validación de `id`, ni la modal previa de tipo, ni el diagrama de estados. |
| Panel flotante de componentes (selección, arrastre, resize) | `003` (1.271 pal.) | ✅ Parcial | `003-panel-componentes` (81) | **Correcta como resumen.** Falta: "traer al frente al interactuar", límites de resize (290px…), doble manejador de esquina, persistencia exacta. |
| Ordenación/filtrado desde cabecera de columna | `004` (556 pal.) | ⚠️ Fusionada | dentro de `003` ("ordenar, filtrar y buscar por texto en cualquier columna") | **Reducida a media frase.** Falta: toggle A-Z/Z-A, `<select>` de valores distintos, AND con filtro de texto, que "Orden" solo ordena y no filtra. |
| Elementos "Copia" vinculados | `005` (785 pal.) | ✅ **Buena** | `006-copias` (93) | Captura bien: qué se sincroniza, qué no (`resultadoActual`/`caraActual`), bloqueo/visibilidad desincronizables, borrado en cascada. Falta: id `-COPY-XXX`, modal reducida, indicador visual, menú contextual condicionado. |
| Panel flotante de recursos con filtro | `006` (399 pal.) | ✅ Parcial | `020-recursos` (99) | Cubierto dentro del combo de recursos. |
| Edición de recurso Imagen con zoom/pan | `007` (241 pal.) | ✅ | `021-recursos-preview` (68) | Correcta como resumen. |
| Etiquetas (organización por nombre) | `008` (1.443 pal.) | ✅ Parcial | `007-etiquetas` (98) | **Buen resumen.** Captura: multi-etiqueta, grupo etiquetable, seleccionar-todos-de-una-etiqueta, cartas dentro de mazo se sacan, confirmación al borrar en uso. Falta: panel flotante, alta al vuelo desde la modal, orden alfabético, columna "Elementos", cadena de compatibilidad `decks→groups→tags`. |
| Subida múltiple y por carpeta | `009` (449 pal.) | ✅ | `020-recursos` (fusionada) | Captura "un fichero / varios / carpeta", subcarpetas omitidas con aviso, resumen final. Bien. |
| Conversión automática a WebP | `010` (244 pal.) | ✅ | `020-recursos` (fusionada) | "PNG/JPG se convierten a WebP para mantener el fichero ligero". Falta: q=0.92, WebP/SVG/GIF sin reconvertir, fallo silencioso. |
| Búsqueda de imagen en "Elegir imagen" | `011` (175 pal.) | ❌ **Ausente** | — | No hay entrada. Se menciona "galería de imágenes … con buscador" de pasada en `013-mazo`. |
| Orden de apilado en la mesa | `012` (265 pal.) | ✅ | `008-orden-apilado` (84) | Fusionada con profundidad 3D. Captura "individual o en bloque para grupos". |
| Subir al mover/interactuar | `013` (234 pal.) | ✅ | `008-orden-apilado` (fusionada) | "una pieza puede subir automáticamente al frente al moverla o interactuar". OK. |
| Interacciones programadas | `014` (537 pal.) | ✅ Parcial | `019-interacciones` (97) | Captura: acción por tipo de click, desactivar interacciones individuales, click derecho configurable. Falta el detalle de qué interacción tiene cada tipo. |
| Posición independiente, arrastre y redimensionado | `015` (1.201 pal.) | ⚠️ Disperso | `004-seleccion-multiple` + `019-interacciones` | El "Bloqueado" de 3 niveles (nunca / solo juego / siempre) sí está en `019`. Falta el grueso: redimensionado libre vs. proporción fija por tipo, Shift = 1:1, `canMove` por modo. |
| Componente oculto en modo juego | `016` (228 pal.) | ✅ | `019-interacciones` (fusionada) | "una pieza puede ocultarse al publico en modo juego". OK como resumen. |
| Componente "cuadro de texto" | `017` (89 pal.) | ⚠️ Divergente | `017-texto` (39) | **Discrepancia a verificar** (ver §4.2): el minimal dice "formato enriquecido, Markdown o HTML"; el baseline `017` describe un cuadro de texto simple (contenido, tamaño de fuente, color, color de fondo). El "Markdown/HTML" es del **Visor de documentos** (`021`), no del cuadro de texto. Posible confusión de tipos. |
| Componente "tablero simple" | `018` (391 pal.) | ✅ Parcial | `015-tablero-simple` (63) | Captura: cuadrícula cuadrada/hexagonal, orientación, color/imagen de fondo, bisel/plano, sombra opcional, "sin recortar ninguna celda". Falta: rangos (filas/columnas 1–50, grosor 1–20), migración `'tablero'`→`'tableroSimple'`, sub-modales. |
| Componente "tablero personalizado" | `019` (494 pal.) | ✅ Parcial | `016-tablero-personalizado` (56) | "mismo editor visual que las cartas, a tamaño real de píxel". Correcto pero mínimo. |
| Componente "dado" | `020` (518 pal.) | ✅ Parcial | `014-dado` (71) | Captura: nº de caras configurable o lista de valores, tipografía propia, animación de tirada, modal de resultado grande, valor al azar. Falta: rango 2–100, mínimo 2 valores, siluetas según nº de resultados (triángulo/cuadrado/rombo/esfera facetada), temblor, clicks ignorados durante tirada. |
| Componente "Visor de documentos" | `021` (384 pal.) | ✅ **Buena** | `018-documento` (68) | Captura: texto/Markdown pegado o web externa embebida, saneado de HTML (scripts + handlers). Bien para su tamaño. Falta: `<iframe sandbox>`, heurística de aviso a los 3s, `marked`. |
| Componente "carta" | `022` (**5.271 pal.** — la feature más grande) | ⚠️ Muy reducida | `012-carta` (103) | El minimal condensa en 1 párrafo: editor visual, capas (imágenes/formas/textos), 2 caras, volteo animado, 11 proporciones + libre, recorte hex/triángulo con borde interior uniforme. **Es un buen titular**, pero deja fuera el 98 %: shapes `Forma`/`TextBox`, orden de apilado dentro de la cara, copiar/pegar elemento, redimensionado por proporción, `esquinasRedondeadas`, migración de medidas reales, feedback de volteo… |
| Componente "mazo" | `023` (1.743 pal.) | ⚠️ Reducida | `013-mazo` (97) | Captura: pila barajable, zona de revelado configurable (posición/texto/cara), imagen propia de dorso, barajar / ver contenido / sacar carta concreta / meter carta, "mientras está en un mazo no se dibuja como pieza independiente". **Buen resumen.** Falta: fallback al dorso de la carta de arriba, icono de vacío, `{cards_current}` sustituye a la etiqueta fija, arrastre múltiple en edición con `confirm()`, orientación/forma circular. |
| Migración de fichas antiguas → Carta/Ficha | `024` (326 pal.) | ⚠️ Fusionada | `025-importar-informe` ("guardados … se migran automáticamente") | **Reducida a media frase genérica.** No menciona el tipo `'ficha'`, ni el mapeo `forma`→`proporcion`, ni la etiqueta "Carta/Ficha". |
| Identificación de componentes al pasar el ratón | `025` (294 pal.) | ✅ Parcial | `009-titulo-tooltip` (93) | Fusionada con "Título de componente". Captura: etiqueta "Tipo: id" en edición, tooltip opcional en juego, formato básico, variables de texto, `{cards_current}` literal si no aplica. **Buena densidad.** |
| Menú contextual en modo juego | `026` (503 pal.) | ✅ Parcial | `010-menus-contextuales` (101) | Fusionada con edición y atajos. Captura: bloquear/desbloquear, barajar, ver contenido, meter en mazo, interacciones del tipo, click derecho configurable. |
| Menú contextual en modo edición | `027` (553 pal.) | ✅ Parcial | `010-menus-contextuales` (fusionada) | Captura: clonar, copiar, eliminar, agrupar/desagrupar, ocultar/mostrar, voltear, añadir a etiqueta. Falta: actúa sobre la selección completa, `<select>` inline, deshabilitado sin etiquetas. |
| Atajos de teclado en modo edición | `028` (493 pal.) | ✅ Parcial | `010-menus-contextuales` (fusionada) | "Escape cancela, Intro acepta, Supr elimina la selección, flechas mueven". Falta: Intro no dispara con foco en textarea, paso 1px/10px, `bloqueado:'todos'` no se mueve salvo en grupo, no disponible en modo juego. |
| Autoguardado en el navegador | `029` (330 pal.) | ✅ **Buena** | `027-autoguardado` (79) | Captura: guardado tras cada cambio sin acción del usuario, funciona offline, fallo de cuota omitido en silencio. Muy buena para su tamaño. |
| Título de cabecera editable | `030` (206 pal.) | ✅ | `026-titulo-partida` (67) | Fusionada con "Título de partida". Captura: se edita desde cabecera, es nombre de fichero por defecto, versión siempre visible y no editable. |
| Guardar a fichero | `031` (111 pal.) | ✅ **Buena** | `023-guardar` (58) | Captura: HTML autocontenido con la partida embebida, doble clic, sin instalación/cuentas/conexión. Equivalente al baseline. |
| Exportar/importar JSON con selección | `032` (862 pal.) | ✅ Parcial | `024-exportar-importar` (80) | Captura: componentes/recursos/etiquetas selectivos, añadir vs. sobrescribir, id duplicado (sobrescribir / conservar ambos renombrando), nombres de etiqueta duplicados renombrados. **Buen resumen.** Falta: el flujo de modales, `nextImportedId`, reparación de refs. |
| Modal de error común a toda la app | `033` (125 pal.) | ❌ **Ausente** | — | No hay entrada. Es un patrón funcional transversal ("todo error se comunica igual"). El minimal lo trata solo como detalle de `018-documento` / `021`. |
| Agrupación: agrupar y desagrupar | `034` (1.507 pal.) | ✅ Parcial | `005-agrupacion` (93) | Captura: unidad con propiedades propias que gobiernan a los miembros, mover/seleccionar/editar como uno, desagrupar sin pérdida, disolución automática ≤1 miembro. **Buen resumen.** Falta: no se redimensiona, tabla de habilitación Agrupar/Desagrupar, filas sintéticas en el panel, edición individual de miembro. |
| Título de componente | `035` (318 pal.) | ✅ | `009-titulo-tooltip` (fusionada) | Captura: título propio con color de texto/fondo/transparencia, variables de texto, `{cards_current}`. Bien. |
| Contenido de ejemplo al arrancar partida nueva | `036` (202 pal.) | ⚠️ Fusionada | `020-recursos` ("incluye recursos de ejemplo desde el primer arranque") | **Reducida a media frase.** No menciona "2 recursos, uno por tipo", ni el backfill único para guardados antiguos. |
| — | — | ➕ | `002-modos` | El minimal **añade** una feature marco ("modo edición vs. modo juego") que en el baseline está implícita/dispersa. Aportación razonable. |
| — | — | ➕ | `011-portapapeles-estilos` (43) | El minimal le da entrada propia (el baseline lo trata dentro de `022-carta`). Correcto, aunque es la entrada más pobre (2 frases genéricas). |
| — | — | ➕ | `022-tipografias` (46) | Entrada propia para "tipografías como recurso aplicables a texto". El baseline lo reparte entre `006`/`020`. Aportación razonable. |

### 2.1 Recuento

- **Cubiertas bien (resumen fiel y útil):** ~10 (`001`, `005`, `021` doc, `029`, `031`, mesa/copias/guardar/autoguardado/visor…).
- **Cubiertas parcialmente (titular correcto, sin detalle accionable):** ~18.
- **Ausentes o reducidas a media frase:** `011` (búsqueda de imagen), `033` (modal de error común), `024`/`036` (migración de fichas, contenido de ejemplo — degradadas a una cláusula).
- **Divergencia a verificar:** `017` (cuadro de texto — el minimal parece describir el Visor de documentos).

---

## 3. Análisis cualitativo

### 3.1 Lo que el nivel `minimal` hace bien

1. **Clasificación temática limpia.** El INDEX agrupa las 27 features en 7 áreas coherentes (Componentes, Editor, Mesa de juego, Modo edición/juego, Persistencia e intercambio, Recursos). Más navegable que el INDEX plano del baseline (una sola lista de 36).
2. **Fusión sensata de features atómicas.** El baseline tiene features muy granulares que son cambios históricos individuales (`012` orden de apilado, `013` subir al mover, `008` etiquetas…). El minimal las agrupa por concepto de usuario (`008-orden-apilado` = orden + profundidad + subida automática). Para una visión funcional, esto **mejora** la legibilidad.
3. **Resúmenes densos y sin paja.** En ~80 palabras mete lo esencial. Ejemplos buenos: `027-autoguardado` (guarda tras cada cambio / offline / fallo silencioso), `013-mazo` (pila / zona revelado / barajar-ver-sacar-meter / no se dibuja aparte).
4. **Metadatos estructurados por feature** (`**Area**`, `**Available in**`, `**Code**`, `**Since**`, `**Last modified**`) — mismo esqueleto que el baseline, facilita el diff.
5. **Precisión.** Salvo la posible confusión de `017` (§4.2), **no se detectan afirmaciones falsas**. Los rangos que sí cita (zoom 0,5–2,5×) coinciden con el baseline.
6. **Añade el marco "dos modos"** (`002-modos`) que el baseline da por sabido — útil para quien llega de cero.
7. **Lenguaje orientado a usuario**, no a implementación ("sin riesgo de tocar el diseño", "siempre a mano", "sin instalación, cuentas ni conexión").

### 3.2 Carencias críticas

Ordenadas por impacto:

1. **Ningún detalle accionable: no hay valores, rangos ni casos límite.**
   El baseline es una especificación: "número máximo de caras entre **2 y 100**"; "lista de valores: **mínimo 2**, al menos uno no vacío"; "filas/columnas **1–50**"; "resize del panel: mínimo **290px** de ancho". El minimal dice "número de caras configurable". **Con la doc `minimal` no se puede implementar ni testear una feature** — no se sabe qué es válido y qué no.

2. **No hay comportamiento diferenciado por modo.**
   El baseline detalla sistemáticamente "en modo juego X, en modo edición Y" (el dado se lanza en juego pero no en edición; la carta dentro de un mazo se filtra en ambos modos, a diferencia de "oculto" que solo en juego; las flechas no existen en modo juego). El minimal lo colapsa a `**Available in**: Modo edición y modo juego`.

3. **Cero diagramas.**
   El baseline usa `stateDiagram-v2` / `flowchart` para flujos no triviales (navegación de pestañas de la modal, flujo de importación, máquina de estados de la carta). El minimal no tiene ninguno. Para features con estados (importación, modal de tabs, volteo de carta) esto es una pérdida real de comprensión.

4. **Los dos componentes más complejos quedan en un párrafo.**
   `022-carta` (5.271 palabras en baseline) y `023-mazo` (1.743) son el núcleo del producto. El minimal les da 103 y 97 palabras. El titular es correcto; todo lo demás — que es donde está el 90 % del comportamiento y de las trampas — no está.

5. **Sin trazabilidad ni historia.**
   El baseline lleva por feature la lista real de cambios (`Code: 00020, 00031, 00063, 00129, 00210`) y fechas distintas (`Since: 2026-07-19`, `Last modified: 2026-08-19`). El minimal pone `Code: init` y `2026-08-28` en las 27 — metadatos de relleno. Se pierde "cuándo entró esto y por qué", y "qué cambió por última vez".

6. **Sin enlaces cruzados.**
   El baseline teje las features entre sí (`ver [Etiquetas](008-…)`, `ver [Interacciones programadas](014-…)`). El minimal no enlaza nada, pese a haber fusionado features que en el baseline se referencian mutuamente. El lector no puede navegar el grafo de dependencias funcionales.

7. **Features transversales perdidas.**
   `033-modal-de-error-comun` ("todo error de la app se comunica con el mismo elemento") y `036-contenido-de-ejemplo` son decisiones de producto con valor propio. El minimal las disuelve en cláusulas dentro de otras entradas o las omite.

---

## 4. Diagnóstico transversal

### 4.1 Qué tipo de conocimiento se pierde

Igual que en el análisis de arquitectura/estilo, el patrón es claro:

- **El `minimal` captura bien el "qué":** qué features existen, en qué área encajan, qué hacen a grandes rasgos. Como **catálogo de capacidades** es fiable y está bien ordenado.
- **El `minimal` no captura el "cómo se comporta exactamente":** rangos válidos, defaults, qué pasa en el borde, diferencias por modo, secuencias de pasos, estados. Todo eso vive repartido por el código (validaciones en `ui/`, defaults en `core/`, ramas por modo en `modes/`) y no se condensa en una pasada de lectura orientada a "resumir la feature".
- **Y no captura nada histórico:** qué cambio introdujo la feature, cuándo, qué la modificó después, cómo se relaciona con otras. Eso solo está en el control de versiones y en la cabeza de quien lo hizo.

Coherente con lo esperable de una generación automática "solo mirando el código": ve la superficie funcional, no la especificación ni la genealogía.

### 4.2 Precisión — discrepancia a verificar

**`017-texto` ("Cuadro de texto").**

| | Contenido |
|---|---|
| **Minimal** (`017-texto`) | "Cuadro de texto con formato enriquecido, escrito en **Markdown o en HTML**." |
| **Baseline** (`017-componente-cuadro-de-texto`, 89 pal.) | Cuadro de texto simple: propiedades `contenido`, `tamañoFuente`, `colorTexto`, `colorFondo`. Sin mención a Markdown/HTML. |
| **Baseline** (`021-componente-visor-de-documentos`) | *Este* es el que interpreta Markdown/HTML (`formato: 'markdown' | 'html'`, `core/markdown.js`, saneado). |

El minimal parece haber **atribuido al "cuadro de texto" (`'texto'`) una capacidad que es del "visor de documentos" (`'documento'`)**. El propio minimal tiene `018-documento` correcto ("texto o Markdown pegado … se sanea"), así que es una confusión entre los dos tipos en `017`, no un desconocimiento del visor. **Verificar contra `src/ui/componentModal.js` / la definición de `'texto'` en el código de 0.9.6b9** — si `'texto'` realmente solo lleva contenido/tamaño/color, `017-texto` del minimal está mal.

(No se han encontrado otras afirmaciones incorrectas. El resto del minimal es conservador y fiable.)

### 4.3 Organización

En igualdad de contenido, el `minimal` **organiza mejor** el catálogo funcional que el baseline:
- INDEX temático de 7 áreas vs. lista plana de 36.
- Fusión de features atómicas (que en el baseline son cambios históricos sueltos) en conceptos de usuario.
- Metadatos uniformes.

Si al nivel `minimal` se le pidiera **más profundidad por entrada** manteniendo esta taxonomía, el resultado sería una buena documentación funcional.

---

## 5. Conclusiones y recomendaciones

### 5.1 Sobre el nivel `minimal` como tal

**Cumple como catálogo de features.** 27 entradas de un párrafo, bien clasificadas, sin errores materiales (salvo la duda de `017`), en ~2.200 palabras. Para "¿qué sabe hacer esta app?" o para el arranque de un agente, es suficiente y está limpio.

**No es especificación funcional.** Cubre ~9 % del volumen del baseline. Falta todo lo accionable: rangos, defaults, casos límite, comportamiento por modo, flujos paso a paso, diagramas de estado, migraciones detalladas, y la trazabilidad a cambios. Un desarrollador no puede implementar ni un QA testear a partir de estas entradas.

### 5.2 Prioridades si se quiere subir de nivel

Por orden de retorno:

1. **Añadir valores concretos a cada entrada**: rangos válidos, defaults, mínimos/máximos. Es lo más barato de regenerar (están en las validaciones del código) y lo que más cambia la utilidad.
2. **Sección "comportamiento por modo"** en cada feature que se comporte distinto en juego vs. edición.
3. **Expandir `carta` y `mazo`** a documentos propios de varias secciones (hoy: 1 párrafo cada uno para los dos componentes más complejos).
4. **Recuperar `011` (búsqueda de imagen)** y **`033` (modal de error común)** como entradas propias.
5. **Casos límite explícitos**: qué pasa con 0 componentes, lista de valores vacía, importar referencia rota, borrar recurso en uso, cuota de `localStorage` excedida (algunos ya están; sistematizarlo).
6. **Diagramas de estado/flujo** para: navegación de la modal de tabs, flujo de importación, volteo de carta, sacar carta de mazo.
7. **Enlaces cruzados** entre features fusionadas y relacionadas.
8. **Trazabilidad**: si el generador puede leer el historial de git, poblar `Code:` y las fechas reales en vez de `init` / `2026-08-28`.

### 5.3 Verificación pendiente

- **`017-texto`**: confirmar en el código de 0.9.6b9 si el "cuadro de texto" interpreta Markdown/HTML (minimal) o es texto plano con contenido/tamaño/color (baseline). Sospecha alta de confusión con el "visor de documentos".
- Confirmar que las 27 features del minimal no omiten ninguna capacidad viva de 0.9.6b9 más allá de las ya señaladas (`011`, `033`).
