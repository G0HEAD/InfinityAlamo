# InfinityAlamo

Automated Probate Lead Extractor — a Python pipeline that collects daily
probate filings, downloads PDFs, extracts fields with OCR fallback, and outputs
timestamped Excel lead reports.

## Quick start
1. Create and activate your environment.
2. Install dependencies:
   - `pip install -e .[dev]`
3. Run the demo pipeline:
   - `python -m probate --yesterday`
   - `.\demo.ps1` (Windows one-command demo)
   - `./demo.sh` (macOS/Linux one-command demo)

## Configuration
Edit `config/counties.yaml` to add or enable counties. For each county, set:
- `connector` to a connector module name in `src/probate/connectors/`
- `portal_url`
- `mode` and `auth` settings

## Running
Examples:
- `python -m probate --yesterday`
- `python -m probate --today`
- `python -m probate --date 2026-01-15`

## Tests
- `pytest`

## OCR
OCR fallback uses `pytesseract` and renders PDF pages to images via
`pdfplumber`. Install Tesseract separately (system dependency) and ensure it is
on your PATH.

## Scheduling
Windows Task Scheduler:
1. Create a new Task.
2. Trigger: Daily at 9:00 PM.
3. Action: Start a program.
4. Program/script: your Python executable.
5. Arguments: `-m probate --yesterday`
6. Start in: the `InfinityAlamo` repo directory.

macOS/Linux (cron):
```
0 21 * * * /path/to/python -m probate --yesterday
```

## Troubleshooting
- If OCR returns empty results, confirm Tesseract is installed and on PATH.
- If PDFs fail to download, check portal availability and credentials.
- Logs are written to `output/logs/<YYYY-MM-DD>.log`.

## Adding a county
1. Create a new connector in `src/probate/connectors/<county>.py`.
2. Add a matching entry in `config/counties.yaml`.
