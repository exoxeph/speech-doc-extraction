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


def test_parse_collapsed_row_with_inequality_reference_range() -> None:
    raw_line = "RP <8.5 mg/dL <1.0 N/A"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "RP"
    assert result.value.numeric == 8.5
    assert result.value.operator == "<"
    assert result.unit == "mg/dL"
    assert result.reference_range == "<1.0"
    assert result.flag == "N/A"


def test_parse_collapsed_row_with_range_value() -> None:
    raw_line = "Test Ratio 0.8 - 1.2 mmol/L N/A N/A"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "Test Ratio"
    assert result.value.kind == "range"
    assert result.value.numeric is None
    assert result.value.range is not None
    assert result.value.range.lower == 0.8
    assert result.value.range.upper == 1.2
    assert result.value.raw == "0.8 - 1.2"
    assert result.unit == "mmol/L"
    assert result.reference_range == "N/A"
    assert result.flag == "N/A"


def test_parse_pipe_separated_ocr_result_row_preserves_raw_line() -> None:
    raw_line = 'Creatinine [Mass/volume] in Serum or Plasma | 1.9 | mg/d | "/a'

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "Creatinine [Mass/volume] in Serum or Plasma"
    assert result.value.numeric == 1.9
    assert result.unit == "mg/dL"
    assert result.reference_range == "N/A"
    assert result.flag == ""
    assert result.raw_line == raw_line


def test_parse_pipe_separated_ocr_zero_confusion() -> None:
    raw_line = "Glucose [Mass/volume] in Urine by Test strip | Â©.9 | mg/dt | w/a"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.value.numeric == 0.9
    assert result.value.raw == "Â©.9"
    assert result.unit == "mg/dL"
    assert result.reference_range == "N/A"
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


def test_parse_multiline_observed_value_rows_preserves_ocr_lines() -> None:
    lines = [
        "01. Glucose [Mass/volume] in Serum or Plasma",
        "    Observed Value: 117.8 mg/dL    Reference Range: N/A",
        "02. Urea nitrogen [Mass/volume] in Serum or Plasma",
        "Observed Value: 16.2 mg/d Reference Range:",
    ]

    results = parse_lab_result_rows(lines)

    assert len(results) == 2
    assert results[0].test_name == "Glucose [Mass/volume] in Serum or Plasma"
    assert results[0].value.numeric == 117.8
    assert results[0].unit == "mg/dL"
    assert results[0].reference_range == "N/A"
    assert results[0].raw_line == "\n".join(lines[:2])
    assert results[1].test_name == "Urea nitrogen [Mass/volume] in Serum or Plasma"
    assert results[1].value.numeric == 16.2
    assert results[1].unit == "mg/dL"
    assert results[1].reference_range == ""
    assert results[1].raw_line == "\n".join(lines[2:])


def test_parse_multiline_observed_value_row_cleans_ocr_list_marker_noise() -> None:
    lines = [
        "0), Glucose [Mass/Vvo : anee)",
        "observed Value: 217.8 mg/dL Reference Range!",
        "%. Potassium [Moles/volume] in Serum or Plasma",
        "Observed Value: 4.@ mmol/L — Reference Range: N/A",
    ]

    results = parse_lab_result_rows(lines)

    assert len(results) == 2
    assert results[0].test_name == "Glucose [Mass/Vvo : anee)"
    assert results[1].test_name == "Potassium [Moles/volume] in Serum or Plasma"


def test_parse_multiline_observed_value_row_cleans_cropped_artifacts() -> None:
    lines = [
        "creatinine [Mass/volume] in Serum or Plasma : WA",
        "Observed Value: 2.0 mg/dl Reference Range:",
        "Sodium [Moles/volume] in Serum or Plasma",
        "Observed Value: 137.4 mmol/L —s- Reference Range: N/A",
    ]

    results = parse_lab_result_rows(lines)

    assert len(results) == 2
    assert results[0].test_name == "creatinine [Mass/volume] in Serum or Plasma"
    assert results[0].unit == "mg/dL"
    assert results[1].test_name == "Sodium [Moles/volume] in Serum or Plasma"
    assert results[1].unit == "mmol/L"
    assert results[1].reference_range == "N/A"


def test_parse_alternate_key_value_result_rows_preserves_ocr_lines() -> None:
    lines = [
        "* Glucose [Mass/volume] in Serum or Plasma",
        "  value=84.23 unit=mg/dl; range=N/A",
        "* Urea nitrogen [Mass/volume] in Serum or Plasma",
        "  yalue=16.75 unit=mg/dt3 range=N/A",
    ]

    results = parse_lab_result_rows(lines)

    assert len(results) == 2
    assert results[0].test_name == "Glucose [Mass/volume] in Serum or Plasma"
    assert results[0].value.numeric == 84.23
    assert results[0].unit == "mg/dL"
    assert results[0].reference_range == "N/A"
    assert results[0].raw_line == "\n".join(lines[:2])
    assert results[1].test_name == "Urea nitrogen [Mass/volume] in Serum or Plasma"
    assert results[1].value.numeric == 16.75
    assert results[1].unit == "mg/dL"


def test_parse_collapsed_ocr_result_row_preserves_raw_line() -> None:
    raw_line = "Hemoglobin 12.5 gm/di 13.0 - 17.0 L"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "Hemoglobin"
    assert result.value.numeric == 12.5
    assert result.unit == "gm/di"
    assert result.reference_range == "13.0 - 17.0"
    assert result.flag == "L"
    assert result.raw_line == raw_line


def test_parse_collapsed_ocr_result_row_with_comma_range() -> None:
    raw_line = "WBC Count 12,500 10*3/uL 4,000- 11,000 H"

    result = parse_lab_result_row(raw_line)

    assert result is not None
    assert result.test_name == "WBC Count"
    assert result.value.numeric == 12500.0
    assert result.unit == "10*3/uL"
    assert result.reference_range == "4,000- 11,000"
    assert result.flag == "H"
    assert result.raw_line == raw_line
