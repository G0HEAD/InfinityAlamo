# Outstanding Considerations

## Functional
- Real county connector is not implemented yet; demo uses `DemoCounty`.
- End‑to‑end run against a real portal requires URL + access details.

## Notifications
- Task Scheduler pop‑up (`msg *`) only works when the user is logged in.

## Data handling
- Output files contain potentially sensitive data and should be stored securely.
- The app does not encrypt output files by default.

## OCR
- Tesseract must be installed for OCR; otherwise OCR results are empty.

## Access policy
- Only use trusted portal URLs; the app will fetch any URL provided.
