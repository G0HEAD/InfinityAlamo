from __future__ import annotations

from probate.config import CountyConfig
from probate.connectors.base import BaseConnector
from probate.models import CaseDetails, CaseRef, PdfLink


class Connector(BaseConnector):
    def __init__(self, config: CountyConfig) -> None:
        self.config = config

    def validate_config(self) -> None:
        if not self.config.portal_url:
            raise ValueError("portal_url is required")

    def fetch_case_index(self, run_date: str):
        return []

    def fetch_case_details(self, case_ref: CaseRef) -> CaseDetails:
        return CaseDetails(case_ref=case_ref, metadata={})

    def get_pdf_links(self, case_details: CaseDetails):
        return []
