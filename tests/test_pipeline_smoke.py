from datetime import date
from pathlib import Path

from probate.pipeline import run_from_config


def test_pipeline_smoke(tmp_path: Path):
    config_path = tmp_path / "counties.yaml"
    config_path.write_text(
        "\n".join(
            [
                "run:",
                '  timezone: "America/Chicago"',
                '  default_mode: "yesterday"',
                "output:",
                f'  pdf_dir: "{(tmp_path / "pdfs").as_posix()}"',
                f'  report_dir: "{(tmp_path / "reports").as_posix()}"',
                f'  logs_dir: "{(tmp_path / "logs").as_posix()}"',
                "counties:",
                "  - name: \"DemoCounty\"",
                "    enabled: true",
                "    connector: \"demo_county\"",
                "    portal_url: \"https://example.com/probate\"",
                "    mode: \"requests\"",
                "    auth:",
                "      type: \"none\"",
            ]
        ),
        encoding="utf-8",
    )

    results = run_from_config(str(config_path), date(2026, 1, 15))
    assert results

    report = tmp_path / "reports" / "Daily_Probate_Leads_2026-01-15.xlsx"
    assert report.exists()

    pdf_dir = tmp_path / "pdfs" / "DemoCounty" / "2026-01-15"
    assert pdf_dir.exists()

    checksum_files = list(pdf_dir.rglob("*.sha256"))
    assert checksum_files
