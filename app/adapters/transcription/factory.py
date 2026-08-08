from pathlib import Path

from app.adapters.transcription.base import TranscriptionProvider
from app.adapters.transcription.mock import MockTranscriptionAdapter
from app.config import Settings


def create_transcription_provider(settings: Settings) -> TranscriptionProvider:
    if settings.transcription_provider == "mock":
        return MockTranscriptionAdapter(
            _resolve_project_path(settings.mock_transcription_response_dir)
        )

    raise ValueError(
        f"Unsupported transcription provider: {settings.transcription_provider}"
    )


def _resolve_project_path(path: Path) -> Path:
    if path.is_absolute():
        return path

    project_root = Path(__file__).resolve().parents[3]
    return project_root / path
