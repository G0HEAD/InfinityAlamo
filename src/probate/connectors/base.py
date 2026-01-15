from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from probate.models import CaseDetails, CaseRef, PdfLink


class BaseConnector(ABC):
    """Base contract for county connectors."""

    @abstractmethod
    def validate_config(self) -> None:
        """Validate connector-specific configuration."""

    @abstractmethod
    def fetch_case_index(self, run_date: str) -> Iterable[CaseRef]:
        """Return case references for a given date."""

    @abstractmethod
    def fetch_case_details(self, case_ref: CaseRef) -> CaseDetails:
        """Return case details for a case reference."""

    @abstractmethod
    def get_pdf_links(self, case_details: CaseDetails) -> Iterable[PdfLink]:
        """Return PDF links for a case."""
