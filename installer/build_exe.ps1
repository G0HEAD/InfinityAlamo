param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "Building InfinityAlamoDemo executable..." -ForegroundColor Cyan

& $PythonExe -m PyInstaller `
  --name "InfinityAlamoDemo" `
  --windowed `
  --icon "assets\\infinity_alamo_demo.ico" `
  --noconfirm `
  --clean `
  --hidden-import "probate.connectors.demo_county" `
  --hidden-import "probate.connectors.democounty2" `
  --add-data "config;config" `
  --add-data "tools;tools" `
  --add-data "src;src" `
  "tools\\portal_scraper_demo.py"

Write-Host "Build complete. Output: dist\\InfinityAlamoDemo\\InfinityAlamoDemo.exe" -ForegroundColor Green
