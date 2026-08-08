import json
from pathlib import Path

from app.services.models import TranscriptionResult


class MockTranscriptionAdapter:
    def __init__(self, response_dir: Path | str) -> None:
        self.response_dir = Path(response_dir)

    async def transcribe(self, audio: bytes, language: str) -> TranscriptionResult:
        response_path = self.response_dir / f"{language}.json"

        with response_path.open(encoding="utf-8") as response_file:
            payload = json.load(response_file)

        return TranscriptionResult(
            transcript=payload["transcript"],
            detected_language=payload["detected_language"],
            duration=float(payload["duration"]),
            provider=payload["provider"],
        )
