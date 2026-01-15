from __future__ import annotations

from pathlib import Path

import pdfplumber

from probate.pdf.text_extract import extract_text


def test_extract_text_returns_string(tmp_path: Path, monkeypatch) -> None:
    """Uses monkeypatched pdfplumber to avoid real PDF parsing."""
    def fake_open(path: Path):
        class FakePage:
            def extract_text(self):
                return "Hello"

        class FakePdf:
            pages = [FakePage()]

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        return FakePdf()

    monkeypatch.setattr(pdfplumber, "open", fake_open)
    text = extract_text(tmp_path / "sample.pdf")
    assert text == "Hello"
