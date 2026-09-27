param(
    [string]$ToolsDir = "$PSScriptRoot\..\..\.reverse-tools"
)

$ErrorActionPreference = 'Stop'
$tools = [System.IO.Path]::GetFullPath($ToolsDir)
New-Item -ItemType Directory -Force -Path $tools | Out-Null
$log = Join-Path $tools 'install.log'
$manifestPath = Join-Path $tools 'install-manifest.json'
$manifest = @{}
if (Test-Path $manifestPath) {
    try { $manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json -AsHashtable } catch { $manifest = @{} }
}

function Download-File([string]$Name, [string]$Url, [string]$Destination) {
    $dest = Join-Path $tools $Destination
    $parent = Split-Path -Parent $dest
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    if (-not (Test-Path $dest)) {
        Invoke-WebRequest -Uri $Url -OutFile $dest -UseBasicParsing
    }
    $hash = (Get-FileHash -Algorithm SHA256 $dest).Hash.ToLowerInvariant()
    Add-Content -Path $log -Value ("{0}`t{1}`t{2}`t{3}`t{4}" -f (Get-Date -Format o), $Name, $Url, $dest, $hash)
    $manifest[$Name] = @{ source_url = $Url; version = 'pinned'; sha256 = $hash; path = $dest }
}

Download-File 'dex2jar' 'https://github.com/pxb1988/dex2jar/releases/download/v2.4/dex-tools-v2.4.zip' 'downloads/dex-tools-v2.4.zip'
if (-not (Test-Path (Join-Path $tools 'dex2jar'))) {
    Expand-Archive -Path (Join-Path $tools 'downloads/dex-tools-v2.4.zip') -DestinationPath (Join-Path $tools 'dex2jar')
}
Download-File 'vineflower' 'https://repo1.maven.org/maven2/org/vineflower/vineflower/1.11.2/vineflower-1.11.2.jar' 'vineflower.jar'
Download-File 'cfr' 'https://www.benf.org/other/cfr/cfr-0.152.jar' 'cfr.jar'
Download-File 'enigma' 'https://maven.fabricmc.net/cuchaz/enigma/2.5.1/enigma-2.5.1.jar' 'enigma.jar'
Download-File 'rizin' 'https://github.com/rizinorg/rizin/releases/download/v0.9.1/rizin-windows-static-v0.9.1.zip' 'downloads/rizin-windows-static-v0.9.1.zip'
if (-not (Test-Path (Join-Path $tools 'rizin'))) {
    Expand-Archive -Path (Join-Path $tools 'downloads/rizin-windows-static-v0.9.1.zip') -DestinationPath (Join-Path $tools 'rizin')
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python -and $python.Source -match 'WindowsApps') { $python = $null }
if (-not $python) {
    $pythonPath = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python" -Recurse -Filter python.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($pythonPath) { $python = Get-Command $pythonPath }
}
if ($python) {
    $fridaTarget = Join-Path $tools 'python'
    & $python.Source -m pip install --disable-pip-version-check --no-warn-script-location --target $fridaTarget frida-tools 2>&1 | Tee-Object -FilePath $log -Append
    $frida = Join-Path $fridaTarget 'Scripts/frida.exe'
    if (-not (Test-Path $frida)) { $frida = Join-Path $fridaTarget 'bin/frida.exe' }
    if (Test-Path $frida) {
        $manifest['frida'] = @{ source_url = 'https://pypi.org/project/frida-tools/'; version = 'pip-installed'; sha256 = (Get-FileHash -Algorithm SHA256 $frida).Hash.ToLowerInvariant(); path = $frida }
    }
}

$manifest | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $manifestPath
Write-Output (Get-Content -Raw $manifestPath)
