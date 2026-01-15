from __future__ import annotations

from pathlib import Path
import hashlib
from urllib.parse import urlparse, unquote

import requests

from probate.models import PdfLink


def download_pdf(link: PdfLink, dest_path: Path) -> Path:
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if link.url.startswith("file://"):
        parsed = urlparse(link.url)
        path_str = unquote(parsed.path)
        if parsed.netloc:
            path_str = f"//{parsed.netloc}{path_str}"
        if path_str.startswith("/") and len(path_str) > 2 and path_str[2] == ":":
            path_str = path_str.lstrip("/")
        source = Path(path_str)
        dest_path.write_bytes(source.read_bytes())
        return dest_path

    response = requests.get(link.url, timeout=30)
    response.raise_for_status()
    dest_path.write_bytes(response.content)
    return dest_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".sha256")
