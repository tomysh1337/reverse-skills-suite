param(
  [string]$Output = "",
  [switch]$Force
)

$ErrorActionPreference = 'Stop'
$project = (Resolve-Path "$PSScriptRoot\..").Path
$repo = (Resolve-Path "$project\..").Path
if ([string]::IsNullOrWhiteSpace($Output)) {
  $Output = Join-Path $repo 'dist\phantom-protector-v1.skill'
}

$staging = Join-Path ([System.IO.Path]::GetTempPath()) ("phantom-protector-skill-" + [guid]::NewGuid().ToString('N'))
try {
  New-Item -ItemType Directory -Force $staging | Out-Null
  $items = @('README.md', 'SKILL.md', 'pom.xml', 'scripts')
  foreach ($item in $items) {
    $source = Join-Path $project $item
    if (-not (Test-Path $source)) { throw "Missing required skill item: $item" }
    Copy-Item -LiteralPath $source -Destination (Join-Path $staging $item) -Recurse -Force
  }

  $parent = Split-Path -Parent $Output
  New-Item -ItemType Directory -Force $parent | Out-Null
  if ((Test-Path $Output) -and -not $Force) {
    throw "Output exists. Re-run with -Force: $Output"
  }
  if (Test-Path $Output) { Remove-Item -LiteralPath $Output -Force }
  Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $Output -CompressionLevel Optimal
  Write-Output "Created $Output"
} finally {
  if (Test-Path $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
}
