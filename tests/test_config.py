from pathlib import Path

import pytest

from app.adapters.transcription.factory import create_transcription_provider
import app.adapters.transcription.factory as transcription_factory
from app.adapters.ocr.factory import create_ocr_provider
from app.adapters.ocr.mock import MockOCRAdapter
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


def test_factory_creates_mock_ocr_provider() -> None:
    provider = create_ocr_provider(Settings(ocr_provider="mock"))

    assert isinstance(provider, MockOCRAdapter)


def test_factory_rejects_unknown_transcription_provider() -> None:
    settings = Settings(transcription_provider="banana")

    with pytest.raises(ValueError, match="Unsupported transcription provider: banana"):
        create_transcription_provider(settings)


def test_factory_rejects_unknown_ocr_provider() -> None:
    settings = Settings(ocr_provider="banana")

    with pytest.raises(ValueError, match="Unsupported OCR provider: banana"):
        create_ocr_provider(settings)


def test_factory_creates_faster_whisper_provider(monkeypatch) -> None:
    class StubFasterWhisperProvider:
        pass

    monkeypatch.setattr(
        transcription_factory,
        "FasterWhisperTranscriptionAdapter",
        StubFasterWhisperProvider,
    )

    provider = create_transcription_provider(
        Settings(transcription_provider="faster-whisper")
    )

    assert isinstance(provider, StubFasterWhisperProvider)
