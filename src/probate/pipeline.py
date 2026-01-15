from __future__ import annotations

from dataclasses import dataclass
import logging

from probate.config import AppConfig
from probate.connectors.loader import load_connectors
from probate.logging import RunSummary

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    summary: RunSummary


def run_pipeline(config: AppConfig, run_date: str) -> PipelineResult:
    logger.info("Starting pipeline for %s", run_date)
    summary = RunSummary()
    connectors = load_connectors(config.counties)
    logger.info("Loaded %s connectors", len(connectors))
    return PipelineResult(summary=summary)
