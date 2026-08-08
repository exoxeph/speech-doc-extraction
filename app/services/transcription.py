from app.adapters.transcription.base import TranscriptionProvider
from app.services.models import TranscriptionResult


class TranscriptionService:
    def __init__(self, provider: TranscriptionProvider) -> None:
        self.provider = provider

    async def transcribe(self, audio: bytes, language: str) -> TranscriptionResult:
        return await self.provider.transcribe(audio, language)
