from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.adapters.transcription.mock import MockTranscriptionAdapter
from app.api.schemas.transcription import TranscriptionResponse
from app.services.transcription import TranscriptionService


router = APIRouter(prefix="/api/v1", tags=["transcription"])
SUPPORTED_LANGUAGES = {"bn", "en", "auto"}


def get_transcription_service() -> TranscriptionService:
    project_root = Path(__file__).resolve().parents[3]
    response_dir = project_root / "testdata" / "mock_responses" / "transcription"
    return TranscriptionService(MockTranscriptionAdapter(response_dir))


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(...),
) -> TranscriptionResponse | JSONResponse:
    if language not in SUPPORTED_LANGUAGES:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_LANGUAGE",
                    "message": "Supported languages are bn, en and auto.",
                }
            },
        )

    audio = await file.read()
    service = get_transcription_service()
    result = await service.transcribe(audio, language)

    return TranscriptionResponse(
        transcript=result.transcript,
        detected_language=result.detected_language,
        duration=result.duration,
        provider=result.provider,
    )
