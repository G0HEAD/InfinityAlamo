from __future__ import annotations

from pathlib import Path

import pdfplumber

from probate.pdf.ocr import extract_text_from_pdf


def extract_text(pdf_path: Path) -> str:
    text_chunks: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    text = "\n".join(text_chunks).strip()
    if not text:
        return extract_text_from_pdf(pdf_path)
    return text
