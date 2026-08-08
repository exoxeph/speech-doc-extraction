import json
from pathlib import Path

from app.services.models import TranscriptionResult


class MockTranscriptionAdapter:
    def __init__(self, response_dir: Path | str) -> None:
        self.response_dir = Path(response_dir)

    async def transcribe(self, audio: bytes, language: str) -> TranscriptionResult:
        if not audio or audio.strip(b"\x00") == b"":
            return self._load_response("silence")

        return self._load_response(language)

    def _load_response(self, fixture_name: str) -> TranscriptionResult:
        response_path = self.response_dir / f"{fixture_name}.json"

        with response_path.open(encoding="utf-8") as response_file:
            payload = json.load(response_file)

        return TranscriptionResult(
            transcript=payload["transcript"],
            detected_language=payload["detected_language"],
            duration=float(payload["duration"]),
            provider=payload["provider"],
        )
