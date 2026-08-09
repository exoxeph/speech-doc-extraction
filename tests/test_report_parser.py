from app.services.report_parser import parse_lab_result_row, parse_lab_result_rows


def test_parse_laboratory_result_row_preserves_raw_line_exactly() -> None:
    raw_line = "Hemoglobin    12.5    gm/dl    13.0 - 17.0    L"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "Hemoglobin"
    assert result.value.numeric == 12.5
    assert result.value.operator is None
    assert result.unit == "g/dL"
    assert result.reference_range == "13.0 - 17.0"
    assert result.flag == "L"
    assert result.raw_line == raw_line


def test_parse_laboratory_result_row_handles_qualified_value() -> None:
    raw_line = "CRP     <0.5     mg/dL     0.0 - 1.0"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "CRP"
    assert result.value.numeric == 0.5
    assert result.value.operator == "<"
    assert result.unit == "mg/dL"
    assert result.reference_range == "0.0 - 1.0"
    assert result.flag == ""
    assert result.raw_line == raw_line


def test_parse_laboratory_result_row_handles_comma_value_and_flag() -> None:
    raw_line = "WBC Count     12,500     10^3/uL     4,000 - 11,000     H"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "WBC Count"
    assert result.value.numeric == 12500.0
    assert result.unit == "10^3/uL"
    assert result.reference_range == "4,000 - 11,000"
    assert result.flag == "H"
    assert result.raw_line == raw_line


def test_parse_laboratory_result_row_rejects_uncertain_numeric_value() -> None:
    raw_line = "Hemoqlobin     ??13.?     mg??     13.0 - 17.0"

    assert parse_lab_result_row(raw_line) is None


def test_parse_laboratory_result_rows_skips_non_result_lines() -> None:
    lines = [
        "Patient Name: John Doe",
        "Hemoglobin    12.5    gm/dl    13.0 - 17.0    L",
    ]

    results = parse_lab_result_rows(lines)

    assert len(results) == 1
    assert results[0].test_name == "Hemoglobin"
