$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
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
  --name survey_dashboard `
  --add-data "frontend;frontend" `
  --add-data "data;data" `
  --add-data "outputs;outputs" `
  dashboard_app.py

Write-Host ""
Write-Host "Build complete:" -ForegroundColor Green
Write-Host (Join-Path $projectRoot "dist\survey_dashboard.exe")
