import asyncio

from app.services.models import TranscriptionResult
from app.services.transcription import TranscriptionService


class StubTranscriptionProvider:
    async def transcribe(self, audio: bytes, language: str) -> TranscriptionResult:
        return TranscriptionResult(
            transcript=f"{language}:{audio.decode('utf-8')}",
            detected_language=language,
            duration=3.0,
            provider="stub",
        )


def test_transcription_service_uses_injected_provider() -> None:
    service = TranscriptionService(StubTranscriptionProvider())

    result = asyncio.run(service.transcribe(b"sample", "en"))

    assert result.transcript == "en:sample"
    assert result.detected_language == "en"
    assert result.duration == 3.0
    assert result.provider == "stub"
