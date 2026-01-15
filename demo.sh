#!/usr/bin/env bash
set -euo pipefail

DATE="${1:-2026-01-15}"
echo "Running InfinityAlamo demo for date: ${DATE}"
python -m probate --date "${DATE}"

echo ""
echo "Demo complete. Outputs:"
echo "  PDFs:   data/pdfs/DemoCounty/${DATE}/"
echo "  Report: output/reports/Daily_Probate_Leads_${DATE}.xlsx"
