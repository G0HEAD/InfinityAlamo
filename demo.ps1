param(
  [string]$Date = "2026-01-15"
)

Write-Host "Running InfinityAlamo demo for date: $Date"
python -m probate --date $Date

Write-Host ""
Write-Host "Demo complete. Outputs:"
Write-Host "  PDFs:   data/pdfs/DemoCounty/$Date/"
Write-Host "  Report: output/reports/Daily_Probate_Leads_$Date.xlsx"
