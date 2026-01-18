# Client Readiness Checklist

## Environment
- [ ] Python 3.11+ installed
- [ ] `pip install -e .[dev]` completed without errors
- [ ] Tesseract installed and on PATH (OCR)

## Demo
- [ ] Portal Scraper Demo UI launches
- [ ] Demo run produces Excel report
- [ ] Logs created in `output/logs/`

## Scheduling
- [ ] Task Scheduler/cron configured
- [ ] Task verified with a manual run
- [ ] User understands notifications (Windows pop-up only when logged in)

## Data Handling
- [ ] Client understands that outputs are stored locally
- [ ] Sensitive data stored in secured folders
- [ ] `.env` and `.portal_demo_settings.json` are not committed

## Support
- [ ] Setup guide provided
- [ ] Troubleshooting steps reviewed
