from __future__ import annotations

from pathlib import Path


def ocr_text(pdf_path: Path) -> str:
    try:
        import pdfplumber  # type: ignore
        import pytesseract  # type: ignore
    except Exception:
        return ""

    text_chunks: list[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=200).original
                text_chunks.append(pytesseract.image_to_string(image))
    except Exception:
        return ""

    return "\n".join(chunk for chunk in text_chunks if chunk)
