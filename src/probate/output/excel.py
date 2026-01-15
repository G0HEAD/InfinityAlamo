from __future__ import annotations

from pathlib import Path

import pandas as pd

from probate.models import CaseResult


def write_excel(results: list[CaseResult], report_path: Path) -> Path:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for result in results:
        fields = result.extracted_fields
        rows.append(
            {
                "County": result.county,
                "CaseNumber": result.case_ref.case_number,
                "FilingDate": result.case_ref.filing_date,
                "DeceasedName": fields.deceased_name,
                "FilerName": fields.filer_name,
                "PropertyAddress": fields.property_address,
                "PdfPaths": " | ".join(result.pdf_paths),
                "SourceLinks": result.case_ref.detail_url,
                "ExtractionNotes": fields.notes,
            }
        )

    df = pd.DataFrame(rows)
    df.to_excel(report_path, index=False)
    return report_path
