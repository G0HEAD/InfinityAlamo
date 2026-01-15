from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List

from probate.config import CountyConfig
from probate.connectors.base import BaseConnector
from probate.models import CaseDetails, CaseRef, PdfLink


class DemoCountyConnector(BaseConnector):
    def __init__(self, config: CountyConfig) -> None:
        super().__init__(config)
        self.fixture_path = (
            Path(__file__).resolve().parent.parent / "fixtures" / "demo_case.pdf"
        )

    def fetch_case_index(self, target_date: date) -> List[CaseRef]:
        return [
            CaseRef(
                case_number="DEMO-2026-0001",
                filing_date=target_date,
                detail_url="https://example.com/case/DEMO-2026-0001",
            )
        ]

    def fetch_case_details(self, case_ref: CaseRef) -> CaseDetails:
        pdf_links = [
            PdfLink(url=self.fixture_path.as_uri(), label="demo_case"),
        ]
        return CaseDetails(case_ref=case_ref, pdf_links=pdf_links)


Connector = DemoCountyConnector
