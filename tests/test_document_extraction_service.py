import asyncio
from pathlib import Path

from app.adapters.ocr.mock import MockOCRAdapter
from app.services.document_extraction import DocumentExtractionService


FIXTURE_DIR = Path("testdata/mock_responses/ocr")


def test_document_extraction_service_composes_ocr_metadata_and_results() -> None:
    service = DocumentExtractionService(MockOCRAdapter(FIXTURE_DIR))

    extraction = asyncio.run(service.extract(b"normal_report"))

    assert extraction.document_type == "lab_report"
    assert extraction.provider == "mock"
    assert extraction.meta.patient_name == "John Doe"
    assert extraction.meta.report_date == "2026-08-07"
    assert len(extraction.results) == 1
    assert extraction.results[0].test_name == "Hemoglobin"
    assert extraction.results[0].raw_line == "Hemoglobin    12.5    gm/dl    13.0 - 17.0    L"


def test_document_extraction_service_normalizes_unambiguous_metadata_date() -> None:
    service = DocumentExtractionService(MockOCRAdapter(FIXTURE_DIR))

    extraction = asyncio.run(service.extract(b"difficult_report"))

    assert extraction.meta.patient_name == "Jane Smith"
    assert extraction.meta.report_date == "2026-08-08"
    assert [result.test_name for result in extraction.results] == ["WBC Count", "CRP"]
    assert extraction.results[0].value.numeric == 12500.0


def test_document_extraction_service_returns_unknown_for_non_lab_document() -> None:
    service = DocumentExtractionService(MockOCRAdapter(FIXTURE_DIR))

    extraction = asyncio.run(service.extract(b"not_lab_report"))

    assert extraction.document_type == "unknown"
    assert extraction.meta.patient_name is None
    assert extraction.results == []
