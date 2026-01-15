from __future__ import annotations

from pathlib import Path

from PIL import Image
import pdfplumber
import pytesseract


def extract_text_from_images(images: list[Image.Image]) -> str:
    chunks: list[str] = []
    for image in images:
        chunks.append(pytesseract.image_to_string(image))
    return "\n".join(chunks).strip()


def extract_text_from_pdf(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        images = [page.to_image(resolution=300).original for page in pdf.pages]
    return extract_text_from_images(images)
