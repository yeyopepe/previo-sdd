# Plan: barra de progreso 0-100% en los scripts de instalación

## Contexto

`install.sh` e `install.ps1` descargan el tarball del release (`TARBALL` /
`$Tarball`) sin ningún indicador de progreso reconocible:

- `install.sh:34` usa `curl -fsSL "$TARBALL" | tar -xz ...`. La flag `-s`
  (silent) de curl suprime también su barra de progreso nativa, y como va
  en pipe a `tar` tampoco se puede usar `-#`/`--progress-bar` de forma
  fiable (curl detecta que stdout no es una TTY interactiva en algunos
  casos, pero aquí el problema real es `-s`).
- `install.ps1:37` usa `Invoke-WebRequest -Uri $Tarball -OutFile $TarPath`.
  Por defecto `Invoke-WebRequest` sí dibuja una barra de progreso window
  nativa de PowerShell, pero es conocida por ser muy lenta (activa el
  progress reporting interno del `WebClient` subyacente, que puede
  ralentizar la descarga 10-100x en archivos grandes).

Objetivo: en ambos scripts, mostrar una barra de progreso simple `0-100%`
en lugar de la salida actual (nada, o el rendimiento degradado de IWR).

## Cambios

### 1. `install.sh`

Sustituir la descarga en un solo paso (descarga+extracción en pipe) por
dos pasos: descargar a fichero con barra de progreso, luego extraer.

```sh
TAR_PATH="$TMP/previo.tar.gz"
echo "Downloading Previo (${TAG})..."
curl -fL --progress-bar "$TARBALL" -o "$TAR_PATH"
tar -xzf "$TAR_PATH" -C "$TMP" --strip-components=1
```

- Quitar `-s` (silent) y usar `--progress-bar` en su lugar: curl dibuja
  una barra `#######` con porcentaje cuando stderr es una terminal.
  `--progress-bar` no imprime un `0-100%` numérico grande, pero sí
  incluye el porcentaje inline (formato `curl` estándar: `Total ... %`).
  Si se quiere un `NN%` explícito y grande, ver la alternativa con `awk`
  más abajo.
- Nota: `--progress-bar` de curl no funciona bien si stderr no es tty
  (p.ej. pipeado a un log); en ese caso curl cae a no mostrar nada, lo
  cual es aceptable (no rompe el script).
- Alternativa más controlada y consistente entre curl/PowerShell: parsear
  `curl -w` o usar `curl --progress-bar` tal cual (recomendado, menos
  código que mantener, no hay que reinventar el parser de progreso).

**Decisión**: usar `curl -fL --progress-bar` (opción simple, sin
dependencias nuevas, evita reinventar un parser de porcentaje).

**Ejemplo real de salida** (`curl --progress-bar`, terminal ~80 columnas):

```
Downloading Previo (v0.9.8)...
######################################################          82.4%
```

Progresión en el tiempo (misma línea, se sobreescribe con `\r`):

```
Downloading Previo (v0.9.8)...
#                                                                 1.2%
########                                                         12.8%
###############################                                 48.3%
############################################################   100.0%
```

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
    Write-Host -NoNewline ("`r[{0}] {1,3}% {2} {3}  " -f $bar, $pct, $sizeInfo, $speedInfo)
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
  `cmd.exe` clásico y consolas remotas a veces los rompen).
- Incluye tamaño (`MB/MB`) y velocidad instantánea (`MB/s`), calculada
  con `Stopwatch` sobre el total acumulado — más útil que un `%` pelado
  para saber si la descarga está viva o colgada.
- Si `Content-Length` no viene (`$totalBytes` es `-1`/`$null`), la barra
  queda vacía (sin `=`/`>`) y solo se actualizan tamaño descargado y
  velocidad (no debería ocurrir con GitHub releases, pero cubre el caso
  sin dejar una barra de progreso mintiendo un `%` inventado).
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
repintado in-place con `\r`, no son líneas nuevas):

```
Downloading Previo (v0.9.8)...
[                                        ]   0% 0.0/9.4 MB  0.0 MB/s
```

Progresión (misma línea, la punta `>` avanza y la velocidad se
actualiza en vivo — mismo lenguaje visual que `cargo build`/`gh`):

```
[===>                                    ]  12% 1.1/9.4 MB  3.2 MB/s
[================>                       ]  42% 4.0/9.4 MB  4.8 MB/s
[===============================>        ]  78% 7.3/9.4 MB  5.1 MB/s
[========================================] 100% 9.4/9.4 MB  5.0 MB/s
```

Al llegar a 100%, la punta `>` desaparece (barra llena de `=`) y
`Write-Host ""` cierra la línea con un salto — el prompt continúa
normal (equivalente al comportamiento de curl).

Caso sin `Content-Length` (fallback, barra vacía, solo bytes y
velocidad se mueven):

```
[                                        ]   0% 4.2 MB  4.6 MB/s
```

## Fuera de alcance

- No se toca la lógica de resolución de release/tag (`RELEASE_JSON`,
  `Invoke-RestMethod` para metadata), solo la descarga del tarball.
- No se añade barra de progreso a otras descargas del proyecto (no hay
  otras, confirmado por grep sobre `Invoke-WebRequest|DownloadFile|curl|wget`).

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
