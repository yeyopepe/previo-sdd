# Changelog de Previo v0.9.5 (desde v0.9.21)

## Índice

- ⭐[Novedades](#novedades)
  - Auditoría de salud del framework y autorreparación
  - 📂Documentación del framework (3 cambios)
  - Análisis del código base en la primera inicialización
  - Soporte multilingüe
  - Verificación de versión del framework
  - Eliminación de entradas de la lista de ideas
  - Preparación aislada del changelog
- ✏️[Cambios](#cambios)
  - 📂Estructura y rutas de `workFolder` (4 cambios)
  - 📂Informes de `pv-status` (2 cambios)
  - Tolerancia al riesgo relajada en fixes triviales
  - La documentación técnica/de estilo ahora se redacta con reglas compartidas
  - Aumento del relleno de ceros por defecto en los códigos secuenciales
  - La base de modelo/esfuerzo por skill ahora se registra siempre
  - La configuración rota o desincronizada ahora se delega en `pv-update`
  - Traducción de la prosa del framework al inglés

## ⭐Novedades

- **Auditoría de salud del framework y autorreparación** — `pv-update`: se ha añadido una nueva skill que audita `.claude/pv-context.json` y los ficheros instalados del framework en busca de desincronizaciones — configuración rota, carpetas faltantes, códigos de cambio duplicados, versiones de skill que no coinciden, `pv.py` desactualizado, etiquetas de documento corruptas — y corrige automáticamente todo lo que puede determinar con seguridad, preguntando al usuario solo cuando la corrección implicaría adivinar (JSON inválido, o una posible regresión de versión).
- 📂**Documentación del framework**:
  - **Documentación de guía de usuario** — `pv-doc`: se ha añadido una guía de usuario bilingüe (inglés/español) que explica cómo usar el framework `pv-*`, algo que antes no estaba documentado fuera de las propias skills.
  - **Guía de redacción de la biblia de estilo** — `pv-internal-doc-style`: se ha añadido una nueva skill compartida que indica a `pv-do` qué categorías de estilo (redacción, diseño visual, interacción, accesibilidad, componentes reutilizables) aplican a un cambio concreto y qué debe registrar cada una, usada para mantener sincronizada la biblia de estilo del proyecto.
  - **Reglas compartidas de redacción de documentación técnica** — `pv-internal-doc-technical`: se ha añadido una nueva skill compartida que define las convenciones de redacción densas y orientadas a IA (etiquetas fijas, tablas, bloques de código) que debe seguir la documentación de arquitectura y de biblia de estilo, invocada por `pv-do` y `pv-init` antes de redactar ese contenido.
- **Análisis del código base en la primera inicialización** — `pv-init`: al inicializar sobre un proyecto que ya tiene código fuente, la skill ahora ofrece elegir entre un análisis mínimo o completo, y genera documentación real de arquitectura, estilo y funcionalidades a partir del código existente, en lugar de limitarse a crear plantillas vacías.
- **Soporte multilingüe** — `pv-init` y el framework en general: se ha añadido configuración para el idioma en que el framework se comunica con el usuario en el chat, además de idiomas opcionales independientes para los documentos de cambios en curso, el changelog de versión, la documentación de funcionalidades y la documentación técnica, cada uno con el idioma del chat como valor por defecto si no se especifica.
- **Verificación de versión del framework** — `pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-status`, `pv-todo`, `pv-version`: todas las skills invocables por el usuario ahora comprueban, antes de hacer cualquier otra cosa, que la versión instalada del framework coincide con la última verificada por `pv-update`, y se niegan a continuar (remitiendo al usuario a `pv-update`) si la configuración parece desactualizada o bloqueada.
- **Eliminación de entradas de la lista de ideas** — `pv-internal-workflow`: se ha añadido la capacidad de eliminar una entrada de la lista de ideas, expuesta internamente para la limpieza posterior a su conversión.
- **Preparación aislada del changelog** — `pv-internal-changelog`: las entradas pendientes de incluir en una versión ahora se preparan en una copia aislada en `closed/temp/` antes de redactar el changelog, de forma que las entradas de cambio/fix que se cierran mientras se redacta ya no interfieren con esa ejecución; la eliminación posterior de las entradas incorporadas ya no requiere confirmación del usuario, puesto que la copia aislada es demostrablemente segura de borrar.

## ✏️Cambios

- 📂**Estructura y rutas de `workFolder`**:
  - **Cambios en el comportamiento y valor por defecto de `workFolder`** — `pv-init`: la carpeta de trabajo del framework ahora usa por defecto una ruta fija `/previo-sdd` en lugar de la raíz del repositorio, y se escribe de forma silenciosa sin pedir confirmación al usuario (antes siempre se preguntaba/confirmaba); se ha añadido una nueva subcarpeta fija `stuff/` junto a `changes/`/`versions/`. Los proyectos inicializados previamente en la raíz del repositorio deberían volver a ejecutar `pv-init`/`pv-update` para revisar la nueva estructura.
  - **Rutas de documentación técnica/funcional ahora relativas a `workFolder`** — `pv-init`: las carpetas de documentación de arquitectura, biblia de estilo y funcionalidades ahora se ubican en relación con `workFolder` en lugar de la raíz del repositorio, alineándolas con `changes/`/`versions/`. Las configuraciones existentes que apunten fuera de `workFolder` necesitan revisión mediante `pv-update`.
  - **Reubicación del fichero de procedimiento de compilación** — `pv-version`: el documento de procedimiento de build/compilación del proyecto se ha movido de `{workFolder}/framework/how-to-compile-version.md` a `{workFolder}/stuff/how-to-compile-version.md`. Los proyectos existentes deben volver a ejecutar `pv-update` (o reubicar el fichero manualmente) tras actualizar.
  - **Resolución de rutas uniforme independientemente de la barra inicial** — `pv-internal-workflow`, `pv-how`: los valores de `workFolder` ahora se resuelven de la misma forma tengan o no una barra inicial, evitando comprobaciones inconsistentes de colisión de códigos de cambio (corrección interna sin cambio de comportamiento visible en proyectos correctamente configurados).
- 📂**Informes de `pv-status`**:
  - **El informe de estado incorpora datos de riesgo y versión** — `pv-status`: los informes de estado general y filtrado ahora muestran el nivel de riesgo evaluado de cada entrada y un recuento de versiones preparadas; el informe general también separa las entradas "en curso" en un grupo distinto de "listas para cerrar", junto a "planificadas, pendientes de implementación" y "pendientes de análisis técnico". El texto del propio informe (encabezados, etiquetas) ahora se muestra siempre en inglés, independientemente del idioma de chat configurado por el usuario, ya que lo generan scripts deterministas y no prosa redactada.
  - **Ancho configurable del informe de terminal** — `pv-status`: la salida de texto plano en terminal que usa `pv.py` ahora acepta un ancho de columna indicado por quien la invoca, en lugar de un valor fijo.
- **Tolerancia al riesgo relajada en fixes triviales** — `pv-fix`: la clasificación "rápida" (trivial) ahora tolera un pequeño riesgo para el resto de la aplicación en lugar de exigir riesgo exactamente nulo.
- **La documentación técnica/de estilo ahora se redacta con reglas compartidas** — `pv-do`: al actualizar la documentación de arquitectura o de biblia de estilo tras implementar un cambio, ahora carga las convenciones de redacción compartidas de `pv-internal-doc-technical` y, específicamente para la biblia de estilo, consulta a `pv-internal-doc-style` qué categorías aplican, en lugar de redactar ese contenido sin una base común.
- **Aumento del relleno de ceros por defecto en los códigos secuenciales** — `pv-init`: se ha aumentado el ancho de relleno de ceros por defecto para los códigos de cambio/fix, y el campo ahora siempre se escribe explícitamente en la configuración en lugar de dejarse como valor por defecto implícito.
- **La base de modelo/esfuerzo por skill ahora se registra siempre** — `pv-init`: el mapeo de qué modelo/esfuerzo de Claude usa cada skill `pv-*` ahora siempre se escribe en `pv-context.json` (reflejando el frontmatter real de cada skill), incluso cuando el usuario no personaliza nada, en lugar de omitirse cuando no se usa.
- **La configuración rota o desincronizada ahora se delega en `pv-update`** — `pv-init`: cuando detecta un problema más allá de un campo opcional sin configurar (JSON inválido, una referencia colgante, un `pv.py` desactualizado), ahora delega el diagnóstico y la reparación a la nueva skill `pv-update` en lugar de intentar corregirlo directamente.
- **Traducción de la prosa del framework al inglés** — casi todas las skills `pv-*`: todas las instrucciones de las skills, plantillas de mensajes y plantillas de documentos (antes escritas en español) se han traducido al inglés como idioma base del framework, usando en las etiquetas de campo de los documentos una nueva convención de marcador fijo para que sigan siendo interpretables independientemente del idioma de contenido configurado.
