$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptRoot)
Set-Location $projectRoot

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  throw "Python venv not found: $python"
}

& $python -m pip install pyinstaller

& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --name survey_dashboard_modern `
  --distpath "arts\dists" `
  --workpath "arts\builds" `
  --specpath "tls\builds" `
  --add-data "uis;uis" `
  --add-data "dats;dats" `
  --add-data "outs;outs" `
  pkgs\surveys\clis\dashboard.py

Write-Host ""
Write-Host "Build complete:" -ForegroundColor Green
Write-Host (Join-Path $projectRoot "arts\dists\survey_dashboard_modern.exe")
