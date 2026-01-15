from __future__ import annotations

import re

from probate.models import ExtractedFields


def parse_fields(text: str) -> ExtractedFields:
    notes = []

    case_number = _first_match(
        text,
        [
            r"Case Number:\s*([A-Z0-9\-]+)",
            r"Case No\.\s*([A-Z0-9\-]+)",
        ],
        notes,
        "case_number",
    )

    filing_date = _first_match(
        text,
        [
            r"Filing Date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
            r"Filed:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
        ],
        notes,
        "filing_date",
    )

    deceased_name = _first_match(
        text,
        [
            r"Deceased:\s*([A-Za-z\. ]+)",
            r"Decedent:\s*([A-Za-z\. ]+)",
        ],
        notes,
        "deceased_name",
    )

    filer_name = _first_match(
        text,
        [
            r"Petitioner:\s*([A-Za-z\. ]+)",
            r"Executor:\s*([A-Za-z\. ]+)",
        ],
        notes,
        "filer_name",
    )

    property_address = _first_match(
        text,
        [
            r"Property Address:\s*([^\n]+)",
            r"Address:\s*([^\n]+)",
        ],
        notes,
        "property_address",
    )

    return ExtractedFields(
        deceased_name=_clean(deceased_name),
        filer_name=_clean(filer_name),
        property_address=_clean(property_address),
        case_number=_clean(case_number),
        filing_date=_clean(filing_date),
        notes="; ".join(notes),
    )


def _first_match(text: str, patterns: list[str], notes: list[str], label: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            notes.append(f"{label}: matched {pattern}")
            return match.group(1).strip()
    notes.append(f"{label}: no match")
    return ""


def _clean(value: str) -> str | None:
    value = value.strip()
    return value or None
