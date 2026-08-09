from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TranscriptionResult:
    transcript: str
    detected_language: str | None
    duration: float
    provider: str


@dataclass(frozen=True)
class LabReportMeta:
    patient_name: str | None = None
    age: str | None = None
    sex: str | None = None
    report_date: str | None = None
    lab_name: str | None = None
    reference_no: str | None = None


@dataclass(frozen=True)
class LabValueRange:
    lower: float
    upper: float


@dataclass(frozen=True)
class LabValue:
    numeric: float | None
    kind: Literal["scalar", "range"] = "scalar"
    operator: str | None = None
    range: LabValueRange | None = None
    raw: str | None = None


@dataclass(frozen=True)
class LabResult:
    test_name: str
    value: LabValue
    unit: str
    reference_range: str
    flag: str
    raw_line: str


@dataclass(frozen=True)
class DocumentExtractionResult:
    document_type: Literal["lab_report", "unknown"]
    meta: LabReportMeta
    results: list[LabResult]
    provider: str
