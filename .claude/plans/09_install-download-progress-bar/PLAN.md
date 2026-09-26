# Plan: barra de progreso 0-100% en los scripts de instalación

## Índice

- [Objetivo](#objetivo)
- [Contexto](#contexto)
- [Cambios](#cambios)
  - [1. `install.sh`](#1-installsh)
  - [2. `install.ps1`](#2-installps1)
  - [3. Fallback a tag cuando la versión no existe como release](#3-fallback-a-tag-cuando-la-versión-no-existe-como-release)
- [Fuera de alcance](#fuera-de-alcance)
- [Verificación](#verificación)
- [TASKS.md](TASKS.md)
- [Reviews](#reviews)

## Objetivo

En `install.sh` e `install.ps1`: (1) mostrar una barra de progreso simple
`0-100%` al descargar el tarball del release, en azul, en lugar de la
salida actual (nada, o el rendimiento degradado de `Invoke-WebRequest`);
y (2) cuando se pide una versión concreta que no existe como release
publicado, comprobar si existe como tag puro en el repo y, si es así,
instalarla igualmente avisando en amarillo de que no es una versión
publicada.

## Contexto

`install.sh` e `install.ps1` descargan el tarball del release (`TARBALL` /
`$Tarball`) sin ningún indicador de progreso reconocible:

- `install.sh:34` usa `curl -fsSL "$TARBALL" | tar -xz ...`. La flag `-s`
  (silent) de curl suprime también su barra de progreso nativa, y como va
  en pipe a `tar` tampoco se puede usar `-#`/`--progress-bar` de forma
  fiable (curl detecta que stdout no es una TTY interactiva en algunos
  casos, pero aquí el problema real es `-s`).
- `install.ps1:37` usa `Invoke-WebRequest -Uri $Tarball -OutFile $TarPath`.
  Por defecto `Invoke-WebRequest` sí dibuja una barra de progreso nativa
  de PowerShell, pero es conocida por ser muy lenta (activa el progress
  reporting interno del `WebClient` subyacente, que puede ralentizar la
  descarga 10-100x en archivos grandes).

Además, hoy ambos scripts solo saben resolver una versión pedida
explícitamente si existe como **release publicado**: llaman a
`GET /repos/{repo}/releases/tags/{tag}` (`install.sh:16`,
`install.ps1:17`), que devuelve 404 tanto si el tag no existe como si
existe pero no tiene release asociado. En ese segundo caso el script
aborta igual que si la versión no existiera en absoluto, aunque el tag —
y por tanto el tarball de código fuente en
`archive/refs/tags/{tag}.tar.gz` — sí exista y sea perfectamente
descargable.

## Cambios

### 1. `install.sh`

Sustituir la descarga en un solo paso (descarga+extracción en pipe) por
dos pasos: descargar a fichero con barra de progreso, luego extraer.

```sh
TAR_PATH="$TMP/previo.tar.gz"
echo "Downloading Previo (${TAG})..."
printf '\033[34m'
curl -fL --progress-bar "$TARBALL" -o "$TAR_PATH"
printf '\033[0m'
tar -xzf "$TAR_PATH" -C "$TMP" --strip-components=1
```

- Quitar `-s` (silent) y usar `--progress-bar` en su lugar: curl dibuja
  una barra `#######` con porcentaje cuando stderr es una terminal.
  `--progress-bar` no imprime un `0-100%` numérico grande, pero sí
  incluye el porcentaje inline (formato `curl` estándar: `Total ... %`).
- Nota: `--progress-bar` de curl no funciona bien si stderr no es tty
  (p.ej. pipeado a un log); en ese caso curl cae a no mostrar nada, lo
  cual es aceptable (no rompe el script).
- **Color**: curl dibuja la barra internamente — no tiene flag para
  forzar color en `--progress-bar`. Se envuelve la llamada con
  `printf '\033[34m'` (azul) antes y `printf '\033[0m'` (reset) después;
  como curl repinta toda la línea con `\r` dentro de ese rango, la línea
  entera queda en azul mientras avanza. Solo aplica si stderr es tty —
  si no lo es, curl no imprime nada y los `printf` son un no-op visual
  (no rompen el pipe).

**Decisión**: usar `curl -fL --progress-bar` (opción simple, sin
dependencias nuevas, evita reinventar un parser de porcentaje).

**Ejemplo real de salida** (`curl --progress-bar`, terminal ~80 columnas,
la línea de la barra se imprime en azul en terminales con color):

<pre>
Downloading Previo (v0.9.8)...
<span style="color:#3b82f6">######################################################          82.4%</span>
</pre>

Progresión en el tiempo (misma línea, se sobreescribe con `\r`, todo en azul):

<pre>
Downloading Previo (v0.9.8)...
<span style="color:#3b82f6">#                                                                 1.2%</span>
<span style="color:#3b82f6">########                                                         12.8%</span>
<span style="color:#3b82f6">###############################                                 48.3%</span>
<span style="color:#3b82f6">############################################################   100.0%</span>
</pre>

Notas sobre el formato real de curl (no es un invento, así es como lo pinta):

- Es una única línea que crece de izquierda a derecha con `#`, el resto
  en blanco hasta completar el ancho de terminal, y el porcentaje pegado
  al final a la derecha.
- No hay `[` `]` ni corchetes — a diferencia de `pv` o de barras hechas a
  mano, curl no los añade.
- Cuando termina, la línea deja de refrescarse en el 100% y el prompt
  continúa en la línea siguiente (la de `tar -xzf`).
- Si stderr no es tty (log, CI sin tty asignado), no se imprime nada de
  esto — el script sigue funcionando, solo sin indicador visual.

**Nota — diferencia de formato con `install.ps1` (decisión consciente,
no descuido)**: la barra manual de `install.ps1` (sección 2) sí dibuja
corchetes `[===>   ]` porque la construimos carácter a carácter; la de
`install.sh` no los tiene porque `curl --progress-bar` no acepta ningún
formato personalizado — solo se activa o desactiva, sin control sobre su
salida. Igualar el formato exigiría abandonar `--progress-bar` y
reimplementar el parseo de progreso a mano en `install.sh` (leyendo
`Content-Length` y el tamaño del fichero mientras se descarga), lo cual
va contra la decisión ya tomada en este mismo plan de no reinventar ese
parser (ver "Decisión" más abajo). Se acepta la pequeña diferencia
visual entre plataformas por ese motivo.

### 2. `install.ps1`

Sustituir `Invoke-WebRequest` por `.NET HttpClient` con descarga a stream
y una barra **manual** de una sola línea (nada de `Write-Progress`: ver
"Decisión" más abajo para por qué se descarta).

```powershell
Write-Host "Downloading Previo ($Tag)..."
$TarPath = Join-Path $Tmp "previo.tar.gz"

function Write-ProgressBar {
    param([long]$ReadTotal, [long]$TotalBytes, [double]$SpeedBps)

    $width = 40
    if ($TotalBytes -gt 0) {
        $pct = [int](($ReadTotal / $TotalBytes) * 100)
        $filled = [int]($width * $ReadTotal / $TotalBytes)
        if ($filled -ge $width) {
            $bar = ('=' * $width)
        } elseif ($filled -gt 0) {
            $bar = ('=' * ($filled - 1)) + '>' + (' ' * ($width - $filled))
        } else {
            $bar = ' ' * $width
        }
        $sizeInfo = "{0:N1}/{1:N1} MB" -f ($ReadTotal / 1MB), ($TotalBytes / 1MB)
    } else {
        $pct = 0
        $bar = ' ' * $width
        $sizeInfo = "{0:N1} MB" -f ($ReadTotal / 1MB)
    }
    $speedInfo = "{0:N1} MB/s" -f ($SpeedBps / 1MB)
    Write-Host -NoNewline ("`r[")
    Write-Host -NoNewline $bar -ForegroundColor Blue
    Write-Host -NoNewline ("] {0,3}% {1} {2}  " -f $pct, $sizeInfo, $speedInfo)
}

Add-Type -AssemblyName System.Net.Http
$httpClient = [System.Net.Http.HttpClient]::new()
try {
    $response = $httpClient.GetAsync($Tarball, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
    $response.EnsureSuccessStatusCode() | Out-Null
    $totalBytes = $response.Content.Headers.ContentLength

    $inStream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    $outStream = [System.IO.File]::Create($TarPath)
    $buffer = New-Object byte[] 81920
    $readTotal = 0
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while (($read = $inStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $outStream.Write($buffer, 0, $read)
        $readTotal += $read
        $speed = if ($sw.Elapsed.TotalSeconds -gt 0) { $readTotal / $sw.Elapsed.TotalSeconds } else { 0 }
        Write-ProgressBar -ReadTotal $readTotal -TotalBytes $totalBytes -SpeedBps $speed
    }
    Write-Host ""
    $outStream.Close()
    $inStream.Close()
}
finally {
    $httpClient.Dispose()
}
```

- Nada de `Write-Progress`: descartado a propósito (ver más abajo).
  En su lugar, `Write-Host -NoNewline "`r..."` repinta **una sola
  línea** con `\r`, igual que hace `curl --progress-bar`.
- Barra de 40 caracteres estilo `cargo`/`gh`/`rustup`: `=` rellenando lo
  ya descargado y una punta `>` marcando el frente de avance (ASCII
  puro, sin depender de que la consola tenga fuente con glifos Unicode —
  `cmd.exe` clásico y consolas remotas a veces los rompen). Lleva
  corchetes `[`/`]` porque la dibujamos nosotros carácter a carácter —
  `install.sh` no los tiene, ver la nota en la sección 1 sobre por qué
  esa diferencia de formato es intencional.
- Incluye tamaño (`MB/MB`) y velocidad instantánea (`MB/s`), calculada
  con `Stopwatch` sobre el total acumulado — más útil que un `%` pelado
  para saber si la descarga está viva o colgada.
- Si `Content-Length` no viene (`$totalBytes` es `-1`/`$null`), la barra
  queda vacía (sin `=`/`>`) y solo se actualizan tamaño descargado y
  velocidad (no debería ocurrir con GitHub releases, pero cubre el caso
  sin dejar una barra de progreso mintiendo un `%` inventado).
- **Color**: solo el relleno `=`/`>` se imprime con
  `-ForegroundColor Blue`; los corchetes `[`/`]`, el `%`, el tamaño y la
  velocidad se imprimen en el color de texto normal de la consola (tres
  `Write-Host -NoNewline` en vez de uno, para poder aplicar el color a
  un tramo sin afectar al resto de la línea).
- Mantener el resto del bloque `try/finally` existente para limpieza de
  `$Tmp`.

**Decisión: por qué no `Write-Progress`.** La primera versión de este
plan usaba `Write-Progress`, pero tiene problemas reales, no solo
estéticos:

1. Ocupa una región de 2-3 líneas separada del flujo normal de texto —
   inconsistente con la barra de una línea de `install.sh`.
2. Sin `Content-Length` no puede dibujar barra en absoluto (solo un
   spinner genérico "trabajando"), mientras que la versión manual sigue
   mostrando bytes y velocidad reales.
3. No se ve igual en todos los hosts (Windows Terminal vs consola
   clásica vs VS Code integrated terminal) — la manual es determinista
   porque la dibujamos nosotros carácter a carácter.

**Ejemplo real de salida** (barra manual, terminal ~80 columnas,
repintado in-place con `\r`, no son líneas nuevas; solo el relleno
`=`/`>` va en azul, el resto de la línea en color normal):

<pre>
Downloading Previo (v0.9.8)...
[<span style="color:#3b82f6">                                        </span>]   0% 0.0/9.4 MB  0.0 MB/s
</pre>

Progresión (misma línea, la punta `>` avanza y la velocidad se
actualiza en vivo — mismo lenguaje visual que `cargo build`/`gh`):

<pre>
[<span style="color:#3b82f6">===>                                    </span>]  12% 1.1/9.4 MB  3.2 MB/s
[<span style="color:#3b82f6">================>                       </span>]  42% 4.0/9.4 MB  4.8 MB/s
[<span style="color:#3b82f6">===============================>        </span>]  78% 7.3/9.4 MB  5.1 MB/s
[<span style="color:#3b82f6">========================================</span>] 100% 9.4/9.4 MB  5.0 MB/s
</pre>

Al llegar a 100%, la punta `>` desaparece (barra llena de `=`) y
`Write-Host ""` cierra la línea con un salto — el prompt continúa
normal (equivalente al comportamiento de curl).

Caso sin `Content-Length` (fallback, barra vacía, solo bytes y
velocidad se mueven):

<pre>
[                                        ]   0% 4.2 MB  4.6 MB/s
</pre>

### 3. Fallback a tag cuando la versión no existe como release

Hoy, si se pide una versión explícita (`install.sh <tag>` /
`$env:PREVIO_VERSION`), ambos scripts solo comprueban
`GET /repos/{repo}/releases/tags/{tag}` y abortan si falla. Ese endpoint
solo resuelve **releases publicados**: un tag que existe en el repo pero
sin release asociado da 404 igual que un tag que no existe en absoluto.

**Cambio**: si la comprobación de release falla, antes de abortar,
comprobar si el tag existe como tag de git puro con
`GET /repos/{repo}/git/refs/tags/{tag}` (200 si existe, 404 si no). Si
existe, continuar la instalación igual que hoy (la URL del tarball,
`archive/refs/tags/{tag}.tar.gz`, no depende de que haya release), pero
mostrando un aviso de que se instaló una versión no publicada. Si
tampoco existe como tag, abortar con el mismo mensaje de error que hoy.

**`install.sh`** — sustituir el bloque de resolución de `TAG` (líneas
15-23):

```sh
INSTALLED_FROM_RAW_TAG=0
if [ -n "$REQUESTED_TAG" ]; then
  RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/tags/${REQUESTED_TAG}") || RELEASE_JSON=""
  if [ -n "$RELEASE_JSON" ]; then
    TAG=$(echo "$RELEASE_JSON" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
  else
    if curl -fsSL -o /dev/null "https://api.github.com/repos/${REPO}/git/refs/tags/${REQUESTED_TAG}"; then
      TAG="$REQUESTED_TAG"
      INSTALLED_FROM_RAW_TAG=1
    else
      echo "Version '${REQUESTED_TAG}' doesn't exist in Previo's releases." >&2
      exit 1
    fi
  fi
else
  TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
fi
```

**`install.ps1`** — sustituir el bloque de resolución de `$Tag` (líneas
15-26):

```powershell
$InstalledFromRawTag = $false
if ($Version) {
    try {
        $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/tags/$Version"
        $Tag = $Release.tag_name
    }
    catch {
        try {
            Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/git/refs/tags/$Version" | Out-Null
            $Tag = $Version
            $InstalledFromRawTag = $true
        }
        catch {
            throw "Version '$Version' doesn't exist in Previo's releases."
        }
    }
}
else {
    $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
    $Tag = $Release.tag_name
}
```

**Aviso al usuario** (tras la descarga/instalación, siguiendo el mismo
formato de bloque `====...====` que el resto del script, ver
`install.sh:83-89` / `install.ps1:96-103`), en amarillo:

```sh
if [ "$INSTALLED_FROM_RAW_TAG" = "1" ]; then
  printf '\033[33m'
  echo "=========================================================="
  echo " Warning: '${TAG}' is not a published release, it was"
  echo " installed as a raw git tag. It may be untested/unstable."
  echo "=========================================================="
  printf '\033[0m'
  echo ""
fi
```

```powershell
if ($InstalledFromRawTag) {
    Write-Host "==========================================================" -ForegroundColor Yellow
    Write-Host " Warning: '$Tag' is not a published release, it was" -ForegroundColor Yellow
    Write-Host " installed as a raw git tag. It may be untested/unstable." -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Yellow
    Write-Host ""
}
```

**Alcance del amarillo**: aplica a este bloque de aviso nuevo, y por
consistencia también al bloque de aviso ya existente de changelog
faltante (`install.sh:83-89` / `install.ps1:96-103` — ver tarea
correspondiente en `TASKS.md`). El bloque de "You're updating.../First
install..." (no es un warning, es informativo) se deja en el color de
texto normal, sin cambios.

**Ejemplos exactos de cada caso** (con `REPO="yeyopepe/previo-sdd"`):

**Caso A — versión pedida existe como release publicado**
(comportamiento actual, sin cambios)

Ejemplo: `install.sh v0.9.8`, siendo `v0.9.8` un release publicado.

```
$ curl -fsSL "https://api.github.com/repos/yeyopepe/previo-sdd/releases/tags/v0.9.8"
# HTTP 200, cuerpo con "tag_name": "v0.9.8", ...
```

`RELEASE_JSON` no está vacío → `TAG="v0.9.8"`, `INSTALLED_FROM_RAW_TAG=0`.
Salida del script: sin aviso de tag crudo, igual que hoy.

**Caso B — versión pedida no existe como release, pero sí como tag de git puro**
(caso nuevo)

Ejemplo: `install.sh v0.9.8b14`, siendo `v0.9.8b14` un tag existente en el
repo (visible en `git tag` / en la pestaña "Tags" de GitHub) pero sin
release publicado asociado (no aparece en la pestaña "Releases").

```
$ curl -fsSL "https://api.github.com/repos/yeyopepe/previo-sdd/releases/tags/v0.9.8b14"
# HTTP 404 → curl -f hace que el comando falle → RELEASE_JSON=""

$ curl -fsSL -o /dev/null "https://api.github.com/repos/yeyopepe/previo-sdd/git/refs/tags/v0.9.8b14"
# HTTP 200 (el ref existe) → exit code 0
```

`RELEASE_JSON` vacío → se prueba `git/refs/tags` → existe → `TAG="v0.9.8b14"`,
`INSTALLED_FROM_RAW_TAG=1`. El script continúa exactamente igual que en el
caso A a partir de aquí (mismo `TARBALL`, misma descarga, misma barra de
progreso), y al final imprime:

<pre>
Downloading Previo (v0.9.8b14)...
<span style="color:#3b82f6">######################################################          100.0%</span>
Previo installed/updated in .claude/skills.

<span style="color:#eab308">==========================================================
 Warning: 'v0.9.8b14' is not a published release, it was
 installed as a raw git tag. It may be untested/unstable.
==========================================================</span>

==========================================================
 First install: run /pv-init in your agent to set it up.
==========================================================
</pre>

(la línea de la barra de progreso se imprime en azul; el bloque
`Warning: ...` se imprime en amarillo; el bloque `First install...` es
informativo y se deja en el color normal — equivalente en `install.ps1`:
mismo orden de bloques y mismos colores, con `Write-Host` en vez de
`echo`.)

**Caso C — versión pedida no existe ni como release ni como tag**
(comportamiento actual, sin cambios)

Ejemplo: `install.sh v9.9.9-inexistente`.

```
$ curl -fsSL "https://api.github.com/repos/yeyopepe/previo-sdd/releases/tags/v9.9.9-inexistente"
# HTTP 404 → RELEASE_JSON=""

$ curl -fsSL -o /dev/null "https://api.github.com/repos/yeyopepe/previo-sdd/git/refs/tags/v9.9.9-inexistente"
# HTTP 404 → exit code distinto de 0
```

Ninguna de las dos comprobaciones resuelve el tag → mensaje de error y
salida sin instalar nada:

```
Version 'v9.9.9-inexistente' doesn't exist in Previo's releases.
```

(exit code 1 en `install.sh`; excepción/`throw` que detiene la ejecución
en `install.ps1`, mismo texto de mensaje.)

**Caso D — sin versión pedida ("latest")**
(comportamiento actual, sin cambios; no pasa por el fallback a tag)

Ejemplo: `install.sh` (sin argumentos).

```
$ curl -fsSL "https://api.github.com/repos/yeyopepe/previo-sdd/releases/latest"
# HTTP 200, cuerpo con "tag_name": "<último release publicado>"
```

`REQUESTED_TAG` está vacío → se entra directo en la rama `else` →
`TAG="<último release publicado>"`. El bloque de resolución de release/tag
puro no se ejecuta en absoluto, `INSTALLED_FROM_RAW_TAG` permanece en su
valor por defecto (`0`) y no se muestra ningún aviso.

## Fuera de alcance

- No se añade barra de progreso a otras descargas del proyecto (no hay
  otras, confirmado por grep sobre `Invoke-WebRequest|DownloadFile|curl|wget`).
- El fallback a tag solo aplica cuando se pide una versión explícita; la
  resolución de "latest" (`releases/latest`) no cambia — "latest" siempre
  significa el último release publicado, nunca un tag suelto.

## Verificación

- `install.sh`: ejecutar contra un release real y confirmar que aparece
  la barra `curl --progress-bar` en terminal interactiva, y que el
  tarball se extrae igual que antes (`tar -xzf` en dos pasos en vez de
  pipe).
- `install.ps1`: ejecutar en PowerShell interactivo y confirmar que la
  barra manual avanza `0%` → `100%` en una sola línea (sin dejar líneas
  basura por cada refresco), que velocidad y tamaño se actualizan, y que
  el fichero descargado es idéntico en tamaño/hash al que producía
  `Invoke-WebRequest`.
- Confirmar que ambos scripts siguen funcionando cuando se invocan vía
  pipe (`curl ... | sh`, `irm ... | iex`), que es el modo de uso principal
  documentado en el README.
- Pedir una versión que existe como release publicado → sigue
  instalando igual que hoy, sin aviso de tag crudo.
- Pedir una versión que no existe como release pero sí como tag de git
  puro → se instala igualmente y se muestra el aviso de tag no
  publicado, en ambos scripts.
- Pedir una versión que no existe ni como release ni como tag → falla
  con el mismo mensaje de error que hoy ("Version '...' doesn't exist in
  Previo's releases."), sin cambios de comportamiento.
- Pedir "latest" (sin argumento) → sigue resolviendo el último release
  publicado, nunca cae en el camino de fallback a tag.

## Reviews

**2026-09-26**: análisis crítico inicial. Hallazgos de estructura (documento
suelto sin carpeta/TASKS.md/Índice/Objetivo/Reviews) y de contenido
(nueva funcionalidad de fallback a tag pedida por el usuario, sin
especificar endpoint ni mensaje de aviso, y en contradicción con el
"Fuera de alcance" original) resueltos en esta misma revisión: plan
migrado a carpeta con `PLAN.md`+`TASKS.md`, y añadida la sección
"3. Fallback a tag..." con endpoint `git/refs/tags/{tag}` y aviso en
bloque `====` consistente con el resto del script. Añadidos también
ejemplos exactos de los 4 casos (release existente, fallback a tag,
ninguno de los dos, "latest") en la sección 3.

**2026-09-26 (2)**: añadido color a los scripts: barras de progreso en
azul (envolviendo `curl --progress-bar` con ANSI en `install.sh`;
coloreando solo el relleno `=`/`>` con `-ForegroundColor Blue` en
`install.ps1`), y bloques de aviso (`Warning: ...`) en amarillo en
ambos scripts — incluido, por consistencia, el aviso ya existente de
changelog faltante. Tareas añadidas a `TASKS.md`.
