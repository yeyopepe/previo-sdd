# Diseño técnico — Prototipo digital "BF Factory"

Mapa de la documentación de arquitectura. Este fichero cubre objetivo/restricciones, capas, convenciones de código y el checklist a revisar al añadir un tipo/colección nuevo. Para modelo de datos, modos, UI y persistencia, ver la tabla de ficheros hermanos al final.

## 1. Objetivo y restricciones

- Prototipo digital funciona en cualquier navegador moderno.
- Entregable: único fichero HTML autocontenido (JS y CSS incrustados, cualquier librería externa embebida en el propio fichero).
- Se abre con doble clic (`file://`), sin servidor ni instalación.
- Build no depende de Node.js ni de herramientas de build complejas: usa Python.
- Código fuente organizado en ficheros/capas separadas dentro de `/src`.
- `src/scripts/build.py` transforma el código fuente en un fichero único versionado bajo `src/_output/versions/`.

## 2. Arquitectura por capas

```
core/    → estado de la aplicación, modelo de datos (componentes y recursos), bus de eventos, persistencia y exportación a fichero
modes/   → modo juego (play) y modo edición (edit), cada uno con su propia carpeta
ui/      → elementos de interfaz reutilizables entre modos
data/    → datos de versión de la app y recursos por defecto de la galería
main.js  → bootstrap: conecta las capas anteriores
```

Dependencias entre capas (flecha = "depende de"):

```
modes/* ──▶ ui/* ──▶ core/*
modes/* ──────────▶ core/*
main.js ──▶ data/*, ui/*, modes/*, core/*
```

- `core` no depende de ninguna otra capa.
- `ui` solo depende de `core` (lee/escribe estado).
- `modes` compone `ui` y `core` para construir cada pantalla.
- `main.js` es el único punto que conoce y conecta todas las capas.
- Estado (`core/state.js`) es la única fuente de verdad.
- Cambios se notifican vía bus de eventos simple (`core/eventBus.js`, `emit`/`on`) para que la UI se vuelva a renderizar sin acoplar módulos entre sí.

## 7. Convenciones de código

- Módulos ES (`import`/`export`) organizados por capa/responsabilidad, un fichero por módulo funcional.
- Sin dependencias externas por defecto.
- Librería nueva solo se incorpora si su bundle puede embeberse íntegramente en el HTML final (sin CDN en runtime ni instalación adicional).
- Recursos gráficos van en `/src/img`, organizados por tipo de componente.
- Convenciones visuales (tokens de color, tipografía, espaciado, nomenclatura BEM, patrones de componente) documentadas en `design/docs/style/`.
- `src/test/` contiene ficheros `.json` de ejemplo con el formato exportado por "Guardar a fichero" (`core/fileExport.js`: `{ version, components, resources }`), para importar manualmente (pegando en `#initial-state`, o vía `localStorage`) y probar tipos de componente ya configurados.
- Comentarios en código: solo los necesarios. Explican el porqué no evidente (restricción oculta, invariante, workaround puntual), nunca el qué (ya lo dice el propio código). Sin comentario si borrarlo no confundiría a quien lea después.
- Estilo del comentario, cuando hace falta: igual que la documentación técnica — telegráfico. Sin artículos superfluos, sin adverbios de relleno, verbos en presente, sujeto implícito. Referencias (nombre de campo, tipo, fichero) siempre explícitas, sin ambigüedad.
- Excepción: `src/vendor/` y `src/scripts/vendor/` son código de terceros tal cual (§2) — sus comentarios no se tocan.

## 8. Checklist al añadir un tipo/colección nuevo

Funcionalidades transversales, no ligadas a un único tipo — recorren "todos los que haya". Revisar cada una al añadir un tipo de componente o una colección nueva a nivel de `core/state.js`:

