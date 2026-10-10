$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $root
$venvPython = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating Python 3.12 virtual environment..."
    py -3.12 -m venv (Join-Path $root ".venv")
}

Write-Host "Installing/checking project dependencies..."
& $venvPython -m pip install -r (Join-Path $root "requirements.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$logPath = Join-Path $root "results\terminal_run.log"
Write-Host "Running Homework 6. Full terminal output: $logPath"
$ErrorActionPreference = "Continue"
& $venvPython (Join-Path $root "main.py") @args 2>&1 | Tee-Object -FilePath $logPath
exit $LASTEXITCODE
