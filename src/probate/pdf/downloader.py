from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import hashlib
import requests


@dataclass(frozen=True)
class DownloadResult:
    path: Path
    skipped: bool


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def download_pdf(url: str, dest: Path, timeout: int = 30) -> DownloadResult:
    _ensure_dir(dest.parent)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    content = response.content

    if dest.exists() and _sha256(dest.read_bytes()) == _sha256(content):
        return DownloadResult(path=dest, skipped=True)

    dest.write_bytes(content)
    return DownloadResult(path=dest, skipped=False)