- **Persistencia y guardado a fichero** (`core/persistence.js`, `core/fileExport.js`): ambos serializan una lista fija de campos (`components`, `panelState`, `resources`, `resourcePanelState`, `resourcesSeeded`, `tags`, `tagPanelState`, `appTitle`). Colección/campo nuevo a nivel de `state.js` debe añadirse explícitamente en los dos sitios, y a la suscripción de eventos del autoguardado — si no, no se guarda ni se exporta.
- **Detección de uso de un recurso** (`core/resource.js`, `isResourceInUse`/`getComponentsUsingResource` + helper `collectDeepValues`): recorre `component.properties` en profundidad para encontrar cualquier referencia a un `resourceId`. Si un tipo nuevo guarda referencias fuera de objetos/arrays planos (p. ej. claves de un `Map`), el borrado de ese recurso no se bloquea aunque esté en uso.
- **Alta de un tipo de componente nuevo** (`ui/componentTypeModal.js` + `createDefaultComponent`/`DEFAULT_*_PROPERTIES` de `ui/componentModal.js`): lista de tipos disponibles y valores por defecto (tamaño inicial, `bloqueado`, `properties` de partida) están hardcodeados ahí. Tipo nuevo no aparece en el selector de alta ni tiene valores por defecto si no se añade en ambos sitios.
- **Renderizado en la mesa** (`ui/componentRenderer.js`): cada tipo necesita su propia rama de dibujo dentro de `renderComponentsOnTable`. Debe respetar reglas transversales: overflow del contenido recortado en contenedor interno (nunca en el exterior, por la etiqueta `identifyMode: 'label'`), orden de dibujo según `order` (z-index visual), soporte de `onSelect`/`onToggleSelect`/`onMove`/`onResize` si aplica.
- **Redimensionado con restricción de proporción** (`ui/resizeHandle.js`, parámetro `clamp`): tipos que fuerzan proporción fija (`'dado'` con 1:1, `'carta'` con `getProporcionRatio`) pasan su propio `clamp`. Tipo nuevo con esa necesidad replica el patrón — `resizeHandle.js` no lo hace por sí solo.
- **`getComponentsBounds`** (`ui/componentRenderer.js`): usa los mismos valores por defecto que el renderizado (`x`/`y`/`width`/`height` mínimos) para la caja envolvente de "Ajustar zoom". Si un tipo nuevo cambia esos criterios de tamaño por defecto, la función puede desalinearse del renderizado real.
- **Recursos por defecto y su siembra** (`data/defaultResources.js`, `main.js`): tipo de recurso nuevo (además de `'imagen'`/`'tipografia'`) o extensión de fichero nueva requiere revisar `resourceTypeForFileName` (`core/resource.js`).
- **Guía de estilo** (`design/docs/style/03-modales-menus.md` y demás): revisar excepciones ya catalogadas (bisel de `'tableroSimple'`/`'dado'`, `border-radius` de "contenedores destacados" reutilizado por `'carta'`) antes de introducir una excepción nueva.
- **Menú contextual, candado de bloqueo, indicador de oculto** (`ui/componentRenderer.js`): tipo nuevo que use `renderComponentsOnTable` obtiene automáticamente listener `contextmenu` (`onContextMenu`), insignia de candado (`showLockIndicator`) e insignia de "Oculto" (`showHiddenIndicator`) sin nada específico por tipo. Revisar solo si el tipo nuevo necesita acción **específica** en el menú contextual — se pasa vía `specificItems` de `openContextMenu` desde el modo que lo invoque, no desde `componentRenderer.js`.
- **Ficheros de prueba** (`src/test/*.json`): no se actualizan automáticamente. Añadir un ejemplo del tipo nuevo ya configurado.

## Ficheros hermanos

| Fichero | Cubre |
|---|---|
| `01-component-model.md` | Modelo genérico de componente (campos, tabla), lógica de `order`, copias vinculadas (`copyOf`) |
| `02-component-types.md` | Los ocho tipos de componente implementados y sus propiedades específicas |
| `03-groups-resources.md` | Modelo de etiqueta, modelo de recurso/galería, migración de `'ficha'`, portapapeles de estilo |
| `04-modes.md` | Modo juego vs modo edición: paneles, selección, menús contextuales, indicadores, z-index, título editable |
| `05-ui-layer.md` | Módulos de la capa UI reutilizables entre modos |
| `06-persistence-build.md` | Flujo de desarrollo/build y persistencia/guardado a fichero |
