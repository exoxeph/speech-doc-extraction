import asyncio
from pathlib import Path

from app.adapters.transcription.mock import MockTranscriptionAdapter


FIXTURE_DIR = Path("testdata/mock_responses/transcription")


def test_mock_transcription_adapter_returns_english_fixture() -> None:
    provider = MockTranscriptionAdapter(FIXTURE_DIR)

    result = asyncio.run(provider.transcribe(b"audio bytes", "en"))

    assert result.transcript == "Hello, this is a test."
    assert result.detected_language == "en"
    assert result.duration == 2.4
    assert result.provider == "mock"


def test_mock_transcription_adapter_returns_bengali_fixture() -> None:
    provider = MockTranscriptionAdapter(FIXTURE_DIR)

    result = asyncio.run(provider.transcribe(b"audio bytes", "bn"))

    assert result.transcript == "আমি আজ হাসপাতালে গিয়েছিলাম"
    assert result.detected_language == "bn"
    assert result.duration == 4.32
    assert result.provider == "mock"


def test_mock_transcription_adapter_returns_empty_transcript_for_silence() -> None:
    provider = MockTranscriptionAdapter(FIXTURE_DIR)

    result = asyncio.run(provider.transcribe(b"\x00" * 100, "en"))

    assert result.transcript == ""
    assert result.detected_language is None
    assert result.duration == 4.8
    assert result.provider == "mock"
