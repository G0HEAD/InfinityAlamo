from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class CaseRef:
    case_number: str
    filing_date: date
    detail_url: str


@dataclass
class PdfLink:
    url: str
    label: str


@dataclass
class CaseDetails:
    case_ref: CaseRef
    pdf_links: List[PdfLink]


@dataclass
class ExtractedFields:
    deceased_name: Optional[str]
    filer_name: Optional[str]
    property_address: Optional[str]
    case_number: Optional[str]
    filing_date: Optional[str]
    notes: str = ""


@dataclass
class CaseResult:
    county: str
    case_ref: CaseRef
    pdf_paths: List[str]
    extracted_fields: ExtractedFields
    errors: List[str]
