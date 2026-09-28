param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path "$PSScriptRoot\..").Path
& "$PSScriptRoot\build-jdk.ps1"
$asm = Resolve-Path "$PSScriptRoot\..\..\.reverse-tools\dex2jar\dex-tools-v2.4\lib\asm-9.5.jar"
$commons = Resolve-Path "$PSScriptRoot\..\..\.reverse-tools\dex2jar\dex-tools-v2.4\lib\asm-commons-9.5.jar"
$tree = Resolve-Path "$PSScriptRoot\..\..\.reverse-tools\dex2jar\dex-tools-v2.4\lib\asm-tree-9.5.jar"
$analysis = Resolve-Path "$PSScriptRoot\..\..\.reverse-tools\dex2jar\dex-tools-v2.4\lib\asm-analysis-9.5.jar"
$util = Resolve-Path "$PSScriptRoot\..\..\.reverse-tools\dex2jar\dex-tools-v2.4\lib\asm-util-9.5.jar"
$cp = "$project\target/classes;$asm;$commons;$tree;$analysis;$util"
& 'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot\bin\java.exe' -cp $cp dev.reverse.phantom.cli.Main @Arguments
