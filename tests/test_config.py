from pathlib import Path

import pytest

from app.adapters.transcription.factory import create_transcription_provider
from app.adapters.transcription.mock import MockTranscriptionAdapter
from app.config import Settings, get_settings


def test_settings_default_to_mock_provider() -> None:
    settings = Settings()

    assert settings.transcription_provider == "mock"


def test_settings_read_transcription_provider_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("TRANSCRIPTION_PROVIDER", "mock")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.transcription_provider == "mock"

    get_settings.cache_clear()


def test_factory_creates_mock_transcription_provider() -> None:
    settings = Settings(
        transcription_provider="mock",
        mock_transcription_response_dir=Path("testdata/mock_responses/transcription"),
    )

    provider = create_transcription_provider(settings)

    assert isinstance(provider, MockTranscriptionAdapter)


def test_factory_rejects_unknown_transcription_provider() -> None:
    settings = Settings(transcription_provider="banana")

    with pytest.raises(ValueError, match="Unsupported transcription provider: banana"):
        create_transcription_provider(settings)
