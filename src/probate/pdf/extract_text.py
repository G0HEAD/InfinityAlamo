from __future__ import annotations

from pathlib import Path

import pdfplumber

from probate.pdf.ocr import ocr_text


def extract_text(pdf_path: Path) -> tuple[str, bool]:
    text = ""
    used_ocr = False

    if pdf_path.suffix.lower() == ".txt":
        return pdf_path.read_text(encoding="utf-8"), False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception:
        text = _read_text_fallback(pdf_path)

    if not text.strip():
        text = ocr_text(pdf_path)
        used_ocr = bool(text.strip())

    return text, used_ocr


def _read_text_fallback(pdf_path: Path) -> str:
    try:
        return pdf_path.read_text(encoding="utf-8")
    except Exception:
        return ""
