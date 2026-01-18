# Security & Privacy

## Data handling
- Runs locally; no data is uploaded by default.
- Outputs (reports, PDFs, logs) are written to the local `output/` and `data/` folders.
- The demo UI stores preferences in `.portal_demo_settings.json` (ignored by git).

## Sensitive inputs
- Do not paste secrets or credentials into the URL field.
- The UI masks query parameters in the display log to reduce exposure.

## Safe defaults
- `.env` and `.portal_demo_settings.json` are ignored by git.
- Logs contain only summary metadata and do not store raw PDF text.

## Recommendations
- Keep your repository private if it includes sensitive data.
- Regularly review `output/` and `data/` folders for sensitive files.
- Use OS‑level permissions to restrict access to the project directory.
