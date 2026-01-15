from __future__ import annotations

from pathlib import Path

import pdfplumber
import pytesseract

from probate.pdf.ocr import extract_text_from_pdf


def test_extract_text_from_pdf_uses_tesseract(tmp_path: Path, monkeypatch) -> None:
    def fake_open(path: Path):
        class FakePage:
            def to_image(self, resolution: int = 300):
                class FakeImage:
                    original = "image"

                return FakeImage()

        class FakePdf:
            pages = [FakePage()]

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        return FakePdf()

    monkeypatch.setattr(pdfplumber, "open", fake_open)
    monkeypatch.setattr(pytesseract, "image_to_string", lambda img: "OCR TEXT")

    text = extract_text_from_pdf(tmp_path / "sample.pdf")
    assert text == "OCR TEXT"
