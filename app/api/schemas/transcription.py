from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    transcript: str
    detected_language: str | None
    duration: float
    provider: str
