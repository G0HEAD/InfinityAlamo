from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class StoragePaths:
    pdf_dir: Path
    report_dir: Path
    logs_dir: Path


def build_paths(base_pdf: str, base_report: str, base_logs: str) -> StoragePaths:
    return StoragePaths(
        pdf_dir=Path(base_pdf),
        report_dir=Path(base_report),
        logs_dir=Path(base_logs),
    )


def case_pdf_dir(
    storage: StoragePaths, county: str, target_date: date, case_number: str
) -> Path:
    safe_case = case_number.replace("/", "_")
    return storage.pdf_dir / county / target_date.isoformat() / safe_case
