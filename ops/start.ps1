param([Parameter(Mandatory=$true)][double]$Hours, [int]$Slots = 1, [string]$Python = "python")
$ErrorActionPreference = "Stop"
$taskRoot = Split-Path $PSScriptRoot
$taskRuntime = Join-Path $PSScriptRoot "runtime"
New-Item -ItemType Directory -Force -Path $taskRuntime | Out-Null
$pythonExe = (Get-Command $Python).Source
Start-Process -FilePath $pythonExe -ArgumentList @("-m", "ops.supervisor", "run", "--hours", $Hours, "--slots", $Slots) -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskRuntime "supervisor.log") -RedirectStandardError (Join-Path $taskRuntime "supervisor.err") -PassThru | Select-Object Id
