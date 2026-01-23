# Infinity Alamo

Automated Probate Lead Extractor — a Python pipeline that collects daily
probate filings, downloads PDFs, extracts fields with OCR fallback, and outputs
timestamped Excel lead reports.

## Quick start (no prior experience needed)
Choose one path:

### A) Windows installer (recommended for clients)
1. Download the latest `InfinityAlamoDemo-Setup.exe` from the GitHub Releases.
2. Run the installer → it creates a desktop shortcut.
3. Launch **InfinityAlamoDemo** from the desktop.

### B) Run from source
1. Create and activate your environment.
2. Install dependencies:
   - `pip install -e .[dev]`
3. Run the demo pipeline (CLI):
   - `python -m probate --yesterday`
   - `.\demo.ps1` (Windows one-command demo)
   - `./demo.sh` (macOS/Linux one-command demo)

## Portal Scraper Demo (UI)
Use the lightweight desktop UI to run the probate pipeline and review results:
- Windows (source): double-click `launch_portal_tester.bat` or run `.\launch_portal_tester.ps1`
- macOS/Linux (source): `python tools/portal_scraper_demo.py`
- Windows (installer): launch **InfinityAlamoDemo** from the desktop

## Windows Installer (InfinityAlamoDemo)
Build a desktop installer with icon + shortcut:
- See `installer/README.md`

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
Use the **Schedule Help** button in the UI for a copy-paste command, or:

Windows Task Scheduler (manual):
1. Create a new Task.
2. Trigger: Daily at your preferred time.
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
- Logs are written to `output/logs/<YYYY-MM-DD>.log` (installer: `%LOCALAPPDATA%\\InfinityAlamoDemo\\output\\logs`).

## Adding a county
1. Create a new connector in `src/probate/connectors/<county>.py`.
2. Add a matching entry in `config/counties.yaml`.

## Security & Privacy
See `SECURITY.md` for data handling, safe defaults, and privacy guidance.

## Project Structure
```
InfinityAlamo/
  config/               # counties.yaml
  tools/                # portal_scraper_demo.py (UI)
  src/probate/          # pipeline + connectors + pdf + output
  tests/                # pytest suite
  output/               # reports + logs (generated)
  data/                 # downloaded PDFs (generated)
```

## Client Readiness
- `CLIENT_READINESS.md` — go/no-go checklist before client delivery.
- `SETUP_GUIDE.md` — step-by-step setup, scheduling, and troubleshooting.
- `KNOWN_LIMITATIONS.md` — items to disclose to clients.

## GitHub
- Repo: https://github.com/G0HEAD/InfinityAlamo
- Releases: download the latest Windows installer from the **Releases** page.
