from app.services.document_metadata import parse_lab_report_meta


def test_parse_complete_lab_report_metadata() -> None:
    meta = parse_lab_report_meta(
        [
            "ABC Diagnostic Centre",
            "Patient Name: John Doe",
            "Age: 28    Sex: Male",
            "Report Date: 2026-08-07",
            "Reference No: R12345",
        ]
    )

    assert meta.patient_name == "John Doe"
    assert meta.age == "28"
    assert meta.sex == "Male"
    assert meta.report_date == "2026-08-07"
    assert meta.lab_name == "ABC Diagnostic Centre"
    assert meta.reference_no == "R12345"


def test_parse_metadata_with_spacing_and_case_variations() -> None:
    meta = parse_lab_report_meta(
        [
            "City Lab",
            "patient name : Jane Smith",
            "AGE 34      SEX Female",
            "Date: 8 Aug 2026",
            "Ref No. ZX-7788",
        ]
    )

    assert meta.patient_name == "Jane Smith"
    assert meta.age == "34"
    assert meta.sex == "Female"
    assert meta.report_date == "8 Aug 2026"
    assert meta.lab_name == "City Lab"
    assert meta.reference_no == "ZX-7788"


def test_parse_partial_metadata_leaves_missing_fields_unset() -> None:
    meta = parse_lab_report_meta(["Patient Name: John Doe"])

    assert meta.patient_name == "John Doe"
    assert meta.age is None
    assert meta.sex is None
    assert meta.report_date is None
    assert meta.lab_name is None
    assert meta.reference_no is None


def test_parse_metadata_does_not_invent_values_from_unrelated_text() -> None:
    meta = parse_lab_report_meta(
        [
            "RESTAURANT RECEIPT",
            "Burger        12.99",
            "Tax            1.30",
        ]
    )

    assert meta.patient_name is None
    assert meta.age is None
    assert meta.sex is None
    assert meta.report_date is None
    assert meta.lab_name is None
    assert meta.reference_no is None


def test_parse_metadata_from_tesseract_clean_report_lines() -> None:
    meta = parse_lab_report_meta(
        [
            "LYNN URGENT CARE LLC",
            "LABORATORY RESULT REPORT",
            "Patient Name: Guadalupe206 Valencia279",
            "Date of Birth: 1954-04-26 Age: 60 Sex: F",
            "Report Date: 2014-06-30",
            "Reference No: SYN-7AD140AB",
        ]
    )

    assert meta.patient_name == "Guadalupe206 Valencia279"
    assert meta.age == "60"
    assert meta.sex == "Female"
    assert meta.report_date == "2014-06-30"
    assert meta.lab_name == "LYNN URGENT CARE LLC"
    assert meta.reference_no == "SYN-7AD140AB"


def test_parse_metadata_strips_ocr_punctuation_after_label() -> None:
    meta = parse_lab_report_meta(["patient Name; Guadalupe206 valencia279"])

    assert meta.patient_name == "Guadalupe206 valencia279"


def test_parse_metadata_from_rotated_alternate_ocr_lines() -> None:
    meta = parse_lab_report_meta(
        [
            "facility: PRIMARY CARE ASSOCIATES LLC",
            "report date: november 26, 2019",
            "cases SYN-@1AQQ6CE",
            "rogelioi? pacochao35 (M)» 008 1969-10-07, age 5°",
        ]
    )

    assert meta.age == "50"
    assert meta.report_date == "november 26, 2019"
    assert meta.lab_name == "PRIMARY CARE ASSOCIATES LLC"
    assert meta.reference_no == "SYN-01A006CE"
