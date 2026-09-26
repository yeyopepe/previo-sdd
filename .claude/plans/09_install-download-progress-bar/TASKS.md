# Tasks: barra de progreso 0-100% + fallback a tag en los scripts de instalación

## 1. `install.sh` — barra de progreso

- [ ] Sustituir `curl -fsSL "$TARBALL" | tar -xz -C "$TMP" --strip-components=1`
      (línea 34) por descarga a fichero + extracción en dos pasos:
      `curl -fL --progress-bar "$TARBALL" -o "$TAR_PATH"` seguido de
      `tar -xzf "$TAR_PATH" -C "$TMP" --strip-components=1`.
- [ ] Declarar `TAR_PATH="$TMP/previo.tar.gz"` antes de la descarga.
- [ ] Envolver la llamada a curl con `printf '\033[34m'` antes y
      `printf '\033[0m'` después, para que la barra se imprima en azul.

## 2. `install.ps1` — barra de progreso

- [ ] Sustituir `Invoke-WebRequest -Uri $Tarball -OutFile $TarPath`
      (línea 37) por descarga vía `System.Net.Http.HttpClient` a stream,
      con la función `Write-ProgressBar` (barra ASCII de 40 caracteres,
      `%`, tamaño `MB/MB`, velocidad `MB/s`, repintado en una sola línea
      con `` `r ``).
- [ ] Añadir `Add-Type -AssemblyName System.Net.Http` antes del bloque de
      descarga.
- [ ] Envolver la descarga en `try/finally` con `$httpClient.Dispose()`,
      dejando intacto el `try/finally` externo existente que limpia `$Tmp`.
- [ ] En `Write-ProgressBar`, imprimir el relleno `$bar` (`=`/`>`) con
      `Write-Host -NoNewline $bar -ForegroundColor Blue`, separado de los
      corchetes y del resto de la línea (`%`, tamaño, velocidad), que se
      quedan en el color de texto normal.

## 3. Fallback a tag — `install.sh`

- [ ] Sustituir el bloque de resolución de `TAG` (líneas 15-23) para que,
      si `GET /repos/${REPO}/releases/tags/${REQUESTED_TAG}` falla,
      compruebe `GET /repos/${REPO}/git/refs/tags/${REQUESTED_TAG}`
      (`curl -fsSL -o /dev/null`) antes de abortar.
- [ ] Añadir la variable `INSTALLED_FROM_RAW_TAG` (0/1) para saber, más
      adelante en el script, si hay que mostrar el aviso de tag no
      publicado.
- [ ] Si el tag puro existe, usar `TAG="$REQUESTED_TAG"` directamente
      (sin pasar por `RELEASE_JSON`) y continuar el flujo normal
      (`TARBALL`, descarga, extracción) sin cambios.
- [ ] Si ni el release ni el tag puro existen, mantener el mensaje de
      error actual ("Version '...' doesn't exist in Previo's releases.")
      y el `exit 1`.
- [ ] Añadir, junto a los otros avisos de bloque `====` (tras la sección
      de sync de skills/docs, antes o junto al aviso de changelog
      faltante), el nuevo bloque de aviso cuando
      `INSTALLED_FROM_RAW_TAG=1`, envuelto en `printf '\033[33m'` /
      `printf '\033[0m'` para que se imprima en amarillo.
- [ ] Aplicar el mismo tratamiento (envolver con `printf '\033[33m'` /
      `printf '\033[0m'`) al bloque de aviso ya existente de changelog
      faltante (`install.sh:83-89`), por consistencia.

## 4. Fallback a tag — `install.ps1`

- [ ] Sustituir el bloque de resolución de `$Tag` (líneas 15-26) para que,
      si `Invoke-RestMethod -Uri ".../releases/tags/$Version"` lanza
      excepción, compruebe
      `Invoke-RestMethod -Uri ".../git/refs/tags/$Version"` antes de
      volver a lanzar el error original.
- [ ] Añadir la variable `$InstalledFromRawTag` (bool) para saber, más
      adelante en el script, si hay que mostrar el aviso de tag no
      publicado.
- [ ] Si el tag puro existe, usar `$Tag = $Version` directamente y
      continuar el flujo normal (`$Tarball`, descarga, extracción) sin
      cambios.
- [ ] Si ni el release ni el tag puro existen, mantener el mensaje de
      error actual (`throw "Version '$Version' doesn't exist in Previo's
      releases."`).
- [ ] Añadir, junto a los otros avisos de bloque `====` (junto al aviso
      de changelog faltante), el nuevo bloque de aviso cuando
      `$InstalledFromRawTag` sea `$true`, con cada línea usando
      `-ForegroundColor Yellow`.
- [ ] Aplicar `-ForegroundColor Yellow` al bloque de aviso ya existente
      de changelog faltante (`install.ps1:96-103`), por consistencia.

## 5. Verificación manual

- [ ] `install.sh` contra un release real: aparece la barra
      `curl --progress-bar` en terminal interactiva y el tarball se
      extrae igual que antes.
- [ ] `install.ps1` interactivo: la barra manual avanza `0%` → `100%` en
      una sola línea, sin líneas basura, con tamaño/velocidad en vivo, y
      el fichero descargado es idéntico en tamaño/hash al que producía
      `Invoke-WebRequest`.
- [ ] Ambos scripts siguen funcionando invocados vía pipe
      (`curl ... | sh`, `irm ... | iex`).
- [ ] Pedir una versión que existe como release publicado → comportamiento
      idéntico al actual, sin aviso de tag crudo.
- [ ] Pedir una versión que no existe como release pero sí como tag de
      git puro → se instala y se muestra el aviso, en ambos scripts.
- [ ] Pedir una versión que no existe ni como release ni como tag → falla
      con el mismo mensaje de error que hoy.
- [ ] No pasar versión (instalar "latest") → sigue resolviendo el último
      release publicado, sin pasar por el camino de fallback a tag.
- [ ] Confirmar visualmente el color: la barra de progreso en azul (curl
      en terminal interactiva; barra manual de `install.ps1`), y los
      bloques de aviso (`Warning: ...` de tag crudo, y el de changelog
      faltante) en amarillo, en ambos scripts.
