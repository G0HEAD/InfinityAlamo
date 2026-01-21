param(
    [string]$IsccPath = "ISCC.exe"
)

$ErrorActionPreference = "Stop"

Write-Host "Building InfinityAlamoDemo installer..." -ForegroundColor Cyan

& $IsccPath ".\\installer\\InfinityAlamoDemo.iss"

Write-Host "Installer complete. Output: installer\\Output\\InfinityAlamoDemo-Setup.exe" -ForegroundColor Green
