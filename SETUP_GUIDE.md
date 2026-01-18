# Setup Guide

## 1) Install Python
- Install Python 3.11+ from https://www.python.org/downloads/
- Ensure "Add Python to PATH" is checked during install.

## 2) Install dependencies
From the repo root:
```
pip install -e .[dev]
```

## 3) Run the demo
```
python -m probate --yesterday
```
Or use:
- `.\demo.ps1` (Windows)
- `./demo.sh` (macOS/Linux)

## 4) Launch the UI
```
python tools/portal_scraper_demo.py
```
Windows: double‑click `launch_portal_tester.bat`.

## 5) Schedule a daily run
Open the UI → Schedule Help → use “Create Task Now”.

## Troubleshooting
- **OCR empty:** Install Tesseract and restart terminal.
- **Missing reports:** If no cases found, report is intentionally skipped.
- **No notification:** Windows pop‑up works only when logged in.
