from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path


@dataclass(frozen=True)
class RunSummary:
    cases_found: int = 0
    pdfs_downloaded: int = 0
    errors: int = 0


def configure_logging(log_dir: str) -> Path:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    log_path = path / "run.log"

    handlers = [
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=handlers,
    )
    return log_path
