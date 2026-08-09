import pytest

from app.services.models import (
    DocumentExtractionResult,
    LabReportMeta,
    LabResult,
    LabValue,
)


def test_document_extraction_result_holds_required_lab_fields() -> None:
    raw_line = "Hemoglobin    12.5    gm/dl    13.0 - 17.0    L"
    result = LabResult(
        test_name="Hemoglobin",
        value=LabValue(numeric=12.5),
        unit="g/dL",
        reference_range="13.0 - 17.0",
        flag="L",
        raw_line=raw_line,
    )

    extraction = DocumentExtractionResult(
        document_type="lab_report",
        meta=LabReportMeta(
            patient_name="John Doe",
            age="28",
            sex="Male",
            report_date="2026-08-07",
            lab_name="ABC Diagnostic Centre",
            reference_no="R12345",
        ),
        results=[result],
        provider="mock",
    )

    assert extraction.results[0].test_name == "Hemoglobin"
    assert extraction.results[0].value.numeric == 12.5
    assert extraction.results[0].raw_line == raw_line


def test_lab_result_cannot_omit_required_fields() -> None:
    with pytest.raises(TypeError):
        LabResult(test_name="Hemoglobin")
