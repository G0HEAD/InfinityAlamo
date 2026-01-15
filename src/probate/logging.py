from __future__ import annotations

import logging
from datetime import date
from pathlib import Path


def setup_logging(
    logs_dir: Path, target_date: date | None = None, name: str = "probate"
) -> logging.Logger:
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if target_date:
        log_file = logs_dir / f"{target_date.isoformat()}.log"
    else:
        log_file = logs_dir / "run.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)
    return logger
