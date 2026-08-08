from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.adapters.transcription.factory import create_transcription_provider
from app.api.schemas.transcription import TranscriptionResponse
from app.config import get_settings
from app.services.transcription import TranscriptionService


router = APIRouter(prefix="/api/v1", tags=["transcription"])
SUPPORTED_LANGUAGES = {"bn", "en", "auto"}
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a"}
MAX_AUDIO_BYTES = 25 * 1024 * 1024


def get_transcription_service() -> TranscriptionService:
    settings = get_settings()
    provider = create_transcription_provider(settings)
    return TranscriptionService(provider)


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

    file_extension = Path(file.filename or "").suffix.lower()
    if file_extension not in SUPPORTED_AUDIO_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "UNSUPPORTED_AUDIO_FORMAT",
                    "message": "Supported audio formats are wav, mp3 and m4a.",
                }
            },
        )

    audio = await file.read()
    if len(audio) > MAX_AUDIO_BYTES:
        return JSONResponse(
            status_code=413,
            content={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "Audio file exceeds the 25 MB limit.",
                }
            },
        )

    service = get_transcription_service()
    result = await service.transcribe(audio, language)

    return TranscriptionResponse(
        transcript=result.transcript,
        detected_language=result.detected_language,
        duration=result.duration,
        provider=result.provider,
    )
