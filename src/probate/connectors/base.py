from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from probate.config import CountyConfig
from probate.models import CaseDetails, CaseRef


class BaseConnector(ABC):
    def __init__(self, config: CountyConfig) -> None:
        self.config = config

    @abstractmethod
    def fetch_case_index(self, target_date: date) -> List[CaseRef]:
        raise NotImplementedError

    @abstractmethod
    def fetch_case_details(self, case_ref: CaseRef) -> CaseDetails:
        raise NotImplementedError
