import asyncio

from app.adapters.transcription.base import TranscriptionProvider
from app.services.models import TranscriptionResult


class FakeTranscriptionProvider:
    async def transcribe(self, audio: bytes, language: str) -> TranscriptionResult:
        return TranscriptionResult(
            transcript=audio.decode("utf-8"),
            detected_language=language,
            duration=1.0,
            provider="fake",
        )


def test_provider_contract_can_be_used_by_calling_code() -> None:
    provider: TranscriptionProvider = FakeTranscriptionProvider()

    result = asyncio.run(provider.transcribe(b"Hello", "en"))

    assert result.transcript == "Hello"
    assert result.detected_language == "en"
    assert result.provider == "fake"
