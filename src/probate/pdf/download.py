from __future__ import annotations

from pathlib import Path
import hashlib
from urllib.parse import urlparse, unquote

import requests

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
except Exception:  # pragma: no cover - fallback when tenacity isn't installed
    def retry(*_args, **_kwargs):  # type: ignore
        def decorator(func):
            return func

        return decorator

    def stop_after_attempt(_attempts):  # type: ignore
        return None

    def wait_exponential(*_args, **_kwargs):  # type: ignore
        return None

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

    dest_path.write_bytes(_download_http(link.url))
    return dest_path


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
def _download_http(url: str) -> bytes:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".sha256")
