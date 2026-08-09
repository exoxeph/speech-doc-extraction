import asyncio
from pathlib import Path

from app.adapters.ocr.mock import MockOCRAdapter


FIXTURE_DIR = Path("testdata/mock_responses/ocr")


def test_mock_ocr_adapter_returns_recorded_lines() -> None:
    adapter = MockOCRAdapter(FIXTURE_DIR)

    result = asyncio.run(adapter.extract_text(b"normal_report"))

    assert result.provider == "mock"
    assert result.lines[0] == "ABC Diagnostic Centre"
    assert result.lines[-1] == "Hemoglobin    12.5    gm/dl    13.0 - 17.0    L"


def test_mock_ocr_adapter_preserves_whitespace_in_result_lines() -> None:
    adapter = MockOCRAdapter(FIXTURE_DIR)

    result = asyncio.run(adapter.extract_text(b"difficult_report"))

    assert "AGE 34      SEX Female" in result.lines
    assert "WBC Count     12,500     10^3/uL     4,000 - 11,000     H" in result.lines


def test_mock_ocr_adapter_defaults_to_normal_report_for_empty_document_marker() -> None:
    adapter = MockOCRAdapter(FIXTURE_DIR)

    result = asyncio.run(adapter.extract_text(b""))

    assert result.lines[1] == "Patient Name: John Doe"
