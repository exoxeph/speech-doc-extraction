from fastapi import APIRouter, File, UploadFile

from app.adapters.ocr.factory import create_ocr_provider
from app.api.schemas.documents import (
    DocumentExtractionResponse,
    LabReportMetaResponse,
    LabResultResponse,
    LabValueResponse,
)
from app.config import get_settings
from app.services.document_extraction import DocumentExtractionService
from app.services.models import DocumentExtractionResult


router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


def get_document_extraction_service() -> DocumentExtractionService:
    settings = get_settings()
    provider = create_ocr_provider(settings)
    return DocumentExtractionService(provider)


@router.post("/extract", response_model=DocumentExtractionResponse)
async def extract_document(file: UploadFile = File(...)) -> DocumentExtractionResponse:
    document = await file.read()
    service = get_document_extraction_service()
    result = await service.extract(document)
    return _to_response(result)


def _to_response(result: DocumentExtractionResult) -> DocumentExtractionResponse:
    return DocumentExtractionResponse(
        document_type=result.document_type,
        meta=LabReportMetaResponse(
            patient_name=result.meta.patient_name,
            age=result.meta.age,
            sex=result.meta.sex,
            report_date=result.meta.report_date,
            lab_name=result.meta.lab_name,
            reference_no=result.meta.reference_no,
        ),
        results=[
            LabResultResponse(
                test_name=item.test_name,
                value=LabValueResponse(
                    numeric=item.value.numeric,
                    operator=item.value.operator,
                    raw=item.value.raw,
                ),
                unit=item.unit,
                reference_range=item.reference_range,
                flag=item.flag,
                raw_line=item.raw_line,
            )
            for item in result.results
        ],
        provider=result.provider,
    )
