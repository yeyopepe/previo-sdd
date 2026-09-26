# Installs or updates Previo in the current project.
# Usage: irm https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.ps1 | iex
# Usage (specific version): $env:PREVIO_VERSION = "v1.2.3"; irm https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.ps1 | iex
param(
    [string]$Version = $env:PREVIO_VERSION
)
$ErrorActionPreference = "Stop"

$Repo = "yeyopepe/previo-sdd"

# Detect, before overwriting anything, whether this project already had the
# framework installed -- used at the end to show the right next-step message.
$WasAlreadyInstalled = Test-Path ".claude\skills\pv-init"

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
if (-not $Tag) {
    throw "Couldn't determine which version of Previo to install."
}
$Tarball = "https://github.com/$Repo/archive/refs/tags/$Tag.tar.gz"

$Tmp = Join-Path $env:TEMP "previo-install-$([guid]::NewGuid())"
New-Item -ItemType Directory -Path $Tmp -Force | Out-Null
try {
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

    tar -xzf $TarPath -C $Tmp --strip-components=1
    if ($LASTEXITCODE -ne 0) { throw "Failed to extract the downloaded package." }

    $SrcSkills = Join-Path $Tmp ".claude\skills"
    $DestSkills = ".claude\skills"
    New-Item -ItemType Directory -Path $DestSkills -Force | Out-Null

    # Syncs only the framework's own skills (pv- prefix), without touching the user's own skills.
    Get-ChildItem -Path $SrcSkills -Directory -Filter "pv-*" | ForEach-Object {
        $Dest = Join-Path $DestSkills $_.Name
        if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
        Copy-Item -Recurse -Path $_.FullName -Destination $Dest
        # Dev-only tooling (sandbox test files, their builder script) never ships to consuming projects.
        Get-ChildItem -Path $Dest -Recurse -File -Include "*.sandbox.*", "_build_sandbox.py" | Remove-Item -Force
    }

    if (Test-Path $DestSkills) {
        Get-ChildItem -Path $DestSkills -Directory -Filter "pv-*" | ForEach-Object {
            $SrcDir = Join-Path $SrcSkills $_.Name
            if (-not (Test-Path $SrcDir)) {
                Write-Host "Removing obsolete skill: $($_.Name)"
                Remove-Item -Recurse -Force $_.FullName
            }
        }
    }

    # Syncs the framework's documentation.
    $DestDocDir = Join-Path ".claude" "pv-doc"
    New-Item -ItemType Directory -Force -Path $DestDocDir | Out-Null
    foreach ($doc in @("pv-guide.en.md", "pv-guide.es.md")) {
        $DestDoc = Join-Path $DestDocDir $doc
        $SrcDoc = Join-Path $Tmp ".claude\pv-doc\$doc"
        if (Test-Path $SrcDoc) {
            Copy-Item -Path $SrcDoc -Destination $DestDoc -Force
        }
    }

    # Syncs the framework's changelog.
    $ChangelogMissing = $false
    foreach ($doc in @("pv-changelog.en.md", "pv-changelog.es.md")) {
        $SrcChangelog = Join-Path $Tmp ".claude\$doc"
        if (Test-Path $SrcChangelog) {
            Copy-Item -Path $SrcChangelog -Destination (Join-Path ".claude" $doc) -Force
        }
        else {
            $ChangelogMissing = $true
        }
    }

    # Syncs the pv.py launcher at the repo root (generated file, always overwritten).
    $SrcPvPy = Join-Path $SrcSkills "pv-init\assets\pv.py"
    if (Test-Path $SrcPvPy) {
        Copy-Item -Path $SrcPvPy -Destination "pv.py" -Force
    }

    Write-Host "Previo installed/updated in .claude/skills."
    Write-Host ""
    if ($ChangelogMissing) {
        Write-Host "==========================================================" -ForegroundColor Yellow
        Write-Host " Warning: the new version was installed, but something" -ForegroundColor Yellow
        Write-Host " went wrong and the changelog for this release is missing." -ForegroundColor Yellow
        Write-Host " You won't have information about what changed." -ForegroundColor Yellow
        Write-Host "==========================================================" -ForegroundColor Yellow
        Write-Host ""
    }
    if ($InstalledFromRawTag) {
        Write-Host "==========================================================" -ForegroundColor Yellow
        Write-Host " Warning: '$Tag' is not a published release, it was" -ForegroundColor Yellow
        Write-Host " installed as a raw git tag. It may be untested/unstable." -ForegroundColor Yellow
        Write-Host "==========================================================" -ForegroundColor Yellow
        Write-Host ""
    }
    if ($WasAlreadyInstalled) {
        Write-Host "=========================================================="
        Write-Host " You're updating from a previous version: run /pv-update"
        Write-Host " in your agent to check and repair the configuration."
        Write-Host "=========================================================="
    }
    else {
        Write-Host "=========================================================="
        Write-Host " First install: run /pv-init in your agent to set it up."
        Write-Host "=========================================================="
    }
}
finally {
    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
