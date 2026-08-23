# 009 — Subida múltiple y por carpeta de recursos

**Area**: Mesa de juego

El botón "+ Añadir recurso" del panel de recursos despliega un menú con tres formas de añadir recursos a la galería, que conviven entre sí sin sustituirse:

- **Subir fichero**: comportamiento original, un único fichero mediante el selector de fichero del sistema.
- **Subir varios ficheros**: el mismo selector permitiendo marcar varios ficheros a la vez; todos los ficheros válidos elegidos se añaden como recursos independientes, igual que si se hubieran subido uno a uno.
- **Subir carpeta**: selector de carpeta del sistema de ficheros; se añaden como recursos todos los ficheros válidos que estén directamente dentro de ella — solo el primer nivel, sin entrar en subcarpetas (aviso junto a esta opción del menú recordándolo).

A diferencia de la subida de un único fichero (que corta con un aviso de error si el fichero no es válido, sin añadir nada), en una subida de varios ficheros o de una carpeta se suben todos los ficheros válidos y se omiten los no válidos: al terminar se muestra siempre un aviso resumen con el recuento de recursos añadidos (incluye los que se hayan reemplazado por confirmar un duplicado, ver abajo) y, si los hay, el detalle de los omitidos por formato no soportado (tabla con el nombre de cada fichero) y el recuento de los omitidos por estar dentro de una subcarpeta. Si una carpeta elegida no tiene ningún elemento con formato soportado en su primer nivel (vacía, solo con subcarpetas, o sin ningún formato soportado), se muestra en su lugar un aviso informativo indicando que no se ha encontrado ningún recurso válido, y no se añade nada.

**Aviso al añadir un recurso con nombre duplicado** (fix 00166): si el nombre de un fichero que se está añadiendo (sin la extensión, insensible a mayúsculas y tildes) coincide con el de un recurso ya existente en la galería, no se añade directamente — se avisa de que ya existe un recurso con ese nombre y de que continuar reemplazará su contenido (los componentes que ya lo usaban pasan a mostrar el nuevo), pidiendo confirmación antes de aplicar el reemplazo. Si se cancela, ese recurso en concreto no se añade ni se modifica nada. En la subida de varios ficheros o de una carpeta, todos los duplicados detectados en la misma operación (incluidos dos ficheros del propio lote con el mismo nombre entre sí) se agrupan en un único aviso de confirmación, listando cada nombre en conflicto; el resto de ficheros sin conflicto se añaden con normalidad sin esperar a esa confirmación.

- **Available in**: modo edición.
- **Code**: 00076, 00166.
- **Since**: 2026-07-24
- **Last modified**: 2026-08-06
