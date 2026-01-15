from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CaseRef:
    case_number: str
    filing_date: str
    detail_url: str


@dataclass(frozen=True)
class CaseDetails:
    case_ref: CaseRef
    metadata: dict[str, Any]


@dataclass(frozen=True)
class PdfLink:
    url: str
    label: str | None = None
