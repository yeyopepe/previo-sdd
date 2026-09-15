# Cómo compilar el entregable de este proyecto

Fichero propio de `pv-version` (no forma parte de `.claude/pv-context.json`): describe el procedimiento de shell/build concreto de este repo para generar el entregable jugable. Lo rellena `pv-version` la primera vez que se invoca y el fichero no existe todavía, preguntando al usuario; en invocaciones siguientes se lee y se sigue tal cual, sin volver a preguntar. También se actualiza cuando el usuario reporta un cambio en este procedimiento.

## Distinción: build interna vs. versión oficial

En este repo hay dos procesos distintos:

- **Build interna** (`src/scripts/build.py`): se genera tras aplicar cambios, para probar. Numeración automática `vNNNNN`. **NO es lo que `pv-version` debe empaquetar.**
- **Versión oficial** (`src/scripts/generate-version.py`): el entregable que `pv-version` prepara. Versión semántica `x.y.z` confirmada con el usuario. Internamente lanza `build.py`, así que arrastra su efecto secundario.

Este documento describe **el proceso de versión oficial**.

## Comando(s) a ejecutar

Desde cualquier ubicación del repo:

```
python src/scripts/generate-version.py
```

El script es **interactivo**: al arrancar pregunta por consola `Version oficial a empaquetar (formato x.y.z):`. Teclea ahí la versión oficial ya confirmada con el usuario (formato `x.y.z`, p. ej. `0.9.0`). El script rechaza y vuelve a preguntar si el formato no es `x.y.z`.

Comando único: genera el entregable oficial completo en una sola pasada.

## Fichero(s) generado(s)

El script deja **tres ficheros** en `src/_output/versions/official/v{x.y.z}/`. Los tres son artefactos del entregable oficial y `pv-version` debe copiarlos todos a `versions/{XXXX}/files/` (una `--source` por fichero en `copy-build-artifacts.py`):

1. `bgfactory-{x.y.z}.html` — el HTML autocontenido, idéntico en contenido a la build interna pero con la versión reescrita a la oficial:
   - `<title>BG Factory v.{x.y.z}</title>`
   - `const CURRENT_VERSION = 'v{x.y.z}';` (conserva el prefijo `v`; `core/appTitle.js` hace `CURRENT_VERSION.slice(1)`)
2. `README.md` — README del repo (inglés), copiado tal cual desde la raíz.
3. `README.es.md` — README del repo (español), copiado tal cual desde la raíz.

El script crea la subcarpeta `official/v{x.y.z}/` si no existe. Esa **misma carpeta** es donde debe crearse después el fichero de changelog (ver "Notas"). Al terminar, el script imprime la ruta del HTML (`Paquete oficial generado en src\_output\versions\official\vX.Y.Z\bgfactory-X.Y.Z.html`) y una línea `README incluido: ...` por cada README copiado.

Si falta cualquiera de los dos README en la raíz del repo, el script aborta con error sin dejar el entregable a medias.

## Partida de ejemplo a incluir en `files/samples/`

Además de los tres artefactos anteriores, hay que copiar en `versions/{XXXX}/files/samples/` (subcarpeta `samples/` dentro de `files/`, créala si no existe):

- El fichero `.json` **más reciente** (por número de versión en el nombre, p. ej. `Plinius versus Vesuvium v.00239.json` → el de `vNNNNN` más alto) que haya en `games/plinius-vs-vesubio/`. Se copia tal cual, sin renombrar.

Este paso es manual (no lo hace `generate-version.py`): `pv-version` lo realiza tras copiar los artefactos del entregable.

## Notas

- **Changelog**: tras generar la versión oficial, crear el fichero de changelog dentro de `src/_output/versions/official/v{x.y.z}/` (junto al HTML). Ese es el trabajo que `pv-version` encadena a `pv-internal-changelog` pasándole esa carpeta como destino.
- **Efecto secundario en el repo**: `generate-version.py` lanza `build.py`, que incrementa `CURRENT_VERSION` en `src/data/version.js`. Ese cambio queda sin commitear en el árbol de trabajo tras ejecutar el script; consérvalo (es la fuente de verdad del contador interno).
- El script aborta con error, sin generar el paquete oficial, si:
  - `build.py` falla (código de salida ≠ 0).
  - `src/data/version.js` no tiene una `CURRENT_VERSION` con formato `'vNNNNN'`.
  - No aparece el fichero de build interno esperado (`src/_output/versions/index-vNNNNN.html`).
  - No encuentra en el bundle los fragmentos de versión a reescribir (`v.NNNNN` en el `<title>` y `'vNNNNN'` en `CURRENT_VERSION`).
  - Falta `README.md` o `README.es.md` en la raíz del repo.
- No requiere Node.js ni instalación de paquetes: solo Python 3 de la librería estándar.
