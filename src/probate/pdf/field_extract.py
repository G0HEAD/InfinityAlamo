from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedFields:
    deceased_name: str | None = None
    filer_name: str | None = None
    property_address: str | None = None
    notes: str | None = None


def _match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group("value").strip()
    return None


def extract_fields(text: str) -> ExtractedFields:
    deceased_patterns = [
        r"Deceased\s*Name\s*:\s*(?P<value>.+)",
        r"Estate\s*of\s*(?P<value>[A-Za-z ,.'-]+)",
    ]
    filer_patterns = [
        r"Applicant\s*:\s*(?P<value>.+)",
        r"Administrator\s*:\s*(?P<value>.+)",
    ]
    address_patterns = [
        r"Property\s*Address\s*:\s*(?P<value>.+)",
        r"Address\s*:\s*(?P<value>\d+\s+[^\n]+)",
    ]

    return ExtractedFields(
        deceased_name=_match(deceased_patterns, text),
        filer_name=_match(filer_patterns, text),
        property_address=_match(address_patterns, text),
    )
