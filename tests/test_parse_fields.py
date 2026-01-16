from pathlib import Path

from probate.pdf.parse_fields import parse_fields


def test_parse_fields_primary_labels():
    text = (
        "Case Number: DEMO-2026-0001\n"
        "Filing Date: 2026-01-15\n"
        "Deceased: John Q. Doe\n"
        "Petitioner: Jane Executor\n"
        "Property Address: 123 Main St, Austin, TX 78701\n"
    )
    fields = parse_fields(text)
    assert fields.case_number == "DEMO-2026-0001"
    assert fields.filing_date == "2026-01-15"
    assert fields.deceased_name == "John Q. Doe"
    assert fields.filer_name == "Jane Executor"
    assert fields.property_address == "123 Main St, Austin, TX 78701"


def test_parse_fields_alternate_labels():
    text = (
        "Case No. ABC-123\n"
        "Filed: 2025-12-01\n"
        "Decedent: Alice Example\n"
        "Executor: Bob Example\n"
        "Address: 55 Pine Rd, Dallas, TX 75001\n"
    )
    fields = parse_fields(text)
    assert fields.case_number == "ABC-123"
    assert fields.filing_date == "2025-12-01"
    assert fields.deceased_name == "Alice Example"
    assert fields.filer_name == "Bob Example"
    assert fields.property_address == "55 Pine Rd, Dallas, TX 75001"


# ===== EDGE CASE TESTS =====


def test_parse_fields_names_with_apostrophes_and_hyphens():
    r"""
    Edge Case: Names with apostrophes, hyphens, and suffixes.

    Current regex [A-Za-z\.\s]+ will FAIL to capture these properly.
    Expected behavior: Should capture full names including special characters.
    """
    text = (
        "Case Number: TEST-001\n"
        "Filing Date: 2026-01-15\n"
        "Deceased: Patrick O'Brien Jr.\n"
        "Petitioner: Mary-Jane Smith-Jones\n"
        "Property Address: 123 Main St, Austin, TX 78701\n"
    )
    fields = parse_fields(text)

    # Current implementation will truncate at apostrophe/hyphen
    # These assertions document the CURRENT BROKEN behavior
    # After regex improvements, update these to expect full names
    assert fields.deceased_name == "Patrick O"  # BROKEN: should be "Patrick O'Brien Jr."
    assert fields.filer_name == "Mary"  # BROKEN: should be "Mary-Jane Smith-Jones"

    # These should work fine
    assert fields.case_number == "TEST-001"
    assert fields.property_address == "123 Main St, Austin, TX 78701"


def test_parse_fields_case_number_lowercase():
    r"""
    Edge Case: Case numbers with lowercase letters.

    Current regex [A-Z0-9\-]+ requires uppercase only.
    Many real-world systems use mixed case or lowercase identifiers.
    """
    text = (
        "Case Number: demo-2026-0001\n"
        "Filing Date: 2026-01-15\n"
        "Deceased: Test Person\n"
    )
    fields = parse_fields(text)

    # Lowercase should still match due to re.IGNORECASE
    assert fields.case_number == "demo-2026-0001"
    assert "case_number: matched" in fields.notes


def test_parse_fields_missing_all_fields():
    """
    Edge Case: Text with no recognizable field labels.

    Should gracefully handle missing data without errors.
    All fields should be None, notes should track all "no match" results.
    """
    text = "This is some random text with no probate fields at all."

    fields = parse_fields(text)

    # All fields should be None
    assert fields.case_number is None
    assert fields.filing_date is None
    assert fields.deceased_name is None
    assert fields.filer_name is None
    assert fields.property_address is None

    # Notes should indicate all fields had no match
    assert "case_number: no match" in fields.notes
    assert "filing_date: no match" in fields.notes
    assert "deceased_name: no match" in fields.notes
    assert "filer_name: no match" in fields.notes
    assert "property_address: no match" in fields.notes


def test_parse_fields_extra_whitespace():
    """
    Edge Case: Extra whitespace around field values.

    The _clean() helper should strip leading/trailing whitespace.
    Internal multiple spaces should be preserved (part of the name).
    """
    text = (
        "Case Number:    SPACE-001    \n"
        "Filing Date:   2026-01-15   \n"
        "Deceased:    John   Q.   Doe    \n"  # Multiple internal spaces
        "Petitioner:   Jane Executor   \n"
        "Property Address:    123 Main St    \n"
    )
    fields = parse_fields(text)

    # Leading/trailing spaces should be cleaned
    assert fields.case_number == "SPACE-001"
    assert fields.filing_date == "2026-01-15"
    assert fields.filer_name == "Jane Executor"
    assert fields.property_address == "123 Main St"

    # Internal multiple spaces should be preserved
    assert fields.deceased_name == "John   Q.   Doe"


def test_parse_fields_names_with_suffixes():
    r"""
    Edge Case: Names with generational suffixes (Jr., Sr., III, IV).

    Current regex [A-Za-z\.\s]+ should handle these since they use dots and letters.
    But special handling may be needed for Roman numerals without dots.
    """
    text = (
        "Deceased: Robert James Smith III\n"
        "Petitioner: William Brown Sr.\n"
    )
    fields = parse_fields(text)

    # These should work with current regex (dots and letters only)
    assert fields.deceased_name == "Robert James Smith III"
    assert fields.filer_name == "William Brown Sr."


def test_parse_fields_address_with_special_characters():
    """
    Edge Case: Addresses with apartment numbers, special characters (#, &, etc.).

    Current regex [^\n]+ captures everything until newline, so should work.
    This test verifies that special characters are preserved.
    """
    text = (
        "Property Address: 123 Main St, Apt #456, Austin, TX 78701\n"
        "Case Number: TEST-002\n"
    )
    fields = parse_fields(text)

    # Should capture full address including # symbol
    assert fields.property_address == "123 Main St, Apt #456, Austin, TX 78701"
    assert fields.case_number == "TEST-002"


def test_parse_fields_partial_match_scenario():
    """
    Edge Case: Only some fields are present in the text.

    Should extract available fields and return None for missing ones.
    """
    text = (
        "Case Number: PARTIAL-123\n"
        "Deceased: Jane Doe\n"
        # Missing: filing_date, filer_name, property_address
    )
    fields = parse_fields(text)

    # Present fields should be extracted
    assert fields.case_number == "PARTIAL-123"
    assert fields.deceased_name == "Jane Doe"

    # Missing fields should be None
    assert fields.filing_date is None
    assert fields.filer_name is None
    assert fields.property_address is None

    # Notes should track matches and non-matches
    assert "case_number: matched" in fields.notes
    assert "deceased_name: matched" in fields.notes
    assert "filing_date: no match" in fields.notes


def test_parse_fields_fixture_text():
    fixture_path = (
        Path(__file__).parent / "fixtures" / "sample_case_text.txt"
    )
    text = fixture_path.read_text(encoding="utf-8")
    fields = parse_fields(text)
    assert fields.case_number == "SAMPLE-2026-0099"
    assert fields.filing_date == "2026-01-20"
    assert fields.deceased_name == "Maria D. Example"
    assert fields.filer_name == "Luis Executor"
    assert fields.property_address == "987 Elm St, Houston, TX 77002"
