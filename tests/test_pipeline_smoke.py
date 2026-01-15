from __future__ import annotations

from pathlib import Path

from probate.config import load_config
from probate.pipeline import run_pipeline


def test_pipeline_smoke(tmp_path: Path) -> None:
    config = load_config(Path("config/counties.yaml"))
    result = run_pipeline(config, "2026-01-15")
    assert result.summary is not None
