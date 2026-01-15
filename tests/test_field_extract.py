from __future__ import annotations

from probate.pdf.field_extract import extract_fields


def test_extract_fields_basic() -> None:
    text = """
    Case Number: 12345
    Deceased Name: John Doe
    Applicant: Jane Doe
    Property Address: 100 Main St, Houston, TX
    """
    fields = extract_fields(text)
    assert fields.deceased_name == "John Doe"
    assert fields.filer_name == "Jane Doe"
    assert fields.property_address == "100 Main St, Houston, TX"
