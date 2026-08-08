from typing import Protocol

from app.services.models import TranscriptionResult


class TranscriptionProvider(Protocol):
    async def transcribe(
        self,
        audio: bytes,
        language: str,
    ) -> TranscriptionResult:
        ...
