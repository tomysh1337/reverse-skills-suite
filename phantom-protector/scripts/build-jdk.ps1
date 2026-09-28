param(
  [string]$AsmRoot = "$PSScriptRoot\..\..\.reverse-tools\dex2jar\dex-tools-v2.4\lib",
  [string]$JavaHome = "C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot"
)
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path "$PSScriptRoot\..").Path
$out = Join-Path $project 'target/classes'
New-Item -ItemType Directory -Force $out | Out-Null
$cp = @("$AsmRoot\asm-9.5.jar", "$AsmRoot\asm-commons-9.5.jar", "$AsmRoot\asm-tree-9.5.jar", "$AsmRoot\asm-analysis-9.5.jar", "$AsmRoot\asm-util-9.5.jar") -join ';'
$sources = (Get-ChildItem "$project\src\main\java" -Recurse -Filter '*.java').FullName
& "$JavaHome\bin\javac.exe" -cp $cp -d $out $sources
Write-Output "Compiled phantom-protector main sources to $out"
