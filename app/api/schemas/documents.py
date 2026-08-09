from pydantic import BaseModel


class LabReportMetaResponse(BaseModel):
    patient_name: str | None
    age: str | None
    sex: str | None
    report_date: str | None
    lab_name: str | None
    reference_no: str | None


class LabValueRangeResponse(BaseModel):
    lower: float
    upper: float


class LabValueResponse(BaseModel):
    kind: str
    numeric: float | None
    operator: str | None
    range: LabValueRangeResponse | None
    raw: str | None


class LabResultResponse(BaseModel):
    test_name: str
    value: LabValueResponse
    unit: str
    reference_range: str
    flag: str
    raw_line: str


class DocumentExtractionResponse(BaseModel):
    document_type: str
    meta: LabReportMetaResponse
    results: list[LabResultResponse]
    provider: str
