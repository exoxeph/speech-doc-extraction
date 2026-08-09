from app.adapters.ocr.base import OCRProvider
from app.services.date_normalizer import normalize_report_date
from app.services.document_metadata import parse_lab_report_meta
from app.services.models import DocumentExtractionResult, LabReportMeta
from app.services.report_parser import parse_lab_result_rows


class DocumentExtractionService:
    def __init__(self, provider: OCRProvider) -> None:
        self.provider = provider

    async def extract(self, document: bytes) -> DocumentExtractionResult:
        ocr_result = await self.provider.extract_text(document)
        meta = _normalize_meta(parse_lab_report_meta(ocr_result.lines))
        results = parse_lab_result_rows(ocr_result.lines)

        return DocumentExtractionResult(
            document_type="lab_report",
            meta=meta,
            results=results,
            provider=ocr_result.provider,
        )


def _normalize_meta(meta: LabReportMeta) -> LabReportMeta:
    normalized_date = None
    if meta.report_date is not None:
        normalized_date = normalize_report_date(meta.report_date)

    return LabReportMeta(
        patient_name=meta.patient_name,
        age=meta.age,
        sex=meta.sex,
        report_date=normalized_date or meta.report_date,
        lab_name=meta.lab_name,
        reference_no=meta.reference_no,
    )
