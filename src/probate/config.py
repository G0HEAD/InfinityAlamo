from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class RunConfig:
    timezone: str = "America/Chicago"
    default_mode: str = "yesterday"
    rate_limit_seconds: float = 1.0
    retries: int = 3


@dataclass
class OutputConfig:
    pdf_dir: str = "data/pdfs"
    report_dir: str = "output/reports"
    logs_dir: str = "output/logs"


@dataclass
class CountyConfig:
    name: str
    enabled: bool
    connector: str
    portal_url: str
    mode: str = "requests"
    auth: Dict[str, Any] | None = None


@dataclass
class AppConfig:
    run: RunConfig
    output: OutputConfig
    counties: List[CountyConfig]


def load_config(path: str | Path) -> AppConfig:
    data = _read_yaml(path)
    run = RunConfig(**data.get("run", {}))
    output = OutputConfig(**data.get("output", {}))
    counties = [CountyConfig(**c) for c in data.get("counties", [])]
    return AppConfig(run=run, output=output, counties=counties)


def _read_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
