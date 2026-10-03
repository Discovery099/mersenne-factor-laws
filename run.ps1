param([ValidateSet("all", "build", "test", "verify", "status", "demo")][string]$Action = "all")
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$taskPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path -LiteralPath $taskPython)) {
    $taskPython = (Get-Command python -ErrorAction Stop).Source
}
if ($Action -ne "status") {
    & $taskPython -m ops.build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($Action -in @("all", "test")) {
    & $taskPython -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($Action -in @("all", "verify")) { & $taskPython -m ops.verify }
if ($Action -eq "status") { & $taskPython -m ops.supervisor status }
if ($Action -eq "demo") { & $taskPython -m ops.validate --full }
exit $LASTEXITCODE
