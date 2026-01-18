from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List

from probate.config import CountyConfig
from probate.connectors.base import BaseConnector
from probate.models import CaseDetails, CaseRef, PdfLink


class DemoCounty2Connector(BaseConnector):
    def __init__(self, config: CountyConfig) -> None:
        super().__init__(config)
        fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
        self.fixture_map = {
            f"DEMO2-2026-{i:04d}": fixtures_dir / f"democounty2_case_{i:02d}.pdf"
            for i in range(1, 11)
        }

    def fetch_case_index(self, target_date: date) -> List[CaseRef]:
        return [
            CaseRef(
                case_number=case_number,
                filing_date=target_date,
                detail_url=f"https://example.com/case/{case_number}",
            )
            for case_number in self.fixture_map.keys()
        ]

    def fetch_case_details(self, case_ref: CaseRef) -> CaseDetails:
        fixture_path = self.fixture_map.get(case_ref.case_number)
        if fixture_path is None:
            fixture_path = next(iter(self.fixture_map.values()))
        pdf_links = [
            PdfLink(url=fixture_path.as_uri(), label=case_ref.case_number),
        ]
        return CaseDetails(case_ref=case_ref, pdf_links=pdf_links)


Connector = DemoCounty2Connector
