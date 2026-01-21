from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List

from probate.config import AppConfig, load_config
from probate.connectors import get_connector
from probate.logging import setup_logging
from probate.models import CaseResult
from probate.output.excel import write_excel
from probate.pdf.download import checksum_path, download_pdf, sha256_file
from probate.pdf.extract_text import extract_text
from probate.pdf.parse_fields import parse_fields
from probate.storage import build_paths, case_pdf_dir


def run_from_config(config_path: str, target_date: date) -> List[CaseResult]:
    config = load_config(config_path)
    return run_pipeline(config, target_date)


def run_pipeline(config: AppConfig, target_date: date) -> List[CaseResult]:
    storage = build_paths(
        config.output.pdf_dir, config.output.report_dir, config.output.logs_dir
    )
    logger = setup_logging(storage.logs_dir, target_date=target_date)

    results: List[CaseResult] = []
    cases_found = 0
    pdfs_downloaded = 0
    ocr_used = 0
    error_count = 0

    for county in config.counties:
        if not county.enabled:
            continue
        connector = get_connector(county.connector, county)
        case_refs = connector.fetch_case_index(target_date)
        cases_found += len(case_refs)
        for case_ref in case_refs:
            errors = []
            pdf_paths: List[str] = []
            try:
                details = connector.fetch_case_details(case_ref)
                case_dir = case_pdf_dir(storage, county.name, target_date, case_ref.case_number)
                for link in details.pdf_links:
                    dest = case_dir / f"{link.label}.pdf"
                    checksum_file = checksum_path(dest)
                    if dest.exists() and dest.stat().st_size > 0:
                        if checksum_file.exists():
                            existing_checksum = checksum_file.read_text(
                                encoding="utf-8"
                            ).strip()
                            if existing_checksum and existing_checksum == sha256_file(dest):
                                pdf_paths.append(str(dest))
                                continue
                        else:
                            checksum_file.write_text(
                                sha256_file(dest), encoding="utf-8"
                            )
                            pdf_paths.append(str(dest))
                            continue
                    downloaded = download_pdf(link, dest)
                    pdf_paths.append(str(downloaded))
                    pdfs_downloaded += 1
                    checksum_file.write_text(sha256_file(downloaded), encoding="utf-8")

                extracted_text = ""
                used_ocr = False
                if pdf_paths:
                    extracted_text, used_ocr = extract_text(Path(pdf_paths[0]))
                if used_ocr:
                    ocr_used += 1

                fields = parse_fields(extracted_text)
                if used_ocr:
                    fields.notes = (fields.notes + "; used OCR").strip("; ")

                results.append(
                    CaseResult(
                        county=county.name,
                        case_ref=case_ref,
                        pdf_paths=pdf_paths,
                        extracted_fields=fields,
                        errors=errors,
                    )
                )
            except Exception as exc:
                logger.exception("Failed case %s", case_ref.case_number)
                errors.append(str(exc))
                error_count += 1
                results.append(
                    CaseResult(
                        county=county.name,
                        case_ref=case_ref,
                        pdf_paths=pdf_paths,
                        extracted_fields=parse_fields(""),
                        errors=errors,
                    )
                )

    report_path = Path(storage.report_dir) / f"Daily_Probate_Leads_{target_date.isoformat()}.xlsx"
    if results:
        write_excel(results, report_path)
    else:
        logger.info("No cases found; skipping report generation.")
    logger.info(
        "Run summary: cases_found=%s pdfs_downloaded=%s ocr_used=%s errors=%s",
        cases_found,
        pdfs_downloaded,
        ocr_used,
        error_count,
    )
    logger.info("Run complete: %s cases", len(results))
    return results
