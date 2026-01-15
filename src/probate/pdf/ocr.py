from __future__ import annotations

from pathlib import Path


def ocr_text(pdf_path: Path) -> str:
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
    except Exception:
        return ""

    try:
        image = Image.open(pdf_path)
    except Exception:
        return ""

    return pytesseract.image_to_string(image)
