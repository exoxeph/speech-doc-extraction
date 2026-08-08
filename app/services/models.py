from dataclasses import dataclass


@dataclass(frozen=True)
class TranscriptionResult:
    transcript: str
    detected_language: str | None
    duration: float
    provider: str
