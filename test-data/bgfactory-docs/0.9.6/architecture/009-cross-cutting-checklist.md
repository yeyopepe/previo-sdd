# 009 — Checklist: adding a type or a state collection

**Area**: Conventions

Cross-cutting features, not tied to a single type — they iterate "all there are". Review each when adding a component type, a new collection at the `core/state.js` level, or changing a component/group/tag's configuration UI:

| Aspecto | Fichero(s) | Qué revisar |
|---|---|---|
| Persistencia y guardado | `core/persistence.js` (`saveState`/`parseState`, `buildComponentsExport`/`parseImportedComponents`) | Añadir la colección/campo nuevo a `persistence.serializedFields` (ver `00-namespace.md`), a la exportación ligera si aplica, y a la suscripción de eventos de autosave (`core/eventBus.js`, ver `007-persistence-build.md`) — si no, ni se guarda ni se exporta |
| Detección de recurso en uso | `core/resource.js` (`isResourceInUse`/`getComponentsUsingResource` + `collectDeepValues`) | Si el tipo nuevo guarda referencias fuera de objetos/arrays planos (p. ej. claves de `Map`), borrar ese recurso no se bloquea aunque esté en uso |
| Creación de tipo nuevo | `ui/componentTypeModal.js` + `createDefaultComponent`/`DEFAULT_*_PROPERTIES` de `ui/componentModal.js` | Lista de tipos disponibles y valores por defecto hardcodeados; sin añadirlo en ambos no aparece en el selector ni tiene defaults |
| Render en la mesa | `ui/componentRenderer.js` (`renderComponentsOnTable`) | Rama de dibujo propia; respetar overflow en contenedor interno, orden por `order`, soporte `onSelect`/`onToggleSelect`/`onMove`/`onResize` |
| Resize con proporción fija | `ui/resizeHandle.js` (parámetro `clamp`) | Tipos con proporción fija (`'dado'` 1:1, `'carta'` `getProporcionRatio`) pasan su propio `clamp`; `resizeHandle.js` no lo hace solo |
| `getComponentsBounds` | `ui/componentRenderer.js` | Usa los mismos defaults que el render para el "Ajustar zoom"; si el tipo nuevo cambia los criterios de tamaño por defecto puede desincronizarse |
| Recursos por defecto y su seeding | `data/defaultResources.js`, `main.js` | Un tipo de recurso nuevo (más allá de `'imagen'`/`'tipografia'`) o una extensión nueva obliga a revisar `resourceTypeForFileName` (`core/resource.js`) |
| Guía de estilo | `../style/003-modales-menus.md` y otros | Revisar excepciones ya catalogadas (bisel de `'tableroSimple'`/`'dado'`, `border-radius` de contenedores destacados reusado por `'carta'`) antes de introducir una excepción nueva |
| Menú contextual, badge de bloqueo, indicador de oculto | `ui/componentRenderer.js` | Un tipo que use `renderComponentsOnTable` obtiene `contextmenu` (`onContextMenu`), badge de bloqueo (`showLockIndicator`) y badge "Oculto" (`showHiddenIndicator`) sin nada específico; un tipo sin caja de relleno propia (como `'texto'`) sí debe respetar el patrón de contenedor interno y anclar sus badges con offsets propios |
| Ficheros de test | `src/test/*.json` | No se actualizan solos; añadir un ejemplo del tipo nuevo ya configurado |
| Catálogo de propiedades (componente / grupo / etiqueta) | `../features/040-catalogo-de-propiedades-de-componentes-grupos-y-etiquetas.md` | Al añadir, quitar o reordenar una pestaña, sección o campo de `ui/componentModal.js` (y sus sub-modales), `ui/groupModal.js` o `ui/tagModal.js`, actualizar la Tabla A del bloque de esa ventana (fila, icono, tipo, contenedor, "Aparece en", ayuda, "Visible cuando…", clave i18n) y la Tabla B (solo si el elemento del modal de componente depende del tipo), y revisar las posiciones. Si `componentModal` cambia un rótulo compartido, comprobar que `groupModal` lo hereda como se espera |

Referencia de guía de estilo: `../style/003-modales-menus.md`.
